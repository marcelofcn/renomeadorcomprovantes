# 🏗️ Arquitetura Visual - Processadores

## Padrão de Design: Factory + Strategy

```
           ProcessadorFactory
                   |
                   |-- criar('sicredi')  → SicrediProcessor
                   |-- criar('bradesco') → BradescoProcessor
                   |-- criar('itau')     → ItauProcessor
                   |
                   ↓

        ┌─────────────────────────────┐
        │  ProcessadorBase (ABC)       │
        │  (classe abstrata)           │
        ├─────────────────────────────┤
        │ + extrair_dados(texto)      │
        │ + validar(dados)            │
        └─────────────────────────────┘
                   △
                   |
        ┌──────────┼──────────┬──────────┐
        |          |          |          |
   SicrediProcessor|    BradescoProcessor|  ItauProcessor
                   |          |          |
```

---

## 📊 Fluxo de Processamento

```
User Upload
    |
    v
POST /api/upload?banco=sicredi
    |
    v
ProcessadorFactory.criar('sicredi')
    |
    v
SicrediProcessor() instance
    |
    v
extract_pdf()
    |
    +--- extrair_beneficiario()  → "EMPRESA XYZ"
    |
    +--- extrair_valor()         → 1234.56
    |
    +--- extrair_data()          → "09_jun"
    |
    v
dados = {
  'banco': 'SICREDI',
  'tipo': 'BOLETO',
  'descricao': 'EMPRESA_XYZ',
  'valor': 1234.56,
  'data': '09_jun'
}
    |
    v
validar(dados) → True/False
    |
    v
Salvar PDF renomeado
+ Registro no DB
    |
    v
Response 200 OK
```

---

## 🔀 Estrutura de Pastas (Novo)

```
backend/
│
├── main.py                          # FastAPI app
├── config.py                        # Settings
├── database.py                      # SQLAlchemy
│
├── models/
│   ├── __init__.py
│   └── comprovante.py              # DB model
│
├── services/                        # Serviços compartilhados
│   ├── __init__.py
│   ├── normalizer.py               # ✨ NOVO: Normalização centralizada
│   ├── extrator.py                 # ✨ NOVO: Factory + orquestração
│   └── pdf_processing.py           # Legacy (será refatorado)
│
├── processors/                      # ✨ NOVO: Lógica por banco
│   ├── __init__.py
│   ├── base.py                     # Classe abstrata
│   ├── sicredi.py                  # Implementação Sicredi
│   └── bradesco.py                 # Implementação Bradesco
│
├── routes/
│   ├── __init__.py
│   └── upload.py                   # ✨ NOVO: Rota /api/upload
│
├── tests/                           # ✨ NOVO: Testes por banco
│   ├── __init__.py
│   ├── test_sicredi.py
│   ├── test_bradesco.py
│   └── test_normalizer.py
│
├── .env                             # Configurações locais
├── requirements.txt                 # Dependências
└── README.md                        # Este arquivo
```

---

## 🔗 Dependências Entre Módulos

```
main.py
  |
  +--- config.py
  |
  +--- routes/upload.py
       |
       +--- services/extrator.py
            |
            +--- processors/base.py
            |    |
            |    +--- processors/sicredi.py
            |    |    |
            |    |    +--- services/normalizer.py
            |    |
            |    +--- processors/bradesco.py
            |         |
            |         +--- services/normalizer.py
            |
            +--- models/comprovante.py
                 |
                 +--- database.py
```

---

## 📝 Exemplo de Uso

### Antes (Hardcoded)
```python
# main.py - Sicredi apenas
@app.post("/api/upload")
async def upload(file):
    # Sempre assume Sicredi ❌
    beneficiario = extrair_beneficiario_sicredi(pdf_text)
    valor = extrair_valor_sicredi(pdf_text)
    # ...
```

### Depois (Flexível)
```python
# routes/upload.py - Multi-banco
@app.post("/api/upload")
async def upload(file, banco: str = "sicredi"):
    # Dinâmico ✅
    processor = ProcessadorFactory.criar(banco)
    dados = processor.extrair_dados(pdf_text)
    # ...
```

