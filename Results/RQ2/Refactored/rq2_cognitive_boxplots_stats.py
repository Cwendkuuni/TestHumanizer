#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RQ2 - Cognitive Complexity (GPT refactored) boxplots + stats CSVs

Input:
  - cognitive_analysis_detailed_GPT.csv

Outputs:
  - rq2_cognitive_outputs/rq2_cognitive_long_format.csv
  - rq2_cognitive_outputs/rq2_cognitive_stats_min_q1_mean_q3_max.csv
  - rq2_cognitive_outputs/boxplot_defects4j_Cognitive_Complexity.pdf/.png
  - rq2_cognitive_outputs/boxplot_sf110_Cognitive_Complexity.pdf/.png

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
BASE_DIR = Path("/home/e113/Documents/Humanization-Project/HUMANIZATION/NEW-EXPERIMENTS-OUTPUTS/LLM-REFACTORED/RQ2")
INPUT_CSV = BASE_DIR / "cognitive_analysis_detailed_GPT.csv"

OUTDIR = Path("rq2_cognitive_outputs")
OUTDIR.mkdir(exist_ok=True)

SCENARIO_ORDER = ["Scenario-1", "Scenario-2", "Scenario-3"]
SCENARIO_LABELS = {
    "Scenario-1": "Tests-only",
    "Scenario-2": "Code-centric",
    "Scenario-3": "Summary-based",
}

COLOR_MAP = {
    "Scenario-1": "#2ca02c",
    "Scenario-2": "#ff7f0e",
    "Scenario-3": "#d62728",
}

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
    # Normalize columns
    df = df.rename(columns={
        "Dataset": "dataset",
        "Scenario": "scenario",
        "Cognitive Complexity": "value",
    })

    # Keep only needed
    df = df[["dataset", "scenario", "value"]].copy()

    # Normalize dataset names (optional)
    df["dataset"] = df["dataset"].str.strip().str.lower()

    # Ensure scenario format is Scenario-*
    df["scenario"] = df["scenario"].str.strip()

    # Drop NaNs
    df = df.dropna(subset=["value"])

    # Cast numeric
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])

    # Add pretty label (for plots)
    df["approach"] = df["scenario"].map(SCENARIO_LABELS)

    df["metric"] = "Cognitive Complexity"
    return df


def compute_stats(df_long: pd.DataFrame) -> pd.DataFrame:
    def q1(x): return float(np.percentile(x, 25))
    def q3(x): return float(np.percentile(x, 75))

    stats = (
        df_long
        .groupby(["dataset", "scenario", "approach"])["value"]
        .agg(min="min", q1=q1, mean="mean", q3=q3, max="max", n="count")
        .reset_index()
    )

    for c in ["min", "q1", "mean", "q3", "max"]:
        stats[c] = stats[c].round(2)

    stats["scenario"] = pd.Categorical(stats["scenario"], categories=SCENARIO_ORDER, ordered=True)
    stats = stats.sort_values(["dataset", "scenario"]).reset_index(drop=True)
    return stats


def save_boxplot(df_long: pd.DataFrame, dataset: str):
    dfp = df_long[df_long["dataset"] == dataset].copy()
    dfp["scenario"] = pd.Categorical(dfp["scenario"], categories=SCENARIO_ORDER, ordered=True)

    fig = px.box(
        dfp,
        x="approach",
        y="value",
        color="scenario",
        color_discrete_map=COLOR_MAP,
        points="outliers",
        title=""
    )

    fig.update_traces(boxmean=True)

    fig.update_layout(
        width=FIG_WIDTH,
        height=FIG_HEIGHT,
        font=dict(size=FONT_SIZE),
        xaxis_title="Approach",
        yaxis_title="Cognitive Complexity",
        margin=dict(t=30, b=170, l=160, r=60),
        showlegend=False
    )

    fig.update_xaxes(
        tickfont=dict(size=AXIS_TICK_SIZE),
        tickangle=-15,
        title=dict(font=dict(size=FONT_SIZE))
    )

    fig.update_yaxes(
        tickfont=dict(size=AXIS_TICK_SIZE),
        title=dict(font=dict(size=FONT_SIZE)),
        rangemode="tozero"
    )

    safe_ds = dataset.lower()
    pdf_path = OUTDIR / f"boxplot_{safe_ds}_Cognitive_Complexity.pdf"
    png_path = OUTDIR / f"boxplot_{safe_ds}_Cognitive_Complexity.png"

    fig.write_image(str(pdf_path), format="pdf", scale=EXPORT_SCALE_PDF)
    fig.write_image(str(png_path), format="png", scale=EXPORT_SCALE_PNG)

    print(f"📦 Saved: {pdf_path}")
    print(f"🖼️  Saved: {png_path}")


def main():
    print("📥 Loading:", INPUT_CSV)
    df = pd.read_csv(INPUT_CSV)

    df_long = to_long(df)

    # Save intermediate file
    long_path = OUTDIR / "rq2_cognitive_long_format.csv"
    df_long.to_csv(long_path, index=False)
    print("✅ Long format saved:", long_path)

    # Stats
    stats = compute_stats(df_long)
    stats_path = OUTDIR / "rq2_cognitive_stats_min_q1_mean_q3_max.csv"
    stats.to_csv(stats_path, index=False)
    print("✅ Stats saved:", stats_path)

    # Boxplots
    for dataset in sorted(df_long["dataset"].unique()):
        save_boxplot(df_long, dataset)

    print("\n✅ Done. Outputs in:", OUTDIR.resolve())


if __name__ == "__main__":
    main()
