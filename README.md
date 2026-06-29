# 📑 Relatório Técnico: Renomeador de Comprovantes Inteligente v2.1

## 1. Visão Geral
Sistema Fullstack desenvolvido para processar lotes de comprovantes bancários (PDF), realizar o recorte de páginas, extração de metadados via OCR/Texto, classificação financeira (Pagamentos vs. Transferências Interunidades) e organização cronológica.

## 2. Stack Tecnológica
Backend: Python 3.10+ (FastAPI).
Extração: pdfplumber (Texto) e PyPDF2 (Manipulação de arquivos).
Persistência: SQLite com ORM SQLAlchemy.
Frontend: React 18 + TypeScript + Vite.
Comunicação: REST API (JSON).

## 3. Arquitetura de Dados e Arquivos
O sistema utiliza uma estrutura de pastas na raiz do projeto para persistência física:
/data/app.db: Banco de dados relacional.
/data/processados/: Repositório de arquivos renomeados (AAAA-MM-DD_BANCO_ID_VALOR.pdf).
/data/uploads/: Buffer temporário de upload (limpo automaticamente).
Modelo de Dados (Comprovante):
Colunas principais: bank, source_path (Conta Origem), dest_account (Unidade Destino), amount, date (ISO), comprovante_type.

## 4. Inteligência de Processamento (pdf_processing.py)
O motor de extração possui lógicas específicas para três grandes bancos:
A. Sicredi
Tipos: Boletos, Tributos (IPTU, ISS, ICMS), Consumo (VIVO, etc) e DARF.
Diferencial: Captura do número do documento DARF em layouts variáveis e limpeza de sufixos como "COD BARRAS".
B. Bradesco (Net Empresa / Office Banking)
Tipos: Boletos e Tributos Estaduais/Municipais (DAE, DARE, DAR).
Diferencial: "Scanner de Órgãos" que identifica a UF (BA, SP, MT, DF, CE) e Prefeituras mesmo quando o rótulo está desalinhado no PDF.
C. Banco do Brasil (SISBB)
Tipos: Pagamentos (IPVA) e Transferências entre filiais.
Diferencial: Ignora o cabeçalho de impressão (data de emissão) para capturar a data real da transação. Detecta transferências para o CNPJ radical 04.251.333.

## 5. Funcionalidades do Dashboard
Filtros Multi-nível: Banco, Unidade (Conta), Ano, Mês e Dia.
Modo Pagamentos: Agrupamento por lote diário (Cards) com função de Download em ZIP gerado em tempo real.
Modo Transferências: Tabela de conciliação com mapeamento "De -> Para" baseado no UNIDADES_MAP (traduzindo contas para nomes como "Aracaju", "Matriz", etc).
Trava de Duplicidade: O sistema impede o reprocessamento da mesma transação, verificando a combinação de Banco+Conta+Data+Valor+Identificador.

### 🛠 Guia de Comit e Deploy (Git)
Para subir o projeto para o GitHub e posteriormente para o servidor:

# 1. Preparar o .gitignore
Certifique-se de ignorar os dados sensíveis e os arquivos processados:
code
Text
.venv/
__pycache__/
data/*.db
data/processados/*.pdf
data/uploads/*.pdf
node_modules/
dist/
.env

# 2. Comandos para o Git (Terminal)
code
Bash
git init
git add .
git commit -m "feat: implementacao completa multibanco, filtros avancados e gestao de transferencias"
git branch -M main
git remote add origin https://github.com/usuario/renomeadorcomprovantes.git
git push -u origin main

# 3. Instruções para o Servidor Ubuntu (TI)
Backend: Criar serviço Systemd para o Gunicorn rodando na porta 8000.
Frontend: Gerar build (npm run build) e servir os arquivos estáticos via Nginx.
Permissões: O usuário do Nginx (www-data) deve ter permissão de escrita na pasta /data.
Database: Na primeira execução, o SQLAlchemy criará automaticamente o esquema do banco.
Observação: O mapeamento das unidades está centralizado no frontend (UNIDADES_MAP), permitindo alteração rápida de nomes de filiais sem necessidade de mexer no banco de dados.