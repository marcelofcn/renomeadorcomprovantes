# 🚀 Guia de Deployment - Ubuntu 22.04 LTS

**Data:** 25 de maio de 2026  
**Sistema:** Ubuntu 22.04 LTS  
**Última atualização:** 2026-05-25

---

## 📋 Checklist Pré-Deployment

### Server
- [ ] Ubuntu 22.04 LTS instalado
- [ ] Acesso SSH disponível
- [ ] Sudo privileges configurado
- [ ] Firewall (UFW) configurado

### Domínio
- [ ] Domínio registrado (opcional)
- [ ] DNS apontando para o servidor
- [ ] SSL certificate (vamos gerar com Let's Encrypt)

### Código
- [ ] Repositório Git clonado
- [ ] .env configurado
- [ ] Testes passando localmente

---

## 🔧 Passo 1: Preparar Server (30 min)

### 1.1 Atualizar Sistema

```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y build-essential libssl-dev libffi-dev python3-dev
```

### 1.2 Instalar Dependências

```bash
# Python e Pip
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Nginx
sudo apt-get install -y nginx

# PostgreSQL (opcional, use SQLite para começar)
# sudo apt-get install -y postgresql postgresql-contrib

# Git
sudo apt-get install -y git

# UFW Firewall
sudo apt-get install -y ufw
```

### 1.3 Configurar Firewall

```bash
# Ativar UFW
sudo ufw enable

# Permitir SSH
sudo ufw allow 22/tcp

# Permitir HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Verificar regras
sudo ufw status
```

---

## 📂 Passo 2: Estrutura de Diretórios (20 min)

### 2.1 Criar usuário de aplicação

```bash
# Criar usuário 'renomeador' (sem shell)
sudo useradd -r -s /bin/bash -m -d /home/renomeador renomeador

# Dar permissões sudo
sudo visudo
# Adicionar a linha:
# renomeador ALL=(ALL) NOPASSWD: /usr/bin/systemctl

# Trocar para usuário renomeador
sudo su - renomeador
```

### 2.2 Clonar repositório

```bash
cd /home/renomeador
git clone https://github.com/seu-usuario/renomeadorcomprovantes.git
cd renomeadorcomprovantes

# Criar diretórios de dados
mkdir -p data/{uploads,processados,histórico}
chmod 755 data
```

---

## 🐍 Passo 3: Setup Backend (30 min)

### 3.1 Criar virtual environment

```bash
cd /home/renomeador/renomeadorcomprovantes/backend
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3.2 Instalar dependências Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.3 Configurar .env

```bash
# Criar .env a partir do exemplo
cp .env.example .env

# Editar .env com valores reais
nano .env
```

**Conteúdo do `.env`:**

```env
# App
APP_NAME=Renomeador de Comprovantes
APP_VERSION=1.0.0

# Server
API_HOST=0.0.0.0
API_PORT=8000

# JWT (gerar chave segura!)
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Database
DATABASE_URL=sqlite:////home/renomeador/renomeadorcomprovantes/data/app.db

# CORS
CORS_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com

# Email (opcional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seu-email@gmail.com
SMTP_PASSWORD=sua-senha
```

### 3.4 Inicializar database

```bash
python3 -c "from database import init_db; init_db()"
```

---

## 🎨 Passo 4: Setup Frontend (30 min)

### 4.1 Build do Vite

```bash
cd /home/renomeador/renomeadorcomprovantes/frontend
npm install
npm run build
```

Isso criará a pasta `dist/` com os arquivos otimizados.

### 4.2 Copiar para Nginx

```bash
sudo cp -r dist/* /var/www/renomeador/
sudo chown -R www-data:www-data /var/www/renomeador
```

---

## 🌐 Passo 5: Nginx Reverse Proxy (30 min)

### 5.1 Criar configuração Nginx

**Arquivo:** `/etc/nginx/sites-available/renomeador`

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;
    client_max_body_size 100M;

    # Frontend
    location / {
        root /var/www/renomeador;
        try_files $uri $uri/ /index.html;
        
        # Cache estático
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API Backend
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket (se usar)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeout
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Documentação API
    location /docs {
        proxy_pass http://backend/docs;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://backend/openapi.json;
        proxy_set_header Host $host;
    }
}
```

### 5.2 Habilitar site

```bash
# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/renomeador /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Recarregar Nginx
sudo systemctl reload nginx
```

### 5.3 Verificar status

```bash
sudo systemctl status nginx
```

---

## 🔐 Passo 6: SSL/TLS com Let's Encrypt (20 min)

### 6.1 Instalar Certbot

```bash
sudo apt-get install -y certbot python3-certbot-nginx
```

### 6.2 Gerar certificado

```bash
# Gerar certificado (automático com Nginx)
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com

# Responder às perguntas
# - Email
# - Aceitar termos
# - Aceitar newsletter (opcional)
```

### 6.3 Auto-renewal

```bash
# Testar renovação automática
sudo certbot renew --dry-run

# Verificar se Nginx já redireciona HTTP para HTTPS
sudo nginx -t && sudo systemctl reload nginx
```

---

## ⚙️ Passo 7: Systemd Service (20 min)

### 7.1 Criar arquivo de serviço

**Arquivo:** `/etc/systemd/system/renomeador-backend.service`

```ini
[Unit]
Description=Renomeador de Comprovantes - Backend
After=network.target

[Service]
Type=notify
User=renomeador
WorkingDirectory=/home/renomeador/renomeadorcomprovantes/backend
Environment="PATH=/home/renomeador/renomeadorcomprovantes/backend/.venv/bin"
ExecStart=/home/renomeador/renomeadorcomprovantes/backend/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 7.2 Habilitar serviço

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar para start automático
sudo systemctl enable renomeador-backend

# Iniciar serviço
sudo systemctl start renomeador-backend

# Verificar status
sudo systemctl status renomeador-backend

# Ver logs
sudo journalctl -u renomeador-backend -f
```

---

## 📊 Passo 8: Monitoramento e Logs (15 min)

### 8.1 Ver logs

```bash
# Logs da aplicação
sudo journalctl -u renomeador-backend -f

# Logs do Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Logs do sistema
sudo dmesg -f
```

### 8.2 Health check

```bash
# Testar backend
curl http://127.0.0.1:8000/api/health

# Testar frontend
curl https://seu-dominio.com

# Testar API através do Nginx
curl https://seu-dominio.com/api/health
```

### 8.3 Setup de alertas (opcional)

```bash
# Instalar Uptime Kuma para monitoramento
sudo docker pull louislam/uptime-kuma:latest
```

---

## 🔄 Passo 9: Backup Automático (15 min)

### 9.1 Script de backup

**Arquivo:** `/home/renomeador/backup.sh`

```bash
#!/bin/bash

BACKUP_DIR="/home/renomeador/backups"
SOURCE_DIR="/home/renomeador/renomeadorcomprovantes"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup do banco de dados
tar -czf $BACKUP_DIR/db_$DATE.tar.gz $SOURCE_DIR/data/

# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "db_*.tar.gz" -mtime +7 -delete

echo "Backup concluído: $DATE"
```

### 9.2 Agendar cron

```bash
# Editar crontab
crontab -e

# Adicionar linha para backup diário às 02:00
0 2 * * * /home/renomeador/backup.sh >> /home/renomeador/backup.log 2>&1
```

---

## ✅ Passo 10: Verificações Finais (20 min)

### 10.1 Checklist de deployment

```bash
# ✅ Backend rodando
sudo systemctl status renomeador-backend

# ✅ Nginx rodando
sudo systemctl status nginx

# ✅ Portas abertas
sudo netstat -tulpn | grep LISTEN

# ✅ SSL válido
sudo certbot certificates

# ✅ Firewall ativo
sudo ufw status

# ✅ Database acessível
ls -la /home/renomeador/renomeadorcomprovantes/data/app.db

# ✅ Logs sem erros
sudo journalctl -u renomeador-backend -n 50
```

### 10.2 Testes de conectividade

```bash
# De outro computador:
curl -I https://seu-dominio.com         # Frontend
curl https://seu-dominio.com/api/health # Backend
```

---

## 🆘 Troubleshooting

### Backend não inicia

```bash
# Ver erro detalhado
sudo systemctl status renomeador-backend -l

# Ver logs
sudo journalctl -u renomeador-backend -n 100

# Testar manualmente
cd /home/renomeador/renomeadorcomprovantes/backend
source .venv/bin/activate
python main.py
```

### Frontend não carrega

```bash
# Verificar permissões
sudo ls -la /var/www/renomeador/

# Testar Nginx
sudo nginx -t

# Ver erro Nginx
sudo tail -20 /var/log/nginx/error.log
```

### SSL não funciona

```bash
# Verificar certificado
sudo certbot certificates

# Renovar certificado
sudo certbot renew

# Forçar renovação
sudo certbot renew --force-renewal
```

### Database locked

```bash
# Remover lock do SQLite
rm /home/renomeador/renomeadorcomprovantes/data/app.db-wal
rm /home/renomeador/renomeadorcomprovantes/data/app.db-shm
```

---

## 📈 Performance Tuning (Optional)

### Nginx caching

```nginx
# Adicionar em /etc/nginx/nginx.conf
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m;

location /api {
    proxy_cache api_cache;
    proxy_cache_valid 200 10m;
}
```

### Python gunicorn (alternativa ao uvicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:8000 main:app
```

### PostgreSQL (para produção)

```bash
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres createdb renomeador
# Atualizar DATABASE_URL em .env
```

---

## 📞 Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| 502 Bad Gateway | Ver logs do backend: `journalctl -u renomeador-backend` |
| 403 Forbidden | Verificar permissões: `sudo chown -R www-data:www-data /var/www/renomeador` |
| SSL não funciona | Renovar cert: `sudo certbot renew --force-renewal` |
| Database locked | Remover arquivos -wal e -shm |
| Porta em uso | `sudo lsof -i :8000` |

---

## 🎉 Pronto!

Sua aplicação deve estar rodando em:

```
🌐 Frontend:  https://seu-dominio.com
📚 API Docs:  https://seu-dominio.com/docs
💻 SSH:       ssh renomeador@seu-dominio.com
```

---

## 🔄 Atualizações Futuras

```bash
# Puxar código novo
cd /home/renomeador/renomeadorcomprovantes
git pull origin main

# Reinstalar dependências (se houver)
cd backend
pip install -r requirements.txt

# Rebuild frontend (se houver)
cd ../frontend
npm install
npm run build

# Reiniciar serviço
sudo systemctl restart renomeador-backend
```

---

## 📚 Referências

- [Ubuntu 22.04 LTS](https://ubuntu.com/server)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
- [FastAPI on Production](https://fastapi.tiangolo.com/deployment/)
- [Systemd Service](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

---

**Deployment pronto em ~3-4 horas! 🚀**

*Última atualização: 25 de maio de 2026*
