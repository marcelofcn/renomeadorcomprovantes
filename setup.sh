#!/bin/bash

# 🚀 Script de Setup Automático - Renomeador de Comprovantes
# Data: 25 de maio de 2026
# Função: Criar estrutura inicial do projeto

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Setup Automático - Renomeador de Comprovantes          ║"
echo "║   Nova Arquitetura (FastAPI + Vite + React)              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verifica se está no diretório correto
if [ ! -d "backend" ] && [ ! -f "setup.sh" ]; then
    echo -e "${YELLOW}⚠️  Execute este script na raiz do projeto!${NC}"
    echo "Uso: cd /home/house/developer/renomeadorcomprovantes && bash setup.sh"
    exit 1
fi

# ════════════════════════════════════════════════════════════════
# 1. Criar estrutura de diretórios
# ════════════════════════════════════════════════════════════════

echo -e "${BLUE}📁 Criando estrutura de diretórios...${NC}"

# Backend
mkdir -p backend/{models,routes,services,utils}

# Frontend
mkdir -p frontend/src/{components,pages,services,hooks,styles}

# Dados
mkdir -p data/{uploads,processados,histórico}

# Logs
mkdir -p logs

echo -e "${GREEN}✅ Estrutura criada${NC}"

# ════════════════════════════════════════════════════════════════
# 2. Backend - Criar arquivos base
# ════════════════════════════════════════════════════════════════

echo -e "${BLUE}🐍 Configurando Backend (FastAPI)...${NC}"

# requirements.txt
cat > backend/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
email-validator==2.1.0
python-multipart==0.0.6
pydantic-extra-types==2.3.0
pytest==7.4.3
httpx==0.25.1
python-dotenv==1.0.0
pdfplumber>=0.9.0
PyPDF2>=3.0.0
EOF

# .env.example
cat > backend/.env.example << 'EOF'
# App
APP_NAME=Renomeador de Comprovantes
APP_VERSION=1.0.0

# Server
API_HOST=0.0.0.0
API_PORT=8000

# JWT (gerar chave segura com: python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
SECRET_KEY=sua-chave-secreta-muito-segura-aqui-mudar-em-producao
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Database
DATABASE_URL=sqlite:///./data/app.db

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost:3000

# Email (opcional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seu-email@gmail.com
SMTP_PASSWORD=sua-senha
EOF

echo -e "${GREEN}✅ Backend configurado${NC}"

# ════════════════════════════════════════════════════════════════
# 3. Frontend - Criar arquivos base
# ════════════════════════════════════════════════════════════════

echo -e "${BLUE}⚛️  Configurando Frontend (Vite + React)...${NC}"

# package.json
cat > frontend/package.json << 'EOF'
{
  "name": "renomeador-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.2",
    "react-router-dom": "^6.18.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.36",
    "@types/react-dom": "^18.2.14",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.2.2",
    "vite": "^5.0.0",
    "tailwindcss": "^3.3.6",
    "postcss": "^8.4.31",
    "autoprefixer": "^10.4.16"
  }
}
EOF

# tsconfig.json
cat > frontend/tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
EOF

# vite.config.ts
cat > frontend/vite.config.ts << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
EOF

echo -e "${GREEN}✅ Frontend configurado${NC}"

# ════════════════════════════════════════════════════════════════
# 4. Criar arquivo de documentação de início rápido
# ════════════════════════════════════════════════════════════════

echo -e "${BLUE}📚 Criando documentação...${NC}"

cat > QUICKSTART.md << 'EOF'
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
EOF

echo -e "${GREEN}✅ Documentação criada${NC}"

# ════════════════════════════════════════════════════════════════
# 5. Criar .gitignore
# ════════════════════════════════════════════════════════════════

echo -e "${BLUE}📝 Configurando Git...${NC}"

cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Node
node_modules/
npm-debug.log
yarn-error.log
.npm/

# Vite
dist/
.vite/
.svelte-kit/

# Environment
.env
.env.local
.env.*.local

# Database
*.db
*.sqlite3
*.sqlite

# Logs
logs/
*.log

# Upload/Output
data/uploads/*
data/processados/*
!data/uploads/.gitkeep
!data/processados/.gitkeep

# OS
.DS_Store
Thumbs.db
EOF

echo -e "${GREEN}✅ Git configurado${NC}"

# ════════════════════════════════════════════════════════════════
# 6. Resumo Final
# ════════════════════════════════════════════════════════════════

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║            ✅ Setup Completo!                              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${BLUE}📂 Estrutura criada:${NC}"
echo "   ├── backend/         (Python FastAPI)"
echo "   ├── frontend/        (React Vite)"
echo "   ├── data/            (Uploads, processados)"
echo "   ├── docs/            (Documentação)"
echo "   └── logs/            (Logs)"
echo ""

echo -e "${BLUE}📚 Próximos passos:${NC}"
echo "   1. Ler: cat QUICKSTART.md"
echo "   2. Ler: cat docs/SUMARIO_NOVA_ARQUITETURA.md"
echo "   3. Ler: cat docs/PLANO_IMPLEMENTACAO.md"
echo ""

echo -e "${BLUE}🚀 Para começar a desenvolver:${NC}"
echo ""
echo "   Backend:"
echo "   ┌─────────────────────────────────────────┐"
echo "   │ cd backend                              │"
echo "   │ python3 -m venv .venv                  │"
echo "   │ source .venv/bin/activate              │"
echo "   │ pip install -r requirements.txt        │"
echo "   │ cp .env.example .env                   │"
echo "   │ python main.py                         │"
echo "   └─────────────────────────────────────────┘"
echo ""
echo "   Frontend (novo terminal):"
echo "   ┌─────────────────────────────────────────┐"
echo "   │ cd frontend                             │"
echo "   │ npm install                             │"
echo "   │ npm run dev                             │"
echo "   └─────────────────────────────────────────┘"
echo ""

echo -e "${GREEN}✨ Tudo pronto! Bom desenvolvimento! 🎉${NC}"
echo ""
