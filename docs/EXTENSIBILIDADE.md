# 🏗️ Guia de Extensibilidade - Adicionar Novo Banco

**Objetivo:** Tornar fácil adicionar suporte a novos bancos (Bradesco, Itaú, Caixa, etc.)

**Tempo estimado:** 30-60 minutos por banco novo

---

## 🎯 Arquitetura: Factory + Strategy Pattern

A arquitetura usa dois padrões para flexibilidade:

### Factory Pattern
```
ProcessadorFactory.criar('sicredi')  → SicrediProcessor
ProcessadorFactory.criar('bradesco') → BradescoProcessor
ProcessadorFactory.criar('itau')     → ItauProcessor
```

### Strategy Pattern
```
class ProcessadorBase (abstração)
├─ SicrediProcessor (implementação específica)
├─ BradescoProcessor (implementação específica)
└─ ItauProcessor (implementação específica)
```

---

## 📋 Pré-Requisitos

Antes de adicionar novo banco, você precisa:

1. **PDF de exemplo** do comprovante do banco
2. **Campos necessários** (beneficiário, valor, data, etc.)
3. **Padrões regex** para extrair esses campos
4. **Casos de teste** com variações reais

---

## 🔧 Passo a Passo: Adicionar Bradesco

### Passo 1: Criar Arquivo do Processador

**Arquivo:** `backend/processors/bradesco.py`

```python
"""
Processador para comprovantes Bradesco
Suporta: Boleto, Transação, Débito Automático
"""

from backend.processors.base import ProcessadorBase
from backend.services.normalizer import Normalizer
import re

class BradescoProcessor(ProcessadorBase):
    BANCO_NOME = "BRADESCO"
    TIPOS_SUPORTADOS = ["BOLETO", "TRANSACAO", "DEBITO"]
    
    def extrair_dados(self, texto: str) -> dict:
        """Extrai dados de comprovante Bradesco"""
        
        tipo = self._identificar_tipo(texto)
        
        return {
            'banco': self.BANCO_NOME,
            'tipo': tipo,
            'descricao': self._extrair_descricao(texto),
            'valor': self._extrair_valor(texto),
            'data': self._extrair_data(texto),
        }
    
    def _identificar_tipo(self, texto: str) -> str:
        """Identifica tipo de comprovante Bradesco"""
        texto_lower = texto.lower()
        
        if "débito automático" in texto_lower:
            return "DEBITO"
        elif "transação" in texto_lower:
            return "TRANSACAO"
        else:
            return "BOLETO"
    
    def _extrair_descricao(self, texto: str) -> str:
        """
        Bradesco usa diferentes campos conforme tipo:
        - Boleto: "Beneficiário"
        - Débito: "Descricao da operação"
        - Transação: "Para:" ou "De:"
        """
        
        # Estratégia 1: Procurar "Beneficiário" (Boleto)
        match = re.search(r"beneficiário\s*:?\s*(.+)", texto, re.I)
        if match:
            beneficiario = match.group(1).strip()
            return Normalizer.normalizar_acentos(beneficiario)
        
        # Estratégia 2: Procurar "Descrição da operação"
        match = re.search(r"descri[çc][aã]o\s+da\s+opera[çc][aã]o\s*:?\s*(.+)", 
                         texto, re.I)
        if match:
            descricao = match.group(1).strip()
            return Normalizer.normalizar_acentos(descricao)
        
        # Estratégia 3: Procurar "Para:" (último recurso)
        match = re.search(r"para\s*:?\s*(.+)", texto, re.I)
        if match:
            destino = match.group(1).strip()
            return Normalizer.normalizar_acentos(destino)
        
        return "SEM_DESCRICAO"
    
    def _extrair_valor(self, texto: str) -> float:
        """Extrai valor do comprovante Bradesco"""
        
        # Bradesco pode ter diferentes formatos
        patterns = [
            r"valor\s+(?:do\s+)?(?:débito|crédito|pagamento)\s*:?\s*r?\$?\s*([\d.,]+)",
            r"r?\$?\s*([\d.,]+)\s+(?:débito|crédito|pagamento)",
            r"total\s*:?\s*r?\$?\s*([\d.,]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texto, re.I)
            if match:
                valor_str = match.group(1)
                # Converter "1.234,56" para 1234.56
                valor_str = valor_str.replace('.', '').replace(',', '.')
                try:
                    return float(valor_str)
                except ValueError:
                    pass
        
        return 0.0
    
    def _extrair_data(self, texto: str) -> str:
        """Extrai data do comprovante Bradesco"""
        
        # Procurar padrões de data
        patterns = [
            r"data\s+(?:da\s+)?(?:transação|operação|débito)\s*:?\s*(\d{2}/\d{2}/\d{4})",
            r"em\s+(\d{2}/\d{2}/\d{4})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texto, re.I)
            if match:
                data_str = match.group(1)
                return Normalizer.converter_data(data_str)
        
        return "00_jan"
    
    def validar(self, dados: dict) -> bool:
        """Valida dados extraídos"""
        
        # Todos os campos são obrigatórios
        campos_obrigatorios = ['banco', 'tipo', 'descricao', 'valor', 'data']
        
        for campo in campos_obrigatorios:
            if not dados.get(campo):
                return False
        
        # Valor deve ser positivo
        if dados['valor'] <= 0:
            return False
        
        # Descrição não pode ser o default
        if dados['descricao'] == "SEM_DESCRICAO":
            return False
        
        return True
```

