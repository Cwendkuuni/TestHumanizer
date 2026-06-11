# Running TestHumanizer on Custom Java Projects

This guide explains how to use TestHumanizer with your own Java classes instead of the included example project.

A custom project run requires:

1.  A Java project or Java source files.
2.  Compiled `.class` files for the classes under test.
3.  A target CSV file describing the classes to process.
4.  A YAML experiment configuration.
5.  Correct classpaths for EvoSuite, compilation, JUnit, and metrics.

## 1. Overview

TestHumanizer expects each target class to be described explicitly.

For each class, the pipeline needs to know:

- where the Java source file is located
- how to resolve the compiled class
- what classpath is required
- where generated and refactored tests should be compiled
- where source files are located for coverage and reporting

The custom project workflow is:

1. Prepare or compile the Java project
2. Create a target CSV file
3. Create a YAML experiment config
4. Run TestHumanizer
5. Inspect validation, metrics, selected candidates, and reports
## 2. Recommended Java Project Structure

A standard Maven-like or Gradle-like structure is recommended:

```text
my-java-project/
├── src/
│   ├── main/
│   │   └── java/
│   │       └── com/example/MyClass.java
│   └── test/
│       └── java/
├── target/
│   └── classes/
└── pom.xml
```
or:

```text
my-java-project/
├── src/
│   ├── main/
│   │   └── java/
│   └── test/
│       └── java/
├── build/
│   └── classes/
│       └── java/
│           └── main/
└── build.gradle
```
TestHumanizer does not require Maven or Gradle directly, but the Java classes must be compilable and resolvable through the configured classpath.

## 3. Compile the Java Project First

Before using TestHumanizer, compile your Java project manually.

For Maven:

```bash
cd my-java-project
mvn test-compile
```
For Gradle:

```bash
cd my-java-project
gradle testClasses
```
For a simple Java project:

```bash
javac -d target/classes src/main/java/com/example/MyClass.java
```
After compilation, verify that the `.class` file exists.

Example:

```text
my-java-project/target/classes/com/example/MyClass.class
```
or:

```text
my-java-project/build/classes/java/main/com/example/MyClass.class
```
## 4. Create a Target CSV File

The target CSV tells TestHumanizer which classes to process.

Example:

```text
dataset,project,class_name,bug_id,source_path,classpath,test_class_fqdn,class_files_dir,source_files_dir
custom,my-java-project,MyClass,,examples/my-java-project/src/main/java/com/example/MyClass.java,examples/my-java-project/target/classes,com.example.MyClass,examples/my-java-project/target/classes,examples/my-java-project/src/main/java
```
Save it as, for example:

```text
configs/experiments/targets_my_project.csv
```
## 5. Target CSV Fields

### `dataset`

Logical dataset name.

For a custom project, use:

```text
custom
```
Example:

```text
custom
```
### `project`

Project name.

Example:

```text
my-java-project
```
This value is used in output metadata and file naming.

### `class_name`

Simple class name without package.

Example:

```text
MyClass
```
### `bug_id`

Optional bug identifier.

For non-bug-dataset projects, leave it empty.

Example:

If you are using a bug benchmark, you can set:

```text
1
```
or:

```text
Lang-1
```
depending on your naming convention.

### `source_path`

Path to the Java source file.

Example:

```text
examples/my-java-project/src/main/java/com/example/MyClass.java
```
This file is used for source-code context, summarization, and metadata.

### `classpath`

Classpath required to resolve the target class and its dependencies.

For a simple project:

```text
examples/my-java-project/target/classes
```
For a project with dependencies, include all required jars and class directories.

Linux/macOS example:

```text
examples/my-java-project/target/classes:libs/dependency-a.jar:libs/dependency-b.jar
```
Java classpaths on Linux/macOS use `:` as separator.

On Windows, use `;` as separator.

### `test_class_fqdn`

Fully qualified name of the class under test.

Example:

```text
com.example.MyClass
```
This is important for EvoSuite, because EvoSuite usually expects the fully qualified class name.

### `class_files_dir`

Directory containing compiled `.class` files.

Maven example:

```text
examples/my-java-project/target/classes
```
Gradle example:

```text
examples/my-java-project/build/classes/java/main
```
### `source_files_dir`

Root directory of the Java source files.

Example:

```text
examples/my-java-project/src/main/java
```
This is useful for coverage and source-level reporting.

## 6. Multiple Target Classes

You can process multiple classes by adding multiple rows.

Example:

