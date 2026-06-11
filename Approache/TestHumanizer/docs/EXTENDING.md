# Extending TestHumanizer

This document explains how to extend TestHumanizer.

It is intended for developers and researchers who want to customize the pipeline, add new models, define new prompt scenarios, integrate new metrics, modify candidate selection, or generate additional reports.

## 1. Extension Philosophy

TestHumanizer is designed as a modular, configuration-driven, file-based pipeline.

Most extensions should follow these principles:

```text
configuration-first
phase-level modularity
stable metadata identifiers
CSV/JSONL outputs
clear status and error fields
clean logging
reproducible outputs
```
A good extension should:

- [ ] be controlled from the YAML configuration
- [ ] read existing phase artifacts when possible
- [ ] write structured outputs
- [ ] avoid breaking downstream phases
- [ ] preserve identifiers such as class_name, testsuite_id, scenario_id, model_alias, and iteration
- [ ] use THLogger instead of direct console.print calls
- [ ] include documentation
## 2. Main Extension Points

The most common extension points are:

| Extension                            | Main location                                      |
|--------------------------------------|----------------------------------------------------|
| Add a new LLM provider               | `testhumanizer/refactoring/`                       |
| Add a new model alias                | YAML configuration                                 |
| Add a new prompt scenario            | `testhumanizer/refactoring/prompt_preparer.py`     |
| Add a new summarization strategy     | `testhumanizer/summarization/`                     |
| Add a new metric                     | `testhumanizer/metrics/`                           |
| Add a new embedding backend          | `testhumanizer/metrics/embeddings/`                |
| Add a new complexity metric          | `testhumanizer/metrics/complexity/`                |
| Add a new candidate selection policy | `testhumanizer/selection/candidate_selector.py`    |
| Add a new report figure              | `testhumanizer/reports/synthetic_report.py`        |
| Add a new test generator             | `testhumanizer/generators/`                        |
| Add a new dataset adapter            | `testhumanizer/core/targets.py` or related loaders |
| Modify logging                       | `testhumanizer/utils/logging.py`                   |

## 3. Before Adding a Feature

Before implementing a new feature, identify:

1. Which phase does it belong to?
2. What input files does it need?
3. What output files will it write?
4. What YAML configuration is needed?
5. Does candidate selection or reporting need to consume it?
6. Does it need to be visible in normal logs?
7. How should failures be represented?
Recommended output pattern:

```text
outputs/<experiment>/06_metrics/<new_metric>/
├── <new_metric>_results.csv
├── <new_metric>_results.jsonl
├── <new_metric>_summary.csv
└── <new_metric>_summary.jsonl
```
For non-metric phases, follow the existing output directory convention.

## 4. Logging Convention

TestHumanizer uses:

```text
testhumanizer/utils/logging.py
```
New components should use:

```python
from testhumanizer.utils.logging import THLogger
```
Example:

```python
class MyComponent:
    def __init__(self, output_dir, config):
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.config = config
        self.log = THLogger(config)

    def run(self):
        self.log.detail("Detailed per-item information.")
        self.log.metric("Metric-level debug information.")
        self.log.warning("Recoverable issue.")
        self.log.success("My component completed: rows=10, ok=10/10.")
```
### Logging levels

Use:

```text
success  -> one concise summary at the end of a phase
warning  -> important recoverable issues
error    -> serious failures
detail   -> per-item processing logs
metric   -> per-item metric values
```
Avoid direct `console.print(...)` in pipeline components.

## 5. Adding a New LLM Model Alias

The simplest extension is adding a new model alias in the YAML configuration.

Example:

```yaml
models:
  my_model:
    provider: openai
    model: gpt-4o
    api_key_env: OPENAI_API_KEY_1
    temperature: 0.2
    max_retries: 30
    retry_wait_seconds: 10
    timeout_seconds: 120
```
Then run:

```bash
testhumanizer run \
  --config configs/experiments/my_config.yaml \
  --models my_model
```
If the provider is already supported, no code change is needed.

## 6. Adding a New LLM Provider

To add a new provider, update the LLM execution layer.

Typical location:

```text
testhumanizer/refactoring/llm_refactorer.py
```
Recommended steps:

1. Create a provider client or provider-specific call function.
2. Add provider configuration fields in YAML.
3. Add dispatch logic based on provider name.
4. Preserve model_alias, provider, and model in output metadata.
5. Implement retries, timeout, and error handling.
6. Ensure raw outputs are saved in raw_refactoring_outputs.jsonl.
7. Add documentation and an example config.
Example YAML:

```yaml
models:
  my_provider_model:
    provider: my_provider
    model: my-provider-model-name
    api_key_env: MY_PROVIDER_API_KEY
    temperature: 0.2
    max_retries: 20
    retry_wait_seconds: 10
    timeout_seconds: 120
```
Recommended raw output fields:

```text
id
dataset
project
class_name
bug_id
testsuite_id
scenario
scenario_id
model_alias
provider
model
iteration
status
raw_output
error
```
The provider should not break downstream phases if one call fails. Instead, save a failed row with `status=error`.

## 7. Adding a New Prompt Scenario

Prompt scenarios are prepared before LLM execution.

Main location:

```text
testhumanizer/refactoring/prompt_preparer.py
```
Existing scenarios include:

```text
tests-only
code-centric
summary-based
```
To add a new scenario:

1. Add the scenario name to the YAML configuration.
2. Add prompt-construction logic in the prompt preparer.
3. Include scenario-specific metadata.
4. Make sure the scenario_id is stable.
5. Ensure LLM outputs use the same scenario_id.
6. Ensure extraction, validation, metrics, selection, and reports preserve the scenario_id.
Example scenario name:

```text
assertion-focused
```
Example CLI use:

```bash
testhumanizer run \
  --config configs/experiments/my_config.yaml \
  --scenarios assertion-focused
```
Recommended metadata fields:

```text
scenario
scenario_id
prompt_chars
prompt_tokens
summary_used
summary_source
context_used
```
### Prompt scenario design tips

A good scenario should clearly define:

```text
what the LLM sees
what the LLM is allowed to change
what must be preserved
expected output format
whether code fences are required
```
Always keep extraction in mind. If the output format is too flexible, Phase 6 may become fragile.

## 8. Adding a New Summarization Strategy

Summarization is handled under:

```text
testhumanizer/summarization/
```
Current summarization outputs include:

```text
03_summaries/source_summaries.jsonl
03_summaries/source_summaries_metadata.csv
03_summaries/summary_attempts.jsonl
```
To add a new summarization strategy:

1. Add configuration fields under summarization.
2. Implement or modify summary generation.
3. Store every attempt when useful.
4. Store selected summaries.
5. Add quality metadata if available.
6. Update summary injection into summary-based prompts.
Recommended fields:

```text
summary_text
selected
selection_reason
summary_model
summary_provider
quality_score
faithfulness
coverage
hallucination_risk
error
```
### Adding a new summary evaluator

If you want to add another summary quality evaluator:

1. Create a new module under testhumanizer/metrics/side/ or testhumanizer/summarization/.
2. Return structured scores.
3. Add configuration flags.
4. Store evaluator outputs in source_summaries_metadata.csv.
5. Decide whether the evaluator is used for selection.
## 9. Adding a New Metric

Metrics are usually added under:

```text
testhumanizer/metrics/
```
Recommended module layout:

```text
testhumanizer/metrics/my_metric/
├── __init__.py
├── evaluator.py
└── runner.py
```
Use `runner.py` if the metric depends on an external tool. Use `evaluator.py` to load pipeline artifacts, call the runner, and write outputs.

### Recommended evaluator skeleton

```python
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from testhumanizer.utils.logging import THLogger

class MyMetricEvaluator:
    def __init__(self, *, output_dir: str | Path, config: Dict[str, Any]) -> None:
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.config = config
        self.metric_config = config.get("metrics", {}).get("my_metric", {})
        self.log = THLogger(config)

    def evaluate(self, *, input_csv: str | Path) -> None:
        rows: List[Dict[str, Any]] = []

        # Load inputs
        # Compute metric
        # Append rows

        output_root = self.output_dir / "06_metrics" / "my_metric"
        output_root.mkdir(parents=True, exist_ok=True)

        # Write CSV and JSONL

        ok_rows = [row for row in rows if row.get("status") == "ok"]

        self.log.success(
            f"My metric completed: rows={len(rows)}, ok={len(ok_rows)}/{len(rows)}."
        )
```
### Recommended metric output fields

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
metric_value
status
error
```
### Add metric to YAML

```yaml
metrics:
  my_metric:
    enabled: true
    option_a: value
    option_b: value
```
### Register metric in the pipeline

Add a phase or subphase in:

```text
testhumanizer/core/pipeline.py
```
Example:

```yaml
my_metric_config = self.config.get("metrics", {}).get("my_metric", {})

if my_metric_config.get("enabled", False):
    evaluator = MyMetricEvaluator(
        output_dir=self.output_dir,
        config=self.config,
    )
    evaluator.evaluate(input_csv=some_input_path)
    self.log.success("My metric computed.")
else:
    self.log.warning("My metric disabled.")
```
## 10. Adding a New Embedding Backend

Embedding metrics are located under:

```text
testhumanizer/metrics/embeddings/
```
Current backends include:

```text
CodeBERT
GraphCodeBERT
OpenAI embeddings
```
To add a new backend:

1. Implement an embedder class.
2. Add configuration fields under metrics.embeddings.
3. Register the backend in the embedding evaluator.
4. Write embedding_model_alias and embedding_model_name to outputs.
5. Add status and error handling.
6. Update candidate selection if the backend becomes primary.
Example config:

```yaml
metrics:
  embeddings:
    my_embedder:
      enabled: true
      model_name: my/model-name
      device: auto
      max_length: 512
