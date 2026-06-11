from __future__ import annotations

import csv
import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from rich.console import Console

from testhumanizer.llms.factory import build_llm_client_from_model_config
from testhumanizer.metrics.side.llm_side import LLMSIDEEvaluator
from testhumanizer.metrics.side.side_model import SIDEModel
from testhumanizer.summarization.prompt_builder import build_source_summarization_prompt
from testhumanizer.summarization.summary_extractor import extract_summary_from_response


console = Console()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


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


def read_jsonl(path: str | Path) -> List[Dict[str, Any]]:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        return []

    rows: List[Dict[str, Any]] = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def make_target_id(target: Dict[str, Any]) -> str:
    dataset = target.get("dataset", "unknown")
    project = target.get("project", "unknown")
    class_name = target.get("class_name", target.get("class", "unknown"))
    bug_id = target.get("bug_id", "") or "NA"
    return f"{dataset}_{project}_{class_name}_{bug_id}"


class SourceSummarizer:
    def __init__(
        self,
        *,
        output_dir: str | Path,
        config: Dict[str, Any],
        project_root: str | Path,
    ) -> None:
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.config = config
        self.project_root = Path(project_root).expanduser().resolve()

        self.summary_config = config.get("summarization", {})
        self.prompt_config = self.summary_config.get("prompt", {})
        self.output_config = self.summary_config.get("output", {})

        self.iterations = int(self.summary_config.get("iterations", 1))
        self.max_attempts = int(self.summary_config.get("max_attempts", 3))
        self.selection_policy = self.summary_config.get("selection_policy", "first_success")
        self.keep_best_if_below_threshold = bool(
            self.summary_config.get("keep_best_if_below_threshold", True)
        )

        self.side_model: SIDEModel | None = None
        self.llm_side_evaluator: LLMSIDEEvaluator | None = None
        self.llm_client = None

    def summarize_targets(self, targets: Iterable[Dict[str, Any]]) -> None:
        summaries_dir = self.output_dir / "03_summaries"
        summaries_dir.mkdir(parents=True, exist_ok=True)

        selected_path = summaries_dir / "source_summaries.jsonl"
        attempts_path = summaries_dir / "summary_attempts.jsonl"
        metadata_path = summaries_dir / "source_summaries_metadata.csv"

        skip_existing = bool(self.output_config.get("skip_existing", True))

        existing_selected = read_jsonl(selected_path)
        existing_ids = {row.get("id") for row in existing_selected}

        all_selected: List[Dict[str, Any]] = list(existing_selected)
        all_attempts: List[Dict[str, Any]] = []

        targets_list = list(targets)

        for target in targets_list:
            summary_id = make_target_id(target)

            if skip_existing and summary_id in existing_ids:
                console.print(f"[yellow]Summary exists, skipping[/yellow] {summary_id}")
                continue

            selected, attempts = self._summarize_one_target(target)

            all_attempts.extend(attempts)

            if selected is not None:
                all_selected.append(selected)

        write_jsonl(selected_path, all_selected)
        write_jsonl(attempts_path, all_attempts)

        fieldnames = [
            "id",
            "dataset",
            "project",
            "class_name",
            "bug_id",
            "source_path",
            "summarizer_alias",
            "provider",
            "model",
            "selected_iteration",
            "selected_attempt",
            "selection_policy",
            "summary_status",
            "summary_chars",
            "summary_sha256",
            "official_side_enabled",
            "official_side_score",
            "official_side_ok",
            "official_side_threshold",
            "official_side_used_for_selection",
            "code_token_count",
            "summary_token_count",
            "code_truncated",
            "summary_truncated",
            "llm_side_enabled",
            "llm_side_score",
            "llm_side_ok",
            "llm_side_threshold",
            "llm_side_used_for_selection",
            "llm_side_faithfulness",
            "llm_side_coverage",
            "llm_side_conciseness",
            "llm_side_hallucination_risk",
            "llm_side_reason",
            "llm_side_error",
            "error",
        ]

        metadata_rows = [self._metadata_row(row) for row in all_selected]
        write_csv(metadata_path, metadata_rows, fieldnames)

        console.print(
            f"[bold green]Source summarization completed.[/bold green] "
            f"selected={len(all_selected)} attempts={len(all_attempts)}"
        )

    def _summarize_one_target(
        self,
        target: Dict[str, Any],
    ) -> tuple[Dict[str, Any] | None, List[Dict[str, Any]]]:
        source_path = self._resolve_source_path(target.get("source_path", ""))

        if not source_path.exists():
            summary_id = make_target_id(target)
            error_row = self._base_row(target)
            error_row.update(
                {
                    "id": summary_id,
                    "summary_status": "source_not_found",
                    "error": f"Source path not found: {source_path}",
                    "selected": False,
                }
            )
            return None, [error_row]

        source_code = source_path.read_text(encoding="utf-8", errors="replace")
        attempts: List[Dict[str, Any]] = []

        for iteration in range(1, self.iterations + 1):
            for attempt in range(1, self.max_attempts + 1):
                row = self._generate_summary_attempt(
                    target=target,
                    source_code=source_code,
                    iteration=iteration,
                    attempt=attempt,
                )

                attempts.append(row)

                if self.selection_policy == "first_success" and row["summary_status"] in {
                    "ok",
                    "ok_no_fence",
                }:
                    row["selected"] = True
                    console.print(
                        f"[cyan]Summary[/cyan] "
                        f"{target.get('class_name', target.get('class', ''))} "
                        f"iter={iteration} attempt={attempt} "
                        f"status={row['summary_status']} "
                        f"SIDE={row.get('official_side_score', '')} "
                        f"LLM_SIDE={row.get('llm_side_score', '')}"
                    )
                    return row, attempts

        selected = self._select_best_summary(attempts)

        if selected is not None:
            selected["selected"] = True
            console.print(
                f"[cyan]Summary[/cyan] "
                f"{target.get('class_name', target.get('class', ''))} "
                f"selected_by={self.selection_policy} "
                f"SIDE={selected.get('official_side_score', '')} "
                f"LLM_SIDE={selected.get('llm_side_score', '')} "
                f"status={selected.get('summary_status', '')}"
            )

        return selected, attempts

    def _generate_summary_attempt(
        self,
        *,
        target: Dict[str, Any],
        source_code: str,
        iteration: int,
        attempt: int,
    ) -> Dict[str, Any]:
        base = self._base_row(target)
        base.update(
            {
                "iteration": iteration,
                "attempt": attempt,
                "selected": False,
            }
        )

        prompt = build_source_summarization_prompt(source_code)

        try:
            raw_output = self._call_llm(prompt)

            extraction = extract_summary_from_response(
                raw_output,
                require_code_fence=bool(self.prompt_config.get("require_code_fence", True)),
            )

            base["raw_output"] = raw_output
            base["summary_text"] = extraction.summary
            base["summary_status"] = extraction.status
            base["summary_ok"] = extraction.ok
            base["error"] = extraction.error

            if extraction.ok:
                base["summary_chars"] = len(extraction.summary)
                base["summary_sha256"] = sha256_text(extraction.summary)

                self._add_official_side(
                    row=base,
                    source_code=source_code,
                    summary=extraction.summary,
                )

                self._add_llm_side(
                    row=base,
                    source_code=source_code,
                    summary=extraction.summary,
                )

            return base

        except Exception as e:
            base.update(
                {
                    "summary_text": "",
                    "summary_status": "llm_error",
                    "summary_ok": False,
                    "error": f"{type(e).__name__}: {e}",
                }
            )

            wait = int(self._llm_config().get("retry_wait_seconds", 10))
            if attempt < self.max_attempts:
                time.sleep(wait)

            return base

    def _add_official_side(
        self,
        *,
        row: Dict[str, Any],
        source_code: str,
        summary: str,
    ) -> None:
        official_side = self.summary_config.get("official_side", {})
        enabled = bool(official_side.get("enabled", False))

        row["official_side_enabled"] = enabled
        row["official_side_used_for_selection"] = bool(
            official_side.get("use_for_selection", False)
        )
        row["official_side_threshold"] = float(
            official_side.get(
                "threshold",
                self.summary_config.get("side_threshold", 0.5),
            )
        )

        if not enabled:
            row["official_side_ok"] = ""
            row["official_side_score"] = ""
            row["code_token_count"] = ""
            row["summary_token_count"] = ""
            row["code_truncated"] = ""
            row["summary_truncated"] = ""
            return

        side = self._get_side_model()
        result = side.score(source_code, summary)

        row["official_side_ok"] = result.ok
        row["official_side_score"] = result.score if result.score is not None else ""
        row["code_token_count"] = result.code_token_count
        row["summary_token_count"] = result.summary_token_count
        row["code_truncated"] = result.code_truncated
        row["summary_truncated"] = result.summary_truncated

        if not result.ok and not row.get("error"):
            row["error"] = result.error

    def _add_llm_side(
        self,
        *,
        row: Dict[str, Any],
        source_code: str,
        summary: str,
    ) -> None:
        llm_side = self.summary_config.get("llm_side", {})
        enabled = bool(llm_side.get("enabled", False))

        row["llm_side_enabled"] = enabled
        row["llm_side_used_for_selection"] = bool(
            llm_side.get("use_for_selection", False)
        )
        row["llm_side_threshold"] = float(llm_side.get("threshold", 0.7))

        if not enabled:
            row["llm_side_ok"] = ""
            row["llm_side_score"] = ""
            row["llm_side_faithfulness"] = ""
            row["llm_side_coverage"] = ""
            row["llm_side_conciseness"] = ""
            row["llm_side_hallucination_risk"] = ""
            row["llm_side_reason"] = ""
            row["llm_side_error"] = ""
            return

        evaluator = self._get_llm_side_evaluator()
        result = evaluator.score(source_code, summary)

        row["llm_side_ok"] = result.ok
        row["llm_side_score"] = result.score if result.score is not None else ""
        row["llm_side_faithfulness"] = (
            result.faithfulness if result.faithfulness is not None else ""
        )
        row["llm_side_coverage"] = result.coverage if result.coverage is not None else ""
        row["llm_side_conciseness"] = (
            result.conciseness if result.conciseness is not None else ""
        )
        row["llm_side_hallucination_risk"] = (
            result.hallucination_risk
            if result.hallucination_risk is not None
            else ""
        )
        row["llm_side_reason"] = result.reason
        row["llm_side_error"] = result.error

        if not result.ok and not row.get("error"):
            row["error"] = result.error

    def _select_best_summary(self, attempts: List[Dict[str, Any]]) -> Dict[str, Any] | None:
        valid = [
            row
            for row in attempts
            if row.get("summary_status") in {"ok", "ok_no_fence"}
            and row.get("summary_text")
        ]

        if not valid:
            return None

        official_side = self.summary_config.get("official_side", {})
        threshold = float(
            official_side.get(
                "threshold",
                self.summary_config.get("side_threshold", 0.5),
            )
        )

        if self.selection_policy == "best_side":
            return self._best_by_side(valid)

        if self.selection_policy == "threshold_then_best":
            for row in valid:
                score = self._safe_float(row.get("official_side_score"))
                if score is not None and score >= threshold:
                    return row

            if self.keep_best_if_below_threshold:
                return self._best_by_side(valid)

            return None

        return valid[0]

    @staticmethod
    def _best_by_side(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        def score(row: Dict[str, Any]) -> float:
            value = row.get("official_side_score")
            try:
                return float(value)
            except (TypeError, ValueError):
                return float("-inf")

        return max(rows, key=score)

    @staticmethod
    def _safe_float(value: Any) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _base_row(self, target: Dict[str, Any]) -> Dict[str, Any]:
        llm_cfg = self._llm_config()

        return {
            "id": make_target_id(target),
            "dataset": target.get("dataset", ""),
            "project": target.get("project", ""),
            "class_name": target.get("class_name", target.get("class", "")),
            "bug_id": target.get("bug_id", "") or "",
            "source_path": target.get("source_path", ""),
            "summarizer_alias": llm_cfg.get("name", "summarizer"),
            "provider": llm_cfg.get("provider", ""),
            "model": llm_cfg.get("model", ""),
            "iteration": "",
            "attempt": "",
            "summary_text": "",
            "raw_output": "",
            "summary_status": "",
            "summary_ok": False,
            "summary_chars": "",
            "summary_sha256": "",
            "official_side_enabled": "",
            "official_side_score": "",
            "official_side_ok": "",
            "official_side_threshold": "",
            "official_side_used_for_selection": "",
            "code_token_count": "",
            "summary_token_count": "",
            "code_truncated": "",
            "summary_truncated": "",
            "llm_side_enabled": "",
            "llm_side_score": "",
            "llm_side_ok": "",
            "llm_side_threshold": "",
            "llm_side_used_for_selection": "",
            "llm_side_faithfulness": "",
            "llm_side_coverage": "",
            "llm_side_conciseness": "",
            "llm_side_hallucination_risk": "",
            "llm_side_reason": "",
            "llm_side_error": "",
            "selected": False,
            "selection_policy": self.selection_policy,
            "error": "",
        }

    def _metadata_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": row.get("id", ""),
            "dataset": row.get("dataset", ""),
            "project": row.get("project", ""),
            "class_name": row.get("class_name", ""),
            "bug_id": row.get("bug_id", ""),
            "source_path": row.get("source_path", ""),
            "summarizer_alias": row.get("summarizer_alias", ""),
            "provider": row.get("provider", ""),
            "model": row.get("model", ""),
            "selected_iteration": row.get("iteration", ""),
            "selected_attempt": row.get("attempt", ""),
            "selection_policy": row.get("selection_policy", ""),
            "summary_status": row.get("summary_status", ""),
            "summary_chars": row.get("summary_chars", ""),
            "summary_sha256": row.get("summary_sha256", ""),
            "official_side_enabled": row.get("official_side_enabled", ""),
            "official_side_score": row.get("official_side_score", ""),
            "official_side_ok": row.get("official_side_ok", ""),
            "official_side_threshold": row.get("official_side_threshold", ""),
            "official_side_used_for_selection": row.get(
                "official_side_used_for_selection",
                "",
            ),
            "code_token_count": row.get("code_token_count", ""),
            "summary_token_count": row.get("summary_token_count", ""),
            "code_truncated": row.get("code_truncated", ""),
            "summary_truncated": row.get("summary_truncated", ""),
            "llm_side_enabled": row.get("llm_side_enabled", ""),
            "llm_side_score": row.get("llm_side_score", ""),
            "llm_side_ok": row.get("llm_side_ok", ""),
            "llm_side_threshold": row.get("llm_side_threshold", ""),
            "llm_side_used_for_selection": row.get("llm_side_used_for_selection", ""),
            "llm_side_faithfulness": row.get("llm_side_faithfulness", ""),
            "llm_side_coverage": row.get("llm_side_coverage", ""),
            "llm_side_conciseness": row.get("llm_side_conciseness", ""),
            "llm_side_hallucination_risk": row.get("llm_side_hallucination_risk", ""),
            "llm_side_reason": row.get("llm_side_reason", ""),
            "llm_side_error": row.get("llm_side_error", ""),
            "error": row.get("error", ""),
        }

    def _resolve_source_path(self, source_path: str | Path) -> Path:
        p = Path(source_path).expanduser()
        if not p.is_absolute():
            p = self.project_root / p
        return p.absolute()

    def _llm_config(self) -> Dict[str, Any]:
        if "llm" in self.summary_config:
            return self.summary_config["llm"]

        return self.config.get("llms", {}).get("summarization", {})

    def _get_llm_client(self):
        if self.llm_client is None:
            self.llm_client = build_llm_client_from_model_config(self._llm_config())
        return self.llm_client

    def _get_side_model(self) -> SIDEModel:
        if self.side_model is not None:
            return self.side_model

        side_cfg = self.summary_config.get("official_side", {})

        self.side_model = SIDEModel(
            model_dir=side_cfg.get("model_dir", "tools/SIDE_Model/hard-negatives"),
            device=side_cfg.get("device", "auto"),
            max_length=int(side_cfg.get("max_length", 512)),
            project_root=self.project_root,
        )

        return self.side_model

    def _get_llm_side_evaluator(self) -> LLMSIDEEvaluator:
        if self.llm_side_evaluator is not None:
            return self.llm_side_evaluator

        llm_side_config = dict(self.summary_config.get("llm_side", {}))

        base_llm_config = self._llm_config()

        llm_side_config.setdefault("provider", base_llm_config.get("provider", "openai"))
        llm_side_config.setdefault("model", base_llm_config.get("model", "gpt-4o"))
        llm_side_config.setdefault(
            "api_key_env",
            base_llm_config.get("api_key_env", "OPENAI_API_KEY"),
        )
        llm_side_config.setdefault("temperature", 0.0)
        llm_side_config.setdefault("max_retries", 30)
        llm_side_config.setdefault("retry_wait_seconds", 10)
        llm_side_config.setdefault("timeout_seconds", 120)
        llm_side_config.setdefault("reserved_response_tokens", 2000)
        llm_side_config.setdefault("max_total_tokens", 128000)

        self.llm_side_evaluator = LLMSIDEEvaluator(llm_side_config)
        return self.llm_side_evaluator

    def _call_llm(self, prompt: str) -> str:
        client = self._get_llm_client()

        if hasattr(client, "complete"):
            response = client.complete(prompt)
        elif hasattr(client, "generate"):
            response = client.generate(prompt)
        elif hasattr(client, "run"):
            response = client.run(prompt)
        elif callable(client):
            response = client(prompt)
        else:
            raise TypeError(
                "Unsupported LLM client interface. Expected complete(), "
                "generate(), run(), or callable client."
            )

        if isinstance(response, str):
            return response

        for attr in [
            "content",
            "text",
            "message",
            "output",
            "raw_text",
            "response",
        ]:
            if hasattr(response, attr):
                value = getattr(response, attr)
                if isinstance(value, str):
                    return value

        if isinstance(response, dict):
            for key in [
                "content",
                "text",
                "message",
                "output",
                "raw_text",
                "response",
            ]:
                value = response.get(key)
                if isinstance(value, str):
                    return value

        raise TypeError(
            f"LLM client returned unsupported response type: {type(response).__name__}. "
            f"Available attributes: {[name for name in dir(response) if not name.startswith('_')]}"
        )
