from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console

from testhumanizer.metrics.complexity.pmd_runner import (
    PMDRunner,
    parse_pmd_cyclomatic_report,
)


console = Console()


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


class PMDComplexityEvaluator:
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

        self.complexity_config = config.get("metrics", {}).get("complexity", {})
        self.pmd_config = self.complexity_config.get("pmd", {})

        self.runner = PMDRunner(
            pmd_dir=self.pmd_config.get("pmd_dir", "tools/pmd-bin-7.0.0-rc4"),
            pmd_bin=self.pmd_config.get("pmd_bin", "bin/pmd"),
            ruleset=self.pmd_config.get("ruleset", "cyclomatic_ruleset.xml"),
            timeout_seconds=int(self.pmd_config.get("timeout_seconds", 120)),
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

        output_root = self.output_dir / "06_metrics" / "complexity" / "pmd"

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
            "pmd_ok",
            "pmd_returncode",
            "pmd_report_xml",
            "total_cyclomatic_complexity",
            "loc",
            "number_of_methods",
            "comment_density",
            "maintainability_index",
            "method_complexities",
            "error",
            "stdout",
            "stderr",
        ]

        write_csv(output_root / "pmd_complexity_results.csv", rows, detailed_fields)
        write_jsonl(output_root / "pmd_complexity_results.jsonl", rows)

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
            "average_maintainability_index",
            "median_maintainability_index",
            "min_maintainability_index",
            "max_maintainability_index",
            "average_cyclomatic_complexity",
            "median_cyclomatic_complexity",
            "min_cyclomatic_complexity",
            "max_cyclomatic_complexity",
            "total_cyclomatic_complexity",
            "total_loc",
        ]

        write_csv(output_root / "pmd_complexity_summary.csv", summary_rows, summary_fields)
        write_jsonl(output_root / "pmd_complexity_summary.jsonl", summary_rows)

        console.print(
            f"[bold green]PMD complexity evaluation completed.[/bold green] "
            f"rows={len(rows)}"
        )

    def _evaluate_original(self, original_suites_csv: str | Path) -> List[Dict[str, Any]]:
        suites = read_csv(original_suites_csv)
        rows: List[Dict[str, Any]] = []

        for suite in suites:
            java_file = suite.get("test_file", "")
            output_xml = self._report_path(
                suite_kind="original",
                dataset=suite.get("dataset", ""),
                project=suite.get("project", ""),
                class_name=suite.get("class_name", ""),
                testsuite_id=suite.get("testsuite_id", ""),
                scenario_id="Original",
                model_alias="original",
                iteration="",
            )

            row = self._run_one(
                suite_id=f"{suite['dataset']}_{suite['project']}_{suite['class_name']}_{suite.get('bug_id') or 'NA'}_{suite['testsuite_id']}_original",
                suite_kind="original",
                dataset=suite.get("dataset", ""),
                project=suite.get("project", ""),
                class_name=suite.get("class_name", ""),
                bug_id=suite.get("bug_id", ""),
                testsuite_id=suite.get("testsuite_id", ""),
                scenario="original",
                scenario_id="Original",
                iteration="",
                model_alias="original",
                provider="",
                model="",
                java_file=java_file,
                output_xml=output_xml,
            )

            rows.append(row)

            console.print(
                f"[cyan]PMD[/cyan] "
                f"original/{suite.get('class_name', '')}/{suite.get('testsuite_id', '')} "
                f"complexity={row['total_cyclomatic_complexity']} "
                f"mi={row['maintainability_index']} ok={row['pmd_ok']}"
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

            output_xml = self._report_path(
                suite_kind="refactored",
                dataset=suite.get("dataset", ""),
                project=suite.get("project", ""),
                class_name=suite.get("class_name", ""),
                testsuite_id=suite.get("testsuite_id", ""),
                scenario_id=suite.get("scenario_id", ""),
                model_alias=suite.get("model_alias", ""),
                iteration=suite.get("iteration", ""),
            )

            row = self._run_one(
                suite_id=suite.get("id", ""),
                suite_kind="refactored",
                dataset=suite.get("dataset", ""),
                project=suite.get("project", ""),
                class_name=suite.get("class_name", ""),
                bug_id=suite.get("bug_id", ""),
                testsuite_id=suite.get("testsuite_id", ""),
                scenario=suite.get("scenario", ""),
                scenario_id=suite.get("scenario_id", ""),
                iteration=suite.get("iteration", ""),
                model_alias=suite.get("model_alias", ""),
                provider=suite.get("provider", ""),
                model=suite.get("model", ""),
                java_file=java_file,
                output_xml=output_xml,
            )

            rows.append(row)

            console.print(
                f"[cyan]PMD[/cyan] "
                f"{suite.get('class_name', '')}/{suite.get('scenario_id', '')}/"
                f"{suite.get('model_alias', '')}/iter_{suite.get('iteration', '')} "
                f"complexity={row['total_cyclomatic_complexity']} "
                f"mi={row['maintainability_index']} ok={row['pmd_ok']}"
            )

        return rows

    def _run_one(
        self,
        *,
        suite_id: str,
        suite_kind: str,
        dataset: str,
        project: str,
        class_name: str,
        bug_id: str,
        testsuite_id: str,
        scenario: str,
        scenario_id: str,
        iteration: str,
        model_alias: str,
        provider: str,
        model: str,
        java_file: str,
        output_xml: Path,
    ) -> Dict[str, Any]:
        run_result = self.runner.run_file(
            java_file=java_file,
            output_xml=output_xml,
        )

        metrics = parse_pmd_cyclomatic_report(
            report_xml=run_result.report_xml,
            java_file=java_file,
        )

        return {
            "id": suite_id,
            "suite_kind": suite_kind,
            "dataset": dataset,
            "project": project,
            "class_name": class_name,
            "bug_id": bug_id,
            "testsuite_id": testsuite_id,
            "scenario": scenario,
            "scenario_id": scenario_id,
            "iteration": iteration,
            "model_alias": model_alias,
            "provider": provider,
            "model": model,
            "java_file": java_file,
            "pmd_ok": run_result.ok,
            "pmd_returncode": run_result.returncode,
            "pmd_report_xml": str(run_result.report_xml),
            "total_cyclomatic_complexity": metrics.total_cyclomatic_complexity,
            "loc": metrics.loc,
            "number_of_methods": metrics.number_of_methods,
            "comment_density": metrics.comment_density,
            "maintainability_index": metrics.maintainability_index,
            "method_complexities": ";".join(str(x) for x in metrics.complexities),
            "error": run_result.error,
            "stdout": run_result.stdout,
            "stderr": run_result.stderr,
        }

    def _report_path(
        self,
        *,
        suite_kind: str,
        dataset: str,
        project: str,
        class_name: str,
        testsuite_id: str,
        scenario_id: str,
        model_alias: str,
        iteration: str,
    ) -> Path:
        safe_iter = f"iter_{iteration}" if iteration else "iter_NA"

        return (
            self.output_dir
            / "06_metrics"
            / "complexity"
            / "pmd"
            / "reports"
            / suite_kind
            / model_alias
            / dataset
            / project
            / class_name
            / testsuite_id
            / scenario_id
            / safe_iter
            / f"{class_name}.xml"
        )

    def _summarize(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        grouped: Dict[tuple, List[Dict[str, Any]]] = {}

        for row in rows:
            key = (
                row.get("suite_kind", ""),
                row.get("dataset", ""),
                row.get("project", ""),
                row.get("class_name", ""),
                row.get("scenario_id", ""),
                row.get("model_alias", ""),
            )
            grouped.setdefault(key, []).append(row)

        summary_rows: List[Dict[str, Any]] = []

        for key, group_rows in grouped.items():
            suite_kind, dataset, project, class_name, scenario_id, model_alias = key

            ok_rows = [row for row in group_rows if str(row.get("pmd_ok")) == "True"]

            complexities = []
            maintainability_indices = []
            total_loc = 0

            for row in ok_rows:
                try:
                    complexities.append(float(row.get("total_cyclomatic_complexity", 0)))
                except (TypeError, ValueError):
                    pass

                try:
                    maintainability_indices.append(float(row.get("maintainability_index", 0)))
                except (TypeError, ValueError):
                    pass

                try:
                    total_loc += int(float(row.get("loc", 0)))
                except (TypeError, ValueError):
                    pass

            summary_rows.append(
                {
                    "suite_kind": suite_kind,
                    "dataset": dataset,
                    "project": project,
                    "class_name": class_name,
                    "scenario_id": scenario_id,
                    "model_alias": model_alias,
                    "total_files": len(group_rows),
                    "ok_files": len(ok_rows),
                    "average_maintainability_index": statistics.mean(maintainability_indices) if maintainability_indices else "",
                    "median_maintainability_index": statistics.median(maintainability_indices) if maintainability_indices else "",
                    "min_maintainability_index": min(maintainability_indices) if maintainability_indices else "",
                    "max_maintainability_index": max(maintainability_indices) if maintainability_indices else "",
                    "average_cyclomatic_complexity": statistics.mean(complexities) if complexities else "",
                    "median_cyclomatic_complexity": statistics.median(complexities) if complexities else "",
                    "min_cyclomatic_complexity": min(complexities) if complexities else "",
                    "max_cyclomatic_complexity": max(complexities) if complexities else "",
                    "total_cyclomatic_complexity": sum(complexities) if complexities else "",
                    "total_loc": total_loc,
                }
            )

        return summary_rows
