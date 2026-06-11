from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table

from testhumanizer.core.artifacts import TargetClass
from testhumanizer.core.targets import load_targets
from testhumanizer.utils.io import ensure_dir, write_csv, write_jsonl
from testhumanizer.utils.logging import THLogger

from testhumanizer.generators.evosuite import EvoSuiteGenerator
from testhumanizer.generators.indexing import save_generated_suites

from testhumanizer.validation.original_validator import OriginalSuiteValidator
from testhumanizer.validation.refactored_validator import RefactoredSuiteValidator

from testhumanizer.refactoring.input_preparer import RefactoringInputPreparer
from testhumanizer.refactoring.prompt_preparer import RefactoringPromptPreparer
from testhumanizer.refactoring.llm_refactorer import LLMRefactorer
from testhumanizer.refactoring.output_extractor import RefactoredOutputExtractor

from testhumanizer.metrics.ctses.evaluator import CTSESEvaluator
from testhumanizer.metrics.embeddings.evaluator import EmbeddingSimilarityEvaluator
from testhumanizer.metrics.readability.evaluator import ReadabilityEvaluator
from testhumanizer.metrics.complexity.evaluator import CCTRComplexityEvaluator
from testhumanizer.metrics.complexity.pmd_evaluator import PMDComplexityEvaluator

from testhumanizer.summarization.source_summarizer import SourceSummarizer
from testhumanizer.selection.candidate_selector import CandidateSelector
from testhumanizer.reports.synthetic_report import SyntheticReportGenerator


console = Console()


