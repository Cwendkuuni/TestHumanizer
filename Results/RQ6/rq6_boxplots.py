#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RQ6 - Boxplots (Plotly) + stats CSVs

On part de rq6_ratings_long.csv (généré par le script d'analyse RQ6) et on produit :

- Des boxplots HD (PDF + PNG) comparant EvoSuite vs TestHumanizer (Summary-based)
  pour 3 métriques :
    * readability
    * trust
    * adopt

- Deux variantes de boxplots :
    1) Global (tous les évaluateurs)
    2) Par rôle (Senior developer vs Advanced graduate student), en facets

- Un CSV de stats globales par approche × métrique :
    min, q1, median, mean, q3, max, N

Dépendances:
    pip install pandas numpy plotly kaleido
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio
from pathlib import Path

# Désactiver MathJax pour l’export Kaleido (plus stable)
pio.defaults.mathjax = None

# =========================
# CONFIG
# =========================

BASE_DIR = Path(
    "/home/e113/Documents/Humanization-Project/HUMANIZATION/NEW-EXPERIMENTS-OUTPUTS/HUMAN-EVAL"
)

INPUT_LONG = BASE_DIR / "rq6_ratings_long.csv"
OUTDIR     = BASE_DIR / "rq6_boxplots"
OUTDIR.mkdir(exist_ok=True)

METRICS = {
    "readability": "Readability / clarity of intent",
    "trust":       "Trust in correctness",
    "adopt":       "Willingness to adopt",
}

# Ordre + labels d’approche
APPROACH_ORDER = ["EvoSuite", "Summary"]
APPROACH_LABEL = {
    "EvoSuite": "EvoSuite",
    "Summary": "TestHumanizer",
}

# Couleurs fixes
COLOR_MAP = {
    "EvoSuite":      "#000000",  # noir
    "TestHumanizer": "#d62728",  # rouge
}

# Paramètres HD (à adapter si tu veux)
FIG_WIDTH       = 1600
FIG_HEIGHT      = 900#900
FONT_SIZE       = 40#33#42
AXIS_TICK_SIZE  = 48#32
TITLE_SIZE      = 48

EXPORT_SCALE_PDF = 10#10  # PDF HD
EXPORT_SCALE_PNG = 8   # PNG HD


# =========================
# HELPERS
# =========================

def describe_series(s: pd.Series):
    """Retourne N, min, Q1, median, mean, Q3, max pour une série numérique."""
    s = s.dropna()
    if s.empty:
        return {
            "N": 0,
            "min": np.nan,
            "q1": np.nan,
            "median": np.nan,
            "mean": np.nan,
            "q3": np.nan,
            "max": np.nan,
        }
    return {
        "N": int(s.count()),
        "min": float(s.min()),
        "q1": float(s.quantile(0.25)),
        "median": float(s.median()),
        "mean": float(s.mean()),
        "q3": float(s.quantile(0.75)),
        "max": float(s.max()),
    }


def prepare_long_df(path: Path) -> pd.DataFrame:
    """Charge rq6_ratings_long.csv et prépare les colonnes pour les plots."""
    df = pd.read_csv(path)

    # Normaliser l’étiquette d’approche pour l’affichage (TestHumanizer)
    df["approach"] = df["approach"].replace({"Summary": "TestHumanizer"})
    df["approach"] = pd.Categorical(
        df["approach"],
        categories=["EvoSuite", "TestHumanizer"],
        ordered=True,
    )

    # Petite normalisation éventuelle des noms d’évaluateurs
    # (au cas où il y aurait des variations de casse/espaces)
    df["evaluator"] = df["evaluator"].str.strip()

    return df


