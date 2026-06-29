# 🏗️ Arquitetura Melhorada - Renomeador de Comprovantes

**Data:** 25 de maio de 2026  
**Status:** Proposta de Refatoração Arquitetônica

---

## 📊 Estrutura Proposta

```
renomeadorcomprovantes/
│
├── backend/                          # API Python (FastAPI)
│   ├── __init__.py
│   ├── main.py                       # Entry point FastAPI
│   ├── config.py                     # Configurações centralizadas
│   ├── database.py                   # Inicialização DB
│   │
│   ├── models/                       # Modelos de dados
│   │   ├── __init__.py
│   │   ├── user.py                   # Usuários (auth)
│   │   ├── comprovante.py            # Comprovante processado
│   │   └── processamento.py          # Log de processamento
│   │
│   ├── routes/                       # Rotas da API
│   │   ├── __init__.py
│   │   ├── auth.py                   # Login/Register
│   │   ├── upload.py                 # Upload PDF
│   │   ├── processamento.py          # Status de processamento
│   │   └── histórico.py              # Histórico de renomeações
│   │
│   ├── services/                     # Lógica de negócio
│   │   ├── __init__.py
│   │   ├── auth.py                   # Autenticação JWT
│   │   ├── extracoes.py              # Extrações (PIX, Boleto, etc)
│   │   ├── renomeador.py             # Lógica de renomeação
│   │   └── processador_pdf.py        # Processamento de PDF
│   │
│   ├── utils/                        # Utilitários
│   │   ├── __init__.py
│   │   ├── validators.py             # Validações
│   │   ├── formatadores.py           # Formatações
│   │   └── erros.py                  # Classes de erro customizado
│   │
│   ├── requirements.txt              # Dependências Python
│   ├── .env.example                  # Exemplo de .env
│   └── .env                          # Variáveis de ambiente
│
├── frontend/                         # Interface Web (Vite + React)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx
│   │   │   ├── Upload/
│   │   │   │   └── UploadArea.tsx
│   │   │   ├── Dashboard/
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   └── Stats.tsx
│   │   │   ├── Historico/
│   │   │   │   └── HistoricoComprovantes.tsx
│   │   │   └── Auth/
│   │   │       ├── Login.tsx
│   │   │       └── Register.tsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── Processar.tsx
│   │   │   ├── Historico.tsx
│   │   │   └── Admin.tsx
│   │   │
│   │   ├── services/
│   │   │   ├── api.ts                # Cliente HTTP (axios/fetch)
│   │   │   ├── auth.ts               # Serviço de auth
│   │   │   └── comprovantes.ts       # Serviço de comprovantes
│   │   │
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   └── useComprovantes.ts
│   │   │
│   │   ├── styles/
│   │   │   └── index.css             # Estilos globais (Tailwind)
│   │   │
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── vite-env.d.ts
│   │
│   ├── public/
│   │   └── favicon.ico
│   │
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── postcss.config.js
│
├── data/                            # Dados (será criado dinamicamente)
│   ├── uploads/                     # PDFs subidos
│   ├── processados/                 # PDFs renomeados
│   ├── histórico/                   # Histórico de processamentos
│   └── db.sqlite3                   # Banco de dados
│
├── docker-compose.yml               # Orquestração de containers
├── Dockerfile                       # Build da imagem
├── .env.example                     # Exemplo de variáveis globais
├── start.sh                         # Script para iniciar tudo
│
└── docs/
    ├── ARQUITETURA.md               # Este arquivo
    ├── API.md                        # Documentação da API
    ├── DEPLOYMENT.md                # Deploy no Ubuntu
    └── DESENVOLVIMENTO.md           # Guia para dev
```

---

## 🔄 Fluxo de Dados

