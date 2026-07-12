# Guia de Desenvolvimento - Plataforma de Análise de Dados

## 💻 Padrões de Código e Desenvolvimento

Para manter a consistência e a qualidade do código fonte do **Plataforma de Análise de Dados**, siga as diretrizes abaixo.

### Padrão de Estilo de Código
- **Formatadores/Linters:** Utilize ferramentas automáticas de qualidade como `ruff` ou `eslint` antes de realizar commits.
- **Comentários:** Escreva comentários curtos, claros e em português apenas para explicar lógicas complexas ou decisões de negócio atípicas.
- **Tipagem:** Sempre que aplicável, utilize tipagem estática explícita para evitar erros em tempo de execução.

### Fluxo de Trabalho de Alterações
1. Crie uma nova branch a partir de `main` (`git checkout -b feature/nome-da-funcionalidade`).
2. Implemente o código seguindo as convenções.
3. Escreva testes para validar a nova lógica.
4. Execute e passe nos testes locais.
5. Crie o Pull Request para mesclagem na `main`.
