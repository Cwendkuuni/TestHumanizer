# Metrics

This document describes the metrics computed by TestHumanizer.

The goal of these metrics is to evaluate whether LLM-refactored test suites preserve the intent of the original EvoSuite-generated tests while improving readability, maintainability, and human-oriented structure.

TestHumanizer computes several metric families:

```text
semantic and structural preservation
embedding-based similarity
readability
cognitive complexity
PMD complexity and maintainability
candidate selection scores
```
## 1. Metric Overview

| Metric family               | Purpose                                                    |
|-----------------------------|------------------------------------------------------------|
| CTSES                       | Composite similarity between original and refactored tests |
| CodeBLEU                    | Code-aware syntactic and structural similarity             |
| METEOR                      | Lexical similarity with synonym-aware matching             |
| ROUGE-L                     | Longest-common-subsequence structural overlap              |
| Embedding cosine similarity | Semantic similarity between original and refactored tests  |
| Scalabrino readability      | Human-oriented code readability                            |
| CCTR cognitive complexity   | Cognitive effort required to understand the test code      |
| PMD metrics                 | Complexity and maintainability indicators                  |
| Candidate selection         | Chooses the best valid refactored suite                    |

## 2. Metric Inputs

Most preservation metrics compare two artifacts:

```text
original EvoSuite-generated test suite
refactored LLM-generated test suite
```
The original test suite usually comes from:

```text
outputs/<experiment>/04_refactorings/prepared_inputs.jsonl
```
The refactored test suite usually comes from:

```text
outputs/<experiment>/04_refactorings/extracted_suites/extracted_refactored_suites.jsonl
```
File-based metrics, such as readability and complexity, operate on Java files referenced by metadata files:

```text
outputs/<experiment>/02_evosuite/original_suites_metadata.csv
outputs/<experiment>/04_refactorings/extracted_suites/extracted_refactored_suites_metadata.csv
```
## 3. CTSES

### Purpose

CTSES is a composite similarity score used to estimate whether a refactored test suite preserves the semantic and structural intent of the original EvoSuite-generated test suite.

CTSES combines:

```text
CodeBLEU
METEOR
ROUGE-L
```
The general formula is:

```text
CTSES = alpha * CodeBLEU + beta * METEOR + gamma * ROUGE-L
```
with:

```text
alpha + beta + gamma = 1
```
## 4. CTSES Variants

TestHumanizer reports three CTSES variants.

### CTSESAVG

Uniform baseline.

```text
CTSESAVG = 1/3 * CodeBLEU + 1/3 * METEOR + 1/3 * ROUGE-L
```
In the current output files, this variant may appear as:

```text
average_score_1
```
### CTSES_1

Semantic-prioritized profile.

```text
CTSES_1 = 0.5 * CodeBLEU + 0.3 * METEOR + 0.2 * ROUGE-L
```
In the current output files, this variant may appear as:

```text
CTSES_score_1
```
### CTSES_2

Readability-aware profile.

```text
CTSES_2 = 0.4 * CodeBLEU + 0.3 * METEOR + 0.3 * ROUGE-L
```
In the current output files, this variant may appear as:

```text
CTSES_score_2
```
## 5. CTSES Output Files

CTSES outputs are written under:

```text
outputs/<experiment>/06_metrics/ctses/
```
Typical files:

```text
ctses_results.csv
ctses_results.jsonl
```
Typical fields include:

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
CodeBLEU
METEOR
ROUGE-L
average_score_1
CTSES_score_1
CTSES_score_2
CodeBLEU_status
error
```
## 6. Interpreting CTSES

Higher CTSES values generally indicate stronger preservation between the original and refactored test suite.

A high CTSES score suggests that the refactoring preserved:

```text
code structure
lexical content
semantic intent
test behavior proxies
```
A low CTSES score may indicate that the refactored suite changed too much, lost important assertions, removed relevant test logic, or introduced a structurally different test.

CTSES should not be interpreted alone. It is best combined with:

```text
compilation status
JUnit status
embedding similarity
coverage
readability
complexity
```
## 7. CodeBLEU

### Purpose

CodeBLEU is a code-aware similarity metric.

It is useful because Java test suites are structured programs, not plain text.

CodeBLEU can capture information related to:

```text
token overlap
syntax structure
data-flow similarity
code-aware matching
```
### Interpretation

Higher values indicate stronger code-level similarity.

Low CodeBLEU may mean:

```text
major restructuring
changed control flow
removed or rewritten assertions
different object initialization
large lexical or syntactic divergence
```
### Notes

CodeBLEU is part of CTSES but can also be inspected independently.

## 8. METEOR

### Purpose

METEOR measures lexical similarity while allowing more flexible matching than simple exact overlap.

It is useful for identifying whether semantically related words or identifiers are preserved across refactoring.

### Interpretation

Higher METEOR means stronger lexical similarity.

Low METEOR may occur when:

```text
the LLM heavily renames identifiers
comments and helper names are rewritten
test data is changed
assertion messages are changed
```
## 9. ROUGE-L

### Purpose

ROUGE-L measures longest-common-subsequence similarity.

It is useful for estimating structural alignment between original and refactored test suites.

### Interpretation

Higher ROUGE-L means stronger sequence-level overlap.

Low ROUGE-L may occur when:

```text
test methods are reordered
helper methods are moved
large blocks are rewritten
original structure is heavily changed
```
## 10. Embedding Cosine Similarity

### Purpose

Embedding cosine similarity estimates semantic similarity between original and refactored test suites using vector representations.

TestHumanizer computes cosine similarity using:

```text
CodeBERT
GraphCodeBERT
OpenAI embeddings
```
### Output files

Embedding outputs are written under:

```text
outputs/<experiment>/06_metrics/embeddings/
```
Typical files:

```text
embedding_similarity_results.csv
embedding_similarity_results.jsonl
```
Typical fields include:

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
llm_model_alias
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
## 11. CodeBERT Similarity

### Purpose

CodeBERT provides code-oriented representations that can be used to compare original and refactored Java test suites.

### Interpretation

Higher cosine similarity indicates stronger semantic proximity in CodeBERT embedding space.

CodeBERT can be useful as a diagnostic metric, but it should not be the only decision criterion.

## 12. GraphCodeBERT Similarity

### Purpose

GraphCodeBERT is another code-oriented embedding model that can capture structural and data-flow-aware information.

### Interpretation

Higher cosine similarity indicates stronger semantic or structural proximity.

GraphCodeBERT is especially useful as a second diagnostic signal alongside CodeBERT and OpenAI embeddings.

## 13. OpenAI Embedding Similarity

### Purpose

OpenAI embeddings provide a strong semantic similarity signal between original and refactored test suites.

In the default candidate-selection setup, OpenAI cosine similarity is used as the primary embedding similarity metric.

### Interpretation

Higher values indicate stronger semantic preservation.

A high OpenAI cosine similarity suggests that the refactored suite remains close to the original test intent.

A low score may indicate that the LLM changed too much or lost relevant test behavior.

## 14. Embedding Similarity Thresholds

The default selection configuration uses a threshold such as:

```yaml
selection:
  cosine_similarity:
    enabled: true
    threshold: 0.80
    primary_embedding_model_alias: openai