class TestHumanizerPipeline:
    def __init__(self, config: Dict[str, Any], config_path: str | Path) -> None:
        self.config = config
        self.config_path = Path(config_path).expanduser().resolve()
        self.output_dir = ensure_dir(config["experiment"]["output_dir"])
        self.log = THLogger(config)

    def run(self) -> None:
        self._prepare_run_dir()

        # Phase 1: load and index targets
        self.log.phase("1", "Load and index target classes")

        targets = self._load_targets()
        self._print_targets(targets)
        self._save_targets(targets)

        self.log.success(f"Targets loaded and indexed: {len(targets)} classes.")

        # Phase 2: generate EvoSuite suites
        self.log.phase("2", "Generate EvoSuite test suites")

        generated_suites = []

        if self.config.get("test_generation", {}).get("enabled", False):
            generated_suites = self._run_test_generation(targets)

            save_generated_suites(
                self.output_dir / "02_evosuite",
                generated_suites,
            )

            self.log.success(
                f"EvoSuite generation completed: {len(generated_suites)} suites indexed."
            )
        else:
            self.log.warning("Test generation disabled in config.")

        original_suites_metadata = (
            self.output_dir / "02_evosuite" / "original_suites_metadata.csv"
        )

        # Phase 3: compile, run, and optionally cover original EvoSuite suites
        self.log.phase("3", "Validate original EvoSuite suites")

        validation_config = self.config.get("validation", {})
        compilation_config = validation_config.get("compilation", {})

        if compilation_config.get("enabled", False) and generated_suites:
            validator = OriginalSuiteValidator(
                config=self.config,
                project_root=Path.cwd(),
                output_dir=self.output_dir,
            )

            validator.validate(original_suites_metadata)

            self.log.success("Original EvoSuite suites validated.")
        else:
            self.log.warning("Original suite validation disabled or no generated suites.")

        # Phase 4: prepare LLM refactoring inputs
        self.log.phase("4", "Prepare LLM refactoring inputs")

        preparation_config = self.config.get("preparation", {})

        if preparation_config.get("refactoring_inputs", False):
            if not original_suites_metadata.exists():
                self.log.warning(
                    "Refactoring input preparation skipped: "
                    "original_suites_metadata.csv not found."
                )
            else:
                input_preparer = RefactoringInputPreparer(output_dir=self.output_dir)

                input_preparer.prepare(
                    original_suites_csv=original_suites_metadata,
                    targets_csv=self.output_dir / "01_targets" / "targets_resolved.csv",
                )

                self.log.success("LLM refactoring inputs prepared.")
        else:
            self.log.warning("Refactoring input preparation disabled.")

        # Phase 4.5: source-code summarization + optional SIDE validation
        self.log.phase("4.5", "Generate and evaluate source-code summaries")

        summarization_config = self.config.get("summarization", {})

        if summarization_config.get("enabled", False):
            summaries_dir = self.output_dir / "03_summaries"
            summaries_dir.mkdir(parents=True, exist_ok=True)

            summarizer = SourceSummarizer(
                output_dir=self.output_dir,
                config=self.config,
                project_root=Path.cwd(),
            )

            summarizer.summarize_targets([self._target_to_record(t) for t in targets])

            self.log.success("Source-code summaries generated and evaluated.")
        else:
            self.log.warning("Source-code summarization disabled.")

        # Phase 5A: prepare prompts for each refactoring scenario
        self.log.phase("5A", "Prepare refactoring prompts")

        if preparation_config.get("refactoring_prompts", False):
            prepared_inputs_path = (
                self.output_dir / "04_refactorings" / "prepared_inputs.jsonl"
            )

            if not prepared_inputs_path.exists():
                self.log.warning(
                    "Refactoring prompt preparation skipped: "
                    "prepared_inputs.jsonl not found."
                )
            else:
                prompt_preparer = RefactoringPromptPreparer(
                    output_dir=self.output_dir,
                    config=self.config,
                )

                prompt_preparer.prepare(prepared_inputs_path)

                self.log.success("LLM refactoring prompts prepared.")
        else:
            self.log.warning("Refactoring prompt preparation disabled.")

        # Phase 5B: call LLMs and save raw refactoring outputs
        self.log.phase("5B", "Run LLM refactoring")

        llm_execution_config = self.config.get("llm_execution", {})

        if llm_execution_config.get("refactoring_outputs", False):
            prompts_path = (
                self.output_dir
                / "04_refactorings"
                / "prompts"
                / "refactoring_prompts.jsonl"
            )

            if not prompts_path.exists():
                self.log.warning(
                    "LLM refactoring skipped: refactoring_prompts.jsonl not found."
                )
            else:
                llm_refactorer = LLMRefactorer(
                    output_dir=self.output_dir,
                    config=self.config,
                )

                llm_refactorer.run(prompts_path)

                self.log.success("Raw LLM refactoring outputs saved.")
        else:
            self.log.warning("LLM refactoring execution disabled.")

        # Phase 6: extract Java code from raw LLM outputs and reconstruct suites
        self.log.phase("6", "Extract Java and reconstruct refactored suites")

        extraction_config = self.config.get("extraction", {})

        if extraction_config.get("refactored_suites", False):
            raw_outputs_path = (
                self.output_dir
                / "04_refactorings"
                / "llm_outputs"
                / "raw_refactoring_outputs.jsonl"
            )

            prepared_inputs_path = (
                self.output_dir / "04_refactorings" / "prepared_inputs.jsonl"
            )

            if not raw_outputs_path.exists():
                self.log.warning(
                    "Refactored suite extraction skipped: raw_refactoring_outputs.jsonl not found."
                )
            elif not prepared_inputs_path.exists():
                self.log.warning(
                    "Refactored suite extraction skipped: prepared_inputs.jsonl not found."
                )
            else:
                #extractor = RefactoredOutputExtractor(output_dir=self.output_dir)
                extractor = RefactoredOutputExtractor(
                    output_dir=self.output_dir,
                    config=self.config,
                )

                extractor.extract(
                    raw_outputs_jsonl=raw_outputs_path,
                    prepared_inputs_jsonl=prepared_inputs_path,
                )

                self.log.success("Java code extracted and refactored suites reconstructed.")
        else:
            self.log.warning("Refactored suite extraction disabled.")

        # Phase 7: validate refactored suites
        self.log.phase("7", "Validate refactored test suites")

        refactored_validation_config = (
            self.config.get("validation", {}).get("refactored", {})
        )

        if refactored_validation_config.get("enabled", False):
            extracted_suites_csv = (
                self.output_dir
                / "04_refactorings"
                / "extracted_suites"
                / "extracted_refactored_suites_metadata.csv"
            )

            if not extracted_suites_csv.exists():
                self.log.warning(
                    "Refactored validation skipped: "
                    "extracted_refactored_suites_metadata.csv not found."
                )
            else:
                refactored_validator = RefactoredSuiteValidator(
                    config=self.config,
                    project_root=Path.cwd(),
                    output_dir=self.output_dir,
                )

                refactored_validator.validate(extracted_suites_csv)

                self.log.success("Refactored suites validated.")
        else:
            self.log.warning("Refactored suite validation disabled.")

        # Phase 8: CTSES metrics
        self.log.phase("8", "Compute CTSES metrics")

        ctses_config = self.config.get("metrics", {}).get("ctses", {})

        if ctses_config.get("enabled", False):
            prepared_inputs_jsonl = (
                self.output_dir / "04_refactorings" / "prepared_inputs.jsonl"
            )

            extracted_suites_jsonl = (
                self.output_dir
                / "04_refactorings"
                / "extracted_suites"
                / "extracted_refactored_suites.jsonl"
            )

            if not prepared_inputs_jsonl.exists():
                self.log.warning("CTSES skipped: prepared_inputs.jsonl not found.")
            elif not extracted_suites_jsonl.exists():
                self.log.warning("CTSES skipped: extracted_refactored_suites.jsonl not found.")
            else:
                ctses_evaluator = CTSESEvaluator(
                    output_dir=self.output_dir,
                    config=self.config,
                    project_root=Path.cwd(),
                )

                ctses_evaluator.evaluate(
                    prepared_inputs_jsonl=prepared_inputs_jsonl,
                    extracted_suites_jsonl=extracted_suites_jsonl,
                )

                self.log.success("CTSES metrics computed.")
        else:
            self.log.warning("CTSES evaluation disabled.")

        # Phase 9: embedding-based cosine similarity
        self.log.phase("9", "Compute embedding cosine similarity")

        embeddings_config = self.config.get("metrics", {}).get("embeddings", {})

        if embeddings_config.get("enabled", False):
            prepared_inputs_jsonl = (
                self.output_dir / "04_refactorings" / "prepared_inputs.jsonl"
            )

            extracted_suites_jsonl = (
                self.output_dir
                / "04_refactorings"
                / "extracted_suites"
                / "extracted_refactored_suites.jsonl"
            )

            if not prepared_inputs_jsonl.exists():
                self.log.warning(
                    "Embedding similarity skipped: prepared_inputs.jsonl not found."
                )
            elif not extracted_suites_jsonl.exists():
                self.log.warning(
                    "Embedding similarity skipped: extracted_refactored_suites.jsonl not found."
                )
            else:
                embedding_evaluator = EmbeddingSimilarityEvaluator(
                    output_dir=self.output_dir,
                    config=self.config,
                )

                embedding_evaluator.evaluate(
                    prepared_inputs_jsonl=prepared_inputs_jsonl,
                    extracted_suites_jsonl=extracted_suites_jsonl,
                )

                self.log.success("Embedding cosine similarity metrics computed.")
        else:
            self.log.warning("Embedding similarity evaluation disabled.")

        # Phase 10: Scalabrino readability
        self.log.phase("10", "Compute Scalabrino readability")

        readability_config = self.config.get("metrics", {}).get("readability", {})

        if readability_config.get("enabled", False) and readability_config.get("scalabrino", False):
            original_suites_csv = (
                self.output_dir / "02_evosuite" / "original_suites_metadata.csv"
            )

            extracted_suites_csv = (
                self.output_dir
                / "04_refactorings"
                / "extracted_suites"
                / "extracted_refactored_suites_metadata.csv"
            )

            if not original_suites_csv.exists():
                self.log.warning(
                    "Readability skipped: original_suites_metadata.csv not found."
                )
            elif not extracted_suites_csv.exists():
                self.log.warning(
                    "Readability skipped: extracted_refactored_suites_metadata.csv not found."
                )
            else:
                readability_evaluator = ReadabilityEvaluator(
                    output_dir=self.output_dir,
                    config=self.config,
                    project_root=Path.cwd(),
                )

                readability_evaluator.evaluate(
                    original_suites_csv=original_suites_csv,
                    extracted_suites_csv=extracted_suites_csv,
                )

                self.log.success("Scalabrino readability metrics computed.")
        else:
            self.log.warning("Readability evaluation disabled.")

        # Phase 11: CCTR cognitive complexity
        self.log.phase("11", "Compute CCTR cognitive complexity")

        complexity_config = self.config.get("metrics", {}).get("complexity", {})
        cctr_config = complexity_config.get("cctr", {})

        if complexity_config.get("enabled", False) and cctr_config.get("enabled", False):
            original_suites_csv = (
                self.output_dir / "02_evosuite" / "original_suites_metadata.csv"
            )

            extracted_suites_csv = (
                self.output_dir
                / "04_refactorings"
                / "extracted_suites"
                / "extracted_refactored_suites_metadata.csv"
            )

            if not original_suites_csv.exists():
                self.log.warning("CCTR skipped: original_suites_metadata.csv not found.")
            elif not extracted_suites_csv.exists():
                self.log.warning(
                    "CCTR skipped: extracted_refactored_suites_metadata.csv not found."
                )
            else:
                cctr_evaluator = CCTRComplexityEvaluator(
                    output_dir=self.output_dir,
                    config=self.config,
                    project_root=Path.cwd(),
                )

                cctr_evaluator.evaluate(
                    original_suites_csv=original_suites_csv,
                    extracted_suites_csv=extracted_suites_csv,
                )

                self.log.success("CCTR cognitive complexity metrics computed.")
        else:
            self.log.warning("CCTR cognitive complexity evaluation disabled.")

        # Phase 12: PMD cyclomatic complexity and maintainability
        self.log.phase("12", "Compute PMD complexity and maintainability")

        complexity_config = self.config.get("metrics", {}).get("complexity", {})
        pmd_config = complexity_config.get("pmd", {})

        if complexity_config.get("enabled", False) and pmd_config.get("enabled", False):
            original_suites_csv = (
                self.output_dir / "02_evosuite" / "original_suites_metadata.csv"
            )

            extracted_suites_csv = (
                self.output_dir
                / "04_refactorings"
                / "extracted_suites"
                / "extracted_refactored_suites_metadata.csv"
            )

            if not original_suites_csv.exists():
                self.log.warning("PMD skipped: original_suites_metadata.csv not found.")
            elif not extracted_suites_csv.exists():
                self.log.warning(
                    "PMD skipped: extracted_refactored_suites_metadata.csv not found."
                )
            else:
                pmd_evaluator = PMDComplexityEvaluator(
                    output_dir=self.output_dir,
                    config=self.config,
                    project_root=Path.cwd(),
                )

                pmd_evaluator.evaluate(
                    original_suites_csv=original_suites_csv,
                    extracted_suites_csv=extracted_suites_csv,
                )

                self.log.success("PMD cyclomatic complexity and maintainability metrics computed.")
        else:
            self.log.warning("PMD complexity evaluation disabled.")

        # Phase 12.5: select best refactored candidate per class/scenario/model
        self.log.phase("12.5", "Select best refactored candidates")

        selection_config = self.config.get("selection", {})

        if selection_config.get("enabled", False):
            selector = CandidateSelector(
                output_dir=self.output_dir,
                config=self.config,
            )

            selector.run()

            self.log.success("Best refactored candidates selected.")
        else:
            self.log.warning("Candidate selection disabled.")

        # Phase 13: synthetic report and Plotly dashboard
        self.log.phase("13", "Generate synthetic report and Plotly dashboard")

        reports_config = self.config.get("reports", {}).get("synthetic", {})

        if reports_config.get("enabled", True):
            report_generator = SyntheticReportGenerator(
                output_dir=self.output_dir,
                config=self.config,
            )

            report_generator.run()

            self.log.success("Synthetic report and Plotly dashboard generated.")
        else:
            self.log.warning("Synthetic report generation disabled.")

        self.log.final_success(
            "Pipeline completed successfully. Reports are available in 07_reports."
        )

    def _prepare_run_dir(self) -> None:
        config_copy = self.output_dir / "config.yaml"
        shutil.copy2(self.config_path, config_copy)

        ensure_dir(self.output_dir / "logs")
        ensure_dir(self.output_dir / "01_targets")
        ensure_dir(self.output_dir / "02_evosuite")
        ensure_dir(self.output_dir / "03_summaries")
        ensure_dir(self.output_dir / "04_refactorings")
        ensure_dir(self.output_dir / "05_validation")
        ensure_dir(self.output_dir / "06_metrics")
        ensure_dir(self.output_dir / "07_reports")

        self.log.info(f"Output directory: {self.output_dir}")

    def _load_targets(self) -> List[TargetClass]:
        targets_file = self.config["dataset"]["targets_file"]
        targets = load_targets(targets_file)

        if not targets:
            raise ValueError(f"No targets found in {targets_file}")

        return targets

    def _print_targets(self, targets: List[TargetClass]) -> None:
        if self.log.config.quiet:
            return

        table = Table(title="Resolved targets")
        table.add_column("#", justify="right")
        table.add_column("Dataset")
        table.add_column("Project")
        table.add_column("Class")
        table.add_column("Bug ID")
        table.add_column("Source path")

        for i, target in enumerate(targets, start=1):
            table.add_row(
                str(i),
                target.dataset,
                target.project,
                target.class_name,
                target.bug_id or "",
                str(target.source_path),
            )

        console.print(table)

    def _target_to_record(self, target: TargetClass) -> Dict[str, Any]:
        return {
            "dataset": target.dataset,
            "project": target.project,
            "class_name": target.class_name,
            "bug_id": target.bug_id or "",
            "source_path": str(target.source_path),
            "classpath": target.classpath or "",
            "test_class_fqdn": target.test_class_fqdn or "",
            "class_files_dir": target.class_files_dir or "",
            "source_files_dir": target.source_files_dir or "",
        }

    def _save_targets(self, targets: List[TargetClass]) -> None:
        records = [self._target_to_record(t) for t in targets]

        fieldnames = [
            "dataset",
            "project",
            "class_name",
            "bug_id",
            "source_path",
            "classpath",
            "test_class_fqdn",
            "class_files_dir",
            "source_files_dir",
        ]

        write_csv(
            self.output_dir / "01_targets" / "targets_resolved.csv",
            records,
            fieldnames,
        )

        write_jsonl(
            self.output_dir / "01_targets" / "targets_resolved.jsonl",
            records,
        )

    def _run_test_generation(self, targets: List[TargetClass]):
        tg_config = self.config["test_generation"]

        tool = tg_config["tool"]
        if tool != "evosuite":
            raise ValueError(f"Unsupported test generation tool for now: {tool}")

        generator = EvoSuiteGenerator(
            evosuite_jar=tg_config["evosuite_jar"],
            runs_per_class=int(tg_config.get("runs_per_class", 15)),
            search_budget_seconds=int(tg_config.get("search_budget_seconds", 180)),
            algorithm=tg_config.get("algorithm", "DynaMOSA"),
            stopping_condition=tg_config.get("stopping_condition", "MaxTime"),
            criterion=tg_config.get("criterion", "BRANCH:METHOD:LINE"),
            generate_mo_suite=bool(tg_config.get("generate_mo_suite", True)),
            show_progress=bool(tg_config.get("show_progress", False)),
            disable_minimization=bool(tg_config.get("disable_minimization", False)),
            disable_cleanup=bool(tg_config.get("disable_cleanup", False)),
            java_cmd=tg_config.get("java_cmd", "java"),
            java_memory=tg_config.get("java_memory", "-Xmx512M"),
        )

        all_suites = []

        for target in targets:
            self.log.detail(
                f"Running EvoSuite for "
                f"{target.dataset}/{target.project}/{target.class_name}"
                f"{'/' + target.bug_id if target.bug_id else ''}"
            )

            target_output_dir = self.output_dir / "02_evosuite" / "generated"

            suites = generator.generate(
                target=target,
                output_dir=target_output_dir,
            )

            self.log.detail(
                f"Generated/indexed suites for {target.class_name}: {len(suites)}"
            )

            all_suites.extend(suites)

        return all_suites


