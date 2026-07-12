"""Carregamento genérico de planilhas (CSV, Excel)."""

from __future__ import annotations

import io
import re
from typing import BinaryIO

import pandas as pd


def _detect_skiprows(content: str) -> int:
    first = content.split("\n", 1)[0] if content else ""
    if ";;" in first or "Período" in first or first.strip().startswith(";"):
        return 1
    return 0


def _guess_sep(sample: str) -> str:
    if sample.count(";") > sample.count(","):
        return ";"
    return ","


def load_from_path(file_path: str) -> pd.DataFrame:
    """Carrega arquivo por caminho local."""
    lower = file_path.lower()
    if lower.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file_path)
        offset = 0
        for idx in range(min(5, len(df))):
            row_vals = [str(val).strip().lower() for val in df.iloc[idx].values if pd.notna(val)]
            matches = sum(1 for sig in ["caminhão", "operador", "destino", "basculamento"] if any(sig in v for v in row_vals))
            if matches >= 2:
                offset = idx + 1
                break
        if offset > 0:
            df = pd.read_excel(file_path, skiprows=offset)
        df.columns = [str(c).strip() for c in df.columns]
        df = df.dropna(how="all")
        return df
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read(8192)
    skip = _detect_skiprows(content)
    sep = _guess_sep(content)
    return pd.read_csv(file_path, sep=sep, skiprows=skip, encoding="utf-8", low_memory=False)


def load_from_upload(uploaded_file: BinaryIO, filename: str) -> pd.DataFrame:
    """Carrega arquivo enviado via Streamlit."""
    name = (filename or "").lower()
    raw = uploaded_file.read()
    uploaded_file.seek(0)

    if name.endswith((".xlsx", ".xls")):
        # Load excel data
        excel_bytes = io.BytesIO(raw)
        df = pd.read_excel(excel_bytes)
        
        # Smart header offset detection (if metadata rows are present at the top)
        offset = 0
        for idx in range(min(5, len(df))):
            row_vals = [str(val).strip().lower() for val in df.iloc[idx].values if pd.notna(val)]
            matches = sum(1 for sig in ["caminhão", "operador", "destino", "basculamento"] if any(sig in v for v in row_vals))
            if matches >= 2:
                offset = idx + 1
                break
        
        if offset > 0:
            df = pd.read_excel(io.BytesIO(raw), skiprows=offset)
            
        df.columns = [str(c).strip() for c in df.columns]
        df = df.dropna(how="all")
        return df

    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = raw.decode("utf-8", errors="replace")

    skip = _detect_skiprows(text)
    sep = _guess_sep(text[:4096])
    return pd.read_csv(io.StringIO(text), sep=sep, skiprows=skip, low_memory=False)


def clean_numeric_br(val) -> float:
    """Converte números no padrão brasileiro para float."""
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if not s:
        return 0.0
    s = s.replace(".", "").replace(",", ".")
    s = re.sub(r"[^\d.\-]", "", s)
    try:
        return float(s) if s else 0.0
    except ValueError:
        return 0.0
