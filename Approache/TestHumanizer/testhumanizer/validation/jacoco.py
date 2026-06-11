from __future__ import annotations

import csv
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from testhumanizer.validation.classpath import build_classpath


@dataclass
class JaCoCoResult:
    ok: bool
    returncode: int
    exec_file: Path
    report_dir: Path
    csv_file: Path
    xml_file: Path
    html_dir: Path
    stdout: str
    stderr: str
    metrics: Dict[str, Any]


class JaCoCoRunner:
    def __init__(
        self,
        jacoco_agent_jar: str | Path,
        jacoco_cli_jar: str | Path,
        java_cmd: str = "java",
        java_memory: str = "-Xmx512M",
        project_classpath: str | None = None,
        compiled_tests_dir: str | Path | None = None,
        extra_classpath: list[str] | None = None,
        base_dir: str | Path | None = None,
        jvm_args: list[str] | None = None,
    ) -> None:

        self.base_dir = Path(base_dir).expanduser().resolve() if base_dir else Path.cwd().resolve()

        self.jacoco_agent_jar = self._resolve(jacoco_agent_jar)
        self.jacoco_cli_jar = self._resolve(jacoco_cli_jar)

        self.java_cmd = java_cmd
        self.java_memory = java_memory
        self.project_classpath = project_classpath
        self.compiled_tests_dir = Path(compiled_tests_dir).expanduser().resolve() if compiled_tests_dir else None
        self.extra_classpath = extra_classpath or []
        self.jvm_args = jvm_args or []

        if not self.jacoco_agent_jar.exists():
            raise FileNotFoundError(f"JaCoCo agent jar not found: {self.jacoco_agent_jar}")

        if not self.jacoco_cli_jar.exists():
            raise FileNotFoundError(f"JaCoCo CLI jar not found: {self.jacoco_cli_jar}")

    def _resolve(self, path: str | Path) -> Path:
        p = Path(path).expanduser()
        if not p.is_absolute():
            p = self.base_dir / p
        return p.resolve()

    def run_with_coverage(
        self,
        test_class_fqdn: str,
        class_files_dir: str | Path,
        source_files_dir: str | Path,
        output_dir: str | Path,
    ) -> JaCoCoResult:
        output_dir = Path(output_dir).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        exec_file = output_dir / "jacoco.exec"
        report_dir = output_dir / "report"
        html_dir = report_dir / "html"
        csv_file = report_dir / "jacoco.csv"
        xml_file = report_dir / "jacoco.xml"

        report_dir.mkdir(parents=True, exist_ok=True)
        html_dir.mkdir(parents=True, exist_ok=True)

        classpath = build_classpath(
            [
                self.project_classpath,
                str(self.compiled_tests_dir) if self.compiled_tests_dir else None,
                *self.extra_classpath,
            ],
            base_dir=self.base_dir,
        )

        junit_cmd = [
            self.java_cmd,
            self.java_memory,
            *self.jvm_args,
            f"-javaagent:{self.jacoco_agent_jar}=destfile={exec_file},append=false",
            "-cp",
            classpath,
            "org.junit.runner.JUnitCore",
            test_class_fqdn,
        ]

        junit_result = subprocess.run(
            junit_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        if junit_result.returncode != 0:
            return JaCoCoResult(
                ok=False,
                returncode=junit_result.returncode,
                exec_file=exec_file,
                report_dir=report_dir,
                csv_file=csv_file,
                xml_file=xml_file,
                html_dir=html_dir,
                stdout=junit_result.stdout,
                stderr=junit_result.stderr,
                metrics={},
            )

        class_files_dir = self._resolve(class_files_dir)
        source_files_dir = self._resolve(source_files_dir)

        report_cmd = [
            self.java_cmd,
            "-jar",
            str(self.jacoco_cli_jar),
            "report",
            str(exec_file),
            "--classfiles",
            str(class_files_dir),
            "--sourcefiles",
            str(source_files_dir),
            "--csv",
            str(csv_file),
            "--xml",
            str(xml_file),
            "--html",
            str(html_dir),
        ]

        report_result = subprocess.run(
            report_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        metrics = {}
        if report_result.returncode == 0 and csv_file.exists():
            metrics = parse_jacoco_csv(csv_file)

        return JaCoCoResult(
            ok=report_result.returncode == 0,
            returncode=report_result.returncode,
            exec_file=exec_file,
            report_dir=report_dir,
            csv_file=csv_file,
            xml_file=xml_file,
            html_dir=html_dir,
            stdout=junit_result.stdout + "\n" + report_result.stdout,
            stderr=junit_result.stderr + "\n" + report_result.stderr,
            metrics=metrics,
        )


def parse_jacoco_csv(csv_file: str | Path) -> Dict[str, Any]:
    path = Path(csv_file).expanduser().resolve()

    totals = {
        "instruction_missed": 0,
        "instruction_covered": 0,
        "branch_missed": 0,
        "branch_covered": 0,
        "line_missed": 0,
        "line_covered": 0,
        "complexity_missed": 0,
        "complexity_covered": 0,
        "method_missed": 0,
        "method_covered": 0,
        "class_missed": 0,
        "class_covered": 0,
    }

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            totals["instruction_missed"] += int(row.get("INSTRUCTION_MISSED", 0))
            totals["instruction_covered"] += int(row.get("INSTRUCTION_COVERED", 0))
            totals["branch_missed"] += int(row.get("BRANCH_MISSED", 0))
            totals["branch_covered"] += int(row.get("BRANCH_COVERED", 0))
            totals["line_missed"] += int(row.get("LINE_MISSED", 0))
            totals["line_covered"] += int(row.get("LINE_COVERED", 0))
            totals["complexity_missed"] += int(row.get("COMPLEXITY_MISSED", 0))
            totals["complexity_covered"] += int(row.get("COMPLEXITY_COVERED", 0))
            totals["method_missed"] += int(row.get("METHOD_MISSED", 0))
            totals["method_covered"] += int(row.get("METHOD_COVERED", 0))
            totals["class_missed"] += int(row.get("CLASS_MISSED", 0))
            totals["class_covered"] += int(row.get("CLASS_COVERED", 0))

    def pct(covered: int, missed: int) -> float:
        total = covered + missed
        if total == 0:
            return 0.0
        return round((covered / total) * 100.0, 4)

    totals["instruction_coverage"] = pct(
        totals["instruction_covered"], totals["instruction_missed"]
    )
    totals["branch_coverage"] = pct(
        totals["branch_covered"], totals["branch_missed"]
    )
    totals["line_coverage"] = pct(
        totals["line_covered"], totals["line_missed"]
    )
    totals["complexity_coverage"] = pct(
        totals["complexity_covered"], totals["complexity_missed"]
    )
    totals["method_coverage"] = pct(
        totals["method_covered"], totals["method_missed"]
    )
    totals["class_coverage"] = pct(
        totals["class_covered"], totals["class_missed"]
    )

    return totals