############################
# from __future__ import annotations

# import shutil
# from pathlib import Path
# from typing import Any, Dict, List

# from rich.console import Console
# from rich.table import Table

# from testhumanizer.core.artifacts import TargetClass
# from testhumanizer.core.targets import load_targets
# from testhumanizer.utils.io import ensure_dir, write_csv, write_jsonl

# from testhumanizer.generators.evosuite import EvoSuiteGenerator
# from testhumanizer.generators.indexing import save_generated_suites

# from testhumanizer.validation.original_validator import OriginalSuiteValidator
# from testhumanizer.validation.refactored_validator import RefactoredSuiteValidator

# from testhumanizer.refactoring.input_preparer import RefactoringInputPreparer
# from testhumanizer.refactoring.prompt_preparer import RefactoringPromptPreparer
# from testhumanizer.refactoring.llm_refactorer import LLMRefactorer
# from testhumanizer.refactoring.output_extractor import RefactoredOutputExtractor

# from testhumanizer.metrics.ctses.evaluator import CTSESEvaluator

# from testhumanizer.metrics.embeddings.evaluator import EmbeddingSimilarityEvaluator

# from testhumanizer.metrics.readability.evaluator import ReadabilityEvaluator

# from testhumanizer.metrics.complexity.evaluator import CCTRComplexityEvaluator