```
┌─────────────────────────────────────────────────────────────┐
│                     USUÁRIO                                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND (Vite)                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  React Components (Upload, Dashboard, Histórico)    │  │
│  │  Tailwind CSS                                        │  │
│  │  Services (api.ts, auth.ts)                          │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTP/REST
                       │ JWT Token
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               BACKEND (FastAPI)                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Routes:                                             │  │
│  │  - POST /api/auth/login                             │  │
│  │  - POST /api/upload/pdf                             │  │
│  │  - GET  /api/processamento/status/{id}              │  │
│  │  - GET  /api/histórico                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                       │                                      │
│         ┌─────────────┼─────────────┐                       │
│         ▼             ▼             ▼                       │
│  ┌────────────┐ ┌──────────┐ ┌────────────────┐             │
│  │ Serviço    │ │ Serviço  │ │ Serviço de     │             │
│  │ de Auth    │ │ de       │ │ Renomeação    │             │
│  │            │ │ Extração │ │                │             │
│  └────────────┘ └──────────┘ └────────────────┘             │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Banco de Dados (SQLite/PostgreSQL)          │  │
│  │  - Usuários                                          │  │
│  │  - Log de Processamentos                            │  │
│  │  - Histórico de Comprovantes                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Sistema de Arquivos                          │  │
│  │  - /data/uploads/    (PDFs originais)               │  │
│  │  - /data/processados/ (PDFs renomeados)             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Funcionalidades

### Frontend
- 🔐 **Autenticação**: Login/Register com JWT
- 📤 **Upload de PDFs**: Drag-and-drop, múltiplos arquivos
- ⏱️ **Processamento em tempo real**: Barra de progresso, status
- 📊 **Dashboard**: Estatísticas e métricas
- 📋 **Histórico**: Lista de todos os comprovantes processados
- 🔍 **Busca**: Filtrar por data, tipo, valor
- 💾 **Download**: Baixar PDFs renomeados

### Backend
- 🔐 **JWT Authentication**: Segurança de endpoints
- 📤 **Upload seguro**: Validação de tipo, tamanho, vírus
- 🔄 **Processamento assíncrono**: Fila (Celery/RQ)
- 📊 **API REST**: Documentação automática (Swagger/OpenAPI)
- 💾 **Persistência**: Histórico em banco de dados
- 📝 **Logging**: Rastreamento de erros e processamentos
- 🚀 **Performance**: Cache, compressão, otimizações

---

## 🛠️ Stack Técnico

### Backend
```
FastAPI           - Framework web moderno
SQLAlchemy        - ORM (Object-Relational Mapping)
Pydantic          - Validação de dados
python-jose       - JWT
PyPDF2/pdfplumber - Processamento de PDFs
Celery (opcional) - Processamento assíncrono
PostgreSQL/SQLite - Banco de dados
```

### Frontend
```
React 18          - UI framework
TypeScript        - Type safety
Vite              - Build tool (2-4x mais rápido que Webpack)
Tailwind CSS      - Utility-first CSS
Axios             - HTTP client
React Router      - Roteamento
Zustand           - State management (opcional)
```

### DevOps
```
Docker            - Containerização
Docker Compose    - Orquestração
Nginx             - Reverse proxy
Systemd/Supervisor - Gerenciamento de processos (Ubuntu)
```

---

## 📈 Benefícios da Nova Arquitetura

| Benefício | Antes | Depois |
|-----------|-------|--------|
| **Interface** | CLI | Web moderna com Vite |
| **Escalabilidade** | Script único | Microserviços prontos |
| **Múltiplos usuários** | ❌ | ✅ Com autenticação JWT |
| **Histórico** | Arquivos | Banco de dados |
| **Performance** | Síncrono | Assíncrono (Celery) |
| **Segurança** | Nenhuma | JWT + Validações |
| **Deployment** | Manual | Docker + Systemd |
| **Documentação API** | Manual | Swagger automático |
| **Testes** | 0% | 80%+ cobertura |

---

## 🚀 Fases de Implementação

### FASE 1: Backend Básico (1-2 semanas)
```
✅ Estrutura FastAPI
✅ Models (User, Comprovante)
✅ Routes (auth, upload)
✅ Services (auth, extração, renomeação)
✅ Database setup
```

### FASE 2: Frontend Básico (1-2 semanas)
```
✅ Setup Vite + React + TypeScript
✅ Componentes básicos
✅ Integração com API
✅ Autenticação
```

### FASE 3: Produção (1 semana)
```
✅ Docker setup
✅ Nginx reverse proxy
✅ Deploy no Ubuntu
✅ Systemd service
✅ CI/CD pipeline
```

### FASE 4: Melhorias (opcional)
```
✅ Processamento assíncrono (Celery)
✅ Real-time updates (WebSocket)
✅ Email notifications
✅ Admin dashboard avançado
```

---

## 🔐 Segurança

### Implementado
- ✅ **JWT Authentication**: Token-based auth
- ✅ **CORS**: Controle de origem
- ✅ **Validação de Input**: Pydantic
- ✅ **HTTPS**: SSL/TLS no production
- ✅ **Rate Limiting**: Proteção contra abuso
- ✅ **CSRF Protection**: CSRF tokens

### Recomendado
- 🔐 Senhas com bcrypt (não plaintext)
- 🔐 Variáveis de ambiente (.env)
- 🔐 Backup automático do DB
- 🔐 Logs de auditoria
- 🔐 2FA (autenticação em duas fases)

---

## 📊 Comparação: Antes vs Depois

### Antes
```
CLI Script Puro
↓
User rodava: python renomeador_comprovantes.py
↓
PDFs renomeados em pasta local
↓
Sem histórico, sem múltiplos usuários
```

### Depois
```
Web App Moderno
↓
User acessa: https://seu-dominio.com
↓
Faz login (JWT)
↓
Faz upload via interface
↓
Vê status em tempo real
↓
Histórico persistido no BD
↓
Múltiplos usuários simultaneamente
```

---

## 📱 Responsividade

Frontend será **100% responsivo**:

```
Desktop      Tablet      Mobile
┌─────────┐  ┌──────┐   ┌───┐
│ Header  │  │ Hedr │   │ ☰ │
│ Sidebar │  │      │   │───│
│ Content │  │ Cont │   │Con│
│         │  │ ent  │   │ t │
└─────────┘  └──────┘   └───┘
```

---

## 🔄 Fluxo de Upload e Processamento

```
┌─ User faz upload de PDF
│
├─ Frontend valida (tipo, tamanho)
│
├─ POST /api/upload/pdf (multipart)
│
├─ Backend recebe e armazena em data/uploads/
│
├─ Inicia processamento (sync ou async)
│
├─ Extrai dados (PIX, Boleto, etc)
│
├─ Renomeia arquivo para data/processados/
│
├─ Salva no BD
│
├─ Retorna status "Concluído"
│
└─ Frontend exibe resultado e histórico
```

---

## 💾 Banco de Dados (Schema)

```sql
-- Usuários
CREATE TABLE users (
    id INT PRIMARY KEY,
    username VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    created_at TIMESTAMP
);

