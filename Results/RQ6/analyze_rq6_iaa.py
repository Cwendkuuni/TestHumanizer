#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats


# -------------------------
# Ordinal agreement metrics
# -------------------------

def quadratic_weighted_kappa(a, b, min_rating=1, max_rating=5):
    """
    Quadratic Weighted Cohen's Kappa for ordinal ratings.
    a, b: 1D arrays of same length (no NaN)
    """
    a = np.asarray(a, dtype=int)
    b = np.asarray(b, dtype=int)
    assert a.shape == b.shape

    n_cat = max_rating - min_rating + 1
    # Confusion matrix O
    O = np.zeros((n_cat, n_cat), dtype=float)
    for x, y in zip(a, b):
        O[x - min_rating, y - min_rating] += 1.0

    # Expected matrix E from marginals
    a_hist = O.sum(axis=1)
    b_hist = O.sum(axis=0)
    N = O.sum()
    if N == 0:
        return np.nan

    E = np.outer(a_hist, b_hist) / N

    # Weight matrix W (quadratic)
    W = np.zeros((n_cat, n_cat), dtype=float)
    for i in range(n_cat):
        for j in range(n_cat):
            W[i, j] = ((i - j) ** 2) / ((n_cat - 1) ** 2)

    num = (W * O).sum()
    den = (W * E).sum()
    if den == 0:
        return np.nan
    return 1.0 - (num / den)


def percent_agreement(a, b):
    a = np.asarray(a)
    b = np.asarray(b)
    if len(a) == 0:
        return np.nan
    return float(np.mean(a == b))


def krippendorff_alpha_ordinal(df_wide: pd.DataFrame) -> float:
    """
    Krippendorff's alpha for ordinal data.
    df_wide: rows=items, cols=raters, values=ratings (1..5), NaN allowed
    """
    data = df_wide.to_numpy(dtype=float)
    values = data[~np.isnan(data)]
    if values.size == 0:
        return np.nan

    cats = np.unique(values)
    k = len(cats)
    if k < 2:
        return np.nan

    cat_to_idx = {c: i for i, c in enumerate(cats)}
    ranks = np.arange(k)

    def delta(x, y):
        ix, iy = cat_to_idx[x], cat_to_idx[y]
        return ((ranks[ix] - ranks[iy]) ** 2) / ((k - 1) ** 2)

    # Observed disagreement Do
    Do = 0.0
    n_pairs = 0
    for row in data:
        row_vals = row[~np.isnan(row)]
        m = len(row_vals)
        if m < 2:
            continue
        for i in range(m):
            for j in range(i + 1, m):
                Do += delta(row_vals[i], row_vals[j])
                n_pairs += 1
    if n_pairs == 0:
        return np.nan
    Do /= n_pairs

    # Expected disagreement De
    counts = {c: 0 for c in cats}
    for v in values:
        counts[v] += 1
    N = values.size
    if N < 2:
        return np.nan

    denom = N * (N - 1) / 2
    De = 0.0
    for i in range(k):
        for j in range(i + 1, k):
            ci, cj = cats[i], cats[j]
            De += counts[ci] * counts[cj] * delta(ci, cj)
    De /= denom

    if De == 0:
        return np.nan
    return 1.0 - (Do / De)


# -------------------------
# Data wrangling
# -------------------------