# from testhumanizer.metrics.complexity.pmd_evaluator import PMDComplexityEvaluator

# from testhumanizer.summarization.source_summarizer import SourceSummarizer

# from testhumanizer.selection.candidate_selector import CandidateSelector

# from testhumanizer.reports.synthetic_report import SyntheticReportGenerator

# from testhumanizer.utils.logging import THLogger


# console = Console()


# class TestHumanizerPipeline:
#     def __init__(self, config: Dict[str, Any], config_path: str | Path) -> None:
#         self.config = config
#         self.config_path = Path(config_path).expanduser().resolve()
#         self.output_dir = ensure_dir(config["experiment"]["output_dir"])
#         self.log = THLogger(config)

#     def run(self) -> None:
#         self._prepare_run_dir()

#         # Phase 1: load and index targets
#         targets = self._load_targets()
#         self._print_targets(targets)
#         self._save_targets(targets)

#         console.print(
#             "[bold green]Phase 1 completed:[/bold green] "
#             "targets loaded and indexed."
#         )

#         # Phase 2: generate EvoSuite suites
#         generated_suites = []

#         if self.config.get("test_generation", {}).get("enabled", False):
#             generated_suites = self._run_test_generation(targets)

#             save_generated_suites(
#                 self.output_dir / "02_evosuite",
#                 generated_suites,
#             )

