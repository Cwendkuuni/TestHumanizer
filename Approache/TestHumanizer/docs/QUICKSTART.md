# Quickstart

This guide shows how to run TestHumanizer on the included example Java project.

The goal is to quickly verify that the installation, configuration, external tools, LLM settings, validation pipeline, metrics, candidate selection, and report generation work correctly.

## 1. Activate the Python Environment

From the root of the TestHumanizer repository:

```bash
source .venv/bin/activate
```
If the environment does not exist yet:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```
## 2. Check Java

TestHumanizer uses Java-based tools such as EvoSuite, JUnit, JaCoCo, PMD, and the Scalabrino readability model.

Check that Java is available:

```bash
java -version
javac -version
```
A working Java installation is required before running the pipeline.

## 3. Check External Tool Paths

The default example configuration is:

```text
configs/experiments/evosuite_simple_project.yaml
```
This configuration expects tools such as EvoSuite, JUnit/Hamcrest, JaCoCo, PMD, and the Scalabrino readability model to be available under the `tools/` directory.

Typical expected paths include:

```text
tools/evosuite-master-1.2.1-SNAPSHOT.jar
tools/JUNIT-HAMCREST/junit-4.13.2.jar
tools/JUNIT-HAMCREST/hamcrest-core-1.3.jar
tools/jacoco-0.8.8/lib/jacocoagent.jar
tools/jacoco-0.8.8/lib/jacococli.jar
tools/pmd-bin-7.0.0-rc4/
tools/Readability-model/rsm.jar
```
If your local paths are different, update the YAML configuration before running the pipeline.

## 4. Configure API Keys

If the configuration enables LLM refactoring and OpenAI embeddings, export the required API keys.

Example:

```bash
export OPENAI_API_KEY_1="your-openai-api-key"
export MISTRAL_API_KEY_2="your-mistral-api-key"
```
The exact environment variable names are defined in the YAML configuration.

## 5. Run the Example Project

The fastest way to test the full pipeline is:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast
```
The `fast` preset runs all supported prompt scenarios with one refactoring iteration, unless explicitly overridden from the CLI. The CLI also supports `ready` and `full` presets, as well as overrides for models, scenarios, iterations, output directory, and logging options.

## 6. Expected Terminal Output

A successful run should end with:

```text
✓ Pipeline completed successfully. Reports are available in 07_reports.
```
During the run, TestHumanizer executes the following phases:

```text
Phase 1    Load and index target classes
Phase 2    Generate EvoSuite test suites
Phase 3    Validate original EvoSuite suites
Phase 4    Prepare LLM refactoring inputs
Phase 4.5  Generate and evaluate source-code summaries
Phase 5A   Prepare refactoring prompts
Phase 5B   Run LLM refactoring
Phase 6    Extract Java and reconstruct refactored suites
Phase 7    Validate refactored test suites
Phase 8    Compute CTSES metrics
Phase 9    Compute embedding cosine similarity
Phase 10   Compute Scalabrino readability
Phase 11   Compute CCTR cognitive complexity
Phase 12   Compute PMD complexity and maintainability
Phase 12.5 Select best refactored candidates
Phase 13   Generate synthetic report and Plotly dashboard
```
These phases are orchestrated by the main pipeline in `testhumanizer/core/pipeline.py`.

## 7. Main Output Directory

By default, the example run writes outputs to:

```text
outputs/evosuite_simple_project/
```
The output directory contains all intermediate artifacts, validation results, metrics, selected candidates, and final reports.

## 8. Important Output Files

After a successful run, the most useful files are:

```text
outputs/evosuite_simple_project/01_targets/targets_resolved.csv
outputs/evosuite_simple_project/02_evosuite/original_suites_metadata.csv
outputs/evosuite_simple_project/03_summaries/source_summaries_metadata.csv
outputs/evosuite_simple_project/04_refactorings/prompts/refactoring_prompts_metadata.csv
outputs/evosuite_simple_project/04_refactorings/llm_outputs/raw_refactoring_outputs.jsonl
outputs/evosuite_simple_project/04_refactorings/extracted_suites/extracted_refactored_suites_metadata.csv
outputs/evosuite_simple_project/05_validation/
outputs/evosuite_simple_project/06_metrics/
outputs/evosuite_simple_project/06_metrics/selection/selected_candidates.csv
outputs/evosuite_simple_project/07_reports/synthetic_report.html
outputs/evosuite_simple_project/07_reports/synthetic_report.md
outputs/evosuite_simple_project/07_reports/report_summary.json
```
## 9. Open the Final Report

The main report is:

```text
outputs/evosuite_simple_project/07_reports/synthetic_report.html
```
Open it in a browser:

```bash
xdg-open outputs/evosuite_simple_project/07_reports/synthetic_report.html
```
On macOS:

```bash
open outputs/evosuite_simple_project/07_reports/synthetic_report.html
```
## 10. Run Only One Model

To run only GPT-4o:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast \
  --models gpt4o
```
To run GPT-4o and Mistral:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast \
  --models gpt4o,mistral
```
## 11. Run Only One Scenario

To run only the tests-only scenario:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast \
  --scenarios tests-only
```
To run all scenarios explicitly:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --scenarios all
```
Supported scenarios are:

```text
tests-only
code-centric
summary-based
```
## 12. Run a Full Experiment

For a more complete run with three iterations:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset full
```
The `full` preset runs all scenarios with three iterations unless explicitly overridden.

## 13. Reuse Existing LLM Outputs

If raw LLM outputs already exist and you want to avoid calling the LLM again:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast \
  --no-llm
```
This is useful for debugging extraction, validation, metrics, selection, and reporting without spending additional API calls.

## 14. Disable Coverage

To skip JaCoCo coverage computation:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast \
  --no-coverage
```
This can be useful for faster debugging.

## 15. Inspect the Loaded Configuration

To check whether a YAML configuration loads correctly:

```bash
testhumanizer inspect-config \
  --config configs/experiments/evosuite_simple_project.yaml
```
This prints the parsed configuration to the terminal.

## 16. Logging Modes

### Default mode

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast
```
### Quiet mode

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast \
  --quiet
```
### Verbose mode

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast \
  --verbose
```
### Show per-item details

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast \
  --show-details
```
### Show detailed metric logs

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast \
  --show-metrics
```
## 17. Fresh Run

To test the pipeline from scratch, remove the existing output directory:

```bash
rm -rf outputs/evosuite_simple_project
```
Then run:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast
```
## 18. Cached Run

After a successful run, run the same command again:

```bash
testhumanizer run \
  --config configs/experiments/evosuite_simple_project.yaml \
  --preset fast
```
This helps verify that TestHumanizer can reuse existing generated artifacts, summaries, LLM outputs, and cached embeddings where applicable.

## 19. Common Quickstart Issues

### `testhumanizer: command not found`

Make sure the environment is activated and the package was installed:

```bash
source .venv/bin/activate
pip install -e .
```
### EvoSuite fails

Check:

```text
tools/evosuite-master-1.2.1-SNAPSHOT.jar
```
Also verify the target classpath in the YAML and target CSV.

### Java compilation fails

Check the JUnit, Hamcrest, and EvoSuite runtime jars.

### CodeBLEU fails

Check the CodeBLEU Python environment configured in the YAML.

### OpenAI calls fail

Check the API key environment variable and model name.

### PMD fails

Check the PMD directory and executable path in the YAML.

### Readability fails

Check the Scalabrino readability model path and Java availability.

## 20. Next Steps

After the quickstart works, read:

```text
docs/CONFIGURATION.md
docs/CUSTOM_PROJECTS.md
docs/ARCHITECTURE.md
docs/METRICS.md
docs/EXTENDING.md
docs/TROUBLESHOOTING.md
```
These documents explain how to configure, customize, extend, and debug TestHumanizer.
