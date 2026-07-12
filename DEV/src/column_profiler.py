"""Classificação automática de colunas para escolha de gráficos."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


MAX_PIE_CATEGORIES = 8
MAX_BAR_CATEGORIES = 40
MIN_ROWS_FOR_CHART = 3


@dataclass
class ColumnProfile:
    name: str
    kind: str  # datetime | numeric | categorical | id_text
    unique_count: int
    null_ratio: float


@dataclass
class DatasetProfile:
    datetime_cols: list[str]
    numeric_cols: list[str]
    categorical_cols: list[str]
    columns: list[ColumnProfile]


def _classify_column(name: str, series: pd.Series) -> ColumnProfile:
    null_ratio = float(series.isna().mean())
    nunique = int(series.nunique(dropna=True))

    if pd.api.types.is_datetime64_any_dtype(series):
        return ColumnProfile(name, "datetime", nunique, null_ratio)

    if pd.api.types.is_numeric_dtype(series):
        return ColumnProfile(name, "numeric", nunique, null_ratio)

    if nunique > max(50, len(series) * 0.9):
        return ColumnProfile(name, "id_text", nunique, null_ratio)

    return ColumnProfile(name, "categorical", nunique, null_ratio)


def profile_dataframe(df: pd.DataFrame) -> DatasetProfile:
    """Analisa dtypes e cardinalidade de cada coluna."""
    columns = [_classify_column(c, df[c]) for c in df.columns]
    return DatasetProfile(
        datetime_cols=[c.name for c in columns if c.kind == "datetime"],
        numeric_cols=[c.name for c in columns if c.kind == "numeric"],
        categorical_cols=[
            c.name
            for c in columns
            if c.kind == "categorical" and c.unique_count <= MAX_BAR_CATEGORIES
        ],
        columns=columns,
    )


def pie_eligible_categories(df: pd.DataFrame, col: str) -> bool:
    n = df[col].nunique(dropna=True)
    return 2 <= n <= MAX_PIE_CATEGORIES
