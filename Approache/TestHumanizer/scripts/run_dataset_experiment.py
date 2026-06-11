from __future__ import annotations

import argparse
import csv
import json
import os
import random
import shlex
import shutil
import subprocess
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import yaml


TARGET_FIELDS = [
    "dataset",
    "project",
    "class_name",
    "bug_id",
    "source_path",
    "classpath",
    "test_class_fqdn",
    "class_files_dir",
    "source_files_dir",
]


INTERNAL_FIELDS = [
    "_source_exists",
    "_class_exists",
    "_source_token_count",
    "_source_method_count",
    "_source_loc",
    "_metadata_key",
]


REQUIRED_JSON_FIELDS = [
    "dataset",
    "project_name",
    "class",
    "fqdn",
    "source_code",
]


def load_json_records(path: Path) -> List[Dict[str, Any]]:
    """
    Load either:
      1. a standard JSON list: [ {...}, {...} ]
      2. a JSONL file: one JSON object per line

    The current Defects4J/SF110 extracted datasets are expected to be JSON lists,
    but JSONL support is useful for future large datasets.
    """
    if not path.exists():
        raise FileNotFoundError(f"Metadata file not found: {path}")

    text = path.read_text(encoding="utf-8").strip()

    if not text:
        return []

    if text.startswith("["):
        data = json.loads(text)
        if not isinstance(data, list):
            raise ValueError(f"Expected a JSON list in {path}")
        if not all(isinstance(item, dict) for item in data):
            raise ValueError(f"Expected all JSON list items to be objects in {path}")
        return data

    rows: List[Dict[str, Any]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue

        obj = json.loads(line)
        if not isinstance(obj, dict):
            raise ValueError(f"Expected JSON object at line {line_no} in {path}")
        rows.append(obj)

    return rows


def validate_json_rows(rows: Sequence[Dict[str, Any]], *, dataset: str) -> None:
    """
    Validate the minimal expected schema.

    Defects4J should normally have bug-id.
    SF110 can have bug-id = null.
    """
    if not rows:
        raise ValueError("Metadata contains no rows.")

    missing_examples: List[str] = []

    for index, row in enumerate(rows[:50]):
        missing = [field for field in REQUIRED_JSON_FIELDS if field not in row]
        if missing:
            missing_examples.append(f"row={index}, missing={missing}")

    if missing_examples:
        joined = "\n".join(missing_examples[:10])
        raise ValueError(f"Invalid metadata schema:\n{joined}")

    if dataset.lower() == "defects4j":
        missing_bug_id = [
            index
            for index, row in enumerate(rows[:50])
            if row.get("bug-id") in (None, "")
        ]
        if missing_bug_id:
            raise ValueError(
                "Defects4J rows should contain a non-empty bug-id. "
                f"Examples with missing bug-id: {missing_bug_id[:10]}"
            )


def stable_key(row: Dict[str, Any]) -> Tuple[str, str, str, str, str]:
    """
    Unique target key.

    The raw extracted datasets can contain duplicates because the same source
    class may appear multiple times after extraction/enrichment.
    """
    return (
        str(row.get("dataset") or ""),
        str(row.get("project_name") or ""),
        str(row.get("bug-id") or ""),
        str(row.get("class") or ""),
        str(row.get("fqdn") or ""),
    )


def key_to_string(key: Tuple[str, str, str, str, str]) -> str:
    dataset, project, bug_id, class_name, fqdn = key
    return f"{dataset}|{project}|{bug_id}|{class_name}|{fqdn}"


def deduplicate_rows(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: set[Tuple[str, str, str, str, str]] = set()
    unique: List[Dict[str, Any]] = []

    for row in rows:
        key = stable_key(row)
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)

    return unique


def fqdn_to_path(fqdn: str) -> Path:
    return Path(*fqdn.split(".")) if fqdn else Path()


def make_test_class_fqdn(package_fqdn: str, class_name: str) -> str:
    if package_fqdn:
        return f"{package_fqdn}.{class_name}"
    return class_name


def collect_jars(directory: Path, *, recursive: bool = False) -> List[str]:
    """
    Collect real jar paths.

    Important: do not return wildcard entries such as /path/to/jars/* because
    EvoSuite validates classpath entries literally and can reject wildcard paths.
    """
    if not directory.exists():
        return []

    pattern = "**/*.jar" if recursive else "*.jar"
    jars = sorted(directory.glob(pattern))

    return [str(jar.resolve()) for jar in jars if jar.is_file()]


def split_classpath_entries(classpath: str | None) -> List[str]:
    """
    Split a user-provided classpath string.

    Supports OS-specific separators. On Linux, this is ':'.
    Empty values are ignored.
    """
    if not classpath:
        return []

    entries: List[str] = []

    for part in classpath.split(os.pathsep):
        clean = part.strip()
        if clean:
            entries.append(clean)

    return entries


def normalize_extra_classpath_entries(entries: Sequence[str]) -> List[str]:
    """
    Normalize extra classpath entries.

    Entries can be:
      - jar files
      - directories
      - class directories

    Wildcards are intentionally not expanded here. Use real paths.
    """
    normalized: List[str] = []

    for entry in entries:
        path = Path(entry).expanduser().resolve()
        if path.exists():
            normalized.append(str(path))
        else:
            normalized.append(str(path))

    return normalized


def build_classpath(
    *,
    class_files_dir: Path,
    project_root: Path,
    global_dependencies_dir: Path | None,
    extra_classpath_entries: Sequence[str],
    project_jars_recursive: bool,
) -> str:
    """
    Build the classpath used by EvoSuite and downstream validation.

    Default behavior:
      - include the class directory/root
      - include project-local jars
      - do not include huge global dependency directories unless explicitly requested

    This avoids EvoSuite scanning unrelated modern jars and failing on unsupported
    Java class file versions.
    """
    parts: List[str] = [str(class_files_dir.resolve())]

    # Project-local jars, e.g., SF110 project jars such as javex.jar.
    parts.extend(
        collect_jars(project_root.resolve(), recursive=project_jars_recursive)
    )

    # Optional global dependency jars. Disabled by default.
    if global_dependencies_dir is not None:
        parts.extend(collect_jars(global_dependencies_dir.resolve(), recursive=False))

    # Optional user-provided extra classpath entries.
    parts.extend(normalize_extra_classpath_entries(extra_classpath_entries))

    # Preserve order while removing duplicates.
    deduped: List[str] = []
    seen: set[str] = set()

    for part in parts:
        if part not in seen:
            seen.add(part)
            deduped.append(part)

    return os.pathsep.join(deduped)


def normalize_defects4j_row(
    row: Dict[str, Any],
    *,
    defects4j_sources_root: Path,
    global_dependencies_dir: Path | None,
    extra_classpath_entries: Sequence[str],
    project_jars_recursive: bool,
) -> Dict[str, str]:
    project = str(row["project_name"])
    bug_id = str(row["bug-id"])
    class_name = str(row["class"])
    package_fqdn = str(row.get("fqdn") or "")

    project_bug_root = defects4j_sources_root / project / bug_id
    package_path = fqdn_to_path(package_fqdn)

    source_path = project_bug_root / package_path / f"{class_name}.java"
    class_file = project_bug_root / package_path / f"{class_name}.class"

    return {
        "dataset": "Defects4J",
        "project": project,
        "class_name": class_name,
        "bug_id": bug_id,
        "source_path": str(source_path.resolve()),
        "classpath": build_classpath(
            class_files_dir=project_bug_root,
            project_root=project_bug_root,
            global_dependencies_dir=global_dependencies_dir,
            extra_classpath_entries=extra_classpath_entries,
            project_jars_recursive=project_jars_recursive,
        ),
        "test_class_fqdn": make_test_class_fqdn(package_fqdn, class_name),
        "class_files_dir": str(project_bug_root.resolve()),
        "source_files_dir": str(project_bug_root.resolve()),
        "_source_exists": str(source_path.exists()),
        "_class_exists": str(class_file.exists()),
        "_source_token_count": str(row.get("source_token_count", "")),
        "_source_method_count": str(row.get("source_method_count", "")),
        "_source_loc": str(row.get("source_loc", "")),
        "_metadata_key": key_to_string(stable_key(row)),
    }


def normalize_sf110_row(
    row: Dict[str, Any],
    *,
    sf110_sources_root: Path,
    global_dependencies_dir: Path | None,
    extra_classpath_entries: Sequence[str],
    project_jars_recursive: bool,
) -> Dict[str, str]:
    project = str(row["project_name"])
    class_name = str(row["class"])
    package_fqdn = str(row.get("fqdn") or "")

    project_root = sf110_sources_root / project
    package_path = fqdn_to_path(package_fqdn)

    source_path = project_root / package_path / f"{class_name}.java"
    class_file = project_root / package_path / f"{class_name}.class"

    return {
        "dataset": "SF110",
        "project": project,
        "class_name": class_name,
        "bug_id": "",
        "source_path": str(source_path.resolve()),
        "classpath": build_classpath(
            class_files_dir=project_root,
            project_root=project_root,
            global_dependencies_dir=global_dependencies_dir,
            extra_classpath_entries=extra_classpath_entries,
            project_jars_recursive=project_jars_recursive,
        ),
        "test_class_fqdn": make_test_class_fqdn(package_fqdn, class_name),
        "class_files_dir": str(project_root.resolve()),
        "source_files_dir": str(project_root.resolve()),
        "_source_exists": str(source_path.exists()),
        "_class_exists": str(class_file.exists()),
        "_source_token_count": str(row.get("source_token_count", "")),
        "_source_method_count": str(row.get("source_method_count", "")),
        "_source_loc": str(row.get("source_loc", "")),
        "_metadata_key": key_to_string(stable_key(row)),
    }


def normalize_rows(
    rows: List[Dict[str, Any]],
    *,
    dataset: str,
    defects4j_sources_root: Path,
    sf110_sources_root: Path,
    global_dependencies_dir: Path | None,
    extra_classpath_entries: Sequence[str],
    project_jars_recursive: bool,
) -> List[Dict[str, str]]:
    normalized: List[Dict[str, str]] = []

    for row in rows:
        if dataset.lower() == "defects4j":
            normalized.append(
                normalize_defects4j_row(
                    row,
                    defects4j_sources_root=defects4j_sources_root,
                    global_dependencies_dir=global_dependencies_dir,
                    extra_classpath_entries=extra_classpath_entries,
                    project_jars_recursive=project_jars_recursive,
                )
            )
        elif dataset.lower() == "sf110":
            normalized.append(
                normalize_sf110_row(
                    row,
                    sf110_sources_root=sf110_sources_root,
                    global_dependencies_dir=global_dependencies_dir,
                    extra_classpath_entries=extra_classpath_entries,
                    project_jars_recursive=project_jars_recursive,
                )
            )
        else:
            raise ValueError(f"Unsupported dataset: {dataset}")

    return normalized


def filter_missing(
    rows: List[Dict[str, str]],
    *,
    strict: bool,
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    valid: List[Dict[str, str]] = []
    skipped: List[Dict[str, str]] = []

    for row in rows:
        source_ok = row.get("_source_exists") == "True"
        class_ok = row.get("_class_exists") == "True"

        if source_ok and class_ok:
            valid.append(row)
        else:
            skipped.append(row)

    if strict and skipped:
        preview = "\n".join(
            f"- {r['dataset']}/{r['project']}/{r['bug_id']}/{r['test_class_fqdn']} "
            f"source_exists={r['_source_exists']} class_exists={r['_class_exists']} "
            f"source_path={r['source_path']}"
            for r in skipped[:20]
        )
        raise FileNotFoundError(
            f"{len(skipped)} target(s) have missing source or class files.\n{preview}"
        )

    return valid, skipped


def apply_sampling(
    rows: List[Dict[str, str]],
    *,
    sample_size: int | None,
    sample_seed: int,
    full: bool,
) -> List[Dict[str, str]]:
    if full:
        return sorted_rows(rows)

    if sample_size is None:
        sample_size = min(10, len(rows))

    if sample_size < 1:
        raise ValueError("--sample-size must be >= 1 when provided.")

    if sample_size >= len(rows):
        return sorted_rows(rows)

    rng = random.Random(sample_seed)

    return sorted_rows(rng.sample(rows, sample_size))


def sorted_rows(rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    return sorted(
        rows,
        key=lambda r: (
            r.get("dataset", ""),
            r.get("project", ""),
            r.get("bug_id", ""),
            r.get("class_name", ""),
            r.get("test_class_fqdn", ""),
        ),
    )


def write_targets_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TARGET_FIELDS)
        writer.writeheader()

        for row in rows:
            writer.writerow({field: row.get(field, "") for field in TARGET_FIELDS})


def write_diagnostics_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = TARGET_FIELDS + INTERNAL_FIELDS

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Base config file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {path}")

    return data


def write_yaml(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def set_nested(config: Dict[str, Any], keys: List[str], value: Any) -> None:
    current = config

    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]

    current[keys[-1]] = value


def build_generated_config(
    *,
    base_config: Dict[str, Any],
    experiment_name: str,
    output_dir: Path,
    targets_csv: Path,
) -> Dict[str, Any]:
    config = deepcopy(base_config)

    set_nested(config, ["experiment", "name"], experiment_name)
    set_nested(config, ["experiment", "output_dir"], str(output_dir))
    set_nested(config, ["dataset", "targets_file"], str(targets_csv))

    return config


def build_run_command(
    *,
    generated_config_path: Path,
    preset: str,
    models: str | None,
    scenarios: str | None,
    iterations: int | None,
    no_llm: bool,
    no_coverage: bool,
    log_level: str | None,
    show_details: bool,
    show_metrics: bool,
    extra_args: List[str],
) -> List[str]:
    command = [
        "testhumanizer",
        "run",
        "--config",
        str(generated_config_path),
        "--preset",
        preset,
    ]

    if models:
        command.extend(["--models", models])

    if scenarios:
        command.extend(["--scenarios", scenarios])

    if iterations is not None:
        command.extend(["--iterations", str(iterations)])

    if no_llm:
        command.append("--no-llm")

    if no_coverage:
        command.append("--no-coverage")

    if log_level:
        command.extend(["--log-level", log_level])

    if show_details:
        command.append("--show-details")

    if show_metrics:
        command.append("--show-metrics")

    command.extend(extra_args)

    return command


def count_by_field(rows: Sequence[Dict[str, str]], field: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}

    for row in rows:
        key = row.get(field, "")
        counts[key] = counts.get(key, 0) + 1

    return dict(sorted(counts.items(), key=lambda item: item[0]))


def preview_rows(rows: Sequence[Dict[str, str]], *, limit: int = 10) -> List[Dict[str, str]]:
    preview: List[Dict[str, str]] = []

    for row in rows[:limit]:
        preview.append(
            {
                "dataset": row.get("dataset", ""),
                "project": row.get("project", ""),
                "bug_id": row.get("bug_id", ""),
                "class_name": row.get("class_name", ""),
                "test_class_fqdn": row.get("test_class_fqdn", ""),
                "source_exists": row.get("_source_exists", ""),
                "class_exists": row.get("_class_exists", ""),
            }
        )

    return preview


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare and optionally run a TestHumanizer experiment from "
            "Defects4J or SF110 JSON metadata."
        )
    )

    parser.add_argument(
        "--dataset",
        required=True,
        choices=["defects4j", "sf110"],
        help="Dataset to prepare.",
    )
    parser.add_argument(
        "--metadata",
        required=True,
        help="Path to Defects4J_base_extracted.json or SF110_base_extracted.json.",
    )
    parser.add_argument(
        "--base-config",
        required=True,
        help="Base TestHumanizer YAML config used as template.",
    )
    parser.add_argument(
        "--output-root",
        default="outputs/reproducibility",
        help="Root directory for generated reproducibility runs.",
    )
    parser.add_argument(
        "--defects4j-sources-root",
        default="/home/e113/Documents/Humanization-Project/HUMANIZATION/DEFECTS4J/SOURCES",
        help="Root directory containing Defects4J SOURCES.",
    )
    parser.add_argument(
        "--sf110-sources-root",
        default="/home/e113/Documents/Humanization-Project/HUMANIZATION/SF-110/SOURCES",
        help="Root directory containing SF110 SOURCES.",
    )
    parser.add_argument(
        "--global-dependencies-dir",
        default="",
        help=(
            "Directory containing extra dependency jars. Disabled by default because "
            "passing a large global jar directory to EvoSuite can make it analyze "
            "unrelated/incompatible Java class versions. Use only when a target "
            "project actually needs extra jars."
        ),
    )
    parser.add_argument(
        "--extra-classpath",
        default="",
        help=(
            "Additional classpath entries separated by the OS path separator. "
            "Use real paths, not wildcards."
        ),
    )
    parser.add_argument(
        "--project-jars-recursive",
        action="store_true",
        help=(
            "Collect project-local jars recursively. By default, only jars directly "
            "under the project root are included."
        ),
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=None,
        help="Number of unique valid targets to sample. Ignored with --full.",
    )
    parser.add_argument(
        "--sample-seed",
        type=int,
        default=42,
        help="Random seed for reproducible sampling.",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Use all unique valid targets instead of sampling.",
    )
    parser.add_argument(
        "--preset",
        default="fast",
        choices=["ready", "fast", "full"],
        help="TestHumanizer preset.",
    )
    parser.add_argument(
        "--models",
        default=None,
        help="Comma-separated model aliases passed to TestHumanizer.",
    )
    parser.add_argument(
        "--scenarios",
        default=None,
        help="Comma-separated scenarios or 'all'.",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=None,
        help="Number of refactoring iterations passed to TestHumanizer.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if any target has a missing .java or .class file.",
    )
    parser.add_argument(
        "--no-run",
        action="store_true",
        help="Only generate targets/config/summary. Do not launch TestHumanizer.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print summary without writing files or launching TestHumanizer.",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Pass --no-llm to TestHumanizer.",
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Pass --no-coverage to TestHumanizer.",
    )
    parser.add_argument(
        "--log-level",
        default=None,
        choices=["quiet", "normal", "verbose"],
        help="Optional TestHumanizer log level override.",
    )
    parser.add_argument(
        "--show-details",
        action="store_true",
        help="Pass --show-details to TestHumanizer.",
    )
    parser.add_argument(
        "--show-metrics",
        action="store_true",
        help="Pass --show-metrics to TestHumanizer.",
    )
    parser.add_argument(
        "--extra-testhumanizer-arg",
        action="append",
        default=[],
        help="Extra argument passed to testhumanizer. Can be repeated.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    metadata_path = Path(args.metadata).expanduser().resolve()
    base_config_path = Path(args.base_config).expanduser().resolve()
    output_root = Path(args.output_root).expanduser().resolve()

    defects4j_sources_root = Path(args.defects4j_sources_root).expanduser().resolve()
    sf110_sources_root = Path(args.sf110_sources_root).expanduser().resolve()

    global_dependencies_dir = (
        None
        if args.global_dependencies_dir == ""
        else Path(args.global_dependencies_dir).expanduser().resolve()
    )

    extra_classpath_entries = split_classpath_entries(args.extra_classpath)

    raw_rows = load_json_records(metadata_path)
    validate_json_rows(raw_rows, dataset=args.dataset)

    unique_rows = deduplicate_rows(raw_rows)

    normalized_rows = normalize_rows(
        unique_rows,
        dataset=args.dataset,
        defects4j_sources_root=defects4j_sources_root,
        sf110_sources_root=sf110_sources_root,
        global_dependencies_dir=global_dependencies_dir,
        extra_classpath_entries=extra_classpath_entries,
        project_jars_recursive=args.project_jars_recursive,
    )

    valid_rows, skipped_rows = filter_missing(
        normalized_rows,
        strict=args.strict,
    )

    if not valid_rows:
        raise RuntimeError(
            "No valid target remains after path resolution. "
            "Check source roots, JSON metadata, and compiled .class files."
        )

    selected_rows = apply_sampling(
        valid_rows,
        sample_size=args.sample_size,
        sample_seed=args.sample_seed,
        full=args.full,
    )

    if not selected_rows:
        raise RuntimeError("No selected target. Check --sample-size and input metadata.")

    dataset_name = args.dataset.lower()

    if args.full:
        run_name = "full"
    else:
        run_name = f"sample_{len(selected_rows)}_seed_{args.sample_seed}"

    experiment_name = f"{dataset_name}_{run_name}"
    run_dir = output_root / dataset_name / run_name

    targets_csv = run_dir / "generated_targets.csv"
    diagnostics_csv = run_dir / "target_diagnostics.csv"
    generated_config_path = run_dir / "generated_config.yaml"
    testhumanizer_output_dir = run_dir / "testhumanizer_outputs"

    summary = {
        "dataset": args.dataset,
        "metadata_path": str(metadata_path),
        "base_config_path": str(base_config_path),
        "raw_rows": len(raw_rows),
        "unique_targets": len(unique_rows),
        "valid_targets": len(valid_rows),
        "skipped_missing_files": len(skipped_rows),
        "selected_targets": len(selected_rows),
        "sample_seed": args.sample_seed,
        "sample_size": args.sample_size,
        "full": args.full,
        "project_counts_selected": count_by_field(selected_rows, "project"),
        "project_counts_valid": count_by_field(valid_rows, "project"),
        "global_dependencies_dir": (
            None if global_dependencies_dir is None else str(global_dependencies_dir)
        ),
        "extra_classpath_entries": extra_classpath_entries,
        "project_jars_recursive": args.project_jars_recursive,
        "run_dir": str(run_dir),
        "targets_csv": str(targets_csv),
        "target_diagnostics_csv": str(diagnostics_csv),
        "generated_config": str(generated_config_path),
        "testhumanizer_output_dir": str(testhumanizer_output_dir),
        "selected_preview": preview_rows(selected_rows, limit=10),
    }

    print(json.dumps(summary, indent=2, ensure_ascii=False))

    if args.dry_run:
        print("\nDry run only. No files written.")
        return 0

    run_dir.mkdir(parents=True, exist_ok=True)

    write_targets_csv(targets_csv, selected_rows)
    write_diagnostics_csv(diagnostics_csv, selected_rows)

    write_json(run_dir / "selected_targets.json", selected_rows)
    write_json(run_dir / "all_valid_targets.json", valid_rows)
    write_json(run_dir / "skipped_missing_files.json", skipped_rows)
    write_json(run_dir / "dataset_summary.json", summary)

    base_config = load_yaml(base_config_path)

    generated_config = build_generated_config(
        base_config=base_config,
        experiment_name=experiment_name,
        output_dir=testhumanizer_output_dir,
        targets_csv=targets_csv,
    )

    write_yaml(generated_config_path, generated_config)

    command = build_run_command(
        generated_config_path=generated_config_path,
        preset=args.preset,
        models=args.models,
        scenarios=args.scenarios,
        iterations=args.iterations,
        no_llm=args.no_llm,
        no_coverage=args.no_coverage,
        log_level=args.log_level,
        show_details=args.show_details,
        show_metrics=args.show_metrics,
        extra_args=args.extra_testhumanizer_arg,
    )

    command_text = shlex.join(command)

    (run_dir / "run_command.txt").write_text(
        command_text + "\n",
        encoding="utf-8",
    )

    print("\nGenerated:")
    print(f"  targets:      {targets_csv}")
    print(f"  diagnostics:  {diagnostics_csv}")
    print(f"  config:       {generated_config_path}")
    print(f"  summary:      {run_dir / 'dataset_summary.json'}")
    print(f"  command:      {run_dir / 'run_command.txt'}")

    print("\nCommand:")
    print(command_text)

    if args.no_run:
        print("\n--no-run enabled. TestHumanizer was not launched.")
        return 0

    if shutil.which("testhumanizer") is None:
        raise RuntimeError(
            "testhumanizer command not found. Activate your environment and run: "
            "pip install -e ."
        )

    completed = subprocess.run(command, check=False)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())


