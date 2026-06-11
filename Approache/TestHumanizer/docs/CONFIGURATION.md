# Configuration Guide

TestHumanizer is configured through YAML experiment files.

A typical configuration file defines:

- the experiment name and output directory
- the Java classes under test
- EvoSuite generation settings
- validation settings
- LLM refactoring models
- prompt scenarios
- summarization settings
- extraction settings
- metric settings
- candidate selection settings
- report generation settings
- logging behavior

The example configuration used in the quickstart is:

```text
configs/experiments/evosuite_simple_project.yaml
```
## 1. Configuration Philosophy

TestHumanizer follows a configuration-first design.

Most behavior should be controlled from the YAML file. The CLI is mainly used to launch experiments and optionally override common parameters such as models, scenarios, iterations, output directory, and logging.

This makes experiments easier to reproduce because the effective configuration is copied into the output directory at the beginning of each run:

```text
outputs/<experiment_name>/config.yaml
```
## 2. Inspect a Configuration

Before running an experiment, you can inspect the parsed configuration with:

```bash
testhumanizer inspect-config \
  --config configs/experiments/evosuite_simple_project.yaml
```
This is useful for checking whether paths, models, scenarios, and metric settings are loaded correctly.

## 3. Minimal Configuration Structure

A TestHumanizer YAML file generally follows this structure:

```yaml
experiment:
  name: evosuite_simple_project
  output_dir: outputs/evosuite_simple_project

dataset:
  targets_file: configs/experiments/targets_simple_project.csv

test_generation:
  enabled: true
  tool: evosuite

validation:
  compilation:
    enabled: true
  coverage:
    enabled: true
  refactored:
    enabled: true

preparation:
  refactoring_inputs: true
  refactoring_prompts: true

summarization:
  enabled: true

llm_execution:
  refactoring_outputs: true

extraction:
  refactored_suites: true

metrics:
  ctses:
    enabled: true
  embeddings:
    enabled: true
  readability:
    enabled: true
  complexity:
    enabled: true

selection:
  enabled: true

reports:
  synthetic:
    enabled: true

logging:
  level: normal
```
The exact fields can be extended depending on the tools and metrics you enable.

## 4. Experiment Section

The `experiment` section defines the name and output directory of the run.

Example:

```yaml
experiment:
  name: evosuite_simple_project
  output_dir: outputs/evosuite_simple_project
```
### Fields

| Field        | Description                                 |
|--------------|---------------------------------------------|
| `name`       | Human-readable name of the experiment       |
| `output_dir` | Directory where all outputs will be written |

The pipeline creates the output directory automatically if it does not already exist.

## 5. Dataset Section

The `dataset` section points to the CSV file listing the Java classes under test.

Example:

```yaml
dataset:
  targets_file: configs/experiments/targets_simple_project.csv
```
The target CSV describes each class that should be processed by TestHumanizer.

Typical fields include:

```text
dataset,project,class_name,bug_id,source_path,classpath,test_class_fqdn,class_files_dir,source_files_dir
```
### Important target fields

| Field              | Description                                                           |
|--------------------|-----------------------------------------------------------------------|
| `dataset`          | Dataset name, for example `custom`, `Defects4J`, or another benchmark |
| `project`          | Project name                                                          |
| `class_name`       | Simple class name                                                     |
| `bug_id`           | Optional bug identifier                                               |
| `source_path`      | Path to the Java source file                                          |
| `classpath`        | Classpath required to compile and run the class                       |
| `test_class_fqdn`  | Fully qualified class name                                            |
| `class_files_dir`  | Directory containing compiled `.class` files                          |
| `source_files_dir` | Root source directory                                                 |

For custom Java projects, these paths must be correct before running EvoSuite and validation.

## 6. Test Generation Section

The `test_generation` section controls EvoSuite.

Example:

```yaml
test_generation:
  enabled: true
  tool: evosuite
  evosuite_jar: tools/evosuite-master-1.2.1-SNAPSHOT.jar
  runs_per_class: 1
  search_budget_seconds: 60
  algorithm: DynaMOSA
  stopping_condition: MaxTime
  criterion: BRANCH:METHOD:LINE
  generate_mo_suite: true
  show_progress: false
  disable_minimization: false
  disable_cleanup: false
  java_cmd: java
  java_memory: -Xmx512M
```
### Fields

