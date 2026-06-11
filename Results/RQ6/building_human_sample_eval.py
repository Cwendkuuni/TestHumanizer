#!/usr/bin/env python3
import json
import random
from pathlib import Path
from collections import defaultdict

# ============================================================
# Config
# ============================================================

BASE_DIR = Path("/home/e113/Documents/Humanization-Project/HUMANIZATION")

HUMAN_EVAL_DIR = BASE_DIR / "NEW-EXPERIMENTS-OUTPUTS" / "HUMAN-EVAL"
DEFECTS4J_JSON = HUMAN_EVAL_DIR / "Defects4J_complet_enriched.json"
SF110_JSON     = HUMAN_EVAL_DIR / "SF110_complet_enriched.json"

# Root directory where refactored tests live (Scenario-3, gpt-4o)
REFACTORED_ROOT = (
    BASE_DIR
    / "LLM-REFACTORED-TEST"
    / "GPT-ONLY-FOR-ICPC"
    / "A-REORGANIZ-COMPILE"
    / "REORGANIZED-TESTS-NEW"
)

REFACTORED_DEFECTS4J = REFACTORED_ROOT / "Defects4J-Compilable-OK" / "Scenario-3"
REFACTORED_SF110     = REFACTORED_ROOT / "SF110-Compilable-OK" / "Scenario-3"

# Where to write the selected tasks
OUTPUT_DIR = HUMAN_EVAL_DIR / "rq6_selected_tasks"

# Number of tasks per (dataset, size-bin)
TASKS_PER_BIN_PER_DATASET = 5  # tu peux remettre à 2 si tu veux

NOTE_LINES = [
    "Note:",
    "  - source.java         = full production class (from JSON).",
    "  - evo.java            = cleaned body of the original test class.",
    "  - testhumanizer.java  = cleaned body of the refactored test class (Scenario-3, gpt-4o).",
]


# ============================================================
# Helpers
# ============================================================

def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def size_bin(loc: int) -> str:
    """Bucket based on source_loc (you can tune thresholds if you like)."""
    if loc is None:
        return "unknown"
    if loc < 80:
        return "small"
    elif loc < 180:
        return "medium"
    else:
        return "large"


def extract_class_body(java_source: str) -> str:
    """
    Roughly keep only the class body:
    - drop package/imports/headers
    - keep from first '{' to last '}'.
    """
    if not java_source:
        return ""
    first = java_source.find('{')
    last = java_source.rfind('}')
    if first == -1 or last == -1 or last <= first:
        return java_source.strip()
    body = java_source[first + 1:last]
    return body.strip()


def walk_refactored_tests(root: Path):
    """
    Walk all *_ESTest.java under root and return a list of records:
    {
      "project_name": <folder 0>,
      "class":        <folder 1>,
      "test_file":    <filename>,
      "path":         Path(...)
    }

    Assumes a structure like:
      Scenario-3/<project>/<class>/<bug-id>/testsuite_X/iter-Y/.../*ESTest.java  (Defects4J)
      Scenario-3/<project>/<class>/testsuite_X/iter-Y/*ESTest.java             (SF110)
    We only care about the first two path components after root.
    """
    results = []
    for path in root.rglob("*_ESTest.java"):
        rel_parts = path.relative_to(root).parts
        if len(rel_parts) < 2:
            continue
        project = rel_parts[0]
        clazz   = rel_parts[1]
        test_file = path.name
        results.append(
            {
                "project_name": project,
                "class": clazz,
                "test_file": test_file,
                "path": path,
            }
        )
    return results


def build_index_by_project_class(json_records):
    """
    Build an index:
      (project_name, class) -> list of JSON records
    """
    index = defaultdict(list)
    for rec in json_records:
        proj = rec.get("project_name")
        cls  = rec.get("class")
        if proj is None or cls is None:
            continue
        index[(proj, cls)].append(rec)
    return index


def build_candidates_for_dataset(dataset_name: str,
                                 json_records,
                                 refactored_root: Path):
    """
    Build candidates by matching refactored tests with JSON entries via (project_name, class).
    We keep at most ONE candidate per (project_name, class) to avoid duplicates.
    """
    index = build_index_by_project_class(json_records)
    ref_infos = walk_refactored_tests(refactored_root)

    candidates = []
    seen_classes = set()  # (project_name, class) to avoid duplicates

    # deterministic order: sort by project/class/path
    ref_infos.sort(key=lambda r: (r["project_name"], r["class"], r["path"].as_posix()))

    for info in ref_infos:
        proj = info["project_name"]
        cls  = info["class"]
        key  = (proj, cls)

        if key in seen_classes:
            continue  # already have a candidate for this class

        if key not in index:
            continue

        # pick one JSON record (e.g., first) for this class
        rec = index[key][0]
        test_code   = rec.get("test_code") or ""
        source_code = rec.get("source_code") or ""
        source_loc  = rec.get("source_loc")

        if not test_code or not source_code or source_loc is None:
            continue

        candidates.append(
            {
                "dataset": dataset_name,
                "project_name": proj,
                "class": cls,
                "json_record": rec,
                "refactored_path": info["path"],
                "source_loc": source_loc,
            }
        )
        seen_classes.add(key)

    return candidates


