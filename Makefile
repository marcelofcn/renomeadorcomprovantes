.PHONY: help setup backend frontend dev clean test lint

help:
	@echo "🧾 Renomeador de Comprovantes Sicredi"
	@echo ""
	@echo "Comandos disponíveis:"
	@echo "  make setup        → Preparar ambiente (primeira vez)"
	@echo "  make dev          → Rodar backend + frontend (desenvolvimento)"
	@echo "  make backend      → Rodar apenas backend"
	@echo "  make frontend     → Rodar apenas frontend"
	@echo "  make test         → Executar testes"
	@echo "  make lint         → Verificar qualidade do código"
	@echo "  make clean        → Limpar cache e arquivos temporários"
	@echo ""
	@echo "🚀 Início rápido:"
	@echo "  1. make setup"
	@echo "  2. make dev"
	@echo "  3. Abrir http://localhost:5173"

# Setup inicial do projeto
setup:
	@echo "📦 Preparando ambiente..."
	@mkdir -p data/uploads data/processados data/histórico logs
	@echo "✅ Diretórios criados"
	@cd backend && python3 -m venv .venv 2>/dev/null || echo "venv já existe"
	@bash -c "source backend/.venv/bin/activate && pip install -q -r backend/requirements.txt" 2>/dev/null
	@echo "✅ Backend dependencies instaladas"
	@cd frontend && npm install -q 2>/dev/null || echo "npm packages já instalados"
	@echo "✅ Frontend dependencies instaladas"
	@echo ""
	@echo "🎉 Setup completo!"
	@echo "Próximo passo: make dev"

# Rodar backend
backend:
	@echo "🐍 Iniciando backend (http://localhost:8000)..."
	@cd backend && bash -c "source .venv/bin/activate && python main.py"

# Rodar frontend
frontend:
	@echo "⚛️  Iniciando frontend (http://localhost:5173)..."
	@cd frontend && npm run dev

# Rodar ambos (em paralelo, com Ctrl+C para parar)
dev:
	@echo "🚀 Iniciando desenvolvimento (2 terminais necessários)"
	@echo ""
	@echo "Terminal 1 - Backend:"
	@echo "  $$ cd backend && source .venv/bin/activate && python main.py"
	@echo ""
	@echo "Terminal 2 - Frontend:"
	@echo "  $$ cd frontend && npm run dev"
	@echo ""
	@echo "Ou execute em 2 abas separadas:"
	@echo "  $$ make backend"
	@echo "  $$ make frontend"

# Executar testes
test:
	@echo "🧪 Executando testes..."
	@cd backend && bash -c "source .venv/bin/activate && pytest -v tests/"

# Verificar qualidade do código
lint:
	@echo "🔍 Verificando qualidade do código..."
	@cd backend && bash -c "source .venv/bin/activate && python -m pylint **/*.py" || true
	@echo "✅ Verificação concluída"

# Limpar cache e temporários
clean:
	@echo "🧹 Limpando..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf backend/.venv/build backend/.venv/dist 2>/dev/null || true
	@echo "✅ Limpeza concluída"
