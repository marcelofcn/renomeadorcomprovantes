# 🚀 Plano de Implementação - Nova Arquitetura

**Data:** 25 de maio de 2026  
**Versão:** 1.0

---

## 📋 Overview

Transformar projeto CLI em **aplicação web moderna** com:
- Backend FastAPI (Python)
- Frontend Vite + React + TypeScript
- Banco de dados SQLite/PostgreSQL
- Docker para deployment
- Deploy em Ubuntu 22.04 LTS

**Estimativa total:** 3-4 semanas

---

## 📅 Timeline

```
Semana 1: Backend + Models (5-8 horas)
├─ Setup estrutura FastAPI
├─ Criar models (User, Comprovante)
├─ Implementar auth (JWT)
├─ Criar routes básicas
└─ Testes unitários

Semana 2: Frontend + Integração (5-8 horas)
├─ Setup Vite + React + TypeScript
├─ Componentes básicos
├─ Integração API
├─ Autenticação no frontend
└─ Testes

Semana 3: Produção + Deploy (4-6 horas)
├─ Docker setup
├─ Nginx reverse proxy
├─ SSL/TLS
├─ Deploy Ubuntu
└─ Systemd service

Semana 4: Melhorias (opcional)
├─ CI/CD pipeline
├─ Processamento assíncrono
├─ Real-time updates
└─ Monitoramento
```

---

## ✅ FASE 1: Backend (5-8 horas)

### 1.1 Setup Inicial (30 min)

```bash
# Criar estrutura de diretórios
mkdir -p backend/{models,routes,services,utils}
mkdir -p frontend/{src/{components,pages,services,hooks,styles}}
mkdir -p docs data/uploads data/processados
```

### 1.2 Backend - Python Setup (1h)

**Arquivo:** `backend/requirements.txt`

```
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
```

**Arquivo:** `backend/config.py`

```python
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    # App
    app_name: str = "Renomeador de Comprovantes"
    app_version: str = "1.0.0"
    
    # Servidor
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:5174"
    
    # JWT
    secret_key: str = "sua-chave-secreta-muito-segura-aqui"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Caminhos
    upload_dir: str = str(BASE_DIR / "data" / "uploads")
    output_dir: str = str(BASE_DIR / "data" / "processados")
    
    # Database
    database_url: str = f"sqlite:///{BASE_DIR}/data/app.db"
    # Para PostgreSQL: database_url = "postgresql://user:pass@localhost/dbname"
    
    @property
    def cors_origins_list(self):
        return [x.strip() for x in self.cors_origins.split(",")]

settings = Settings()
```

### 1.3 Backend - Database Setup (1h)

**Arquivo:** `backend/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 1.4 Backend - Models (2h)

**Arquivo:** `backend/models/__init__.py`

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    comprovantes = relationship("Comprovante", back_populates="usuario")

class Comprovante(Base):
    __tablename__ = "comprovantes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    arquivo_original = Column(String(255))
    arquivo_renomeado = Column(String(255))
    tipo = Column(String(50))  # PIX, Boleto, DARF, etc
    descricao = Column(String(255))
    valor = Column(Float)
    data_pagamento = Column(DateTime)
    status = Column(String(50), default="processando")  # processando, sucesso, erro
    mensagem_erro = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    usuario = relationship("User", back_populates="comprovantes")
```

### 1.5 Backend - Services (2h)

**Arquivo:** `backend/services/auth.py`

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TokenData(BaseModel):
    username: Optional[str] = None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)
```

### 1.6 Backend - Routes (2h)

**Arquivo:** `backend/routes/auth.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel
from database import get_db
from models import User
from services.auth import create_access_token, get_password_hash, verify_password
from config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=Token)
def register(user: UserRegister, db: Session = Depends(get_db)):
    # Verificar se usuário já existe
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Usuário já existe")
    
    # Criar novo usuário
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=get_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Gerar token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": new_user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Buscar usuário
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    # Verificar senha
    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    # Gerar token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": db_user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
```

### 1.7 Backend - Main (30 min)

**Arquivo:** `backend/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import init_db
from routes.auth import router as auth_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Init DB
init_db()

# Routes
app.include_router(auth_router)

@app.get("/api/health")
def health():
    return {"status": "online"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.api_host, port=settings.api_port, reload=True)
