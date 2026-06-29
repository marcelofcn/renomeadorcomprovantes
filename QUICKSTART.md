# 🚀 Quick Start - Desenvolvimento Local

## Pré-requisitos

- Python 3.11+
- Node.js 20+
- Git

## Setup Rápido (5 minutos)

### Backend

```bash
# 1. Entrar no diretório backend
cd backend

# 2. Criar virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou: .venv\Scripts\activate  # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Criar .env
cp .env.example .env

# 5. Inicializar database
python3 -c "from database import init_db; init_db()"

# 6. Rodar servidor
python main.py
```

Backend rodando em: http://localhost:8000
Documentação API: http://localhost:8000/docs

### Frontend

```bash
# 1. Entrar no diretório frontend
cd frontend

# 2. Instalar dependências
npm install

# 3. Rodar servidor de desenvolvimento
npm run dev
```

Frontend rodando em: http://localhost:5173

## Estrutura do Projeto

```
renomeadorcomprovantes/
├── backend/               # API FastAPI
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── utils/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   └── requirements.txt
│
├── frontend/              # Interface Vite + React
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── data/                  # Dados (uploads, processados, etc)
├── docs/                  # Documentação
└── logs/                  # Logs da aplicação
```

## Próximos Passos

1. Ler `docs/SUMARIO_NOVA_ARQUITETURA.md`
2. Ler `docs/PLANO_IMPLEMENTACAO.md`
3. Começar a implementar!

## Troubleshooting

### ModuleNotFoundError
```bash
# Verificar que venv está ativado
source .venv/bin/activate
pip install -r requirements.txt
```

### npm ERR! 404
```bash
cd frontend
npm cache clean --force
npm install
```

### Port already in use
```bash
# Backend (mude em config.py)
# Frontend (adicione: npm run dev -- --port 5174)
```

---

Mais detalhes em `docs/DESENVOLVIMENTO.md` (será criado durante dev)
