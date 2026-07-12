# 📊 PAINEL DE CONTROLE E PROGRESSO DOS AGENTES — DEV

Este é o documento central de acompanhamento de melhorias do sistema de análise de dados de frota. À medida que cada Agente de IA executa e valida suas tarefas, ele deve marcar a tarefa correspondente como concluída `[x]` e atualizar o percentual de progresso.

---

## 📈 STATUS GERAL DO PROJETO DEV

- **Progresso de Automação de Carga (Agente 1):** 0% concluído
- **Progresso de Automação de Basculamento (Agente 2):** 0% concluído
- **Status Geral do Projeto:** 🟡 Planejamento Concluído / Em Execução

---

## 🔵 AGENTE 1: ANALISTA DE CARGA (ESCAVADEIRAS)

O **Agente 1** é responsável por refatorar, otimizar e auditar o fluxo de **Carga** (início/fim de carregamento, escavadeiras e operadores de carga).

| Status | ID | Descrição da Tarefa | Arquivos Impactados | Responsável |
| :---: | :---: | :--- | :--- | :---: |
| [ ] | C-01 | Otimizar e refatorar `analise_carga.py` para melhor legibilidade e robustez | `src/fleet_analyzer.py`, `app.py` | Agente 1 |
| [ ] | C-02 | Refinar o Heatmap de Operador × Equipamento de Carga (Gráfico 09) | `src/chart_engine.py` | Agente 1 |
| [ ] | C-03 | Criar gráficos adicionais ou métricas avançadas para Carga | `src/chart_engine.py` | Agente 1 |
| [ ] | C-04 | Validar o Score de Dificuldade de Carga (Bloqueio se score >= 85%) | `src/fleet_analyzer.py` | Agente 1 |
| [ ] | C-05 | Garantir integridade dos testes de regressão de Carga | `tests/` | Agente 1 |

---

## 🟠 AGENTE 2: ANALISTA DE BASCULAMENTO (CAMINHÕES)

O **Agente 2** é responsável por implementar a lógica detalhada de **Basculamento** (descargas, operadores de caminhão, geofences, coordenadas GPS).

| Status | ID | Descrição da Tarefa | Arquivos Impactados | Responsável |
| :---: | :---: | :--- | :--- | :---: |
| [ ] | B-01 | Implementar análise separada de operadores de Basculamento (motoristas de caminhão por TAG) | `src/fleet_analyzer.py` | Agente 2 |
| [ ] | B-02 | Criar o Score de Dificuldade de Basculamento (mesma lógica do score de carga, pesos específicos) | `src/fleet_analyzer.py` | Agente 2 |
| [ ] | B-03 | Incluir operadores de Basculamento no Plano de Intervenção (Prioridade 1 ampliada) | `src/fleet_analyzer.py` | Agente 2 |
| [ ] | B-04 | Implementar o Gráfico de Evolução Diária da Automação de Basculamento | `src/chart_engine.py` | Agente 2 |
| [ ] | B-05 | Implementar o Heatmap de Operador de Caminhão × Destino de descarga | `src/chart_engine.py` | Agente 2 |
| [ ] | B-06 | Criar testes automatizados para validar a lógica de Basculamento | `tests/` | Agente 2 |

---

## 🛠️ COMO OS AGENTES DEVEM ATUALIZAR ESTE DOCUMENTO

Cada agente de IA, ao concluir uma tarefa, **DEVE**:
1. Utilizar a ferramenta `replace` neste arquivo `DEV/agentes/TAREFAS_PROGRESSO.md`.
2. Alterar o status correspondente de `[ ]` para `[x]`.
3. Recalcular os percentuais de progresso de Carga/Basculamento no topo do documento.
4. Adicionar uma linha na seção **Histórico de Alterações** (abaixo) especificando o que foi feito, o ID da tarefa, e a data/hora.

---

## 📝 HISTÓRICO DE ALTERAÇÕES

*Nenhuma alteração realizada ainda. Aguardando o início dos trabalhos dos Agentes.*
