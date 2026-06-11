# TestHumanizer

**TestHumanizer** is a modular SBST + LLM pipeline for improving automatically generated Java unit test suites.

It starts from EvoSuite-generated tests, prepares multiple refactoring prompts, applies LLM-based refactoring strategies, validates the resulting test suites, computes semantic and structural preservation metrics, and generates a synthetic report for analysis.

The goal of TestHumanizer is to support research and experimentation on the humanization of automatically generated test suites while preserving their behavioral intent.

## Overview

Automatically generated tests are often useful for fault detection and coverage, but they can be hard to read, difficult to maintain, and poorly aligned with human-written test style.

TestHumanizer provides an end-to-end experimental pipeline to:

1.  Generate Java unit tests with EvoSuite.
2.  Prepare test suites for LLM-based refactoring.
3.  Run multiple refactoring scenarios.
4.  Extract valid Java test suites from raw LLM outputs.
5.  Validate original and refactored tests.
6.  Compare original and refactored tests using semantic, lexical, readability, and complexity metrics.
7.  Select the best refactored candidates.
8.  Generate reports and dashboards.

## Main Features

- EvoSuite-based test generation.
- Multi-scenario LLM refactoring.
- Support for OpenAI and Mistral models.
- Optional source-code summarization for summary-based prompting.
- Original and refactored test validation.
- Compilation and JUnit execution checks.
- Optional JaCoCo coverage analysis.
- CTSES composite similarity metrics.
- CodeBERT, GraphCodeBERT, and OpenAI embedding cosine similarity.
- Scalabrino readability score.
- CCTR cognitive complexity.
- PMD cyclomatic complexity and maintainability metrics.
- Candidate selection based on validation, similarity, and CTSES thresholds.
- Synthetic Markdown/HTML report generation.
- Configurable CLI presets.
- Lightweight logging modes for clean terminal output.

## Pipeline Summary

TestHumanizer currently runs the following phases:

| Phase      | Description                                         |
|------------|-----------------------------------------------------|
| Phase 1    | Load and index target Java classes                  |
| Phase 2    | Generate EvoSuite test suites                       |
| Phase 3    | Validate original EvoSuite suites                   |
| Phase 4    | Prepare LLM refactoring inputs                      |
| Phase 4.5  | Generate and evaluate source-code summaries         |
| Phase 5A   | Prepare refactoring prompts                         |
| Phase 5B   | Run LLM refactoring                                 |
| Phase 6    | Extract Java code and reconstruct refactored suites |
| Phase 7    | Validate refactored suites                          |
| Phase 8    | Compute CTSES metrics                               |
| Phase 9    | Compute embedding cosine similarity                 |
| Phase 10   | Compute Scalabrino readability                      |
| Phase 11   | Compute CCTR cognitive complexity                   |
| Phase 12   | Compute PMD complexity and maintainability          |
| Phase 12.5 | Select best refactored candidates                   |
| Phase 13   | Generate synthetic report and Plotly dashboard      |

## Repository Structure

A typical TestHumanizer repository contains:

```text
TestHumanizer/
├── configs/
│   └── experiments/
│       ├── evosuite_simple_project.yaml
│       └── targets_simple_project.csv
├── examples/
│   └── simple-java-project/
├── testhumanizer/
│   ├── cli.py
│   ├── core/
│   ├── config/
│   ├── generators/
│   ├── validation/
│   ├── refactoring/
│   ├── summarization/
│   ├── metrics/
│   ├── selection/
│   ├── reports/
│   └── utils/
├── tools/
│   ├── evosuite-master-1.2.1-SNAPSHOT.jar
│   ├── JUNIT-HAMCREST/
│   ├── jacoco-0.8.8/
│   ├── pmd-bin-7.0.0-rc4/
│   └── Readability-model/
├── outputs/
├── pyproject.toml
└── README.md
```
## Installation

### 1. Create a Python environment

