# Plano de Deploy em Produção - Plataforma de Análise de Dados

## 🌐 Guia de Implantação em VPS Linux

Para implantar o **Plataforma de Análise de Dados** em produção em uma VPS Linux, siga as recomendações arquiteturais abaixo.

### 1. Gunicorn/PM2 (Gerenciador de Processos)
Utilize um gerenciador de processos para manter o app ativo em background.
Para aplicações Python/Flask:
```bash
pip install gunicorn
gunicorn --workers 3 --bind 127.0.0.1:8000 app:app --daemon
```

### 2. Configuração do Reverse Proxy com Nginx
Crie um arquivo de configuração de site no Nginx (`/etc/nginx/sites-available/plataforma_analise_dados`):
```nginx
server {
    listen 80;
    server_name seu_dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Habilitação de SSL com Certbot (HTTPS)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d seu_dominio.com
```