#             console.print(
#                 f"[bold green]Phase 2 completed:[/bold green] "
#                 f"{len(generated_suites)} EvoSuite suites indexed."
#             )
#         else:
#             console.print("[yellow]Test generation disabled in config.[/yellow]")

#         # Common output from Phase 2
#         original_suites_metadata = (
#             self.output_dir / "02_evosuite" / "original_suites_metadata.csv"
#         )

#         # Phase 3: compile, run, and optionally cover original EvoSuite suites
#         validation_config = self.config.get("validation", {})
#         compilation_config = validation_config.get("compilation", {})

#         if compilation_config.get("enabled", False) and generated_suites:
#             validator = OriginalSuiteValidator(
#                 config=self.config,
#                 project_root=Path.cwd(),
#                 output_dir=self.output_dir,
#             )

#             validator.validate(original_suites_metadata)

#             console.print(
#                 "[bold green]Phase 3 completed:[/bold green] "
#                 "original EvoSuite suites validated."
#             )
#         else:
#             console.print(
#                 "[yellow]Original suite validation disabled or no generated suites.[/yellow]"
#             )

#         # Phase 4: prepare LLM refactoring inputs
#         preparation_config = self.config.get("preparation", {})

#         if preparation_config.get("refactoring_inputs", False):
#             if not original_suites_metadata.exists():
#                 console.print(
#                     "[yellow]Refactoring input preparation skipped: "
#                     "original_suites_metadata.csv not found.[/yellow]"
#                 )
#             else:
#                 input_preparer = RefactoringInputPreparer(output_dir=self.output_dir)

#                 input_preparer.prepare(
#                     original_suites_csv=original_suites_metadata,
#                     targets_csv=self.output_dir / "01_targets" / "targets_resolved.csv",
#                 )

#                 console.print(
#                     "[bold green]Phase 4 completed:[/bold green] "
#                     "LLM refactoring inputs prepared."
#                 )

        

#         # Phase 4.5: source-code summarization + optional SIDE validation
#         summarization_config = self.config.get("summarization", {})

#         if summarization_config.get("enabled", False):
#             summaries_dir = self.output_dir / "03_summaries"
#             summaries_dir.mkdir(parents=True, exist_ok=True)

#             summarizer = SourceSummarizer(
#                 output_dir=self.output_dir,
#                 config=self.config,
#                 project_root=Path.cwd(),
#             )

#             summarizer.summarize_targets([self._target_to_record(t) for t in targets])

#             console.print(
#                 "[bold green]Phase 4.5 completed:[/bold green] "
#                 "source-code summaries generated and evaluated."
#             )
#         else:
#             console.print("[yellow]Source-code summarization disabled.[/yellow]")

#         # else:
#         #     console.print("[yellow]Refactoring input preparation disabled.[/yellow]")

#         # Phase 5A: prepare prompts for each refactoring scenario
#         if preparation_config.get("refactoring_prompts", False):
#             prepared_inputs_path = (
#                 self.output_dir / "04_refactorings" / "prepared_inputs.jsonl"
#             )

#             if not prepared_inputs_path.exists():
#                 console.print(
#                     "[yellow]Refactoring prompt preparation skipped: "
#                     "prepared_inputs.jsonl not found.[/yellow]"
#                 )
#             else:
#                 prompt_preparer = RefactoringPromptPreparer(
#                     output_dir=self.output_dir,
#                     config=self.config,
#                 )

#                 prompt_preparer.prepare(prepared_inputs_path)

#                 console.print(
#                     "[bold green]Phase 5A completed:[/bold green] "
#                     "LLM refactoring prompts prepared."
#                 )
#         else:
#             console.print("[yellow]Refactoring prompt preparation disabled.[/yellow]")

#         # Phase 5B: call LLMs and save raw refactoring outputs
#         llm_execution_config = self.config.get("llm_execution", {})

#         if llm_execution_config.get("refactoring_outputs", False):
#             prompts_path = (
#                 self.output_dir
#                 / "04_refactorings"
#                 / "prompts"
#                 / "refactoring_prompts.jsonl"
#             )

