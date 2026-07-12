"""Plotly charts engine with custom slate & neon dark dashboard styling."""

from __future__ import annotations

from dataclasses import dataclass
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .column_profiler import DatasetProfile, MIN_ROWS_FOR_CHART, pie_eligible_categories
from .fleet_analyzer import clean_numeric_value


@dataclass
class GeneratedChart:
    chart_id: str
    title: str
    chart_type: str  # line | bar | pie
    figure: go.Figure
    x_col: str | None = None
    y_col: str | None = None


# Premium color definitions (Slate & Neon Theme)
COLOR_AUTO = "#10B981"      # Emerald Green
COLOR_MANUAL = "#EF4444"    # Rose Red
COLOR_MIXED = "#F59E0B"     # Amber Orange
COLOR_NEON_BLUE = "#3B82F6"  # Bright Blue
COLOR_NEON_PINK = "#EC4899"  # Neon Pink
COLOR_NEON_PURPLE = "#8B5CF6" # Violet Purple

THEME_GRID_COLOR = "#334155" # Slate 700 grid
THEME_FONT_COLOR = "#F8FAFC" # Slate 50 font
THEME_LABEL_COLOR = "#94A3B8" # Slate 400 label


def apply_premium_theme(fig: go.Figure, title: str):
    """Applies premium glassmorphism dark theme styling to a Plotly figure."""
    fig.update_layout(
        title={
            "text": title,
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": {"size": 16, "color": THEME_FONT_COLOR, "family": "Inter, sans-serif"}
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=THEME_FONT_COLOR, family="Inter, sans-serif"),
        xaxis=dict(
            gridcolor=THEME_GRID_COLOR,
            tickfont=dict(color=THEME_LABEL_COLOR),
            title=dict(font=dict(color=THEME_FONT_COLOR)),
            zerolinecolor=THEME_GRID_COLOR,
            linecolor=THEME_GRID_COLOR,
        ),
        yaxis=dict(
            gridcolor=THEME_GRID_COLOR,
            tickfont=dict(color=THEME_LABEL_COLOR),
            title=dict(font=dict(color=THEME_FONT_COLOR)),
            zerolinecolor=THEME_GRID_COLOR,
            linecolor=THEME_GRID_COLOR,
        ),
        hoverlabel=dict(
            bgcolor="#1E293B",
            font_size=13,
            font_color=THEME_FONT_COLOR,
            font_family="Inter, sans-serif"
        ),
        legend=dict(
            font=dict(color=THEME_LABEL_COLOR),
            bgcolor="rgba(15, 23, 42, 0.75)",
            bordercolor=THEME_GRID_COLOR,
            borderwidth=1,
            orientation="h",
            yanchor="bottom",
            y=-0.22,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=65, b=65, l=55, r=35)
    )


def _aggregate_time_series(df: pd.DataFrame, date_col: str, num_col: str) -> pd.DataFrame:
    tmp = df[[date_col, num_col]].dropna().copy()
    tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
    tmp = tmp.dropna()
    if tmp.empty:
        return tmp
    freq = "D" if tmp[date_col].nunique() > 1 else "h"
    grouped = tmp.set_index(date_col).resample(freq)[num_col].sum().reset_index()
    grouped.columns = [date_col, num_col]
    return grouped


def _build_line_charts(df: pd.DataFrame, profile: DatasetProfile) -> list[GeneratedChart]:
    charts = []
    for date_col in profile.datetime_cols:
        for num_col in profile.numeric_cols:
            if date_col == num_col:
                continue
            agg = _aggregate_time_series(df, date_col, num_col)
            if len(agg) < MIN_ROWS_FOR_CHART:
                continue
            fig = px.line(
                agg,
                x=date_col,
                y=num_col,
                markers=True,
            )
            fig.update_traces(line=dict(color=COLOR_NEON_BLUE, width=3), marker=dict(size=6))
            apply_premium_theme(fig, f"Evolução de {num_col} no Tempo")
            fig.update_layout(hovermode="x unified")
            charts.append(
                GeneratedChart(
                    chart_id=f"line_{date_col}_{num_col}",
                    title=f"Linha — {num_col} × {date_col}",
                    chart_type="line",
                    figure=fig,
                    x_col=date_col,
                    y_col=num_col,
                )
            )
            if len(charts) >= 5:
                return charts
    return charts


