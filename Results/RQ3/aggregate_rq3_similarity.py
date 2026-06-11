import os
import json
import pandas as pd
import numpy as np

# === ROOT PATH ===
ROOT = "/home/e113/Documents/Humanization-Project/HUMANIZATION/NEW-EXPERIMENTS-OUTPUTS/LLM-REFACTORED/RQ3"

FOLDERS = {
    "CodeBERT": "GPT_OUTPUT_CODEBERT_PREPROCESS",
    "GraphCodeBERT": "GPT_OUTPUT_GRAPH_CODEBERT_PREPROCESS",
    "OpenAI": "GPT_OUTPUT_OPENAI_PREPROCESS",
}

all_rows = []

# === PARSE ALL FILES ===
for model_name, folder in FOLDERS.items():
    folder_path = os.path.join(ROOT, folder)

    for filename in os.listdir(folder_path):
        if not filename.endswith(".json"):
            continue

        # Example: Defects4J-Scenario-1-similarity.json
        parts = filename.replace(".json", "").split("-")
        dataset = parts[0]
        scenario = parts[2]

        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r") as f:
            data = json.load(f)

        for entry in data:
            all_rows.append({
                "dataset": dataset,
                "scenario": scenario,
                "embedding_model": model_name,
                "cosine_similarity": entry["cosine_similarity"]
            })

# === CREATE DATAFRAME ===
df = pd.DataFrame(all_rows)

print("\nTotal entries:", len(df))

# ==========================================================
# 📊 GLOBAL AGGREGATION (ALL EMBEDDINGS)
# ==========================================================

global_stats = (
    df.groupby(["dataset", "scenario"])["cosine_similarity"]
    .agg(
        min="min",
        max="max",
        mean="mean",
        q1=lambda x: np.percentile(x, 25),
        q3=lambda x: np.percentile(x, 75)
    )
    .reset_index()
)

print("\n===== GLOBAL STATS (ALL EMBEDDINGS) =====")
print(global_stats)

# ==========================================================
# 📊 PER EMBEDDING MODEL
# ==========================================================

model_stats = (
    df.groupby(["dataset", "scenario", "embedding_model"])["cosine_similarity"]
    .agg(
        min="min",
        max="max",
        mean="mean",
        q1=lambda x: np.percentile(x, 25),
        q3=lambda x: np.percentile(x, 75)
    )
    .reset_index()
)

print("\n===== STATS PER EMBEDDING MODEL =====")
print(model_stats)

# ==========================================================
# 💾 SAVE TO CSV (FOR PAPER)
# ==========================================================

global_stats.to_csv("RQ3_global_similarity_stats.csv", index=False)
model_stats.to_csv("RQ3_per_model_similarity_stats.csv", index=False)

print("\nCSV files generated:")
print("- RQ3_global_similarity_stats.csv")
print("- RQ3_per_model_similarity_stats.csv")
