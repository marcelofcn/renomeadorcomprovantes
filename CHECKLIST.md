# ✅ Checklist de Desenvolvimento

## 🎯 Estado Atual

✅ **MVP Funcional:** Sicredi Boleto  
✅ **Backend:** FastAPI rodando  
✅ **Frontend:** React scaffold criado  
✅ **Database:** SQLite com modelo básico  

🚀 **Próximo:** Refatoração em processadores + Bradesco

---

## 📋 Fase 1: Refatoração (PRIORITY) - ~6 horas

### Estrutura de Processadores

- [ ] Criar `backend/processors/__init__.py`
- [ ] Criar `backend/processors/base.py` (classe abstrata)
- [ ] Criar `backend/processors/sicredi.py` (refatorar código existente)
- [ ] Criar `backend/services/normalizer.py` (centralizar funções)
- [ ] Criar `backend/services/extrator.py` (factory pattern)

### Testes Unitários

- [ ] Criar `backend/tests/test_sicredi.py`
- [ ] Criar `backend/tests/test_normalizer.py`
- [ ] Rodar `pytest` com sucesso
- [ ] Cobertura mínima 80%

### API Updates

- [ ] Adicionar parâmetro `banco` em POST /api/upload
- [ ] Validar banco antes de processar
- [ ] Response estruturada com status

### Verificação

- [ ] Código sem duplicação (DRY)
- [ ] Testes passando
- [ ] Backend inicia sem erros
- [ ] Swagger documentação OK

---

## 🐍 FASE 1: Backend (Semana 1 - 8 horas)

### Leitura Técnica (1 hora)
- [ ] Ler [docs/ARQUITETURA_MELHORADA.md](./docs/ARQUITETURA_MELHORADA.md)
- [ ] Ler [docs/PLANO_IMPLEMENTACAO.md](./docs/PLANO_IMPLEMENTACAO.md) - FASE 1
- [ ] Entender o schema SQL

### Implementação (6 horas)

#### 1. Setup Python (30 min)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
- [ ] Virtual environment criado
- [ ] Dependências instaladas
- [ ] `pip list` mostra todos os pacotes

#### 2. Arquivos de Configuração (1 hora)
- [ ] Criar `backend/config.py` (template em PLANO_IMPLEMENTACAO.md)
- [ ] Criar `backend/database.py`
- [ ] Criar `backend/.env` (baseado em `.env.example`)
- [ ] Testar imports

#### 3. Models (1 hora)
- [ ] Criar `backend/models/__init__.py`
- [ ] Implementar `User` model
- [ ] Implementar `Comprovante` model
- [ ] Criar migrations básicas

#### 4. Autenticação (1,5 horas)
- [ ] Criar `backend/services/auth.py`
- [ ] Implementar JWT token creation
- [ ] Implementar password hashing
- [ ] Criar `backend/routes/auth.py`
- [ ] Endpoints: POST /auth/register, POST /auth/login

#### 5. API Principal (1 hora)
- [ ] Criar `backend/main.py`
- [ ] Configurar CORS
- [ ] Incluir routes
- [ ] Endpoint GET /api/health
- [ ] Swagger documentação

#### 6. Extração de Dados (1 hora)
- [ ] Criar `backend/services/extracoes.py`
- [ ] Adaptar funções de `exemplo_refatoracao.py`
- [ ] Implementar validações
- [ ] Testes básicos

### Validação (1 hora)
```bash
python main.py
# Deve iniciar em http://localhost:8000
```
- [ ] Backend inicia sem erros
- [ ] Swagger carrega em http://localhost:8000/docs
- [ ] Endpoint GET /api/health retorna 200
- [ ] CORS está configurado

### Testes Unitários (1 hora)
- [ ] Criar `backend/tests/test_auth.py`
- [ ] Criar `backend/tests/test_models.py`
- [ ] Rodar `pytest`
- [ ] Cobertura mínima de 80%

---

## ⚛️ FASE 2: Frontend (Semana 2 - 8 horas)

### Leitura Técnica (30 min)
- [ ] Ler [docs/PLANO_IMPLEMENTACAO.md](./docs/PLANO_IMPLEMENTACAO.md) - FASE 2
- [ ] Entender estrutura React
- [ ] Revisar Tailwind CSS basics

### Setup Vite + React (1 hora)
```bash
cd frontend
npm install
npm run dev
```
- [ ] Node modules instalado
- [ ] Dev server rodando em http://localhost:5173
- [ ] Hot module reloading (HMR) funcionando

### Autenticação Frontend (2 horas)
- [ ] Criar `src/services/auth.ts` (cliente API)
- [ ] Criar componente `src/components/Login.tsx`
- [ ] Criar componente `src/components/Register.tsx`
- [ ] Implementar token storage (localStorage)
- [ ] Interceptor de erro 401

