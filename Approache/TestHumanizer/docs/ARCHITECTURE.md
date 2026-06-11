# Architecture

This document describes the internal architecture of TestHumanizer.

It is intended for developers and researchers who want to understand, maintain, customize, or extend the pipeline.

## 1. High-Level Architecture

TestHumanizer is organized as a modular pipeline.

The main pipeline receives a YAML configuration, loads target Java classes, runs each processing phase, writes intermediate artifacts to disk, computes metrics, selects candidates, and generates reports.

At a high level:

```text
YAML Config
   |
   v
CLI
   |
   v
TestHumanizerPipeline
   |
   +--> Target loading
   +--> EvoSuite generation
   +--> Original validation
   +--> Refactoring input preparation
   +--> Source summarization
   +--> Prompt preparation
   +--> LLM refactoring
   +--> Java extraction
   +--> Refactored validation
   +--> Metrics
   +--> Candidate selection
   +--> Report generation
```
The pipeline is intentionally file-based. Each phase writes CSV and/or JSONL artifacts that are then consumed by later phases.

This makes the pipeline easier to debug, reproduce, and extend.

## 2. Main Entry Points

### CLI

The command-line interface is implemented in:

```text
testhumanizer/cli.py
```
The CLI provides two main commands:

```bash
testhumanizer run --config <config.yaml>
```
and:

```bash
testhumanizer inspect-config --config <config.yaml>
```
The `run` command loads the YAML configuration, applies optional CLI overrides, creates a `TestHumanizerPipeline`, and executes it.

Supported CLI overrides include:

```text
--preset
--models
--temperature
--iterations
--scenarios
--output-dir
--no-llm
--no-coverage
--log-level
--quiet
--verbose
--show-details
--show-metrics
```
### Main Pipeline

The central orchestration class is:

```text
testhumanizer/core/pipeline.py
```
The main class is:

```text
TestHumanizerPipeline
```
Its primary method is:

```text
run()
```
The pipeline controls all phases from target loading to report generation.

## 3. Configuration Flow

The configuration flow is:

```text
YAML file
   |
   v
testhumanizer.config.loader.load_config
   |
   v
CLI overrides
   |
   v
TestHumanizerPipeline(config, config_path)
   |
   v
Phase-specific components
```
At the beginning of a run, the effective configuration is copied into the output directory:

```text
outputs/<experiment_name>/config.yaml
```
This helps preserve experiment reproducibility.

## 4. Output Directory Layout

Each run writes into:

```text
outputs/<experiment_name>/
```
The pipeline creates the following main folders:

```text
outputs/<experiment_name>/
├── logs/
├── 01_targets/
├── 02_evosuite/
├── 03_summaries/
├── 04_refactorings/
├── 05_validation/
├── 06_metrics/
└── 07_reports/
```
Each phase reads from and writes to this directory.

## 5. Phase Overview

TestHumanizer currently has 13 main phases plus one candidate-selection subphase.

```text
Phase 1     Load and index target classes
Phase 2     Generate EvoSuite test suites
Phase 3     Validate original EvoSuite suites
Phase 4     Prepare LLM refactoring inputs
Phase 4.5   Generate and evaluate source-code summaries
Phase 5A    Prepare refactoring prompts
Phase 5B    Run LLM refactoring
Phase 6     Extract Java and reconstruct refactored suites
Phase 7     Validate refactored test suites
Phase 8     Compute CTSES metrics
Phase 9     Compute embedding cosine similarity
Phase 10    Compute Scalabrino readability
Phase 11    Compute CCTR cognitive complexity
Phase 12    Compute PMD complexity and maintainability
Phase 12.5  Select best refactored candidates
Phase 13    Generate synthetic report and Plotly dashboard
```
## 6. Phase 1: Target Loading

### Responsibility

Phase 1 loads target Java classes from the target CSV file configured in:

```yaml
dataset:
  targets_file: configs/experiments/targets_simple_project.csv
```
### Main module

```text
testhumanizer/core/targets.py
```
### Main artifacts

```text
01_targets/targets_resolved.csv
01_targets/targets_resolved.jsonl
```
### Data model

Target classes are represented internally using:

```text
testhumanizer/core/artifacts.py
```
The key target metadata includes:

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
### Extension notes

To support a new dataset, implement or adapt target loading so that each target is converted into the same internal `TargetClass` representation.

