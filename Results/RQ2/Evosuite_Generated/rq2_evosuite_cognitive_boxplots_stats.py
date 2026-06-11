#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RQ2 - EvoSuite Cognitive Complexity boxplots + stats CSVs

Input:
  - evosuite_cognitive_analysis_detailed-TestAware.csv

Outputs:
  - rq2_evosuite_cognitive_outputs/evosuite_cognitive_long_format.csv
  - rq2_evosuite_cognitive_outputs/evosuite_cognitive_stats_min_q1_mean_q3_max.csv
  - rq2_evosuite_cognitive_outputs/boxplot_defects4j_EvoSuite_Cognitive_Complexity.pdf/.png
  - rq2_evosuite_cognitive_outputs/boxplot_sf110_EvoSuite_Cognitive_Complexity.pdf/.png

Requirements:
  pip install pandas numpy plotly kaleido
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio
from pathlib import Path

pio.defaults.mathjax = None

# =========================
# CONFIG
# =========================
BASE_DIR = Path("/home/e113/Documents/Humanization-Project/HUMANIZATION/NEW-EXPERIMENTS-OUTPUTS/EVOSUITE/RQ2")
INPUT_CSV = BASE_DIR / "evosuite_cognitive_analysis_detailed-TestAware.csv"

OUTDIR = Path("rq2_evosuite_cognitive_outputs")
OUTDIR.mkdir(exist_ok=True)

PARADIGM_LABEL = "EvoSuite"

FIG_WIDTH = 1600
FIG_HEIGHT = 900
FONT_SIZE = 60
AXIS_TICK_SIZE = 52
EXPORT_SCALE_PDF = 10
EXPORT_SCALE_PNG = 8

# =========================
# HELPERS
# =========================
def to_long(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={
        "Dataset": "dataset",
        "Cognitive Complexity": "value",
    })

    df = df[["dataset", "value"]].copy()
    df["dataset"] = df["dataset"].astype(str).str.strip().str.lower()

    # Normalize dataset naming
    df["dataset"] = df["dataset"].replace({
        "defects4j": "defects4j",
        "sf110": "sf110",
        "sf-110": "sf110",
    })

    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])

    df["paradigm"] = PARADIGM_LABEL
    df["metric"] = "Cognitive Complexity"
    return df


def compute_stats(df_long: pd.DataFrame) -> pd.DataFrame:
    def q1(x): return float(np.percentile(x, 25))
    def q3(x): return float(np.percentile(x, 75))

    stats = (
        df_long
        .groupby(["dataset", "paradigm", "metric"])["value"]
        .agg(min="min", q1=q1, mean="mean", q3=q3, max="max", n="count")
        .reset_index()
    )

    for c in ["min", "q1", "mean", "q3", "max"]:
        stats[c] = stats[c].round(2)

    stats = stats.sort_values(["dataset"]).reset_index(drop=True)
    return stats


def save_boxplot(df_long: pd.DataFrame, dataset: str):
    dfp = df_long[df_long["dataset"] == dataset].copy()

    fig = px.box(
        dfp,
        x="paradigm",
        y="value",
        points="outliers",
        title=""
    )
    fig.update_traces(boxmean=True)

    fig.update_layout(
        width=FIG_WIDTH,
        height=FIG_HEIGHT,
        font=dict(size=FONT_SIZE),
        xaxis_title="Paradigm",
        yaxis_title="Cognitive Complexity",
        margin=dict(t=30, b=170, l=160, r=60),
        showlegend=False
    )

    fig.update_xaxes(
        tickfont=dict(size=AXIS_TICK_SIZE),
        tickangle=0,
        title=dict(font=dict(size=FONT_SIZE))
    )
    fig.update_yaxes(
        tickfont=dict(size=AXIS_TICK_SIZE),
        title=dict(font=dict(size=FONT_SIZE)),
        rangemode="tozero"
    )

    pdf_path = OUTDIR / f"boxplot_{dataset}_{PARADIGM_LABEL}_Cognitive_Complexity.pdf"
    png_path = OUTDIR / f"boxplot_{dataset}_{PARADIGM_LABEL}_Cognitive_Complexity.png"

    fig.write_image(str(pdf_path), format="pdf", scale=EXPORT_SCALE_PDF)
    fig.write_image(str(png_path), format="png", scale=EXPORT_SCALE_PNG)

    print(f"📦 Saved: {pdf_path}")
    print(f"🖼️  Saved: {png_path}")


def main():
    print("📥 Loading:", INPUT_CSV)
    df = pd.read_csv(INPUT_CSV)

    df_long = to_long(df)

    long_path = OUTDIR / "evosuite_cognitive_long_format.csv"
    df_long.to_csv(long_path, index=False)
    print("✅ Long format saved:", long_path)

    stats = compute_stats(df_long)
    stats_path = OUTDIR / "evosuite_cognitive_stats_min_q1_mean_q3_max.csv"
    stats.to_csv(stats_path, index=False)
    print("✅ Stats saved:", stats_path)

    for dataset in sorted(df_long["dataset"].unique()):
        save_boxplot(df_long, dataset)

    print("\n✅ Done. Outputs in:", OUTDIR.resolve())


if __name__ == "__main__":
    main()
