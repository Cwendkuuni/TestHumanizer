from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console

from testhumanizer.validation.compilation import JavaTestCompiler
from testhumanizer.validation.java_utils import infer_fqdn
from testhumanizer.validation.junit_runner import JUnitRunner

from testhumanizer.validation.jacoco import JaCoCoRunner

from testhumanizer.validation.evosuite_patch import create_coverage_friendly_test_copy

from testhumanizer.utils.logging import THLogger

console = Console()


def _read_original_suites(metadata_csv: str | Path) -> List[Dict[str, str]]:
    path = Path(metadata_csv).expanduser().resolve()

    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


class OriginalSuiteValidator:
    def __init__(self, config: Dict[str, Any], project_root: str | Path, output_dir: str | Path) -> None:
        self.config = config
        self.project_root = Path(project_root).expanduser().resolve()
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.log = THLogger(config)

    def validate(self, original_suites_csv: str | Path) -> None:
        suites = _read_original_suites(original_suites_csv)

        compilation_rows: List[Dict[str, Any]] = []
        junit_rows: List[Dict[str, Any]] = []
        coverage_rows: List[Dict[str, Any]] = []

        validation_dir = self.output_dir / "05_validation"
        compiled_root = validation_dir / self.config["validation"]["compilation"].get(
            "output_subdir", "compiled_tests"
        )

        for index, suite in enumerate(suites, start=1):
            test_file = suite["test_file"]
            scaffolding_file = suite.get("scaffolding_file") or None

            # Skip failed EvoSuite generations.
            if "NOT_FOUND_ESTest.java" in test_file or not Path(test_file).exists():
                compilation_rows.append(
                    {
                        "dataset": suite["dataset"],
                        "project": suite["project"],
                        "class_name": suite["class_name"],
                        "bug_id": suite.get("bug_id", ""),
                        "testsuite_id": suite["testsuite_id"],
                        "test_file": test_file,
                        "compiled": False,
                        "returncode": "",
                        "compiled_tests_dir": "",
                        "test_class_fqdn": "",
                        "stdout": "",
                        "stderr": "Missing generated test file.",
                    }
                )
                continue

            compiled_tests_dir = (
                compiled_root
                / suite["dataset"]
                / suite["project"]
                / suite["class_name"]
                / suite["testsuite_id"]
            )

            target_classpath = self._find_target_classpath(
                dataset=suite["dataset"],
                project=suite["project"],
                class_name=suite["class_name"],
                bug_id=suite.get("bug_id", ""),
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

            compilation_rows.append(
                {
                    "dataset": suite["dataset"],
                    "project": suite["project"],
                    "class_name": suite["class_name"],
                    "bug_id": suite.get("bug_id", ""),
                    "testsuite_id": suite["testsuite_id"],
                    "test_file": test_file,
                    "compiled": compilation.ok,
                    "returncode": compilation.returncode,
                    "compiled_tests_dir": str(compilation.output_dir),
                    "test_class_fqdn": test_class_fqdn,
                    "stdout": compilation.stdout,
                    "stderr": compilation.stderr,
                }
            )

            if not compilation.ok:
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

            junit_rows.append(
                {
                    "dataset": suite["dataset"],
                    "project": suite["project"],
                    "class_name": suite["class_name"],
                    "bug_id": suite.get("bug_id", ""),
                    "testsuite_id": suite["testsuite_id"],
                    "test_class_fqdn": test_class_fqdn,
                    "junit_ok": junit.ok,
                    "returncode": junit.returncode,
                    "stdout": junit.stdout,
                    "stderr": junit.stderr,
                }
            )

            # console.print(
            #     f"[cyan]Validated[/cyan] {suite['class_name']}/{suite['testsuite_id']} "
            #     f"compile={compilation.ok} junit={junit.ok}"
            # )
            self.log.detail(
                f"Validated original {suite['class_name']}/{suite['testsuite_id']} "
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
                    validation_dir
                    / "coverage"
                    / suite["dataset"]
                    / suite["project"]
                    / suite["class_name"]
                    / suite["testsuite_id"]
                )



                coverage_sources_dir = coverage_output_dir / "patched_sources"

                patched_test_file, patched_scaffolding_file, separate_classloader_patched = (
                    create_coverage_friendly_test_copy(
                        test_file=test_file,
                        scaffolding_file=scaffolding_file,
                        output_dir=coverage_sources_dir,
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
                        {
                            "dataset": suite["dataset"],
                            "project": suite["project"],
                            "class_name": suite["class_name"],
                            "bug_id": suite.get("bug_id", ""),
                            "testsuite_id": suite["testsuite_id"],
                            "coverage_ok": False,
                            "returncode": coverage_compilation.returncode,
                            "separate_classloader_patched": separate_classloader_patched,
                            "exec_file": "",
                            "csv_file": "",
                            "xml_file": "",
                            "html_dir": "",
                            "stdout": coverage_compilation.stdout,
                            "stderr": coverage_compilation.stderr,
                        }
                    )
                    continue



                jacoco = JaCoCoRunner(
                    jacoco_agent_jar=self.config["validation"]["coverage"]["jacoco_agent_jar"],
                    jacoco_cli_jar=self.config["validation"]["coverage"]["jacoco_cli_jar"],
                    java_cmd=self.config["validation"]["junit"].get("java_cmd", "java"),
                    java_memory=self.config["validation"]["junit"].get("java_memory", "-Xmx512M"),
                    project_classpath=target_classpath,
                    #compiled_tests_dir=compiled_tests_dir,
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
                    "dataset": suite["dataset"],
                    "project": suite["project"],
                    "class_name": suite["class_name"],
                    "bug_id": suite.get("bug_id", ""),
                    "testsuite_id": suite["testsuite_id"],
                    "coverage_ok": coverage.ok,
                    "returncode": coverage.returncode,
                    "exec_file": str(coverage.exec_file),
                    "csv_file": str(coverage.csv_file),
                    "xml_file": str(coverage.xml_file),
                    "html_dir": str(coverage.html_dir),
                    "stdout": coverage.stdout,
                    "stderr": coverage.stderr,
                    "separate_classloader_patched": separate_classloader_patched,
                    "coverage_compiled_tests_dir": str(coverage_compiled_tests_dir),
                }

                coverage_row.update(coverage.metrics)
                coverage_rows.append(coverage_row)

                # console.print(
                #     f"[magenta]Coverage[/magenta] {suite['class_name']}/{suite['testsuite_id']} "
                #     f"line={coverage.metrics.get('line_coverage', '')} "
                #     f"branch={coverage.metrics.get('branch_coverage', '')} "
                #     f"method={coverage.metrics.get('method_coverage', '')}"
                # )

                self.log.detail(
                    f"Coverage original {suite['class_name']}/{suite['testsuite_id']} "
                    f"line={coverage.metrics.get('line_coverage', '')} "
                    f"branch={coverage.metrics.get('branch_coverage', '')} "
                    f"method={coverage.metrics.get('method_coverage', '')}"
                )

        _write_csv(
            validation_dir / "original_compilation_results.csv",
            compilation_rows,
            [
                "dataset",
                "project",
                "class_name",
                "bug_id",
                "testsuite_id",
                "test_file",
                "compiled",
                "returncode",
                "compiled_tests_dir",
                "test_class_fqdn",
                "stdout",
                "stderr",
            ],
        )

        _write_jsonl(validation_dir / "original_compilation_results.jsonl", compilation_rows)

        _write_csv(
            validation_dir / "original_junit_results.csv",
            junit_rows,
            [
                "dataset",
                "project",
                "class_name",
                "bug_id",
                "testsuite_id",
                "test_class_fqdn",
                "junit_ok",
                "returncode",
                "stdout",
                "stderr",
            ],
        )

        _write_jsonl(validation_dir / "original_junit_results.jsonl", junit_rows)

        if coverage_rows:
            coverage_fieldnames = [
                "dataset",
                "project",
                "class_name",
                "bug_id",
                "testsuite_id",
                "coverage_ok",
                "returncode",
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
                "separate_classloader_patched",
                "coverage_compiled_tests_dir",
            ]

            _write_csv(
                validation_dir / "original_coverage_results.csv",
                coverage_rows,
                coverage_fieldnames,
            )

            _write_jsonl(
                validation_dir / "original_coverage_results.jsonl",
                coverage_rows,
            )

        #console.print("[bold green]Original suite validation completed.[/bold green]")
        compiled_ok = sum(1 for row in compilation_rows if row.get("compiled") is True)
        junit_ok = sum(1 for row in junit_rows if row.get("junit_ok") is True)
        coverage_ok = sum(1 for row in coverage_rows if row.get("coverage_ok") is True)

        self.log.success(
            f"Original validation completed: "
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
        """
        For now, recover classpath from targets_resolved.csv.
        Later, dataset-specific adapters can override this.
        """
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
