from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable


def _split_csv(value: str | None) -> list[str] | None:
    if value is None:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def _ensure_path(config: Dict[str, Any], *keys: str) -> Dict[str, Any]:
    current = config
    for key in keys:
        current = current.setdefault(key, {})
    return current


def apply_cli_overrides(
    config: Dict[str, Any],
    *,
    models: str | None = None,
    temperature: float | None = None,
    iterations: int | None = None,
    scenarios: str | None = None,
    no_llm: bool = False,
    no_coverage: bool = False,
    output_dir: str | None = None,
) -> Dict[str, Any]:
    updated = deepcopy(config)

    if output_dir is not None:
        _ensure_path(updated, "experiment")["output_dir"] = output_dir

    selected_models = _split_csv(models)
    if selected_models is not None:
        llms = _ensure_path(updated, "llms")

        if "refactoring_models" not in llms:
            # Backward compatibility: convert single refactoring model to list.
            if "refactoring" in llms:
                model_config = dict(llms["refactoring"])
                model_config.setdefault("name", model_config.get("model", "refactoring_model"))
                llms["refactoring_models"] = [model_config]
            else:
                raise ValueError(
                    "--models was provided, but config has no llms.refactoring_models "
                    "or llms.refactoring section."
                )

        available = llms["refactoring_models"]
        available_names = {
            (model.get("name") or model.get("model")): model
            for model in available
        }

        missing = [name for name in selected_models if name not in available_names]
        if missing:
            raise ValueError(
                f"Unknown model alias(es): {missing}. "
                f"Available: {sorted(available_names)}"
            )

        llms["refactoring_models"] = [available_names[name] for name in selected_models]

    if temperature is not None:
        llms = _ensure_path(updated, "llms")

        if "refactoring_models" in llms:
            for model_config in llms["refactoring_models"]:
                model_config["temperature"] = temperature
        elif "refactoring" in llms:
            llms["refactoring"]["temperature"] = temperature
        else:
            raise ValueError(
                "--temperature was provided, but no refactoring LLM config was found."
            )

    if iterations is not None:
        _ensure_path(updated, "refactoring")["iterations"] = iterations

    selected_scenarios = _split_csv(scenarios)
    if selected_scenarios is not None:
        allowed = {"tests-only", "code-centric", "summary-based"}
        invalid = [s for s in selected_scenarios if s not in allowed]
        if invalid:
            raise ValueError(
                f"Unknown scenario(s): {invalid}. Allowed: {sorted(allowed)}"
            )
        _ensure_path(updated, "refactoring")["scenarios"] = selected_scenarios

    if no_llm:
        _ensure_path(updated, "llm_execution")["refactoring_outputs"] = False

    if no_coverage:
        _ensure_path(updated, "validation", "coverage")["enabled"] = False

    return updated
