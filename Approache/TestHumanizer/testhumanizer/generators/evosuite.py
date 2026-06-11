from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List

from testhumanizer.core.artifacts import GeneratedTestSuite, TargetClass
from testhumanizer.generators.base import TestGenerator

def normalize_classpath(classpath: str) -> str:
    parts = classpath.split(":")
    normalized = []

    for part in parts:
        if not part.strip():
            continue

        if "*" in part:
            p = Path(part)
            if not p.is_absolute():
                p = Path.cwd() / p
            normalized.append(str(p.resolve().parent / p.name))
        else:
            p = Path(part)
            if not p.is_absolute():
                p = Path.cwd() / p
            normalized.append(str(p.resolve()))

    return ":".join(normalized)


class EvoSuiteGenerator(TestGenerator):
    def __init__(
        self,
        evosuite_jar: str,
        runs_per_class: int = 15,
        search_budget_seconds: int = 180,
        algorithm: str = "DynaMOSA",
        stopping_condition: str = "MaxTime",
        criterion: str = "BRANCH:METHOD:LINE",
        generate_mo_suite: bool = True,
        show_progress: bool = False,
        disable_minimization: bool = False,
        disable_cleanup: bool = False,
        java_cmd: str = "java",
        java_memory: str = "-Xmx512M",
    ) -> None:
        self.evosuite_jar = Path(evosuite_jar).expanduser().resolve()
        self.runs_per_class = runs_per_class
        self.search_budget_seconds = search_budget_seconds
        self.algorithm = algorithm
        self.stopping_condition = stopping_condition
        self.criterion = criterion
        self.generate_mo_suite = generate_mo_suite
        self.show_progress = show_progress
        self.disable_minimization = disable_minimization
        self.disable_cleanup = disable_cleanup
        self.java_cmd = java_cmd
        self.java_memory = java_memory

        if not self.evosuite_jar.exists():
            raise FileNotFoundError(f"EvoSuite jar not found: {self.evosuite_jar}")

    def generate(self, target: TargetClass, output_dir: Path) -> List[GeneratedTestSuite]:
        output_dir = Path(output_dir).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        generated: List[GeneratedTestSuite] = []

        for run_id in range(1, self.runs_per_class + 1):
            suite_dir = output_dir / target.dataset / target.project / target.class_name
            if target.bug_id:
                suite_dir = suite_dir / str(target.bug_id)

            suite_dir = suite_dir / f"testsuite_{run_id}"
            suite_dir.mkdir(parents=True, exist_ok=True)

            cmd = self._build_command(target=target, suite_dir=suite_dir, seed=run_id)

            log_file = suite_dir / "evosuite.log"
            cmd_file = suite_dir / "evosuite_command.txt"

            cmd_file.write_text(" ".join(cmd) + "\n", encoding="utf-8")

            with log_file.open("w", encoding="utf-8") as log:
                result = subprocess.run(
                    cmd,
                    cwd=str(suite_dir),
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    text=True,
                    check=False,
                )
                
            test_files = [
                p for p in suite_dir.rglob("*_ESTest.java")
                if not p.name.endswith("_ESTest_scaffolding.java")
            ]

            scaffolding_files = list(suite_dir.rglob("*_ESTest_scaffolding.java"))

            if not test_files:
                generated.append(
                    GeneratedTestSuite(
                        target=target,
                        testsuite_id=f"testsuite_{run_id}",
                        test_file=suite_dir / "NOT_FOUND_ESTest.java",
                        scaffolding_file=None,
                        output_dir=suite_dir,
                        generator="evosuite",
                        metadata={
                            "seed": run_id,
                            "returncode": result.returncode,
                            "log_file": str(log_file),
                            "cmd_file": str(cmd_file),
                            "status": "no_test_file_found",
                        },
                    )
                )
                continue

            generated.append(
                GeneratedTestSuite(
                    target=target,
                    testsuite_id=f"testsuite_{run_id}",
                    test_file=test_files[0],
                    scaffolding_file=scaffolding_files[0] if scaffolding_files else None,
                    output_dir=suite_dir,
                    generator="evosuite",
                    metadata={
                        "seed": run_id,
                        "returncode": result.returncode,
                        "log_file": str(log_file),
                        "cmd_file": str(cmd_file),
                        "status": "generated",
                    },
                )
            )

        return generated

    def _build_command(self, target: TargetClass, suite_dir: Path, seed: int) -> list[str]:
        class_under_test = target.test_class_fqdn or target.class_name

        if not normalize_classpath(target.classpath):
            raise ValueError(
                f"Missing classpath for target {target.class_name}. "
                "EvoSuite requires -projectCP."
            )

        cmd = [
            self.java_cmd,
            self.java_memory,
            "-jar",
            str(self.evosuite_jar),
            "-class",
            class_under_test,
            "-projectCP",
            normalize_classpath(target.classpath),
        ]

        if self.generate_mo_suite:
            cmd.append("-generateMOSuite")

        cmd.extend(
            [
                "-Dalgorithm=" + self.algorithm,
                "-Dsearch_budget=" + str(self.search_budget_seconds),
                "-Dstopping_condition=" + self.stopping_condition,
                "-Dcriterion=" + self.criterion,
                "-Dshow_progress=" + str(self.show_progress).lower(),
                "-Drandom_seed=" + str(seed),
                "-Dtest_dir=" + str(suite_dir),
            ]
        )

        if self.disable_minimization:
            cmd.append("-Dminimize=false")

        if self.disable_cleanup:
            cmd.append("-Dcleanup=false")

        return cmd