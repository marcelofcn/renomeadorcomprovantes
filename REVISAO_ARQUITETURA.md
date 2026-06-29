# 📋 Revisão de Código - Renomeador Sicredi Boleto

**Data:** 26 de junho de 2026  
**Status:** Análise Completa com Recomendações  
**Foco:** Limpar o que não é necessário agora e organizar para suportar múltiplos bancos  

---

## 🎯 Objetivo Atual

✅ **MVP Funcional:** Renomear boletos Sicredi  
🚀 **Próxima Evolução:** Suportar múltiplos bancos (Bradesco, Itaú, etc.) e tipos (PIX, DARF)

---

## 📊 Diagnóstico da Arquitetura

### ✅ O QUE ESTÁ BOM

| Item | Status | Localização |
|------|--------|-------------|
| **Lógica de extração Sicredi** | ✅ Funcional | `backend/services/pdf_processing.py` |
| **API FastAPI** | ✅ Base boa | `backend/main.py` |
| **Database + Models** | ✅ OK | `backend/models/comprovante.py` |
| **Requirements.txt** | ✅ Atualizado | `backend/requirements.txt` |
| **Frontend scaffold** | ✅ Estrutura base | `frontend/` |

---

## ⚠️ O QUE PRECISA SER REMOVIDO

### 1. **Documentação Redundante/Genérica** (Remover TODOS)
```
❌ SUMARIO_EXECUTIVO.md      → Muito genérico, fala de roadmap futuro
❌ SUMARIO_VISUAL.md          → Só tem ASCII art, sem valor
❌ MAPA_DOCUMENTACAO.md       → Índice não é necessário agora
❌ CONTRIBUTING.md            → Prematuro, sem contribuidores
❌ BACKEND_PRONTO.md          → Obsoleto/incompleto
❌ REVISAO_CODIGO.md          → Genérico demais
❌ STATUS_FINAL.md            → Documento "achado" de briefing anterior
❌ COMANDOS_PRINCIPAIS.md     → Sem utilidade
❌ COMO_RODAR.md              → Duplica QUICKSTART.md
❌ GUIA_RAPIDO.md             → Genérico, sem foco no Sicredi
```

**Total a remover:** 10 documentos (~40 KB)

---

### 2. **Arquivos de Teste/Exemplo** (Remover)
```
❌ exemplo_refatoracao.py     → Template nunca usado
❌ test_refatoracao.py        → Testes de exemplo abandonados
❌ comprovantes.pdf           → Arquivo de teste solto
```

**Por quê remover?**
- Geram confusão no projeto
- Aumentam o "ruído" visual
- Ninguém sabe se são úteis ou não

---

### 3. **Scripts Shell Desnecessários** (Revisar)
```
❌ run_backend.sh             → Pode ser um Makefile único
❌ run_frontend.sh            → Pode ser um Makefile único
❌ setup.sh                   → OK manter se estiver funcional
```

**Recomendação:** Unificar em um `Makefile` moderno

---

### 4. **Documentação Futurista** (Arquivar)
```
docs/ARQUITETURA_MELHORADA.md          → Fala de PostgreSQL, Docker, deploy
docs/PLANO_IMPLEMENTACAO.md            → Fala de 4 fases complexas
docs/DEPLOYMENT_UBUNTU.md              → Produção não é requisito agora
```

**Recomendação:** Mover para `docs/archived/` e criar `docs/ARQUITETURA_SICREDI.md` focado

---

## 🔴 PROBLEMAS DE CÓDIGO

### 1. **Duplicação de Lógica**
```python
# 1️⃣ renomeador_comprovantes.py (460+ linhas)
def extrair_dados_bradesco():
def identificar_tipo_comprovante():
def normalizar_acentos():

# 2️⃣ backend/services/pdf_processing.py (80+ linhas)
def normalizar_acentos():           # ❌ DUPLICADO
def converter_data():               # ❌ DUPLICADO
def process_pdf_file():             # ✅ Implementado

# 3️⃣ exemplo_refatoracao.py (50+ linhas)
def extrair_data():                 # ❌ DUPLICADO (outra versão)
```

**Impacto:** Mudanças em uma função não se refletem em outras

---

