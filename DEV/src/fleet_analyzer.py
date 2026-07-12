"""Fleet movement data analysis and anomaly detection module."""

from __future__ import annotations

import re
import pandas as pd

# Mandatory fleet column signatures (at least 3 must be present to detect as fleet file)
FLEET_SIGNATURES = [
    "caminhão",
    "operador",
    "destino",
    "início basculamento",
    "fim basculamento",
]


def clean_numeric_value(val) -> float:
    """Converts Brazilian decimal format and strings to clean float."""
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    
    # Standardize string format
    s = str(val).strip()
    if not s:
        return 0.0
    
    # Replace dots (thousands separators in BR) and commas (decimals)
    s = s.replace(".", "").replace(",", ".")
    s = re.sub(r"[^\d.\-]", "", s)
    try:
        return float(s) if s else 0.0
    except ValueError:
        return 0.0


def is_fleet_dataframe(df: pd.DataFrame) -> bool:
    """Smart detection if the dataframe matches fleet operational movement logs."""
    if df is None or df.empty:
        return False
    
    columns_lower = [str(col).strip().lower() for col in df.columns]
    matches = sum(1 for sig in FLEET_SIGNATURES if sig in columns_lower)
    return matches >= 3


def analyze_fleet_data(df: pd.DataFrame) -> dict | None:
    """Performs deep fleet operational analysis and anomaly tracking.
    
    Ported and enhanced from original local report scripts.
    """
    if df is None or df.empty:
        return None

    # Work on a copy to avoid mutating the original dataframe
    data = df.copy()
    
    # Standardize column casing & spacing while preserving originals
    col_mapping = {col: str(col).strip() for col in data.columns}
    data = data.rename(columns=col_mapping)
    
    if "Turma Operador" in data.columns:
        data = data.rename(columns={"Turma Operador": "Turma"})
    elif "Equipe" in data.columns:
        data = data.rename(columns={"Equipe": "Turma"})
    
    # Ensure text columns are clean and stripped
    text_cols = [
        "Início Carga", "Fim Carga", "Início Basculamento", "Fim Basculamento",
        "Operador", "Caminhão", "Turma", "Origem", "Destino", "Material", "Equipamento de Carga"
    ]
    for col in text_cols:
        if col in data.columns:
            data[col] = data[col].astype(str).str.strip()
        else:
            data[col] = "Desconhecido"

    # Fill defaults for text columns
    data["Origem"] = data["Origem"].replace({"nan": "Desconhecido", "None": "Desconhecido", "": "Desconhecido"})
    data["Destino"] = data["Destino"].replace({"nan": "Desconhecido", "None": "Desconhecido", "": "Desconhecido"})
    data["Material"] = data["Material"].replace({"nan": "Desconhecido", "None": "Desconhecido", "": "Desconhecido"})

    # Ensure numeric columns are cleaned
    num_cols = [
        "Distância Cheio (m)", "Tempo Basculamento (min)", "Tempo de Ciclo (min)",
        "Latitude (Basculamento)", "Longitude (Basculamento)", "Tempo Carregamento (min)", "Massa (tons)"
    ]
    for col in num_cols:
        if col in data.columns:
            data[col] = data[col].apply(clean_numeric_value)
        else:
            data[col] = 0.0

    # 1. Anomaly Flags Detection
    data["Erro_Coord_00"] = (data["Latitude (Basculamento)"] == 0.0) & (data["Longitude (Basculamento)"] == 0.0)
    data["Erro_Dist_0"] = data["Distância Cheio (m)"] == 0.0
    data["Erro_Origem_Destino"] = data["Origem"] == data["Destino"]
    data["Erro_Tempo_Basc_Alto"] = data["Tempo Basculamento (min)"] > 15.0
    data["Erro_Ciclo_Curto"] = data["Tempo de Ciclo (min)"] < 2.0
    data["Erro_Ciclo_Longo"] = data["Tempo de Ciclo (min)"] > 120.0
    
    # Manual to Auto transition logic
    data["Erro_Trans_Manual_Auto"] = (
        data["Início Basculamento"].str.contains("Manual", case=False, na=False) &
        data["Fim Basculamento"].str.contains("Automático", case=False, na=False)
    )
    
    # Master error column
    data["Tem_Erro"] = data[
        ["Erro_Coord_00", "Erro_Dist_0", "Erro_Origem_Destino", 
         "Erro_Tempo_Basc_Alto", "Erro_Ciclo_Curto", "Erro_Ciclo_Longo", 
         "Erro_Trans_Manual_Auto"]
    ].any(axis=1)

    # 2. Cycle Automation Classification
    data["Ciclo_100_Auto"] = (
        data["Início Carga"].str.contains("Automático", case=False, na=False) &
        data["Fim Carga"].str.contains("Automático", case=False, na=False) &
        data["Início Basculamento"].str.contains("Automático", case=False, na=False) &
        data["Fim Basculamento"].str.contains("Automático", case=False, na=False)
    )

    data["Ciclo_100_Manual"] = (
        data["Início Carga"].str.contains("Manual", case=False, na=False) &
        data["Fim Carga"].str.contains("Manual", case=False, na=False) &
        data["Início Basculamento"].str.contains("Manual", case=False, na=False) &
        data["Fim Basculamento"].str.contains("Manual", case=False, na=False)
    )

    data["Ciclo_Misto"] = ~data["Ciclo_100_Auto"] & ~data["Ciclo_100_Manual"]

    # Falsos Positivos
    data["Falso_Positivo"] = data["Erro_Dist_0"] & (data["Tempo de Ciclo (min)"] > 5)

    # 3. Overall Statistics
    total_cycles = len(data)
    ok_cycles = len(data[~data["Tem_Erro"]])
    error_cycles = len(data[data["Tem_Erro"]])
    
    # Destination filters
    cava_sul_cycles = int(data["Destino"].str.contains("CAVA SUL", case=False, na=False).sum())

    # Rates
    perc_falhas = (error_cycles / total_cycles * 100) if total_cycles > 0 else 0.0
    reliability_rate = 100.0 - perc_falhas
    false_pos_rate = (data["Falso_Positivo"].sum() / total_cycles * 100) if total_cycles > 0 else 0.0
    gps_loss_rate = (data["Erro_Coord_00"].sum() / total_cycles * 100) if total_cycles > 0 else 0.0
    manual_to_auto_rate = (data["Erro_Trans_Manual_Auto"].sum() / total_cycles * 100) if total_cycles > 0 else 0.0

    # Etapas Status Counts
    etapas = ["Início Carga", "Fim Carga", "Início Basculamento", "Fim Basculamento"]
    etapas_stats = {}
    for etapa in etapas:
        if etapa in data.columns:
            counts = data[etapa].value_counts()
            total_etapa = counts.sum()
            etapas_stats[etapa] = {
                status: {
                    "count": int(count),
                    "percentage": float((count / total_etapa) * 100) if total_etapa > 0 else 0.0
                }
                for status, count in counts.items()
            }

    # 4. Operator Rankings
    top_auto_df = (
        data[data["Fim Basculamento"] == "Automático"]
        .groupby(["Operador", "Caminhão", "Turma"])
        .size()
        .sort_values(ascending=False)
        .head(10)
    )
    top_auto = [
        {"operator": op, "truck": cam, "turma": turma, "cycles": int(val)}
        for (op, cam, turma), val in top_auto_df.items()
    ]

    top_manual_df = (
        data[data["Fim Basculamento"] == "Manual"]
        .groupby(["Operador", "Caminhão", "Turma"])
        .size()
        .sort_values(ascending=False)
        .head(10)
    )
    top_manual = [
        {"operator": op, "truck": cam, "turma": turma, "cycles": int(val)}
        for (op, cam, turma), val in top_manual_df.items()
    ]

    # 5. Critical & High Severities Details
    def classify_severity(row):
        score = sum([
            row["Erro_Coord_00"],
            row["Erro_Dist_0"],
            row["Erro_Origem_Destino"],
            row["Erro_Tempo_Basc_Alto"]
        ])
        if score >= 3 or row["Erro_Tempo_Basc_Alto"]:
            return "CRÍTICA"
        if score == 2:
            return "ALTA"
        if score == 1:
            return "MÉDIA"
        return "BAIXA"

    def define_hypothesis(row):
        h = []
        if row["Erro_Coord_00"]:
            h.append("Perda de pacote GPS ou Área de Sombra")
        if row["Erro_Tempo_Basc_Alto"]:
            h.append("Esquecimento de apontamento / Falha de fechamento")
        if row["Erro_Origem_Destino"]:
            h.append("Geofence incorreta (Basculou na Carga)")
        if row["Erro_Dist_0"]:
            h.append("Drift GPS / Odômetro inativo")
        if row["Erro_Trans_Manual_Auto"]:
            h.append("Intervenção manual indevida")
        return " | ".join(h) if h else "Anomalia FMS"

    # Process events
    data_errors = data[data["Tem_Erro"]].copy()
    
    if not data_errors.empty:
        data_errors["Severidade"] = data_errors.apply(classify_severity, axis=1)
        data_errors["Hipotese"] = data_errors.apply(define_hypothesis, axis=1)
        
        # Get priority anomalies (ALTA and CRÍTICA)
        eventos_prioritarios = (
            data_errors[data_errors["Severidade"].isin(["ALTA", "CRÍTICA"])]
            .sort_values(by="Severidade", ascending=False)
        )
        
        # Find map link column (starts with http)
        map_col = None
        for col in data.columns:
            # Check a few samples
            non_null = data[col].dropna().head(10)
            if not non_null.empty and any(str(x).startswith("http") for x in non_null):
                map_col = col
                break

        anomalous_events = []
        for _, row in eventos_prioritarios.iterrows():
            gps_link = str(row[map_col]) if map_col and pd.notna(row[map_col]) else "Link indisponível"
            anomalous_events.append({
                "severity": row["Severidade"],
                "truck": row["Caminhão"],
                "operator": row["Operador"],
                "hypothesis": row["Hipotese"],
                "origin": row["Origem"],
                "destination": row["Destino"],
                "time_basculamento": float(row["Tempo Basculamento (min)"]),
                "distance": float(row["Distância Cheio (m)"]),
                "latitude": float(row["Latitude (Basculamento)"]),
                "longitude": float(row["Longitude (Basculamento)"]),
                "gps_link": gps_link,
                "date": str(row.get("Data Início", row.get("Data", ""))),
                "time_start": str(row.get("Hora Início", row.get("Hora", "")))
            })
    else:
        anomalous_events = []

    # Compile the final statistics dictionary
    return {
        "summary": {
            "total_cycles": total_cycles,
            "ok_cycles": ok_cycles,
            "error_cycles": error_cycles,
            "cava_sul_cycles": cava_sul_cycles,
            "auto_100_percent": int(data["Ciclo_100_Auto"].sum()),
            "manual_100_percent": int(data["Ciclo_100_Manual"].sum()),
            "mixed_cycles": int(data["Ciclo_Misto"].sum()),
            "reliability_rate": reliability_rate,
            "inconsistency_rate": perc_falhas,
            "false_positive_rate": false_pos_rate,
            "gps_loss_rate": gps_loss_rate,
            "manual_to_auto_rate": manual_to_auto_rate,
        },
        "etapas_stats": etapas_stats,
        "operators_ranking": {
            "top_auto": top_auto,
            "top_manual": top_manual
        },
        "anomaly_counts": {
            "dist_zero": int(data["Erro_Dist_0"].sum()),
            "origin_equals_destination": int(data["Erro_Origem_Destino"].sum()),
            "gps_coords_zero": int(data["Erro_Coord_00"].sum()),
            "high_basculamento_time": int(data["Erro_Tempo_Basc_Alto"].sum()),
            "manual_to_auto_transition": int(data["Erro_Trans_Manual_Auto"].sum())
        },
        "anomalous_events": anomalous_events,
        # Export processed dataframe for charting
        "processed_df": data
    }