################V1
# from __future__ import annotations

# import argparse
# import csv
# import json
# import os
# import random
# import shutil
# import subprocess
# import sys
# from copy import deepcopy
# from pathlib import Path
# from typing import Any, Dict, Iterable, List, Tuple

# import yaml


# TARGET_FIELDS = [
#     "dataset",
#     "project",
#     "class_name",
#     "bug_id",
#     "source_path",
#     "classpath",
#     "test_class_fqdn",
#     "class_files_dir",
#     "source_files_dir",
# ]


# def load_json_records(path: Path) -> List[Dict[str, Any]]:
#     text = path.read_text(encoding="utf-8").strip()

#     if not text:
#         return []

#     if text.startswith("["):
#         data = json.loads(text)
#         if not isinstance(data, list):
#             raise ValueError(f"Expected a JSON list in {path}")
#         return data

#     rows: List[Dict[str, Any]] = []
#     for line in text.splitlines():
#         line = line.strip()
#         if line:
#             rows.append(json.loads(line))
#     return rows


# def stable_key(row: Dict[str, Any]) -> Tuple[str, str, str, str, str]:
#     return (
#         str(row.get("dataset") or ""),
#         str(row.get("project_name") or ""),
#         str(row.get("bug-id") or ""),
#         str(row.get("class") or ""),
#         str(row.get("fqdn") or ""),
#     )