def compute_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Stats globales par approche × métrique."""
    records = []

    # On "melt" pour avoir colonne 'metric' / 'score'
    melted = df.melt(
        id_vars=["approach"],
        value_vars=list(METRICS.keys()),
        var_name="metric",
        value_name="score",
    )

    for (approach, metric), sub in melted.groupby(["approach", "metric"]):
        stats = describe_series(sub["score"])
        rec = {"approach": approach, "metric": metric}
        rec.update(stats)
        records.append(rec)

    stats_df = pd.DataFrame(records)
    stats_df["metric_label"] = stats_df["metric"].map(METRICS)
    stats_df = stats_df[[
        "metric", "metric_label", "approach",
        "N", "min", "q1", "median", "mean", "q3", "max"
    ]]

    # tri joli
    stats_df["approach"] = pd.Categorical(
        stats_df["approach"],
        categories=["EvoSuite", "TestHumanizer"],
        ordered=True,
    )
    stats_df = stats_df.sort_values(["metric", "approach"]).reset_index(drop=True)

    return stats_df


def save_boxplot_overall(df: pd.DataFrame, metric: str):
    """
    Boxplot global (tous évaluateurs) pour une métrique.
    x = approach, y = score.
    """
    label_y = METRICS[metric]

    fig = px.box(
        df,
        x="approach",
        y=metric,
        color="approach",
        category_orders={"approach": ["EvoSuite", "TestHumanizer"]},
        color_discrete_map=COLOR_MAP,
        points="outliers",
        title="",
    )

    fig.update_traces(boxmean=True)

    fig.update_layout(
        width=FIG_WIDTH,
        height=FIG_HEIGHT,
        font=dict(size=FONT_SIZE),
        xaxis_title="Approach",
        yaxis_title=label_y,
        margin=dict(t=30, b=140, l=140, r=60),
        showlegend=False,
    )

    fig.update_xaxes(
        tickfont=dict(size=AXIS_TICK_SIZE),
        tickangle=0,
        title=dict(font=dict(size=FONT_SIZE)),
    )

    fig.update_yaxes(
        tickfont=dict(size=AXIS_TICK_SIZE),
        title=dict(font=dict(size=FONT_SIZE)),
        range=[1, 5],  # Likert 1–5
        dtick=1,
    )

    pdf_path = OUTDIR / f"rq6_boxplot_overall_{metric}.pdf"
    png_path = OUTDIR / f"rq6_boxplot_overall_{metric}.png"

    fig.write_image(str(pdf_path), format="pdf", scale=EXPORT_SCALE_PDF)
    fig.write_image(str(png_path), format="png", scale=EXPORT_SCALE_PNG)

    print(f"✅ Saved overall plot: {pdf_path}")
    print(f"✅ Saved overall plot: {png_path}")


def save_boxplot_by_role(df: pd.DataFrame, metric: str):
    """
    Boxplot par rôle (Senior vs Grad) pour une métrique.
    On utilise facet_col = evaluator.
    """
    label_y = METRICS[metric]

    fig = px.box(
        df,
        x="approach",
        y=metric,
        color="approach",
        facet_col="evaluator",
        category_orders={"approach": ["EvoSuite", "TestHumanizer"]},
        color_discrete_map=COLOR_MAP,
        points="outliers",
        title="",
    )

    fig.update_traces(boxmean=True)

    fig.update_layout(
        width=FIG_WIDTH * 1.4,
        height=FIG_HEIGHT,
        font=dict(size=FONT_SIZE),
        xaxis_title="Approach",
        yaxis_title=label_y,
        margin=dict(t=30, b=140, l=140, r=60),
        showlegend=False,
    )

    fig.update_xaxes(
        tickfont=dict(size=AXIS_TICK_SIZE),
        tickangle=0,
        title=dict(font=dict(size=FONT_SIZE)),
    )
    fig.update_yaxes(
        tickfont=dict(size=AXIS_TICK_SIZE),
        title=dict(font=dict(size=FONT_SIZE)),
        range=[1, 5],
        dtick=1,
    )

    # 🔥 Ici on nettoie les titres de facette : "evaluator=Senior developer"
    # -> "Senior developer"
    for ann in fig.layout.annotations:
        if isinstance(ann.text, str) and ann.text.startswith("evaluator="):
            ann.text = ann.text.split("=", 1)[1]

    pdf_path = OUTDIR / f"rq6_boxplot_by_role_{metric}.pdf"
    png_path = OUTDIR / f"rq6_boxplot_by_role_{metric}.png"

    fig.write_image(str(pdf_path), format="pdf", scale=EXPORT_SCALE_PDF)
    fig.write_image(str(png_path), format="png", scale=EXPORT_SCALE_PNG)

    print(f"✅ Saved by-role plot: {pdf_path}")
    print(f"✅ Saved by-role plot: {png_path}")


# =========================
# MAIN
# =========================

def main():
    # Charger et préparer le long DF
    df = prepare_long_df(INPUT_LONG)

    # Stats globales (approach × métrique)
    stats_df = compute_stats(df)
    stats_path = OUTDIR / "rq6_boxplot_stats_overall.csv"
    stats_df.to_csv(stats_path, index=False)
    print(f"📊 Stats CSV written to: {stats_path}")

    # Générer les boxplots pour chaque métrique
    for metric in METRICS.keys():
        save_boxplot_overall(df, metric)
        save_boxplot_by_role(df, metric)

    print("\n🎉 RQ6 boxplots done. Outputs in:", OUTDIR.resolve())


if __name__ == "__main__":
    main()