## 7. Phase 2: EvoSuite Generation

### Responsibility

Phase 2 invokes EvoSuite for each target class and indexes the generated test suites.

### Main modules

```text
testhumanizer/generators/evosuite.py
testhumanizer/generators/indexing.py
```
### Main artifacts

```text
02_evosuite/generated/
02_evosuite/original_suites_metadata.csv
02_evosuite/original_suites_metadata.jsonl
```
### Configuration

```yaml
test_generation:
  enabled: true
  tool: evosuite
  evosuite_jar: tools/evosuite-master-1.2.1-SNAPSHOT.jar
  runs_per_class: 1
  search_budget_seconds: 60
```
### Extension notes

To support another SBST tool, add a new generator module with an interface similar to the EvoSuite generator, then register it in the pipeline.

## 8. Phase 3: Original Suite Validation

### Responsibility

Phase 3 validates the original EvoSuite-generated suites.

It can perform:

```text
compilation
JUnit execution
coverage computation
```
### Main module

```text
testhumanizer/validation/original_validator.py
```
### Main inputs

```text
02_evosuite/original_suites_metadata.csv
```
### Main outputs

```text
05_validation/
```
The exact CSV files depend on the validation configuration, but they typically include compilation, JUnit, and coverage results.

### Extension notes

Validation is one of the most important hard constraints in the pipeline. Later candidate selection can require original and refactored suites to compile and pass JUnit tests.

## 9. Phase 4: Refactoring Input Preparation

### Responsibility

Phase 4 converts generated EvoSuite suites into structured refactoring inputs.

It extracts useful information such as:

```text
full test code
test methods
helper methods
target class metadata
source-code context
```
### Main module

```text
testhumanizer/refactoring/input_preparer.py
```
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
### Extension notes

If you want to enrich prompts with additional context, Phase 4 is one of the best places to add metadata.

## 10. Phase 4.5: Source-Code Summarization

### Responsibility

Phase 4.5 generates summaries of the source classes and optionally evaluates them.

The selected summaries can be injected into the `summary-based` refactoring scenario.

### Main modules

```text
testhumanizer/summarization/source_summarizer.py
testhumanizer/summarization/summary_store.py
testhumanizer/metrics/side/
```
### Main inputs

```text
01_targets/targets_resolved.csv
source_path from each target
```
### Main outputs

```text
03_summaries/source_summaries.jsonl
03_summaries/source_summaries_metadata.csv
03_summaries/summary_attempts.jsonl
```
### Summary quality metadata

Depending on configuration, metadata can include:

```text
selected
official_side_score
llm_side_score
llm_side_faithfulness
llm_side_coverage
llm_side_conciseness
llm_side_hallucination_risk
```
### Extension notes

To customize summarization:

- change the summarization prompt
- change the LLM model
- add another summary evaluator
- modify selection policy
- adjust summary injection into prompts

## 11. Phase 5A: Prompt Preparation

### Responsibility

Phase 5A creates LLM refactoring prompts for each target suite, scenario, model, and iteration setting.

### Main module

```text
testhumanizer/refactoring/prompt_preparer.py
```
### Main input

```text
04_refactorings/prepared_inputs.jsonl
```
### Main outputs

```text
04_refactorings/prompts/refactoring_prompts.jsonl
04_refactorings/prompts/refactoring_prompts_metadata.csv
```
### Supported scenarios

```text
tests-only
code-centric
summary-based
```
### Extension notes

To add a new prompt scenario:

1.  Add the scenario name to configuration.
2.  Update prompt preparation logic.
3.  Add scenario-specific prompt construction.
4.  Add metadata fields.
5.  Validate that Phase 5B can consume the new prompts.

## 12. Phase 5B: LLM Refactoring

### Responsibility

Phase 5B sends prompts to configured LLM providers and stores raw refactoring outputs.

### Main module

```text
testhumanizer/refactoring/llm_refactorer.py
```
### Main input

```text
04_refactorings/prompts/refactoring_prompts.jsonl
```
### Main output

```text
04_refactorings/llm_outputs/raw_refactoring_outputs.jsonl
```
### Providers

Current configurations typically use aliases such as:

```text
gpt4o
mistral
```
Each alias maps to a provider and model name in the YAML configuration.

### Extension notes

To add a new provider:

