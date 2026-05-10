#!/bin/bash
# ============================================================
# PonteVPN — Setup de Servidor WireGuard
# Execute num servidor Ubuntu 22.04 limpo (Hetzner/Vultr)
# Uso: bash setup-vpn-server.sh <VPN_AGENT_SECRET>
# ============================================================
set -e

AGENT_SECRET=${1:-"change-this-secret"}
SERVER_PORT=51820
VPN_SUBNET="10.8.0.0/16"
SERVER_VPN_IP="10.8.0.1"
DNS="1.1.1.1"

echo "🚀 Iniciando setup do servidor PonteVPN..."

# ── 1. Dependências ──────────────────────────────────────────
apt-get update -qq
apt-get install -y wireguard ufw python3 python3-pip curl

# ── 2. Gerar chaves do servidor ──────────────────────────────
mkdir -p /etc/wireguard
chmod 700 /etc/wireguard

if [ ! -f /etc/wireguard/privatekey ]; then
  wg genkey | tee /etc/wireguard/privatekey | wg pubkey > /etc/wireguard/publickey
  chmod 600 /etc/wireguard/privatekey
fi

SERVER_PRIVATE=$(cat /etc/wireguard/privatekey)
SERVER_PUBLIC=$(cat /etc/wireguard/publickey)

echo "✅ Chave pública do servidor: $SERVER_PUBLIC"

# ── 3. Interface WireGuard ───────────────────────────────────
INTERFACE=$(ip route | grep default | awk '{print $5}' | head -1)

cat > /etc/wireguard/wg0.conf << EOF
[Interface]
PrivateKey = ${SERVER_PRIVATE}
Address = ${SERVER_VPN_IP}/16
ListenPort = ${SERVER_PORT}
DNS = ${DNS}

# Encaminhamento de tráfego (NAT)
PostUp   = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -A FORWARD -o wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o ${INTERFACE} -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -D FORWARD -o wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o ${INTERFACE} -j MASQUERADE
EOF

chmod 600 /etc/wireguard/wg0.conf

# ── 4. IP Forwarding ─────────────────────────────────────────
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p

# ── 5. Firewall ──────────────────────────────────────────────
ufw allow 22/tcp     # SSH
ufw allow ${SERVER_PORT}/udp  # WireGuard
ufw allow 8080/tcp   # Agente VPN (só acessível internamente via secret)
ufw --force enable

# ── 6. WireGuard como serviço ────────────────────────────────
systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0

# ── 7. Instalar o agente HTTP (PonteVPN Agent) ───────────────
pip3 install fastapi uvicorn --quiet

mkdir -p /opt/pontevpn-agent

cat > /opt/pontevpn-agent/agent.py << 'AGENT_EOF'
"""
PonteVPN Agent — API local para gerir peers WireGuard
Escuta na porta 8080, apenas acessível pelo backend via secret
"""
import subprocess
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import os

app = FastAPI()
SECRET = os.environ.get("AGENT_SECRET", "change-this")


def verify_secret(x_secret: str = Header(...)):
    if x_secret != SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")


class PeerRequest(BaseModel):
    public_key: str
    allowed_ip: str  # ex: "10.8.1.5/32"


@app.post("/peers", dependencies=[Depends(verify_secret)])
def add_peer(req: PeerRequest):
    result = subprocess.run(
        ["wg", "set", "wg0", "peer", req.public_key, "allowed-ips", req.allowed_ip],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr)
    # Persistir configuração
    subprocess.run(["wg-quick", "save", "wg0"], capture_output=True)
    return {"status": "added", "peer": req.public_key[:16] + "..."}


@app.delete("/peers/{public_key}", dependencies=[Depends(verify_secret)])
def remove_peer(public_key: str):
    result = subprocess.run(
        ["wg", "set", "wg0", "peer", public_key, "remove"],
        capture_output=True, text=True
    )
    subprocess.run(["wg-quick", "save", "wg0"], capture_output=True)
    return {"status": "removed"}


@app.get("/health")
def health():
    result = subprocess.run(["wg", "show", "wg0"], capture_output=True, text=True)
    peers = result.stdout.count("peer:")
    return {"status": "ok", "active_peers": peers}
AGENT_EOF

# Serviço systemd para o agente
cat > /etc/systemd/system/pontevpn-agent.service << EOF
[Unit]
Description=PonteVPN WireGuard Agent
After=network.target

[Service]
Environment="AGENT_SECRET=${AGENT_SECRET}"
ExecStart=uvicorn agent:app --host 0.0.0.0 --port 8080
WorkingDirectory=/opt/pontevpn-agent
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable pontevpn-agent
systemctl start pontevpn-agent

# ── 8. Resumo ────────────────────────────────────────────────
SERVER_IP=$(curl -s ifconfig.me)

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║      ✅ SERVIDOR PONTEVPN CONFIGURADO        ║"
echo "╠══════════════════════════════════════════════╣"
echo "║ IP do Servidor:   ${SERVER_IP}"
echo "║ Porta WireGuard:  ${SERVER_PORT}/UDP"
echo "║ Porta Agente:     8080/TCP"
echo "╠══════════════════════════════════════════════╣"
echo "║ Chave pública WireGuard (adicionar no DB):   ║"
echo "║ ${SERVER_PUBLIC}"
echo "╠══════════════════════════════════════════════╣"
echo "║ URL do agente: http://${SERVER_IP}:8080"
echo "║ Secret do agente: ${AGENT_SECRET}"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "⚠️  Guarde estes valores — vai precisar deles no painel admin."
