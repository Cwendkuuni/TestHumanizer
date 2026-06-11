from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from nltk.translate.meteor_score import meteor_score
from rouge_score import rouge_scorer

from testhumanizer.metrics.ctses.codebleu_subprocess import calculate_codebleu_subprocess
from testhumanizer.metrics.preprocessing import preprocess_java_code
from testhumanizer.utils.logging import THLogger
from testhumanizer.utils.nltk_resources import ensure_nltk_resources


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


def calculate_meteor(reference: str, prediction: str, log: THLogger | None = None) -> float:
    if not reference.strip() or not prediction.strip():
        return 0.0

    reference_tokens = reference.split()
    prediction_tokens = prediction.split()

    try:
        return float(
            meteor_score(
                [reference_tokens],
                prediction_tokens,
            )
        )
    except Exception as first_error:
        if log is not None:
            log.warning(
                f"METEOR WordNet failed once; retrying without WordNet fallback: "
                f"{type(first_error).__name__}: {first_error}"
            )

        try:
            from nltk.translate.meteor_score import single_meteor_score

            return float(
                single_meteor_score(
                    reference_tokens,
                    prediction_tokens,
                    wordnet=None,
                )
            )
        except Exception as second_error:
            if log is not None:
                log.warning(
                    f"METEOR fallback failed: "
                    f"{type(second_error).__name__}: {second_error}"
                )
            return 0.0


def calculate_rouge_l(reference: str, prediction: str) -> float:
    if not reference.strip() or not prediction.strip():
        return 0.0

    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=False)
    scores = scorer.score(reference, prediction)

    return float(scores["rougeL"].fmeasure)


def zero_codebleu_result(status: str, error: str = "") -> Dict[str, float | str]:
    return {
        "codebleu": 0.0,
        "ngram_match_score": 0.0,
        "weighted_ngram_match_score": 0.0,
        "syntax_match_score": 0.0,
        "dataflow_match_score": 0.0,
        "status": status,
        "error": error,
    }


def compute_ctses_aggregates(
    *,
    meteor: float,
    rouge_l: float,
    codebleu: float,
) -> Dict[str, float]:
    average_score_1 = (meteor + rouge_l + codebleu) / 3.0
    ctses_score_1 = 0.5 * codebleu + 0.3 * meteor + 0.2 * rouge_l
    ctses_score_2 = 0.4 * codebleu + 0.3 * meteor + 0.3 * rouge_l

    return {
        "average_score_1": round(float(average_score_1), 4),
        "CTSES_score_1": round(float(ctses_score_1), 4),
        "CTSES_score_2": round(float(ctses_score_2), 4),
    }