```

---

## ✅ FASE 2: Frontend (5-8 horas)

### 2.1 Setup Vite + React (1h)

```bash
# Criar projeto Vite
cd frontend
npm create vite@latest . -- --template react-ts
npm install
```

### 2.2 Dependências Frontend (30 min)

**Arquivo:** `frontend/package.json`

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.2",
    "react-router-dom": "^6.18.0",
    "tailwindcss": "^3.3.6"
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
  },
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  }
}
```

### 2.3 Componentes Base (2h)

**Arquivo:** `frontend/src/App.tsx`

```typescript
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Dashboard />} />
        <Route path="/upload" element={<Upload />} />
      </Routes>
    </Router>
  );
}

export default App;
```

### 2.4 Serviços API (2h)

**Arquivo:** `frontend/src/services/api.ts`

```typescript
import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// Adicionar token ao header
API.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default API;
```

---

## ✅ FASE 3: Produção (4-6 horas)

### 3.1 Docker

**Arquivo:** `Dockerfile`

```dockerfile
# Backend
FROM python:3.11-slim as backend
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Frontend
FROM node:20-alpine as frontend-build
WORKDIR /app
COPY frontend/package*.json .
RUN npm install
COPY frontend/ .
RUN npm run build

# Production
FROM nginx:alpine
COPY --from=frontend-build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 3.2 Docker Compose

**Arquivo:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./data/app.db
    volumes:
      - ./data:/app/data
    networks:
      - app-network

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "5173:5173"
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
      - frontend
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

### 3.3 Ubuntu Systemd Service

**Arquivo:** `/etc/systemd/system/renomeador.service`

```ini
[Unit]
Description=Renomeador de Comprovantes
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/home/www/renomeadorcomprovantes
ExecStart=/usr/bin/python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 📊 Checklist de Implementação

### FASE 1 Backend
- [ ] Criar estrutura FastAPI
- [ ] Setup database (SQLAlchemy)
- [ ] Models (User, Comprovante)
- [ ] Auth (JWT)
- [ ] Routes (auth)
- [ ] Testes unitários
- [ ] Documentação API

### FASE 2 Frontend
- [ ] Setup Vite + React + TypeScript
- [ ] Componentes base
- [ ] Páginas (Login, Dashboard, Upload)
- [ ] Integração API
- [ ] Autenticação
- [ ] Testes

### FASE 3 Produção
- [ ] Docker setup
- [ ] Nginx reverse proxy
- [ ] SSL/TLS
- [ ] Deploy Ubuntu
- [ ] Systemd service
- [ ] Backup automático

---

## 🎯 Decisões Críticas

### 1. Database
```
SQLite: ✅ Desenvolvimento, demo
PostgreSQL: ✅ Produção, múltiplos usuários
```

Recomendação: **SQLite para começar, migrar para PostgreSQL depois**

### 2. Autenticação
```
JWT (stateless): ✅ Escalável
Sessions (stateful): ❌ Não escalável
```

Recomendação: **JWT**

### 3. Processamento
```
Síncrono: ✅ MVP
Assíncrono (Celery): ⏰ Depois (Fase 4)
```

Recomendação: **Síncrono para Fase 1, Celery na Fase 4**

---

## 📈 Estimativas de Esforço

| Tarefa | Horas | Dificuldade |
|--------|-------|------------|
| Backend setup | 8 | ⭐⭐ |
| Frontend setup | 8 | ⭐⭐ |
| Docker | 4 | ⭐⭐ |
| Deploy Ubuntu | 4 | ⭐⭐⭐ |
| **Total** | **24** | - |

**Total: 3-4 semanas com 6-8h/dia**

---

## 🚀 Como Começar

### Passo 1: Ler documentação
```bash
cat docs/ARQUITETURA_MELHORADA.md
```

### Passo 2: Setup local
```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Passo 3: Rodar localmente
```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Passo 4: Acessar
```
Backend:   http://localhost:8000/docs (Swagger)
Frontend:  http://localhost:5173
```

---

## 📞 Próximos Passos

1. ✅ Revisar ARQUITETURA_MELHORADA.md
2. ⏭️ Iniciar FASE 1 (Backend)
3. ⏭️ Criar estrutura e arquivos
4. ⏭️ Implementar funcionalidades

**Quer que eu comece a criar os arquivos?** 🚀

---

*Último update: 25 de maio de 2026*