### Upload & Processamento (2 horas)
- [ ] Criar `src/components/Upload.tsx`
- [ ] Drag-and-drop de PDFs
- [ ] Chamada POST /api/upload/pdf
- [ ] Status do processamento
- [ ] Download de arquivo

### Dashboard (2 horas)
- [ ] Criar `src/pages/Dashboard.tsx`
- [ ] Lista de processamentos
- [ ] Estatísticas básicas
- [ ] Botão de logout

### Routing (1 hora)
- [ ] Configurar `React Router`
- [ ] Página HOME
- [ ] Página LOGIN
- [ ] Página PROCESSAR
- [ ] Página HISTÓRICO
- [ ] Redirect não autenticado

### Validação
```bash
npm run dev
# Deve abrir em http://localhost:5173
```
- [ ] Frontend carrega
- [ ] Pode fazer login
- [ ] Pode fazer upload (após autenticar)
- [ ] Pode ver histórico

---

## 🐳 FASE 3: Deploy (Semana 3 - 4 horas)

### Leitura (30 min)
- [ ] Ler [docs/PLANO_IMPLEMENTACAO.md](./docs/PLANO_IMPLEMENTACAO.md) - FASE 3
- [ ] Ler [docs/DEPLOYMENT_UBUNTU.md](./docs/DEPLOYMENT_UBUNTU.md)
- [ ] Revisar Docker basics

### Docker Setup (1 hora)
- [ ] Criar `Dockerfile.backend`
- [ ] Criar `Dockerfile.frontend`
- [ ] Criar `docker-compose.yml`
- [ ] Build imagens locais
- [ ] Rodar `docker-compose up`

### Nginx Configuration (1 hora)
- [ ] Criar config `/etc/nginx/sites-available/renomeador`
- [ ] Reverse proxy para backend:8000
- [ ] Serve frontend estático
- [ ] Reload nginx

### SSL/TLS (1 hora)
- [ ] Instalar certbot
- [ ] Gerar certificado Let's Encrypt
- [ ] Renovação automática
- [ ] HTTPS funcionando

---

## 🚀 Fase 2: Adicionar Bradesco - ~3 horas

### Análise do PDF

- [ ] Obter PDF de exemplo Bradesco
- [ ] Identificar padrões de extração (regex)
- [ ] Documentar diferenças vs Sicredi

### Implementação

- [ ] Criar `backend/processors/bradesco.py`
- [ ] Implementar métodos: extrair_dados(), validar()
- [ ] Registrar no `ProcessadorFactory`
- [ ] Testar com PDF real

### Testes

- [ ] Criar `backend/tests/test_bradesco.py`
- [ ] Mínimo 5 testes
- [ ] `pytest` passa com sucesso

### Frontend (Opcional)

- [ ] Adicionar dropdown de banco
- [ ] POST com parâmetro `banco=bradesco`
- [ ] Testar fluxo completo

---

## 🎯 Fase 3: Refinements - ~2 horas

- [ ] Tratamento robusto de erros
- [ ] Logging detalhado
- [ ] Documentação de código
- [ ] README.md atualizado
- [ ] Exemplo de uso por banco

---

## 📝 Limpeza do Projeto (FEITO)

✅ Removido documentação desnecessária:
- ✅ SUMARIO_EXECUTIVO.md
- ✅ SUMARIO_VISUAL.md
- ✅ MAPA_DOCUMENTACAO.md
- ✅ CONTRIBUTING.md
- ✅ BACKEND_PRONTO.md
- ✅ REVISAO_CODIGO.md
- ✅ STATUS_FINAL.md
- ✅ COMANDOS_PRINCIPAIS.md
- ✅ COMO_RODAR.md
- ✅ GUIA_RAPIDO.md

✅ Removido testes/exemplos abandonados:
- ✅ exemplo_refatoracao.py
- ✅ test_refatoracao.py
- ✅ comprovantes.pdf

✅ Criado Makefile unificado
✅ Atualizado README.md

---

## 📖 Documentação Criada

✅ [REVISAO_ARQUITETURA.md](./REVISAO_ARQUITETURA.md) - Análise + recomendações  
✅ [docs/SICREDI_BOLETO.md](./docs/SICREDI_BOLETO.md) - Spec Sicredi  
✅ [docs/EXTENSIBILIDADE.md](./docs/EXTENSIBILIDADE.md) - Como adicionar banco
- [ ] Enable e start serviço
- [ ] Auto-restart configurado
- [ ] Logs acessíveis

### Validação
- [ ] Backend API respondendo
- [ ] Frontend carregando
- [ ] HTTPS funcional
- [ ] Auto-restart após reboot

---

## 🎁 FASE 4: Melhorias (Opcional - Semana 4+)

### Processamento Assíncrono (2 horas)
- [ ] Instalar Celery
- [ ] Setup Redis/RabbitMQ
- [ ] Fila de processamento
- [ ] Status real-time

