from __future__ import annotations

import tiktoken


def encoding_for_model_safe(model: str):
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        # Good fallback for recent OpenAI chat models.
        return tiktoken.get_encoding("o200k_base")


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    encoding = encoding_for_model_safe(model)
    return len(encoding.encode(text or ""))