| Field                   | Description                                |
|-------------------------|--------------------------------------------|
| `enabled`               | Enables or disables EvoSuite generation    |
| `tool`                  | Currently expected to be `evosuite`        |
| `evosuite_jar`          | Path to the EvoSuite jar                   |
| `runs_per_class`        | Number of EvoSuite runs per target class   |
| `search_budget_seconds` | Time budget per EvoSuite run               |
| `algorithm`             | EvoSuite search algorithm                  |
| `stopping_condition`    | EvoSuite stopping condition                |
| `criterion`             | EvoSuite coverage criteria                 |
| `generate_mo_suite`     | Whether to generate multi-objective suites |
| `show_progress`         | Whether EvoSuite progress should be shown  |
| `disable_minimization`  | Whether to disable EvoSuite minimization   |
| `disable_cleanup`       | Whether to disable EvoSuite cleanup        |
| `java_cmd`              | Java command                               |
| `java_memory`           | JVM memory argument                        |

If `enabled` is `false`, Phase 2 is skipped.

## 7. Validation Section

The `validation` section controls compilation, JUnit execution, coverage, and refactored-suite validation.

Example:

```yaml
validation:
  compilation:
    enabled: true

  junit:
    enabled: true

  coverage:
    enabled: true
    jacoco_agent_jar: tools/jacoco-0.8.8/lib/jacocoagent.jar
    jacoco_cli_jar: tools/jacoco-0.8.8/lib/jacococli.jar

  refactored:
    enabled: true
```
### Compilation

Compilation validates that generated and refactored test suites are syntactically and semantically valid Java code.

```yaml
validation:
  compilation:
    enabled: true
```
### JUnit

JUnit validation checks whether the generated or refactored test suites execute successfully.

```yaml
validation:
  junit:
    enabled: true
```
### Coverage

Coverage validation uses JaCoCo when enabled.

```yaml
validation:
  coverage:
    enabled: true
```
You can disable coverage from the CLI:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --no-coverage
```
### Refactored Validation

The refactored validation block controls whether TestHumanizer validates LLM-refactored suites.

```yaml
validation:
  refactored:
    enabled: true
```
## 8. Preparation Section

The `preparation` section controls the preparation of LLM inputs and prompts.

Example:

```yaml
preparation:
  refactoring_inputs: true
  refactoring_prompts: true
```
### Fields

| Field                 | Description                                                  |
|-----------------------|--------------------------------------------------------------|
| `refactoring_inputs`  | Enables preparation of structured inputs from EvoSuite tests |
| `refactoring_prompts` | Enables prompt generation for the configured scenarios       |

If `refactoring_inputs` is disabled, Phase 4 is skipped.

If `refactoring_prompts` is disabled, Phase 5A is skipped.

## 9. Refactoring Scenarios

TestHumanizer supports three main scenarios:

```yaml
scenarios:
  - tests-only
  - code-centric
  - summary-based
```
### `tests-only`

The LLM receives only the generated test suite.

### `code-centric`

The LLM receives the generated test suite and additional production-code context.

### `summary-based`

The LLM receives the generated test suite and a source-code summary.

The scenarios can also be overridden from the CLI:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --scenarios tests-only
```
or:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --scenarios all
```
## 10. Summarization Section

The `summarization` section controls source-code summarization and optional summary quality evaluation.

Example:

```yaml
summarization:
  enabled: true
  iterations: 1
  max_attempts: 3
  selection_policy: threshold_then_best
  keep_best_if_below_threshold: true
  side_threshold: 0.5
  inject_into_summary_based: true

  prompt:
    require_code_fence: true
    extract_from_code_fence: true
    max_total_tokens: 128000
    reserved_response_tokens: 16000

  llm:
    name: gpt4o-summary
    provider: openai
    model: gpt-4o
    api_key_env: OPENAI_API_KEY_1
    temperature: 0.1
    max_retries: 30
    retry_wait_seconds: 10
    timeout_seconds: 120
    reserved_response_tokens: 16000
    max_total_tokens: 128000

  official_side:
    enabled: false
    use_for_selection: false
    model_dir: tools/SIDE_Model/hard-negatives
    device: auto
    max_length: 512
    threshold: 0.5

  llm_side:
    enabled: true
    use_for_selection: true
    threshold: 0.5
    provider: openai
    model: gpt-4o
    api_key_env: OPENAI_API_KEY_1
    temperature: 0.0
    max_retries: 30
    retry_wait_seconds: 10
    timeout_seconds: 120
    reserved_response_tokens: 2000
    max_total_tokens: 128000

  output:
    skip_existing: true
    save_raw_outputs: true
    save_attempts: true
