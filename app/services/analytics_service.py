import io
import json
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional


def analyze_csv_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """Generates deep statistical profiling and Chart.js datasets from a Pandas DataFrame."""
    row_count, col_count = df.shape
    missing_cells = int(df.isna().sum().sum())
    missing_pct = round((missing_cells / (row_count * col_count) * 100), 2) if row_count * col_count > 0 else 0
    duplicate_rows = int(df.duplicated().sum())

    columns_info = []
    numeric_stats = {}
    chart_data = {}

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

    for col in df.columns:
        col_type = "numeric" if col in numeric_cols else "categorical"
        null_count = int(df[col].isna().sum())
        unique_count = int(df[col].nunique())

        columns_info.append({
            "name": col,
            "type": col_type,
            "null_count": null_count,
            "unique_count": unique_count,
        })

    # Numeric summary statistics
    for col in numeric_cols:
        series = df[col].dropna()
        if not series.empty:
            numeric_stats[col] = {
                "mean": round(float(series.mean()), 2),
                "median": round(float(series.median()), 2),
                "std": round(float(series.std()), 2) if len(series) > 1 else 0.0,
                "min": round(float(series.min()), 2),
                "max": round(float(series.max()), 2),
                "sum": round(float(series.sum()), 2),
            }

            # Generate histogram bins for Chart.js
            counts, bin_edges = np.histogram(series, bins=min(10, max(3, series.nunique())))
            chart_data[f"hist_{col}"] = {
                "labels": [f"{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}" for i in range(len(counts))],
                "values": [int(c) for c in counts],
            }

    # Categorical top values
    for col in categorical_cols[:5]:
        val_counts = df[col].value_counts().head(8)
        chart_data[f"cat_{col}"] = {
            "labels": [str(idx) for idx in val_counts.index],
            "values": [int(v) for v in val_counts.values],
        }

    # Correlation matrix for numeric columns
    correlation_matrix = {}
    if len(numeric_cols) >= 2:
        corr_df = df[numeric_cols].corr().fillna(0)
        correlation_matrix = {
            "columns": numeric_cols,
            "values": [[round(float(val), 2) for val in row] for row in corr_df.values],
        }

    # Preview top 15 rows
    sample_rows = df.head(15).fillna("").to_dict(orient="records")

    return {
        "overview": {
            "row_count": row_count,
            "col_count": col_count,
            "missing_cells": missing_cells,
            "missing_pct": missing_pct,
            "duplicate_rows": duplicate_rows,
            "numeric_cols_count": len(numeric_cols),
            "categorical_cols_count": len(categorical_cols),
        },
        "columns": columns_info,
        "numeric_stats": numeric_stats,
        "correlation_matrix": correlation_matrix,
        "charts": chart_data,
        "preview_data": sample_rows,
    }


def parse_csv_bytes(file_bytes: bytes, filename: str = "dataset.csv") -> Dict[str, Any]:
    """Loads CSV/TSV from raw bytes into Pandas and profiles it."""
    try:
        # Try UTF-8 first, fallback to Latin-1
        try:
            df = pd.read_csv(io.BytesIO(file_bytes))
        except UnicodeDecodeError:
            df = pd.read_csv(io.BytesIO(file_bytes), encoding="latin-1")

        return analyze_csv_dataframe(df)
    except Exception as e:
        raise ValueError(f"Failed to parse CSV file: {str(e)}")