TestHumanizer requires Python 3.10 or later.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```
### 2. Install Java

TestHumanizer relies on Java tools such as EvoSuite, JUnit, JaCoCo, PMD, and the Scalabrino readability model.

Check Java availability:

```bash
java -version
javac -version
```
### 3. Prepare external tools

The default configuration expects the following tools:

```text
tools/evosuite-master-1.2.1-SNAPSHOT.jar
tools/JUNIT-HAMCREST/junit-4.13.2.jar
tools/JUNIT-HAMCREST/hamcrest-core-1.3.jar
tools/jacoco-0.8.8/lib/jacococli.jar
tools/jacoco-0.8.8/lib/jacocoagent.jar
tools/pmd-bin-7.0.0-rc4/
tools/Readability-model/rsm.jar
```
If your paths differ, update the YAML configuration accordingly.

### 4. Prepare CodeBLEU environment

CodeBLEU is isolated in a separate environment in the current setup.

Example:

```bash
python3 -m venv .venv-codebleu
source .venv-codebleu/bin/activate
pip install -U pip
# install the CodeBLEU dependencies required by your setup
deactivate
```
The main YAML configuration points to:

```yaml
metrics:
  ctses:
    codebleu_python: .venv-codebleu/bin/python
```
### 5. Configure API keys

For OpenAI and Mistral models, export the required API keys:

```bash
export OPENAI_API_KEY_1="your-openai-key"
export MISTRAL_API_KEY_2="your-mistral-key"
```
The environment variable names can be changed in the YAML configuration.

## Quickstart

Run the included simple Java project:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast
```
The `fast` preset runs all three refactoring scenarios with one iteration.

Expected final output:

```text
✓ Pipeline completed successfully. Reports are available in 07_reports.
```
The main report will be available under:

```text
outputs/evosuite_simple_project/07_reports/
```
## CLI Usage

TestHumanizer provides a command-line interface through the `testhumanizer` command.

### Run a pipeline

```bash
testhumanizer run --config configs/experiments/evosuite_simple_project.yaml
```
### Inspect a configuration

```bash
testhumanizer inspect-config --config configs/experiments/evosuite_simple_project.yaml
```
### Use presets

```bash
testhumanizer run --config configs/experiments/evosuite_simple_project.yaml --preset ready
testhumanizer run --config configs/experiments/evosuite_simple_project.yaml --preset fast
testhumanizer run --config configs/experiments/evosuite_simple_project.yaml --preset full
```
Preset behavior:

| Preset  | Behavior                                                   |
|---------|------------------------------------------------------------|
| `ready` | Uses the YAML configuration as the source of truth         |
| `fast`  | Runs all scenarios with one iteration unless overridden    |
| `full`  | Runs all scenarios with three iterations unless overridden |

Explicit CLI arguments override preset defaults.

### Override models

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --models gpt4o
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --models gpt4o,mistral
```
### Override scenarios

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --scenarios tests-only
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --scenarios tests-only,code-centric,summary-based
```
You can also use:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --scenarios all
```
### Override iterations

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --iterations 3
```
### Disable LLM execution

Useful when you only want to reuse existing raw LLM outputs:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --no-llm
```
### Disable coverage

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --no-coverage
```
### Override output directory

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --output-dir outputs/my_custom_run
```
## Logging Options

By default, TestHumanizer uses a clean normal logging mode.

The YAML configuration supports:

```yaml
logging:
  level: normal
  show_phase_headers: true
  show_per_item_details: false
  show_metric_details: false
  show_warnings: true
```
### Quiet mode

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --quiet
```
### Verbose mode

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --verbose
```
### Show per-item details

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --show-details
```
### Show detailed metrics

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --show-metrics
```
## Refactoring Scenarios

TestHumanizer currently supports three prompt scenarios.

### Scenario 1: Tests-only

The LLM receives only the generated test suite and is asked to refactor it.

This scenario measures how much the LLM can improve test readability and structure using only the test code.

### Scenario 2: Code-centric

The LLM receives the generated test suite and additional production-code context.

This scenario helps the model understand the class under test and generate more meaningful names, organization, and assertions.

### Scenario 3: Summary-based

The LLM receives the generated test suite and a generated source-code summary.

This scenario uses a compact semantic description of the class under test instead of relying only on raw source code.

## Metrics

TestHumanizer computes several families of metrics.

### CTSES

CTSES is a composite refactoring similarity score designed to estimate how well a refactored test suite preserves the original generated suite.

It combines:

- CodeBLEU
- METEOR
- ROUGE-L

The current implementation reports three variants:

| Variant                      | Weights                      |
|------------------------------|------------------------------|
| `average_score_1` / CTSESAVG | Uniform baseline             |
| `CTSES_score_1` / CTSES_1    | Semantic-prioritized profile |
| `CTSES_score_2` / CTSES_2    | Readability-aware profile    |

### Embedding Similarity

TestHumanizer computes cosine similarity between original and refactored test suites using:

- CodeBERT
- GraphCodeBERT
- OpenAI `text-embedding-3-small`

The OpenAI similarity is used as the primary semantic-preservation metric in the default candidate selection policy.

### Readability

TestHumanizer uses the Scalabrino readability model to estimate code readability for original and refactored test suites.

### Cognitive Complexity

TestHumanizer includes a CCTR cognitive complexity calculator based on Java parsing with Tree-sitter.

### PMD Complexity and Maintainability

TestHumanizer uses PMD to compute additional complexity and maintainability indicators, including cyclomatic complexity and maintainability-related metrics.

## Candidate Selection

After validation and metric computation, TestHumanizer selects the best refactored candidate for each class, test suite, scenario, model, and iteration group.

The default selection policy is:

```yaml
selection:
  policy: first_passing_then_best