1.  Add or implement a provider client.
2.  Add configuration fields.
3.  Register dispatch logic in the LLM refactoring layer.
4.  Add retry and timeout handling.
5.  Save provider metadata in raw outputs.

## 13. Phase 6: Java Extraction and Suite Reconstruction

### Responsibility

Phase 6 extracts Java code from raw LLM outputs and reconstructs complete refactored test suites.

### Main module

```text
testhumanizer/refactoring/output_extractor.py
```
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
### Extraction statuses

Typical extraction statuses include:

```text
ok
ok_no_fence
ok_without_java_markers
failed
```
### Extension notes

If a new LLM output format is introduced, update extraction logic here. This phase should remain conservative: invalid or partial Java should be marked as failed rather than silently passed to validation.

## 14. Phase 7: Refactored Suite Validation

### Responsibility

Phase 7 validates reconstructed refactored suites.

It can perform:

```text
compilation
JUnit execution
coverage computation
```
### Main module

```text
testhumanizer/validation/refactored_validator.py
```
### Main input

```text
04_refactorings/extracted_suites/extracted_refactored_suites_metadata.csv
```
### Main outputs

```text
05_validation/
```
### Extension notes

This phase is critical because candidate selection can require refactored suites to compile and pass JUnit tests.

## 15. Phase 8: CTSES Metrics

### Responsibility

Phase 8 computes CTSES similarity between original and refactored test suites.

CTSES combines:

```text
CodeBLEU
METEOR
ROUGE-L
```
### Main module

```text
testhumanizer/metrics/ctses/evaluator.py
```
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
### CTSES variants

The implementation reports three variants:

```text
average_score_1
CTSES_score_1
CTSES_score_2
```
These correspond to the uniform baseline and the two CTSES profiles used in the paper.

### Extension notes

To add a new CTSES variant, update the aggregate computation and add the new field to the CSV/JSONL schema.

## 16. Phase 9: Embedding Similarity

### Responsibility

Phase 9 computes embedding-based cosine similarity between original and refactored test suites.

### Main module

```text
testhumanizer/metrics/embeddings/evaluator.py
```
### Embedding backends

Supported backends include:

```text
CodeBERT
GraphCodeBERT
OpenAI embeddings
```
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
### Extension notes

To add a new embedding backend:

1.  Implement an embedder class.
2.  Add configuration fields.
3.  Register the model in the evaluator.
4.  Write model alias and model name to outputs.
5.  Update candidate selection if the new embedding is used as a primary metric.

## 17. Phase 10: Scalabrino Readability

### Responsibility

Phase 10 computes code readability using the Scalabrino readability model.

### Main modules

```text
testhumanizer/metrics/readability/evaluator.py
testhumanizer/metrics/readability/scalabrino.py
```
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
### Extension notes

To use another readability model, implement a runner with a similar interface and update the evaluator.

## 18. Phase 11: CCTR Cognitive Complexity

### Responsibility

Phase 11 computes CCTR cognitive complexity for original and refactored test suites.

### Main modules

```text
testhumanizer/metrics/complexity/cctr.py
testhumanizer/metrics/complexity/evaluator.py
```
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
### Extension notes

The CCTR calculator is separated from the evaluator. This allows developers to modify the complexity calculation independently from output formatting and pipeline integration.

## 19. Phase 12: PMD Complexity and Maintainability

### Responsibility

Phase 12 uses PMD to compute additional complexity and maintainability metrics.

### Main modules

```text
testhumanizer/metrics/complexity/pmd_evaluator.py
testhumanizer/metrics/complexity/pmd_runner.py
```
### Main inputs

```text
02_evosuite/original_suites_metadata.csv
04_refactorings/extracted_suites/extracted_refactored_suites_metadata.csv
```
### Main outputs

```text
06_metrics/complexity/pmd/
```
### Extension notes

The PMD runner should remain isolated from the evaluator. If PMD CLI behavior changes, adapt the runner rather than the pipeline.

## 20. Phase 12.5: Candidate Selection

### Responsibility

Phase 12.5 selects the best refactored candidate for each target/scenario/model group.

### Main module

```text
testhumanizer/selection/candidate_selector.py
```
### Main inputs

Candidate selection consumes outputs from:

```text
04_refactorings/extracted_suites/
05_validation/
06_metrics/ctses/
06_metrics/embeddings/
```
### Main outputs