# def deduplicate_rows(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     seen: set[Tuple[str, str, str, str, str]] = set()
#     unique: List[Dict[str, Any]] = []

#     for row in rows:
#         key = stable_key(row)
#         if key in seen:
#             continue
#         seen.add(key)
#         unique.append(row)

#     return unique


# def fqdn_to_path(fqdn: str) -> Path:
#     return Path(*fqdn.split(".")) if fqdn else Path()


# def make_test_class_fqdn(package_fqdn: str, class_name: str) -> str:
#     if package_fqdn:
#         return f"{package_fqdn}.{class_name}"
#     return class_name


# def collect_jars(directory: Path) -> List[str]:
#     if not directory.exists():
#         return []

#     jars = sorted(directory.glob("*.jar"))
#     return [str(jar) for jar in jars if jar.is_file()]


# def build_classpath(
#     *,
#     class_files_dir: Path,
#     project_root: Path,
#     global_dependencies_dir: Path | None,
# ) -> str:
#     parts: List[str] = [str(class_files_dir)]

#     # Project-local jars, e.g., SF110 project jars such as javex.jar.
#     parts.extend(collect_jars(project_root))

#     # Global dependency jars. Do NOT use dependencies/* because EvoSuite
#     # validates each classpath element literally and rejects wildcard entries.
#     if global_dependencies_dir is not None:
#         parts.extend(collect_jars(global_dependencies_dir))