### 2. **Modelo de Dados Desorganizado**
```python
# backend/models/comprovante.py

Comprovante(
    original_filename,
    saved_filename,
    description,          # ❌ Vago: é o beneficiário?
    bank,                 # ✅ OK
    comprovante_type,     # ✅ OK
    amount,               # ✅ OK
    date,                 # ✅ OK
    page_number,          # ✅ OK
    source_path,          # ⚠️ Redundante com original_filename?
)
```

**Problema:** Não está claro qual banco/tipo é suportado

---

### 3. **API Sem Suporte a Múltiplos Bancos**
```python
# backend/main.py
@app.post("/api/upload")
async def upload_comprovante(file: UploadFile):
    resultados = process_pdf_file(...)  # ❌ Sem parâmetro "banco"
    # Sempre assume Sicredi
```

**Falta:** Campo `banco` na requisição

---

## 🏗️ ARQUITETURA RECOMENDADA

### Estrutura de Diretórios (NOVO)

```
renomeadorcomprovantes/
│
├── README.md                      # Uma página, objetivo claro
├── CHECKLIST.md                   # Manter: próximos passos
├── Makefile                       # Novo: unificar scripts
├── requirements.txt               # Frontend + Backend
│
├── backend/
│   ├── main.py                    # FastAPI app
│   ├── config.py                  # Configs
│   ├── database.py                # SQLAlchemy
│   │
│   ├── models/
│   │   └── comprovante.py         # Model único bem definido
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── extrator.py            # ✨ NOVO: unifica toda extração
│   │   └── normalizer.py          # ✨ NOVO: normalização centralizada
│   │
│   ├── processors/                # ✨ NOVO: um arquivo por banco
│   │   ├── __init__.py
│   │   ├── base.py                # Classe base abstracta
│   │   ├── sicredi.py             # ✅ Suporta: Boleto
│   │   ├── bradesco.py            # 🚀 Próximo
│   │   └── itau.py                # 🚀 Futuro
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── upload.py              # Endpoint /api/upload
│   │
│   ├── tests/
│   │   ├── test_sicredi.py
│   │   └── test_normalizer.py
│   │
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Upload.tsx         # Upload simples
│   │   │   └── Dashboard.tsx      # Histórico
│   │   ├── components/
│   │   ├── services/
│   │   └── App.tsx
│   └── package.json
│
├── docs/
│   ├── README.md                  # índice de docs
│   ├── SICREDI_BOLETO.md          # ✨ NOVO: especificação Sicredi
│   ├── EXTENSIBILIDADE.md         # ✨ NOVO: como adicionar novo banco
│   └── archived/                  # Docs antigas (leitura opcional)
│       ├── ARQUITETURA_MELHORADA.md
│       ├── PLANO_IMPLEMENTACAO.md
│       └── DEPLOYMENT_UBUNTU.md
│
└── data/
    ├── uploads/
    ├── processados/
    └── histórico/
```

---

## ✨ REFATORAÇÃO RECOMENDADA

### 1. **Centralizar Extração (ALTA PRIORIDADE)**

**Criar:** `backend/services/extrator.py`

```python
"""
Extrator de dados de comprovantes - Suporte multi-banco
"""
from abc import ABC, abstractmethod
from backend.processors.sicredi import SicrediProcessor
from backend.processors.bradesco import BradescoProcessor

class ProcessadorFactory:
    """Factory para criar processadores específicos por banco"""
    
    PROCESSADORES = {
        'sicredi': SicrediProcessor,
        'bradesco': BradescoProcessor,
    }
    
    @staticmethod
    def criar(banco: str):
        cls = ProcessadorFactory.PROCESSADORES.get(banco)
        if not cls:
            raise ValueError(f"Banco '{banco}' não suportado")
        return cls()

# Uso:
processor = ProcessadorFactory.criar('sicredi')
dados = processor.extrair_dados(pdf_texto)
```

---

### 2. **Classe Base para Processadores**

**Criar:** `backend/processors/base.py`