```text
06_metrics/selection/selected_candidates.csv
06_metrics/selection/selected_candidates.jsonl
```
### Default selection logic

The default policy uses:

```text
compilation status
JUnit status
OpenAI embedding cosine similarity
CTSES score
weighted ranking
```
### Extension notes

To add a new selection policy:

1.  Add a policy name to the YAML.
2.  Implement policy logic in the selector.
3.  Preserve existing output schema where possible.
4.  Add new policy metadata fields if needed.
5.  Update the report generator if the new fields are displayed.

## 21. Phase 13: Synthetic Report Generation

### Responsibility

Phase 13 generates a synthetic Markdown/HTML report and Plotly dashboard.

### Main module

```text
testhumanizer/reports/synthetic_report.py
```
### Main inputs

Report generation consumes many previous outputs, including:

```text
06_metrics/selection/selected_candidates.csv
06_metrics/ctses/ctses_results.csv
06_metrics/embeddings/embedding_similarity_results.csv
06_metrics/readability/readability_results.csv
06_metrics/complexity/
05_validation/
```
### Main outputs

```text
07_reports/synthetic_report.md
07_reports/synthetic_report.html
07_reports/report_summary.json
07_reports/figures/
```
### Extension notes

To add a new figure:

1.  Load the metric file in the report generator.
2.  Add a Plotly figure function.
3.  Save HTML and optionally PNG.
4.  Add the figure to the synthetic report.

## 22. Module Organization

The main package is organized as follows:

```text
testhumanizer/
├── cli.py
├── config/
├── core/
├── generators/
├── validation/
├── refactoring/
├── summarization/
├── metrics/
├── selection/
├── reports/
└── utils/
```
### `cli.py`

Handles command-line arguments, presets, and CLI overrides.

### `config/`

Loads YAML files and applies overrides.

### `core/`

Contains the main pipeline, target artifacts, and target loading helpers.

### `generators/`

Contains test generation logic, currently EvoSuite-based.

### `validation/`

Contains original and refactored validation logic.

### `refactoring/`

Contains refactoring input preparation, prompt preparation, LLM execution, and Java extraction.

### `summarization/`

Contains source summarization and summary storage.

### `metrics/`

Contains all metric evaluators.

### `selection/`

Contains candidate-selection logic.

### `reports/`

Contains synthetic report and dashboard generation.

### `utils/`

Contains shared utilities such as I/O helpers and logging.

## 23. Data Flow

The core data flow is:

```text
targets CSV
   |
   v
01_targets/targets_resolved.*
   |
   v
02_evosuite/original_suites_metadata.*
   |
   v
04_refactorings/prepared_inputs.jsonl
   |
   +-----------------------------+
   |                             |
   v                             v
03_summaries/source_summaries.*  04_refactorings/prompts/refactoring_prompts.*
   |                             |
   +-------------+---------------+
                 |
                 v
04_refactorings/llm_outputs/raw_refactoring_outputs.jsonl
                 |
                 v
04_refactorings/extracted_suites/extracted_refactored_suites.*
                 |
                 v
05_validation/
                 |
                 v
06_metrics/
                 |
                 v
06_metrics/selection/selected_candidates.*
                 |
                 v
07_reports/
```
This file-based structure allows restarting from intermediate phases when outputs already exist.

## 24. Logging Architecture

TestHumanizer uses a shared logger:

```text
testhumanizer/utils/logging.py
```
The logger supports:

```text
phase headers
success messages
warnings
errors
details
metric-level logs
final success panels
```
The logging behavior is controlled by YAML:

```yaml
logging:
  level: normal
  show_phase_headers: true
  show_per_item_details: false
  show_metric_details: false
  show_warnings: true
```
And can be overridden from the CLI:

```text
--quiet
--verbose
--show-details
--show-metrics
```
### Logging conventions

For new modules:

```text
self.log.success("Short summary.")
self.log.warning("Important warning.")
self.log.detail("Per-item detail.")
self.log.metric("Metric-level detail.")
```
Avoid direct `console.print(...)` calls in pipeline components unless there is a specific reason.

## 25. CSV and JSONL Convention

Most phases write both CSV and JSONL.

### CSV

CSV files are useful for:

```text
manual inspection
spreadsheet analysis
statistics
report generation
```
### JSONL

