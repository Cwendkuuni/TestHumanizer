#!/usr/bin/env python3
import pandas as pd
import numpy as np
from pathlib import Path

# =========================
# Config
# =========================

BASE_DIR = Path(
    "/home/e113/Documents/Humanization-Project/HUMANIZATION/NEW-EXPERIMENTS-OUTPUTS/HUMAN-EVAL"
)

INPUT_XLSX            = BASE_DIR / "Final_annotation_score.xlsx"
OUT_LONG              = BASE_DIR / "rq6_ratings_long.csv"
OUT_SUMMARY_OVERALL   = BASE_DIR / "rq6_summary_overall.csv"
OUT_SUMMARY_BY_ROLE   = BASE_DIR / "rq6_summary_by_role.csv"
OUT_SUMMARY_BY_DATASET= BASE_DIR / "rq6_summary_by_dataset.csv"
OUT_DELTAS_PER_TASK   = BASE_DIR / "rq6_deltas_per_task.csv"


# =========================
# Helpers
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


# =========================
# Main
# =========================

def main():
    # 1) Charger la feuille "Master"
    df = pd.read_excel(INPUT_XLSX, sheet_name="Master")

    # Sanity-check rapide
    print("Rows in Master:", len(df))
    print("Columns:", list(df.columns))

    # 2) Construire un format 'long' pour les scores, par approche
    #
    # On a déjà dans le fichier des colonnes canonisées :
    #   EvoSuite_readability, Summary_readability,
    #   EvoSuite_trust,       Summary_trust,
    #   EvoSuite_adopt,       Summary_adopt
    #
    # On va transformer chaque ligne en 2 lignes :
    #   - approach = "EvoSuite"
    #   - approach = "Summary" (TestHumanizer)
    long_rows = []
    for _, r in df.iterrows():
        base = {
            "evaluator": r["evaluator"],          # Senior / Advanced graduate student
            "group": r["group"],                  # A / B
            "task_label": r["task_label"],        # Task 01, etc.
            "dataset": r["dataset"],              # Defects4J / SF110
            "project": r["project"],
            "class": r["class"],
            "size_bin": r["size_bin"],            # small / medium / large
            "loc": r["loc"],
        }

        for approach, prefix in [("EvoSuite", "EvoSuite"),
                                 ("Summary", "Summary")]:
            row = base.copy()
            row["approach"] = approach
            row["readability"] = r[f"{prefix}_readability"]
            row["trust"]       = r[f"{prefix}_trust"]
            row["adopt"]       = r[f"{prefix}_adopt"]
            long_rows.append(row)

    long_df = pd.DataFrame(long_rows)
    long_df.to_csv(OUT_LONG, index=False)
    print(f"Long ratings written to: {OUT_LONG}")

    # 3) Résumé global par approche × métrique
    records_overall = []
    melted = long_df.melt(
        id_vars=["approach"],
        value_vars=["readability", "trust", "adopt"],
        var_name="metric",
        value_name="score",
    )
    for (approach, metric), sub in melted.groupby(["approach", "metric"]):
        stats = describe_series(sub["score"])
        rec = {"approach": approach, "metric": metric}
        rec.update(stats)
        records_overall.append(rec)

    summary_overall = pd.DataFrame(records_overall).sort_values(
        ["metric", "approach"]
    )
    summary_overall.to_csv(OUT_SUMMARY_OVERALL, index=False)
    print(f"Overall summary written to: {OUT_SUMMARY_OVERALL}")

    # 4) Résumé par rôle (evaluator) × approche × métrique
    records_role = []
    melted_role = long_df.melt(
        id_vars=["evaluator", "approach"],
        value_vars=["readability", "trust", "adopt"],
        var_name="metric",
        value_name="score",
    )
    for (evaluator, approach, metric), sub in melted_role.groupby(
        ["evaluator", "approach", "metric"]
    ):
        stats = describe_series(sub["score"])
        rec = {
            "evaluator": evaluator,
            "approach": approach,
            "metric": metric,
        }
        rec.update(stats)
        records_role.append(rec)

    summary_by_role = pd.DataFrame(records_role).sort_values(
        ["metric", "evaluator", "approach"]
    )
    summary_by_role.to_csv(OUT_SUMMARY_BY_ROLE, index=False)
    print(f"Summary by role written to: {OUT_SUMMARY_BY_ROLE}")

    # 5) Résumé par dataset × approche × métrique
    records_dataset = []
    melted_ds = long_df.melt(
        id_vars=["dataset", "approach"],
        value_vars=["readability", "trust", "adopt"],
        var_name="metric",
        value_name="score",
    )
    for (dataset, approach, metric), sub in melted_ds.groupby(
        ["dataset", "approach", "metric"]
    ):
        stats = describe_series(sub["score"])
        rec = {
            "dataset": dataset,
            "approach": approach,
            "metric": metric,
        }
        rec.update(stats)
        records_dataset.append(rec)

    summary_by_dataset = pd.DataFrame(records_dataset).sort_values(
        ["dataset", "metric", "approach"]
    )
    summary_by_dataset.to_csv(OUT_SUMMARY_BY_DATASET, index=False)
    print(f"Summary by dataset written to: {OUT_SUMMARY_BY_DATASET}")

    # 6) Deltas Summary − EvoSuite par tâche (pour Wilcoxon & co plus tard)
    delta_cols = {
        "delta_readability": "Summary_readability",
        "delta_trust": "Summary_trust",
        "delta_adopt": "Summary_adopt",
    }
    deltas_df = df[
        [
            "evaluator",
            "group",
            "task_label",
            "dataset",
            "project",
            "class",
            "size_bin",
            "loc",
            "EvoSuite_readability",
            "Summary_readability",
            "EvoSuite_trust",
            "Summary_trust",
            "EvoSuite_adopt",
            "Summary_adopt",
        ]
    ].copy()

    deltas_df["delta_readability"] = (
        deltas_df["Summary_readability"] - deltas_df["EvoSuite_readability"]
    )
    deltas_df["delta_trust"] = (
        deltas_df["Summary_trust"] - deltas_df["EvoSuite_trust"]
    )
    deltas_df["delta_adopt"] = (
        deltas_df["Summary_adopt"] - deltas_df["EvoSuite_adopt"]
    )

    deltas_df.to_csv(OUT_DELTAS_PER_TASK, index=False)
    print(f"Deltas per task written to: {OUT_DELTAS_PER_TASK}")

    print("\nDone. You can now use:")
    print(f"  - {OUT_LONG.name} for boxplots")
    print(f"  - {OUT_SUMMARY_OVERALL.name} / {OUT_SUMMARY_BY_ROLE.name} / {OUT_SUMMARY_BY_DATASET.name} for tables")
    print(f"  - {OUT_DELTAS_PER_TASK.name} for Wilcoxon / paired analyses.")

if __name__ == "__main__":
    main()