def stratified_sample_tasks(candidates, tasks_per_bin: int):
    """
    Stratify by (dataset, size_bin) and sample up to tasks_per_bin per group.
    """
    grouped = defaultdict(list)
    for c in candidates:
        b = size_bin(c["source_loc"])
        if b == "unknown":
            continue
        grouped[(c["dataset"], b)].append(c)

    selected = []
    stats = defaultdict(lambda: {"count": 0, "methods": 0})

    for (dataset, bin_name), group in grouped.items():
        if not group:
            continue
        random.shuffle(group)
        take = min(tasks_per_bin, len(group))
        chosen = group[:take]
        for c in chosen:
            selected.append(c)
            stats[(dataset, bin_name)]["count"] += 1
            stats[(dataset, bin_name)]["methods"] += int(
                c["json_record"].get("method_count", 0)
            )

    return selected, stats


# ============================================================
# Main
# ============================================================

def main():
    random.seed(42)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    defects_data = load_json(DEFECTS4J_JSON)
    sf110_data   = load_json(SF110_JSON)

    # Build candidates
    defects_candidates = build_candidates_for_dataset(
        "Defects4J", defects_data, REFACTORED_DEFECTS4J
    )
    sf110_candidates = build_candidates_for_dataset(
        "SF110", sf110_data, REFACTORED_SF110
    )

    print(f"Defects4J: {len(defects_candidates)} candidates found.")
    print(f"SF110: {len(sf110_candidates)} candidates found.")

    all_candidates = defects_candidates + sf110_candidates

    selected, stats = stratified_sample_tasks(
        all_candidates,
        tasks_per_bin=TASKS_PER_BIN_PER_DATASET,
    )

    print(f"Selected {len(selected)} tasks in total.")
    # tri pour affichage lisible
    selected.sort(key=lambda c: (c["dataset"], c["project_name"], c["class"]))
    for c in selected:
        print(
            f"- {c['dataset']} / {c['project_name']} / {c['class']} "
            f"(source_loc={c['source_loc']})"
        )

    # Matérialiser les tâches
    for idx, c in enumerate(selected, start=1):
        rec        = c["json_record"]
        dataset    = c["dataset"]
        project    = c["project_name"]
        clazz      = c["class"]
        loc        = c["source_loc"]
        bin_name   = size_bin(loc)
        iteration  = rec.get("iteration", "N/A")
        test_file  = rec.get("test_file", "N/A")

        task_dir_name = f"{idx:02d}_{dataset}_{project}_{clazz}_{bin_name}"
        task_dir = OUTPUT_DIR / task_dir_name
        task_dir.mkdir(parents=True, exist_ok=True)

        # README
        readme_path = task_dir / "README.txt"
        with readme_path.open("w", encoding="utf-8") as f:
            f.write(f"Dataset : {dataset}\n")
            f.write(f"Project : {project}\n")
            f.write(f"Class   : {clazz}\n")
            f.write(f"Size    : {bin_name} (source_loc={loc})\n")
            f.write(f"Iteration   : {iteration}\n")
            f.write(f"Test file   : {test_file}\n")
            f.write("\n")
            for line in NOTE_LINES:
                f.write(line + "\n")

        # Source code (production class)
        source_code = rec.get("source_code") or ""
        (task_dir / "source.java").write_text(source_code, encoding="utf-8")

        # EvoSuite test body (cleaned)
        evo_code_raw = rec.get("test_code") or ""
        evo_clean = extract_class_body(evo_code_raw)
        (task_dir / "evo.java").write_text(evo_clean, encoding="utf-8")

        # TestHumanizer refactored test (cleaned)
        ref_path = c["refactored_path"]
        ref_code_raw = ref_path.read_text(encoding="utf-8", errors="ignore")
        ref_clean = extract_class_body(ref_code_raw)
        (task_dir / "testhumanizer.java").write_text(ref_clean, encoding="utf-8")

        # Class summary file
        summary_text = rec.get("source_code_summary") or ""
        summary_path = task_dir / "summary.txt"
        with summary_path.open("w", encoding="utf-8") as f:
            f.write(f"Dataset : {dataset}\n")
            f.write(f"Project : {project}\n")
            f.write(f"Class   : {clazz}\n")
            f.write(f"Size    : {bin_name} (source_loc={loc})\n")
            f.write(f"Test methods : {rec.get('method_count', 'N/A')}\n")
            f.write("\nClass summary:\n")
            f.write(summary_text.strip() + "\n")

    # Stats recap
    print("\nSummary of selected tasks (by dataset and size bin):")
    for dataset in ["Defects4J", "SF110"]:
        for bin_name in ["small", "medium", "large"]:
            key = (dataset, bin_name)
            if key not in stats:
                continue
            info = stats[key]
            print(
                f"- {dataset} / {bin_name}: "
                f"{info['count']} classes, "
                f"{info['methods']} EvoSuite test methods in total"
            )

    print(f"\nTasks written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
