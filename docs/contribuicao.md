# Guia de Contribuição e Branches - Plataforma de Análise de Dados

## 🤝 Processo de Trabalho em Equipe

Este projeto foi preparado para o desenvolvimento colaborativo. Todas as alterações devem seguir o modelo de branches abaixo para manter a estabilidade do produto em produção.

## 🌿 Estratégia de Branches (Git Flow Simplificado)

Adotamos a seguinte nomenclatura para branches:
- **`main`**: Branch de produção. Código sempre estável, homologado e testado. É o backup definitivo do sistema.
- **`feature/*`**: Utilizada para desenvolvimento de novas funcionalidades (ex: `feature/sistema-de-login`).
- **`fix/*`**: Utilizada para correção de bugs identificados em ambiente de homologação ou dev.
- **`hotfix/*`**: Utilizada para correções críticas urgentes feitas diretamente a partir de produção.
- **`release/*`**: Preparação de uma nova versão para envio a homologação e produção.

## 💬 Padrão de Mensagens de Commit (Conventional Commits)
Gostaríamos de manter as mensagens de commit padronizadas:
- `feat(modulo): adiciona nova funcionalidade`
- `fix(modulo): corrige comportamento incorreto`
- `docs(readme): atualiza instruções de instalação`
- `style(css): melhora espaçamentos do layout`
- `refactor(modulo): melhora legibilidade do código`