```python
from abc import ABC, abstractmethod

class ProcessadorBase(ABC):
    """Classe base para processadores de bancos"""
    
    BANCO_NOME: str  # "SICREDI", "BRADESCO", etc
    TIPOS_SUPORTADOS: list  # ["BOLETO", "PIX"]
    
    @abstractmethod
    def extrair_dados(self, texto: str) -> dict:
        """
        Extrai dados do texto do PDF
        
        Returns:
            {
                'banco': 'SICREDI',
                'tipo': 'BOLETO',
                'descricao': '...',
                'valor': 123.45,
                'data': '09_jun',
            }
        """
        pass
    
    @abstractmethod
    def validar(self, dados: dict) -> bool:
        """Valida se os dados extraídos fazem sentido"""
        pass
```

---

### 3. **Implementação Sicredi (Refatorada)**

**Criar:** `backend/processors/sicredi.py`

```python
from backend.processors.base import ProcessadorBase
from backend.services.normalizer import Normalizer

class SicrediProcessor(ProcessadorBase):
    BANCO_NOME = "SICREDI"
    TIPOS_SUPORTADOS = ["BOLETO", "PIX"]
    
    def extrair_dados(self, texto: str) -> dict:
        """Extrai dados específicos de boleto Sicredi"""
        return {
            'banco': 'SICREDI',
            'tipo': self._identificar_tipo(texto),
            'descricao': self._extrair_descricao(texto),
            'valor': self._extrair_valor(texto),
            'data': self._extrair_data(texto),
        }
    
    def _identificar_tipo(self, texto: str) -> str:
        # Lógica específica Sicredi
        if "comprovante de pagamento pix" in texto.lower():
            return "PIX"
        return "BOLETO"
    
    def _extrair_descricao(self, texto: str) -> str:
        # Lógica específica Sicredi
        # ...
        return Normalizer.normalizar_acentos(descricao)
    
    def validar(self, dados: dict) -> bool:
        return all([dados.get('descricao'), dados.get('valor')])
```

---

### 4. **Normalizer Centralizado**

**Criar:** `backend/services/normalizer.py`

```python
import unicodedata
import re
from typing import Optional

class Normalizer:
    """Funções centralizadas de normalização"""
    
    MESES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 
             'jul', 'ago', 'set', 'out', 'nov', 'dez']
    
    @staticmethod
    def normalizar_acentos(texto: Optional[str], 
                           max_len: int = 50) -> str:
        """Remove acentos e caracteres especiais"""
        if not texto:
            return "SEM_DESCRICAO"
        
        nfd = unicodedata.normalize('NFD', texto)
        sem_acentos = ''.join(c for c in nfd 
                             if unicodedata.category(c) != 'Mn')
        limpo = re.sub(r'[^a-zA-Z0-9\s]', '', sem_acentos)
        
        resultado = limpo.strip().replace(" ", "_").upper()
        return resultado[:max_len]
    
    @staticmethod
    def converter_data(data_str: str) -> str:
        """Converte DD/MM/YYYY para DD_mes"""
        try:
            dia, mes, ano = data_str.split('/')
            return f"{dia}_{Normalizer.MESES[int(mes) - 1]}"
        except:
            return "00_jan"
    
    @staticmethod
    def formatar_valor(valor: float) -> str:
        """Formata valor para nome de arquivo (1.234,56)"""
        return f"{valor:,.2f}".replace(',', 'X') \
                              .replace('.', ',') \
                              .replace('X', '.')
```

---

## 🧪 ESTRUTURA DE TESTES

### **Novo:** `backend/tests/test_sicredi.py`

```python
import pytest
from backend.processors.sicredi import SicrediProcessor

@pytest.fixture
def processor():
    return SicrediProcessor()

def test_extrair_boleto(processor):
    texto = """
    Razão Social do Beneficiário: EMPRESA XYZ
    Valor Pago (R$): 1.234,56
    Data do Pagamento: 09/06/2026
    """
    dados = processor.extrair_dados(texto)
    
    assert dados['tipo'] == 'BOLETO'
    assert dados['descricao'] == 'EMPRESA_XYZ'
    assert dados['valor'] == 1234.56
    assert dados['data'] == '09_jun'

def test_validar_dados_completos(processor):
    dados = {
        'banco': 'SICREDI',
        'tipo': 'BOLETO',
        'descricao': 'TEST',
        'valor': 100.0,
        'data': '09_jun',
    }
    assert processor.validar(dados) == True
```

---

## 📋 PLANO DE AÇÃO (POR ORDEM)