```
### Main fields

| Field                          | Description                                                      |
|--------------------------------|------------------------------------------------------------------|
| `enabled`                      | Enables or disables source summarization                         |
| `iterations`                   | Number of summary candidates                                     |
| `max_attempts`                 | Maximum attempts per source class                                |
| `selection_policy`             | Strategy for selecting the best summary                          |
| `keep_best_if_below_threshold` | Keeps the best summary even if below threshold                   |
| `side_threshold`               | Summary quality threshold                                        |
| `inject_into_summary_based`    | Makes selected summaries available to the summary-based scenario |

### LLM-SIDE

`llm_side` allows an LLM judge to evaluate generated summaries.

Useful metadata may include:

- faithfulness
- coverage
- conciseness
- hallucination risk
- LLM-SIDE score
- selection status

## 11. LLM Execution Section

The `llm_execution` section controls whether raw refactoring outputs are produced.

Example:

```yaml
llm_execution:
  refactoring_outputs: true
```
If this is disabled, Phase 5B is skipped.

You can also disable LLM calls from the CLI:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --no-llm
```
This is useful when existing LLM outputs already exist and you only want to rerun extraction, validation, metrics, selection, or reporting.

## 12. LLM Model Configuration

The exact model section may vary depending on your setup, but a typical configuration defines aliases such as:

```yaml
models:
  gpt4o:
    provider: openai
    model: gpt-4o
    api_key_env: OPENAI_API_KEY_1
    temperature: 0.2
    max_retries: 30
    retry_wait_seconds: 10
    timeout_seconds: 120

  mistral:
    provider: mistral
    model: mistral-large-latest
    api_key_env: MISTRAL_API_KEY_2
    temperature: 0.2
    max_retries: 30
    retry_wait_seconds: 10
    timeout_seconds: 120
```
### Fields

| Field                | Description                                     |
|----------------------|-------------------------------------------------|
| `provider`           | LLM provider, for example `openai` or `mistral` |
| `model`              | Provider-specific model name                    |
| `api_key_env`        | Environment variable containing the API key     |
| `temperature`        | Sampling temperature                            |
| `max_retries`        | Maximum API retries                             |
| `retry_wait_seconds` | Wait time between retries                       |
| `timeout_seconds`    | Request timeout                                 |

You can override the selected models from the CLI:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --models gpt4o,mistral
```
You can override the temperature from the CLI:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --temperature 0.1
```
## 13. Extraction Section

The `extraction` section controls Java extraction from raw LLM outputs.

Example:

```yaml
extraction:
  refactored_suites: true
```
Phase 6 reads raw LLM outputs and prepared inputs, then reconstructs complete refactored Java test suites.

The extracted suites are written under:

```text
outputs/<experiment_name>/04_refactorings/extracted_suites/
```
## 14. CTSES Metrics Section

The `metrics.ctses` section controls CTSES computation.

Example:

```yaml
metrics:
  ctses:
    enabled: true
    codebleu_enabled: true
    codebleu_python: .venv-codebleu/bin/python
```
CTSES combines:

- CodeBLEU
- METEOR
- ROUGE-L

The implementation reports three variants:

| Variant           | Meaning                            |
|-------------------|------------------------------------|
| `average_score_1` | Uniform CTSES average baseline     |
| `CTSES_score_1`   | Semantic-prioritized CTSES profile |
| `CTSES_score_2`   | Readability-aware CTSES profile    |

The results are written under:

```text
outputs/<experiment_name>/06_metrics/ctses/
```
## 15. Embedding Metrics Section

The `metrics.embeddings` section controls embedding-based cosine similarity.

Example:

```yaml
metrics:
  embeddings:
    enabled: true
    preprocess: true

    codebert:
      enabled: true
      model_name: microsoft/codebert-base
      device: auto
      max_length: 512

    graphcodebert:
      enabled: true
      model_name: microsoft/graphcodebert-base
      device: auto
      max_length: 512

    openai:
      enabled: true
      model_name: text-embedding-3-small
      api_key_env: OPENAI_API_KEY_1
      max_retries: 30
      retry_wait_seconds: 15
      timeout_seconds: 120
      cache_enabled: true
```
### Fields