JSONL files are useful for:

```text
nested metadata
prompt contents
raw LLM outputs
structured code content
programmatic reuse
```
### Recommendation for new phases

A new phase should usually write:

```text
<phase_output>.csv
<phase_output>.jsonl
```
And should include:

```text
id
dataset
project
class_name
bug_id
testsuite_id
scenario
scenario_id
iteration
model_alias
status
error
```
where applicable.

## 26. IDs and Metadata

Stable IDs are important because outputs from different phases must be joined later.

Typical identifiers include:

```text
dataset
project
class_name
bug_id
testsuite_id
scenario_id
model_alias
iteration
```
A refactored candidate ID usually encodes several of these fields.

When adding new artifacts, preserve these identifiers as much as possible.

## 27. Error Handling

TestHumanizer should prefer structured failure metadata over silent crashes.

Recommended pattern:

```text
status = ok | skipped | failed | error
error = short error message
```
For batch phases, one failed item should not necessarily stop the entire run. Instead:

1.  Write an error row.
2.  Continue processing other rows.
3.  Print a warning.
4.  Summarize failures at the end.

Hard failures should be reserved for configuration errors or missing mandatory global inputs.

## 28. Adding a New Phase

To add a new pipeline phase:

1.  Create a module under the appropriate package.
2.  Implement an evaluator or processor class.
3.  Add configuration keys.
4.  Add input existence checks in the pipeline.
5.  Write CSV and JSONL outputs.
6.  Add concise logging.
7.  Update report generation if needed.
8.  Update documentation.

Example skeleton:

```python
class NewMetricEvaluator:
    def __init__(self, output_dir, config):
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.config = config
        self.log = THLogger(config)

    def evaluate(self, input_path):
        rows = []

        # process inputs

        write_csv(...)
        write_jsonl(...)

        self.log.success(
            f"New metric completed: rows={len(rows)}."
        )
```
## 29. Adding a New Metric

A metric evaluator should:

1.  Read existing artifacts.
2.  Compute one or more scores.
3.  Write detailed results.
4.  Write summaries if useful.
5.  Include status and error fields.
6.  Avoid stopping the entire pipeline on one item failure.
7.  Log one concise summary.

Recommended output directory:

```text
06_metrics/<metric_name>/
```
Recommended files:

```text
<metric_name>_results.csv
<metric_name>_results.jsonl
<metric_name>_summary.csv
<metric_name>_summary.jsonl
```
## 30. Adding a New Report Figure

Report figures should be added in:

```text
testhumanizer/reports/synthetic_report.py
```
A figure should:

1.  Load the relevant CSV.
2.  Create a Plotly figure.
3.  Save an HTML file.
4.  Optionally save a PNG file.
5.  Register the figure in the report.

Recommended output:

```text
07_reports/figures/<figure_name>.html
07_reports/figures/<figure_name>.png
```
## 31. Reproducibility Design

TestHumanizer supports reproducibility by:

```text
copying the effective config into the output directory
writing intermediate artifacts to disk
using CSV/JSONL outputs
recording model aliases and model names
recording scenario IDs
recording validation status
recording metric status and errors
using deterministic file paths where possible
```
For full reproducibility, also record:

```text
Java version
Python version
EvoSuite version
PMD version
LLM model versions
API model names
CodeBLEU environment
GPU/CPU device information
```
## 32. Development Checklist

Before committing a new feature:

- [ ] The feature is configurable from YAML
- [ ] It has a clear output directory
- [ ] It writes CSV and/or JSONL outputs
- [ ] It preserves core identifiers
- [ ] It logs a concise success summary
- [ ] It does not spam normal terminal output
- [ ] It handles per-item failures gracefully
- [ ] It is documented
- [ ] It works with the simple Java example
- [ ] It does not break candidate selection or reports
## 33. Recommended Developer Workflow

For local development:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast
```
For debugging:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast \
  --verbose
```
For metric debugging:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast \
  --show-metrics
```
For avoiding new LLM calls:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast \
  --no-llm
```
## 34. Design Principles

TestHumanizer follows these principles:

```text
configuration-first
file-based reproducibility
phase-by-phase modularity
structured metadata
graceful per-item failure handling
clear validation gates
metric transparency
extensibility
clean terminal output
```
New code should follow the same principles.