def _build_bar_charts(df: pd.DataFrame, profile: DatasetProfile) -> list[GeneratedChart]:
    charts = []
    for cat_col in profile.categorical_cols:
        for num_col in profile.numeric_cols:
            grouped = (
                df.groupby(cat_col, dropna=False)[num_col]
                .sum()
                .reset_index()
                .sort_values(num_col, ascending=False)
                .head(15)
            )
            if len(grouped) < 2:
                continue
            fig = px.bar(
                grouped,
                x=cat_col,
                y=num_col,
                text=num_col,
            )
            fig.update_traces(
                marker_color=COLOR_NEON_BLUE,
                texttemplate="%{text:.2s}",
                textposition="outside",
                marker_line_color=COLOR_NEON_BLUE,
                marker_line_width=1.5
            )
            apply_premium_theme(fig, f"Comparativo: {num_col} por {cat_col}")
            fig.update_layout(xaxis_tickangle=-35)
            charts.append(
                GeneratedChart(
                    chart_id=f"bar_{cat_col}_{num_col}",
                    title=f"Barra — {num_col} × {cat_col}",
                    chart_type="bar",
                    figure=fig,
                    x_col=cat_col,
                    y_col=num_col,
                )
            )
            if len(charts) >= 8:
                return charts

        counts = df[cat_col].value_counts().head(15).reset_index()
        counts.columns = [cat_col, "Quantidade"]
        if len(counts) >= 2:
            fig = px.bar(
                counts,
                x=cat_col,
                y="Quantidade",
            )
            fig.update_traces(
                marker_color=COLOR_NEON_PINK,
                marker_line_color=COLOR_NEON_PINK,
                marker_line_width=1.5
            )
            apply_premium_theme(fig, f"Volume por {cat_col}")
            fig.update_layout(xaxis_tickangle=-35)
            charts.append(
                GeneratedChart(
                    chart_id=f"bar_count_{cat_col}",
                    title=f"Barra — contagem × {cat_col}",
                    chart_type="bar",
                    figure=fig,
                    x_col=cat_col,
                    y_col="Quantidade",
                )
            )
    return charts


def _build_pie_charts(df: pd.DataFrame, profile: DatasetProfile) -> list[GeneratedChart]:
    charts = []
    for cat_col in profile.categorical_cols:
        if not pie_eligible_categories(df, cat_col):
            continue
        counts = df[cat_col].value_counts().reset_index()
        counts.columns = [cat_col, "Quantidade"]
        fig = px.pie(
            counts,
            names=cat_col,
            values="Quantidade",
            hole=0.4,
        )
        fig.update_traces(
            textinfo="percent+label",
            marker=dict(line=dict(color="#1E293B", width=2))
        )
        apply_premium_theme(fig, f"Proporção: distribuição de {cat_col}")
        charts.append(
            GeneratedChart(
                chart_id=f"pie_{cat_col}",
                title=f"Pizza — {cat_col}",
                chart_type="pie",
                figure=fig,
                x_col=cat_col,
            )
        )
        if len(charts) >= 5:
            break
    return charts


def generate_all_charts(df: pd.DataFrame, profile: DatasetProfile) -> list[GeneratedChart]:
    """Generates charts for generic files using high-end custom styles."""
    if df is None or df.empty or len(df) < MIN_ROWS_FOR_CHART:
        return []

    charts: list[GeneratedChart] = []
    charts.extend(_build_line_charts(df, profile))
    charts.extend(_build_bar_charts(df, profile))
    charts.extend(_build_pie_charts(df, profile))
    return charts


# =========================================================================
# SPECIALIZED FLEET GRAPHICS GENERATOR (POWER BI SLATE & NEON AESTHETICS)
# =========================================================================

