# Tipos de Comprovantes Sicredi Suportados

## 📋 Visão Geral

O processador Sicredi suporta múltiplos tipos de comprovantes de pagamento. Cada tipo possui lógica de extração especializada para capturar os dados corretos.

---

## ✅ Tipos Implementados

### 1. **BOLETO** (Principal)

Comprovante de pagamento de boleto bancário.

**Identificação**: Contém seção "Boleto" no texto  
**Campos principais**:
- **Descrição**: Extraída de "Descrição do Pagamento" (pode incluir NF e código)
- **Beneficiário**: Nome da entidade receptora do pagamento
- **Valor**: Campo "Valor Pago (R$)" ou similar
- **Data**: "Data do Pagamento"

**Exemplo de Descrição Extraída**:
```
NF_D_12345_AP_98765
TEXTO_REFERENCIA_PAGAMENTO
```

**Filename Gerado**:
```
BENEFICIARIO_NF_D_12345_AP_98765_1200.50_15062026.pdf
```

---

### 2. **TRIBUTO** (Novo ✨)

Comprovante de pagamento de tributos (impostos) a órgãos governamentais.

**Identificação**: Contém seção "Tributos" no texto  
**Tipo de Pagamento**: "Órgãos Governamentais"  
**Campos principais**:
- **Descrição**: Extraída de "Descrição do Pagamento" (tipo de imposto: ICMS, ISS, DARF, etc)
- **Órgão**: Nome da empresa recebedora (ex: "SEFAZ BAHIA ICMS")
- **Valor**: Campo "Valor Total (R$)"
- **Data**: "Data do Pagamento"

**Exemplo de Descrição Extraída**:
```
ICMS_DD_AP_542519
ICMS_REFERENCIA_NOTA_FISCAL
```

**Filename Gerado**:
```
COMUNIDADE_CANCAO_ICMS_DD_AP_542519_757.76_09062026.pdf
```

**Tipos de Tributo Reconhecidos**:
- ICMS (Imposto sobre Circulação de Mercadorias e Serviços)
- ISS (Imposto sobre Serviços)
- DARF (Documento de Arrecadação de Receitas Federais)
- NF (Nota Fiscal)
- AP (Número de Referência/Apuração)

---

### 3. **PIX** (Planejado)

Comprovante de transferência PIX.

**Status**: Detecção funcional, extração ainda não implementada  
**Identificação**: Contém palavra "pix" no texto  

---

## 🔧 Lógica de Detecção

```python
# Ordem de prioridade:
1. Se texto contém "tributo" → TRIBUTO
2. Senão, se contém "pix" → PIX  
3. Senão → BOLETO (padrão)
```

---

## 📊 Estrutura de Dados Retornada

Todos os tipos retornam a seguinte estrutura:

```python
{
    "banco": "SICREDI",
    "tipo": "BOLETO" | "TRIBUTO" | "PIX",
    "descricao": "string normalizado",  # sem acentos, com underscores
    "beneficiario": "string normalizado",  # entidade recebedora
    "valor": 1234.56,  # em reais
    "data": "DD_mmm"  # ex: "09_jun"
}
```

---

## 🔐 Normalização de Campos

**Descrição e Beneficiário**:
- Remove acentos (NFD normalization)
- Converte para UPPERCASE
- Substitui espaços por underscores
- Remove caracteres especiais

**Exemplos**:
```
"Autenticação Eletrônica" → "AUTENTICACAO_ELETRONICA"
"COMUNIDADE CANCÃO NOVA" → "COMUNIDADE_CANCAO_NOVA"
"ICMS DD ap 542519" → "ICMS_DD_AP_542519"
```

**Data**:
- Formato de entrada: DD/MM/YYYY
- Formato de saída: "DD_mmm" (ex: "09_jun", "15_dez")

---

## 🧪 Exemplos de Teste

### BOLETO
```python
texto = """
Associado: EMPRESA TESTE LTDA
Descrição do Pagamento: NF D 12345 AP 98765
Valor Pago (R$): 1.200,50
Data do Pagamento: 15/06/2026
"""
# Extrai: EMPRESA_TESTE_LTDA_NF_D_12345_AP_98765_1200.50_15062026.pdf
```

### TRIBUTO
```python
texto = """
Tributos
Associado: COMUNIDADE CANCAO NOVA
Nome da Empresa: SEFAZ BAHIA ICMS
Descrição do Pagamento: ICMS DD ap 542519
Valor Total (R$): 757,76
Data do Pagamento: 09/06/2026
"""
# Extrai: COMUNIDADE_CANCAO_NOVA_ICMS_DD_AP_542519_757.76_09062026.pdf
```

---

## 📈 Próximas Etapas

1. ✅ BOLETO - Implementado e testado
2. ✅ TRIBUTO - Implementado e testado
3. ⏳ PIX - Detecção funcional, aguardando exemplos reais
4. ⏳ Consumo - Comprovantes de consumo de água/energia
5. ⏳ Outros bancos - Expandir suporte além de Sicredi

---

## 🔗 Relacionados

- [Arquitetura do Processador](../ARQUITETURA_MELHORADA.md)
- [Processador Sicredi](../backend/processors/sicredi.py)
- [Testes do Processador](../backend/tests/test_processors.py)
