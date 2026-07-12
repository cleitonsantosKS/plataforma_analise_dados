# 🤖 SISTEMA MULTIAGENTE DE DESENVOLVIMENTO (DEV)

Bem-vindo ao ambiente de melhorias automatizadas do sistema de análise de dados de frota mineira. Este diretório contém as diretrizes, atribuições de tarefas e painéis de controle para coordenar o trabalho cooperativo de dois agentes de inteligência artificial.

## 👥 OS DOIS AGENTES E SEUS PAPÉIS

1. **🔵 Agente 1 — Analista de Carga (Escavadeiras)**
   - **Foco:** Operações de carga (`Início Carga`, `Fim Carga`), escavadeiras, frentes de carregamento e operadores de escavadeira.
   - **Manual de Trabalho:** [AGENTE_1_CARGA.md](AGENTE_1_CARGA.md)
   
2. **🟠 Agente 2 — Analista de Basculamento (Caminhões)**
   - **Foco:** Operações de basculamento/descarga (`Início Basculamento`, `Fim Basculamento`), caminhões, motoristas de transporte, geofences e sinal de GPS.
   - **Manual de Trabalho:** [AGENTE_2_BASCULAMENTO.md](AGENTE_2_BASCULAMENTO.md)

## 📊 PAINEL DE CONTROLE

O progresso unificado das tarefas atribuídas a cada um dos agentes é centralizado e atualizado dinamicamente no arquivo:
- **Painel de Controle:** [TAREFAS_PROGRESSO.md](TAREFAS_PROGRESSO.md)

## ⚙️ FLUXO DE TRABALHO PARA OS AGENTES

1. **Leitura:** O agente deve ler seu respectivo manual (`AGENTE_1_CARGA.md` ou `AGENTE_2_BASCULAMENTO.md`) para compreender suas tarefas e regras de negócio.
2. **Implementação Cirúrgica:** Realizar modificações precisas no código da pasta `DEV/src/` e `DEV/tests/`.
3. **Validação:** Rodar testes e análises estáticas na pasta `DEV` para assegurar que a nova lógica não quebrou nada e funciona perfeitamente.
4. **Atualização de Progresso:** Atualizar o arquivo [TAREFAS_PROGRESSO.md](TAREFAS_PROGRESSO.md) marcando a tarefa como concluída `[x]`, alterando os percentuais de progresso e registrando um breve resumo no **Histórico de Alterações**.
