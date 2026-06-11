from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console

from testhumanizer.llms.factory import get_refactoring_model_configs
from testhumanizer.prompts.builder import PromptBuilder
from testhumanizer.summarization.summary_store import SummaryStore
from testhumanizer.utils.tokens import count_tokens


console = Console()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def safe_id_part(value: str) -> str:
    return (
        str(value)
        .replace("/", "_")
        .replace("\\", "_")
        .replace("-", "_")
        .replace(".", "_")
        .replace(" ", "_")
    )


def read_jsonl(path: str | Path) -> List[Dict[str, Any]]:
    p = Path(path).expanduser().resolve()
    rows: List[Dict[str, Any]] = []

    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    return rows


def write_jsonl(path: str | Path, rows: List[Dict[str, Any]]) -> None:
    p = Path(path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: str | Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    p = Path(path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


class RefactoringPromptPreparer:
    def __init__(self, output_dir: str | Path, config: Dict[str, Any]) -> None:
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.config = config
        self.builder = PromptBuilder()

        self.summary_store = SummaryStore(
            self.output_dir / "03_summaries" / "source_summaries.jsonl"
        )

    def prepare(self, prepared_inputs_jsonl: str | Path) -> None:
        inputs = read_jsonl(prepared_inputs_jsonl)

        scenarios = self.config.get("refactoring", {}).get(
            "scenarios",
            ["tests-only", "code-centric", "summary-based"],
        )

        refactoring_models = get_refactoring_model_configs(self.config)

        prompt_rows: List[Dict[str, Any]] = []
        metadata_rows: List[Dict[str, Any]] = []

        for item in inputs:
            content = item["content"]
            static_part = content["static_part"]
            test_code = content["test_code"]
            class_source_code = content.get("class_source_code", "")

            fallback_summary = (
                f"This class is named {item['class_name']}. "
                "A generated source-code summary is not available for this target. "
                "Use the available source code, EvoSuite test suite, and test structure "
                "to preserve behavior while improving readability."
            )

            selected_summary_row = self.summary_store.get_summary_for(
                dataset=item.get("dataset", ""),
                project=item.get("project", ""),
                class_name=item.get("class_name", ""),
                bug_id=item.get("bug_id", "") or "",
            )

            selected_summary_text = ""
            selected_summary_side_score = ""
            selected_summary_status = ""

            if selected_summary_row:
                selected_summary_text = str(
                    selected_summary_row.get("summary_text", "") or ""
                ).strip()
                selected_summary_side_score = selected_summary_row.get(
                    "official_side_score",
                    "",
                )
                selected_summary_status = selected_summary_row.get(
                    "summary_status",
                    "",
                )

            for scenario in scenarios:
                summary_used = False
                summary_source = ""

                if scenario == "summary-based":
                    if selected_summary_text:
                        source_code_summary = selected_summary_text
                        summary_used = True
                        summary_source = "generated_summary"
                    else:
                        source_code_summary = item.get("source_code_summary") or fallback_summary
                        summary_used = bool(item.get("source_code_summary"))
                        summary_source = (
                            "prepared_input_summary"
                            if item.get("source_code_summary")
                            else "fallback_summary"
                        )
                else:
                    source_code_summary = None
                    summary_source = ""

                prompt = self.builder.build_refactoring_prompt(
                    scenario=scenario,
                    static_part=static_part,
                    test_code=test_code,
                    class_source_code=class_source_code,
                    source_code_summary=source_code_summary,
                )

                scenario_id = self.builder.scenario_id(scenario)
                prompt_sha256 = sha256_text(prompt)
                prompt_length_chars = len(prompt)

                for model_config in refactoring_models:
                    model_alias = model_config.get("name") or model_config.get("model")
                    provider = model_config.get("provider", "openai")
                    model_target = model_config.get("model", "unknown")

                    prompt_token_count = count_tokens(prompt, model=model_target)

                    prompt_id = "_".join(
                        [
                            item["id"],
                            scenario_id,
                            safe_id_part(model_alias),
                        ]
                    )

                    row = {
                        "id": prompt_id,
                        "input_id": item["id"],
                        "dataset": item["dataset"],
                        "project": item["project"],
                        "class_name": item["class_name"],
                        "bug_id": item.get("bug_id"),
                        "testsuite_id": item["testsuite_id"],
                        "scenario": scenario,
                        "scenario_id": scenario_id,
                        "model_alias": model_alias,
                        "provider": provider,
                        "model_target": model_target,
                        "prompt": prompt,
                        "prompt_sha256": prompt_sha256,
                        "prompt_length_chars": prompt_length_chars,
                        "prompt_token_count": prompt_token_count,
                        "summary_used": summary_used,
                        "summary_source": summary_source,
                        "summary_status": selected_summary_status,
                        "summary_official_side_score": selected_summary_side_score,
                    }

                    prompt_rows.append(row)

                    metadata_rows.append(
                        {
                            "id": prompt_id,
                            "input_id": item["id"],
                            "dataset": item["dataset"],
                            "project": item["project"],
                            "class_name": item["class_name"],
                            "bug_id": item.get("bug_id") or "",
                            "testsuite_id": item["testsuite_id"],
                            "scenario": scenario,
                            "scenario_id": scenario_id,
                            "model_alias": model_alias,
                            "provider": provider,
                            "model_target": model_target,
                            "prompt_sha256": prompt_sha256,
                            "prompt_length_chars": prompt_length_chars,
                            "prompt_token_count": prompt_token_count,
                            "summary_used": summary_used,
                            "summary_source": summary_source,
                            "summary_status": selected_summary_status,
                            "summary_official_side_score": selected_summary_side_score,
                        }
                    )

                    summary_info = ""
                    if scenario == "summary-based":
                        summary_info = (
                            f" summary_source={summary_source} "
                            f"SIDE={selected_summary_side_score}"
                        )

                    console.print(
                        f"[cyan]Prepared prompt[/cyan] "
                        f"{item['class_name']}/{item['testsuite_id']} "
                        f"{scenario_id} model={model_alias} "
                        f"chars={prompt_length_chars} tokens={prompt_token_count}"
                        f"{summary_info}"
                    )

        prompts_dir = self.output_dir / "04_refactorings" / "prompts"

        write_jsonl(
            prompts_dir / "refactoring_prompts.jsonl",
            prompt_rows,
        )

        write_csv(
            prompts_dir / "refactoring_prompts_metadata.csv",
            metadata_rows,
            [
                "id",
                "input_id",
                "dataset",
                "project",
                "class_name",
                "bug_id",
                "testsuite_id",
                "scenario",
                "scenario_id",
                "model_alias",
                "provider",
                "model_target",
                "prompt_sha256",
                "prompt_length_chars",
                "prompt_token_count",
                "summary_used",
                "summary_source",
                "summary_status",
                "summary_official_side_score",
            ],
        )

        console.print(
            f"[bold green]Prepared {len(prompt_rows)} refactoring prompts.[/bold green]"
        )

#########################################################""
# from __future__ import annotations

# import csv
# import hashlib
# import json
# from pathlib import Path
# from typing import Any, Dict, List

# from rich.console import Console

# from testhumanizer.llms.factory import get_refactoring_model_configs
# from testhumanizer.prompts.builder import PromptBuilder
# from testhumanizer.utils.tokens import count_tokens


# console = Console()


# def sha256_text(text: str) -> str:
#     return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


# def safe_id_part(value: str) -> str:
#     return (
#         str(value)
#         .replace("/", "_")
#         .replace("\\", "_")
#         .replace("-", "_")
#         .replace(".", "_")
#         .replace(" ", "_")
#     )


# def read_jsonl(path: str | Path) -> List[Dict[str, Any]]:
#     p = Path(path).expanduser().resolve()
#     rows: List[Dict[str, Any]] = []

#     with p.open("r", encoding="utf-8") as f:
#         for line in f:
#             line = line.strip()
#             if line:
#                 rows.append(json.loads(line))

#     return rows


# def write_jsonl(path: str | Path, rows: List[Dict[str, Any]]) -> None:
#     p = Path(path).expanduser().resolve()
#     p.parent.mkdir(parents=True, exist_ok=True)

#     with p.open("w", encoding="utf-8") as f:
#         for row in rows:
#             f.write(json.dumps(row, ensure_ascii=False) + "\n")


# def write_csv(path: str | Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
#     p = Path(path).expanduser().resolve()
#     p.parent.mkdir(parents=True, exist_ok=True)

#     with p.open("w", encoding="utf-8", newline="") as f:
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
#         writer.writeheader()
#         for row in rows:
#             writer.writerow(row)


# class RefactoringPromptPreparer:
#     def __init__(self, output_dir: str | Path, config: Dict[str, Any]) -> None:
#         self.output_dir = Path(output_dir).expanduser().resolve()
#         self.config = config
#         self.builder = PromptBuilder()

#     def prepare(self, prepared_inputs_jsonl: str | Path) -> None:
#         inputs = read_jsonl(prepared_inputs_jsonl)

#         scenarios = self.config.get("refactoring", {}).get(
#             "scenarios",
#             ["tests-only", "code-centric", "summary-based"],
#         )

#         refactoring_models = get_refactoring_model_configs(self.config)

#         prompt_rows: List[Dict[str, Any]] = []
#         metadata_rows: List[Dict[str, Any]] = []

#         for item in inputs:
#             content = item["content"]
#             static_part = content["static_part"]
#             test_code = content["test_code"]
#             class_source_code = content.get("class_source_code", "")

#             fallback_summary = (
#                 f"This class is named {item['class_name']}. "
#                 "A generated summary is not available yet. "
#                 "Use the available test suite structure to preserve behavior."
#             )

#             for scenario in scenarios:
#                 if scenario == "summary-based":
#                     source_code_summary = item.get("source_code_summary") or fallback_summary
#                 else:
#                     source_code_summary = None

#                 prompt = self.builder.build_refactoring_prompt(
#                     scenario=scenario,
#                     static_part=static_part,
#                     test_code=test_code,
#                     class_source_code=class_source_code,
#                     source_code_summary=source_code_summary,
#                 )

#                 scenario_id = self.builder.scenario_id(scenario)
#                 prompt_sha256 = sha256_text(prompt)
#                 prompt_length_chars = len(prompt)

#                 for model_config in refactoring_models:
#                     model_alias = model_config.get("name") or model_config.get("model")
#                     provider = model_config.get("provider", "openai")
#                     model_target = model_config.get("model", "unknown")

#                     prompt_token_count = count_tokens(prompt, model=model_target)

#                     prompt_id = "_".join(
#                         [
#                             item["id"],
#                             scenario_id,
#                             safe_id_part(model_alias),
#                         ]
#                     )

#                     row = {
#                         "id": prompt_id,
#                         "input_id": item["id"],
#                         "dataset": item["dataset"],
#                         "project": item["project"],
#                         "class_name": item["class_name"],
#                         "bug_id": item.get("bug_id"),
#                         "testsuite_id": item["testsuite_id"],
#                         "scenario": scenario,
#                         "scenario_id": scenario_id,
#                         "model_alias": model_alias,
#                         "provider": provider,
#                         "model_target": model_target,
#                         "prompt": prompt,
#                         "prompt_sha256": prompt_sha256,
#                         "prompt_length_chars": prompt_length_chars,
#                         "prompt_token_count": prompt_token_count,
#                     }

#                     prompt_rows.append(row)

#                     metadata_rows.append(
#                         {
#                             "id": prompt_id,
#                             "input_id": item["id"],
#                             "dataset": item["dataset"],
#                             "project": item["project"],
#                             "class_name": item["class_name"],
#                             "bug_id": item.get("bug_id") or "",
#                             "testsuite_id": item["testsuite_id"],
#                             "scenario": scenario,
#                             "scenario_id": scenario_id,
#                             "model_alias": model_alias,
#                             "provider": provider,
#                             "model_target": model_target,
#                             "prompt_sha256": prompt_sha256,
#                             "prompt_length_chars": prompt_length_chars,
#                             "prompt_token_count": prompt_token_count,
#                         }
#                     )

#                     console.print(
#                         f"[cyan]Prepared prompt[/cyan] "
#                         f"{item['class_name']}/{item['testsuite_id']} "
#                         f"{scenario_id} model={model_alias} "
#                         f"chars={prompt_length_chars} tokens={prompt_token_count}"
#                     )

#         prompts_dir = self.output_dir / "04_refactorings" / "prompts"

#         write_jsonl(
#             prompts_dir / "refactoring_prompts.jsonl",
#             prompt_rows,
#         )

#         write_csv(
#             prompts_dir / "refactoring_prompts_metadata.csv",
#             metadata_rows,
#             [
#                 "id",
#                 "input_id",
#                 "dataset",
#                 "project",
#                 "class_name",
#                 "bug_id",
#                 "testsuite_id",
#                 "scenario",
#                 "scenario_id",
#                 "model_alias",
#                 "provider",
#                 "model_target",
#                 "prompt_sha256",
#                 "prompt_length_chars",
#                 "prompt_token_count",
#             ],
#         )

#         console.print(
#             f"[bold green]Prepared {len(prompt_rows)} refactoring prompts.[/bold green]"
#         )
