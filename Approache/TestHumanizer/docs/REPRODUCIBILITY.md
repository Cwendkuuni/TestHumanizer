# Reproducibility Guide

This document explains how to reproduce TestHumanizer experiments on the Defects4J and SF110 datasets from the extracted JSON metadata files.

The reproducibility workflow starts from structured metadata, prepares a target CSV compatible with TestHumanizer, generates a run-specific configuration file, launches EvoSuite, runs LLM-based refactoring, computes all metrics, selects the best candidates, and generates the final synthetic report.

## 1. Overview

The reproducibility workflow is handled by:

```text
scripts/run_dataset_experiment.py
```
The script performs the following steps:

1.  Loads the extracted dataset metadata.
2.  Deduplicates repeated target classes.
3.  Resolves `.java` and `.class` files on disk.
4.  Builds a TestHumanizer-compatible target CSV.
5.  Generates a run-specific YAML configuration.
6.  Optionally launches the full TestHumanizer pipeline.
7.  Saves diagnostics and run metadata for traceability.

The recommended base configuration for dataset experiments is:

```text
configs/templates/base_dataset_experiment.yaml
```
## 2. Expected dataset files

The runner expects one of the following metadata files:

```text
Datasets/Defects4J_base_extracted.json
Datasets/SF110_base_extracted.json
```
Each Defects4J entry should contain fields similar to:

```json
{
  "dataset": "Defects4J",
  "project_name": "Time",
  "bug-id": "1",
  "class": "UnsupportedDurationField",
  "fqdn": "org.joda.time.field",
  "source_code": "...",
  "source_token_count": 1386,
  "source_method_count": 24,
  "source_loc": 95
}
```
Each SF110 entry should contain fields similar to:

```json
{
  "dataset": "SF110",
  "project_name": "trove",
  "bug-id": null,
  "class": "TCharHash",
  "fqdn": "gnu.trove.impl.hash",
  "source_code": "...",
  "source_token_count": 1202,
  "source_method_count": 10,
  "source_loc": 115
}
```
The runner deduplicates targets using:

```text
dataset + project_name + bug-id + class + fqdn
```
This is important because the enriched metadata files may contain repeated entries for the same target class.

## 3. Expected source layout

### Defects4J

The default Defects4J source root is:

```text
/home/e113/Documents/Humanization-Project/HUMANIZATION/DEFECTS4J/SOURCES
```
The expected layout is:

```text
DEFECTS4J/SOURCES/<project>/<bug-id>/<package-path>/<ClassName>.java
DEFECTS4J/SOURCES/<project>/<bug-id>/<package-path>/<ClassName>.class
```
Example:

```text
DEFECTS4J/SOURCES/Cli/19/org/apache/commons/cli/PosixParser.java
DEFECTS4J/SOURCES/Cli/19/org/apache/commons/cli/PosixParser.class
```
### SF110

The default SF110 source root is:

```text
/home/e113/Documents/Humanization-Project/HUMANIZATION/SF-110/SOURCES
```
The expected layout is:

```text
SF-110/SOURCES/<project>/<package-path>/<ClassName>.java
SF-110/SOURCES/<project>/<package-path>/<ClassName>.class
```
Example:

```text
SF-110/SOURCES/33_javaviewcontrol/com/pmdesigns/jvc/tools/TokenMgrError.java
SF-110/SOURCES/33_javaviewcontrol/com/pmdesigns/jvc/tools/TokenMgrError.class
```
## 4. Important EvoSuite classpath note

By default, the dataset runner does **not** inject the global dependency directory into EvoSuite’s classpath.

This is intentional.

A large global dependency directory can contain unrelated jars compiled with newer Java versions. EvoSuite may scan these jars and fail with errors such as:

```text
Unsupported class file major version 63
```
or:

```text
Classpath element does not exist on disk
```
Therefore, the default classpath contains:

```text
target class directory + project-local jars
```
If a specific project requires additional dependencies, use:

```text
--extra-classpath "/path/to/a.jar:/path/to/classes"
```
or explicitly enable a dependency directory with:

```text
--global-dependencies-dir /path/to/dependencies
```
Use real paths only. Do not use wildcards such as:

```text
/path/to/dependencies/*
```
EvoSuite validates classpath entries literally and may reject wildcard entries.

