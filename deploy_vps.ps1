# deploy_vps.ps1
# Script PowerShell para enviar os arquivos da aplicação para a VPS e executar a configuração
$ErrorActionPreference = "Stop"

$VPS_USER = "root"
$VPS_IP = "143.14.79.33"
$DEST_DIR = "/home/plataforma_analise_dados"

Write-Host "Iniciando o deploy da Plataforma para a VPS ($VPS_IP)..." -ForegroundColor Cyan

# 1. Cria a pasta no servidor
Write-Host "Criando diretório no servidor..." -ForegroundColor Yellow
ssh ${VPS_USER}@${VPS_IP} "mkdir -p $DEST_DIR"

# 2. Copia os arquivos usando scp (compactando e enviando via ssh para evitar enviar pastas inúteis)
Write-Host "Compactando e enviando arquivos (Isso pode demorar alguns segundos)..." -ForegroundColor Yellow
# O tar compacta ignorando as pastas de ambiente local, e descompacta direto no servidor
tar -cf - --exclude="venv" --exclude=".git" --exclude="__pycache__" --exclude=".streamlit" --exclude="*.log" . | ssh ${VPS_USER}@${VPS_IP} "cd $DEST_DIR && tar -xf -"

# 3. Dá permissão de execução no script de setup
Write-Host "Dando permissão de execução no setup_vps.sh..." -ForegroundColor Yellow
ssh ${VPS_USER}@${VPS_IP} "chmod +x $DEST_DIR/setup_vps.sh"

# 4. Executa o script de configuração no servidor
Write-Host "Rodando a instalação na VPS (Isso vai instalar Nginx, SSL, e Python)..." -ForegroundColor Magenta
ssh ${VPS_USER}@${VPS_IP} "cd $DEST_DIR && ./setup_vps.sh"

Write-Host "`nDeploy finalizado com sucesso!" -ForegroundColor Green
Write-Host "Acesse a aplicação em: https://f2m-analytics.cltn.com.br" -ForegroundColor Blue
