# 📋 Sicredi Boleto - Especificação Técnica

**Versão:** 1.0  
**Data:** 26 de junho de 2026  
**Status:** MVP em funcionamento  

---

## 🎯 O Que é Suportado

### Tipo de Comprovante
- ✅ **Boleto** (extrato de pagamento de boleto)
- 🚀 PIX (futuro)

### Dados Extraídos

| Campo | Exemplo | Fonte no PDF | Obrigatório |
|-------|---------|--------------|-------------|
| **Beneficiário** | EMPRESA XYZ LTDA | "Razão Social do Beneficiário" | ✅ Sim |
| **Valor** | 1.234,56 | "Valor Pago (R$)" | ✅ Sim |
| **Data** | 09_jun | "Data do Pagamento" → 09/06/2026 | ✅ Sim |

### Formato do Nome do Arquivo Gerado

```
{BENEFICIARIO}_{VALOR}_{DATA}.pdf

Exemplos:
├─ EMPRESA_XYZ_1.234,56_09_jun.pdf
├─ BANCO_DO_BRASIL_500,00_15_mai.pdf
└─ PREFEITURA_MUNICIPAL_2.100,00_01_jun.pdf
```

### Estrutura no PDF Sicredi Boleto

```
┌─────────────────────────────────────────────┐
│        COMPROVANTE DE PAGAMENTO             │
│              SICREDI BOLETO                 │
├─────────────────────────────────────────────┤
│                                             │
│ Razão Social do Beneficiário:               │
│ EMPRESA EXEMPLO LTDA                        │
│                                             │
│ Valor Pago (R$):                            │
│ 1.234,56                                    │
│                                             │
│ Data do Pagamento:                          │
│ 09/06/2026                                  │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 🔧 Implementação Atual

### Localização do Código
```
backend/services/pdf_processing.py
└─ function: process_pdf_file()
   └─ Extrai: beneficiário, valor, data
```

### Fluxo de Processamento

```
1. Usuário faz upload PDF
   ↓
2. API /api/upload recebe arquivo
   ↓
3. process_pdf_file() extrai dados
   ├─ Página por página
   ├─ PDFPlumber busca texto
   ├─ Regex extrai beneficiário/valor/data
   └─ Normaliza acentos e formata nome
   ↓
4. PDF é renomeado: BENEFICIARIO_VALOR_DATA.pdf
   ↓
5. Salvo em backend/data/processados/
   ↓
6. Registro criado no banco de dados
   ↓
7. Resposta enviada ao frontend
```

### Regex Utilizados

```python
# Beneficiário
re.search(r"Razão Social do Beneficiário:\s*(.*)", texto, re.I)

# Valor
re.search(r"Valor Pago \(R\$\):\s*([\d.,]+)", texto)

# Data
re.search(r"Data do Pagamento:\s*(\d{2}/\d{2}/\d{4})", texto)
```

---

## ⚠️ Limitações Conhecidas

1. **Acentuação**
   - ❌ Converte "São Paulo" → "SAO_PAULO"
   - ⚠️ Pode gerar confusão com empresas que têm nomes similares

2. **Caracteres Especiais**
   - ❌ Remove: "Empresa & Filhos" → "EMPRESA_FILHOS"
   - ⚠️ Perde informação importante

3. **Beneficiários Longos**
   - ❌ Limita a 25 caracteres para nome de arquivo curto
   - ✅ Nome completo fica no banco de dados

4. **Múltiplas Páginas**
   - ✅ Suporta: Cria 1 PDF por página do arquivo original
   - ⚠️ Pode gerar muitos arquivos de um único upload

---

## 🧪 Exemplos de Teste

### PDF de Teste: Boleto Sicredi Válido

```
Texto extraído:
─────────────────────────────────────────
Razão Social do Beneficiário: CONCESSIONARIA RODOVIA SP
Valor Pago (R$): 537,89
Data do Pagamento: 15/03/2026
─────────────────────────────────────────

Resultado esperado:
{
  'banco': 'SICREDI',
  'tipo': 'BOLETO',
  'descricao': 'CONCESSIONARIA_RODOVIA_SP',
  'valor': 537.89,
  'data': '15_mar',
  'nome_arquivo': 'CONCESSIONARIA_RODOVIA_SP_537,89_15_mar.pdf'
}
```

### Casos de Erro

| Caso | Cenário | Resultado |
|------|---------|-----------|
| **Sem beneficiário** | Campo não encontrado | `descricao = "DESCONHECIDO"` |
| **Valor inválido** | "R$ --" | `valor = 0.00` |
| **Data fora formato** | "15 de março" | `data = "00_jan"` |

---

## 🔄 Como Testar Localmente

### 1. Preparar PDF de Teste

```bash
# Usar um PDF real de boleto Sicredi
# Ou criar um PDF com texto:
cat > /tmp/teste_sicredi.txt << 'EOF'
Razão Social do Beneficiário: EMPRESA TESTE LTDA
Valor Pago (R$): 1.000,00
Data do Pagamento: 09/06/2026
EOF

# Converter para PDF (se tiver ghostscript)
enscript -p /tmp/teste.pdf /tmp/teste_sicredi.txt
```

### 2. Enviar via API

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/tmp/teste_sicredi.pdf"
```

### 3. Verificar Resultado

```bash
# Verificar arquivo processado
ls -la backend/data/processados/

# Checar banco de dados
sqlite3 data/app.db "SELECT * FROM comprovantes LIMIT 5;"
```

---

## 🚀 Roadmap Sicredi (Futuro)

### Próximo: Sicredi PIX

```
Status: 🚀 Planejado

Campos a extrair:
├─ Recebedor (PIX)
├─ Valor
├─ Data da transação
└─ Identificador PIX (CPF/Email/Telefone)

Exemplo de nome:
└─ RECEBEDOR_PIX_100,00_09_jun.pdf
```

---

## 📝 Checklist para Implementação

### Backend

- [x] Regex para Sicredi Boleto implementado
- [x] Normalização de caracteres OK
- [x] Conversão de datas OK
- [ ] Validação robusta (tratamento de edge cases)
- [ ] Testes unitários completos
- [ ] Logging de erros detalhado

### API

- [x] Endpoint POST /api/upload funcional
- [x] Suporte a múltiplas páginas
- [ ] Parâmetro `banco` na requisição
- [ ] Resposta estruturada com erros específicos
- [ ] Rate limiting

### Frontend

- [x] Componente Upload.tsx básico
- [x] Conexão com backend OK
- [ ] Feedback de progresso (% upload)
- [ ] Visualização de erros por arquivo
- [ ] Download dos PDFs processados

### Qualidade

- [ ] Testes unitários backend (80%+ cobertura)
- [ ] Testes E2E frontend
- [ ] Tratamento de edge cases
- [ ] Documentação de código

---

## 🤝 Links Úteis

- [Backend API Docs](http://localhost:8000/docs) - Swagger interativo
- [PDF Processing Code](../backend/services/pdf_processing.py)
- [Model Database](../backend/models/comprovante.py)
