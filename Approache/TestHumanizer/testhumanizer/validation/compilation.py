from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from testhumanizer.validation.classpath import build_classpath


@dataclass
class CompilationResult:
    ok: bool
    returncode: int
    command: List[str]
    stdout: str
    stderr: str
    output_dir: Path


class JavaTestCompiler:
    def __init__(
        self,
        javac_cmd: str = "javac",
        project_classpath: str | None = None,
        extra_classpath: list[str] | None = None,
        base_dir: str | Path | None = None,
    ) -> None:
        self.javac_cmd = javac_cmd
        self.project_classpath = project_classpath
        self.extra_classpath = extra_classpath or []
        self.base_dir = Path(base_dir).resolve() if base_dir else Path.cwd().resolve()

    def compile_tests(
        self,
        test_file: str | Path,
        scaffolding_file: str | Path | None,
        output_dir: str | Path,
    ) -> CompilationResult:
        test_file = Path(test_file).expanduser().resolve()
        output_dir = Path(output_dir).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        java_files = []
        if scaffolding_file:
            scaffolding_path = Path(scaffolding_file).expanduser().resolve()
            if scaffolding_path.exists():
                java_files.append(str(scaffolding_path))

        java_files.append(str(test_file))

        classpath = build_classpath(
            [
                self.project_classpath,
                str(output_dir),
                *self.extra_classpath,
            ],
            base_dir=self.base_dir,
        )

        cmd = [
            self.javac_cmd,
            "-cp",
            classpath,
            "-d",
            str(output_dir),
            *java_files,
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        return CompilationResult(
            ok=result.returncode == 0,
            returncode=result.returncode,
            command=cmd,
            stdout=result.stdout,
            stderr=result.stderr,
            output_dir=output_dir,
        )
