# Pipeline Phases

This document describes each TestHumanizer pipeline phase.

It is intended as a technical reference for users and developers who want to understand what each phase reads, writes, and controls.

For a higher-level view of the system, see:

```text
docs/ARCHITECTURE.md
```
## Phase 1 — Load and Index Target Classes

### Purpose

Loads the Java classes under test from the configured target CSV file.

### Main input

```text
configs/experiments/<targets_file>.csv
```
### Main outputs

```text
outputs/<experiment>/01_targets/targets_resolved.csv
outputs/<experiment>/01_targets/targets_resolved.jsonl
```
### Main module

```text
testhumanizer/core/targets.py
```
### Notes

Each target row is converted into an internal target record containing:

```text
dataset
project
class_name
bug_id
source_path
classpath
test_class_fqdn
class_files_dir
source_files_dir
```
If this phase fails, check the target CSV path and the correctness of each target row.

## Phase 2 — Generate EvoSuite Test Suites

### Purpose

Runs EvoSuite on each target class and indexes the generated test suites.

### Main inputs

```text
01_targets/targets_resolved.csv
```
### Main outputs

```text
02_evosuite/generated/
02_evosuite/original_suites_metadata.csv
02_evosuite/original_suites_metadata.jsonl
```
### Main modules

```text
testhumanizer/generators/evosuite.py
testhumanizer/generators/indexing.py
```
### Configuration

```yaml
test_generation:
  enabled: true
  tool: evosuite
  evosuite_jar: tools/evosuite-master-1.2.1-SNAPSHOT.jar
```
### Common failures

```text
EvoSuite jar not found
target class not found
wrong classpath
missing compiled .class files
Java version mismatch
```
## Phase 3 — Validate Original EvoSuite Suites

### Purpose

Validates the original EvoSuite-generated test suites.

Depending on the configuration, this phase can run:

```text
Java compilation
JUnit execution
JaCoCo coverage
```
### Main input

```text
02_evosuite/original_suites_metadata.csv
```
### Main outputs

```text
05_validation/
```
### Main module

```text
testhumanizer/validation/original_validator.py
```
### Configuration

```yaml
validation:
  compilation:
    enabled: true
  junit:
    enabled: true
  coverage:
    enabled: true
```
### Common failures

```text
missing JUnit or Hamcrest jars
missing EvoSuite runtime dependency
wrong classpath
generated test does not compile
generated test fails at runtime
coverage tool path is wrong
```
## Phase 4 — Prepare LLM Refactoring Inputs

### Purpose

Transforms original EvoSuite suites into structured inputs for prompt generation.

### Main inputs

```text
02_evosuite/original_suites_metadata.csv
01_targets/targets_resolved.csv
```
### Main outputs

```text
04_refactorings/prepared_inputs.jsonl
04_refactorings/prepared_inputs_metadata.csv
```
### Main module

```text
testhumanizer/refactoring/input_preparer.py
```
### Configuration

```yaml
preparation:
  refactoring_inputs: true
```
### Notes

Prepared inputs may include:

```text
full generated test code
test methods
helper methods
target metadata
source-code context
```
If this phase fails, check that Phase 2 completed and `original_suites_metadata.csv` exists.

## Phase 4.5 — Generate and Evaluate Source-Code Summaries

### Purpose

Generates summaries of the production classes under test.

These summaries are mainly used by the `summary-based` refactoring scenario.

### Main inputs

```text
01_targets/targets_resolved.csv
source_path for each target class
```
### Main outputs

```text
03_summaries/source_summaries.jsonl
03_summaries/source_summaries_metadata.csv
03_summaries/summary_attempts.jsonl
```
### Main modules

```text
testhumanizer/summarization/source_summarizer.py
testhumanizer/summarization/summary_store.py
```
### Configuration

```yaml
summarization:
  enabled: true
  inject_into_summary_based: true
```
### Notes

If LLM-SIDE is enabled, the summary metadata can include faithfulness, coverage, conciseness, hallucination-risk, and summary-selection information.

## Phase 5A — Prepare Refactoring Prompts

### Purpose

Creates LLM refactoring prompts from prepared inputs.

### Main input

```text
04_refactorings/prepared_inputs.jsonl
```
### Main outputs

```text
04_refactorings/prompts/refactoring_prompts.jsonl
04_refactorings/prompts/refactoring_prompts_metadata.csv
```
### Main module

```text
testhumanizer/refactoring/prompt_preparer.py
```
### Supported scenarios

```text
tests-only
code-centric
summary-based
```
### Configuration

```yaml
preparation:
  refactoring_prompts: true
```
### Notes

Each prompt is associated with:

```text
target class
test suite
scenario
model alias
iteration
summary metadata, when applicable
```
## Phase 5B — Run LLM Refactoring

### Purpose

Sends refactoring prompts to configured LLM providers and saves raw outputs.

### Main input

```text
04_refactorings/prompts/refactoring_prompts.jsonl
```
### Main output

```text
04_refactorings/llm_outputs/raw_refactoring_outputs.jsonl
```
### Main module

```text
testhumanizer/refactoring/llm_refactorer.py
```
### Configuration

```yaml
llm_execution:
  refactoring_outputs: true
```
### CLI shortcut

```bash
testhumanizer run --config <config.yaml> --no-llm
```
### Notes

Use `--no-llm` when raw LLM outputs already exist and you want to rerun later phases without making new API calls.

## Phase 6 — Extract Java and Reconstruct Refactored Suites

### Purpose

Extracts Java code from raw LLM responses and reconstructs complete test suite files.

### Main inputs

```text
04_refactorings/llm_outputs/raw_refactoring_outputs.jsonl
04_refactorings/prepared_inputs.jsonl
```
### Main outputs

```text
04_refactorings/extracted_suites/extracted_refactored_suites.jsonl
04_refactorings/extracted_suites/extracted_refactored_suites_metadata.csv
```
### Main module

```text
testhumanizer/refactoring/output_extractor.py
```
### Typical extraction statuses

```text
ok
ok_no_fence
ok_without_java_markers
failed
```
### Notes

Only successfully extracted suites should proceed to validation and metric computation.

## Phase 7 — Validate Refactored Test Suites

### Purpose

Validates the refactored test suites produced by LLMs.

Depending on configuration, this phase can run:

```text
Java compilation
JUnit execution
JaCoCo coverage
```
### Main input

```text
04_refactorings/extracted_suites/extracted_refactored_suites_metadata.csv
```
### Main outputs

```text
05_validation/
```
### Main module

```text
testhumanizer/validation/refactored_validator.py
```
### Configuration

```yaml
validation:
  refactored:
    enabled: true
```
### Common failures

```text
LLM output has invalid Java syntax
missing imports
changed package declaration
changed class name
removed EvoSuite scaffolding dependency
changed test semantics
JUnit failure
```
## Phase 8 — Compute CTSES Metrics

### Purpose

Computes semantic and structural similarity between original and refactored test suites.

### Main inputs

```text
04_refactorings/prepared_inputs.jsonl
04_refactorings/extracted_suites/extracted_refactored_suites.jsonl
```
### Main outputs

```text
06_metrics/ctses/ctses_results.csv
06_metrics/ctses/ctses_results.jsonl
```
### Main module

```text
testhumanizer/metrics/ctses/evaluator.py
```
### Metrics

CTSES combines:

```text
CodeBLEU
METEOR
ROUGE-L
```
The current implementation reports:

```text
average_score_1
CTSES_score_1
CTSES_score_2
```
### Common failures

```text
CodeBLEU environment not found
NLTK resource issue
empty original or refactored code
failed extraction upstream
```
## Phase 9 — Compute Embedding Cosine Similarity

### Purpose

Computes embedding-based cosine similarity between original and refactored test suites.

### Main inputs

```text
04_refactorings/prepared_inputs.jsonl
04_refactorings/extracted_suites/extracted_refactored_suites.jsonl
```
### Main outputs

```text
06_metrics/embeddings/embedding_similarity_results.csv
06_metrics/embeddings/embedding_similarity_results.jsonl
```
### Main module

```text
testhumanizer/metrics/embeddings/evaluator.py
```
### Supported embedding models

```text
CodeBERT
GraphCodeBERT
OpenAI embeddings
```
### Common failures

```text
HuggingFace model loading issue
GPU or CUDA issue
OpenAI API key missing
input too long
empty code after preprocessing
```
## Phase 10 — Compute Scalabrino Readability

### Purpose

Computes readability scores for original and refactored test suites.

### Main inputs

```text
02_evosuite/original_suites_metadata.csv
04_refactorings/extracted_suites/extracted_refactored_suites_metadata.csv
```
### Main outputs

```text
06_metrics/readability/readability_results.csv
06_metrics/readability/readability_results.jsonl
06_metrics/readability/readability_summary.csv
06_metrics/readability/readability_summary.jsonl
```
### Main modules

```text
testhumanizer/metrics/readability/evaluator.py
testhumanizer/metrics/readability/scalabrino.py
```
### Common failures

```text
readability jar not found
Java command not found
timeout
invalid Java file path
```
## Phase 11 — Compute CCTR Cognitive Complexity

### Purpose

Computes cognitive complexity for original and refactored test suites.

### Main inputs