## 5. Sample run: Defects4J

Use this command to run a small Defects4J sample with two targets:

```bash
rm -rf outputs/reproducibility/defects4j/sample_2_seed_42

python scripts/run_dataset_experiment.py \
  --dataset defects4j \
  --metadata /home/e113/Documents/Humanization-Project/HUMANIZATION/For_GitHub/TestHumanizer/Datasets/Defects4J_base_extracted.json \
  --base-config configs/templates/base_dataset_experiment.yaml \
  --output-root outputs/reproducibility \
  --sample-size 2 \
  --sample-seed 42 \
  --models gpt4o \
  --scenarios tests-only \
  --iterations 1 \
  --preset fast
```
The run directory will be:

```text
outputs/reproducibility/defects4j/sample_2_seed_42
```
## 6. Sample run: SF110

Use this command to run a small SF110 sample with two targets:

```bash
rm -rf outputs/reproducibility/sf110/sample_2_seed_42

python scripts/run_dataset_experiment.py \
  --dataset sf110 \
  --metadata /home/e113/Documents/Humanization-Project/HUMANIZATION/For_GitHub/TestHumanizer/Datasets/SF110_base_extracted.json \
  --base-config configs/templates/base_dataset_experiment.yaml \
  --output-root outputs/reproducibility \
  --sample-size 2 \
  --sample-seed 42 \
  --models gpt4o \
  --scenarios tests-only \
  --iterations 1 \
  --preset fast
```
The run directory will be:

```text
outputs/reproducibility/sf110/sample_2_seed_42
```
## 7. Dry run mode

To generate the dataset summary without writing files or launching TestHumanizer, use:

```bash
python scripts/run_dataset_experiment.py \
  --dataset defects4j \
  --metadata /home/e113/Documents/Humanization-Project/HUMANIZATION/For_GitHub/TestHumanizer/Datasets/Defects4J_base_extracted.json \
  --base-config configs/templates/base_dataset_experiment.yaml \
  --output-root outputs/reproducibility \
  --sample-size 2 \
  --sample-seed 42 \
  --dry-run
```
## 8. Generate files without launching TestHumanizer

To generate the target CSV, configuration, and diagnostics without launching the pipeline, use:

```bash
python scripts/run_dataset_experiment.py \
  --dataset defects4j \
  --metadata /home/e113/Documents/Humanization-Project/HUMANIZATION/For_GitHub/TestHumanizer/Datasets/Defects4J_base_extracted.json \
  --base-config configs/templates/base_dataset_experiment.yaml \
  --output-root outputs/reproducibility \
  --sample-size 2 \
  --sample-seed 42 \
  --models gpt4o \
  --scenarios tests-only \
  --iterations 1 \
  --preset fast \
  --no-run
```
This produces:

```text
generated_targets.csv
target_diagnostics.csv
selected_targets.json
all_valid_targets.json
skipped_missing_files.json
dataset_summary.json
generated_config.yaml
run_command.txt
```
## 9. Full Defects4J run

To run all valid Defects4J targets:

```bash
python scripts/run_dataset_experiment.py \
  --dataset defects4j \
  --metadata /home/e113/Documents/Humanization-Project/HUMANIZATION/For_GitHub/TestHumanizer/Datasets/Defects4J_base_extracted.json \
  --base-config configs/templates/base_dataset_experiment.yaml \
  --output-root outputs/reproducibility \
  --full \
  --models gpt4o \
  --scenarios tests-only \
  --iterations 1 \
  --preset fast
```
The run directory will be:

```text
outputs/reproducibility/defects4j/full
```
## 10. Full SF110 run

To run all valid SF110 targets:

```bash
python scripts/run_dataset_experiment.py \
  --dataset sf110 \
  --metadata /home/e113/Documents/Humanization-Project/HUMANIZATION/For_GitHub/TestHumanizer/Datasets/SF110_base_extracted.json \
  --base-config configs/templates/base_dataset_experiment.yaml \
  --output-root outputs/reproducibility \
  --full \
  --models gpt4o \
  --scenarios tests-only \
  --iterations 1 \
  --preset fast
```
The run directory will be:

```text
outputs/reproducibility/sf110/full
```
## 11. Paper-like run

For a more complete experiment with multiple scenarios and multiple LLM refactoring iterations:

```bash
python scripts/run_dataset_experiment.py \
  --dataset defects4j \
  --metadata /home/e113/Documents/Humanization-Project/HUMANIZATION/For_GitHub/TestHumanizer/Datasets/Defects4J_base_extracted.json \
  --base-config configs/templates/base_dataset_experiment.yaml \
  --output-root outputs/reproducibility \
  --full \
  --models gpt4o,mistral \
  --scenarios all \
  --iterations 3 \
  --preset full
```
For SF110:

```bash
python scripts/run_dataset_experiment.py \
  --dataset sf110 \
  --metadata /home/e113/Documents/Humanization-Project/HUMANIZATION/For_GitHub/TestHumanizer/Datasets/SF110_base_extracted.json \
  --base-config configs/templates/base_dataset_experiment.yaml \
  --output-root outputs/reproducibility \
  --full \
  --models gpt4o,mistral \
  --scenarios all \
  --iterations 3 \
  --preset full
```
## 12. Output structure

Each run creates a dedicated directory:

```text
outputs/reproducibility/<dataset>/<run-name>/
```
Example:

```text
outputs/reproducibility/defects4j/sample_2_seed_42/
```
The runner-level files are:

```text
generated_targets.csv
target_diagnostics.csv
selected_targets.json
all_valid_targets.json
skipped_missing_files.json
dataset_summary.json
generated_config.yaml
run_command.txt
```
The TestHumanizer pipeline output is stored in:

```text
testhumanizer_outputs/
```
Typical pipeline subdirectories include:

```text
01_targets/
02_evosuite/
03_inputs/
04_prompts/
05_validation/
06_metrics/
07_reports/
```
## 13. How to verify a successful run

### 13.1 Check EvoSuite generation

A successful EvoSuite run should contain real `ESTest.java` files:

```bash
find outputs/reproducibility/defects4j/sample_2_seed_42/testhumanizer_outputs/02_evosuite \
  -name "*.java" | head -20
```
Expected examples:

```text
PosixParser_ESTest.java
PosixParser_ESTest_scaffolding.java
Entities_ESTest.java
Entities_ESTest_scaffolding.java
```
The metadata should not contain placeholder files such as:

```text
NOT_FOUND_ESTest.java
```
Check with:

```text
head -n 5 outputs/reproducibility/defects4j/sample_2_seed_42/testhumanizer_outputs/02_evosuite/original_suites_metadata.csv
```
### 13.2 Check report summary

For Defects4J:

```bash
cat outputs/reproducibility/defects4j/sample_2_seed_42/testhumanizer_outputs/07_reports/report_summary.json
```
For SF110:

```bash
cat outputs/reproducibility/sf110/sample_2_seed_42/testhumanizer_outputs/07_reports/report_summary.json
```
A successful run should report non-zero values for:

```text
num_targets
num_prompt_rows
num_summary_rows
num_candidate_rows
num_selected_candidates
```
## 14. Reproducibility metadata

The runner stores all important run-level metadata in:

```text
dataset_summary.json
```
This file records:

```text
dataset
metadata_path
base_config_path
raw_rows
unique_targets
valid_targets
skipped_missing_files
selected_targets
sample_seed
sample_size
full
project_counts_selected
project_counts_valid
global_dependencies_dir
extra_classpath_entries
run_dir
targets_csv
generated_config
testhumanizer_output_dir
selected_preview
```
The exact TestHumanizer command is stored in:

```text
run_command.txt
```
This file can be used to rerun the experiment later.

## 15. Handling missing source or class files

The runner checks whether each target has both:

```text
<ClassName>.java
<ClassName>.class
```
Targets with missing files are skipped by default and saved in:

```text
skipped_missing_files.json
```
To fail immediately if any target is missing source or class files, use:

```text
--strict
```
Example:

```bash
python scripts/run_dataset_experiment.py \
  --dataset sf110 \
  --metadata /path/to/SF110_base_extracted.json \
  --base-config configs/templates/base_dataset_experiment.yaml \
  --output-root outputs/reproducibility \
  --sample-size 2 \
  --strict \
  --no-run
```
## 16. Custom source roots

If the datasets are stored in different locations, override the default source roots.

For Defects4J:

```text
--defects4j-sources-root /path/to/DEFECTS4J/SOURCES
```
For SF110:

```text
--sf110-sources-root /path/to/SF-110/SOURCES
```
Example:

```bash
python scripts/run_dataset_experiment.py \
  --dataset defects4j \
  --metadata /path/to/Defects4J_base_extracted.json \
  --base-config configs/templates/base_dataset_experiment.yaml \
  --defects4j-sources-root /path/to/DEFECTS4J/SOURCES \
  --output-root outputs/reproducibility \
  --sample-size 2 \
  --no-run
```
## 17. Extra classpath entries

For projects requiring additional dependencies, use:

```text
--extra-classpath "/path/to/dependency.jar:/path/to/classes"
```
Do not use wildcard entries.

Recommended:

```text
--extra-classpath "/path/to/lib/a.jar:/path/to/lib/b.jar"
```
Avoid:

```text
--extra-classpath "/path/to/lib/*"
```
If project-local jars are nested in subdirectories and should be collected recursively, use:

```text
--project-jars-recursive
```
## 18. Common issues

### EvoSuite generates `NOT_FOUND_ESTest.java`

This means EvoSuite did not produce a real test suite. Check:

```bash
cat outputs/reproducibility/<dataset>/<run-name>/testhumanizer_outputs/02_evosuite/generated/.../evosuite.log
```
Common causes include:

```text
invalid classpath
missing .class files
unsupported Java bytecode in dependency jars
EvoSuite cannot resolve target class
```
### EvoSuite fails with wildcard classpath

Avoid classpath entries such as:

```text
/path/to/dependencies/*
```
Use real jar paths instead.

### EvoSuite fails with unsupported class file version

Avoid injecting large global dependency directories by default. Some jars may be compiled with Java versions unsupported by EvoSuite’s bytecode analyzer.

Use only the dependencies needed by the target project.

### No prompts are generated

If Phase 5A prepares zero prompts, check whether original EvoSuite tests were generated and validated correctly.

Useful files:

```text
02_evosuite/original_suites_metadata.csv
05_validation/original_compilation_results.csv
05_validation/original_junit_results.csv
```
### No candidates are selected

Check:

```text
06_metrics/selection/
07_reports/report_summary.json
```
Possible causes:

```text
LLM output extraction failed
refactored tests did not compile
candidate failed JUnit
candidate did not pass similarity or CTSES thresholds
```
## 19. Recommended workflow

For development:

```bash
python scripts/run_dataset_experiment.py \
  --dataset defects4j \
  --metadata /path/to/Defects4J_base_extracted.json \
  --base-config configs/templates/base_dataset_experiment.yaml \
  --output-root outputs/reproducibility \
  --sample-size 2 \
  --sample-seed 42 \
  --models gpt4o \
  --scenarios tests-only \
  --iterations 1 \
  --preset fast
```
For validating both datasets:

```bash
python scripts/run_dataset_experiment.py \
  --dataset defects4j \
  --metadata /path/to/Defects4J_base_extracted.json \
  --base-config configs/templates/base_dataset_experiment.yaml \
  --output-root outputs/reproducibility \
  --sample-size 2 \
  --sample-seed 42 \
  --models gpt4o \
  --scenarios tests-only \
  --iterations 1 \
  --preset fast

python scripts/run_dataset_experiment.py \
  --dataset sf110 \
  --metadata /path/to/SF110_base_extracted.json \
  --base-config configs/templates/base_dataset_experiment.yaml \
  --output-root outputs/reproducibility \
  --sample-size 2 \
  --sample-seed 42 \
  --models gpt4o \
  --scenarios tests-only \
  --iterations 1 \
  --preset fast
```
For full paper-like experiments:

```bash
python scripts/run_dataset_experiment.py \
  --dataset defects4j \
  --metadata /path/to/Defects4J_base_extracted.json \
  --base-config configs/templates/base_dataset_experiment.yaml \
  --output-root outputs/reproducibility \
  --full \
  --models gpt4o,mistral \
  --scenarios all \
  --iterations 3 \
  --preset full
```
## 20. Current validated status

The reproducibility runner has been validated on sample runs for:

```text
Defects4J
SF110
```
Both sample runs successfully generated real EvoSuite test suites, produced refactoring prompts, executed LLM refactoring, computed metrics, selected candidates, and generated synthetic reports.