class CTSESEvaluator:
    def __init__(
        self,
        output_dir: str | Path,
        config: Dict[str, Any],
        project_root: str | Path,
    ) -> None:
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.config = config
        self.project_root = Path(project_root).expanduser().resolve()
        self.ctses_config = config.get("metrics", {}).get("ctses", {})
        self.log = THLogger(config)

    def evaluate(
        self,
        *,
        prepared_inputs_jsonl: str | Path,
        extracted_suites_jsonl: str | Path,
    ) -> None:
        self._prepare_nltk()

        prepared_inputs = read_jsonl(prepared_inputs_jsonl)
        extracted_suites = read_jsonl(extracted_suites_jsonl)

        prepared_by_key = {_key(row): row for row in prepared_inputs}

        rows: List[Dict[str, Any]] = []
        skipped_missing_original = 0
        codebleu_errors = 0

        preprocess = bool(self.ctses_config.get("preprocess", True))
        lang = self.ctses_config.get("codebleu_lang", "java")
        weights = self.ctses_config.get("codebleu_weights", [0.25, 0.25, 0.25, 0.25])
        codebleu_python = self.ctses_config.get(
            "codebleu_python",
            ".venv-codebleu/bin/python",
        )
        codebleu_timeout_seconds = int(
            self.ctses_config.get("codebleu_timeout_seconds", 120)
        )

        for suite in extracted_suites:
            key = _key(suite)
            original = prepared_by_key.get(key)

            if original is None:
                skipped_missing_original += 1
                self.log.warning(
                    f"CTSES skipped missing original for {suite.get('id')}."
                )
                continue

            original_code = original["content"]["full_test_code"]
            refactored_code = suite["content"]["refactored_test_code"]

            if preprocess:
                original_code_for_metrics = preprocess_java_code(original_code)
                refactored_code_for_metrics = preprocess_java_code(refactored_code)
            else:
                original_code_for_metrics = original_code
                refactored_code_for_metrics = refactored_code

            meteor_value = 0.0
            rouge_l_value = 0.0
            codebleu_values = zero_codebleu_result(status="disabled")

            if self.ctses_config.get("meteor", True):
                meteor_value = calculate_meteor(
                    original_code_for_metrics,
                    refactored_code_for_metrics,
                    log=self.log,
                )

            if self.ctses_config.get("rouge_l", True):
                rouge_l_value = calculate_rouge_l(
                    original_code_for_metrics,
                    refactored_code_for_metrics,
                )

            if self.ctses_config.get("codebleu", True):
                try:
                    codebleu_values = calculate_codebleu_subprocess(
                        original_code_for_metrics,
                        refactored_code_for_metrics,
                        codebleu_python=codebleu_python,
                        lang=lang,
                        weights=weights,
                        project_root=self.project_root,
                        timeout_seconds=codebleu_timeout_seconds,
                    )
                except Exception as e:
                    codebleu_errors += 1
                    codebleu_values = zero_codebleu_result(
                        status="error",
                        error=str(e),
                    )

            if codebleu_values.get("status") == "error":
                codebleu_errors += 1

            codebleu_score = float(codebleu_values.get("codebleu", 0.0))

            aggregates = compute_ctses_aggregates(
                meteor=meteor_value,
                rouge_l=rouge_l_value,
                codebleu=codebleu_score,
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
                "model_alias": suite.get("model_alias", ""),
                "provider": suite.get("provider", ""),
                "model": suite.get("model", ""),
                "METEOR": round(float(meteor_value), 4),
                "ROUGE-L": round(float(rouge_l_value), 4),
                "CodeBLEU": round(codebleu_score, 4),
                "N-gram Match": round(
                    float(codebleu_values.get("ngram_match_score", 0.0)),
                    4,
                ),
                "Weighted N-gram Match": round(
                    float(codebleu_values.get("weighted_ngram_match_score", 0.0)),
                    4,
                ),
                "Syntax Match": round(
                    float(codebleu_values.get("syntax_match_score", 0.0)),
                    4,
                ),
                "Dataflow Match": round(
                    float(codebleu_values.get("dataflow_match_score", 0.0)),
                    4,
                ),
                "CodeBLEU_status": codebleu_values.get("status", ""),
                "CodeBLEU_error": codebleu_values.get("error", ""),
                **aggregates,
            }

            rows.append(row)

            self.log.metric(
                f"CTSES {suite['class_name']}/{suite['scenario_id']}/"
                f"{suite.get('model_alias', '')}/iter_{suite['iteration']} "
                f"CodeBLEU={row['CodeBLEU']} "
                f"ROUGE-L={row['ROUGE-L']} "
                f"METEOR={row['METEOR']} "
                f"CTSES-1={row['CTSES_score_1']} "
                f"CodeBLEU_status={row['CodeBLEU_status']}"
            )

        metrics_dir = self.output_dir / "06_metrics" / "ctses"

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
            "model_alias",
            "provider",
            "model",
            "METEOR",
            "ROUGE-L",
            "CodeBLEU",
            "N-gram Match",
            "Weighted N-gram Match",
            "Syntax Match",
            "Dataflow Match",
            "CodeBLEU_status",
            "CodeBLEU_error",
            "average_score_1",
            "CTSES_score_1",
            "CTSES_score_2",
        ]

        write_csv(metrics_dir / "ctses_results.csv", rows, fieldnames)
        write_jsonl(metrics_dir / "ctses_results.jsonl", rows)

        ok_rows = sum(1 for row in rows if row.get("CodeBLEU_status") in {"ok", "disabled"})
        avg_ctses = (
            sum(float(row.get("CTSES_score_1", 0.0)) for row in rows) / len(rows)
            if rows
            else 0.0
        )

        self.log.success(
            f"CTSES evaluation completed: "
            f"rows={len(rows)}, ok={ok_rows}/{len(rows)}, "
            f"skipped_missing_original={skipped_missing_original}, "
            f"codebleu_errors={codebleu_errors}, "
            f"mean_ctses_1={avg_ctses:.4f}."
        )

    def _prepare_nltk(self) -> None:
        nltk_data_dir = self.ctses_config.get("nltk_data_dir")
        download_if_missing = bool(
            self.ctses_config.get("nltk_download_if_missing", True)
        )

        ensure_nltk_resources(
            nltk_data_dir=nltk_data_dir,
            download_if_missing=download_if_missing,
        )