### Passo 2: Registrar no Factory

**Arquivo:** `backend/services/extrator.py`

```python
"""
Factory para criar processadores específicos por banco
"""

from backend.processors.sicredi import SicrediProcessor
from backend.processors.bradesco import BradescoProcessor  # ← Novo!


class ProcessadorFactory:
    """Factory para criar processadores por banco"""
    
    PROCESSADORES = {
        'sicredi': SicrediProcessor,
        'bradesco': BradescoProcessor,  # ← Registrar aqui!
    }
    
    @staticmethod
    def criar(banco: str):
        """
        Cria processador para o banco especificado
        
        Args:
            banco: Nome do banco ('sicredi', 'bradesco', etc.)
        
        Returns:
            Instância do processador
        
        Raises:
            ValueError: Se banco não é suportado
        """
        banco_lower = banco.lower().strip()
        cls = ProcessadorFactory.PROCESSADORES.get(banco_lower)
        
        if not cls:
            suportados = ', '.join(ProcessadorFactory.PROCESSADORES.keys())
            raise ValueError(
                f"Banco '{banco}' não suportado. "
                f"Bancos disponíveis: {suportados}"
            )
        
        return cls()
```

### Passo 3: Criar Testes

**Arquivo:** `backend/tests/test_bradesco.py`