```
This means candidates below the threshold may not be considered as fully passing semantic preservation constraints.

Thresholds should be adjusted carefully depending on the dataset, model, and research setting.

## 15. Scalabrino Readability

### Purpose

Scalabrino readability estimates the readability of Java code.

In TestHumanizer, it is computed for:

```text
original EvoSuite-generated test suites
refactored LLM-generated test suites
```
The goal is to evaluate whether LLM refactoring improves human-oriented readability.

### Output files

Readability outputs are written under:

```text
outputs/<experiment>/06_metrics/readability/
```
Typical files:

```text
readability_results.csv
readability_results.jsonl
readability_summary.csv
readability_summary.jsonl
```
Typical fields include:

```text
id
suite_kind
dataset
project
class_name
testsuite_id
scenario
scenario_id
iteration
model_alias
java_file
readability_ok
readability_score
returncode
error
stdout
stderr
```
## 16. Interpreting Readability

Higher readability scores generally indicate more readable code according to the Scalabrino model.

Useful comparisons include:

```text
original vs refactored
scenario-level readability
model-level readability
selected candidate readability
```
A good refactoring should ideally improve readability while preserving validation success and semantic similarity.

## 17. CCTR Cognitive Complexity

### Purpose

CCTR estimates cognitive complexity for Java test suites.

It is intended to approximate how much mental effort is required to understand the test code.

### Output files

CCTR outputs are written under:

```text
outputs/<experiment>/06_metrics/complexity/cctr/
```
Typical files:

```text
cctr_results.csv
cctr_results.jsonl
cctr_summary.csv
cctr_summary.jsonl
```
Typical fields include:

```text
id
suite_kind
dataset
project
class_name
testsuite_id
scenario
scenario_id
iteration
model_alias
java_file
cctr_ok
cognitive_complexity
error
```
## 18. Interpreting CCTR

Lower cognitive complexity generally indicates simpler code.

A good refactoring may reduce cognitive complexity by:

```text
simplifying test structure
removing unnecessary branching
improving helper extraction
reducing nested constructs
making assertions clearer
```
However, very low complexity is not always better if the test loses behavior or meaningful assertions.

CCTR should be interpreted together with:

```text
compilation
JUnit success
coverage
CTSES
embedding similarity
readability
```
## 19. PMD Complexity and Maintainability

### Purpose

PMD is used to compute additional complexity and maintainability indicators.

It complements CCTR by providing tool-based static analysis.

### Output files

PMD outputs are written under:

```text
outputs/<experiment>/06_metrics/complexity/pmd/
```
Typical outputs may include detailed PMD rows and summary files depending on the evaluator configuration.

### Interpretation

PMD metrics can help identify:

```text
high cyclomatic complexity
large or complex methods
maintainability issues
static analysis violations
```
In TestHumanizer, PMD is mainly used as a complementary signal, not as the only selection criterion.

## 20. Validation Metrics

Before any quality metric is trusted, TestHumanizer checks whether original and refactored test suites are valid.

Validation includes:

```text
compilation
JUnit execution
coverage, when enabled
```
### Why validation matters

A refactored test suite with high readability but failing compilation is not useful.

A refactored test suite with high similarity but failing JUnit may not preserve behavior.

Candidate selection therefore uses validation as a hard constraint.

## 21. Coverage

Coverage is computed when JaCoCo is enabled.

Coverage can be used to check whether refactoring preserved the exercised portions of the production code.

Coverage should be interpreted carefully because:

```text
same coverage does not guarantee same assertions
higher coverage does not guarantee semantic preservation
coverage can remain stable even if test readability changes
```
Coverage is best used as a validation and diagnostic signal.

## 22. Candidate Selection Metrics

Candidate selection combines validation and metric signals to choose the best refactored candidate.

Default hard constraints:

```text
compile OK
JUnit OK
```
Default soft or threshold-based criteria:

```text
OpenAI embedding cosine similarity
CTSES
```
Default ranking signals:

```text
cosine similarity
CTSES
```
Example configuration:

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
    primary_embedding_model_alias: openai

  ctses:
    enabled: true
    threshold: 0.50

  ranking:
    cosine_weight: 0.60
    ctses_weight: 0.40
```
## 23. Candidate Selection Output

Candidate selection outputs are written under:

```text
outputs/<experiment>/06_metrics/selection/
```
Main files:

```text
selected_candidates.csv
selected_candidates.jsonl
```
Useful fields include:

```text
class_name
testsuite_id
scenario
model_alias
iteration
selected_refactored_test_file
compile_ok
junit_ok
selection_cosine_score
selection_ctses_score
passes_all_thresholds
selection_reason
```
## 24. Interpreting Candidate Selection

A selected candidate is not necessarily the globally highest-scoring candidate on every metric.

The default policy is designed to select a candidate that:

```text
compiles
passes JUnit
passes semantic similarity thresholds
passes CTSES threshold
has a good combined score
```
Possible selection reasons include:

```text
first_candidate_passing_all_thresholds
best_valid_candidate_by_composite_score
no_valid_candidate
```
## 25. Recommended Interpretation Strategy

When analyzing results, use this order:

### 1. Validation first

Check:

```text
compile_ok
junit_ok
coverage_ok
```
Invalid candidates should not be interpreted as successful refactorings.

### 2. Semantic preservation second