#     return os.pathsep.join(parts)

# def normalize_defects4j_row(
#     row: Dict[str, Any],
#     *,
#     defects4j_sources_root: Path,
#     global_dependencies_dir: Path | None,
# ) -> Dict[str, str]:
#     project = str(row["project_name"])
#     bug_id = str(row["bug-id"])
#     class_name = str(row["class"])
#     package_fqdn = str(row.get("fqdn") or "")

#     project_bug_root = defects4j_sources_root / project / bug_id
#     source_path = project_bug_root / fqdn_to_path(package_fqdn) / f"{class_name}.java"
#     class_file = project_bug_root / fqdn_to_path(package_fqdn) / f"{class_name}.class"

#     return {
#         "dataset": "Defects4J",
#         "project": project,
#         "class_name": class_name,
#         "bug_id": bug_id,
#         "source_path": str(source_path),
#         "classpath": build_classpath(
#             class_files_dir=project_bug_root,
#             project_root=project_bug_root,
#             global_dependencies_dir=global_dependencies_dir,
#         ),
#         "test_class_fqdn": make_test_class_fqdn(package_fqdn, class_name),
#         "class_files_dir": str(project_bug_root),
#         "source_files_dir": str(project_bug_root),
#         "_source_exists": str(source_path.exists()),
#         "_class_exists": str(class_file.exists()),
#         "_source_token_count": str(row.get("source_token_count", "")),
#         "_source_method_count": str(row.get("source_method_count", "")),
#         "_source_loc": str(row.get("source_loc", "")),
#     }