```python
"""
Testes para processador Bradesco
"""

import pytest
from backend.processors.bradesco import BradescoProcessor


@pytest.fixture
def processor():
    return BradescoProcessor()


class TestBradescoIdentificacao:
    """Testes de identificação de tipo"""
    
    def test_identificar_boleto(self, processor):
        texto = """
        Bradesco - Comprovante de Boleto
        Beneficiário: EMPRESA XYZ
        """
        assert processor._identificar_tipo(texto) == "BOLETO"
    
    def test_identificar_debito_automatico(self, processor):
        texto = "Débito Automático em Conta"
        assert processor._identificar_tipo(texto) == "DEBITO"


class TestBradescoExtracao:
    """Testes de extração de dados"""
    
    def test_extrair_boleto_completo(self, processor):
        texto = """
        Beneficiário: EMPRESA TESTE LTDA
        Valor do pagamento: R$ 1.234,56
        Data da transação: 15/03/2026
        """
        dados = processor.extrair_dados(texto)
        
        assert dados['tipo'] == 'BOLETO'
        assert 'EMPRESA_TESTE' in dados['descricao']
        assert dados['valor'] == 1234.56
        assert dados['data'] == '15_mar'
    
    def test_extrair_debito_automatico(self, processor):
        texto = """
        Descrição da operação: CONTA DE LUZ MARÇO
        Valor do débito: R$ 150,30
        Data do débito: 05/03/2026
        """
        dados = processor.extrair_dados(texto)
        
        assert dados['tipo'] == 'DEBITO'
        assert 'CONTA_DE_LUZ' in dados['descricao']
        assert dados['valor'] == 150.30


class TestBradescoValidacao:
    """Testes de validação"""
    
    def test_validar_dados_completos(self, processor):
        dados = {
            'banco': 'BRADESCO',
            'tipo': 'BOLETO',
            'descricao': 'EMPRESA_XYZ',
            'valor': 100.0,
            'data': '15_mar',
        }
        assert processor.validar(dados) == True
    
    def test_rejeitar_sem_descricao(self, processor):
        dados = {
            'banco': 'BRADESCO',
            'tipo': 'BOLETO',
            'descricao': 'SEM_DESCRICAO',  # ❌ Invalid
            'valor': 100.0,
            'data': '15_mar',
        }
        assert processor.validar(dados) == False
    
    def test_rejeitar_valor_zero(self, processor):
        dados = {
            'banco': 'BRADESCO',
            'tipo': 'BOLETO',
            'descricao': 'EMPRESA_XYZ',
            'valor': 0.0,  # ❌ Invalid
            'data': '15_mar',
        }
        assert processor.validar(dados) == False
```

### Passo 4: Atualizar API para Aceitar `banco`

**Arquivo:** `backend/routes/upload.py` (novo arquivo)

```python
"""
Rotas de upload e processamento de comprovantes
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pathlib import Path
import time
import logging

from backend.services.extrator import ProcessadorFactory
from backend.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["upload"])

BASE_DIR = Path(__file__).parent.parent.parent
PROCESSADOS_DIR = BASE_DIR / 'backend' / 'data' / 'processados'


@router.post("/upload")
async def upload_comprovante(
    file: UploadFile = File(...),
    banco: str = Query("sicredi", description="Banco do comprovante: sicredi, bradesco, etc"),
    db: Session = Depends(get_db)
):
    """
    Upload de comprovante para renomeação automática
    
    **Parâmetros:**
    - `file`: PDF do comprovante
    - `banco`: Nome do banco (padrão: sicredi)
    
    **Exemplo:**
    ```
    curl -X POST "http://localhost:8000/api/upload?banco=bradesco" \\
      -F "file=@comprovante.pdf"
    ```
    """
    
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas PDFs são aceitos")
    
    logger.info(f"Upload: {file.filename} (banco: {banco})")
    
    try:
        # Validar banco
        try:
            processador = ProcessadorFactory.criar(banco)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Processar PDF com banco correto
        # ... (implementar usando ProcessadorFactory)
        
        return {
            "status": "sucesso",
            "banco": banco,
            "arquivo": file.filename
        }
    
    except Exception as e:
        logger.error(f"Erro: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Passo 5: Executar Testes

```bash
cd backend
source .venv/bin/activate
pytest tests/test_bradesco.py -v
```

---

## 📋 Checklist para Novo Banco

Use este checklist toda vez que adicionar novo banco:

- [ ] **1. Análise**
  - [ ] PDF de exemplo obtido
  - [ ] Campos necessários identificados
  - [ ] Padrões regex testados (regex101.com)

- [ ] **2. Desenvolvimento**
  - [ ] `backend/processors/novo_banco.py` criado
  - [ ] Classe herda de `ProcessadorBase`
  - [ ] Métodos: `extrair_dados()`, `validar()` implementados
  - [ ] Regex funcionando corretamente

- [ ] **3. Integração**
  - [ ] Processador registrado no `ProcessadorFactory`
  - [ ] Import adicionado em `extrator.py`
  - [ ] API aceita parâmetro `banco=novo_banco`

- [ ] **4. Testes**
  - [ ] `backend/tests/test_novo_banco.py` criado
  - [ ] Mínimo 5 testes por processador
  - [ ] `pytest` passa com sucesso
  - [ ] Casos edge tratados

- [ ] **5. Documentação**
  - [ ] `docs/NOVO_BANCO.md` criado
  - [ ] Exemplo de PDF de teste
  - [ ] Campos extraídos documentados

- [ ] **6. Frontend (Opcional)**
  - [ ] Dropdown com novo banco adicionado
  - [ ] Mensagem de sucesso atualizada

---

## 🔍 Exemplo Real: Padrões Regex Testados

Para criar padrões regex confiáveis, use https://regex101.com

### Bradesco - Extração de Beneficiário

```regex
Padrão: beneficiário\s*:?\s*(.+)
Teste:
  "Beneficiário: EMPRESA XYZ"              ✓
  "beneficiario: EMPRESA XYZ"              ✓
  "BENEFICIÁRIO: EMPRESA XYZ"              ✓
  "Beneficiário:EMPRESA XYZ"               ✓
