# Plataforma de Análise de Dados

Plataforma web em Python para **qualquer empresa** fazer upload de planilhas, gerar gráficos interativos automaticamente e exportar resultados (HTML, PNG e pacote Power BI).

## Stack

| Camada | Tecnologia |
|--------|------------|
| Interface | **Streamlit** |
| Dados | **Pandas** |
| Gráficos | **Plotly** |
| Imagens | **Kaleido** |

## Lógica automática de gráficos

- **Linha** — colunas de data/hora + colunas numéricas (evolução temporal)
- **Barra** — categorias (texto com poucas opções) + números ou contagem
- **Pizza/Rosca** — categorias com até 8 valores distintos (proporção)

## Instalação

```bash
cd plataforma_analise_dados
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Executar

```bash
streamlit run app.py
```

Acesse o endereço exibido no terminal (geralmente `http://localhost:8501`).

## Estrutura do projeto

```
plataforma_analise_dados/
├── app.py                 # Interface Streamlit
├── requirements.txt
├── src/
│   ├── data_loader.py     # Leitura CSV/Excel (formato BR)
│   ├── data_cleaner.py    # Limpeza e inferência de tipos
│   ├── column_profiler.py # Classificação de colunas
│   ├── chart_engine.py    # Geração Plotly automática
│   └── export_service.py  # HTML, PNG, ZIP Power BI
└── assets/powerbi/        # Template .pbit e instruções
```

## Power BI

1. Exporte o **Pacote Power BI** na aba Exportação.
2. Importe `dados_limpos_*.csv` ou `.xlsx` no Power BI Desktop.
3. Use `powerbi_modelo.json` como guia de tipos de coluna.
4. Para incluir um template `.pbit`, salve como `assets/powerbi/modelo_relatorio.pbit`.

## Origem

Projeto derivado dos scripts de análise de frota (`relatorio_master.py`, `gerar_graficos_master.py`), generalizado para planilhas de qualquer domínio.