# def normalize_sf110_row(
#     row: Dict[str, Any],
#     *,
#     sf110_sources_root: Path,
#     global_dependencies_dir: Path | None,
# ) -> Dict[str, str]:
#     project = str(row["project_name"])
#     class_name = str(row["class"])
#     package_fqdn = str(row.get("fqdn") or "")

#     project_root = sf110_sources_root / project
#     source_path = project_root / fqdn_to_path(package_fqdn) / f"{class_name}.java"
#     class_file = project_root / fqdn_to_path(package_fqdn) / f"{class_name}.class"

#     return {
#         "dataset": "SF110",
#         "project": project,
#         "class_name": class_name,
#         "bug_id": "",
#         "source_path": str(source_path),
#         "classpath": build_classpath(
#             class_files_dir=project_root,
#             project_root=project_root,
#             global_dependencies_dir=global_dependencies_dir,
#         ),
#         "test_class_fqdn": make_test_class_fqdn(package_fqdn, class_name),
#         "class_files_dir": str(project_root),
#         "source_files_dir": str(project_root),
#         "_source_exists": str(source_path.exists()),
#         "_class_exists": str(class_file.exists()),
#         "_source_token_count": str(row.get("source_token_count", "")),
#         "_source_method_count": str(row.get("source_method_count", "")),
#         "_source_loc": str(row.get("source_loc", "")),
#     }


