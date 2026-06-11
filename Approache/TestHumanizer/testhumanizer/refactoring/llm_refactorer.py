from __future__ import annotations

import csv
import hashlib
import json
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console

from testhumanizer.llms.base import LLMClient
from testhumanizer.llms.factory import (
    build_llm_client_from_model_config,
    get_refactoring_model_configs,
)


console = Console()


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def append_jsonl(path: str | Path, row: Dict[str, Any]) -> None:
    p = Path(path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: str | Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    p = Path(path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def load_existing_output_ids(path: str | Path) -> set[str]:
    p = Path(path).expanduser().resolve()

    if not p.exists():
        return set()

    existing = set()
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                row = json.loads(line)
                existing.add(row["id"])
            except Exception:
                continue

    return existing


def safe_log_name(value: str) -> str:
    return (
        value.replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
    )


def log_error(error_dir: str | Path, output_id: str, message: str) -> None:
    p = Path(error_dir).expanduser().resolve()
    p.mkdir(parents=True, exist_ok=True)

    log_path = p / f"{safe_log_name(output_id)}.log"

    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"[{now_utc_iso()}]\n")
        f.write(message)
        f.write("\n\n")


class LLMRefactorer:
    def __init__(self, output_dir: str | Path, config: Dict[str, Any]) -> None:
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.config = config

        self.model_configs = get_refactoring_model_configs(config)
        self.model_configs_by_alias = {
            model_config.get("name") or model_config.get("model"): model_config
            for model_config in self.model_configs
        }
        self.clients_by_alias: Dict[str, LLMClient] = {}

    def _get_client(self, model_alias: str) -> LLMClient:
        if model_alias in self.clients_by_alias:
            return self.clients_by_alias[model_alias]

        if model_alias not in self.model_configs_by_alias:
            raise ValueError(f"No LLM config found for model_alias={model_alias}")

        client = build_llm_client_from_model_config(
            self.model_configs_by_alias[model_alias]
        )
        self.clients_by_alias[model_alias] = client
        return client

    def run(self, prompts_jsonl: str | Path) -> None:
        prompts = read_jsonl(prompts_jsonl)

        refactoring_config = self.config.get("refactoring", {})
        execution_config = self.config.get("llm_execution", {})

        iterations = int(refactoring_config.get("iterations", 3))
        skip_existing = bool(execution_config.get("skip_existing", True))

        output_base = self.output_dir / "04_refactorings" / "llm_outputs"
        output_jsonl = output_base / "raw_refactoring_outputs.jsonl"
        metadata_csv = output_base / "raw_refactoring_outputs_metadata.csv"
        error_dir = output_base / "error_logs"

        existing_ids = load_existing_output_ids(output_jsonl) if skip_existing else set()

        metadata_rows: List[Dict[str, Any]] = []
        if output_jsonl.exists():
            metadata_rows = self._load_existing_metadata_rows(output_jsonl)

        total_expected = len(prompts) * iterations
        completed_now = 0
        skipped = 0
        failed = 0

        console.print(
            f"[bold cyan]Starting LLM refactoring[/bold cyan] "
            f"prompts={len(prompts)} iterations={iterations} expected_outputs={total_expected}"
        )

        for prompt_row in prompts:
            prompt = prompt_row["prompt"]
            model_alias = prompt_row["model_alias"]
            client = self._get_client(model_alias)

            for iteration in range(1, iterations + 1):
                output_id = f"{prompt_row['id']}_iter_{iteration}"

                if skip_existing and output_id in existing_ids:
                    skipped += 1
                    console.print(f"[yellow]Skipping existing[/yellow] {output_id}")
                    continue

                console.print(
                    f"[cyan]Calling LLM[/cyan] "
                    f"{prompt_row['class_name']}/{prompt_row['testsuite_id']} "
                    f"{prompt_row['scenario_id']} "
                    f"model={model_alias} iter={iteration}"
                )

                started_at = now_utc_iso()

                try:
                    response = client.complete(prompt)
                    finished_at = now_utc_iso()

                    content = response.content or ""

                    row = {
                        "id": output_id,
                        "prompt_id": prompt_row["id"],
                        "input_id": prompt_row["input_id"],
                        "dataset": prompt_row["dataset"],
                        "project": prompt_row["project"],
                        "class_name": prompt_row["class_name"],
                        "bug_id": prompt_row.get("bug_id"),
                        "testsuite_id": prompt_row["testsuite_id"],
                        "scenario": prompt_row["scenario"],
                        "scenario_id": prompt_row["scenario_id"],
                        "iteration": iteration,
                        "model_alias": model_alias,
                        "provider": response.provider,
                        "model": response.model,
                        "started_at": started_at,
                        "finished_at": finished_at,
                        "status": "ok",
                        "prompt_sha256": prompt_row.get("prompt_sha256"),
                        "prompt_length_chars": prompt_row.get("prompt_length_chars"),
                        "prompt_token_count_estimated": prompt_row.get("prompt_token_count"),
                        "response_sha256": sha256_text(content),
                        "response_length_chars": len(content),
                        "prompt_tokens": response.prompt_tokens,
                        "completion_tokens": response.completion_tokens,
                        "total_tokens": response.total_tokens,
                        "raw_response_metadata": response.raw,
                        "content": content,
                    }

                    append_jsonl(output_jsonl, row)

                    metadata_rows.append(self._to_metadata_row(row))

                    write_csv(
                        metadata_csv,
                        metadata_rows,
                        self._metadata_fieldnames(),
                    )

                    existing_ids.add(output_id)
                    completed_now += 1

                    console.print(
                        f"[green]Saved[/green] {output_id} "
                        f"chars={len(content)} "
                        f"tokens={response.total_tokens}"
                    )

                except Exception as e:
                    failed += 1
                    finished_at = now_utc_iso()

                    error_message = (
                        f"Output ID: {output_id}\n"
                        f"Started at: {started_at}\n"
                        f"Finished at: {finished_at}\n"
                        f"Error type: {type(e).__name__}\n"
                        f"Error message: {e}\n\n"
                        f"Traceback:\n{traceback.format_exc()}"
                    )

                    log_error(error_dir, output_id, error_message)

                    error_row = {
                        "id": output_id,
                        "prompt_id": prompt_row["id"],
                        "input_id": prompt_row["input_id"],
                        "dataset": prompt_row["dataset"],
                        "project": prompt_row["project"],
                        "class_name": prompt_row["class_name"],
                        "bug_id": prompt_row.get("bug_id"),
                        "testsuite_id": prompt_row["testsuite_id"],
                        "scenario": prompt_row["scenario"],
                        "scenario_id": prompt_row["scenario_id"],
                        "iteration": iteration,
                        "model_alias": model_alias,
                        "provider": getattr(client, "provider", ""),
                        "model": getattr(client, "model", ""),
                        "started_at": started_at,
                        "finished_at": finished_at,
                        "status": "error",
                        "prompt_sha256": prompt_row.get("prompt_sha256"),
                        "prompt_length_chars": prompt_row.get("prompt_length_chars"),
                        "prompt_token_count_estimated": prompt_row.get("prompt_token_count"),
                        "response_sha256": "",
                        "response_length_chars": 0,
                        "prompt_tokens": "",
                        "completion_tokens": "",
                        "total_tokens": "",
                        "raw_response_metadata": {},
                        "content": "",
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                    }

                    append_jsonl(output_jsonl, error_row)
                    metadata_rows.append(self._to_metadata_row(error_row))

                    write_csv(
                        metadata_csv,
                        metadata_rows,
                        self._metadata_fieldnames(),
                    )

                    console.print(f"[red]Failed[/red] {output_id}: {e}")

        console.print(
            f"[bold green]LLM refactoring finished.[/bold green] "
            f"completed_now={completed_now} skipped={skipped} failed={failed}"
        )

    def _load_existing_metadata_rows(self, output_jsonl: Path) -> List[Dict[str, Any]]:
        rows = read_jsonl(output_jsonl)
        return [self._to_metadata_row(row) for row in rows]

    def _to_metadata_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": row.get("id", ""),
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
            "status": row.get("status", ""),
            "started_at": row.get("started_at", ""),
            "finished_at": row.get("finished_at", ""),
            "prompt_sha256": row.get("prompt_sha256", ""),
            "prompt_length_chars": row.get("prompt_length_chars", ""),
            "prompt_token_count_estimated": row.get("prompt_token_count_estimated", ""),
            "response_sha256": row.get("response_sha256", ""),
            "response_length_chars": row.get("response_length_chars", ""),
            "prompt_tokens": row.get("prompt_tokens", ""),
            "completion_tokens": row.get("completion_tokens", ""),
            "total_tokens": row.get("total_tokens", ""),
            "error_type": row.get("error_type", ""),
            "error_message": row.get("error_message", ""),
        }

    def _metadata_fieldnames(self) -> List[str]:
        return [
            "id",
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
            "status",
            "started_at",
            "finished_at",
            "prompt_sha256",
            "prompt_length_chars",
            "prompt_token_count_estimated",
            "response_sha256",
            "response_length_chars",
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
            "error_type",
            "error_message",
        ]