#             if not prompts_path.exists():
#                 console.print(
#                     "[yellow]LLM refactoring skipped: "
#                     "refactoring_prompts.jsonl not found.[/yellow]"
#                 )
#             else:
#                 llm_refactorer = LLMRefactorer(
#                     output_dir=self.output_dir,
#                     config=self.config,
#                 )

#                 llm_refactorer.run(prompts_path)

#                 console.print(
#                     "[bold green]Phase 5B completed:[/bold green] "
#                     "raw LLM refactoring outputs saved."
#                 )
#         else:
#             console.print("[yellow]LLM refactoring execution disabled.[/yellow]")

#         # Phase 6: extract Java code from raw LLM outputs and reconstruct suites
#         extraction_config = self.config.get("extraction", {})

#         if extraction_config.get("refactored_suites", False):
#             raw_outputs_path = (
#                 self.output_dir
#                 / "04_refactorings"
#                 / "llm_outputs"
#                 / "raw_refactoring_outputs.jsonl"
#             )

#             prepared_inputs_path = (
#                 self.output_dir / "04_refactorings" / "prepared_inputs.jsonl"
#             )

#             if not raw_outputs_path.exists():
#                 console.print(
#                     "[yellow]Refactored suite extraction skipped: "
#                     "raw_refactoring_outputs.jsonl not found.[/yellow]"
#                 )
#             elif not prepared_inputs_path.exists():
#                 console.print(
#                     "[yellow]Refactored suite extraction skipped: "
#                     "prepared_inputs.jsonl not found.[/yellow]"
#                 )
#             else:
#                 extractor = RefactoredOutputExtractor(output_dir=self.output_dir)

#                 extractor.extract(
#                     raw_outputs_jsonl=raw_outputs_path,
#                     prepared_inputs_jsonl=prepared_inputs_path,
#                 )

#                 console.print(
#                     "[bold green]Phase 6 completed:[/bold green] "
#                     "Java code extracted and refactored suites reconstructed."
#                 )
#         else:
#             console.print("[yellow]Refactored suite extraction disabled.[/yellow]")

#         # Phase 7: validate refactored suites
#         refactored_validation_config = (
#             self.config.get("validation", {}).get("refactored", {})
#         )

#         if refactored_validation_config.get("enabled", False):
#             extracted_suites_csv = (
#                 self.output_dir
#                 / "04_refactorings"
#                 / "extracted_suites"
#                 / "extracted_refactored_suites_metadata.csv"
#             )

#             if not extracted_suites_csv.exists():
#                 console.print(
#                     "[yellow]Refactored validation skipped: "
#                     "extracted_refactored_suites_metadata.csv not found.[/yellow]"
#                 )
#             else:
#                 refactored_validator = RefactoredSuiteValidator(
#                     config=self.config,
#                     project_root=Path.cwd(),
#                     output_dir=self.output_dir,
#                 )

#                 refactored_validator.validate(extracted_suites_csv)

#                 console.print(
#                     "[bold green]Phase 7 completed:[/bold green] "
#                     "refactored suites validated."
#                 )
#         else:
#             console.print("[yellow]Refactored suite validation disabled.[/yellow]")


#         # Phase 8: CTSES metrics
#         ctses_config = self.config.get("metrics", {}).get("ctses", {})

#         if ctses_config.get("enabled", False):
#             prepared_inputs_jsonl = (
#                 self.output_dir / "04_refactorings" / "prepared_inputs.jsonl"
#             )

#             extracted_suites_jsonl = (
#                 self.output_dir
#                 / "04_refactorings"
#                 / "extracted_suites"
#                 / "extracted_refactored_suites.jsonl"
#             )

#             if not prepared_inputs_jsonl.exists():
#                 console.print(
#                     "[yellow]CTSES skipped: prepared_inputs.jsonl not found.[/yellow]"
#                 )
#             elif not extracted_suites_jsonl.exists():
#                 console.print(
#                     "[yellow]CTSES skipped: extracted_refactored_suites.jsonl not found.[/yellow]"
#                 )
#             else:
#                 ctses_evaluator = CTSESEvaluator(
#                     output_dir=self.output_dir,
#                     config=self.config,
#                     project_root=Path.cwd(),
#                 )
                
#                 ctses_evaluator.evaluate(
#                     prepared_inputs_jsonl=prepared_inputs_jsonl,
#                     extracted_suites_jsonl=extracted_suites_jsonl,
#                 )

#                 console.print(
#                     "[bold green]Phase 8 completed:[/bold green] "
#                     "CTSES metrics computed."
#                 )
#         else:
#             console.print("[yellow]CTSES evaluation disabled.[/yellow]")
        
#         # Phase 9: embedding-based cosine similarity
#         embeddings_config = self.config.get("metrics", {}).get("embeddings", {})

#         if embeddings_config.get("enabled", False):
#             prepared_inputs_jsonl = (
#                 self.output_dir / "04_refactorings" / "prepared_inputs.jsonl"
#             )

#             extracted_suites_jsonl = (
#                 self.output_dir
#                 / "04_refactorings"
#                 / "extracted_suites"
#                 / "extracted_refactored_suites.jsonl"
#             )

#             if not prepared_inputs_jsonl.exists():
#                 console.print(
#                     "[yellow]Embedding similarity skipped: "
#                     "prepared_inputs.jsonl not found.[/yellow]"
#                 )
#             elif not extracted_suites_jsonl.exists():
#                 console.print(
#                     "[yellow]Embedding similarity skipped: "
#                     "extracted_refactored_suites.jsonl not found.[/yellow]"
#                 )
#             else:
#                 embedding_evaluator = EmbeddingSimilarityEvaluator(
#                     output_dir=self.output_dir,
#                     config=self.config,
#                 )

