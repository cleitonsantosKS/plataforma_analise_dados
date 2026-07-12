import os
import subprocess
import sys

print("Preparando ambiente de deploy de DESENVOLVIMENTO (DEV)...")
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
DEST_DIR = "/home/plataforma_analise_dados_dev"

def main():
    # Obtém o diretório deste arquivo (que deve ser o diretório DEV)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    
    print("1. Compactando os arquivos do ambiente DEV localmente...")
    # Tar de todos os arquivos dentro da pasta DEV, ignorando venv, __pycache__, logs e o próprio tarball
    zip_cmd = "tar -czf deploy_dev.tar.gz --exclude=\"venv\" --exclude=\".git\" --exclude=\"__pycache__\" --exclude=\"*.log\" --exclude=\"deploy_dev.tar.gz\" ."
    subprocess.check_call(zip_cmd, shell=True)

    print(f"2. Conectando na VPS {HOST} com o usuário {USER}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # Aceita a chave automaticamente
    
    try:
        ssh.connect(hostname=HOST, username=USER, password=PASSWORD, timeout=10)
    except Exception as e:
        print(f"Erro ao conectar na VPS: {e}")
        return

    print(f"3. Criando diretório de destino {DEST_DIR} na VPS e enviando arquivos...")
    ssh.exec_command(f"mkdir -p {DEST_DIR}")
    
    sftp = ssh.open_sftp()
    print("Fazendo upload do projeto DEV para a VPS... (isso pode demorar um pouco)")
    sftp.put("deploy_dev.tar.gz", f"{DEST_DIR}/deploy_dev.tar.gz")
    sftp.close()

    print("4. Extraindo arquivos e executando o setup de DEV automático na VPS (Nginx, SSL, Python)...")
    command = f"cd {DEST_DIR} && tar -xzf deploy_dev.tar.gz && rm deploy_dev.tar.gz && chmod +x setup_vps_dev.sh && ./setup_vps_dev.sh"
    
    stdin, stdout, stderr = ssh.exec_command(command)
    
    # Exibe os logs do servidor no terminal do usuário em tempo real
    while True:
        line = stdout.readline()
        if not line:
            break
        print(line, end="")
        
    err = stderr.read().decode('utf-8')
    if err:
        print("\nErros/Avisos do servidor:")
        print(err)

    ssh.close()
    
    print("\nLimpando arquivos temporários locais...")
    if os.path.exists("deploy_dev.tar.gz"):
        os.remove("deploy_dev.tar.gz")
        
    print("\n🚀 DEPLOY DE DEV FINALIZADO COM SUCESSO!")
    print("🌐 Acesse: https://f2m-analytics-dev.cltn.com.br")
    print("🔌 Ou acesso direto: http://143.14.79.33:8502")

if __name__ == "__main__":
    main()