Check:

```text
OpenAI cosine similarity
CodeBERT cosine similarity
GraphCodeBERT cosine similarity
CTSES_score_1
CodeBLEU
METEOR
ROUGE-L
```
These metrics estimate whether the refactored suite still matches the original test intent.

### 3. Human-oriented quality third

Check:

```text
readability_score
cognitive_complexity
PMD metrics
```
These metrics estimate whether the refactored suite is easier to read, understand, and maintain.

### 4. Selection last

Use:

```text
selected_candidates.csv
```
to inspect which candidate TestHumanizer selected and why.

## 26. Metric Trade-Offs

A good refactoring is not necessarily the one with the highest value on a single metric.

Typical trade-offs:

| Situation                        | Interpretation                                                       |
|----------------------------------|----------------------------------------------------------------------|
| High readability, low similarity | The refactoring may have changed too much                            |
| High similarity, low readability | The refactoring preserved behavior but may not improve human quality |
| Low complexity, low CTSES        | The test may have been oversimplified                                |
| High CTSES, failing JUnit        | Similar text/code does not guarantee executable correctness          |
| High cosine, low CodeBLEU        | The suite may be semantically similar but structurally different     |
| High CodeBLEU, low readability   | The refactoring may preserve structure but remain hard to read       |

## 27. Scenario-Level Analysis

Metrics can be compared across scenarios:

```text
tests-only
code-centric
summary-based
```
Useful questions:

```text
Does production-code context improve semantic preservation?
Does summary-based prompting improve readability?
Which scenario gives the best trade-off between readability and similarity?
Does one scenario reduce cognitive complexity more than others?
```
## 28. Model-Level Analysis

Metrics can also be compared across models:

```text
gpt4o
mistral
other configured models
```
Useful questions:

```text
Which model preserves semantics better?
Which model improves readability more?
Which model produces more compilable refactorings?
Which model has lower cognitive complexity?
Which model is more stable across iterations?
```
## 29. Iteration-Level Analysis

When multiple iterations are enabled, TestHumanizer can compare candidate quality across repeated LLM attempts.

Useful questions:

```text
Does increasing iterations improve candidate quality?
Are later candidates more readable?
How often does the first candidate pass all thresholds?
How stable is each model across attempts?
```
## 30. Practical Recommendations

For most analyses:

1.  Use compilation and JUnit as hard filters.
2.  Use OpenAI cosine similarity as the primary semantic-preservation signal.
3.  Use CTSES as a complementary preservation metric.
4.  Use readability and CCTR to evaluate humanization.
5.  Use PMD metrics for additional maintainability analysis.
6.  Use selected candidates for final reporting.
7.  Always inspect representative examples manually.

## 31. Main Metric Files

| Metric              | File                                                     |
|---------------------|----------------------------------------------------------|
| CTSES               | `06_metrics/ctses/ctses_results.csv`                     |
| Embeddings          | `06_metrics/embeddings/embedding_similarity_results.csv` |
| Readability         | `06_metrics/readability/readability_results.csv`         |
| Readability summary | `06_metrics/readability/readability_summary.csv`         |
| CCTR                | `06_metrics/complexity/cctr/cctr_results.csv`            |
| CCTR summary        | `06_metrics/complexity/cctr/cctr_summary.csv`            |
| PMD                 | `06_metrics/complexity/pmd/`                             |
| Selection           | `06_metrics/selection/selected_candidates.csv`           |

## 32. Reproducibility Notes

For reproducible metric analysis, keep:

```text
effective config.yaml
metric CSV files
metric JSONL files
selected_candidates.csv
validation outputs
raw and extracted refactored suites
model aliases and model names
tool versions
Java and Python versions
```
Metric values can depend on:

```text
LLM model version
embedding model version
CodeBLEU environment
Java parser version
PMD version
readability model setup
preprocessing configuration
```
## 33. Summary

TestHumanizer metrics are designed to answer three main questions:

1. Did the refactored test suite remain valid?
2. Did it preserve the original test intent?
3. Did it become more readable, understandable, or maintainable?
No single metric answers all three questions.

The recommended analysis is multi-dimensional:

```text
validation + semantic preservation + readability + complexity + selection
```
