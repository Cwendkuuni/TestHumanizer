from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


FENCED_CODE_BLOCK_RE = re.compile(
    r"```(?:java|Java|JAVA)?\s*(.*?)```",
    re.DOTALL,
)


@dataclass
class ExtractedCode:
    code: Optional[str]
    status: str
    extraction_strategy: str
    message: str


def _looks_like_java_test_suite(text: str) -> bool:
    required_markers = [
        "class ",
        "@Test",
    ]
    return all(marker in text for marker in required_markers)


def clean_extracted_code(code: str) -> str:
    code = code.strip()

    # Sometimes the model starts with labels before code.
    code = re.sub(r"^\s*(Here is|Below is).*?:\s*", "", code, flags=re.IGNORECASE)

    # Remove accidental leading/trailing markdown remnants.
    code = code.replace("```java", "").replace("```Java", "").replace("```", "")
    code = code.strip()

    return code


def extract_java_code_from_llm_output(output: str) -> ExtractedCode:
    if not output or not output.strip():
        return ExtractedCode(
            code=None,
            status="empty_output",
            extraction_strategy="none",
            message="LLM output is empty.",
        )

    matches = FENCED_CODE_BLOCK_RE.findall(output)

    if matches:
        cleaned_blocks = [clean_extracted_code(match) for match in matches]

        java_like_blocks = [
            block for block in cleaned_blocks
            if _looks_like_java_test_suite(block)
        ]

        if java_like_blocks:
            # Prefer the longest Java-like block because the prompt asks for the full suite.
            best = max(java_like_blocks, key=len)
            return ExtractedCode(
                code=best,
                status="ok",
                extraction_strategy="fenced_java_like_block",
                message="Extracted Java-like code from fenced block.",
            )

        # Fallback: take the longest fenced block.
        best = max(cleaned_blocks, key=len)
        return ExtractedCode(
            code=best,
            status="ok_without_java_markers",
            extraction_strategy="longest_fenced_block",
            message="Extracted longest fenced block, but Java markers were incomplete.",
        )

    # Fallback for models that ignore fences but output a full Java file.
    cleaned = clean_extracted_code(output)

    if _looks_like_java_test_suite(cleaned):
        return ExtractedCode(
            code=cleaned,
            status="ok_no_fence",
            extraction_strategy="raw_java_like_output",
            message="No fenced block found; raw output looks like Java test suite.",
        )

    return ExtractedCode(
        code=None,
        status="no_code_found",
        extraction_strategy="none",
        message="Could not find a Java code block in the LLM output.",
    )