def generate_fleet_charts(df: pd.DataFrame) -> list[GeneratedChart]:
    """Generates the 5 premium interactive charts for Fleet Intelligence.
    
    Fully stylized for Slate and Neon dashboard experience.
    """
    charts = []
    
    # 1. PIZZA - TIPO DE CICLO GERAL
    # Make sure cycle columns exist
    df_clean = df.copy()
    
    text_cols = ["Início Carga", "Fim Carga", "Início Basculamento", "Fim Basculamento"]
    for col in text_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()
        else:
            df_clean[col] = "Desconhecido"

    df_clean["Ciclo_Auto"] = (
        df_clean["Início Carga"].str.contains("Automático", case=False, na=False) &
        df_clean["Fim Carga"].str.contains("Automático", case=False, na=False) &
        df_clean["Início Basculamento"].str.contains("Automático", case=False, na=False) &
        df_clean["Fim Basculamento"].str.contains("Automático", case=False, na=False)
    )

    df_clean["Ciclo_Manual"] = (
        df_clean["Início Carga"].str.contains("Manual", case=False, na=False) &
        df_clean["Fim Carga"].str.contains("Manual", case=False, na=False) &
        df_clean["Início Basculamento"].str.contains("Manual", case=False, na=False) &
        df_clean["Fim Basculamento"].str.contains("Manual", case=False, na=False)
    )

    def classificar_ciclo(row):
        if row["Ciclo_Auto"]:
            return "100% Automático"
        if row["Ciclo_Manual"]:
            return "100% Manual"
        return "Ciclo Misto / Parcial"

    df_clean["Tipo de Ciclo"] = df_clean.apply(classificar_ciclo, axis=1)
    
    counts_ciclos = df_clean["Tipo de Ciclo"].value_counts().reset_index()
    counts_ciclos.columns = ["Tipo de Ciclo", "Quantidade"]
    
    fig_pizza = px.pie(
        counts_ciclos,
        names="Tipo de Ciclo",
        values="Quantidade",
        hole=0.45,
        color="Tipo de Ciclo",
        color_discrete_map={
            "100% Automático": COLOR_AUTO,
            "100% Manual": COLOR_MANUAL,
            "Ciclo Misto / Parcial": COLOR_MIXED
        }
    )
    fig_pizza.update_traces(
        textinfo="percent+label",
        marker=dict(line=dict(color="#0F172A", width=2.5))
    )
    apply_premium_theme(fig_pizza, "1. Distribuição de Ciclos: Auto vs Manual vs Misto")
    charts.append(
        GeneratedChart(
            chart_id="fleet_cycle_pizza",
            title="Distribuição Geral de Ciclos",
            chart_type="pie",
            figure=fig_pizza
        )
    )

    # 2. BARRAS DUPLAS - ADESÃO POR ETAPA
    etapas = ["Início Carga", "Fim Carga", "Início Basculamento", "Fim Basculamento"]
    dados_etapas = []

    for etapa in etapas:
        if etapa in df_clean.columns:
            counts = df_clean[etapa].value_counts()
            total = counts.sum()
            auto = counts.get("Automático", 0)
            manual = counts.get("Manual", 0)
            dados_etapas.append({
                "Etapa": etapa,
                "Automático": float((auto/total)*100) if total > 0 else 0.0,
                "Manual": float((manual/total)*100) if total > 0 else 0.0
            })

    df_etapas = pd.DataFrame(dados_etapas)
    
    # Restructure for plotting
    df_etapas_melt = pd.melt(df_etapas, id_vars=["Etapa"], value_vars=["Automático", "Manual"],
                             var_name="Modo", value_name="Adesão (%)")
                             
    fig_etapas = px.bar(
        df_etapas_melt,
        x="Etapa",
        y="Adesão (%)",
        color="Modo",
        barmode="group",
        color_discrete_map={"Automático": COLOR_AUTO, "Manual": COLOR_MANUAL},
        text="Adesão (%)"
    )
    fig_etapas.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        marker_line_color="#0F172A",
        marker_line_width=1.5
    )
    apply_premium_theme(fig_etapas, "2. Percentual de Adesão por Etapa do Ciclo")
    fig_etapas.update_layout(yaxis_ticksuffix="%", yaxis_range=[0, 110])
    charts.append(
        GeneratedChart(
            chart_id="fleet_adhesion_steps",
            title="Adesão por Etapa",
            chart_type="bar",
            figure=fig_etapas
        )
    )

    # 3. BARRAS HORIZONTAIS - MÉTRICAS DE QUALIDADE (ERROS/ANOMALIAS)
    df_clean["Dist_0"] = df_clean.get("Distância Cheio (m)", "0").apply(clean_numeric_value) == 0.0
    df_clean["Coord_00"] = (
        (df_clean.get("Latitude (Basculamento)", "0").apply(clean_numeric_value) == 0.0) & 
        (df_clean.get("Longitude (Basculamento)", "0").apply(clean_numeric_value) == 0.0)
    )
    df_clean["Trans_Man_Aut"] = (
        df_clean["Início Basculamento"].str.contains("Manual", case=False, na=False) &
        df_clean["Fim Basculamento"].str.contains("Automático", case=False, na=False)
    )
    
    total_ciclos = len(df_clean)
    taxa_perda_gps = (df_clean["Coord_00"].sum() / total_ciclos) * 100 if total_ciclos > 0 else 0
    taxa_transicao = (df_clean["Trans_Man_Aut"].sum() / total_ciclos) * 100 if total_ciclos > 0 else 0
    taxa_falso_pos = (df_clean["Dist_0"].sum() / total_ciclos) * 100 if total_ciclos > 0 else 0

    df_metricas = pd.DataFrame({
        "Indicador": [
            "Perda de GPS (Coord 0,0)",
            "Drift/Falso Positivo (Dist 0)",
            "Transição Indevida (Man->Aut)"
        ],
        "Ocorrência (%)": [taxa_perda_gps, taxa_falso_pos, taxa_transicao]
    }).sort_values(by="Ocorrência (%)", ascending=True)

    fig_anomalias = px.bar(
        df_metricas,
        y="Indicador",
        x="Ocorrência (%)",
        orientation="h",
        text="Ocorrência (%)"
    )
    fig_anomalias.update_traces(
        marker_color=COLOR_NEON_PINK,
        texttemplate="%{text:.2f}%",
        textposition="outside",
        marker_line_color="#0F172A",
        marker_line_width=1.5
    )
    apply_premium_theme(fig_anomalias, "3. Principais Anomalias e Métricas de Qualidade")
    fig_anomalias.update_layout(xaxis_ticksuffix="%", xaxis_range=[0, max(df_metricas["Ocorrência (%)"].max() + 15, 10)])
    charts.append(
        GeneratedChart(
            chart_id="fleet_anomalies_horizontal",
            title="Métricas de Inconsistências",
            chart_type="bar",
            figure=fig_anomalias
        )
    )

    # 4. BARRAS VERTICAIS - VOLUME POR CAMINHÃO (TOP 15)
    df_clean["Caminhão"] = df_clean["Caminhão"].fillna("Desconhecido")
    top_caminhoes = df_clean["Caminhão"].value_counts().head(15).reset_index()
    top_caminhoes.columns = ["Caminhão", "Quantidade de Ciclos"]

    fig_caminhoes = px.bar(
        top_caminhoes,
        x="Caminhão",
        y="Quantidade de Ciclos",
        text="Quantidade de Ciclos"
    )
    fig_caminhoes.update_traces(
        marker_color=COLOR_NEON_BLUE,
        texttemplate="%{text}",
        textposition="outside",
        marker_line_color="#0F172A",
        marker_line_width=1.5
    )
    apply_premium_theme(fig_caminhoes, "4. Volume de Ciclos Operacionais por Caminhão (Top 15)")
    fig_caminhoes.update_layout(xaxis_tickangle=-45)
    charts.append(
        GeneratedChart(
            chart_id="fleet_caminhoes_volume",
            title="Ciclos por Caminhão",
            chart_type="bar",
            figure=fig_caminhoes
        )
    )

    # 5. BARRAS HORIZONTAIS - TOP DESTINOS (TOP 10)
    df_clean["Destino"] = df_clean["Destino"].fillna("Desconhecido")
    top_destinos = df_clean["Destino"].value_counts().head(10).reset_index()
    top_destinos.columns = ["Destino", "Volume de Basculamentos"]
    top_destinos = top_destinos.sort_values("Volume de Basculamentos", ascending=True)

    fig_destinos = px.bar(
        top_destinos,
        y="Destino",
        x="Volume de Basculamentos",
        orientation="h",
        text="Volume de Basculamentos"
    )
    fig_destinos.update_traces(
        marker_color=COLOR_NEON_PURPLE,
        texttemplate="%{text}",
        textposition="outside",
        marker_line_color="#0F172A",
        marker_line_width=1.5
    )
    apply_premium_theme(fig_destinos, "5. Top 10 Destinos Mais Frequentes (Basc)")
    fig_destinos.update_layout(xaxis_range=[0, max(top_destinos["Volume de Basculamentos"].max() + 15, 10)])
    charts.append(
        GeneratedChart(
            chart_id="fleet_destinos_volume",
            title="Volume por Destino",
            chart_type="bar",
            figure=fig_destinos
        )
    )

    return charts
