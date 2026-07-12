"""Limpeza e inferência de tipos de colunas."""

from __future__ import annotations

import pandas as pd

from .data_loader import clean_numeric_br


DATE_PATTERNS = (
    "data",
    "date",
    "dia",
    "hora",
    "time",
    "timestamp",
    "início",
    "inicio",
    "fim",
    "periodo",
    "período",
)


def _looks_like_date_column(name: str) -> bool:
    n = name.lower()
    return any(p in n for p in DATE_PATTERNS)


def _try_parse_datetime(series: pd.Series) -> pd.Series | None:
    if pd.api.types.is_datetime64_any_dtype(series):
        return series
    parsed = pd.to_datetime(series, dayfirst=True, errors="coerce")
    if parsed.notna().mean() >= 0.5:
        return parsed
    return None


def _try_parse_numeric(series: pd.Series) -> pd.Series | None:
    if pd.api.types.is_numeric_dtype(series):
        return series
    sample = series.dropna().head(200)
    if sample.empty:
        return None
    converted = sample.apply(clean_numeric_br)
    if (converted != 0).sum() >= max(1, len(sample) * 0.1):
        return series.apply(clean_numeric_br)
    return None


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Limpa strings, infere tipos e preenche nulos básicos."""
    out = df.copy()
    out.columns = [str(c).strip() for c in out.columns]

    for col in out.columns:
        if out[col].dtype == object:
            out[col] = out[col].astype(str).str.strip()
            out[col] = out[col].replace({"nan": pd.NA, "None": pd.NA, "": pd.NA})

        if _looks_like_date_column(col):
            dt = _try_parse_datetime(out[col])
            if dt is not None:
                out[col] = dt
                continue

        if out[col].dtype == object:
            num = _try_parse_numeric(out[col])
            if num is not None:
                out[col] = num

    for col in out.select_dtypes(include="object").columns:
        out[col] = out[col].fillna("Não informado")

    return out
