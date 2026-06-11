from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from testhumanizer.core.artifacts import GeneratedTestSuite
from testhumanizer.utils.io import write_csv, write_jsonl


def suite_to_record(suite: GeneratedTestSuite) -> Dict[str, Any]:
    target = suite.target

    return {
        "dataset": target.dataset,
        "project": target.project,
        "class_name": target.class_name,
        "bug_id": target.bug_id or "",
        "testsuite_id": suite.testsuite_id,
        "generator": suite.generator,
        "seed": suite.metadata.get("seed", ""),
        "returncode": suite.metadata.get("returncode", ""),
        "test_file": str(suite.test_file),
        "scaffolding_file": str(suite.scaffolding_file) if suite.scaffolding_file else "",
        "output_dir": str(suite.output_dir),
        "log_file": suite.metadata.get("log_file", ""),
    }


def save_generated_suites(output_dir: str | Path, suites: List[GeneratedTestSuite]) -> None:
    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    records = [suite_to_record(suite) for suite in suites]

    fieldnames = [
        "dataset",
        "project",
        "class_name",
        "bug_id",
        "testsuite_id",
        "generator",
        "seed",
        "returncode",
        "test_file",
        "scaffolding_file",
        "output_dir",
        "log_file",
    ]

    write_csv(output_dir / "original_suites_metadata.csv", records, fieldnames)
    write_jsonl(output_dir / "original_suites.jsonl", records)
