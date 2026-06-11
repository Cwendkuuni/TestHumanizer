from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class LLMResponse:
    provider: str
    model: str
    content: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    raw: Optional[Dict[str, Any]] = None


class LLMClient:
    provider: str
    model: str

    def complete(self, prompt: str) -> LLMResponse:
        raise NotImplementedError