```text
dataset,project,class_name,bug_id,source_path,classpath,test_class_fqdn,class_files_dir,source_files_dir
custom,my-java-project,Calculator,,examples/my-java-project/src/main/java/com/example/Calculator.java,examples/my-java-project/target/classes,com.example.Calculator,examples/my-java-project/target/classes,examples/my-java-project/src/main/java
custom,my-java-project,StringNormalizer,,examples/my-java-project/src/main/java/com/example/StringNormalizer.java,examples/my-java-project/target/classes,com.example.StringNormalizer,examples/my-java-project/target/classes,examples/my-java-project/src/main/java
```
Each row is processed independently by the pipeline.

## 7. Create a YAML Configuration File

Create a new YAML configuration:

```text
configs/experiments/my_project.yaml
```
Minimal example:

```yaml
experiment:
  name: my_project
  output_dir: outputs/my_project

dataset:
  targets_file: configs/experiments/targets_my_project.csv

logging:
  level: normal
  show_phase_headers: true
  show_per_item_details: false
  show_metric_details: false
  show_warnings: true

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

preparation:
  refactoring_inputs: true
  refactoring_prompts: true

llm_execution:
  refactoring_outputs: true

extraction:
  refactored_suites: true

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

summarization:
  enabled: true
  inject_into_summary_based: true

metrics:
  ctses:
    enabled: true

  embeddings:
    enabled: true

  readability:
    enabled: true
    scalabrino: true
    rsm_dir: tools/Readability-model
    rsm_jar: rsm.jar
    java_cmd: java
    timeout_seconds: 60

  complexity:
    enabled: true

    cctr:
      enabled: true

    pmd:
      enabled: true
      pmd_dir: tools/pmd-bin-7.0.0-rc4
      timeout_seconds: 60

selection:
  enabled: true
  policy: first_passing_then_best

reports:
  synthetic:
    enabled: true
    output_dir: 07_reports
    export_html: true
    export_png: true
    png_scale: 3
```
Adjust tool paths and model settings according to your environment.

## 8. Configure LLM Models

Add model aliases to the YAML configuration.

Example:

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
Then export the corresponding keys:

```bash
export OPENAI_API_KEY_1="your-openai-key"
export MISTRAL_API_KEY_2="your-mistral-key"
```
You can select models from the CLI:

```bash
testhumanizer run \
  --config configs/experiments/my_project.yaml \
  --models gpt4o
```
or:

```bash
testhumanizer run \
  --config configs/experiments/my_project.yaml \
  --models gpt4o,mistral
```
## 9. Configure Scenarios

The main supported scenarios are:

```text
tests-only
code-centric
summary-based
```
You can configure them in YAML if your configuration supports scenario lists, or override them from the CLI.

Run all scenarios:

```bash
testhumanizer run \
  --config configs/experiments/my_project.yaml \
  --scenarios all
```
Run only one scenario:

```bash
testhumanizer run \
  --config configs/experiments/my_project.yaml \
  --scenarios tests-only
```
Run two scenarios:

```bash
testhumanizer run \
  --config configs/experiments/my_project.yaml \
  --scenarios code-centric,summary-based
```
## 10. Run the Custom Project

Once the target CSV and YAML configuration are ready, run:

```bash
testhumanizer run \
  --config configs/experiments/my_project.yaml \
  --preset fast
```
Expected final output:

```text
✓ Pipeline completed successfully. Reports are available in 07_reports.
```
Outputs will be written under:

```text
outputs/my_project/
```
## 11. Run a Full Experiment

For a more complete experiment:

```bash
testhumanizer run \
  --config configs/experiments/my_project.yaml \
  --preset full
```
The `full` preset runs all scenarios with three iterations unless explicitly overridden.

## 12. Debug a Custom Project

For more terminal details:

```bash
testhumanizer run \
  --config configs/experiments/my_project.yaml \
  --preset fast \
  --verbose
```
To inspect detailed metric values:

```bash
testhumanizer run \
  --config configs/experiments/my_project.yaml \
  --preset fast \
  --show-metrics
```
To avoid new LLM calls while debugging later phases:

```bash
testhumanizer run \
  --config configs/experiments/my_project.yaml \
  --preset fast \
  --no-llm
```
To skip coverage:

```bash
testhumanizer run \
  --config configs/experiments/my_project.yaml \
  --preset fast \
  --no-coverage
```
## 13. Verify Target Loading

After Phase 1, TestHumanizer writes:

```text
outputs/my_project/01_targets/targets_resolved.csv
outputs/my_project/01_targets/targets_resolved.jsonl
```
Open `targets_resolved.csv` and verify that:

- the class names are correct
- source paths are correct
- classpaths are correct
- class file directories are correct
- source file directories are correct

If Phase 1 fails, the problem is usually in the target CSV.

## 14. Verify EvoSuite Generation

After Phase 2, check:

```text
outputs/my_project/02_evosuite/
```
Important files:

```text
outputs/my_project/02_evosuite/original_suites_metadata.csv
outputs/my_project/02_evosuite/original_suites_metadata.jsonl
outputs/my_project/02_evosuite/generated/
```
If EvoSuite fails, check:

- `test_generation.evosuite_jar`
- target `test_class_fqdn`
- target `classpath`
- compiled `.class` files
- Java version
- project dependencies

## 15. Verify Original Validation

After Phase 3, check:

```text
outputs/my_project/05_validation/
```
Look for original compilation, JUnit, and coverage outputs.

If original tests do not compile:

- verify JUnit and Hamcrest jars
- verify EvoSuite runtime dependencies
- verify the generated test imports
- verify the classpath
- verify the Java version

If JUnit fails:

- check runtime classpath
- check generated test assumptions
- check EvoSuite scaffolding
- inspect the JUnit output logs

## 16. Verify Refactoring Inputs

After Phase 4, check:

```text
outputs/my_project/04_refactorings/prepared_inputs.jsonl
```
This file contains structured data extracted from generated EvoSuite suites.

If it is missing, check:

- `preparation.refactoring_inputs`
- `original_suites_metadata.csv`
- generated test file paths

## 17. Verify Summaries

After Phase 4.5, check:

```text
outputs/my_project/03_summaries/source_summaries.jsonl
outputs/my_project/03_summaries/source_summaries_metadata.csv
outputs/my_project/03_summaries/summary_attempts.jsonl
```
If summary-based prompting is enabled, make sure summaries are generated and selected.

Useful fields may include:

```text
selected
llm_side_score
llm_side_faithfulness
llm_side_coverage
llm_side_hallucination_risk
```
## 18. Verify Prompts

After Phase 5A, check:

```text
outputs/my_project/04_refactorings/prompts/refactoring_prompts.jsonl
outputs/my_project/04_refactorings/prompts/refactoring_prompts_metadata.csv
```
The metadata file should show:

- class name
- test suite ID
- scenario ID
- model alias
- prompt size
- whether a summary was used
- summary source for summary-based prompts

## 19. Verify LLM Outputs

After Phase 5B, check:

```text
outputs/my_project/04_refactorings/llm_outputs/raw_refactoring_outputs.jsonl
```
If the file is missing or contains failures:

- check API keys
- check model names
- check timeout settings
- check max retry settings
- check provider configuration

## 20. Verify Extracted Refactored Suites

After Phase 6, check:

```text
outputs/my_project/04_refactorings/extracted_suites/
```
Important files:

```text
extracted_refactored_suites.jsonl
extracted_refactored_suites_metadata.csv
```
The metadata should contain extraction statuses such as:

```text
ok
ok_no_fence
ok_without_java_markers
failed
```
Only successfully extracted suites are validated and evaluated by later phases.

## 21. Verify Refactored Validation

After Phase 7, check:

```text
outputs/my_project/05_validation/
```
The refactored validation outputs should indicate:

- whether each refactored suite compiles
- whether each suite passes JUnit
- whether coverage was computed successfully

If refactored suites fail compilation:

- inspect the extracted Java files
- check imports
- check missing dependencies
- check invalid LLM output
- check renamed test classes
- check package declarations

## 22. Verify Metrics

Metrics are written under:

```text
outputs/my_project/06_metrics/
```
Important files include:

```text
06_metrics/ctses/ctses_results.csv
06_metrics/embeddings/embedding_similarity_results.csv
06_metrics/readability/readability_results.csv
06_metrics/complexity/cctr/cctr_results.csv
06_metrics/complexity/pmd/pmd_complexity_results.csv
06_metrics/selection/selected_candidates.csv
```
If a metric fails, first check whether the corresponding input files exist and whether previous phases completed successfully.

## 23. Verify Candidate Selection

After Phase 12.5, check:

```text
outputs/my_project/06_metrics/selection/selected_candidates.csv
```
Useful fields include:

```text
passes_all_thresholds
selection_reason
selection_cosine_score
selection_ctses_score
selected_refactored_test_file
```
If no candidate is selected:

- check compilation and JUnit validation
- check cosine similarity threshold
- check CTSES threshold
- check whether metric files exist
- lower thresholds temporarily for debugging

## 24. Verify Reports

After Phase 13, check:

```text
outputs/my_project/07_reports/
```
Important files:

```text
synthetic_report.md
synthetic_report.html
report_summary.json
figures/
```
Open the HTML report:

```bash
xdg-open outputs/my_project/07_reports/synthetic_report.html
```
On macOS:

```bash
open outputs/my_project/07_reports/synthetic_report.html
```
## 25. Common Custom Project Problems

### Problem: EvoSuite cannot find the class

Check:

```java
test_class_fqdn
classpath
class_files_dir
compiled .class files
package declaration
```
The fully qualified class name must match the Java package declaration.

### Problem: Compilation fails after EvoSuite generation

Check:

```text
JUnit jar
Hamcrest jar
EvoSuite runtime jar
classpath
Java version
generated imports
```
### Problem: Refactored tests fail compilation

Possible causes:

```text
LLM removed required imports
LLM changed class name incorrectly
LLM changed package declaration incorrectly
LLM removed scaffolding dependencies
LLM generated partial code
LLM introduced syntax errors
```
Inspect the extracted Java file under:

```text
outputs/my_project/04_refactorings/extracted_suites/
```
### Problem: JUnit fails

Possible causes:

```text
LLM changed assertions
LLM modified test logic
LLM changed object initialization
LLM removed expected exceptions
LLM changed test data
```
Check the JUnit validation logs.

### Problem: Coverage fails

Check:

```text
jacoco_agent_jar
jacoco_cli_jar
class_files_dir
source_files_dir
runtime classpath
```
You can disable coverage temporarily:

```bash
testhumanizer run \
  --config configs/experiments/my_project.yaml \
  --no-coverage
```
### Problem: Summary-based scenario has no summary

Check:

```text
summarization.enabled
summarization.inject_into_summary_based
03_summaries/source_summaries.jsonl
03_summaries/source_summaries_metadata.csv
```
Then inspect the prompt metadata:

```text
04_refactorings/prompts/refactoring_prompts_metadata.csv
```
### Problem: OpenAI embeddings fail

Check:

```text
OPENAI_API_KEY_1
metrics.embeddings.openai.enabled
metrics.embeddings.openai.model_name
network access
cache directory permissions
```
### Problem: PMD fails

Check:

```text
metrics.complexity.pmd.pmd_dir
PMD executable
ruleset
Java file paths
timeout_seconds
```
### Problem: Readability fails

Check:

```text
metrics.readability.rsm_dir
metrics.readability.rsm_jar
java command
timeout_seconds
```
## 26. Recommended Custom Project Workflow

For a new project, use this sequence:

1. Compile the Java project manually.
2. Create the target CSV.
3. Create the YAML config.
4. Run inspect-config.
5. Run with --preset fast --models gpt4o --scenarios tests-only.
6. Verify EvoSuite generation and original validation.
7. Enable all scenarios.
8. Enable all models.
9. Enable full metrics.
10. Run --preset full.
11. Inspect selected candidates and synthetic report.
Suggested first run:

```bash
testhumanizer inspect-config \
  --config configs/experiments/my_project.yaml
```
Then:

```bash
testhumanizer run \
  --config configs/experiments/my_project.yaml \
  --preset fast \
  --models gpt4o \
  --scenarios tests-only
```
Then:

```bash
testhumanizer run \
  --config configs/experiments/my_project.yaml \
  --preset fast
```
Finally:

```bash
testhumanizer run \
  --config configs/experiments/my_project.yaml \
  --preset full
```
## 27. Reproducibility Tips

For reproducible experiments:

- keep the YAML configuration under version control
- keep the target CSV under version control
- store the exact EvoSuite version
- store Java version information
- store model aliases and model names
- store prompt templates if customized
- copy or archive the output `config.yaml`
- avoid changing output files manually
- use separate output directories for separate experiments

Recommended naming:

```text
outputs/<project>_<date>_<setting>/
```
Example:

```text
outputs/my_project_2026_06_10_full/
```
## 28. Minimal Checklist

Before running TestHumanizer on a custom project:

- [ ] The Java project compiles manually
- [ ] The target class has a correct package declaration
- [ ] The compiled .class file exists
- [ ] source_path points to the correct .java file
- [ ] test_class_fqdn matches the package and class name
- [ ] classpath includes classes and dependencies
- [ ] class_files_dir points to compiled classes
- [ ] source_files_dir points to Java sources
- [ ] EvoSuite jar exists
- [ ] JUnit and Hamcrest jars exist
- [ ] JaCoCo jars exist if coverage is enabled
- [ ] PMD exists if PMD is enabled
- [ ] Readability model exists if readability is enabled
- [ ] CodeBLEU environment exists if CTSES CodeBLEU is enabled
- [ ] API keys are exported if LLM calls or OpenAI embeddings are enabled
- [ ] output_dir is writable
## 29. Next Steps

After your custom project runs successfully, inspect:

```text
outputs/my_project/07_reports/synthetic_report.html
outputs/my_project/06_metrics/selection/selected_candidates.csv
```
For deeper customization, read:

```text
docs/ARCHITECTURE.md
docs/PIPELINE_PHASES.md
docs/METRICS.md
docs/EXTENDING.md
docs/TROUBLESHOOTING.md
```
