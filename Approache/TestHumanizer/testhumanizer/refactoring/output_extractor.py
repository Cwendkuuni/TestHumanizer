from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

from testhumanizer.refactoring.code_extractor import extract_java_code_from_llm_output
from testhumanizer.refactoring.suite_reconstructor import write_refactored_suite_files
from testhumanizer.utils.logging import THLogger


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def read_jsonl(path: str | Path) -> List[Dict[str, Any]]:
    p = Path(path).expanduser().resolve()
    rows: List[Dict[str, Any]] = []

    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    return rows


def write_jsonl(path: str | Path, rows: List[Dict[str, Any]]) -> None:
    p = Path(path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: str | Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    p = Path(path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _key(row: Dict[str, Any]) -> tuple[str, str, str, str, str]:
    return (
        row.get("dataset", ""),
        row.get("project", ""),
        row.get("class_name", ""),
        row.get("bug_id", "") or "",
        row.get("testsuite_id", ""),
    )


class RefactoredOutputExtractor:
    def __init__(self, output_dir: str | Path, config: Dict[str, Any] | None = None) -> None:
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.config = config or {}
        self.log = THLogger(self.config)

    def extract(
        self,
        *,
        raw_outputs_jsonl: str | Path,
        prepared_inputs_jsonl: str | Path,
    ) -> None:
        raw_outputs = read_jsonl(raw_outputs_jsonl)
        prepared_inputs = read_jsonl(prepared_inputs_jsonl)

        prepared_by_key = {_key(item): item for item in prepared_inputs}

        extracted_rows: List[Dict[str, Any]] = []
        metadata_rows: List[Dict[str, Any]] = []

        skipped_raw_status = 0
        missing_prepared_inputs = 0
        extraction_failures = 0

        extracted_root = self.output_dir / "04_refactorings" / "extracted_suites"
        generated_root = extracted_root / "generated"

        for raw in raw_outputs:
            if raw.get("status") != "ok":
                skipped_raw_status += 1
                metadata_rows.append(
                    self._metadata_error_row(
                        raw,
                        extraction_status="skipped_raw_status_not_ok",
                        extraction_message=f"Raw status is {raw.get('status')}.",
                    )
                )
                self.log.detail(
                    f"Extraction skipped for {raw.get('id', '')}: "
                    f"raw status={raw.get('status')}."
                )
                continue

            key = _key(raw)
            prepared = prepared_by_key.get(key)

            if prepared is None:
                missing_prepared_inputs += 1
                metadata_rows.append(
                    self._metadata_error_row(
                        raw,
                        extraction_status="missing_prepared_input",
                        extraction_message="Could not find matching prepared input.",
                    )
                )
                self.log.detail(
                    f"Extraction skipped for {raw.get('id', '')}: missing prepared input."
                )
                continue

            extraction = extract_java_code_from_llm_output(raw.get("content", ""))

            if extraction.code is None:
                extraction_failures += 1
                metadata_rows.append(
                    self._metadata_error_row(
                        raw,
                        extraction_status=extraction.status,
                        extraction_message=extraction.message,
                    )
                )
                self.log.warning(
                    f"Extraction failed for {raw.get('id', '')}: status={extraction.status}."
                )
                continue

            original_test_file = Path(prepared["test_file"]).expanduser().resolve()
            test_file_name = original_test_file.name
            scaffolding_file = prepared.get("scaffolding_file")
            fqdn_path = prepared.get("fqdn_path") or ""

            suite_output_base = (
                generated_root
                / str(raw.get("model_alias", raw.get("model", "unknown")))
                / raw["dataset"]
                / raw["project"]
                / raw["class_name"]
                / raw["testsuite_id"]
                / raw["scenario_id"]
                / f"iter_{raw['iteration']}"
            )

            test_output_path, scaffolding_output_path = write_refactored_suite_files(
                refactored_test_code=extraction.code,
                test_file_name=test_file_name,
                original_scaffolding_file=scaffolding_file,
                output_base_dir=suite_output_base,
                fqdn_path=fqdn_path,
            )

            extracted_id = raw["id"]

            record = {
                "id": extracted_id,
                "raw_output_id": raw["id"],
                "prompt_id": raw["prompt_id"],
                "input_id": raw["input_id"],
                "dataset": raw["dataset"],
                "project": raw["project"],
                "class_name": raw["class_name"],
                "bug_id": raw.get("bug_id"),
                "testsuite_id": raw["testsuite_id"],
                "scenario": raw["scenario"],
                "scenario_id": raw["scenario_id"],
                "iteration": raw["iteration"],
                "model_alias": raw.get("model_alias", ""),
                "provider": raw.get("provider", ""),
                "model": raw.get("model", ""),
                "extraction_status": extraction.status,
                "extraction_strategy": extraction.extraction_strategy,
                "extraction_message": extraction.message,
                "fqdn_path": fqdn_path,
                "test_file_name": test_file_name,
                "refactored_test_file": str(test_output_path),
                "scaffolding_file": str(scaffolding_output_path) if scaffolding_output_path else "",
                "refactored_code_sha256": sha256_text(extraction.code),
                "refactored_code_length_chars": len(extraction.code),
                "content": {
                    "refactored_test_code": extraction.code,
                },
            }

            extracted_rows.append(record)
            metadata_rows.append(self._to_metadata_row(record))

            self.log.detail(
                f"Extracted {extracted_id}: "
                f"status={extraction.status}, file={test_output_path}"
            )

        write_jsonl(
            extracted_root / "extracted_refactored_suites.jsonl",
            extracted_rows,
        )

        write_csv(
            extracted_root / "extracted_refactored_suites_metadata.csv",
            metadata_rows,
            self._metadata_fieldnames(),
        )

        self.log.success(
            f"Extraction completed: "
            f"extracted={len(extracted_rows)}, "
            f"metadata_rows={len(metadata_rows)}, "
            f"skipped_raw_status={skipped_raw_status}, "
            f"missing_inputs={missing_prepared_inputs}, "
            f"failed={extraction_failures}."
        )

    def _metadata_error_row(
        self,
        raw: Dict[str, Any],
        *,
        extraction_status: str,
        extraction_message: str,
    ) -> Dict[str, Any]:
        row = {
            "id": raw.get("id", ""),
            "raw_output_id": raw.get("id", ""),
            "prompt_id": raw.get("prompt_id", ""),
            "input_id": raw.get("input_id", ""),
            "dataset": raw.get("dataset", ""),
            "project": raw.get("project", ""),
            "class_name": raw.get("class_name", ""),
            "bug_id": raw.get("bug_id") or "",
            "testsuite_id": raw.get("testsuite_id", ""),
            "scenario": raw.get("scenario", ""),
            "scenario_id": raw.get("scenario_id", ""),
            "iteration": raw.get("iteration", ""),
            "model_alias": raw.get("model_alias", ""),
            "provider": raw.get("provider", ""),
            "model": raw.get("model", ""),
            "extraction_status": extraction_status,
            "extraction_strategy": "",
            "extraction_message": extraction_message,
            "fqdn_path": "",
            "test_file_name": "",
            "refactored_test_file": "",
            "scaffolding_file": "",
            "refactored_code_sha256": "",
            "refactored_code_length_chars": 0,
        }
        return row

    def _to_metadata_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": row.get("id", ""),
            "raw_output_id": row.get("raw_output_id", ""),
            "prompt_id": row.get("prompt_id", ""),
            "input_id": row.get("input_id", ""),
            "dataset": row.get("dataset", ""),
            "project": row.get("project", ""),
            "class_name": row.get("class_name", ""),
            "bug_id": row.get("bug_id") or "",
            "testsuite_id": row.get("testsuite_id", ""),
            "scenario": row.get("scenario", ""),
            "scenario_id": row.get("scenario_id", ""),
            "iteration": row.get("iteration", ""),
            "model_alias": row.get("model_alias", ""),
            "provider": row.get("provider", ""),
            "model": row.get("model", ""),
            "extraction_status": row.get("extraction_status", ""),
            "extraction_strategy": row.get("extraction_strategy", ""),
            "extraction_message": row.get("extraction_message", ""),
            "fqdn_path": row.get("fqdn_path", ""),
            "test_file_name": row.get("test_file_name", ""),
            "refactored_test_file": row.get("refactored_test_file", ""),
            "scaffolding_file": row.get("scaffolding_file", ""),
            "refactored_code_sha256": row.get("refactored_code_sha256", ""),
            "refactored_code_length_chars": row.get("refactored_code_length_chars", ""),
        }

    def _metadata_fieldnames(self) -> List[str]:
        return [
            "id",
            "raw_output_id",
            "prompt_id",
            "input_id",
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
            "extraction_status",
            "extraction_strategy",
            "extraction_message",
            "fqdn_path",
            "test_file_name",
            "refactored_test_file",
            "scaffolding_file",
            "refactored_code_sha256",
            "refactored_code_length_chars",
        ]
