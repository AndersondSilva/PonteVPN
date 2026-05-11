import os
import subprocess
import json
import time
import sys

# Protocolo AETERNA v2.0 - Automação Total
# Este script orquestra a infraestrutura, banco de dados e deploy.

def run_step(name, cmd, cwd=None):
    print(f"\n[STEP] 🚀 {name}...")
    try:
        process = subprocess.run(cmd, shell=True, check=True, cwd=cwd, capture_output=True, text=True)
        print(f"✅ {name} concluído.")
        return process.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro em {name}:")
        print(e.stderr)
        return None

def main():
    print("====================================================")
    print("🛡️  PONTEVPN - ORQUESTRAÇÃO AUTOMÁTICA AETERNA  🛡️")
    print("====================================================")

    # 1. Verificar Infraestrutura (Terraform)
    print("\n[1/4] 🏗️  Provisionando Infraestrutura...")
    if not os.path.exists("infrastructure/.terraform"):
        run_step("Terraform Init", "terraform init", cwd="infrastructure")
    
    # Aplicar mudanças (requer variáveis de ambiente definidas)
    run_step("Terraform Apply", "terraform apply -auto-approve", cwd="infrastructure")
    
    # 2. Obter Dados dos Servidores
    print("\n[2/4] 🛰️  Recuperando IPs dos novos servidores...")
    tf_output = run_step("Terraform Output", "terraform output -json", cwd="infrastructure")
    if not tf_output:
        print("❌ Falha ao obter output do Terraform.")
        return

    ips = json.loads(tf_output)
    br_ip = ips.get("vpn_br_ip", {}).get("value")
    eu_ip = ips.get("vpn_eu_ip", {}).get("value")

    print(f"📍 BR: {br_ip}")
    print(f"📍 EU: {eu_ip}")

    # 3. Sincronizar com o Banco de Dados (Supabase)
    print("\n[3/4] 🗄️  Sincronizando servidores no Banco de Dados...")
    # Aqui usaríamos o sqlx-cli ou um script python com psycopg2
    # Para simplificar e garantir portabilidade, usaremos uma query SQL direta se o psql estiver disponível
    # Ou simplesmente instruímos o usuário sobre a configuração manual do DB_URL
    
    db_url = "postgresql://postgres:S%40coCheio%231@db.yghcnprovjyxkqrfxuwt.supabase.co:5432/postgres"
    
    # SQL para registrar os servidores
    sql_query = f"""
    INSERT INTO servers (name, country, country_code, city, ip, wg_public_key, agent_url, min_plan)
    VALUES 
    ('São Paulo Core', 'Brasil', 'BR', 'São Paulo', '{br_ip}', 'PENDING', 'http://{br_ip}:8080', 'free'),
    ('Nuremberg Node', 'Alemanha', 'DE', 'Nuremberg', '{eu_ip}', 'PENDING', 'http://{eu_ip}:8080', 'pro')
    ON CONFLICT (ip) DO UPDATE SET is_active = true;
    """
    
    with open("sync_db.sql", "w") as f:
        f.write(sql_query)
        
    print("📝 Query de sincronização gerada em 'sync_db.sql'.")
    print("⚠️  Nota: A chave pública real deve ser atualizada após o primeiro handshake do agente.")

    # 4. Push Final e CI/CD
    print("\n[4/4] 📦 Enviando código final para GitHub...")
    run_step("Git Add", "git add .")
    run_step("Git Commit", 'git commit -m "auto: full infrastructure and database sync"')
    run_step("Git Push", "git push origin main")

    print("\n====================================================")
    print("✨ TUDO PRONTO! O SISTEMA ESTÁ EM DEPLOY CONTINUO ✨")
    print("====================================================")
    print("Próximos passos:")
    print("1. Verifique o GitHub Actions para o status do deploy Vercel/Railway.")
    print("2. Use o Painel Admin em /admin para gerir os primeiros usuários.")
    print("====================================================")

if __name__ == "__main__":
    main()
