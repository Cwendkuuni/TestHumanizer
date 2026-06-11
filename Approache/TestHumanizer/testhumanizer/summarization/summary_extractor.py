from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class SummaryExtractionResult:
    ok: bool
    summary: str
    status: str
    error: str = ""


_CODE_FENCE_PATTERN = re.compile(
    r"```(?:text|markdown|java|summary)?\s*(.*?)```",
    re.DOTALL | re.IGNORECASE,
)


def extract_summary_from_response(
    response_text: str,
    *,
    require_code_fence: bool = True,
) -> SummaryExtractionResult:
    if not response_text or not response_text.strip():
        return SummaryExtractionResult(
            ok=False,
            summary="",
            status="empty_response",
            error="LLM response is empty.",
        )

    text = response_text.strip()
    matches = _CODE_FENCE_PATTERN.findall(text)

    if matches:
        summary = matches[0].strip()
        if summary:
            return SummaryExtractionResult(
                ok=True,
                summary=summary,
                status="ok",
                error="",
            )

        return SummaryExtractionResult(
            ok=False,
            summary="",
            status="empty_fenced_summary",
            error="A fenced block was found, but it was empty.",
        )

    if require_code_fence:
        return SummaryExtractionResult(
            ok=False,
            summary="",
            status="missing_code_fence",
            error="No triple-backtick summary block found.",
        )

    return SummaryExtractionResult(
        ok=True,
        summary=text,
        status="ok_no_fence",
        error="",
    )
