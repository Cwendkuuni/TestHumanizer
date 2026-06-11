import os
import re
import json
import pandas as pd

# ✅ Chemin vers ton dossier METRICS_STATISTICS
ROOT = "/home/e113/Documents/Humanization-Project/HUMANIZATION/NEW-EXPERIMENTS-OUTPUTS/LLM-REFACTORED/RQ3/METRICS_OUTPUT_GPT_PREPROCESSED/METRICS_STATISTICS"

# (Optionnel) mapping Scenario -> Approach, si tu veux l'avoir dans le CSV
SCENARIO_TO_APPROACH = {
    "1": "Tests-only",
    "2": "Code-centric",
    "3": "Summary-based",
}

pattern = re.compile(r"^STATS_(?P<dataset>[^-]+)-Scenario-(?P<scenario>\d+)-metrics\.json$")

rows = []

for fname in sorted(os.listdir(ROOT)):
    m = pattern.match(fname)
    if not m:
        continue

    dataset = m.group("dataset")
    scenario = m.group("scenario")
    approach = SCENARIO_TO_APPROACH.get(scenario, f"Scenario-{scenario}")

    fpath = os.path.join(ROOT, fname)
    with open(fpath, "r") as f:
        data = json.load(f)

    # data: { metric_name: { "Min":..., "Q1":..., ... } }
    for metric_name, stats in data.items():
        # Certains champs peuvent manquer selon la métrique => .get()
        row = {
            "dataset": dataset,
            "scenario": int(scenario),
            "approach": approach,
            "metric": metric_name,

            "min": stats.get("Min"),
            "q1": stats.get("Q1"),
            "mean": stats.get("Mean"),
            "q3": stats.get("Q3"),
            "max": stats.get("Max"),

            "lt_0_5_percent": stats.get("<0.5 %"),
            "ge_0_5_percent": stats.get(">=0.5 %"),
        }
        rows.append(row)

df = pd.DataFrame(rows)

# Tri propre
df = df.sort_values(["dataset", "scenario", "metric"]).reset_index(drop=True)

# Sauvegardes
out_csv = os.path.join("RQ3_metrics_statistics_aggregated.csv")
out_json = os.path.join("RQ3_metrics_statistics_aggregated.json")

df.to_csv(out_csv, index=False)
df.to_json(out_json, orient="records", indent=2)

print("✅ Generated:")
print("-", out_csv)
print("-", out_json)
print("\nPreview:")
print(df.head(20).to_string(index=False))
