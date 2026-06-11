from __future__ import annotations

from typing import Any, Dict

from testhumanizer.llms.base import LLMClient
from testhumanizer.llms.mistral_client import MistralChatClient
from testhumanizer.llms.openai_client import OpenAIChatClient


def build_llm_client_from_model_config(model_config: Dict[str, Any]) -> LLMClient:
    provider = model_config.get("provider", "openai")
    model = model_config.get("model", "gpt-4o")

    common_kwargs = {
        "model": model,
        "api_key_env": model_config.get(
            "api_key_env",
            "OPENAI_API_KEY" if provider == "openai" else "MISTRAL_API_KEY",
        ),
        "temperature": float(model_config.get("temperature", 0.1)),
        "max_retries": int(model_config.get("max_retries", 30)),
        "retry_wait_seconds": int(model_config.get("retry_wait_seconds", 10)),
        "timeout_seconds": int(model_config.get("timeout_seconds", 120)),
        "reserved_response_tokens": int(model_config.get("reserved_response_tokens", 16000)),
        "max_total_tokens": int(model_config.get("max_total_tokens", 128000)),
    }

    if provider == "openai":
        return OpenAIChatClient(**common_kwargs)

    if provider == "mistral":
        return MistralChatClient(**common_kwargs)

    raise ValueError(f"Unsupported LLM provider: {provider}")


def get_refactoring_model_configs(config: Dict[str, Any]) -> list[Dict[str, Any]]:
    llms_config = config.get("llms", {})

    if "refactoring_models" in llms_config:
        models = llms_config["refactoring_models"]
        if not isinstance(models, list) or not models:
            raise ValueError("llms.refactoring_models must be a non-empty list.")
        return models

    # Backward compatibility with the old single-model config.
    if "refactoring" in llms_config:
        model_config = dict(llms_config["refactoring"])
        model_config.setdefault("name", model_config.get("model", "refactoring_model"))
        return [model_config]

    raise ValueError(
        "No refactoring LLM configuration found. "
        "Expected llms.refactoring_models or llms.refactoring."
    )
