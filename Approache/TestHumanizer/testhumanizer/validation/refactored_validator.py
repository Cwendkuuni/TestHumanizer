from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console

from testhumanizer.validation.compilation import JavaTestCompiler
from testhumanizer.validation.evosuite_patch import create_coverage_friendly_test_copy
from testhumanizer.validation.jacoco import JaCoCoRunner
from testhumanizer.validation.java_utils import infer_fqdn
from testhumanizer.validation.junit_runner import JUnitRunner

from testhumanizer.utils.logging import THLogger

console = Console()


def _read_csv(path: str | Path) -> List[Dict[str, str]]:
    p = Path(path).expanduser().resolve()
    with p.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _write_csv(path: str | Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    p = Path(path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _write_jsonl(path: str | Path, rows: List[Dict[str, Any]]) -> None:
    p = Path(path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


class RefactoredSuiteValidator:
    def __init__(self, config: Dict[str, Any], project_root: str | Path, output_dir: str | Path) -> None:
        self.config = config
        self.project_root = Path(project_root).expanduser().resolve()
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.log = THLogger(config)

    def validate(self, extracted_suites_csv: str | Path) -> None:
        suites = _read_csv(extracted_suites_csv)

        validation_root = self.output_dir / "05_validation" / "refactored"
        compiled_root = validation_root / "compiled_tests"

        compilation_rows: List[Dict[str, Any]] = []
        junit_rows: List[Dict[str, Any]] = []
        coverage_rows: List[Dict[str, Any]] = []

        for suite in suites:
            if suite.get("extraction_status") not in {"ok", "ok_no_fence", "ok_without_java_markers"}:
                continue

            test_file = suite.get("refactored_test_file", "")
            scaffolding_file = suite.get("scaffolding_file", "") or None

            if not test_file or not Path(test_file).exists():
                compilation_rows.append(
                    self._compilation_error_row(
                        suite,
                        test_file=test_file,
                        stderr="Missing refactored test file.",
                    )
                )
                continue

            target_classpath = self._find_target_classpath(
                dataset=suite["dataset"],
                project=suite["project"],
                class_name=suite["class_name"],
                bug_id=suite.get("bug_id", ""),
            )

            compiled_tests_dir = (
                compiled_root
                / suite["model_alias"]
                / suite["dataset"]
                / suite["project"]
                / suite["class_name"]
                / suite["testsuite_id"]
                / suite["scenario_id"]
                / f"iter_{suite['iteration']}"
            )

            compiler = JavaTestCompiler(
                javac_cmd=self.config["validation"]["compilation"].get("javac_cmd", "javac"),
                project_classpath=target_classpath,
                extra_classpath=self.config["validation"]["compilation"].get("extra_classpath", []),
                base_dir=self.project_root,
            )

            compilation = compiler.compile_tests(
                test_file=test_file,
                scaffolding_file=scaffolding_file,
                output_dir=compiled_tests_dir,
            )

            test_class_fqdn = infer_fqdn(test_file)

            compilation_row = {
                "id": suite["id"],
                "dataset": suite["dataset"],
                "project": suite["project"],
                "class_name": suite["class_name"],
                "bug_id": suite.get("bug_id", ""),
                "testsuite_id": suite["testsuite_id"],
                "scenario": suite["scenario"],
                "scenario_id": suite["scenario_id"],
                "iteration": suite["iteration"],
                "model_alias": suite["model_alias"],
                "provider": suite["provider"],
                "model": suite["model"],
                "test_file": test_file,
                "compiled": compilation.ok,
                "returncode": compilation.returncode,
                "compiled_tests_dir": str(compilation.output_dir),
                "test_class_fqdn": test_class_fqdn,
                "stdout": compilation.stdout,
                "stderr": compilation.stderr,
            }
            compilation_rows.append(compilation_row)

            if not compilation.ok:
                # console.print(
                #     f"[red]Refactored compile failed[/red] "
                #     f"{suite['class_name']}/{suite['scenario_id']}/"
                #     f"{suite['model_alias']}/iter_{suite['iteration']}"
                # )
                self.log.warning(
                    f"Refactored compile failed: "
                    f"{suite['class_name']}/{suite['scenario_id']}/"
                    f"{suite['model_alias']}/iter_{suite['iteration']}"
                )
                continue

            if not self.config["validation"]["junit"].get("enabled", False):
                continue

            runner = JUnitRunner(
                java_cmd=self.config["validation"]["junit"].get("java_cmd", "java"),
                java_memory=self.config["validation"]["junit"].get("java_memory", "-Xmx512M"),
                project_classpath=target_classpath,
                compiled_tests_dir=compiled_tests_dir,
                extra_classpath=self.config["validation"]["junit"].get("extra_classpath", []),
                base_dir=self.project_root,
            )

            junit = runner.run(test_class_fqdn)

            junit_row = {
                "id": suite["id"],
                "dataset": suite["dataset"],
                "project": suite["project"],
                "class_name": suite["class_name"],
                "bug_id": suite.get("bug_id", ""),
                "testsuite_id": suite["testsuite_id"],
                "scenario": suite["scenario"],
                "scenario_id": suite["scenario_id"],
                "iteration": suite["iteration"],
                "model_alias": suite["model_alias"],
                "provider": suite["provider"],
                "model": suite["model"],
                "test_class_fqdn": test_class_fqdn,
                "junit_ok": junit.ok,
                "returncode": junit.returncode,
                "stdout": junit.stdout,
                "stderr": junit.stderr,
            }
            junit_rows.append(junit_row)

            # console.print(
            #     f"[cyan]Validated refactored[/cyan] "
            #     f"{suite['class_name']}/{suite['scenario_id']}/"
            #     f"{suite['model_alias']}/iter_{suite['iteration']} "
            #     f"compile={compilation.ok} junit={junit.ok}"
            # )
            self.log.detail(
                f"Validated refactored "
                f"{suite['class_name']}/{suite['scenario_id']}/"
                f"{suite['model_alias']}/iter_{suite['iteration']} "
                f"compile={compilation.ok} junit={junit.ok}"
            )

            if self.config["validation"]["coverage"].get("enabled", False) and junit.ok:
                class_files_dir, source_files_dir = self._find_coverage_dirs(
                    dataset=suite["dataset"],
                    project=suite["project"],
                    class_name=suite["class_name"],
                    bug_id=suite.get("bug_id", ""),
                )

                coverage_output_dir = (
                    validation_root
                    / "coverage"
                    / suite["model_alias"]
                    / suite["dataset"]
                    / suite["project"]
                    / suite["class_name"]
                    / suite["testsuite_id"]
                    / suite["scenario_id"]
                    / f"iter_{suite['iteration']}"
                )

                patched_sources_dir = coverage_output_dir / "patched_sources"

                patched_test_file, patched_scaffolding_file, separate_classloader_patched = (
                    create_coverage_friendly_test_copy(
                        test_file=test_file,
                        scaffolding_file=scaffolding_file,
                        output_dir=patched_sources_dir,
                    )
                )

                coverage_compiled_tests_dir = coverage_output_dir / "compiled_tests"

                coverage_compiler = JavaTestCompiler(
                    javac_cmd=self.config["validation"]["compilation"].get("javac_cmd", "javac"),
                    project_classpath=target_classpath,
                    extra_classpath=self.config["validation"]["compilation"].get("extra_classpath", []),
                    base_dir=self.project_root,
                )

                coverage_compilation = coverage_compiler.compile_tests(
                    test_file=patched_test_file,
                    scaffolding_file=patched_scaffolding_file,
                    output_dir=coverage_compiled_tests_dir,
                )

                if not coverage_compilation.ok:
                    coverage_rows.append(
                        self._coverage_error_row(
                            suite,
                            returncode=coverage_compilation.returncode,
                            separate_classloader_patched=separate_classloader_patched,
                            coverage_compiled_tests_dir=str(coverage_compiled_tests_dir),
                            stdout=coverage_compilation.stdout,
                            stderr=coverage_compilation.stderr,
                        )
                    )
                    continue

                jacoco = JaCoCoRunner(
                    jacoco_agent_jar=self.config["validation"]["coverage"]["jacoco_agent_jar"],
                    jacoco_cli_jar=self.config["validation"]["coverage"]["jacoco_cli_jar"],
                    java_cmd=self.config["validation"]["junit"].get("java_cmd", "java"),
                    java_memory=self.config["validation"]["junit"].get("java_memory", "-Xmx512M"),
                    project_classpath=target_classpath,
                    compiled_tests_dir=coverage_compiled_tests_dir,
                    extra_classpath=self.config["validation"]["junit"].get("extra_classpath", []),
                    base_dir=self.project_root,
                    jvm_args=self.config["validation"]["coverage"].get("jvm_args", []),
                )

                coverage = jacoco.run_with_coverage(
                    test_class_fqdn=test_class_fqdn,
                    class_files_dir=class_files_dir,
                    source_files_dir=source_files_dir,
                    output_dir=coverage_output_dir,
                )

                coverage_row = {
                    "id": suite["id"],
                    "dataset": suite["dataset"],
                    "project": suite["project"],
                    "class_name": suite["class_name"],
                    "bug_id": suite.get("bug_id", ""),
                    "testsuite_id": suite["testsuite_id"],
                    "scenario": suite["scenario"],
                    "scenario_id": suite["scenario_id"],
                    "iteration": suite["iteration"],
                    "model_alias": suite["model_alias"],
                    "provider": suite["provider"],
                    "model": suite["model"],
                    "coverage_ok": coverage.ok,
                    "returncode": coverage.returncode,
                    "separate_classloader_patched": separate_classloader_patched,
                    "coverage_compiled_tests_dir": str(coverage_compiled_tests_dir),
                    "exec_file": str(coverage.exec_file),
                    "csv_file": str(coverage.csv_file),
                    "xml_file": str(coverage.xml_file),
                    "html_dir": str(coverage.html_dir),
                    "stdout": coverage.stdout,
                    "stderr": coverage.stderr,
                }
                coverage_row.update(coverage.metrics)
                coverage_rows.append(coverage_row)

                # console.print(
                #     f"[magenta]Refactored coverage[/magenta] "
                #     f"{suite['class_name']}/{suite['scenario_id']}/"
                #     f"{suite['model_alias']}/iter_{suite['iteration']} "
                #     f"line={coverage.metrics.get('line_coverage', '')} "
                #     f"branch={coverage.metrics.get('branch_coverage', '')} "
                #     f"method={coverage.metrics.get('method_coverage', '')}"
                # )
                self.log.detail(
                    f"Coverage refactored "
                    f"{suite['class_name']}/{suite['scenario_id']}/"
                    f"{suite['model_alias']}/iter_{suite['iteration']} "
                    f"line={coverage.metrics.get('line_coverage', '')} "
                    f"branch={coverage.metrics.get('branch_coverage', '')} "
                    f"method={coverage.metrics.get('method_coverage', '')}"
                )

        self._write_outputs(validation_root, compilation_rows, junit_rows, coverage_rows)

        #console.print("[bold green]Refactored suite validation completed.[/bold green]")
        compiled_ok = sum(1 for row in compilation_rows if row.get("compiled") is True)
        junit_ok = sum(1 for row in junit_rows if row.get("junit_ok") is True)
        coverage_ok = sum(1 for row in coverage_rows if row.get("coverage_ok") is True)

        self.log.success(
            f"Refactored validation completed: "
            f"compiled={compiled_ok}/{len(compilation_rows)}, "
            f"junit={junit_ok}/{len(junit_rows)}, "
            f"coverage={coverage_ok}/{len(coverage_rows)}."
        )

    def _find_target_classpath(
        self,
        dataset: str,
        project: str,
        class_name: str,
        bug_id: str | None = None,
    ) -> str:
        targets_csv = self.output_dir / "01_targets" / "targets_resolved.csv"

        with targets_csv.open("r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                same_target = (
                    row["dataset"] == dataset
                    and row["project"] == project
                    and row["class_name"] == class_name
                    and (row.get("bug_id", "") or "") == (bug_id or "")
                )
                if same_target:
                    return row.get("classpath", "")

        raise ValueError(
            f"Could not find classpath for target: "
            f"{dataset}/{project}/{class_name}/{bug_id or ''}"
        )

    def _find_coverage_dirs(
        self,
        dataset: str,
        project: str,
        class_name: str,
        bug_id: str | None = None,
    ) -> tuple[str, str]:
        targets_csv = self.output_dir / "01_targets" / "targets_resolved.csv"

        with targets_csv.open("r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                same_target = (
                    row["dataset"] == dataset
                    and row["project"] == project
                    and row["class_name"] == class_name
                    and (row.get("bug_id", "") or "") == (bug_id or "")
                )
                if same_target:
                    class_files_dir = row.get("class_files_dir", "") or row.get("classpath", "")
                    source_files_dir = row.get("source_files_dir", "") or str(Path(row["source_path"]).parent)

                    if not class_files_dir:
                        raise ValueError(
                            f"Missing class_files_dir/classpath for coverage: "
                            f"{dataset}/{project}/{class_name}/{bug_id or ''}"
                        )

                    if not source_files_dir:
                        raise ValueError(
                            f"Missing source_files_dir for coverage: "
                            f"{dataset}/{project}/{class_name}/{bug_id or ''}"
                        )

                    return class_files_dir, source_files_dir

        raise ValueError(
            f"Could not find coverage dirs for target: "
            f"{dataset}/{project}/{class_name}/{bug_id or ''}"
        )

    def _compilation_error_row(
        self,
        suite: Dict[str, str],
        *,
        test_file: str,
        stderr: str,
    ) -> Dict[str, Any]:
        return {
            "id": suite.get("id", ""),
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
            "test_file": test_file,
            "compiled": False,
            "returncode": "",
            "compiled_tests_dir": "",
            "test_class_fqdn": "",
            "stdout": "",
            "stderr": stderr,
        }

    def _coverage_error_row(
        self,
        suite: Dict[str, str],
        *,
        returncode: int,
        separate_classloader_patched: bool,
        coverage_compiled_tests_dir: str,
        stdout: str,
        stderr: str,
    ) -> Dict[str, Any]:
        return {
            "id": suite.get("id", ""),
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
            "coverage_ok": False,
            "returncode": returncode,
            "separate_classloader_patched": separate_classloader_patched,
            "coverage_compiled_tests_dir": coverage_compiled_tests_dir,
            "instruction_coverage": "",
            "branch_coverage": "",
            "line_coverage": "",
            "complexity_coverage": "",
            "method_coverage": "",
            "class_coverage": "",
            "instruction_missed": "",
            "instruction_covered": "",
            "branch_missed": "",
            "branch_covered": "",
            "line_missed": "",
            "line_covered": "",
            "complexity_missed": "",
            "complexity_covered": "",
            "method_missed": "",
            "method_covered": "",
            "class_missed": "",
            "class_covered": "",
            "exec_file": "",
            "csv_file": "",
            "xml_file": "",
            "html_dir": "",
            "stdout": stdout,
            "stderr": stderr,
        }

    def _write_outputs(
        self,
        validation_root: Path,
        compilation_rows: List[Dict[str, Any]],
        junit_rows: List[Dict[str, Any]],
        coverage_rows: List[Dict[str, Any]],
    ) -> None:
        compilation_fields = [
            "id",
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
            "test_file",
            "compiled",
            "returncode",
            "compiled_tests_dir",
            "test_class_fqdn",
            "stdout",
            "stderr",
        ]

        junit_fields = [
            "id",
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
            "test_class_fqdn",
            "junit_ok",
            "returncode",
            "stdout",
            "stderr",
        ]

        coverage_fields = [
            "id",
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
            "coverage_ok",
            "returncode",
            "separate_classloader_patched",
            "coverage_compiled_tests_dir",
            "instruction_coverage",
            "branch_coverage",
            "line_coverage",
            "complexity_coverage",
            "method_coverage",
            "class_coverage",
            "instruction_missed",
            "instruction_covered",
            "branch_missed",
            "branch_covered",
            "line_missed",
            "line_covered",
            "complexity_missed",
            "complexity_covered",
            "method_missed",
            "method_covered",
            "class_missed",
            "class_covered",
            "exec_file",
            "csv_file",
            "xml_file",
            "html_dir",
            "stdout",
            "stderr",
        ]

        _write_csv(
            validation_root / "refactored_compilation_results.csv",
            compilation_rows,
            compilation_fields,
        )
        _write_jsonl(
            validation_root / "refactored_compilation_results.jsonl",
            compilation_rows,
        )

        _write_csv(
            validation_root / "refactored_junit_results.csv",
            junit_rows,
            junit_fields,
        )
        _write_jsonl(
            validation_root / "refactored_junit_results.jsonl",
            junit_rows,
        )

        _write_csv(
            validation_root / "refactored_coverage_results.csv",
            coverage_rows,
            coverage_fields,
        )
        _write_jsonl(
            validation_root / "refactored_coverage_results.jsonl",
            coverage_rows,
        )
