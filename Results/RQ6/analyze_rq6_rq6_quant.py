#!/usr/bin/env python3
import pandas as pd
import numpy as np
from pathlib import Path
from math import sqrt
from scipy import stats  # <--- nouveau

# =========================
# Config
# =========================

BASE_DIR = Path(
    "/home/e113/Documents/Humanization-Project/HUMANIZATION/NEW-EXPERIMENTS-OUTPUTS/HUMAN-EVAL"
)

INPUT_XLSX             = BASE_DIR / "Final_annotation_score.xlsx"
OUT_LONG               = BASE_DIR / "rq6_ratings_long.csv"
OUT_SUMMARY_OVERALL    = BASE_DIR / "rq6_summary_overall.csv"
OUT_SUMMARY_BY_ROLE    = BASE_DIR / "rq6_summary_by_role.csv"
OUT_SUMMARY_BY_DATASET = BASE_DIR / "rq6_summary_by_dataset.csv"
OUT_DELTAS_PER_TASK    = BASE_DIR / "rq6_deltas_per_task.csv"

OUT_WILCOX_OVERALL     = BASE_DIR / "rq6_wilcoxon_overall.csv"   # <--- nouveau
OUT_WILCOX_BY_ROLE     = BASE_DIR / "rq6_wilcoxon_by_role.csv"   # <--- nouveau


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


def compute_wilcoxon(sub_df: pd.DataFrame,
                     metric_name: str,
                     evo_col: str,
                     summary_col: str,
                     level_name: str,
                     level_value: str):
    """
    Calcule Wilcoxon (paired) + taille d'effet r pour un sous-dataframe.

    level_name  : "scope" ou "evaluator" (étiquette de niveau)
    level_value : "overall" ou "Senior developer", etc.
    """
    x = sub_df[evo_col].astype(float)
    y = sub_df[summary_col].astype(float)

    # enlever NaN
    mask = ~(x.isna() | y.isna())
    x = x[mask]
    y = y[mask]

    if len(x) == 0:
        return None

    diff = y - x
    # N non-zéro pour la taille d'effet
    diff_nz = diff[diff != 0]
    N_nonzero = len(diff_nz)

    median_diff = float(diff.median())
    mean_diff = float(diff.mean())

    # si toutes les différences sont nulles, Wilcoxon n'a pas de sens
    if N_nonzero == 0:
        return {
            "metric": metric_name,
            level_name: level_value,
            "N_pairs": int(len(x)),
            "N_nonzero_diff": 0,
            "median_EvoSuite": float(x.median()),
            "median_Summary": float(y.median()),
            "median_diff_TH_minus_EV": 0.0,
            "mean_diff_TH_minus_EV": 0.0,
            "W_statistic": np.nan,
            "p_two_sided": 1.0,
            "p_one_sided_TH_greater_EV": 1.0,
            "z_approx": np.nan,
            "effect_size_r": np.nan,
        }

    # Wilcoxon apparié, two-sided
    stat, p_two = stats.wilcoxon(x, y, alternative="two-sided", zero_method="wilcox")

    # Approximation du Z à partir de la p-value (two-sided)
    if p_two > 0:
        z = stats.norm.isf(p_two / 2.0) * np.sign(median_diff)
        r = z / sqrt(N_nonzero)
    else:
        z = np.nan
        r = np.nan

    # p-value one-sided pour l'hypothèse "Summary (TestHumanizer) > EvoSuite"
    if median_diff > 0:
        p_one = p_two / 2.0
    else:
        p_one = 1.0 - p_two / 2.0

    return {
        "metric": metric_name,
        level_name: level_value,
        "N_pairs": int(len(x)),
        "N_nonzero_diff": int(N_nonzero),
        "median_EvoSuite": float(x.median()),
        "median_Summary": float(y.median()),
        "median_diff_TH_minus_EV": median_diff,
        "mean_diff_TH_minus_EV": mean_diff,
        "W_statistic": float(stat),
        "p_two_sided": float(p_two),
        "p_one_sided_TH_greater_EV": float(p_one),
        "z_approx": float(z),
        "effect_size_r": float(r),
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
        stats_desc = describe_series(sub["score"])
        rec = {"approach": approach, "metric": metric}
        rec.update(stats_desc)
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
        stats_desc = describe_series(sub["score"])
        rec = {
            "evaluator": evaluator,
            "approach": approach,
            "metric": metric,
        }
        rec.update(stats_desc)
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
        stats_desc = describe_series(sub["score"])
        rec = {
            "dataset": dataset,
            "approach": approach,
            "metric": metric,
        }
        rec.update(stats_desc)
        records_dataset.append(rec)

    summary_by_dataset = pd.DataFrame(records_dataset).sort_values(
        ["dataset", "metric", "approach"]
    )
    summary_by_dataset.to_csv(OUT_SUMMARY_BY_DATASET, index=False)
    print(f"Summary by dataset written to: {OUT_SUMMARY_BY_DATASET}")

    # 6) Deltas Summary − EvoSuite par tâche (pour Wilcoxon & co)
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

    # =======================================================
    # 7) Wilcoxon apparié + taille d'effet r
    #    (overall et par rôle) pour readability / trust / adopt
    # =======================================================

    metrics_info = {
        "readability": ("EvoSuite_readability", "Summary_readability"),
        "trust":       ("EvoSuite_trust",       "Summary_trust"),
        "adopt":       ("EvoSuite_adopt",       "Summary_adopt"),
    }

    # 7.a) Overall (tous évaluateurs confondus)
    rows_overall = []
    for metric_name, (evo_col, summary_col) in metrics_info.items():
        res = compute_wilcoxon(
            deltas_df,
            metric_name=metric_name,
            evo_col=evo_col,
            summary_col=summary_col,
            level_name="scope",
            level_value="overall",
        )
        if res is not None:
            rows_overall.append(res)

    wilcox_overall = pd.DataFrame(rows_overall)
    wilcox_overall.to_csv(OUT_WILCOX_OVERALL, index=False)
    print(f"Wilcoxon overall written to: {OUT_WILCOX_OVERALL}")

    # 7.b) Par rôle (Advanced graduate student / Senior developer)
    rows_role = []
    for evaluator in deltas_df["evaluator"].unique():
        sub = deltas_df[deltas_df["evaluator"] == evaluator]
        for metric_name, (evo_col, summary_col) in metrics_info.items():
            res = compute_wilcoxon(
                sub,
                metric_name=metric_name,
                evo_col=evo_col,
                summary_col=summary_col,
                level_name="evaluator",
                level_value=evaluator,
            )
            if res is not None:
                rows_role.append(res)

    wilcox_role = pd.DataFrame(rows_role)
    wilcox_role.to_csv(OUT_WILCOX_BY_ROLE, index=False)
    print(f"Wilcoxon by role written to: {OUT_WILCOX_BY_ROLE}")

    print("\nDone. You can now use:")
    print(f"  - {OUT_LONG.name} for boxplots")
    print(f"  - {OUT_SUMMARY_OVERALL.name} / {OUT_SUMMARY_BY_ROLE.name} / {OUT_SUMMARY_BY_DATASET.name} for tables")
    print(f"  - {OUT_DELTAS_PER_TASK.name} for quick inspection of per-task differences")
    print(f"  - {OUT_WILCOX_OVERALL.name} / {OUT_WILCOX_BY_ROLE.name} for Wilcoxon p-values & effect sizes")


if __name__ == "__main__":
    main()