```text
02_evosuite/original_suites_metadata.csv
04_refactorings/extracted_suites/extracted_refactored_suites_metadata.csv
```
### Main outputs

```text
06_metrics/complexity/cctr/cctr_results.csv
06_metrics/complexity/cctr/cctr_results.jsonl
06_metrics/complexity/cctr/cctr_summary.csv
06_metrics/complexity/cctr/cctr_summary.jsonl
```
### Main modules

```text
testhumanizer/metrics/complexity/cctr.py
testhumanizer/metrics/complexity/evaluator.py
```
### Notes

The calculation logic is separated from the evaluator:

```text
cctr.py       -> complexity calculation
evaluator.py  -> file loading, output writing, pipeline integration
```
## Phase 12 — Compute PMD Complexity and Maintainability

### Purpose

Runs PMD on original and refactored suites to compute complexity and maintainability-related metrics.

### Main inputs

```text
02_evosuite/original_suites_metadata.csv
04_refactorings/extracted_suites/extracted_refactored_suites_metadata.csv
```
### Main outputs

```text
06_metrics/complexity/pmd/
```
### Main modules

```text
testhumanizer/metrics/complexity/pmd_evaluator.py
testhumanizer/metrics/complexity/pmd_runner.py
```
### Common failures

```text
PMD directory not found
PMD executable not found
invalid ruleset
timeout
invalid Java file path
```
## Phase 12.5 — Select Best Refactored Candidates

### Purpose

Selects the best candidate for each class, test suite, scenario, and model group.

### Main inputs

```text
04_refactorings/extracted_suites/extracted_refactored_suites_metadata.csv
05_validation/
06_metrics/ctses/
06_metrics/embeddings/
```
### Main outputs

```text
06_metrics/selection/selected_candidates.csv
06_metrics/selection/selected_candidates.jsonl
```
### Main module

```text
testhumanizer/selection/candidate_selector.py
```
### Default logic

The default policy uses:

```text
compile OK
JUnit OK
OpenAI cosine similarity threshold
CTSES threshold
weighted ranking
```
### Configuration

```yaml
selection:
  enabled: true
  policy: first_passing_then_best
```
## Phase 13 — Generate Synthetic Report and Plotly Dashboard

### Purpose

Generates the final Markdown/HTML report and Plotly dashboard.

### Main inputs

```text
05_validation/
06_metrics/
06_metrics/selection/selected_candidates.csv
```
### Main outputs

```text
07_reports/synthetic_report.md
07_reports/synthetic_report.html
07_reports/report_summary.json
07_reports/figures/
```
### Main module

```text
testhumanizer/reports/synthetic_report.py
```
### Notes

This phase summarizes validation, semantic preservation, readability, complexity, candidate selection, and scenario/model-level comparisons.

## Phase Dependencies

The pipeline is sequential, and most phases depend on outputs from earlier phases.

```text
Phase 1
  -> Phase 2
  -> Phase 3
  -> Phase 4
  -> Phase 4.5
  -> Phase 5A
  -> Phase 5B
  -> Phase 6
  -> Phase 7
  -> Phase 8
  -> Phase 9
  -> Phase 10
  -> Phase 11
  -> Phase 12
  -> Phase 12.5
  -> Phase 13
```
Some phases can reuse existing outputs. For example, if raw LLM outputs already exist, use:

```bash
testhumanizer run --config <config.yaml> --no-llm
```
## Outputs by Directory

```text
01_targets       target resolution
02_evosuite      EvoSuite-generated suites
03_summaries     source-code summaries
04_refactorings  prepared inputs, prompts, raw outputs, extracted suites
05_validation    compilation, JUnit, and coverage results
06_metrics       CTSES, embeddings, readability, complexity, selection
07_reports       final reports and dashboard
```
## Debugging Strategy

When a phase fails, debug from the closest upstream artifact.

Example:

```text
Phase 7 fails
  -> inspect extracted_refactored_suites_metadata.csv
  -> inspect extracted Java files
  -> inspect raw LLM outputs
  -> inspect prompt metadata
```
Example:

```text
Phase 12.5 selects no candidate
  -> inspect refactored validation outputs
  -> inspect embedding_similarity_results.csv
  -> inspect ctses_results.csv
  -> inspect selected_candidates.csv
```
## Developer Notes

When adding or modifying a phase:

- [ ] keep the phase configurable
- [ ] preserve stable metadata identifiers
- [ ] write CSV and/or JSONL outputs
- [ ] include status and error fields when relevant
- [ ] avoid noisy normal-mode logs
- [ ] use THLogger for logging
- [ ] update report generation if the phase creates user-facing metrics
- [ ] update this documentation
