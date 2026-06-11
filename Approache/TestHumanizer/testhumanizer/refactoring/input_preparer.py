from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console

from testhumanizer.refactoring.java_parser import extract_java_test_parts, read_text


console = Console()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def _read_original_suites(metadata_csv: str | Path) -> List[Dict[str, str]]:
    path = Path(metadata_csv).expanduser().resolve()

    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _read_targets(targets_csv: str | Path) -> List[Dict[str, str]]:
    path = Path(targets_csv).expanduser().resolve()

    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _target_key(row: Dict[str, str]) -> tuple[str, str, str, str]:
    return (
        row.get("dataset", ""),
        row.get("project", ""),
        row.get("class_name", ""),
        row.get("bug_id", "") or "",
    )


def _suite_key(row: Dict[str, str]) -> tuple[str, str, str, str]:
    return (
        row.get("dataset", ""),
        row.get("project", ""),
        row.get("class_name", ""),
        row.get("bug_id", "") or "",
    )


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


class RefactoringInputPreparer:
    def __init__(self, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir).expanduser().resolve()

    def prepare(
        self,
        original_suites_csv: str | Path,
        targets_csv: str | Path,
    ) -> None:
        suites = _read_original_suites(original_suites_csv)
        targets = _read_targets(targets_csv)

        targets_by_key = {_target_key(row): row for row in targets}

        prepared_rows: List[Dict[str, Any]] = []
        metadata_rows: List[Dict[str, Any]] = []

        for suite in suites:
            test_file = suite.get("test_file", "")

            if not test_file or "NOT_FOUND_ESTest.java" in test_file:
                continue

            test_path = Path(test_file).expanduser().resolve()
            if not test_path.exists():
                continue

            key = _suite_key(suite)
            target = targets_by_key.get(key)

            if target is None:
                console.print(f"[yellow]Skipping suite without target match:[/yellow] {suite}")
                continue

            extraction = extract_java_test_parts(test_path)

            source_path = Path(target["source_path"]).expanduser()
            if not source_path.is_absolute():
                source_path = Path.cwd() / source_path
            source_path = source_path.resolve()

            source_code = read_text(source_path) if source_path.exists() else ""

            record_id = "_".join(
                [
                    suite["dataset"],
                    suite["project"],
                    suite["class_name"],
                    suite.get("bug_id", "") or "NA",
                    suite["testsuite_id"],
                ]
            )

            record = {
                "id": record_id,
                "dataset": suite["dataset"],
                "project": suite["project"],
                "class_name": suite["class_name"],
                "bug_id": suite.get("bug_id", "") or None,
                "testsuite_id": suite["testsuite_id"],
                "generator": suite.get("generator", "evosuite"),
                "test_file": test_file,
                "scaffolding_file": suite.get("scaffolding_file", "") or None,
                "source_path": str(source_path),
                "package_name": extraction.package_name,
                "test_class_name": extraction.test_class_name,
                "test_class_fqdn": extraction.test_class_fqdn,
                "fqdn_path": extraction.fqdn_path,
                "test_method_count": extraction.test_method_count,
                "helper_method_count": extraction.helper_method_count,
                "hashes": {
                    "full_test_code_sha256": sha256_text(extraction.full_code),
                    "static_part_sha256": sha256_text(extraction.static_part),
                    "test_code_sha256": sha256_text(extraction.test_code),
                    "source_code_sha256": sha256_text(source_code),
                },
                "content": {
                    "static_part": extraction.static_part,
                    "test_code": extraction.test_code,
                    "full_test_code": extraction.full_code,
                    "class_source_code": source_code,
                },
            }

            prepared_rows.append(record)

            metadata_rows.append(
                {
                    "id": record_id,
                    "dataset": suite["dataset"],
                    "project": suite["project"],
                    "class_name": suite["class_name"],
                    "bug_id": suite.get("bug_id", "") or "",
                    "testsuite_id": suite["testsuite_id"],
                    "generator": suite.get("generator", "evosuite"),
                    "test_file": test_file,
                    "scaffolding_file": suite.get("scaffolding_file", "") or "",
                    "source_path": str(source_path),
                    "package_name": extraction.package_name or "",
                    "test_class_name": extraction.test_class_name,
                    "test_class_fqdn": extraction.test_class_fqdn,
                    "fqdn_path": extraction.fqdn_path,
                    "test_method_count": extraction.test_method_count,
                    "helper_method_count": extraction.helper_method_count,
                    "full_test_code_sha256": sha256_text(extraction.full_code),
                    "static_part_sha256": sha256_text(extraction.static_part),
                    "test_code_sha256": sha256_text(extraction.test_code),
                    "source_code_sha256": sha256_text(source_code),
                }
            )

            console.print(
                f"[cyan]Prepared refactoring input[/cyan] "
                f"{suite['class_name']}/{suite['testsuite_id']} "
                f"tests={extraction.test_method_count} helpers={extraction.helper_method_count}"
            )

        refactoring_dir = self.output_dir / "04_refactorings"

        _write_jsonl(
            refactoring_dir / "prepared_inputs.jsonl",
            prepared_rows,
        )

        _write_csv(
            refactoring_dir / "prepared_inputs_metadata.csv",
            metadata_rows,
            [
                "id",
                "dataset",
                "project",
                "class_name",
                "bug_id",
                "testsuite_id",
                "generator",
                "test_file",
                "scaffolding_file",
                "source_path",
                "package_name",
                "test_class_name",
                "test_class_fqdn",
                "fqdn_path",
                "test_method_count",
                "helper_method_count",
                "full_test_code_sha256",
                "static_part_sha256",
                "test_code_sha256",
                "source_code_sha256",
            ],
        )

        console.print(
            f"[bold green]Prepared {len(prepared_rows)} refactoring inputs.[/bold green]"
        )
