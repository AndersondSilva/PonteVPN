"""
Geração de configurações WireGuard.
A chave privada é gerada, usada para montar o .conf e DESCARTADA.
Apenas a chave pública é armazenada no banco.
"""
import subprocess
import ipaddress
import httpx
from app.config import settings


PLAN_BANDWIDTH_LIMITS = {
    "free": 2 * 1024 * 1024 * 1024,   # 2 GB
    "pro": None,                        # Ilimitado
    "business": None,                   # Ilimitado
}

VPN_SUBNET = ipaddress.IPv4Network("10.8.0.0/16")
DNS_SERVERS = "1.1.1.1, 1.0.0.1"


def generate_keypair() -> tuple[str, str]:
    """Gera par de chaves WireGuard. Retorna (private_key, public_key)."""
    private_key = subprocess.check_output(["wg", "genkey"]).decode().strip()
    public_key = subprocess.check_output(
        ["wg", "pubkey"], input=private_key.encode()
    ).decode().strip()
    return private_key, public_key


def build_client_config(
    private_key: str,
    client_vpn_ip: str,
    server_public_key: str,
    server_endpoint: str,
    server_port: int,
) -> str:
    """Monta o arquivo .conf para o cliente WireGuard."""
    return f"""[Interface]
PrivateKey = {private_key}
Address = {client_vpn_ip}/32
DNS = {DNS_SERVERS}

[Peer]
PublicKey = {server_public_key}
Endpoint = {server_endpoint}:{server_port}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
"""


def ip_from_index(index: int) -> str:
    """Gera IP único para o peer a partir do índice (ex: 10.8.1.5)."""
    # Começa em 10.8.1.1 (10.8.0.0 e 10.8.0.1 são reservados para o servidor)
    base = int(VPN_SUBNET.network_address) + 256 + index
    return str(ipaddress.IPv4Address(base))


async def register_peer_on_server(agent_url: str, public_key: str, vpn_ip: str) -> bool:
    """Registra o peer no servidor VPN via agente HTTP."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{agent_url}/peers",
            json={"public_key": public_key, "allowed_ip": f"{vpn_ip}/32"},
            headers={"X-Secret": settings.VPN_SERVERS_API_SECRET},
        )
        return resp.status_code == 200


async def remove_peer_from_server(agent_url: str, public_key: str) -> bool:
    """Remove o peer do servidor VPN via agente HTTP."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.delete(
            f"{agent_url}/peers/{public_key}",
            headers={"X-Secret": settings.VPN_SERVERS_API_SECRET},
        )
        return resp.status_code == 200