#                 embedding_evaluator.evaluate(
#                     prepared_inputs_jsonl=prepared_inputs_jsonl,
#                     extracted_suites_jsonl=extracted_suites_jsonl,
#                 )

#                 console.print(
#                     "[bold green]Phase 9 completed:[/bold green] "
#                     "embedding cosine similarity metrics computed."
#                 )
#         else:
#             console.print("[yellow]Embedding similarity evaluation disabled.[/yellow]")
        
#         # Phase 10: Scalabrino readability
#         readability_config = self.config.get("metrics", {}).get("readability", {})

#         if readability_config.get("enabled", False) and readability_config.get("scalabrino", False):
#             original_suites_csv = (
#                 self.output_dir / "02_evosuite" / "original_suites_metadata.csv"
#             )

#             extracted_suites_csv = (
#                 self.output_dir
#                 / "04_refactorings"
#                 / "extracted_suites"
#                 / "extracted_refactored_suites_metadata.csv"
#             )

#             if not original_suites_csv.exists():
#                 console.print(
#                     "[yellow]Readability skipped: original_suites_metadata.csv not found.[/yellow]"
#                 )
#             elif not extracted_suites_csv.exists():
#                 console.print(
#                     "[yellow]Readability skipped: extracted_refactored_suites_metadata.csv not found.[/yellow]"
#                 )
#             else:
#                 readability_evaluator = ReadabilityEvaluator(
#                     output_dir=self.output_dir,
#                     config=self.config,
#                     project_root=Path.cwd(),
#                 )

#                 readability_evaluator.evaluate(
#                     original_suites_csv=original_suites_csv,
#                     extracted_suites_csv=extracted_suites_csv,
#                 )

#                 console.print(
#                     "[bold green]Phase 10 completed:[/bold green] "
#                     "Scalabrino readability metrics computed."
#                 )
#         else:
#             console.print("[yellow]Readability evaluation disabled.[/yellow]")


#         # Phase 11: CCTR cognitive complexity
#         complexity_config = self.config.get("metrics", {}).get("complexity", {})
#         cctr_config = complexity_config.get("cctr", {})

#         if complexity_config.get("enabled", False) and cctr_config.get("enabled", False):
#             original_suites_csv = (
#                 self.output_dir / "02_evosuite" / "original_suites_metadata.csv"
#             )

#             extracted_suites_csv = (
#                 self.output_dir
#                 / "04_refactorings"
#                 / "extracted_suites"
#                 / "extracted_refactored_suites_metadata.csv"
#             )

#             if not original_suites_csv.exists():
#                 console.print(
#                     "[yellow]CCTR skipped: original_suites_metadata.csv not found.[/yellow]"
#                 )
#             elif not extracted_suites_csv.exists():
#                 console.print(
#                     "[yellow]CCTR skipped: extracted_refactored_suites_metadata.csv not found.[/yellow]"
#                 )
#             else:
#                 cctr_evaluator = CCTRComplexityEvaluator(
#                     output_dir=self.output_dir,
#                     config=self.config,
#                     project_root=Path.cwd(),
#                 )

#                 cctr_evaluator.evaluate(
#                     original_suites_csv=original_suites_csv,
#                     extracted_suites_csv=extracted_suites_csv,
#                 )

#                 console.print(
#                     "[bold green]Phase 11 completed:[/bold green] "
#                     "CCTR cognitive complexity metrics computed."
#                 )
#         else:
#             console.print("[yellow]CCTR cognitive complexity evaluation disabled.[/yellow]")
        
#         # Phase 12: PMD cyclomatic complexity and maintainability
#         complexity_config = self.config.get("metrics", {}).get("complexity", {})
#         pmd_config = complexity_config.get("pmd", {})

#         if complexity_config.get("enabled", False) and pmd_config.get("enabled", False):
#             original_suites_csv = (
#                 self.output_dir / "02_evosuite" / "original_suites_metadata.csv"
#             )

#             extracted_suites_csv = (
#                 self.output_dir
#                 / "04_refactorings"
#                 / "extracted_suites"
#                 / "extracted_refactored_suites_metadata.csv"
#             )

#             if not original_suites_csv.exists():
#                 console.print(
#                     "[yellow]PMD skipped: original_suites_metadata.csv not found.[/yellow]"
#                 )
#             elif not extracted_suites_csv.exists():
#                 console.print(
#                     "[yellow]PMD skipped: extracted_refactored_suites_metadata.csv not found.[/yellow]"
#                 )
#             else:
#                 pmd_evaluator = PMDComplexityEvaluator(
#                     output_dir=self.output_dir,
#                     config=self.config,
#                     project_root=Path.cwd(),
#                 )

#                 pmd_evaluator.evaluate(
#                     original_suites_csv=original_suites_csv,
#                     extracted_suites_csv=extracted_suites_csv,
#                 )

#                 console.print(
#                     "[bold green]Phase 12 completed:[/bold green] "
#                     "PMD cyclomatic complexity and maintainability metrics computed."
#                 )
#         else:
#             console.print("[yellow]PMD complexity evaluation disabled.[/yellow]")



#         # Phase 12.5: select best refactored candidate per class/scenario/model
#         selection_config = self.config.get("selection", {})

#         if selection_config.get("enabled", False):
#             selector = CandidateSelector(
#                 output_dir=self.output_dir,
#                 config=self.config,
#             )

