import os
import subprocess
import sys

print("Preparando ambiente de deploy...")
try:
    import paramiko
except ImportError:
    print("Instalando biblioteca paramiko para acesso SSH automático...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko"])
    import paramiko

# Credenciais e Dados da VPS
HOST = "143.14.79.33"
USER = "root"
PASSWORD = "Cleiton@01"
DEST_DIR = "/home/plataforma_analise_dados"

def main():
    print("1. Compactando o projeto localmente...")
    # Usa o tar nativo do Windows 10/11 para compactar os arquivos ignorando pastas pesadas
    zip_cmd = "tar -czf deploy.tar.gz --exclude=\"venv\" --exclude=\".git\" --exclude=\"__pycache__\" --exclude=\".streamlit\" --exclude=\"*.log\" --exclude=\"deploy.tar.gz\" ."
    subprocess.check_call(zip_cmd, shell=True)

    print(f"2. Conectando na VPS {HOST} com o usuário {USER}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # Aceita a chave automaticamente
    
    try:
        ssh.connect(hostname=HOST, username=USER, password=PASSWORD, timeout=10)
    except Exception as e:
        print(f"Erro ao conectar na VPS: {e}")
        return

    print("3. Criando diretório de destino e enviando os arquivos...")
    ssh.exec_command(f"mkdir -p {DEST_DIR}")
    
    sftp = ssh.open_sftp()
    print("Fazendo upload do projeto para a VPS... (isso pode demorar um pouco)")
    sftp.put("deploy.tar.gz", f"{DEST_DIR}/deploy.tar.gz")
    sftp.close()

    print("4. Extraindo arquivos e executando o setup automático na VPS (Nginx, SSL, Python)...")
    command = f"cd {DEST_DIR} && tar -xzf deploy.tar.gz && rm deploy.tar.gz && chmod +x setup_vps.sh && ./setup_vps.sh"
    
    stdin, stdout, stderr = ssh.exec_command(command)
    
    # Exibe os logs do servidor no terminal do usuário em tempo real
    while True:
        line = stdout.readline()
        if not line:
            break
        print(line, end="")
        
    err = stderr.read().decode('utf-8')
    if err:
        print("Erros/Avisos do servidor:")
        print(err)

    ssh.close()
    
    print("\nLimpando arquivos temporários locais...")
    if os.path.exists("deploy.tar.gz"):
        os.remove("deploy.tar.gz")
        
    print("\n🚀 DEPLOY FINALIZADO COM SUCESSO!")
    print("🌐 Acesse: https://f2m-analytics.cltn.com.br")

if __name__ == "__main__":
    main()
