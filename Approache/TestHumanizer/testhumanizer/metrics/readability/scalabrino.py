from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ReadabilityResult:
    ok: bool
    score: Optional[float]
    returncode: int
    stdout: str
    stderr: str
    error: str = ""


class ScalabrinoReadabilityRunner:
    def __init__(
        self,
        *,
        rsm_dir: str | Path,
        rsm_jar: str = "rsm.jar",
        java_cmd: str = "java",
        timeout_seconds: int = 60,
        project_root: str | Path | None = None,
    ) -> None:
        self.project_root = Path(project_root or ".").expanduser().resolve()
        self.rsm_dir = self._resolve_path(rsm_dir)
        self.rsm_jar = rsm_jar
        self.java_cmd = java_cmd
        self.timeout_seconds = int(timeout_seconds)

        self.rsm_jar_path = self.rsm_dir / self.rsm_jar
        self.classifier_path = self.rsm_dir / "readability.classifier"

        if not self.rsm_dir.exists():
            raise FileNotFoundError(f"Readability model directory not found: {self.rsm_dir}")

        if not self.rsm_jar_path.exists():
            raise FileNotFoundError(f"rsm.jar not found: {self.rsm_jar_path}")

        if not self.classifier_path.exists():
            raise FileNotFoundError(
                f"readability.classifier not found: {self.classifier_path}"
            )

    def _resolve_path(self, path: str | Path) -> Path:
        p = Path(path).expanduser()
        if not p.is_absolute():
            p = self.project_root / p
        return p.absolute()

    def analyze_file(self, java_file_path: str | Path) -> ReadabilityResult:
        java_file = Path(java_file_path).expanduser().absolute()

        if not java_file.exists():
            return ReadabilityResult(
                ok=False,
                score=None,
                returncode=-1,
                stdout="",
                stderr="",
                error=f"Java file not found: {java_file}",
            )

        command = [
            self.java_cmd,
            "-jar",
            str(self.rsm_jar_path),
            str(java_file),
        ]

        try:
            result = subprocess.run(
                command,
                cwd=str(self.rsm_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                timeout=self.timeout_seconds,
            )

            if result.returncode != 0:
                return ReadabilityResult(
                    ok=False,
                    score=None,
                    returncode=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    error="Readability model returned non-zero exit code.",
                )

            score = self._parse_score(result.stdout, java_file)

            if score is None:
                return ReadabilityResult(
                    ok=False,
                    score=None,
                    returncode=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    error="Could not parse readability score from output.",
                )

            return ReadabilityResult(
                ok=True,
                score=score,
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                error="",
            )

        except subprocess.TimeoutExpired as e:
            return ReadabilityResult(
                ok=False,
                score=None,
                returncode=-1,
                stdout=e.stdout or "",
                stderr=e.stderr or "",
                error=f"Timeout after {self.timeout_seconds} seconds.",
            )

        except Exception as e:
            return ReadabilityResult(
                ok=False,
                score=None,
                returncode=-1,
                stdout="",
                stderr="",
                error=f"{type(e).__name__}: {e}",
            )

    def _parse_score(self, stdout: str, java_file: Path) -> Optional[float]:
        expected_basename = java_file.name

        for raw_line in stdout.strip().splitlines():
            line = raw_line.strip()

            if not line:
                continue

            if line.startswith("[INFO]"):
                continue

            if line.lower().startswith("file"):
                continue

            parts = line.split("\t")
            if len(parts) != 2:
                continue

            filename_output, score_str = parts
            output_basename = Path(filename_output.strip()).name

            if output_basename != expected_basename:
                continue

            try:
                return float(score_str.strip())
            except ValueError:
                return None

        return None
