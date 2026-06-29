#!/bin/bash
# Script para testar o backend
# Use: bash run_backend.sh

echo "🚀 Iniciando Renomeador de Comprovantes Backend..."
echo ""

cd /home/house/developer/renomeadorcomprovantes

# Ativar virtual environment
source .venv/bin/activate

# Instalar dependencies se necessário
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Instalando dependências..."
    pip install -r requirements.txt
fi

# Ir para backend
cd backend

# Rodar
echo "🔄 Backend rodando em http://localhost:8000"
echo "📚 Documentação em http://localhost:8000/docs"
echo ""
echo "Pressione Ctrl+C para parar"
echo ""

python main.py
