# Guia de Contribuição

Obrigado por considerar contribuir com o Renomeador Inteligente de Comprovantes! 🎉

## Como Contribuir

### Reportando Bugs

Se você encontrou um bug, por favor abra uma issue incluindo:

- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs comportamento atual
- Screenshots (se aplicável)
- Informações do ambiente:
  - Versão do Python
  - Sistema operacional
  - Versão das dependências

### Sugerindo Melhorias

Para sugerir uma nova funcionalidade:

1. Verifique se já não existe uma issue similar
2. Abra uma nova issue com a tag `enhancement`
3. Descreva claramente:
   - O problema que a funcionalidade resolve
   - Como você imagina que ela funcionaria
   - Exemplos de uso

### Pull Requests

1. **Fork o repositório**
2. **Clone seu fork**
   ```bash
   git clone https://github.com/seu-usuario/renomeador-comprovantes.git
   ```

3. **Crie uma branch**
   ```bash
   git checkout -b feature/minha-nova-funcionalidade
   ```

4. **Faça suas alterações**
   - Escreva código limpo e comentado
   - Siga o estilo de código existente
   - Adicione docstrings às funções

5. **Teste suas alterações**
   - Teste com diferentes tipos de comprovantes
   - Verifique se não quebrou funcionalidades existentes

6. **Commit suas mudanças**
   ```bash
   git commit -m "feat: adiciona suporte para banco X"
   ```

7. **Push para seu fork**
   ```bash
   git push origin feature/minha-nova-funcionalidade
   ```

8. **Abra um Pull Request**
   - Descreva as mudanças claramente
   - Referencie issues relacionadas
   - Aguarde review

## Padrões de Código

### Estilo Python

- Siga o [PEP 8](https://pep8.org/)
- Use nomes descritivos para variáveis e funções
- Máximo de 100 caracteres por linha (quando possível)
- Use type hints quando apropriado

### Convenção de Commits

Use commits semânticos:

- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Mudanças na documentação
- `style:` - Formatação, espaços em branco, etc
- `refactor:` - Refatoração de código
- `test:` - Adição ou correção de testes
- `chore:` - Tarefas de manutenção

Exemplo:
```
feat: adiciona suporte para comprovantes Itaú
```

### Documentação

- Documente todas as funções públicas
- Use docstrings no formato:
  ```python
  def minha_funcao(parametro):
      """
      Breve descrição da função.
      
      Args:
          parametro (tipo): Descrição do parâmetro
          
      Returns:
          tipo: Descrição do retorno
      """
  ```

## Adicionando Suporte para Novos Bancos

Para adicionar suporte a um novo banco:

1. Adicione a lógica de identificação em `identificar_tipo_comprovante()`
2. Crie uma função `extrair_dados_NOME_BANCO()`
3. Documente os campos extraídos
4. Adicione exemplos ao README
5. Teste com comprovantes reais (remova dados sensíveis!)

## Código de Conduta

- Seja respeitoso e inclusivo
- Aceite críticas construtivas
- Foque no que é melhor para a comunidade
- Mostre empatia com outros membros

## Dúvidas?

Se tiver qualquer dúvida, sinta-se à vontade para:
- Abrir uma issue com a tag `question`
- Comentar em issues/PRs existentes

Obrigado por contribuir! 🚀