| Field                   | Description                                                        |
|-------------------------|--------------------------------------------------------------------|
| `preprocess`            | Whether to preprocess Java code before embedding                   |
| `codebert.enabled`      | Enables CodeBERT similarity                                        |
| `graphcodebert.enabled` | Enables GraphCodeBERT similarity                                   |
| `openai.enabled`        | Enables OpenAI embedding similarity                                |
| `device`                | Can be `auto`, `cpu`, or a CUDA device depending on implementation |
| `max_length`            | Maximum input token length for HF models                           |
| `cache_enabled`         | Enables OpenAI embedding cache                                     |

Results are written under:

```text
outputs/<experiment_name>/06_metrics/embeddings/
```
## 16. Readability Metrics Section

The `metrics.readability` section controls Scalabrino readability analysis.

Example:

```yaml
metrics:
  readability:
    enabled: true
    scalabrino: true
    rsm_dir: tools/Readability-model
    rsm_jar: rsm.jar
    java_cmd: java
    timeout_seconds: 60
```
### Fields

| Field             | Description                                |
|-------------------|--------------------------------------------|
| `enabled`         | Enables readability metrics                |
| `scalabrino`      | Enables the Scalabrino readability model   |
| `rsm_dir`         | Directory containing the readability model |
| `rsm_jar`         | Readability model jar                      |
| `java_cmd`        | Java command                               |
| `timeout_seconds` | Timeout per analyzed file                  |

Results are written under:

```text
outputs/<experiment_name>/06_metrics/readability/
```
## 17. Complexity Metrics Section

The `metrics.complexity` section controls CCTR and PMD.

Example:

```yaml
metrics:
  complexity:
    enabled: true

    cctr:
      enabled: true

    pmd:
      enabled: true
      pmd_dir: tools/pmd-bin-7.0.0-rc4
      ruleset: category/java/design.xml
      timeout_seconds: 60
```
### CCTR

CCTR computes cognitive complexity for original and refactored test suites.

```yaml
metrics:
  complexity:
    cctr:
      enabled: true
```
Results are written under:

```text
outputs/<experiment_name>/06_metrics/complexity/cctr/
```
### PMD

PMD computes additional complexity and maintainability indicators.

```yaml
metrics:
  complexity:
    pmd:
      enabled: true
```
Results are written under:

```text
outputs/<experiment_name>/06_metrics/complexity/pmd/
```
## 18. Candidate Selection Section

The `selection` section controls how the best refactored candidates are selected.

Example:

```yaml
selection:
  enabled: true
  policy: first_passing_then_best

  hard_constraints:
    require_compile_ok: true
    require_junit_ok: true

  cosine_similarity:
    enabled: true
    threshold: 0.80
    primary_metric: cosine_similarity
    primary_embedding_model_alias: openai
    diagnostic_metrics:
      - codebert
      - graphcodebert

  ctses:
    enabled: true
    threshold: 0.50
    primary_metric: ctses_score
    fallback_metric: codebleu_score

  ranking:
    cosine_weight: 0.60
    ctses_weight: 0.40

  output:
    directory: 06_metrics/selection
```
### Selection logic

The default policy applies:

1.  Hard validation constraints.
2.  Semantic preservation thresholds.
3.  CTSES threshold.
4.  Weighted ranking if multiple candidates are valid.

### Main output

```text
outputs/<experiment_name>/06_metrics/selection/selected_candidates.csv
```
## 19. Reports Section

The `reports` section controls synthetic report generation.

Example:

```yaml
reports:
  synthetic:
    enabled: true
    output_dir: 07_reports
    export_html: true
    export_png: true
    png_scale: 3
```
### Outputs

```text
outputs/<experiment_name>/07_reports/synthetic_report.md
outputs/<experiment_name>/07_reports/synthetic_report.html
outputs/<experiment_name>/07_reports/report_summary.json
outputs/<experiment_name>/07_reports/figures/
```
PNG export may require additional Plotly/Kaleido support.

## 20. Logging Section

The `logging` section controls terminal output.

Example:

```yaml
logging:
  level: normal
  show_phase_headers: true
  show_per_item_details: false
  show_metric_details: false
  show_warnings: true
```
### Fields

| Field                   | Description                       |
|-------------------------|-----------------------------------|
| `level`                 | `quiet`, `normal`, or `verbose`   |
| `show_phase_headers`    | Shows phase panels                |
| `show_per_item_details` | Shows per-item processing details |
| `show_metric_details`   | Shows detailed metric logs        |
| `show_warnings`         | Shows warnings                    |

### CLI overrides