```
The selection process applies:

1.  Hard constraints:

```text
- The refactored suite must compile.
- The refactored suite must pass JUnit tests.
```
2.  Semantic preservation thresholds:

```text
- OpenAI embedding cosine similarity threshold.
- CTSES threshold.
```
3.  Ranking:

```text
- Cosine similarity weight.
- CTSES weight.
```
Default configuration:

```yaml
selection:
  hard_constraints:
    require_compile_ok: true
    require_junit_ok: true

  cosine_similarity:
    enabled: true
    threshold: 0.80
    primary_metric: cosine_similarity
    primary_embedding_model_alias: openai

  ctses:
    enabled: true
    threshold: 0.50

  ranking:
    cosine_weight: 0.60
    ctses_weight: 0.40
```
## Output Structure

A typical run creates:

```text
outputs/<experiment_name>/
├── config.yaml
├── logs/
├── 01_targets/
│   ├── targets_resolved.csv
│   └── targets_resolved.jsonl
├── 02_evosuite/
│   ├── generated/
│   ├── original_suites_metadata.csv
│   └── original_suites_metadata.jsonl
├── 03_summaries/
│   ├── source_summaries.jsonl
│   ├── source_summaries_metadata.csv
│   └── summary_attempts.jsonl
├── 04_refactorings/
│   ├── prepared_inputs.jsonl
│   ├── prompts/
│   ├── llm_outputs/
│   └── extracted_suites/
├── 05_validation/
├── 06_metrics/
│   ├── ctses/
│   ├── embeddings/
│   ├── readability/
│   ├── complexity/
│   └── selection/
└── 07_reports/
    ├── synthetic_report.md
    ├── synthetic_report.html
    ├── report_summary.json
    └── figures/
```
## Main Output Files

Important files include:

```text
01_targets/targets_resolved.csv
02_evosuite/original_suites_metadata.csv
03_summaries/source_summaries_metadata.csv
04_refactorings/prepared_inputs.jsonl
04_refactorings/prompts/refactoring_prompts_metadata.csv
04_refactorings/llm_outputs/raw_refactoring_outputs.jsonl
04_refactorings/extracted_suites/extracted_refactored_suites_metadata.csv
05_validation/
06_metrics/ctses/ctses_results.csv
06_metrics/embeddings/embedding_similarity_results.csv
06_metrics/readability/readability_results.csv
06_metrics/complexity/cctr/cctr_results.csv
06_metrics/complexity/pmd/pmd_complexity_results.csv
06_metrics/selection/selected_candidates.csv
07_reports/synthetic_report.html
```
## Running Custom Java Projects

To run TestHumanizer on a custom Java project, prepare:

1.  A YAML configuration file.
2.  A target CSV file listing the classes under test.
3.  Java compilation dependencies.
4.  Tool paths for EvoSuite, JUnit, JaCoCo, PMD, and readability if enabled.

A target CSV should contain fields such as:

```text
dataset,project,class_name,bug_id,source_path,classpath,test_class_fqdn,class_files_dir,source_files_dir
custom,my-project,MyClass,,path/to/MyClass.java,path/to/classes,com.example.MyClass,path/to/classes,path/to/src/main/java
```
Then run:

```bash
testhumanizer run \
  --config configs/experiments/my_project.yaml \
  --preset fast
