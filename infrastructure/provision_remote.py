import paramiko
import sys
import os

def provision_server(host, username, password, agent_secret):
    print(f"🚀 Conectando a {host}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=username, password=password)
        
        print("📁 Carregando script de setup...")
        # Lendo o script local
        with open("setup-vpn-server.sh", "r") as f:
            script_content = f.read()
            
        # Criando o arquivo no servidor remoto
        sftp = client.open_sftp()
        with sftp.file("setup.sh", "w") as f:
            f.write(script_content)
        sftp.close()
        
        print("⚙️  Executando setup (pode demorar alguns minutos)...")
        stdin, stdout, stderr = client.exec_command(f"sudo bash setup.sh {agent_secret}")
        
        for line in stdout:
            print(f" [REMOTE] {line.strip()}")
            
        for line in stderr:
            print(f" [ERROR] {line.strip()}")
            
        print(f"✅ Setup concluído em {host}")
        
    except Exception as e:
        print(f"❌ Erro ao provisionar {host}: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Uso: python provision_remote.py <IP> <USER> <PASS> <SECRET>")
        sys.exit(1)
        
    ip, user, pw, sec = sys.argv[1:5]
    provision_server(ip, user, pw, sec)
