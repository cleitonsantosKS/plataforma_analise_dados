"""Export services for HTML, PNG, PDF/Text Reports and Power BI packages."""

from __future__ import annotations

import json
import zipfile
from datetime import datetime
from io import BytesIO
from pathlib import Path

import pandas as pd

from .chart_engine import GeneratedChart

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "powerbi"


def figure_to_html(fig, include_plotlyjs: str = "cdn") -> str:
    return fig.to_html(full_html=False, include_plotlyjs=include_plotlyjs)


def figure_to_png(fig) -> bytes:
    return fig.to_image(format="png", width=1200, height=700, scale=2)


def generate_fleet_text_report(stats: dict) -> str:
    """Generates the premium structured Master Fleet Investigation Report as text."""
    summary = stats["summary"]
    etapas_stats = stats["etapas_stats"]
    rankings = stats["operators_ranking"]
    anom_counts = stats["anomaly_counts"]
    events = stats["anomalous_events"]

    lines = []
    lines.append("=" * 80)
    lines.append("  RELATÓRIO MASTER DE DESEMPENHO, ADESÃO E AUDITORIA DE FROTAS")
    lines.append("=" * 80)
    lines.append(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")

    lines.append("\n[ 1. RESUMO OPERACIONAL GERAL ]")
    lines.append(f"Quantidade total de ciclos analisados  : {summary['total_cycles']:,}".replace(",", "."))
    lines.append(f"Quantidade de ciclos OK                : {summary['ok_cycles']:,}".replace(",", "."))
    lines.append(f"Quantidade de ciclos com ERRO/Anomalia : {summary['error_cycles']:,}".replace(",", "."))
    lines.append(f"Quantidade de 'Basculou na Cava Sul'   : {summary['cava_sul_cycles']:,}".replace(",", "."))
    lines.append("-" * 50)
    lines.append(f"Ciclos 100% Automáticos (4 etapas)     : {summary['auto_100_percent']:,}".replace(",", "."))
    lines.append(f"Ciclos Manuais (4 etapas)              : {summary['manual_100_percent']:,}".replace(",", "."))
    lines.append(f"Ciclos Mistos (Intervenção Parcial)    : {summary['mixed_cycles']:,}".replace(",", "."))

    lines.append("\n[ 2. MÉTRICAS DE QUALIDADE E AUTOMAÇÃO ]")
    lines.append(f"Taxa de Confiabilidade do Sistema      : {summary['reliability_rate']:.2f}%")
    lines.append(f"Taxa de Inconsistência Operacional     : {summary['inconsistency_rate']:.2f}%")
    lines.append(f"Taxa de Falsos Positivos Estimada      : {summary['false_positive_rate']:.2f}%")
    lines.append(f"Taxa de Perda GPS (Coordenada Zerada)  : {summary['gps_loss_rate']:.2f}%")
    lines.append(f"Taxa de Transição Manual -> Auto       : {summary['manual_to_auto_rate']:.2f}%")

    lines.append("\n[ 3. PERCENTUAL DE AUTOMAÇÃO POR ETAPA DO CICLO ]")
    for etapa, val in etapas_stats.items():
        lines.append(f"--- {etapa.upper()} ---")
        for status, counts in val.items():
            lines.append(f"  > {status}: {counts['count']} apontamentos ({counts['percentage']:.1f}%)")

    lines.append("\n[ 4. RANKING DE ADESÃO DOS OPERADORES (Fim Basculamento) ]")
    lines.append("> TOP 10: MAIS ASSERTIVOS NO AUTOMÁTICO:")
    for i, op in enumerate(rankings["top_auto"], 1):
        lines.append(f"  [{i}] Operador: {op['operator']} | TAG: {op['truck']} | Turma: {op.get('turma', 'N/A')} -> {op['cycles']} ciclos")
    if not rankings["top_auto"]:
        lines.append("  Nenhuma ocorrência registrada.")

    lines.append("\n> TOP 10: MAIOR USO DO MODO MANUAL (Possível necessidade de reciclagem):")
    for i, op in enumerate(rankings["top_manual"], 1):
        lines.append(f"  [{i}] Operador: {op['operator']} | TAG: {op['truck']} | Turma: {op.get('turma', 'N/A')} -> {op['cycles']} ciclos")
    if not rankings["top_manual"]:
        lines.append("  Nenhuma ocorrência registrada.")

    lines.append("\n[ 5. ANÁLISE DE PADRÕES E ANOMALIAS DETECTADAS ]")
    lines.append(f"Distância Cheio = 0                    : {anom_counts['dist_zero']}")
    lines.append(f"Origem igual ao Destino                : {anom_counts['origin_equals_destination']}")
    lines.append(f"Coordenadas 0,0                        : {anom_counts['gps_coords_zero']}")
    lines.append(f"Tempos incompatíveis (>15min basc)     : {anom_counts['high_basculamento_time']}")
    lines.append(f"Troca Manual -> Auto (fechamento)       : {anom_counts['manual_to_auto_transition']}")

    lines.append("\n[ 6. EVENTOS CRÍTICOS DETALHADOS E AUDITORIA ]")
    lines.append("🚨 ALTA SEVERIDADE / ANOMALIA / CRÍTICO 🚨\n")

    if events:
        for idx, ev in enumerate(events, 1):
            lines.append(f"   [{ev['severity']}] #{idx} TAG: {ev['truck']} | Op: {ev['operator']} | Início: {ev['date']} {ev['time_start']}")
            lines.append(f"      - Hipótese: {ev['hypothesis']}")
            lines.append(f"      - Trajeto: {ev['origin']} -> {ev['destination']}")
            lines.append(f"      - Dados: Basc({ev['time_basculamento']:.2f} min) | Dist({ev['distance']:.2f} m) | Coord({ev['latitude']}, {ev['longitude']})")
            lines.append(f"      - Rota GPS: {ev['gps_link']}")
            lines.append("   " + "-" * 50)
    else:
        lines.append("   Nenhuma anomalia de alta severidade identificada nos ciclos analisados.")

    lines.append("\n" + "=" * 80)
    lines.append("Fim do Relatório Investigativo de Frota - Plataforma Web")
    return "\n".join(lines)


def build_powerbi_metadata(df: pd.DataFrame) -> dict:
    """Power BI standard metadata configuration file structure."""
    columns = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        kind = "text"
        if "datetime" in dtype:
            kind = "datetime"
        elif "int" in dtype or "float" in dtype:
            kind = "numeric"
        columns.append(
            {
                "nome": col,
                "tipo_sugerido": kind,
                "valores_unicos": int(df[col].nunique(dropna=True)),
                "nulos": int(df[col].isna().sum()),
            }
        )
    return {
        "gerado_em": datetime.now().isoformat(),
        "linhas": len(df),
        "colunas": len(df.columns),
        "campos": columns,
        "instrucoes": [
            "Abra o Power BI Desktop",
            "Obter Dados > Texto/CSV ou Excel > selecione dados_limpos",
            "Use o arquivo modelo_relatorio.pbix se disponível na pasta assets/powerbi",
            "Ajuste tipos conforme colunas em powerbi_modelo.json",
        ],
    }


def create_export_zip(
    df: pd.DataFrame,
    charts: list[GeneratedChart],
    include_html: bool = True,
    include_png: bool = True,
    fleet_stats: dict | None = None,
) -> bytes:
    """Assembles all cleaned assets, charts, Power BI schemas and optional Fleet Reports into a ZIP."""
    buffer = BytesIO()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Cleaned CSV with UTF-8 BOM for Excel compatibility
        csv_buf = BytesIO()
        df.to_csv(csv_buf, index=False, sep=";", encoding="utf-8-sig")
        zf.writestr(f"dados_limpos_{stamp}.csv", csv_buf.getvalue())

        # 2. Cleaned Excel
        xlsx_buf = BytesIO()
        with pd.ExcelWriter(xlsx_buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Dados")
        zf.writestr(f"dados_limpos_{stamp}.xlsx", xlsx_buf.getvalue())

        # 3. Power BI Metadata json schema mapping
        meta = build_powerbi_metadata(df)
        zf.writestr("powerbi_modelo.json", json.dumps(meta, ensure_ascii=False, indent=2))

        # 4. Readme text
        readme = (ASSETS_DIR / "COMO_IMPORTAR_POWERBI.txt")
        if readme.exists():
            zf.writestr("COMO_IMPORTAR_POWERBI.txt", readme.read_text(encoding="utf-8"))
        else:
            zf.writestr(
                "COMO_IMPORTAR_POWERBI.txt",
                "Importe dados_limpos no Power BI Desktop e configure os visuais.\n",
            )

        # 5. Templates if present
        pbit_readme = ASSETS_DIR / "LEIA-ME_TEMPLATE.txt"
        if pbit_readme.exists():
            zf.writestr("powerbi/LEIA-ME_TEMPLATE.txt", pbit_readme.read_text(encoding="utf-8"))

        pbit_file = ASSETS_DIR / "modelo_relatorio.pbit"
        if pbit_file.exists():
            zf.writestr("powerbi/modelo_relatorio.pbit", pbit_file.read_bytes())

        # 6. Specialized Fleet Text Report
        if fleet_stats:
            report_text = generate_fleet_text_report(fleet_stats)
            zf.writestr(f"relatorio_auditoria_frota_{stamp}.txt", report_text)

        # 7. Charts export HTML and PNG
        for chart in charts:
            safe_id = chart.chart_id.replace(" ", "_")
            if include_html:
                html = figure_to_html(chart.figure)
                zf.writestr(f"graficos/html/{safe_id}.html", html)
            if include_png:
                try:
                    png = figure_to_png(chart.figure)
                    zf.writestr(f"graficos/png/{safe_id}.png", png)
                except Exception:
                    zf.writestr(
                        f"graficos/png/{safe_id}.txt",
                        "PNG nao gerado. Instale kaleido: pip install kaleido\n",
                    )

    buffer.seek(0)
    return buffer.getvalue()