#             selector.run()

#             console.print(
#                 "[bold green]Phase 12.5 completed:[/bold green] "
#                 "best refactored candidates selected."
#             )
#         else:
#             console.print("[yellow]Candidate selection disabled.[/yellow]")
            
#         # Phase 13: synthetic report and Plotly dashboard
#         reports_config = self.config.get("reports", {}).get("synthetic", {})

#         if reports_config.get("enabled", True):
#             report_generator = SyntheticReportGenerator(
#                 output_dir=self.output_dir,
#                 config=self.config,
#             )

#             report_generator.run()

#             console.print(
#                 "[bold green]Phase 13 completed:[/bold green] "
#                 "synthetic report and Plotly dashboard generated."
#             )
#         else:
#             console.print("[yellow]Synthetic report generation disabled.[/yellow]")
#             console.print(
#                 "[bold green]Pipeline completed.[/bold green] "
#             )


#     def _prepare_run_dir(self) -> None:
#         config_copy = self.output_dir / "config.yaml"
#         shutil.copy2(self.config_path, config_copy)

#         ensure_dir(self.output_dir / "logs")
#         ensure_dir(self.output_dir / "01_targets")
#         ensure_dir(self.output_dir / "02_evosuite")
#         ensure_dir(self.output_dir / "03_summaries")
#         ensure_dir(self.output_dir / "04_refactorings")
#         ensure_dir(self.output_dir / "05_validation")
#         ensure_dir(self.output_dir / "06_metrics")
#         ensure_dir(self.output_dir / "07_reports")

#         console.print(f"[bold cyan]Output directory:[/bold cyan] {self.output_dir}")

#     def _load_targets(self) -> List[TargetClass]:
#         targets_file = self.config["dataset"]["targets_file"]
#         targets = load_targets(targets_file)

#         if not targets:
#             raise ValueError(f"No targets found in {targets_file}")

#         return targets

#     def _print_targets(self, targets: List[TargetClass]) -> None:
#         table = Table(title="Resolved targets")
#         table.add_column("#", justify="right")
#         table.add_column("Dataset")
#         table.add_column("Project")
#         table.add_column("Class")
#         table.add_column("Bug ID")
#         table.add_column("Source path")

#         for i, target in enumerate(targets, start=1):
#             table.add_row(
#                 str(i),
#                 target.dataset,
#                 target.project,
#                 target.class_name,
#                 target.bug_id or "",
#                 str(target.source_path),
#             )

#         console.print(table)

#     def _target_to_record(self, target: TargetClass) -> Dict[str, Any]:
#         return {
#             "dataset": target.dataset,
#             "project": target.project,
#             "class_name": target.class_name,
#             "bug_id": target.bug_id or "",
#             "source_path": str(target.source_path),
#             "classpath": target.classpath or "",
#             "test_class_fqdn": target.test_class_fqdn or "",
#             "class_files_dir": target.class_files_dir or "",
#             "source_files_dir": target.source_files_dir or "",
#         }

#     def _save_targets(self, targets: List[TargetClass]) -> None:
#         records = [self._target_to_record(t) for t in targets]

#         fieldnames = [
#             "dataset",
#             "project",
#             "class_name",
#             "bug_id",
#             "source_path",
#             "classpath",
#             "test_class_fqdn",
#             "class_files_dir",
#             "source_files_dir",
#         ]

#         write_csv(
#             self.output_dir / "01_targets" / "targets_resolved.csv",
#             records,
#             fieldnames,
#         )

#         write_jsonl(
#             self.output_dir / "01_targets" / "targets_resolved.jsonl",
#             records,
#         )

#     def _run_test_generation(self, targets: List[TargetClass]):
#         tg_config = self.config["test_generation"]

#         tool = tg_config["tool"]
#         if tool != "evosuite":
#             raise ValueError(f"Unsupported test generation tool for now: {tool}")

#         generator = EvoSuiteGenerator(
#             evosuite_jar=tg_config["evosuite_jar"],
#             runs_per_class=int(tg_config.get("runs_per_class", 15)),
#             search_budget_seconds=int(tg_config.get("search_budget_seconds", 180)),
#             algorithm=tg_config.get("algorithm", "DynaMOSA"),
#             stopping_condition=tg_config.get("stopping_condition", "MaxTime"),
#             criterion=tg_config.get("criterion", "BRANCH:METHOD:LINE"),
#             generate_mo_suite=bool(tg_config.get("generate_mo_suite", True)),
#             show_progress=bool(tg_config.get("show_progress", False)),
#             disable_minimization=bool(tg_config.get("disable_minimization", False)),
#             disable_cleanup=bool(tg_config.get("disable_cleanup", False)),
#             java_cmd=tg_config.get("java_cmd", "java"),
#             java_memory=tg_config.get("java_memory", "-Xmx512M"),
#         )

#         all_suites = []

#         for target in targets:
#             console.print(
#                 f"[bold cyan]Running EvoSuite[/bold cyan] "
#                 f"{target.dataset}/{target.project}/{target.class_name}"
#                 f"{'/' + target.bug_id if target.bug_id else ''}"
#             )

#             target_output_dir = self.output_dir / "02_evosuite" / "generated"

#             suites = generator.generate(
#                 target=target,
#                 output_dir=target_output_dir,
#             )

#             console.print(
#                 f"  [green]Generated/indexed suites:[/green] {len(suites)}"
#             )

#             all_suites.extend(suites)

#         return all_suites

