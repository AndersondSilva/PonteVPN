import os
import json
import subprocess
import time

CONFIG_FILE = "production_config.json"
INFRA_DIR = "infrastructure"

def run_cmd(cmd, cwd=None):
    print(f"-> Executando: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True, cwd=cwd)
        return True
    except:
        return False

def main():
    print("🚀 INICIANDO PROTOCOLO DE PRODUÇÃO - PONTEVPN")
    
    if not os.path.exists(CONFIG_FILE):
        print("❌ Arquivo de configuração não encontrado.")
        return

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    # 1. Auditoria e Segurança
    print("\n[1/4] 🛡️ Verificando Segurança...")
    if not run_cmd("python ponte_cli.py audit", cwd=".."):
        print("⚠️  Avisos de segurança detectados. Verifique antes de continuar.")

    # 2. Provisionamento de Servidores
    print("\n[2/4] ⚙️  Provisionando Servidores VPN...")
    for server in config["servers"]:
        if server["host"] == "IP_AQUI":
            print(f"⏩ Pulando {server['name']} (IP não configurado).")
            continue
            
        print(f"🔧 Provisionando {server['name']} ({server['host']})...")
        # Aqui chamamos o provision_remote.py
        # Nota: Password deve estar no ambiente ou pedida uma vez
        run_cmd(f"python {INFRA_DIR}/provision_remote.py {server['host']} {server['user']} PASS_AQUI {server['secret']}")

    # 3. Backup e Push para GitHub (Trigger CI/CD)
    print("\n[3/4] 📦 Sincronizando com GitHub...")
    run_cmd("python ../backup_all_projects.py")
    print("✅ Código enviado. GitHub Actions irá iniciar o deploy para Vercel e Railway.")

    # 4. Verificação Final
    print("\n[4/4] ✨ Checklist de Produção:")
    print(" - [ ] RAILWAY_TOKEN configurado no GitHub Secrets?")
    print(" - [ ] VERCEL_TOKEN configurado no GitHub Secrets?")
    print(" - [ ] STRIPE_SECRET_KEY configurada no Railway?")
    print(" - [ ] Google/Apple/MS OAuth IDs configurados?")
    
    print("\n✅ Automação concluída. O sistema está em fase de deploy contínuo.")

if __name__ == "__main__":
    main()
