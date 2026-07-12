#!/bin/bash
# setup_vps.sh
# Script para configurar a VPS, Nginx, SSL e Streamlit

set -e

DOMAIN="f2m-analytics.cltn.com.br"
APP_DIR="/home/plataforma_analise_dados"

echo "Atualizando pacotes e instalando dependências..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv nginx certbot python3-certbot-nginx

echo "Configurando ambiente Python em $APP_DIR..."
cd $APP_DIR

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

echo "Configurando Nginx para o Streamlit..."
cat <<EOF | sudo tee /etc/nginx/sites-available/$DOMAIN
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://localhost:8501;
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

# Ativa o site no Nginx e remove o default
sudo ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Testa e reinicia o Nginx
sudo nginx -t
sudo systemctl restart nginx

echo "Criando serviço Systemd para manter o Streamlit rodando em background..."
cat <<EOF | sudo tee /etc/systemd/system/streamlit.service
[Unit]
Description=Streamlit Web App
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/python -m streamlit run app.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Atualiza e reinicia o serviço
sudo systemctl daemon-reload
sudo systemctl enable streamlit
sudo systemctl restart streamlit

echo "Configurando SSL via Certbot (Let's Encrypt) para Cloudflare..."
# Nota: Como o Cloudflare atua como proxy, o SSL será gerado se a nuvem estiver no modo "Proxied" (Nuvem Laranja) 
# e o Cloudflare permitir tráfego HTTP para validação, ou se estiver "DNS Only". 
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN || echo "Aviso: Se o SSL falhar aqui, configure no Cloudflare a opção SSL/TLS para 'Flexible' ou 'Full' e acesse via HTTPS."

echo "========================================="
echo "Configuração concluída com sucesso!"
echo "Sua aplicação deve estar rodando em: https://$DOMAIN"
echo "Para verificar os logs do Streamlit, use: sudo journalctl -u streamlit.service -f"
echo "========================================="
