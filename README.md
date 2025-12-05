# renomeadorcomprovantes
Ler arquivos de pagamentos e renomear 
# 📄 Renomeador Inteligente de Comprovantes Bancários

Ferramenta Python para renomear automaticamente comprovantes bancários em PDF, extraindo informações relevantes e organizando-os de forma inteligente.

## 🎯 Funcionalidades

- ✅ Renomeia comprovantes no formato: `DESCRICAO_VALOR_DATA.pdf`
- 🏦 Suporta múltiplos tipos de comprovantes:
  - **PIX** (Sicredi)
  - **Boletos** (Sicredi)
  - **Contas de Consumo** (Sicredi)
  - **Transferências Bradesco**
  - **DARF** (Sicredi)
- 📁 Organiza arquivos em pastas por data
- 🔍 Extração inteligente de dados usando OCR em PDFs

## 📋 Requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)

## 🚀 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/renomeador-comprovantes.git
cd renomeador-comprovantes
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 📦 Dependências

O projeto utiliza as seguintes bibliotecas:

- `pdfplumber` - Extração de texto de PDFs
- `PyPDF2` - Manipulação de arquivos PDF

## 💻 Uso

### Uso Básico

```bash
python renomeador_comprovantes.py
```

O script irá:
1. Processar todos os arquivos PDF na pasta atual
2. Identificar o tipo de comprovante
3. Extrair as informações relevantes
4. Renomear o arquivo seguindo o padrão estabelecido
5. Organizar em pastas por data (se configurado)

### Exemplos de Saída

**PIX:**
```
PENSAO_ALIMENTICIA_AP511704_613,54_09_jun.pdf
```

**Boleto:**
```
INSTALACAO_0150774922_REF_MAI2_237,20_09_jun.pdf
```

**Conta de Consumo:**
```
CONTA_LUZ_MAIO_150,30_15_mai.pdf
```

**Bradesco:**
```
TRANSFERENCIA_BANCARIA_1500,00_15_mar.pdf
```

**DARF:**
```
DARF_123456789_1234,56_15_mar.pdf
```

## 🏗️ Estrutura do Projeto

```
renomeador-comprovantes/
│
├── renomeador_comprovantes.py  # Script principal
├── requirements.txt            # Dependências do projeto
├── README.md                   # Documentação
├── LICENSE                     # Licença do projeto
└── .gitignore                 # Arquivos ignorados pelo Git
```

## 🔧 Como Funciona

### 1. Identificação do Tipo de Comprovante

O script analisa o texto do PDF e identifica o tipo baseado em palavras-chave:

- **DARF**: "comprovante de pagamento de darf"
- **Bradesco**: "bradesco", "data de débito", "data de crédito"
- **PIX**: "comprovante de pagamento pix"
- **Boleto**: "razão social do beneficiário"
- **Consumo**: "nome da empresa"

### 2. Extração de Dados

Para cada tipo de comprovante, o script extrai:

#### PIX
- Descrição: Linha após "Comprovante de Pagamento Pix"
- Valor: Campo "Valor R$"
- Data: Campo "Realizado em"

#### Boleto
- Descrição: Razão social do beneficiário
- Valor: Valor do documento
- Data: Data de vencimento ou pagamento

#### Bradesco
- Descrição: Campo "Descrição"
- Valor: Campo "Valor Total"
- Data: Campo "Data de débito" ou "Data de crédito"

#### DARF
- Descrição: "DARF_" + Número do Documento
- Valor: Campo "Valor Total (R$)"
- Data: Campo "Data do Pagamento"

### 3. Formatação do Nome

O nome final segue o padrão:
```
DESCRICAO_VALOR_DATA.pdf
```

Onde:
- `DESCRICAO`: Texto limpo, sem caracteres especiais, palavras separadas por underscore
- `VALOR`: Formato numérico com vírgula (ex: 1.234,56)
- `DATA`: Formato DD_MMM (ex: 15_mar)

## 🐛 Depuração

O script inclui modo de depuração detalhado que exibe:
- Linhas extraídas do PDF
- Processo de identificação de campos
- Valores encontrados em cada etapa
- Resultado final da extração

Para habilitar, o modo debug já está ativo nas funções `extrair_dados_*`.

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abrir um Pull Request

## 📝 TODO / Roadmap

- [ ] Adicionar suporte a mais bancos
- [ ] Implementar interface gráfica (GUI)
- [ ] Adicionar testes automatizados
- [ ] Suporte a processamento em lote de múltiplas pastas
- [ ] Opção de configuração via arquivo JSON
- [ ] Backup automático antes de renomear
- [ ] Geração de relatório de processamento

## ⚠️ Avisos Importantes

- Sempre faça backup dos seus arquivos antes de usar o script
- Teste com alguns arquivos primeiro antes de processar em lote
- Verifique se os PDFs não estão protegidos por senha
- O script funciona melhor com PDFs que contêm texto extraível (não apenas imagens)

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👤 Autor

Seu Nome - [@seu_usuario](https://github.com/seu-usuario)

## 🙏 Agradecimentos

- Comunidade Python
- Desenvolvedores das bibliotecas pdfplumber e PyPDF2
- Todos que contribuíram com feedback e sugestões

---

**Nota**: Este projeto é fornecido "como está", sem garantias. Use por sua conta e risco.
