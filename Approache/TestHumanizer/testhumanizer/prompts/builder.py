from __future__ import annotations

from testhumanizer.prompts.templates import (
    CODE_CENTRIC_REFACTORING_PROMPT,
    CODE_SUMMARIZATION_PROMPT,
    SUMMARY_BASED_REFACTORING_PROMPT,
    TESTS_ONLY_REFACTORING_PROMPT,
)


SCENARIO_IDS = {
    "tests-only": "Scenario-1",
    "code-centric": "Scenario-2",
    "summary-based": "Scenario-3",
}


class PromptBuilder:
    def build_refactoring_prompt(
        self,
        scenario: str,
        *,
        static_part: str,
        test_code: str,
        class_source_code: str | None = None,
        source_code_summary: str | None = None,
    ) -> str:
        if scenario == "tests-only":
            return TESTS_ONLY_REFACTORING_PROMPT.format(
                static_part=static_part,
                test_code=test_code,
            )

        if scenario == "code-centric":
            if class_source_code is None:
                raise ValueError("code-centric scenario requires class_source_code")

            return CODE_CENTRIC_REFACTORING_PROMPT.format(
                class_source_code=class_source_code,
                static_part=static_part,
                test_code=test_code,
            )

        if scenario == "summary-based":
            if source_code_summary is None:
                raise ValueError("summary-based scenario requires source_code_summary")

            return SUMMARY_BASED_REFACTORING_PROMPT.format(
                source_code_summary=source_code_summary,
                static_part=static_part,
                test_code=test_code,
            )

        raise ValueError(f"Unknown refactoring scenario: {scenario}")

    def build_summarization_prompt(self, *, class_code: str) -> str:
        return CODE_SUMMARIZATION_PROMPT.format(class_code=class_code)

    def scenario_id(self, scenario: str) -> str:
        if scenario not in SCENARIO_IDS:
            raise ValueError(f"Unknown scenario: {scenario}")
        return SCENARIO_IDS[scenario]