# def normalize_rows(
#     rows: List[Dict[str, Any]],
#     *,
#     dataset: str,
#     defects4j_sources_root: Path,
#     sf110_sources_root: Path,
#     global_dependencies_dir: Path | None,
# ) -> List[Dict[str, str]]:
#     normalized: List[Dict[str, str]] = []

#     for row in rows:
#         if dataset.lower() == "defects4j":
#             normalized.append(
#                 normalize_defects4j_row(
#                     row,
#                     defects4j_sources_root=defects4j_sources_root,
#                     global_dependencies_dir=global_dependencies_dir,
#                 )
#             )
#         elif dataset.lower() == "sf110":
#             normalized.append(
#                 normalize_sf110_row(
#                     row,
#                     sf110_sources_root=sf110_sources_root,
#                     global_dependencies_dir=global_dependencies_dir,
#                 )
#             )
#         else:
#             raise ValueError(f"Unsupported dataset: {dataset}")

#     return normalized


# def filter_missing(
#     rows: List[Dict[str, str]],
#     *,
#     strict: bool,
# ) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
#     valid: List[Dict[str, str]] = []
#     skipped: List[Dict[str, str]] = []

#     for row in rows:
#         source_ok = row.get("_source_exists") == "True"
#         class_ok = row.get("_class_exists") == "True"

#         if source_ok and class_ok:
#             valid.append(row)
#         else:
#             skipped.append(row)

#     if strict and skipped:
#         preview = "\n".join(
#             f"- {r['dataset']}/{r['project']}/{r['bug_id']}/{r['test_class_fqdn']} "
#             f"source_exists={r['_source_exists']} class_exists={r['_class_exists']}"
#             for r in skipped[:20]
#         )
#         raise FileNotFoundError(
#             f"{len(skipped)} target(s) have missing source or class files.\n{preview}"
#         )

#     return valid, skipped


# def apply_sampling(
#     rows: List[Dict[str, str]],
#     *,
#     sample_size: int | None,
#     sample_seed: int,
#     full: bool,
# ) -> List[Dict[str, str]]:
#     if full:
#         return rows

#     if sample_size is None:
#         sample_size = min(10, len(rows))

#     if sample_size >= len(rows):
#         return rows