### ✨ FASE 1: Limpeza (2 horas)

```bash
# 1. Remover documentação desnecessária
rm SUMARIO_EXECUTIVO.md SUMARIO_VISUAL.md MAPA_DOCUMENTACAO.md \
   CONTRIBUTING.md BACKEND_PRONTO.md REVISAO_CODIGO.md \
   STATUS_FINAL.md COMANDOS_PRINCIPAIS.md COMO_RODAR.md GUIA_RAPIDO.md

# 2. Remover arquivos de teste
rm exemplo_refatoracao.py test_refatoracao.py comprovantes.pdf

# 3. Arquivar docs futuras
mkdir -p docs/archived
mv docs/ARQUITETURA_MELHORADA.md docs/PLANO_IMPLEMENTACAO.md \
   docs/DEPLOYMENT_UBUNTU.md docs/archived/

# 4. Unificar scripts
# Ver seção "Makefile" abaixo
```

### 🏗️ FASE 2: Refatoração (4 horas)

1. **Criar estrutura de processadores**
   - [ ] `backend/processors/__init__.py`
   - [ ] `backend/processors/base.py`
   - [ ] `backend/processors/sicredi.py`

2. **Criar services centralizados**
   - [ ] `backend/services/normalizer.py`
   - [ ] `backend/services/extrator.py`

3. **Atualizar API**
   - [ ] `backend/routes/upload.py` com parâmetro `banco`
   - [ ] `backend/main.py` com nova rota

4. **Migrar testes**
   - [ ] `backend/tests/test_sicredi.py`
   - [ ] `backend/tests/test_normalizer.py`

### 📖 FASE 3: Documentação (1 hora)

1. **Criar docs focadas**
   - [ ] `docs/SICREDI_BOLETO.md` - Especificação atual
   - [ ] `docs/EXTENSIBILIDADE.md` - Como adicionar novo banco
   - [ ] `README.md` - Uma página clara

2. **Atualizar CHECKLIST.md**
   - [ ] Remover fases futuras
   - [ ] Focar no MVP Sicredi

---

## 📝 Novo README.md (Proposta)

```markdown
# 🧾 Renomeador de Comprovantes Sicredi

Ferramenta para renomear automaticamente comprovantes de pagamento Sicredi boleto.

**Status:** MVP - Sicredi Boleto  
**Próximo:** Bradesco (Q3 2026)

## 🚀 Quick Start

\`\`\`bash
# 1. Setup
bash setup.sh

# 2. Backend
cd backend && python main.py

# 3. Frontend
cd frontend && npm run dev
\`\`\`

## 📚 Documentação

- [SICREDI_BOLETO.md](./docs/SICREDI_BOLETO.md) - Como funciona
- [EXTENSIBILIDADE.md](./docs/EXTENSIBILIDADE.md) - Adicionar novo banco
- [CHECKLIST.md](./CHECKLIST.md) - Próximos passos

## 🏛️ Arquitetura

- **Backend:** FastAPI + SQLAlchemy
- **Frontend:** React + Vite
- **Processadores:** Factory pattern por banco
```

---

## 🎯 Resumo de Mudanças

| Item | Ação | Impacto |
|------|------|--------|
| 10 docs genéricos | ❌ Remover | -40 KB, melhor clareza |
| 3 scripts shell | ➡️ Consolidar em Makefile | Menos confusão |
| Lógica duplicada | 🔄 Centralizar | 1 fonte de verdade |
| Suporte a 1 banco | ↗️ Preparar para N bancos | Pronto para Bradesco |
| Tests abandonados | ❌ Remover | -100 linhas |
| API genérica | ✨ Adicionar parâmetro `banco` | Flexível |

---

## ✅ Resultado Final

```
✨ Projeto limpo
✨ Código DRY (Don't Repeat Yourself)
✨ Pronto para suportar múltiplos bancos
✨ Documentação clara e focada
✨ Testes bem organizados
✨ Fácil para novo desenvolvedor entender
```

---

## 📌 Próximas Etapas APÓS esta refatoração

1. Implementar `BradescoProcessor`
2. Adicionar suporte a PIX (além de Boleto)
3. UI melhorada para selecionar banco/tipo
4. Histórico persistente de conversões
5. Exportar relatório de processados