### WebSocket Real-time (2 horas)
- [ ] Setup WebSocket
- [ ] Notificações ao vivo
- [ ] Barra de progresso
- [ ] Alertas de conclusão

### Monitoring (2 horas)
- [ ] Prometheus metrics
- [ ] Grafana dashboard
- [ ] Alertas automáticos
- [ ] Health checks

### CI/CD (2 horas)
- [ ] GitHub Actions workflow
- [ ] Testes automatizados
- [ ] Build automático
- [ ] Deploy automático

### Melhorias Menores (2 horas)
- [ ] Backup automático
- [ ] Rate limiting
- [ ] Caching
- [ ] Performance optimization

---

## 📊 Timeline Visual

```
HOJE          │ SEMANA 1  │ SEMANA 2  │ SEMANA 3  │ SEMANA 4+
──────────────┼───────────┼───────────┼───────────┼───────────
Prep (1h)     │ Backend   │ Frontend  │ Deploy    │ Melhorias
Setup (5min)  │ (8h)      │ (8h)      │ (4h)      │ (8h+)
Read (1h)     │           │           │           │
              │           │           │           │
TOTAL: 2h     │ 8h        │ 8h        │ 4h        │ 8h+
              │           │           │           │
              │ ✅ Ready  │ ✅ Ready  │ ✅ Live   │ 🎉 Premium
```

---

## 🔧 Troubleshooting Rápido

### Backend não inicia
```bash
cd backend
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

### Frontend não carrega
```bash
cd frontend
npm install
npm run dev
# Limpar: rm -rf node_modules package-lock.json && npm install
```

### Erro de CORS
- [ ] Verificar `backend/config.py` - CORS_ORIGINS
- [ ] Deve incluir http://localhost:5173

### Database bloqueado
```bash
rm data/app.db
cd backend && python -c "from database import Base, engine; Base.metadata.create_all(engine)"
```

### Portas já em uso
```bash
# Backend (8000)
lsof -i :8000 && kill -9 <PID>

# Frontend (5173)
lsof -i :5173 && kill -9 <PID>
```

---

## 📈 Métricas de Sucesso

### FASE 1 Completa
- ✅ Backend inicia sem erros
- ✅ Swagger carrega e funciona
- ✅ Testes passam (pytest)
- ✅ Cobertura ≥ 80%

### FASE 2 Completa
- ✅ Frontend carrega
- ✅ Login funciona
- ✅ Upload funciona
- ✅ Histórico mostra dados

### FASE 3 Completa
- ✅ Docker containers rodam
- ✅ Nginx reverse proxy OK
- ✅ HTTPS funcional
- ✅ Systemd service ativo

### FASE 4 (Opcional)
- ✅ Processamento assíncrono
- ✅ WebSocket em tempo real
- ✅ Monitoring ativo
- ✅ CI/CD pipeline

---

## 🎓 Links Úteis

| Tipo | Link | Descrição |
|------|------|-----------|
| 📋 Quick | [GUIA_RAPIDO.md](./GUIA_RAPIDO.md) | Cheat sheet em 5 min |
| 🚀 Setup | [QUICKSTART.md](./QUICKSTART.md) | Como rodar local |
| 🏗️ Arch | [docs/ARQUITETURA_MELHORADA.md](./docs/ARQUITETURA_MELHORADA.md) | Design técnico |
| 📝 Plan | [docs/PLANO_IMPLEMENTACAO.md](./docs/PLANO_IMPLEMENTACAO.md) | Step-by-step |
| 🚀 Prod | [docs/DEPLOYMENT_UBUNTU.md](./docs/DEPLOYMENT_UBUNTU.md) | Ubuntu deployment |
| 📊 Summary | [RESUMO_FINAL.md](./RESUMO_FINAL.md) | O que foi feito |
| 🗺️ Nav | [MAPA_DOCUMENTACAO.md](./MAPA_DOCUMENTACAO.md) | Índice geral |

---

## ✨ Pontos Importantes

1. **Leia antes de implementar** - Documentação salva tempo
2. **Teste após cada fase** - Evita problemas no final
3. **Comita regularmente** - `git commit -m "FASE 1: Auth implementado"`
4. **Mantenha logs** - Salve outputs de testes e deploys
5. **Backup antes de deploy** - `cp -r data/ data.backup/`

---

## 🚀 Comece AGORA!

```bash
# 1. Leia
cat GUIA_RAPIDO.md

# 2. Setup
bash setup.sh

# 3. Implemente
cat QUICKSTART.md

# 4. Sucesso!
cd backend && python main.py  # Terminal 1
cd frontend && npm run dev     # Terminal 2
```

**Boa sorte! 🎉**

---

*Última atualização: 25 de maio de 2026*  
*Desenvolvido com ❤️ para seu sucesso*