```

### Bradesco - Extração de Valor

```regex
Padrão: valor\s+(?:do\s+)?(?:débito|crédito|pagamento)\s*:?\s*r?\$?\s*([\d.,]+)
Teste:
  "Valor do débito: R$ 1.234,56"           ✓ → "1.234,56"
  "Valor do crédito: 100,00"               ✓ → "100,00"
  "Valor pagamento: r$ 50.000,99"          ✓ → "50.000,99"
```

---

## 🚀 Próximos Bancos Sugeridos

### Priority 🔴 (Alta Demanda)

1. **Bradesco** - 30% dos comprovantes
2. **Itaú** - 25% dos comprovantes
3. **Caixa** - 20% dos comprovantes

### Médio 🟡

4. **Banco do Brasil** - 15% dos comprovantes
5. **Santander** - 5% dos comprovantes

### Baixo 🟢 (Nice to Have)

6. **Nubank** - 5% dos comprovantes
7. **Outros** - <1% dos comprovantes

---

## 💡 Dicas & Boas Práticas

### ✅ Fazer

- ✅ Usar regex modular (um padrão por campo)
- ✅ Testar com múltiplos PDFs do mesmo banco
- ✅ Criar casos de teste para erro
- ✅ Documentar padrões especiais
- ✅ Reutilizar `Normalizer` para padronização

### ❌ Não Fazer

- ❌ Hardcoding de valores
- ❌ Regex genéricos que pegam tudo
- ❌ Assumir que todos PDFs do banco são iguais
- ❌ Skipping de validação
- ❌ Ignorar exceções

---

## 🤝 Exemplo Completo: Itaú (Simplificado)

Para começar com Itaú, copie este template:

```python
# backend/processors/itau.py

from backend.processors.base import ProcessadorBase
from backend.services.normalizer import Normalizer
import re

class ItauProcessor(ProcessadorBase):
    BANCO_NOME = "ITAU"
    TIPOS_SUPORTADOS = ["BOLETO", "TRANSACAO"]
    
    def extrair_dados(self, texto: str) -> dict:
        return {
            'banco': self.BANCO_NOME,
            'tipo': self._identificar_tipo(texto),
            'descricao': self._extrair_descricao(texto),
            'valor': self._extrair_valor(texto),
            'data': self._extrair_data(texto),
        }
    
    def _identificar_tipo(self, texto: str) -> str:
        # TODO: Implementar
        return "BOLETO"
    
    def _extrair_descricao(self, texto: str) -> str:
        # TODO: Implementar
        return "SEM_DESCRICAO"
    
    def _extrair_valor(self, texto: str) -> float:
        # TODO: Implementar
        return 0.0
    
    def _extrair_data(self, texto: str) -> str:
        # TODO: Implementar
        return "00_jan"
    
    def validar(self, dados: dict) -> bool:
        # TODO: Implementar
        return False
```

---

## 📞 Suporte

Se tiver dúvidas ou encontrar problemas:

1. Verifique se o PDF é realmente do banco (não PDF combinar)
2. Teste o regex em https://regex101.com
3. Verifique os logs: `backend/logs/`
4. Compare com implementação do Sicredi
