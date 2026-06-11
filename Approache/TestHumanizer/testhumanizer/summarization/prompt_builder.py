from __future__ import annotations


def build_source_summarization_prompt(class_code: str) -> str:
    """
    Build the source-code summarization prompt used before Scenario-3.

    The summary is meant to describe the class under test so that the
    summary-based refactoring scenario can use it as additional context.
    """
    return f"""
You are an expert software engineer with advanced knowledge of Java programming.

Your task is to summarize the following Java class. Focus on:
1. The overall purpose of the class.
2. The responsibilities of its main methods.
3. The role of important fields or variables.
4. Relationships between methods, especially helper methods, overloaded methods, or methods that collectively implement a behavior.
5. Any relevant behavior, edge cases, or assumptions that are useful for understanding how tests should be written or refactored.

Please follow these rules:
- Produce a concise but informative technical summary.
- Do not rewrite the code.
- Do not invent behavior not present in the code.
- Prefer concrete behavioral descriptions over generic statements.
- If the class has multiple logical sections, summarize them by section.
- The summary must be useful for refactoring generated unit tests into more readable and human-like tests.
- Put the complete summary between triple backticks ``` so it can be extracted automatically.

Here is the Java class to summarize:

{class_code}

Return only the summary between triple backticks.
"""