def build_long(df: pd.DataFrame) -> pd.DataFrame:
    """
    Builds long format with columns:
    item_id, group, evaluator, rater_id, approach, dataset, project, class, size_bin, loc,
    readability, trust, adopt
    """
    df = df.copy()

    # Create a unique rater id (works with your design: 1 senior + 1 grad per group)
    df["rater_id"] = df["group"].astype(str) + "__" + df["evaluator"].astype(str)

    # Define an item_id that is stable within the full dataset
    # Task labels may repeat across groups, so include group in the key.
    df["item_id"] = df["group"].astype(str) + "::" + df["task_label"].astype(str)

    cols_keep = [
        "item_id", "rater_id", "group", "evaluator",
        "dataset", "project", "class", "size_bin", "loc",
        "EvoSuite_readability", "Summary_readability",
        "EvoSuite_trust", "Summary_trust",
        "EvoSuite_adopt", "Summary_adopt"
    ]
    missing = [c for c in cols_keep if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in Master sheet: {missing}")

    df = df[cols_keep]

    long_rows = []

    for _, r in df.iterrows():
        base = {
            "item_id": r["item_id"],
            "rater_id": r["rater_id"],
            "group": r["group"],
            "evaluator": r["evaluator"],
            "dataset": r["dataset"],
            "project": r["project"],
            "class": r["class"],
            "size_bin": r["size_bin"],
            "loc": r["loc"],
        }

        for approach, prefix in [("EvoSuite", "EvoSuite"), ("Summary", "Summary")]:
            row = dict(base)
            row["approach"] = approach
            row["readability"] = r[f"{prefix}_readability"]
            row["trust"] = r[f"{prefix}_trust"]
            row["adopt"] = r[f"{prefix}_adopt"]
            long_rows.append(row)

    return pd.DataFrame(long_rows)


def compute_iaa_for_scope(long_df: pd.DataFrame, scope_name: str) -> pd.DataFrame:
    """
    Computes IAA per (approach x metric) for a scope dataframe.
    If exactly 2 raters are present -> also computes QWK & percent agreement & Spearman.
    Always computes Krippendorff alpha (ordinal) using item×rater matrix.
    """
    results = []
    metrics = ["readability", "trust", "adopt"]
    approaches = ["EvoSuite", "Summary"]

    for approach in approaches:
        sub_a = long_df[long_df["approach"] == approach]
        raters = sorted(sub_a["rater_id"].dropna().unique().tolist())

        for metric in metrics:
            tmp = sub_a[["item_id", "rater_id", metric]].dropna()
            if tmp.empty:
                continue

            wide = tmp.pivot_table(
                index="item_id",
                columns="rater_id",
                values=metric,
                aggfunc="mean"
            ).sort_index()

            n_items = int(wide.shape[0])
            n_raters = int(wide.shape[1])

            alpha = krippendorff_alpha_ordinal(wide)

            row = {
                "scope": scope_name,
                "approach": approach,
                "metric": metric,
                "n_items": n_items,
                "n_raters": n_raters,
                "krippendorff_alpha_ordinal": float(alpha) if not np.isnan(alpha) else np.nan,
                "qwk": np.nan,
                "percent_agreement": np.nan,
                "spearman_rho": np.nan,
                "spearman_p": np.nan,
            }

            # If exactly two raters -> compute pairwise metrics
            if n_raters == 2:
                r1, r2 = wide.columns[0], wide.columns[1]
                pair = wide[[r1, r2]].dropna()
                a = pair[r1].astype(int).to_numpy()
                b = pair[r2].astype(int).to_numpy()

                if len(a) > 0:
                    row["qwk"] = float(quadratic_weighted_kappa(a, b, 1, 5))
                    row["percent_agreement"] = float(percent_agreement(a, b))
                    rho, p = stats.spearmanr(a, b)
                    row["spearman_rho"] = float(rho) if rho is not None else np.nan
                    row["spearman_p"] = float(p) if p is not None else np.nan

                    # n_items should reflect paired items for 2-rater metrics
                    row["n_items"] = int(pair.shape[0])

            results.append(row)

    return pd.DataFrame(results)


# -------------------------
# Main
# -------------------------

def main():
    parser = argparse.ArgumentParser(description="Compute inter-annotator agreement (IAA) for RQ6 human eval.")
    parser.add_argument("--xlsx", required=True, help="Path to Final_annotation_score.xlsx")
    parser.add_argument("--sheet", default="Master", help="Sheet name (default: Master)")
    parser.add_argument("--out", required=True, help="Output CSV path (e.g., rq6_iaa_results.csv)")
    args = parser.parse_args()

    xlsx_path = Path(args.xlsx)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_excel(xlsx_path, sheet_name=args.sheet)

    # Build long format (EvoSuite vs Summary)
    long_df = build_long(df)

    # Scopes: group A, group B, overall
    outputs = []

    for g in sorted(long_df["group"].dropna().unique().tolist()):
        sub = long_df[long_df["group"] == g]
        outputs.append(compute_iaa_for_scope(sub, scope_name=f"group:{g}"))

    outputs.append(compute_iaa_for_scope(long_df, scope_name="overall"))

    res = pd.concat(outputs, ignore_index=True)

    # Nice ordering
    res = res.sort_values(["scope", "metric", "approach"]).reset_index(drop=True)
    res.to_csv(out_path, index=False)

    print(f"[OK] IAA results written to: {out_path}")
    print(res.to_string(index=False))


if __name__ == "__main__":
    main()
