from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from rich.console import Console


console = Console()


Key = Tuple[str, str, str, str, str, str, str]


def _read_csv(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _as_str(value: Any) -> str:
    return str(value or "").strip()


def _as_bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value

    text = str(value or "").strip().lower()

    if text in {"true", "1", "yes", "y", "ok"}:
        return True

    if text in {"false", "0", "no", "n", "fail"}:
        return False

    return None


def _as_float(value: Any) -> Optional[float]:
    try:
        if value is None or str(value).strip() == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _first(row: Dict[str, Any], names: Iterable[str], default: Any = "") -> Any:
    for name in names:
        if name in row and row[name] not in {None, ""}:
            return row[name]
    return default


def _normalise_iteration(value: Any) -> str:
    text = _as_str(value)
    if text.startswith("iter_"):
        return text.replace("iter_", "")
    return text


def _candidate_key(row: Dict[str, Any]) -> Key:
    return (
        _as_str(_first(row, ["dataset"])),
        _as_str(_first(row, ["project"])),
        _as_str(_first(row, ["class_name", "class"])),
        _as_str(_first(row, ["bug_id"])),
        _as_str(_first(row, ["testsuite_id", "suite_id"])),
        _as_str(_first(row, ["scenario"])),
        _as_str(_first(row, ["model_alias", "model_name", "model"])),
    )


def _candidate_iteration(row: Dict[str, Any]) -> str:
    return _normalise_iteration(
        _first(
            row,
            [
                "iteration",
                "refactoring_iteration",
                "llm_iteration",
                "run_iteration",
                "candidate_iteration",
            ],
            "1",
        )
    )


def _candidate_full_key(row: Dict[str, Any]) -> Tuple[Key, str]:
    return _candidate_key(row), _candidate_iteration(row)


def _merge_row(base: Dict[str, Any], extra: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for key, value in extra.items():
        if key not in merged or merged[key] in {"", None}:
            merged[key] = value
        else:
            # Preserve original fields and namespace conflicting metric fields.
            if merged[key] != value and key not in {
                "dataset",
                "project",
                "class_name",
                "bug_id",
                "testsuite_id",
                "scenario",
                "model_alias",
                "iteration",
            }:
                merged[f"extra_{key}"] = value
    return merged


class CandidateSelector:
    """
    Selects the best refactored candidate per dataset/project/class/testsuite/scenario/model.

    This phase does not regenerate outputs. It uses all existing iterations already produced
    by Phase 5B and evaluated by Phases 7, 8 and 9.

    Default selection logic:
    - keep candidates that compile and pass JUnit when configured;
    - prefer the first valid candidate passing both cosine and CTSES thresholds;
    - otherwise keep the valid candidate with the best composite score;
    - if no valid candidate exists, keep the best candidate overall and mark it as unsafe.
    """

    def __init__(
        self,
        *,
        output_dir: str | Path,
        config: Dict[str, Any],
    ) -> None:
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.config = config
        self.selection_config = config.get("selection", {})

        self.require_compile_ok = bool(
            self.selection_config.get("hard_constraints", {}).get(
                "require_compile_ok",
                True,
            )
        )
        self.require_junit_ok = bool(
            self.selection_config.get("hard_constraints", {}).get(
                "require_junit_ok",
                True,
            )
        )

        cosine_cfg = self.selection_config.get("cosine_similarity", {})
        self.cosine_enabled = bool(cosine_cfg.get("enabled", True))
        self.cosine_threshold = float(cosine_cfg.get("threshold", 0.80))
        self.cosine_metric = cosine_cfg.get(
            "primary_metric",
            "openai_cosine_similarity",
        )
        self.primary_embedding_model_alias = str(
            cosine_cfg.get("primary_embedding_model_alias", "openai")
        ).strip().lower()


        ctses_cfg = self.selection_config.get("ctses", {})
        self.ctses_enabled = bool(ctses_cfg.get("enabled", True))
        self.ctses_threshold = float(ctses_cfg.get("threshold", 0.50))
        self.ctses_metric = ctses_cfg.get("primary_metric", "ctses_score")
        self.ctses_fallback_metric = ctses_cfg.get("fallback_metric", "codebleu_score")

        ranking_cfg = self.selection_config.get("ranking", {})
        self.cosine_weight = float(ranking_cfg.get("cosine_weight", 0.60))
        self.ctses_weight = float(ranking_cfg.get("ctses_weight", 0.40))

        output_cfg = self.selection_config.get("output", {})
        self.selection_dir = self.output_dir / output_cfg.get(
            "directory",
            "06_metrics/selection",
        )

    def run(self) -> None:
        candidates = self._load_candidates()

        if not candidates:
            console.print("[yellow]Candidate selection skipped: no candidates found.[/yellow]")
            return

        enriched = [self._score_candidate(row) for row in candidates]
        selected = self._select_by_group(enriched)

        for row in enriched:
            row["selected_candidate"] = False

        selected_ids = {row["candidate_id"] for row in selected}
        for row in enriched:
            if row["candidate_id"] in selected_ids:
                row["selected_candidate"] = True

        all_fieldnames = self._fieldnames(enriched)
        selected_fieldnames = self._fieldnames(selected)

        _write_csv(
            self.selection_dir / "candidate_selection_all.csv",
            enriched,
            all_fieldnames,
        )
        _write_csv(
            self.selection_dir / "selected_candidates.csv",
            selected,
            selected_fieldnames,
        )
        _write_jsonl(
            self.selection_dir / "candidate_selection_all.jsonl",
            enriched,
        )
        _write_jsonl(
            self.selection_dir / "selected_candidates.jsonl",
            selected,
        )

        passed = sum(1 for row in selected if row.get("passes_all_thresholds") is True)

        console.print(
            "[bold green]Candidate selection completed.[/bold green] "
            f"groups={len(selected)} selected={len(selected)} "
            f"threshold_pass={passed}/{len(selected)}"
        )

    def _load_candidates(self) -> List[Dict[str, Any]]:
        base_rows = self._load_extracted_candidates()

        by_full_key: Dict[Tuple[Key, str], Dict[str, Any]] = {}

        for row in base_rows:
            key = _candidate_full_key(row)
            by_full_key[key] = self._normalise_base_candidate(row)

        for metric_row in self._load_refactored_validation_rows():
            self._merge_metric_row(by_full_key, metric_row)

        for metric_row in self._load_ctses_rows():
            self._merge_metric_row(by_full_key, metric_row)

        for metric_row in self._load_embedding_rows():
            self._merge_metric_row(by_full_key, metric_row)

        return list(by_full_key.values())

    def _load_extracted_candidates(self) -> List[Dict[str, Any]]:
        candidates = []

        likely_paths = [
            self.output_dir
            / "04_refactorings"
            / "extracted_suites"
            / "extracted_refactored_suites_metadata.csv",
            self.output_dir
            / "04_refactorings"
            / "extracted_suites"
            / "extracted_refactored_suites.csv",
        ]

        for path in likely_paths:
            rows = _read_csv(path)
            if rows:
                candidates.extend(rows)

        return candidates

    def _load_refactored_validation_rows(self) -> List[Dict[str, Any]]:
        root = self.output_dir / "05_validation"
        return self._read_all_csvs(root)

    def _load_ctses_rows(self) -> List[Dict[str, Any]]:
        root = self.output_dir / "06_metrics" / "ctses"
        return self._read_all_csvs(root)

    # def _load_embedding_rows(self) -> List[Dict[str, Any]]:
    #     root = self.output_dir / "06_metrics" / "embeddings"
    #     return self._read_all_csvs(root)

    def _load_embedding_rows(self) -> List[Dict[str, Any]]:
        root = self.output_dir / "06_metrics" / "embeddings"
        rows = self._read_all_csvs(root)

        if not rows:
            return []

        selected_rows: List[Dict[str, Any]] = []

        for row in rows:
            embedding_alias = str(row.get("embedding_model_alias", "") or "").strip().lower()
            embedding_name = str(row.get("embedding_model_name", "") or "").strip().lower()

            is_primary = (
                embedding_alias == self.primary_embedding_model_alias
                or self.primary_embedding_model_alias in embedding_name
            )

            if not is_primary:
                continue

            normalized = dict(row)

            # Important:
            # The embeddings evaluator stores similarities in long format:
            # one row per embedding model, with the score in "cosine_similarity".
            # The selector expects a single primary cosine field.
            normalized["openai_cosine_similarity"] = row.get("cosine_similarity", "")
            normalized["selection_embedding_model_alias"] = row.get("embedding_model_alias", "")
            normalized["selection_embedding_model_name"] = row.get("embedding_model_name", "")

            # Harmonize model field name for matching with extracted candidates.
            if "model_alias" not in normalized and row.get("llm_model_alias"):
                normalized["model_alias"] = row.get("llm_model_alias")

            selected_rows.append(normalized)

        return selected_rows



    def _read_all_csvs(self, root: Path) -> List[Dict[str, Any]]:
        if not root.exists():
            return []

        rows: List[Dict[str, Any]] = []
        for path in sorted(root.rglob("*.csv")):
            rows.extend(_read_csv(path))
        return rows

    def _normalise_base_candidate(self, row: Dict[str, Any]) -> Dict[str, Any]:
        dataset = _as_str(_first(row, ["dataset"]))
        project = _as_str(_first(row, ["project"]))
        class_name = _as_str(_first(row, ["class_name", "class"]))
        bug_id = _as_str(_first(row, ["bug_id"]))
        testsuite_id = _as_str(_first(row, ["testsuite_id", "suite_id"]))
        scenario = _as_str(_first(row, ["scenario"]))
        model_alias = _as_str(_first(row, ["model_alias", "model_name", "model"]))
        iteration = _candidate_iteration(row)

        candidate_id = "_".join(
            [
                dataset or "dataset",
                project or "project",
                class_name or "class",
                bug_id or "NA",
                testsuite_id or "suite",
                scenario or "scenario",
                model_alias or "model",
                f"iter_{iteration}",
            ]
        )

        normalised = dict(row)
        normalised.update(
            {
                "candidate_id": candidate_id,
                "dataset": dataset,
                "project": project,
                "class_name": class_name,
                "bug_id": bug_id,
                "testsuite_id": testsuite_id,
                "scenario": scenario,
                "model_alias": model_alias,
                "iteration": iteration,
            }
        )

        return normalised

    def _merge_metric_row(
        self,
        by_full_key: Dict[Tuple[Key, str], Dict[str, Any]],
        metric_row: Dict[str, Any],
    ) -> None:
        key = _candidate_full_key(metric_row)

        if key in by_full_key:
            by_full_key[key] = _merge_row(by_full_key[key], metric_row)

    def _score_candidate(self, row: Dict[str, Any]) -> Dict[str, Any]:
        scored = dict(row)

        compile_ok = _as_bool(
            _first(
                row,
                [
                    "compile_ok",
                    "compilation_ok",
                    "refactored_compile_ok",
                    "compiled",
                ],
                "",
            )
        )
        junit_ok = _as_bool(
            _first(
                row,
                [
                    "junit_ok",
                    "tests_ok",
                    "refactored_junit_ok",
                    "junit_success",
                ],
                "",
            )
        )

        cosine_score = self._get_metric_score(
            row,
            preferred=self.cosine_metric,
            fallbacks=[
                "openai_cosine_similarity",
                "openai_similarity",
                "openai_embedding_cosine",
                "cosine_openai",
                "semantic_similarity_openai",
            ],
        )

        ctses_score = self._get_metric_score(
            row,
            preferred=self.ctses_metric,
            fallbacks=[
                self.ctses_fallback_metric,
                "ctses_score",
                "codebleu_score",
                "codebleu",
                "CodeBLEU",
            ],
        )

        compile_pass = True if not self.require_compile_ok else compile_ok is True
        junit_pass = True if not self.require_junit_ok else junit_ok is True

        cosine_pass = (
            True
            if not self.cosine_enabled
            else cosine_score is not None and cosine_score >= self.cosine_threshold
        )
        ctses_pass = (
            True
            if not self.ctses_enabled
            else ctses_score is not None and ctses_score >= self.ctses_threshold
        )

        validation_pass = compile_pass and junit_pass
        passes_all_thresholds = validation_pass and cosine_pass and ctses_pass

        composite_score = self._composite_score(cosine_score, ctses_score)

        scored.update(
            {
                "compile_ok_normalized": compile_ok,
                "junit_ok_normalized": junit_ok,
                "validation_pass": validation_pass,
                "selection_cosine_metric": self.cosine_metric,
                "selection_cosine_score": cosine_score if cosine_score is not None else "",
                "selection_cosine_threshold": self.cosine_threshold,
                "selection_cosine_pass": cosine_pass,
                "selection_ctses_metric": self.ctses_metric,
                "selection_ctses_score": ctses_score if ctses_score is not None else "",
                "selection_ctses_threshold": self.ctses_threshold,
                "selection_ctses_pass": ctses_pass,
                "selection_composite_score": composite_score,
                "passes_all_thresholds": passes_all_thresholds,
            }
        )

        return scored

    def _get_metric_score(
        self,
        row: Dict[str, Any],
        *,
        preferred: str,
        fallbacks: List[str],
    ) -> Optional[float]:
        candidates = [preferred] + [name for name in fallbacks if name != preferred]

        for name in candidates:
            if name in row:
                value = _as_float(row.get(name))
                if value is not None:
                    return value

        # Last fallback: fuzzy search for OpenAI cosine or CTSES/codebleu-like fields.
        preferred_lower = preferred.lower()

        for key, value in row.items():
            key_lower = key.lower()
            if preferred_lower in key_lower:
                parsed = _as_float(value)
                if parsed is not None:
                    return parsed

        return None

    def _composite_score(
        self,
        cosine_score: Optional[float],
        ctses_score: Optional[float],
    ) -> float:
        total_weight = 0.0
        score = 0.0

        if cosine_score is not None:
            score += self.cosine_weight * cosine_score
            total_weight += self.cosine_weight

        if ctses_score is not None:
            score += self.ctses_weight * ctses_score
            total_weight += self.ctses_weight

        if total_weight == 0.0:
            return float("-inf")

        return score / total_weight

    def _select_by_group(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        groups: Dict[Key, List[Dict[str, Any]]] = {}

        for row in rows:
            groups.setdefault(_candidate_key(row), []).append(row)

        selected: List[Dict[str, Any]] = []

        for key, group_rows in groups.items():
            group_rows = sorted(
                group_rows,
                key=lambda r: int(_as_float(r.get("iteration")) or 999999),
            )

            selected_row = self._select_one(group_rows)
            selected.append(selected_row)

        return selected

    def _select_one(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        passing = [row for row in rows if row.get("passes_all_thresholds") is True]

        if passing:
            chosen = dict(passing[0])
            chosen["selection_reason"] = "first_candidate_passing_all_thresholds"
            return chosen

        valid = [row for row in rows if row.get("validation_pass") is True]

        if valid:
            chosen = max(
                valid,
                key=lambda r: float(r.get("selection_composite_score", float("-inf"))),
            )
            chosen = dict(chosen)
            chosen["selection_reason"] = (
                "best_valid_candidate_below_threshold_or_missing_metric"
            )
            return chosen

        chosen = max(
            rows,
            key=lambda r: float(r.get("selection_composite_score", float("-inf"))),
        )
        chosen = dict(chosen)
        chosen["selection_reason"] = "best_candidate_but_validation_failed_or_missing"
        return chosen

    def _fieldnames(self, rows: List[Dict[str, Any]]) -> List[str]:
        preferred = [
            "candidate_id",
            "selected_candidate",
            "selection_reason",
            "dataset",
            "project",
            "class_name",
            "bug_id",
            "testsuite_id",
            "scenario",
            "model_alias",
            "iteration",
            "compile_ok_normalized",
            "junit_ok_normalized",
            "validation_pass",
            "selection_cosine_metric",
            "selection_cosine_score",
            "selection_cosine_threshold",
            "selection_cosine_pass",
            "selection_ctses_metric",
            "selection_ctses_score",
            "selection_ctses_threshold",
            "selection_ctses_pass",
            "selection_composite_score",
            "passes_all_thresholds",
        ]

        all_keys = set()
        for row in rows:
            all_keys.update(row.keys())

        return preferred + sorted(key for key in all_keys if key not in preferred)
