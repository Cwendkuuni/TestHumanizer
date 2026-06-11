from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console

from testhumanizer.metrics.readability.scalabrino import ScalabrinoReadabilityRunner


console = Console()


def read_csv(path: str | Path) -> List[Dict[str, str]]:
    p = Path(path).expanduser().resolve()
    with p.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_jsonl(path: str | Path) -> List[Dict[str, Any]]:
    p = Path(path).expanduser().resolve()
    rows = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


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


class ReadabilityEvaluator:
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
        self.readability_config = config.get("metrics", {}).get("readability", {})

        self.runner = ScalabrinoReadabilityRunner(
            rsm_dir=self.readability_config.get("rsm_dir", "tools/Readability-model"),
            rsm_jar=self.readability_config.get("rsm_jar", "rsm.jar"),
            java_cmd=self.readability_config.get("java_cmd", "java"),
            timeout_seconds=int(self.readability_config.get("timeout_seconds", 60)),
            project_root=self.project_root,
        )

    def evaluate(
        self,
        *,
        original_suites_csv: str | Path,
        extracted_suites_csv: str | Path,
    ) -> None:
        rows: List[Dict[str, Any]] = []

        rows.extend(self._evaluate_original(original_suites_csv))
        rows.extend(self._evaluate_refactored(extracted_suites_csv))

        output_root = self.output_dir / "06_metrics" / "readability"

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
            "readability_ok",
            "readability_score",
            "returncode",
            "error",
            "stdout",
            "stderr",
        ]

        write_csv(output_root / "readability_results.csv", rows, detailed_fields)
        write_jsonl(output_root / "readability_results.jsonl", rows)

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
            "average_readability",
            "median_readability",
            "min_readability",
            "max_readability",
            "total_readability",
        ]

        write_csv(output_root / "readability_summary.csv", summary_rows, summary_fields)
        write_jsonl(output_root / "readability_summary.jsonl", summary_rows)

        console.print(
            f"[bold green]Readability evaluation completed.[/bold green] rows={len(rows)}"
        )

    def _evaluate_original(self, original_suites_csv: str | Path) -> List[Dict[str, Any]]:
        suites = read_csv(original_suites_csv)
        rows: List[Dict[str, Any]] = []

        for suite in suites:
            java_file = suite.get("test_file", "")
            result = self.runner.analyze_file(java_file)

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
                "readability_ok": result.ok,
                "readability_score": result.score if result.score is not None else "",
                "returncode": result.returncode,
                "error": result.error,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

            rows.append(row)

            console.print(
                f"[cyan]Readability[/cyan] "
                f"original/{suite.get('class_name', '')}/{suite.get('testsuite_id', '')} "
                f"score={row['readability_score']} ok={result.ok}"
            )

        return rows

    def _evaluate_refactored(self, extracted_suites_csv: str | Path) -> List[Dict[str, Any]]:
        suites = read_csv(extracted_suites_csv)
        rows: List[Dict[str, Any]] = []

        for suite in suites:
            status = suite.get("extraction_status", "")
            if status not in {"ok", "ok_no_fence", "ok_without_java_markers"}:
                continue

            java_file = suite.get("refactored_test_file", "")
            result = self.runner.analyze_file(java_file)

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
                "readability_ok": result.ok,
                "readability_score": result.score if result.score is not None else "",
                "returncode": result.returncode,
                "error": result.error,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

            rows.append(row)

            console.print(
                f"[cyan]Readability[/cyan] "
                f"{suite.get('class_name', '')}/{suite.get('scenario_id', '')}/"
                f"{suite.get('model_alias', '')}/iter_{suite.get('iteration', '')} "
                f"score={row['readability_score']} ok={result.ok}"
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
                value = float(row.get("readability_score", ""))
            except (TypeError, ValueError):
                continue

            grouped.setdefault(key, []).append(value)

        summary_rows: List[Dict[str, Any]] = []

        for key, values in grouped.items():
            suite_kind, dataset, project, class_name, scenario_id, model_alias = key

            total_files = counts.get(key, 0)
            ok_files = len(values)

            summary_rows.append(
                {
                    "suite_kind": suite_kind,
                    "dataset": dataset,
                    "project": project,
                    "class_name": class_name,
                    "scenario_id": scenario_id,
                    "model_alias": model_alias,
                    "total_files": total_files,
                    "ok_files": ok_files,
                    "average_readability": statistics.mean(values) if values else "",
                    "median_readability": statistics.median(values) if values else "",
                    "min_readability": min(values) if values else "",
                    "max_readability": max(values) if values else "",
                    "total_readability": sum(values) if values else "",
                }
            )

        return summary_rows