#     rng = random.Random(sample_seed)
#     return sorted(
#         rng.sample(rows, sample_size),
#         key=lambda r: (
#             r["dataset"],
#             r["project"],
#             r["bug_id"],
#             r["class_name"],
#             r["test_class_fqdn"],
#         ),
#     )


# def write_targets_csv(path: Path, rows: List[Dict[str, str]]) -> None:
#     path.parent.mkdir(parents=True, exist_ok=True)

#     with path.open("w", encoding="utf-8", newline="") as f:
#         writer = csv.DictWriter(f, fieldnames=TARGET_FIELDS)
#         writer.writeheader()

#         for row in rows:
#             writer.writerow({field: row.get(field, "") for field in TARGET_FIELDS})


# def write_json(path: Path, data: Any) -> None:
#     path.parent.mkdir(parents=True, exist_ok=True)
#     path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# def load_yaml(path: Path) -> Dict[str, Any]:
#     with path.open("r", encoding="utf-8") as f:
#         data = yaml.safe_load(f)
#     if not isinstance(data, dict):
#         raise ValueError(f"Expected YAML mapping in {path}")
#     return data


# def write_yaml(path: Path, data: Dict[str, Any]) -> None:
#     path.parent.mkdir(parents=True, exist_ok=True)
#     with path.open("w", encoding="utf-8") as f:
#         yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


# def set_nested(config: Dict[str, Any], keys: List[str], value: Any) -> None:
#     current = config
#     for key in keys[:-1]:
#         if key not in current or not isinstance(current[key], dict):
#             current[key] = {}
#         current = current[key]
#     current[keys[-1]] = value


# def build_generated_config(
#     *,
#     base_config: Dict[str, Any],
#     experiment_name: str,
#     output_dir: Path,
#     targets_csv: Path,
# ) -> Dict[str, Any]:
#     config = deepcopy(base_config)

#     set_nested(config, ["experiment", "name"], experiment_name)
#     set_nested(config, ["experiment", "output_dir"], str(output_dir))
#     set_nested(config, ["dataset", "targets_file"], str(targets_csv))

#     return config


# def build_run_command(
#     *,
#     generated_config_path: Path,
#     preset: str,
#     models: str | None,
#     scenarios: str | None,
#     iterations: int | None,
#     no_llm: bool,
#     no_coverage: bool,
#     extra_args: List[str],
# ) -> List[str]:
#     command = [
#         "testhumanizer",
#         "run",
#         "--config",
#         str(generated_config_path),
#         "--preset",
#         preset,
#     ]

#     if models:
#         command.extend(["--models", models])

#     if scenarios:
#         command.extend(["--scenarios", scenarios])

#     if iterations is not None:
#         command.extend(["--iterations", str(iterations)])

#     if no_llm:
#         command.append("--no-llm")

#     if no_coverage:
#         command.append("--no-coverage")

#     command.extend(extra_args)

#     return command


# def parse_args() -> argparse.Namespace:
#     parser = argparse.ArgumentParser(
#         description="Prepare and optionally run a TestHumanizer experiment from Defects4J or SF110 JSON metadata."
#     )

#     parser.add_argument(
#         "--dataset",
#         required=True,
#         choices=["defects4j", "sf110"],
#         help="Dataset to prepare.",
#     )
#     parser.add_argument(
#         "--metadata",
#         required=True,
#         help="Path to Defects4J_base_extracted.json or SF110_base_extracted.json.",
#     )
#     parser.add_argument(
#         "--base-config",
#         required=True,
#         help="Base TestHumanizer YAML config used as template.",
#     )
#     parser.add_argument(
#         "--output-root",
#         default="outputs/reproducibility",
#         help="Root directory for generated reproducibility runs.",
#     )
#     parser.add_argument(
#         "--defects4j-sources-root",
#         default="/home/e113/Documents/Humanization-Project/HUMANIZATION/DEFECTS4J/SOURCES",
#         help="Root directory containing Defects4J SOURCES.",
#     )
#     parser.add_argument(
#         "--sf110-sources-root",
#         default="/home/e113/Documents/Humanization-Project/HUMANIZATION/SF-110/SOURCES",
#         help="Root directory containing SF110 SOURCES.",
#     )
    
#     parser.add_argument(
#         "--global-dependencies-dir",
#         default="",
#         help=(
#             "Directory containing extra dependency jars. "
#             "Disabled by default because passing a large global jar directory to EvoSuite "
#             "can make it analyze incompatible Java class versions. "
#             "Use only when a target project actually needs extra jars."
#         ),
#     )
#     parser.add_argument(
#         "--sample-size",
#         type=int,
#         default=None,
#         help="Number of unique targets to sample. Ignored with --full.",
#     )
#     parser.add_argument(
#         "--sample-seed",
#         type=int,
#         default=42,
#         help="Random seed for reproducible sampling.",
#     )
#     parser.add_argument(
#         "--full",
#         action="store_true",
#         help="Use all unique valid targets instead of sampling.",
#     )
#     parser.add_argument(
#         "--preset",
#         default="fast",
#         choices=["ready", "fast", "full"],
#         help="TestHumanizer preset.",
#     )
#     parser.add_argument(
#         "--models",
#         default=None,
#         help="Comma-separated model aliases passed to TestHumanizer.",
#     )
#     parser.add_argument(
#         "--scenarios",
#         default=None,
#         help="Comma-separated scenarios or 'all'.",
#     )
#     parser.add_argument(
#         "--iterations",
#         type=int,
#         default=None,
#         help="Number of refactoring iterations passed to TestHumanizer.",
#     )
#     parser.add_argument(
#         "--strict",
#         action="store_true",
#         help="Fail if any selected target has a missing .java or .class file.",
#     )
#     parser.add_argument(
#         "--no-run",
#         action="store_true",
#         help="Only generate targets/config/summary. Do not launch TestHumanizer.",
#     )
#     parser.add_argument(
#         "--dry-run",
#         action="store_true",
#         help="Print summary without writing files or launching TestHumanizer.",
#     )
#     parser.add_argument(
#         "--no-llm",
#         action="store_true",
#         help="Pass --no-llm to TestHumanizer.",
#     )
#     parser.add_argument(
#         "--no-coverage",
#         action="store_true",
#         help="Pass --no-coverage to TestHumanizer.",
#     )
#     parser.add_argument(
#         "--extra-testhumanizer-arg",
#         action="append",
#         default=[],
#         help="Extra argument passed to testhumanizer. Can be repeated.",
#     )