---

## 🧪 Exemplo de Teste

```python
# tests/test_sicredi.py

def test_sicredi_extrair_boleto():
    processor = SicrediProcessor()
    
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
    assert processor.validar(dados) == True
```

---

## 🚀 Adicionando Novo Banco (Bradesco)

### Passo 1: Criar Processador
```python
# backend/processors/bradesco.py

class BradescoProcessor(ProcessadorBase):
    BANCO_NOME = "BRADESCO"
    TIPOS_SUPORTADOS = ["BOLETO", "TRANSACAO", "DEBITO"]
    
    def extrair_dados(self, texto: str) -> dict:
        # Lógica específica Bradesco
        pass
    
    def validar(self, dados: dict) -> bool:
        # Validação específica Bradesco
        pass
```

### Passo 2: Registrar Factory
```python
# backend/services/extrator.py

PROCESSADORES = {
    'sicredi': SicrediProcessor,
    'bradesco': BradescoProcessor,  # ← Novo
}
```

### Passo 3: Usar API
```bash
# Upload com Bradesco
curl -X POST "http://localhost:8000/api/upload?banco=bradesco" \
  -F "file=@comprovante_bradesco.pdf"
```

### Resultado
```python
{
    'banco': 'BRADESCO',
    'tipo': 'BOLETO',
    'descricao': 'EMPRESA_TESTE',
    'valor': 500.00,
    'data': '15_mar'
}
```

---

## 📈 Escalabilidade

```
Adicionar novo banco = 1 arquivo novo + 1 linha no Factory

Sicredi    ← Arquivo: sicredi.py (150 linhas)
Bradesco   ← Arquivo: bradesco.py (150 linhas)
Itaú       ← Arquivo: itau.py (150 linhas)
Caixa      ← Arquivo: caixa.py (150 linhas)
BB         ← Arquivo: banco_brasil.py (150 linhas)
Santander  ← Arquivo: santander.py (150 linhas)
...

Sem modificar: main.py, routes, services, models
```

---

## ✅ Checklist de Implementação

### Fase 1: Refatoração (6 horas)
- [ ] Criar `processors/base.py`
- [ ] Criar `processors/sicredi.py`
- [ ] Criar `services/normalizer.py`
- [ ] Criar `services/extrator.py`
- [ ] Testes: test_sicredi.py, test_normalizer.py
- [ ] API: Parâmetro `banco` em upload
- [ ] Verificação: Backend inicia e testes passam

### Fase 2: Bradesco (3 horas)
- [ ] Obter PDF de exemplo
- [ ] Criar `processors/bradesco.py`
- [ ] Registrar em Factory
- [ ] Testes: test_bradesco.py
- [ ] Verificação: Testes passam

### Fase 3: Refinements (2 horas)
- [ ] Logging robusto
- [ ] Tratamento de erros
- [ ] Documentação de código
- [ ] Exemplos de uso

---

## 🎓 Aprendizados

Você aprenderá:
- ✅ **Factory Pattern** - Criar objetos dinamicamente
- ✅ **Strategy Pattern** - Diferentes estratégias por banco
- ✅ **Abstração** - Classes base para código reutilizável
- ✅ **DRY Principle** - Don't Repeat Yourself
- ✅ **TDD** - Test-Driven Development
- ✅ **Python ABC** - Abstract Base Classes

---

## 📚 Referência Rápida

| Conceito | Localização | Exemplo |
|----------|-------------|---------|
| Factory | `services/extrator.py` | `ProcessadorFactory.criar()` |
| Strategy | `processors/base.py` | `ProcessadorBase` |
| Sicredi | `processors/sicredi.py` | `SicrediProcessor` |
| Bradesco | `processors/bradesco.py` | `BradescoProcessor` |
| Normalização | `services/normalizer.py` | `Normalizer.normalizar_acentos()` |
| Testes | `tests/` | `test_sicredi.py` |
