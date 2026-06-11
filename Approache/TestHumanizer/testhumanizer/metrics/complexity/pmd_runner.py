from __future__ import annotations

import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class PMDRunResult:
    ok: bool
    report_xml: Path
    returncode: int
    stdout: str
    stderr: str
    error: str = ""


@dataclass
class PMDMetrics:
    total_cyclomatic_complexity: float
    loc: int
    number_of_methods: int
    comment_density: float
    maintainability_index: float
    complexities: List[float]


class PMDRunner:
    def __init__(
        self,
        *,
        pmd_dir: str | Path,
        pmd_bin: str = "bin/pmd",
        ruleset: str = "cyclomatic_ruleset.xml",
        timeout_seconds: int = 120,
        project_root: str | Path | None = None,
    ) -> None:
        self.project_root = Path(project_root or ".").expanduser().resolve()
        self.pmd_dir = self._resolve_path(pmd_dir)
        self.pmd_bin = self._resolve_inside_pmd_dir(pmd_bin)
        self.ruleset = self._resolve_inside_pmd_dir(ruleset)
        self.timeout_seconds = int(timeout_seconds)

        if not self.pmd_dir.exists():
            raise FileNotFoundError(f"PMD directory not found: {self.pmd_dir}")

        if not self.pmd_bin.exists():
            raise FileNotFoundError(f"PMD executable not found: {self.pmd_bin}")

        if not self.ruleset.exists():
            raise FileNotFoundError(f"PMD ruleset not found: {self.ruleset}")

    def _resolve_path(self, path: str | Path) -> Path:
        p = Path(path).expanduser()
        if not p.is_absolute():
            p = self.project_root / p
        return p.absolute()

    def _resolve_inside_pmd_dir(self, path: str | Path) -> Path:
        p = Path(path).expanduser()
        if not p.is_absolute():
            p = self.pmd_dir / p
        return p.absolute()

    def run_file(self, *, java_file: str | Path, output_xml: str | Path) -> PMDRunResult:
        java_path = Path(java_file).expanduser().absolute()
        report_path = Path(output_xml).expanduser().absolute()
        report_path.parent.mkdir(parents=True, exist_ok=True)

        if not java_path.exists():
            return PMDRunResult(
                ok=False,
                report_xml=report_path,
                returncode=-1,
                stdout="",
                stderr="",
                error=f"Java file not found: {java_path}",
            )

        command = [
            str(self.pmd_bin),
            "check",
            "-d",
            str(java_path),
            "-R",
            str(self.ruleset),
            "-f",
            "xml",
            "-r",
            str(report_path),
        ]

        try:
            result = subprocess.run(
                command,
                cwd=str(self.pmd_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                timeout=self.timeout_seconds,
            )

            # PMD often returns non-zero when violations are found.
            # If the XML exists and is parseable, we treat the run as usable.
            ok = report_path.exists()

            return PMDRunResult(
                ok=ok,
                report_xml=report_path,
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                error="" if ok else "PMD did not produce an XML report.",
            )

        except subprocess.TimeoutExpired as e:
            return PMDRunResult(
                ok=False,
                report_xml=report_path,
                returncode=-1,
                stdout=e.stdout or "",
                stderr=e.stderr or "",
                error=f"Timeout after {self.timeout_seconds} seconds.",
            )

        except Exception as e:
            return PMDRunResult(
                ok=False,
                report_xml=report_path,
                returncode=-1,
                stdout="",
                stderr="",
                error=f"{type(e).__name__}: {e}",
            )


def compute_loc_and_comment_density(java_file: str | Path) -> tuple[int, float]:
    java_path = Path(java_file).expanduser().absolute()

    loc = 0
    comment_lines = 0
    in_block_comment = False

    try:
        lines = java_path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        lines = java_path.read_text(encoding="latin-1").splitlines()

    for line in lines:
        stripped = line.strip()

        if stripped:
            loc += 1

        if in_block_comment:
            comment_lines += 1
            if "*/" in stripped:
                in_block_comment = False
            continue

        if stripped.startswith("//"):
            comment_lines += 1
        elif stripped.startswith("/*"):
            comment_lines += 1
            if "*/" not in stripped:
                in_block_comment = True
        elif stripped.endswith("*/"):
            comment_lines += 1

    comment_density = comment_lines / loc if loc > 0 else 0.0
    return loc, comment_density


def calculate_adjusted_maintainability_index(
    *,
    loc: int,
    total_complexity: float,
    comment_density: float,
) -> float:
    import math

    if loc <= 0 or comment_density <= 0:
        return 0.0

    adjusted_comment_density = max(comment_density, 0.01)

    try:
        mi_raw = (
            171
            - 5.2 * math.log(loc)
            - 0.23 * total_complexity
            - 16.2 * math.log(adjusted_comment_density)
        )
        maintainability_index = (mi_raw * 100) / 171
        return max(0.0, min(100.0, maintainability_index))
    except ValueError:
        return 0.0


def parse_pmd_cyclomatic_report(
    *,
    report_xml: str | Path,
    java_file: str | Path,
) -> PMDMetrics:
    report_path = Path(report_xml).expanduser().absolute()
    complexities: List[float] = []

    if report_path.exists():
        try:
            tree = ET.parse(report_path)
            root = tree.getroot()
            namespaces = {"ns": "http://pmd.sourceforge.net/report/2.0.0"}

            for violation in root.findall(
                './/ns:violation[@rule="CyclomaticComplexity"]',
                namespaces,
            ):
                text = (violation.text or "").strip()
                try:
                    complexity_value = float(text.split()[-1])
                    complexities.append(complexity_value)
                except (ValueError, IndexError):
                    continue

            # Fallback without namespace, just in case.
            if not complexities:
                for violation in root.findall('.//violation[@rule="CyclomaticComplexity"]'):
                    text = (violation.text or "").strip()
                    try:
                        complexity_value = float(text.split()[-1])
                        complexities.append(complexity_value)
                    except (ValueError, IndexError):
                        continue

        except ET.ParseError:
            complexities = []

    total_complexity = float(sum(complexities))
    number_of_methods = len(complexities)

    loc, comment_density = compute_loc_and_comment_density(java_file)

    maintainability_index = calculate_adjusted_maintainability_index(
        loc=loc,
        total_complexity=total_complexity,
        comment_density=comment_density,
    )

    return PMDMetrics(
        total_cyclomatic_complexity=total_complexity,
        loc=loc,
        number_of_methods=number_of_methods,
        comment_density=comment_density,
        maintainability_index=maintainability_index,
        complexities=complexities,
    )
