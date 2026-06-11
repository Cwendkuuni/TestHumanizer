from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from testhumanizer.metrics.embeddings.hf_embedder import HuggingFaceCodeEmbedder
from testhumanizer.metrics.embeddings.openai_embedder import OpenAIEmbeddingClient
from testhumanizer.metrics.preprocessing import preprocess_java_code
from testhumanizer.utils.logging import THLogger


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


def compute_cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(cosine_similarity(a.reshape(1, -1), b.reshape(1, -1))[0][0])


class EmbeddingSimilarityEvaluator:
    def __init__(self, output_dir: str | Path, config: Dict[str, Any]) -> None:
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.config = config
        self.embedding_config = config.get("metrics", {}).get("embeddings", {})
        self.log = THLogger(config)

        self._embedders: Dict[str, HuggingFaceCodeEmbedder] = {}
        self._openai_embedder: OpenAIEmbeddingClient | None = None

    def evaluate(
        self,
        *,
        prepared_inputs_jsonl: str | Path,
        extracted_suites_jsonl: str | Path,
    ) -> None:
        prepared_inputs = read_jsonl(prepared_inputs_jsonl)
        extracted_suites = read_jsonl(extracted_suites_jsonl)

        prepared_by_key = {_key(row): row for row in prepared_inputs}

        rows: List[Dict[str, Any]] = []
        skipped_missing_original = 0

        preprocess = bool(self.embedding_config.get("preprocess", True))
        enabled_models = self._enabled_hf_models()
        openai_config = self.embedding_config.get("openai", {})

        if not enabled_models and not openai_config.get("enabled", False):
            self.log.warning("No embedding models enabled.")
            return

        for suite in extracted_suites:
            key = _key(suite)
            original = prepared_by_key.get(key)

            if original is None:
                skipped_missing_original += 1
                self.log.warning(
                    f"Embedding similarity skipped: missing original for {suite.get('id')}."
                )
                continue

            original_code = original["content"]["full_test_code"]
            refactored_code = suite["content"]["refactored_test_code"]

            if preprocess:
                original_code_for_metrics = preprocess_java_code(
                    original_code,
                    remove_comments=True,
                )
                refactored_code_for_metrics = preprocess_java_code(
                    refactored_code,
                    remove_comments=True,
                )
            else:
                original_code_for_metrics = original_code
                refactored_code_for_metrics = refactored_code

            for model_alias, model_config in enabled_models.items():
                embedder = self._get_embedder(model_alias, model_config)

                try:
                    original_embedding = embedder.embed(original_code_for_metrics)
                    refactored_embedding = embedder.embed(refactored_code_for_metrics)

                    if original_embedding is None or refactored_embedding is None:
                        row = self._error_row(
                            suite,
                            model_alias=model_alias,
                            embedding_model=model_config["model_name"],
                            status="empty_input",
                            error="Original or refactored code is empty.",
                        )
                        rows.append(row)
                        self.log.warning(
                            f"Embedding empty input: {suite.get('id')} {model_alias}."
                        )
                        continue

                    cosine = compute_cosine(
                        original_embedding.embedding,
                        refactored_embedding.embedding,
                    )

                    row = {
                        "id": suite["id"],
                        "dataset": suite["dataset"],
                        "project": suite["project"],
                        "class_name": suite["class_name"],
                        "bug_id": suite.get("bug_id") or "",
                        "testsuite_id": suite["testsuite_id"],
                        "scenario": suite["scenario"],
                        "scenario_id": suite["scenario_id"],
                        "iteration": suite["iteration"],
                        "llm_model_alias": suite.get("model_alias", ""),
                        "provider": suite.get("provider", ""),
                        "llm_model": suite.get("model", ""),
                        "embedding_model_alias": model_alias,
                        "embedding_model_name": model_config["model_name"],
                        "device": original_embedding.device,
                        "cosine_similarity": round(cosine, 6),
                        "original_token_count": original_embedding.token_count,
                        "refactored_token_count": refactored_embedding.token_count,
                        "original_truncated": original_embedding.truncated,
                        "refactored_truncated": refactored_embedding.truncated,
                        "status": "ok",
                        "error": "",
                    }

                    rows.append(row)

                    self.log.metric(
                        f"Embedding similarity {suite['class_name']}/"
                        f"{suite['scenario_id']}/"
                        f"{suite.get('model_alias', '')}/iter_{suite['iteration']} "
                        f"{model_alias}={row['cosine_similarity']} "
                        f"device={row['device']}"
                    )

                except Exception as e:
                    rows.append(
                        self._error_row(
                            suite,
                            model_alias=model_alias,
                            embedding_model=model_config["model_name"],
                            status="error",
                            error=f"{type(e).__name__}: {e}",
                        )
                    )

                    self.log.warning(
                        f"Embedding failed: {suite.get('id')} {model_alias}: {e}"
                    )

            if openai_config.get("enabled", False):
                try:
                    openai_embedder = self._get_openai_embedder()

                    original_embedding = openai_embedder.embed(original_code_for_metrics)
                    refactored_embedding = openai_embedder.embed(refactored_code_for_metrics)

                    if original_embedding is None or refactored_embedding is None:
                        rows.append(
                            self._error_row(
                                suite,
                                model_alias="openai",
                                embedding_model=openai_config.get(
                                    "model_name",
                                    "text-embedding-3-small",
                                ),
                                status="empty_input",
                                error="Original or refactored code is empty.",
                            )
                        )
                        self.log.warning(
                            f"OpenAI embedding empty input: {suite.get('id')}."
                        )
                    else:
                        cosine = compute_cosine(
                            original_embedding.embedding,
                            refactored_embedding.embedding,
                        )

                        row = {
                            "id": suite["id"],
                            "dataset": suite["dataset"],
                            "project": suite["project"],
                            "class_name": suite["class_name"],
                            "bug_id": suite.get("bug_id") or "",
                            "testsuite_id": suite["testsuite_id"],
                            "scenario": suite["scenario"],
                            "scenario_id": suite["scenario_id"],
                            "iteration": suite["iteration"],
                            "llm_model_alias": suite.get("model_alias", ""),
                            "provider": suite.get("provider", ""),
                            "llm_model": suite.get("model", ""),
                            "embedding_model_alias": "openai",
                            "embedding_model_name": original_embedding.model_name,
                            "device": "api",
                            "cosine_similarity": round(cosine, 6),
                            "original_token_count": original_embedding.token_count or "",
                            "refactored_token_count": refactored_embedding.token_count or "",
                            "original_truncated": False,
                            "refactored_truncated": False,
                            "status": "ok",
                            "error": "",
                        }

                        rows.append(row)

                        self.log.metric(
                            f"Embedding similarity {suite['class_name']}/"
                            f"{suite['scenario_id']}/"
                            f"{suite.get('model_alias', '')}/iter_{suite['iteration']} "
                            f"openai={row['cosine_similarity']} "
                            f"cache_original={original_embedding.cached} "
                            f"cache_refactored={refactored_embedding.cached}"
                        )

                except Exception as e:
                    rows.append(
                        self._error_row(
                            suite,
                            model_alias="openai",
                            embedding_model=openai_config.get(
                                "model_name",
                                "text-embedding-3-small",
                            ),
                            status="error",
                            error=f"{type(e).__name__}: {e}",
                        )
                    )

                    self.log.warning(
                        f"OpenAI embedding failed: {suite.get('id')}: {e}"
                    )

        metrics_dir = self.output_dir / "06_metrics" / "embeddings"

        fieldnames = [
            "id",
            "dataset",
            "project",
            "class_name",
            "bug_id",
            "testsuite_id",
            "scenario",
            "scenario_id",
            "iteration",
            "llm_model_alias",
            "provider",
            "llm_model",
            "embedding_model_alias",
            "embedding_model_name",
            "device",
            "cosine_similarity",
            "original_token_count",
            "refactored_token_count",
            "original_truncated",
            "refactored_truncated",
            "status",
            "error",
        ]

        write_csv(metrics_dir / "embedding_similarity_results.csv", rows, fieldnames)
        write_jsonl(metrics_dir / "embedding_similarity_results.jsonl", rows)

        ok_rows = [row for row in rows if row.get("status") == "ok"]
        error_rows = [row for row in rows if row.get("status") != "ok"]

        model_means = self._mean_cosine_by_model(ok_rows)
        model_summary = ", ".join(
            f"{alias}={value:.4f}" for alias, value in sorted(model_means.items())
        )

        self.log.success(
            f"Embedding similarity evaluation completed: "
            f"rows={len(rows)}, ok={len(ok_rows)}/{len(rows)}, "
            f"errors={len(error_rows)}, "
            f"skipped_missing_original={skipped_missing_original}"
            f"{', mean_cosine: ' + model_summary if model_summary else ''}."
        )

    def _enabled_hf_models(self) -> Dict[str, Dict[str, Any]]:
        models: Dict[str, Dict[str, Any]] = {}

        codebert_config = self.embedding_config.get("codebert", {})
        if codebert_config.get("enabled", False):
            models["codebert"] = {
                "model_name": codebert_config.get(
                    "model_name",
                    "microsoft/codebert-base",
                ),
                "device": codebert_config.get("device", "auto"),
                "max_length": int(codebert_config.get("max_length", 512)),
            }

        graph_config = self.embedding_config.get("graphcodebert", {})
        if graph_config.get("enabled", False):
            models["graphcodebert"] = {
                "model_name": graph_config.get(
                    "model_name",
                    "microsoft/graphcodebert-base",
                ),
                "device": graph_config.get("device", "auto"),
                "max_length": int(graph_config.get("max_length", 512)),
            }

        return models

    def _get_embedder(
        self,
        model_alias: str,
        model_config: Dict[str, Any],
    ) -> HuggingFaceCodeEmbedder:
        if model_alias not in self._embedders:
            self.log.detail(
                f"Loading embedding model {model_alias}: {model_config['model_name']}"
            )

            self._embedders[model_alias] = HuggingFaceCodeEmbedder(
                model_name=model_config["model_name"],
                device=model_config.get("device", "auto"),
                max_length=int(model_config.get("max_length", 512)),
            )

        return self._embedders[model_alias]

    def _get_openai_embedder(self) -> OpenAIEmbeddingClient:
        if self._openai_embedder is not None:
            return self._openai_embedder

        openai_config = self.embedding_config.get("openai", {})
        cache_dir = self.output_dir / "06_metrics" / "embeddings" / "cache" / "openai"

        self._openai_embedder = OpenAIEmbeddingClient(
            model_name=openai_config.get("model_name", "text-embedding-3-small"),
            api_key_env=openai_config.get("api_key_env", "OPENAI_API_KEY"),
            max_retries=int(openai_config.get("max_retries", 30)),
            retry_wait_seconds=int(openai_config.get("retry_wait_seconds", 15)),
            timeout_seconds=int(openai_config.get("timeout_seconds", 120)),
            cache_dir=cache_dir,
            cache_enabled=bool(openai_config.get("cache_enabled", True)),
        )

        return self._openai_embedder

    def _error_row(
        self,
        suite: Dict[str, Any],
        *,
        model_alias: str,
        embedding_model: str,
        status: str,
        error: str,
    ) -> Dict[str, Any]:
        return {
            "id": suite.get("id", ""),
            "dataset": suite.get("dataset", ""),
            "project": suite.get("project", ""),
            "class_name": suite.get("class_name", ""),
            "bug_id": suite.get("bug_id") or "",
            "testsuite_id": suite.get("testsuite_id", ""),
            "scenario": suite.get("scenario", ""),
            "scenario_id": suite.get("scenario_id", ""),
            "iteration": suite.get("iteration", ""),
            "llm_model_alias": suite.get("model_alias", ""),
            "provider": suite.get("provider", ""),
            "llm_model": suite.get("model", ""),
            "embedding_model_alias": model_alias,
            "embedding_model_name": embedding_model,
            "device": "",
            "cosine_similarity": "",
            "original_token_count": "",
            "refactored_token_count": "",
            "original_truncated": "",
            "refactored_truncated": "",
            "status": status,
            "error": error,
        }

    def _mean_cosine_by_model(
        self,
        rows: List[Dict[str, Any]],
    ) -> Dict[str, float]:
        grouped: Dict[str, List[float]] = {}

        for row in rows:
            alias = str(row.get("embedding_model_alias", ""))
            value = row.get("cosine_similarity", "")

            try:
                grouped.setdefault(alias, []).append(float(value))
            except (TypeError, ValueError):
                continue

        return {
            alias: statistics.mean(values)
            for alias, values in grouped.items()
            if values
        }
