from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict

from testhumanizer.llms.factory import build_llm_client_from_model_config


_JSON_FENCE_PATTERN = re.compile(
    r"```(?:json)?\s*(.*?)```",
    re.DOTALL | re.IGNORECASE,
)


@dataclass
class LLMSIDEResult:
    ok: bool
    score: float | None
    faithfulness: float | None
    coverage: float | None
    conciseness: float | None
    hallucination_risk: float | None
    reason: str
    raw_output: str
    error: str = ""


def _extract_text_response(response: Any) -> str:
    if isinstance(response, str):
        return response

    for attr in ["content", "text", "message", "output", "raw_text", "response"]:
        if hasattr(response, attr):
            value = getattr(response, attr)
            if isinstance(value, str):
                return value

    if isinstance(response, dict):
        for key in ["content", "text", "message", "output", "raw_text", "response"]:
            value = response.get(key)
            if isinstance(value, str):
                return value

    raise TypeError(
        f"Unsupported LLM response type: {type(response).__name__}. "
        f"Available attributes: {[name for name in dir(response) if not name.startswith('_')]}"
    )


def _parse_json_response(raw_output: str) -> Dict[str, Any]:
    text = raw_output.strip()

    matches = _JSON_FENCE_PATTERN.findall(text)
    if matches:
        text = matches[0].strip()

    if not text.startswith("{"):
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]

    return json.loads(text)


def _safe_score(value: Any) -> float | None:
    try:
        score = float(value)
        return max(0.0, min(1.0, score))
    except (TypeError, ValueError):
        return None


class LLMSIDEEvaluator:
    """
    LLM-side evaluator.

    This is not the official SIDE metric. It is a soft, interpretable,
    LLM-based diagnostic score that evaluates whether a generated summary
    is faithful and useful for the provided Java source code.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = dict(config)
        self.config.setdefault("temperature", 0.0)
        self.config.setdefault("reserved_response_tokens", 2000)
        self.config.setdefault("max_total_tokens", 128000)
        self.client = build_llm_client_from_model_config(self.config)

    def score(self, source_code: str, summary: str) -> LLMSIDEResult:
        if not source_code or not source_code.strip():
            return LLMSIDEResult(
                ok=False,
                score=None,
                faithfulness=None,
                coverage=None,
                conciseness=None,
                hallucination_risk=None,
                reason="",
                raw_output="",
                error="Source code is empty.",
            )

        if not summary or not summary.strip():
            return LLMSIDEResult(
                ok=False,
                score=None,
                faithfulness=None,
                coverage=None,
                conciseness=None,
                hallucination_risk=None,
                reason="",
                raw_output="",
                error="Summary is empty.",
            )

        prompt = self._build_prompt(source_code, summary)

        try:
            if hasattr(self.client, "complete"):
                response = self.client.complete(prompt)
            elif hasattr(self.client, "generate"):
                response = self.client.generate(prompt)
            elif hasattr(self.client, "run"):
                response = self.client.run(prompt)
            elif callable(self.client):
                response = self.client(prompt)
            else:
                raise TypeError("Unsupported LLM client interface.")

            raw_output = _extract_text_response(response)
            data = _parse_json_response(raw_output)

            score = _safe_score(data.get("llm_side_score"))
            faithfulness = _safe_score(data.get("faithfulness"))
            coverage = _safe_score(data.get("coverage"))
            conciseness = _safe_score(data.get("conciseness"))
            hallucination_risk = _safe_score(data.get("hallucination_risk"))
            reason = str(data.get("reason", ""))

            if score is None:
                return LLMSIDEResult(
                    ok=False,
                    score=None,
                    faithfulness=faithfulness,
                    coverage=coverage,
                    conciseness=conciseness,
                    hallucination_risk=hallucination_risk,
                    reason=reason,
                    raw_output=raw_output,
                    error="Missing or invalid llm_side_score.",
                )

            return LLMSIDEResult(
                ok=True,
                score=score,
                faithfulness=faithfulness,
                coverage=coverage,
                conciseness=conciseness,
                hallucination_risk=hallucination_risk,
                reason=reason,
                raw_output=raw_output,
                error="",
            )

        except Exception as e:
            return LLMSIDEResult(
                ok=False,
                score=None,
                faithfulness=None,
                coverage=None,
                conciseness=None,
                hallucination_risk=None,
                reason="",
                raw_output="",
                error=f"{type(e).__name__}: {e}",
            )

    def _build_prompt(self, source_code: str, summary: str) -> str:
        return f"""
You are an expert software engineering evaluator.

Your task is to assess whether the provided natural-language summary is suitable for the given Java source code.

Evaluate the summary along four dimensions:

1. faithfulness:
   Does the summary accurately describe behavior that is actually present in the code?

2. coverage:
   Does the summary cover the important responsibilities, methods, fields, and relationships in the code?

3. conciseness:
   Is the summary informative without being unnecessarily verbose?

4. hallucination_risk:
   Does the summary invent behavior, assumptions, APIs, constraints, or responsibilities not supported by the code?

Return only strict JSON with this schema:

{{
  "llm_side_score": 0.0,
  "faithfulness": 0.0,
  "coverage": 0.0,
  "conciseness": 0.0,
  "hallucination_risk": 0.0,
  "reason": "brief explanation"
}}

Scoring rules:
- All numeric values must be between 0.0 and 1.0.
- llm_side_score should be high when the summary is faithful, useful, sufficiently complete, and not hallucinated.
- hallucination_risk should be high when the summary invents unsupported information.
- Do not reward generic summaries that could apply to many classes.
- Do not penalize the summary for using different wording than the code.
- Be strict but fair.

Java source code:

```java
{source_code}
```

Generated summary:

```text
{summary}
```
"""
