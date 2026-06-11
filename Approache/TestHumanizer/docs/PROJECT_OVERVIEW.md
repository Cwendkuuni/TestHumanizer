# TestHumanizer: Humanizing Automatically Generated Unit Test Suites

This repository contains the research artifacts, datasets, prompts, generated tests, refactored test suites, experimental results, and tool implementation associated with the TestHumanizer project.

TestHumanizer investigates how Large Language Models (LLMs) can refactor automatically generated Java unit tests into more readable, maintainable, and human-aligned test suites while preserving behavioral intent and test validity.

The repository is organized as a complete artifact package for:

- reproducing the TestHumanizer pipeline;
- inspecting the datasets and prompts used in the study;
- analyzing generated and refactored test suites;
- accessing the experimental results for the research questions;
- preparing the public GitHub and Zenodo releases.

## 1. Project Overview

Automatically generated unit tests, such as those produced by EvoSuite, are useful for improving coverage and detecting faults, but they are often difficult for developers to read, understand, maintain, and adopt.

TestHumanizer addresses this problem by combining:

1.  automated test generation with EvoSuite;
2.  LLM-based refactoring of generated test suites;
3.  source-code summarization;
4.  semantic and lexical similarity analysis;
5.  readability, complexity, maintainability, and coverage metrics;
6.  candidate selection based on validity and quality constraints;
7.  human evaluation of refactored test suites.

The project evaluates whether LLMs can transform generated tests into more human-readable test suites without destroying their behavioral relationship to the original generated tests.

## 2. Repository Layout

At the root level, the repository contains the following main components:

```text
Approache/
Datasets/
Dependancies/
Generated_tests_EvoSuite/
Prompts/
Refactored_data/
Results/
SIDE_Model/
Summary_generated/
reorganize_old_rq1_refactoring_artifacts.sh
```
## 3. Main Tool Implementation

The main TestHumanizer tool is located in:

```text
Approache/TestHumanizer/
```
This directory contains the autonomous Python package and command-line pipeline used to run the current version of TestHumanizer.

```text
Approache/TestHumanizer/
├── configs/
├── docs/
├── examples/
├── outputs/
├── scripts/
├── testhumanizer/
├── tests/
├── tools/
├── pyproject.toml
└── activate
```
The tool supports:

- loading target classes from Defects4J and SF110;
- generating test suites with EvoSuite;
- validating original generated tests;
- preparing LLM refactoring inputs and prompts;
- running LLM-based test refactoring;
- extracting and reconstructing refactored suites;
- validating refactored suites;
- computing CTSES, embedding similarity, readability, cognitive complexity, and PMD metrics;
- selecting the best candidates;
- generating reports and Plotly dashboards.

For tool-specific usage, see:

```text
Approache/TestHumanizer/README.md
Approache/TestHumanizer/docs/
```
## 4. Datasets

The `Datasets/` directory contains the extracted metadata used to drive the experiments:

```text
Datasets/
├── combined_base_extracted.json
├── Defects4J_base_extracted.json
└── SF110_base_extracted.json
```
These files describe the target classes used in the study, including dataset name, project name, bug identifier when available, class name, package name, source code, and source-level statistics.

The current reproducibility runner can use these files to generate TestHumanizer-compatible target CSV files.

Example runner entry point:

```text
Approache/TestHumanizer/scripts/run_dataset_experiment.py
```
## 5. Dependencies and Compiled Sources

The `Dependancies/` directory contains dependency archives required to reproduce large-scale experiments:

```text
Dependancies/
├── DEFECTS4J.zip
├── JARS.zip
└── SF-110.zip
```
These archives are intended for Zenodo distribution because they are large and include external dependencies or compiled source layouts required for running EvoSuite and validating generated tests.

They include:

- compiled Defects4J source layouts;
- compiled SF110 source layouts;
- Java dependency jars used by the experimental pipeline.

The GitHub repository should preferably keep only lightweight code and metadata, while large dependency archives should be stored on Zenodo.

## 6. EvoSuite-Generated Test Suites

The `Generated_tests_EvoSuite/` directory contains enriched metadata related to EvoSuite-generated test suites:

```text
Generated_tests_EvoSuite/
├── Defects4J_complet_enriched.json
└── SF110_complet_enriched.json
```
These files include generated test information and additional metadata used during later phases of the refactoring pipeline, including source summaries and refactoring preparation data.

## 7. Prompts

The `Prompts/` directory contains the raw prompts used across the different LLM-based phases:

```text
Prompts/
├── code_centric.txt
├── raw_generation.txt
├── source_code_summarization.txt
├── summary_based.txt
└── tests_only.txt
```
These prompts correspond to the main prompting strategies explored in the study, including:

- tests-only refactoring;
- code-centric refactoring;
- summary-based refactoring;
- source-code summarization;
- raw generation baselines.

## 8. Refactored Test Suites

The `Refactored_data/` directory contains raw and compilable LLM-generated refactorings:

```text
Refactored_data/
├── Compilable_refactorings/
└── Raw_refactorings/
```
The raw refactorings include direct LLM outputs before compilation filtering. The compilable refactorings include refactored test suites that passed the compilation stage.

Example files include:

```text
gpt4o_raw_refactored_tests.jsonl
gpt4o_raw_refactored_tests_metadata.csv
mistral_raw_refactored_tests.jsonl
mistral_raw_refactored_tests_metadata.csv
gpt4o_compilable_refactored_tests.jsonl
gpt4o_compilable_refactored_tests_metadata.csv
mistral_compilable_refactored_tests.jsonl
mistral_compilable_refactored_tests_metadata.csv
```
Because these files are large, they are intended for Zenodo distribution.

## 9. Experimental Results

The `Results/` directory contains the results organized by research question:

```text
Results/
├── RQ1/
├── RQ2/
├── RQ3/
├── RQ4/
├── RQ5/
└── RQ6/
```
### RQ1: Refactoring Success and Compilation

`Results/RQ1/` contains compilation statistics, error categories, completeness checks, and code summary SIDE metrics for GPT-4o and Mistral.

### RQ2: Readability, Complexity, and Maintainability

`Results/RQ2/` contains readability, cognitive complexity, cyclomatic complexity, and maintainability analyses for:

- EvoSuite-generated tests;
- raw LLM-generated tests;
- refactored tests.

### RQ3: Semantic and Lexical Similarity

`Results/RQ3/` contains similarity metrics between original and refactored tests using:

- CodeBERT;
- GraphCodeBERT;
- OpenAI embeddings;
- CTSES-related metrics;
- aggregated similarity statistics.

### RQ4: Coverage Preservation

`Results/RQ4/` contains line, instruction, and method coverage statistics and figures for Defects4J and SF110.

### RQ5: Test Smell Analysis

`Results/RQ5/` contains prevalence, total count, and unique count statistics for test smells across scenarios.

### RQ6: Human Evaluation

`Results/RQ6/` contains the human evaluation artifacts, including:

- selected evaluation tasks;
- anonymized survey answers;
- final annotation scores;
- inter-annotator agreement results;
- role-based summaries;
- Wilcoxon tests;
- boxplots for readability, trust, and adoption.

## 10. SIDE Model

The `SIDE_Model/` directory contains the SIDE model artifact used to evaluate source-code summaries:

```text
SIDE_Model/
├── hard-negatives-20260608T120328Z-3-001/
├── hard-negatives-20260608T120328Z-3-001.zip
└── README.md
```
The model is used in the source-code summarization phase to evaluate the quality and faithfulness of generated summaries.

Because the model files are large, this directory is intended for Zenodo distribution.

## 11. Generated Source Summaries

The `Summary_generated/` directory contains source-code summaries and mapping reports:

```text
Summary_generated/
├── code_summary_dataset_flat.json
├── code_summary_dataset_structured.json
└── code_summary_mapping_report.json
```
These files support the summary-based prompting strategy and the analysis of source-code summarization quality.

## 12. Reproducibility

The current autonomous reproducibility workflow is implemented in:

```text
Approache/TestHumanizer/scripts/run_dataset_experiment.py
```
A typical Defects4J sample run is:

```bash
cd Approache/TestHumanizer

python scripts/run_dataset_experiment.py \
  --dataset defects4j \
  --metadata ../../Datasets/Defects4J_base_extracted.json \
  --base-config configs/templates/base_dataset_experiment.yaml \
  --output-root outputs/reproducibility \
  --sample-size 2 \
  --sample-seed 42 \
  --models gpt4o \
  --scenarios tests-only \
  --iterations 1 \
  --preset fast
```
A typical SF110 sample run is:

```bash
cd Approache/TestHumanizer

python scripts/run_dataset_experiment.py \
  --dataset sf110 \
  --metadata ../../Datasets/SF110_base_extracted.json \
  --base-config configs/templates/base_dataset_experiment.yaml \
  --output-root outputs/reproducibility \
  --sample-size 2 \
  --sample-seed 42 \
  --models gpt4o \
  --scenarios tests-only \
  --iterations 1 \
  --preset fast
```
For detailed reproducibility instructions, see:

```text
Approache/TestHumanizer/docs/REPRODUCIBILITY.md
```
## 13. Zenodo Package

Large artifacts should be distributed through Zenodo rather than committed directly to GitHub.

Recommended Zenodo contents:

```text
Dependancies/
Refactored_data/
SIDE_Model/
Summary_generated/
Generated_tests_EvoSuite/
Results/
Datasets/
```
The GitHub repository should include the code, documentation, lightweight metadata, and scripts needed to connect the repository to the Zenodo artifact.

A dedicated Zenodo documentation file should describe:

- archive contents;
- file sizes;
- expected extraction paths;
- how to link Zenodo artifacts with the GitHub repository;
- how to reproduce sample and full experiments.

## 14. Recommended GitHub Release Structure

For the first public release, the repository should ideally contain:

```text
README.md
LICENSE
CITATION.cff
requirements or pyproject files
Approache/TestHumanizer/
Datasets/
Prompts/
Results/README.md
docs/
```
Large files should be referenced through Zenodo.

## 15. Citation

If you use this repository, please cite the associated paper.

A formal citation entry will be added after publication.

## 16. License

A license should be added before the first public release.

Recommended options depend on the intended reuse model:

- MIT or Apache-2.0 for permissive software reuse;
- CC BY 4.0 for datasets and documentation;
- a mixed software/data license if code and datasets have different reuse constraints.

## 17. Status

This repository is being prepared for the first public GitHub release and Zenodo artifact release.