```
Recommended output fields:

```text
embedding_model_alias
embedding_model_name
device
cosine_similarity
original_token_count
refactored_token_count
original_truncated
refactored_truncated
status
error
```
## 11. Adding a New Complexity Metric

Complexity metrics are located under:

```text
testhumanizer/metrics/complexity/
```
Current complexity metrics include:

```text
CCTR cognitive complexity
PMD complexity and maintainability
```
To add a new complexity metric:

1. Add a calculator or runner.
2. Add an evaluator.
3. Add configuration under metrics.complexity.
4. Write results under 06_metrics/complexity/<metric_name>/.
5. Include original and refactored suite results.
6. Add summaries when useful.
Recommended output directory:

```text
06_metrics/complexity/my_complexity_metric/
```
## 12. Adding a New Candidate Selection Policy

Candidate selection is handled by:

```text
testhumanizer/selection/candidate_selector.py
```
The default policy is:

```text
first_passing_then_best
```
To add a new policy:

1. Add a new policy name in YAML.
2. Implement the policy logic in the candidate selector.
3. Preserve hard constraints.
4. Compute policy-specific scores.
5. Store selection_reason.
6. Store whether thresholds were passed.
7. Update reports if the new policy adds fields.
Example YAML:

```yaml
selection:
  enabled: true
  policy: best_composite_score

  ranking:
    cosine_weight: 0.50
    ctses_weight: 0.30
    readability_weight: 0.20
```
### Recommended selection output fields

```text
selected
selection_reason
passes_all_thresholds
selection_cosine_score
selection_ctses_score
selection_composite_score
selected_refactored_test_file
```
### Selection policy guidelines

A good policy should:

```text
never select uncompilable candidates unless explicitly configured
prefer JUnit-passing candidates
make threshold failures visible
avoid hiding why a candidate was selected
be deterministic when scores are tied
```
## 13. Adding a New Report Figure

Reports are generated in:

```text
testhumanizer/reports/synthetic_report.py
```
To add a new figure:

1. Load the relevant metric CSV.
2. Create a Plotly figure.
3. Save the figure as HTML.
4. Optionally save it as PNG.
5. Add a link or embedded reference in the report.
6. Add a summary sentence in Markdown.
Recommended output directory:

```text
07_reports/figures/
```
Recommended file names:

```text
my_metric_by_scenario.html
my_metric_by_scenario.png
```
### Figure design tips

Good report figures should compare:

```text
models
scenarios
iterations
original vs refactored
selected candidates
metric trade-offs
```
Avoid overly large figures when preparing reports for papers.

## 14. Adding a New Test Generator

Test generation is currently EvoSuite-based.

Main location:

```text
testhumanizer/generators/
```
To add a new generator:

1. Create a new generator class.
2. Define a generate(target, output_dir) method.
3. Return generated suite metadata in the same format as EvoSuite indexing.
4. Add configuration under test_generation.
5. Add dispatch logic in the pipeline.
6. Ensure Phase 3 can validate the generated tests.
Example YAML:

```yaml
test_generation:
  enabled: true
  tool: my_generator
  my_generator_path: tools/my-generator.jar
```
### Important compatibility requirement

The generator must produce or be converted into metadata compatible with:

```text
02_evosuite/original_suites_metadata.csv
```
Even if the generator is not EvoSuite, downstream phases expect a metadata file describing original generated suites.

## 15. Adding a New Dataset Adapter

Target loading is handled near:

```text
testhumanizer/core/targets.py
```
To support a new dataset format:

1. Read the dataset-specific metadata.
2. Convert each target into the internal target representation.
3. Preserve dataset, project, class_name, bug_id, source_path, classpath, test_class_fqdn, class_files_dir, and source_files_dir.
4. Write resolved targets to 01_targets/.
If possible, prefer converting your dataset to the standard target CSV format instead of adding custom logic.

Standard target CSV fields:

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
## 16. Adding a New Output Artifact

When adding a new output artifact, follow the existing conventions.

### Use CSV for tabular data

CSV is good for:

```text
metrics
summaries
metadata
selection results
validation results
```
### Use JSONL for structured or nested data

JSONL is good for:

```text
prompts
raw LLM outputs
source summaries
extracted code
nested metadata
```
### Always include stable identifiers

Recommended fields:

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
provider
model
status
error
```
## 17. Adding Configuration Options

When adding configuration options:

1. Choose a clear YAML location.
2. Use explicit names.
3. Provide safe defaults.
4. Avoid hardcoded absolute paths.
5. Document the option.
6. Support CLI overrides only for commonly changed options.
Example:

```yaml
metrics:
  my_metric:
    enabled: true
    threshold: 0.75
    timeout_seconds: 60
```
Avoid ambiguous names such as:

```text
setting: true
value: 0.5
mode: auto
```
Prefer:

```yaml
my_metric:
  enabled: true
  similarity_threshold: 0.5
  device: auto
```
## 18. Updating the CLI

The CLI is implemented in:

```text
testhumanizer/cli.py
```
Only add CLI flags for options that users frequently override.

Good CLI override candidates:

```text
models
scenarios
iterations
temperature
output_dir
logging level
disable LLM execution
disable coverage
```
Avoid adding CLI flags for every low-level option. Those should remain in the YAML.

When adding a CLI option:

1. Add an argparse argument.
2. Apply it through the override layer.
3. Make sure explicit CLI values override presets.
4. Document it in README.md and CONFIGURATION.md.
## 19. Error Handling Guidelines

For batch-processing phases, prefer per-item errors over full pipeline failure.

Recommended pattern:

```yaml
try:
    result = process_item(item)
    row["status"] = "ok"
    row["error"] = ""
except Exception as e:
    row["status"] = "error"
    row["error"] = f"{type(e).__name__}: {e}"
```
Then continue processing.

At the end:

```text
self.log.success(
    f"My phase completed: rows={len(rows)}, ok={ok_count}/{len(rows)}, errors={error_count}."
)
```
Use hard failures only for:

```text
invalid global configuration
missing mandatory input file
unsupported tool
corrupt configuration
```
## 20. Testing an Extension

After implementing an extension, test it on the included simple Java project.

### Compile check

```bash
python -m py_compile path/to/modified_file.py
```
### Quick run

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast
```
### Verbose run

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast \
  --verbose
```
### Metric detail run

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast \
  --show-metrics
```
### No new LLM calls

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast \
  --no-llm
```
## 21. Backward Compatibility

When modifying outputs, avoid breaking existing scripts.

Recommended strategy:

```text
add new columns instead of renaming old ones
keep old aliases when possible
document deprecated fields
preserve JSONL structure where possible
avoid changing IDs unless necessary
```
Example:

```text
CTSES_score_1
```
can be kept even if a clearer name such as:

```text
CTSES_1
```
is added later.

## 22. Documentation Checklist

When adding a feature, update:

```text
README.md
docs/CONFIGURATION.md
docs/ARCHITECTURE.md
docs/PIPELINE_PHASES.md
docs/METRICS.md, if metric-related
docs/EXTENDING.md, if developer-facing
docs/TROUBLESHOOTING.md, if the feature can fail in common ways
```
For small internal changes, a short note in `ARCHITECTURE.md` or `EXTENDING.md` may be enough.

## 23. Release Checklist for Extensions

Before considering an extension complete:

- [ ] The code compiles
- [ ] The simple Java project still runs
- [ ] The extension is configurable
- [ ] Outputs are written in a stable location
- [ ] Outputs include status and error fields
- [ ] Normal logs are concise
- [ ] Detailed logs are available with --show-details or --show-metrics
- [ ] Candidate selection still works
- [ ] Reports still generate
- [ ] Documentation is updated
## 24. Example: Adding a New Metric End-to-End

Suppose you want to add a metric named `assertion_density`.

### Step 1: Add configuration

```yaml
metrics:
  assertion_density:
    enabled: true
```
### Step 2: Create module

```text
testhumanizer/metrics/assertion_density/
├── __init__.py
└── evaluator.py
```
### Step 3: Implement evaluator

```python
class AssertionDensityEvaluator:
    def __init__(self, *, output_dir, config):
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.config = config
        self.log = THLogger(config)

    def evaluate(self, *, extracted_suites_csv):
        rows = []

        # Load extracted suites
        # Count assertions
        # Compute assertion density
        # Write outputs

        self.log.success(
            f"Assertion density completed: rows={len(rows)}."
        )
```
### Step 4: Register in pipeline

Add a new phase or subphase in:

```text
testhumanizer/core/pipeline.py
```
### Step 5: Add report support

If the metric is useful to users, add a figure or table in:

```text
testhumanizer/reports/synthetic_report.py
```
### Step 6: Document it

Update:

```text
docs/METRICS.md
docs/CONFIGURATION.md
docs/PIPELINE_PHASES.md
```
## 25. Summary

To extend TestHumanizer safely:

1. Keep the extension modular.
2. Make it configurable.
3. Preserve identifiers.
4. Write structured outputs.
5. Use clean logging.
6. Handle failures gracefully.
7. Test on the simple Java example.
8. Update documentation.
Following these rules helps keep TestHumanizer reproducible, maintainable, and easy to customize.
