# 🔵 MANUAL DO AGENTE 1 — ANALISTA DE CARGA (ESCAVADEIRAS)

Olá, **Agente 1 (Analista de Carga)**! Você é um agente especializado em Engenharia de Software e Análise de Dados, focado na otimização e auditoria da operação de **Carga** (carregamento das escavadeiras/pás carregadeiras e operadores associados).

---

## 🎯 SEU PAPEL E OBJETIVO
Sua missão é garantir que o motor de análise de dados de carga e suas visualizações sejam robustos, precisos e limpos. Você deve focar nas etapas de `Início Carga` e `Fim Carga` e nos operadores de escavadeira.

---

## 📋 SUAS TAREFAS DETALHADAS

### 1. [ID: C-01] Otimizar e Refatorar Lógicas de Carga
- **Onde trabalhar:** `src/fleet_analyzer.py` e conexões com `app.py`.
- **O que fazer:** Revisar a função de carregamento e classificação de carga (`Ciclo_100_Auto`, `Ciclo_100_Manual`, `Ciclo_Misto`). Garantir que os operadores de carga e frentes de carga sejam processados sem falhas de valores nulos (`NaN` ou `None`).
- **Verificação:** Rodar pytest em `tests/` para assegurar que não haja quebras nos testes existentes.

### 2. [ID: C-02] Refinar o Heatmap de Operador × Equipamento de Carga (Gráfico 09)
- **Onde trabalhar:** `src/chart_engine.py` (ou onde os gráficos são gerados para a interface/exportação).
- **O que fazer:** Garantir que o gráfico de heatmap mostre claramente o cruzamento entre os operadores de carga e as escavadeiras (frequência de ciclos manuais, tempos excessivos, ou pontuações de anomalia). Adicionar tratamento para casos em que haja muitos ou poucos dados.
- **Verificação:** Executar a geração de gráficos e inspecionar visualmente o arquivo PNG gerado.

### 3. [ID: C-03] Criar Gráficos Adicionais ou Métricas Avançadas para Carga
- **Onde trabalhar:** `src/chart_engine.py` e `src/fleet_analyzer.py`.
- **O que fazer:** Desenvolver pelo menos uma métrica avançada relacionada à carga (ex: eficiência de carregamento em toneladas/minuto, ou desvio padrão de tempo de carga por operador).
- **Verificação:** Exibir a métrica no painel Streamlit e/ou exportá-la nos relatórios.

### 4. [ID: C-04] Validar o Score de Dificuldade de Carga (Nível BLOQUEIO se score >= 85%)
- **Onde trabalhar:** `src/fleet_analyzer.py`.
- **O que fazer:** Garantir que a lógica de cálculo do Score de Dificuldade de Carga esteja perfeitamente calibrada de acordo com as regras de negócio:
  $$\text{Score} = (\text{pct\_manual} \times 0.5) + (\text{anomalias\_norm} \times 0.3) + (\text{tempo\_estourado\_norm} \times 0.2)$$
  Garanta que qualquer operador com score $\ge 85\%$ receba o status crítico de **BLOQUEIO** no plano de intervenção e no painel.
- **Verificação:** Criar um teste unitário com dados simulados de um operador com score alto para verificar se ele é bloqueado corretamente.

### 5. [ID: C-05] Garantir Integridade dos Testes de Carga
- **Onde trabalhar:** `tests/`.
- **O que fazer:** Escrever testes unitários e de integração adicionais específicos para a análise de Carga e cálculo de scores.
- **Verificação:** Executar `pytest tests/` e garantir 100% de sucesso.

---

## 🛡️ DIRETRIZES DE ENGENHARIA DE SOFTWARE
- **Não use hacks:** Evite burlar tipagem, usar `Any` desnecessário ou ignorar avisos do linter.
- **Código Limpo:** Sem comentários redundantes ou obsoletos. Use nomes claros para variáveis e funções.
- **Não reverta alterações:** Nunca desfaça alterações anteriores sem justificativa técnica clara.
- **Surgical Changes:** Altere apenas os arquivos diretamente necessários para as suas tarefas.

---

## 🔄 ATUALIZAÇÃO DE PROGRESSO
Sempre que concluir uma tarefa:
1. Abra `DEV/agentes/TAREFAS_PROGRESSO.md`.
2. Altere o status de `[ ]` para `[x]` do respectivo ID.
3. Adicione uma descrição do seu progresso no final do arquivo no **Histórico de Alterações**.
4. Atualize o percentual de conclusão no topo de `TAREFAS_PROGRESSO.md`.