```
For complex Java projects, make sure that:

- `classpath` includes all required compiled classes and dependencies.
- `class_files_dir` points to compiled `.class` files.
- `source_files_dir` points to the Java source tree.
- The class under test can be compiled and executed outside TestHumanizer first.
- EvoSuite can resolve the target class.

## Development Notes

TestHumanizer is organized as a modular pipeline.

Important extension points:

| Component               | Location                             |
|-------------------------|--------------------------------------|
| CLI                     | `testhumanizer/cli.py`               |
| Main pipeline           | `testhumanizer/core/pipeline.py`     |
| EvoSuite generation     | `testhumanizer/generators/`          |
| Validation              | `testhumanizer/validation/`          |
| Refactoring preparation | `testhumanizer/refactoring/`         |
| Source summarization    | `testhumanizer/summarization/`       |
| CTSES metrics           | `testhumanizer/metrics/ctses/`       |
| Embedding metrics       | `testhumanizer/metrics/embeddings/`  |
| Readability metrics     | `testhumanizer/metrics/readability/` |
| Complexity metrics      | `testhumanizer/metrics/complexity/`  |
| Candidate selection     | `testhumanizer/selection/`           |
| Reports                 | `testhumanizer/reports/`             |
| Logging                 | `testhumanizer/utils/logging.py`     |

## Extending TestHumanizer

### Add a new LLM provider

To add a new LLM provider:

1.  Add a client implementation in the LLM/refactoring layer.
2.  Add provider-specific configuration fields.
3.  Register the provider where LLM calls are dispatched.
4.  Add an example configuration.
5.  Test with `--models your_model_alias`.

### Add a new prompt scenario

To add a new scenario:

1.  Extend the scenario list in the configuration.
2.  Update the prompt preparation logic.
3.  Add metadata fields if the scenario uses additional context.
4.  Ensure the scenario appears in output CSV/JSONL metadata.
5.  Validate with `--scenarios your-scenario`.

### Add a new metric

To add a new metric:

1.  Create a new module under `testhumanizer/metrics/`.
2.  Implement an evaluator class with a clear `evaluate(...)` entry point.
3.  Write detailed CSV and JSONL outputs.
4.  Add a concise logging summary.
5.  Register the evaluator in the main pipeline.
6.  Add configuration switches under `metrics`.
7.  Update reports and candidate selection if needed.

### Add a new candidate selection policy

To add a new selection policy:

1.  Extend `testhumanizer/selection/candidate_selector.py`.
2.  Add a new policy name in the YAML configuration.
3.  Define hard constraints and ranking logic.
4.  Save the selected candidate metadata.
5.  Update the documentation.

## Troubleshooting

### EvoSuite cannot find the target class

Check:

- `classpath`
- `class_files_dir`
- compiled `.class` files
- Java package names
- source path correctness

### Java compilation fails

Check:

- JUnit and Hamcrest jars
- EvoSuite runtime jar
- generated test imports
- Java version compatibility

### JUnit execution fails

Check:

- runtime classpath
- EvoSuite runtime dependency
- test scaffolding
- generated assertions
- project dependencies

### Coverage fails

Check:

- JaCoCo jar paths
- `jacocoagent.jar`
- `jacococli.jar`
- source and class directories
- JVM arguments

### CodeBLEU fails

Check:

- `.venv-codebleu`
- `metrics.ctses.codebleu_python`
- CodeBLEU dependencies
- Java language configuration

### OpenAI embeddings fail

Check:

- API key environment variable
- model name
- network access
- retry settings
- cache directory permissions

### Scalabrino readability fails

Check:

- `tools/Readability-model/rsm.jar`
- Java availability
- timeout setting
- input Java files

### PMD fails

Check:

- PMD directory
- PMD binary path
- ruleset path
- Java file paths

## Recommended Workflow

For a quick sanity check:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast
```
For a paper-like run:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset full
```
For debugging:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast \
  --verbose
```
For metric inspection:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast \
  --show-metrics
```
## Citation

If you use TestHumanizer in academic work, please cite the corresponding paper or technical report.

```text
@misc{testhumanizer,
  title = {TestHumanizer: Humanizing Automatically Generated Unit Test Suites with LLM-Based Refactoring},
  author = {Your Name},
  year = {2026},
  note = {Software artifact}
}
```
## License

Add your license information here.

Recommended options for research software include:

- MIT License
- Apache License 2.0
- BSD 3-Clause License

## Status

TestHumanizer is an active research prototype.

The current version is designed for controlled experiments on Java unit test generation, LLM-based refactoring, validation, metric evaluation, candidate selection, and reporting.