#     return parser.parse_args()


# def main() -> int:
#     args = parse_args()

#     metadata_path = Path(args.metadata).expanduser().resolve()
#     base_config_path = Path(args.base_config).expanduser().resolve()
#     output_root = Path(args.output_root).expanduser().resolve()

#     defects4j_sources_root = Path(args.defects4j_sources_root).expanduser().resolve()
#     sf110_sources_root = Path(args.sf110_sources_root).expanduser().resolve()

#     global_dependencies_dir = (
#         None
#         if args.global_dependencies_dir == ""
#         else Path(args.global_dependencies_dir).expanduser().resolve()
#     )

#     raw_rows = load_json_records(metadata_path)
#     unique_rows = deduplicate_rows(raw_rows)

#     normalized_rows = normalize_rows(
#         unique_rows,
#         dataset=args.dataset,
#         defects4j_sources_root=defects4j_sources_root,
#         sf110_sources_root=sf110_sources_root,
#         global_dependencies_dir=global_dependencies_dir,
#     )

#     valid_rows, skipped_rows = filter_missing(
#         normalized_rows,
#         strict=args.strict,
#     )

#     selected_rows = apply_sampling(
#         valid_rows,
#         sample_size=args.sample_size,
#         sample_seed=args.sample_seed,
#         full=args.full,
#     )

#     dataset_name = args.dataset.lower()
#     if args.full:
#         run_name = "full"
#     else:
#         run_name = f"sample_{len(selected_rows)}_seed_{args.sample_seed}"

#     experiment_name = f"{dataset_name}_{run_name}"
#     run_dir = output_root / dataset_name / run_name
#     targets_csv = run_dir / "generated_targets.csv"
#     generated_config_path = run_dir / "generated_config.yaml"
#     testhumanizer_output_dir = run_dir / "testhumanizer_outputs"

#     summary = {
#         "dataset": args.dataset,
#         "metadata_path": str(metadata_path),
#         "base_config_path": str(base_config_path),
#         "raw_rows": len(raw_rows),
#         "unique_targets": len(unique_rows),
#         "valid_targets": len(valid_rows),
#         "skipped_missing_files": len(skipped_rows),
#         "selected_targets": len(selected_rows),
#         "sample_seed": args.sample_seed,
#         "sample_size": args.sample_size,
#         "full": args.full,
#         "run_dir": str(run_dir),
#         "targets_csv": str(targets_csv),
#         "generated_config": str(generated_config_path),
#         "testhumanizer_output_dir": str(testhumanizer_output_dir),
#     }

#     print(json.dumps(summary, indent=2))

#     if args.dry_run:
#         print("\nDry run only. No files written.")
#         return 0

#     run_dir.mkdir(parents=True, exist_ok=True)

#     write_targets_csv(targets_csv, selected_rows)
#     write_json(run_dir / "selected_targets.json", selected_rows)
#     write_json(run_dir / "skipped_missing_files.json", skipped_rows)
#     write_json(run_dir / "dataset_summary.json", summary)

#     base_config = load_yaml(base_config_path)
#     generated_config = build_generated_config(
#         base_config=base_config,
#         experiment_name=experiment_name,
#         output_dir=testhumanizer_output_dir,
#         targets_csv=targets_csv,
#     )
#     write_yaml(generated_config_path, generated_config)

#     command = build_run_command(
#         generated_config_path=generated_config_path,
#         preset=args.preset,
#         models=args.models,
#         scenarios=args.scenarios,
#         iterations=args.iterations,
#         no_llm=args.no_llm,
#         no_coverage=args.no_coverage,
#         extra_args=args.extra_testhumanizer_arg,
#     )

#     (run_dir / "run_command.txt").write_text(
#         " ".join(command) + "\n",
#         encoding="utf-8",
#     )

#     print("\nGenerated:")
#     print(f"  targets: {targets_csv}")
#     print(f"  config:  {generated_config_path}")
#     print(f"  summary: {run_dir / 'dataset_summary.json'}")

#     print("\nCommand:")
#     print(" ".join(command))

#     if args.no_run:
#         print("\n--no-run enabled. TestHumanizer was not launched.")
#         return 0

#     if shutil.which("testhumanizer") is None:
#         raise RuntimeError(
#             "testhumanizer command not found. Activate your environment and run: pip install -e ."
#         )

#     completed = subprocess.run(command, check=False)
#     return int(completed.returncode)


# if __name__ == "__main__":
#     raise SystemExit(main())
