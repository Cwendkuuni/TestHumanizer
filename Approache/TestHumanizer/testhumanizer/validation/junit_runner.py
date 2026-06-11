from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List

from testhumanizer.validation.classpath import build_classpath


@dataclass
class JUnitResult:
    ok: bool
    returncode: int
    command: List[str]
    stdout: str
    stderr: str
    test_class_fqdn: str


class JUnitRunner:
    def __init__(
        self,
        java_cmd: str = "java",
        java_memory: str = "-Xmx512M",
        project_classpath: str | None = None,
        compiled_tests_dir: str | Path | None = None,
        extra_classpath: list[str] | None = None,
        base_dir: str | Path | None = None,
    ) -> None:
        self.java_cmd = java_cmd
        self.java_memory = java_memory
        self.project_classpath = project_classpath
        self.compiled_tests_dir = Path(compiled_tests_dir).resolve() if compiled_tests_dir else None
        self.extra_classpath = extra_classpath or []
        self.base_dir = Path(base_dir).resolve() if base_dir else Path.cwd().resolve()

    def run(self, test_class_fqdn: str) -> JUnitResult:
        classpath = build_classpath(
            [
                self.project_classpath,
                str(self.compiled_tests_dir) if self.compiled_tests_dir else None,
                *self.extra_classpath,
            ],
            base_dir=self.base_dir,
        )

        cmd = [
            self.java_cmd,
            self.java_memory,
            "-cp",
            classpath,
            "org.junit.runner.JUnitCore",
            test_class_fqdn,
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        ok = result.returncode == 0 and "FAILURES!!!" not in result.stdout

        return JUnitResult(
            ok=ok,
            returncode=result.returncode,
            command=cmd,
            stdout=result.stdout,
            stderr=result.stderr,
            test_class_fqdn=test_class_fqdn,
        )
