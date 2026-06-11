from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path
from typing import Any, Dict, List

from testhumanizer.metrics.complexity.cctr import analyze_java_file
from testhumanizer.utils.logging import THLogger


def read_csv(path: str | Path) -> List[Dict[str, str]]:
    p = Path(path).expanduser().resolve()
    with p.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: str | Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    p = Path(path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_jsonl(path: str | Path, rows: List[Dict[str, Any]]) -> None:
    p = Path(path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


class CCTRComplexityEvaluator:
    def __init__(
        self,
        *,
        output_dir: str | Path,
        config: Dict[str, Any],
        project_root: str | Path,
    ) -> None:
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.config = config
        self.project_root = Path(project_root).expanduser().resolve()
        self.log = THLogger(config)

    def evaluate(
        self,
        *,
        original_suites_csv: str | Path,
        extracted_suites_csv: str | Path,
    ) -> None:
        original_rows = self._evaluate_original(original_suites_csv)
        refactored_rows = self._evaluate_refactored(extracted_suites_csv)

        rows: List[Dict[str, Any]] = []
        rows.extend(original_rows)
        rows.extend(refactored_rows)

        output_root = self.output_dir / "06_metrics" / "complexity" / "cctr"

        detailed_fields = [
            "id",
            "suite_kind",
            "dataset",
            "project",
            "class_name",
            "bug_id",
            "testsuite_id",
            "scenario",
            "scenario_id",
            "iteration",
            "model_alias",
            "provider",
            "model",
            "java_file",
            "cctr_ok",
            "cognitive_complexity",
            "error",
        ]

        write_csv(output_root / "cctr_results.csv", rows, detailed_fields)
        write_jsonl(output_root / "cctr_results.jsonl", rows)

        summary_rows = self._summarize(rows)

        summary_fields = [
            "suite_kind",
            "dataset",
            "project",
            "class_name",
            "scenario_id",
            "model_alias",
            "total_files",
            "ok_files",
            "average_cognitive_complexity",
            "median_cognitive_complexity",
            "min_cognitive_complexity",
            "max_cognitive_complexity",
            "total_cognitive_complexity",
        ]

        write_csv(output_root / "cctr_summary.csv", summary_rows, summary_fields)
        write_jsonl(output_root / "cctr_summary.jsonl", summary_rows)

        ok_rows = [row for row in rows if str(row.get("cctr_ok")) == "True"]
        failed_rows = len(rows) - len(ok_rows)

        complexities: List[float] = []
        for row in ok_rows:
            try:
                complexities.append(float(row.get("cognitive_complexity", "")))
            except (TypeError, ValueError):
                continue

        mean_complexity = statistics.mean(complexities) if complexities else 0.0
        min_complexity = min(complexities) if complexities else 0.0
        max_complexity = max(complexities) if complexities else 0.0

        self.log.success(
            f"CCTR cognitive complexity evaluation completed: "
            f"rows={len(rows)}, ok={len(ok_rows)}/{len(rows)}, "
            f"failed={failed_rows}, "
            f"mean={mean_complexity:.2f}, "
            f"min={min_complexity:.0f}, "
            f"max={max_complexity:.0f}."
        )

    def _evaluate_original(self, original_suites_csv: str | Path) -> List[Dict[str, Any]]:
        suites = read_csv(original_suites_csv)
        rows: List[Dict[str, Any]] = []

        for suite in suites:
            java_file = suite.get("test_file", "")
            result = analyze_java_file(java_file)

            row = {
                "id": f"{suite['dataset']}_{suite['project']}_{suite['class_name']}_{suite.get('bug_id') or 'NA'}_{suite['testsuite_id']}_original",
                "suite_kind": "original",
                "dataset": suite.get("dataset", ""),
                "project": suite.get("project", ""),
                "class_name": suite.get("class_name", ""),
                "bug_id": suite.get("bug_id", ""),
                "testsuite_id": suite.get("testsuite_id", ""),
                "scenario": "original",
                "scenario_id": "Original",
                "iteration": "",
                "model_alias": "original",
                "provider": "",
                "model": "",
                "java_file": java_file,
                "cctr_ok": result.ok,
                "cognitive_complexity": result.complexity if result.complexity is not None else "",
                "error": result.error,
            }

            rows.append(row)

            self.log.metric(
                f"CCTR original/{suite.get('class_name', '')}/"
                f"{suite.get('testsuite_id', '')} "
                f"complexity={row['cognitive_complexity']} ok={result.ok}"
            )

        self.log.detail(f"CCTR original suites evaluated: {len(rows)} files.")
        return rows

    def _evaluate_refactored(self, extracted_suites_csv: str | Path) -> List[Dict[str, Any]]:
        suites = read_csv(extracted_suites_csv)
        rows: List[Dict[str, Any]] = []
        skipped = 0

        for suite in suites:
            status = suite.get("extraction_status", "")
            if status not in {"ok", "ok_no_fence", "ok_without_java_markers"}:
                skipped += 1
                continue

            java_file = suite.get("refactored_test_file", "")
            result = analyze_java_file(java_file)

            row = {
                "id": suite.get("id", ""),
                "suite_kind": "refactored",
                "dataset": suite.get("dataset", ""),
                "project": suite.get("project", ""),
                "class_name": suite.get("class_name", ""),
                "bug_id": suite.get("bug_id", ""),
                "testsuite_id": suite.get("testsuite_id", ""),
                "scenario": suite.get("scenario", ""),
                "scenario_id": suite.get("scenario_id", ""),
                "iteration": suite.get("iteration", ""),
                "model_alias": suite.get("model_alias", ""),
                "provider": suite.get("provider", ""),
                "model": suite.get("model", ""),
                "java_file": java_file,
                "cctr_ok": result.ok,
                "cognitive_complexity": result.complexity if result.complexity is not None else "",
                "error": result.error,
            }

            rows.append(row)

            self.log.metric(
                f"CCTR {suite.get('class_name', '')}/"
                f"{suite.get('scenario_id', '')}/"
                f"{suite.get('model_alias', '')}/iter_{suite.get('iteration', '')} "
                f"complexity={row['cognitive_complexity']} ok={result.ok}"
            )

        self.log.detail(
            f"CCTR refactored suites evaluated: {len(rows)} files, skipped={skipped}."
        )
        return rows

    def _summarize(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        grouped: Dict[tuple, List[float]] = {}
        counts: Dict[tuple, int] = {}

        for row in rows:
            key = (
                row.get("suite_kind", ""),
                row.get("dataset", ""),
                row.get("project", ""),
                row.get("class_name", ""),
                row.get("scenario_id", ""),
                row.get("model_alias", ""),
            )

            counts[key] = counts.get(key, 0) + 1

            try:
                value = float(row.get("cognitive_complexity", ""))
            except (TypeError, ValueError):
                continue

            grouped.setdefault(key, []).append(value)

        summary_rows: List[Dict[str, Any]] = []

        for key, values in grouped.items():
            suite_kind, dataset, project, class_name, scenario_id, model_alias = key

            summary_rows.append(
                {
                    "suite_kind": suite_kind,
                    "dataset": dataset,
                    "project": project,
                    "class_name": class_name,
                    "scenario_id": scenario_id,
                    "model_alias": model_alias,
                    "total_files": counts.get(key, 0),
                    "ok_files": len(values),
                    "average_cognitive_complexity": statistics.mean(values) if values else "",
                    "median_cognitive_complexity": statistics.median(values) if values else "",
                    "min_cognitive_complexity": min(values) if values else "",
                    "max_cognitive_complexity": max(values) if values else "",
                    "total_cognitive_complexity": sum(values) if values else "",
                }
            )

        return summary_rows