Quiet mode:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --quiet
```
Verbose mode:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --verbose
```
Show per-item details:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --show-details
```
Show metric details:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --show-metrics
```
## 21. CLI Overrides

The CLI can override common YAML settings.

### Models

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --models gpt4o,mistral
```
### Temperature

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --temperature 0.1
```
### Iterations

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --iterations 3
```
### Scenarios

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --scenarios tests-only,code-centric,summary-based
```
or:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --scenarios all
```
### Output directory

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --output-dir outputs/my_run
```
### Disable LLM execution

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
## 22. Presets

The CLI supports three presets.

### `ready`

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset ready
```
Uses the YAML configuration as the source of truth.

### `fast`

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast
```
Runs all scenarios with one iteration unless explicitly overridden.

### `full`

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset full
```
Runs all scenarios with three iterations unless explicitly overridden.

## 23. Recommended Configuration Profiles

### Fast sanity run

Use for installation and debugging.

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast
```
### Full experiment

Use when collecting experimental results.

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset full
```
### Metrics-only rerun

Use when LLM outputs already exist.

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast \
  --no-llm
```
### Debug run

Use for inspecting detailed behavior.

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast \
  --verbose
```
## 24. Configuration Tips

### Keep paths relative to the repository root

This makes the configuration more portable.

Prefer:

```text
evosuite_jar: tools/evosuite-master-1.2.1-SNAPSHOT.jar
```
over:

```text
evosuite_jar: /home/user/project/tools/evosuite-master-1.2.1-SNAPSHOT.jar
```
### Keep API keys outside the YAML

Use environment variables:

```text
api_key_env: OPENAI_API_KEY_1
```
Then export the key in your shell:

```bash
export OPENAI_API_KEY_1="your-key"
```
### Use `fast` first

Before running a full experiment, validate the setup with:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast
```
### Keep output directories separate

For different experiments, use different output directories:

```yaml
experiment:
  output_dir: outputs/my_new_experiment
```
### Use `--no-llm` for debugging

When raw LLM outputs already exist, avoid new API calls with:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --no-llm
```
## 25. Common Configuration Errors

### Wrong EvoSuite path

Symptom:

```text
EvoSuite generation fails.
```
Check:

```yaml
test_generation:
  evosuite_jar: tools/evosuite-master-1.2.1-SNAPSHOT.jar
```
### Wrong classpath

Symptoms:

```text
Target class not found
Compilation failed
JUnit failed
```
Check the target CSV fields:

```text
classpath
class_files_dir
source_files_dir
test_class_fqdn
```
### Missing API key

Symptom:

```text
LLM call failed
OpenAI embedding failed
```
Check:

```bash
echo $OPENAI_API_KEY_1
echo $MISTRAL_API_KEY_2
```
### Wrong CodeBLEU environment

Symptom:

```text
CodeBLEU error
```
Check:

```yaml
metrics:
  ctses:
    codebleu_python: .venv-codebleu/bin/python
```
### Wrong PMD path

Symptom:

```text
PMD evaluation failed
```
Check:

```yaml
metrics:
  complexity:
    pmd:
      pmd_dir: tools/pmd-bin-7.0.0-rc4
```
### Wrong readability model path

Symptom:

```text
Readability evaluation failed
```
Check:

```yaml
metrics:
  readability:
    rsm_dir: tools/Readability-model
    rsm_jar: rsm.jar
```
## 26. Validation Checklist

Before running a full experiment, check:

- [ ] Python environment is activated
- [ ] TestHumanizer is installed with pip install -e .
- [ ] Java and javac are available
- [ ] EvoSuite jar exists
- [ ] JUnit and Hamcrest jars exist
- [ ] JaCoCo jars exist if coverage is enabled
- [ ] PMD exists if PMD metrics are enabled
- [ ] Scalabrino readability jar exists if readability is enabled
- [ ] CodeBLEU environment exists if CodeBLEU is enabled
- [ ] OpenAI/Mistral API keys are exported if LLM calls are enabled
- [ ] Target CSV paths are correct
- [ ] Output directory is writable
## 27. Next Steps

After configuring an experiment, run:

```bash
testhumanizer inspect-config \
  --config configs/experiments/evosuite_simple_project.yaml
```
Then run:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast
```
For custom projects, continue with:

```text
docs/CUSTOM_PROJECTS.md
```
For developers who want to extend the pipeline, continue with:

```text
docs/ARCHITECTURE.md
docs/EXTENDING.md
```