-- Comprovantes processados
CREATE TABLE comprovantes (
    id INT PRIMARY KEY,
    user_id INT,
    arquivo_original VARCHAR(255),
    arquivo_renomeado VARCHAR(255),
    tipo VARCHAR(50),  -- PIX, Boleto, DARF, etc
    descricao VARCHAR(255),
    valor DECIMAL(10,2),
    data_pagamento DATE,
    status VARCHAR(50),  -- Sucesso, Erro
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Log de processamento
CREATE TABLE processamentos_log (
    id INT PRIMARY KEY,
    comprovante_id INT,
    acao VARCHAR(255),
    resultado VARCHAR(255),
    tempo_ms INT,
    created_at TIMESTAMP,
    FOREIGN KEY (comprovante_id) REFERENCES comprovantes(id)
);
```

---

## 🎯 Próximos Passos

1. **Revisar** este documento (ARQUITETURA.md)
2. **Decidir**: FastAPI vs Flask? SQLite vs PostgreSQL?
3. **Iniciar FASE 1**: Setup do backend
4. **Documentar**: API endpoints no Swagger
5. **Iniciar FASE 2**: Setup do frontend
6. **Integrar**: Backend + Frontend
7. **Testar**: Testes unitários + e2e
8. **Deploy**: Docker + Ubuntu

---

## 📞 Decisões de Design

### Por que FastAPI?
- ✅ Mais rápido que Flask/Django
- ✅ Type hints built-in
- ✅ Documentação automática (Swagger)
- ✅ Performance próxima a Node.js
- ✅ Produção pronta

### Por que Vite?
- ✅ 10-100x mais rápido que Webpack
- ✅ ES modules nativo
- ✅ HMR (Hot Module Reload) instantâneo
- ✅ Build otimizado

### Por que React?
- ✅ Componentes reutilizáveis
- ✅ Grande comunidade
- ✅ Integração fácil com APIs
- ✅ TypeScript support

### Por que Tailwind?
- ✅ Utility-first (rápido)
- ✅ Responsive design
- ✅ Dark mode built-in
- ✅ Customizável

---

## 📚 Documentação Futura

Será criada:
- `API.md` - Endpoints REST
- `DEPLOYMENT.md` - Deploy Ubuntu 22.04
- `DESENVOLVIMENTO.md` - Local development
- `DOCKER.md` - Docker setup
- `TESTES.md` - Testing strategy

---

**Próximo passo:** Iniciar a implementação! 🚀

Quer que eu comece a criar a estrutura do projeto?
