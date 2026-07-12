# 🟠 MANUAL DO AGENTE 2 — ANALISTA DE BASCULAMENTO (CAMINHÕES)

Olá, **Agente 2 (Analista de Basculamento)**! Você é um agente especializado em Engenharia de Software e Análise Geográfica de Frota, focado nas operações de **Basculamento** (descarga dos caminhões, motoristas de caminhão por TAG, geofences, sinal de GPS e rotinas associadas).

---

## 🎯 SEU PAPEL E OBJETIVO
Sua missão é desenvolver a análise aprofundada da operação de **Basculamento**, separando os motoristas dos caminhões (operadores de basculamento) e avaliando-os com rigor analítico. Você deve implementar o cálculo de score de dificuldade de basculamento, gerar relatórios de anomalias focados no basculamento, estender os gráficos da plataforma e enriquecer o Plano de Intervenção.

---

## 📋 SUAS TAREFAS DETALHADAS

### 1. [ID: B-01] Análise Separada dos Operadores de Basculamento (Motoristas)
- **Onde trabalhar:** `src/fleet_analyzer.py` e `app.py`.
- **O que fazer:** Implementar a lógica de agrupamento e contagem separada para operadores que guiam os caminhões (as colunas `Operador` e `Caminhão` representam os dados de transporte/basculamento). Agrupar os dados por motorista e identificar o índice de automação do basculamento (`Fim Basculamento` ou `Início Basculamento` sendo "Automático").
- **Verificação:** Exibir os rankings de adesão de basculamento e listagem de motoristas no painel principal do Streamlit.

### 2. [ID: B-02] Criar o Score de Dificuldade de Basculamento
- **Onde trabalhar:** `src/fleet_analyzer.py`.
- **O que fazer:** Implementar a fórmula para classificar a dificuldade dos operadores de basculamento de forma análoga à carga:
  $$\text{Score Basculamento} = (\text{pct\_manual} \times 0.5) + (\text{anomalias\_norm} \times 0.3) + (\text{tempo\_estourado\_norm} \times 0.2)$$
  *Onde:*
  - `pct_manual`: % de ciclos de basculamento do operador em que `Fim Basculamento` foi manual.
  - `anomalias_norm`: número total de anomalias cometidas pelo motorista (coordenadas (0,0), transição indevida manual$\rightarrow$automático, distância cheio = 0), normalizado por `min(anomalias / 10, 1.0)`.
  - `tempo_estourado_norm`: ocorrências de Tempo de Basculamento > 15 minutos (esquecimento de tela), normalizado por `min(ocorrencias / 5, 1.0)`.
- **Níveis de Alerta:**
  - $< 0.30$: 🟢 OK
  - $0.30 - 0.59$: 🟡 ATENÇÃO
  - $0.60 - 0.84$: 🔴 CRÍTICO (Reciclagem imediata)
  - $\ge 0.85$: ⚫ BLOQUEIO (Suspensão imediata de operação autônoma)
- **Verificação:** Confirmar que o score calcula valores consistentes de 0 a 100%.

### 3. [ID: B-03] Incluir Operadores de Basculamento no Plano de Intervenção
- **Onde trabalhar:** `src/fleet_analyzer.py` (ou nos relatórios/planos de exportação).
- **O que fazer:** Integrar os operadores com nível **CRÍTICO** ou **BLOQUEIO** no basculamento na Prioridade 1 do Plano de Intervenção. O plano de intervenção deve separar claramente "Operadores de Carga" e "Operadores de Basculamento".
- **Verificação:** Exportar o plano de intervenção e verificar se os motoristas de caminhão com dificuldade crítica estão listados separadamente dos operadores de escavadeira.

### 4. [ID: B-04] Implementar o Gráfico de Evolução Diária da Automação de Basculamento
- **Onde trabalhar:** `src/chart_engine.py`.
- **O que fazer:** Criar um gráfico de linha temporal que exibe a taxa de automação de basculamento dia a dia, para acompanhar a evolução histórica da frota e identificar tendências de piora ou melhoria.
- **Verificação:** Salvar o arquivo como imagem (`11_evolucao_diaria_basculamento.png` ou similar) e renderizá-lo na interface.

### 5. [ID: B-05] Heatmap de Operador de Caminhão × Destino de descarga
- **Onde trabalhar:** `src/chart_engine.py`.
- **O que fazer:** Criar um gráfico heatmap que correlaciona os operadores de caminhão (eixo Y) com os destinos de descarga (eixo X, ex: CAVA SUL, etc.), exibindo a taxa de uso do modo manual. Isso ajuda a identificar se há destinos com pior geofence ou sinal de GPS.
- **Verificação:** Gerar e salvar a imagem do heatmap.

### 6. [ID: B-06] Criar Testes Automatizados para Lógica de Basculamento
- **Onde trabalhar:** `tests/`.
- **O que fazer:** Escrever testes unitários para o score de dificuldade de basculamento e novos cruzamentos estatísticos.
- **Verificação:** Executar `pytest tests/` e garantir que passe.

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
