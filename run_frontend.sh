#!/bin/bash
# Script para testar o frontend
# Use: bash run_frontend.sh

echo "🚀 Iniciando Renomeador de Comprovantes Frontend..."
echo ""

cd "$(dirname "$0")/frontend" || exit 1
echo "📦 Instalando dependências..."
npm install

# Rodar
echo "🔄 Frontend rodando em http://localhost:5173"
echo ""
echo "Pressione Ctrl+C para parar"
echo ""

npm run dev






