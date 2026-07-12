#!/bin/bash
# setup_vps_dev.sh
# Script para configurar o ambiente de DESENVOLVIMENTO (DEV) na VPS, Nginx, SSL e Streamlit em porta alternativa.

set -e

DOMAIN="f2m-analytics-dev.cltn.com.br"
APP_DIR="/home/plataforma_analise_dados_dev"
PORT="8502"

echo "========================================="
echo "⚙️ INICIANDO INSTALAÇÃO DO AMBIENTE DEV"
echo "========================================="

echo "Atualizando pacotes e instalando dependências..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv nginx certbot python3-certbot-nginx

echo "Configurando ambiente Python de DEV em $APP_DIR..."
cd $APP_DIR

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

echo "Configurando Nginx para o Streamlit de DEV na porta $PORT..."
cat <<EOF | sudo tee /etc/nginx/sites-available/$DOMAIN
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://localhost:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Websockets suporte (Obrigatório para o Streamlit)
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
EOF

# Ativa o site no Nginx
sudo ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/

# Testa e reinicia o Nginx
sudo nginx -t
sudo systemctl restart nginx

echo "Criando serviço Systemd para manter o Streamlit de DEV rodando..."
cat <<EOF | sudo tee /etc/systemd/system/streamlit-dev.service
[Unit]
Description=Streamlit DEV Web App
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/python -m streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Atualiza e reinicia o serviço de DEV
sudo systemctl daemon-reload
sudo systemctl enable streamlit-dev
sudo systemctl restart streamlit-dev

echo "Configurando SSL via Certbot (Let's Encrypt)..."
# Tenta gerar o SSL. Se falhar (ex: DNS de DEV ainda não configurado), avisa o usuário e prossegue.
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN || {
    echo "⚠️ Aviso: Geração de SSL via Certbot falhou."
    echo "Isso geralmente ocorre se o subdomínio $DOMAIN ainda não estiver apontado no Cloudflare."
    echo "Você ainda poderá acessar o ambiente de DEV diretamente pelo IP na porta $PORT!"
}

echo "========================================="
echo "🚀 CONFIGURAÇÃO DE DEV CONCLUÍDA COM SUCESSO!"
echo "Sua aplicação de DEV está rodando."
echo "🌐 Link Principal (HTTPS): https://$DOMAIN"
echo "🔌 Link Alternativo (Direto IP): http://143.14.79.33:$PORT"
echo "Para verificar os logs de DEV, use: sudo journalctl -u streamlit-dev.service -f"
echo "========================================="
