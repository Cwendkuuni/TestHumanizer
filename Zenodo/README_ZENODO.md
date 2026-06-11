# TestHumanizer Large Artifact Package

**Zenodo record:** https://zenodo.org/records/20644344  
**All-versions DOI:** https://doi.org/10.5281/zenodo.20644343  
**Version:** v1  
**Resource type:** Dataset / Replication artifact  
**Associated paper:** *Humanizing Automatically Generated Unit Test Suites with LLM-Based Refactoring*

## Authors / Creators

Wendkûuni C. Ouédraogo, Yinghua Li, Xueqi Dang, Paweł Borsukiewicz, Lingfeng Bao, Anil Koyuncu, Jacques Klein, David Lo, and Tegawendé F. Bissyandé.

## Description

This Zenodo archive contains the **large artifacts** associated with the TestHumanizer replication package for the study:

> **Humanizing Automatically Generated Unit Test Suites with LLM-Based Refactoring**

TestHumanizer is a hybrid **SBST + LLM** framework that uses EvoSuite-generated Java unit test suites as behaviorally grounded inputs and applies LLM-based refactoring to improve readability, maintainability, structure, and developer-oriented clarity while preserving compilability, coverage, and semantic intent.

The executable tool, scripts, configuration files, prompts, documentation, lightweight metadata, and reproduction commands are maintained in the associated GitHub repository. This Zenodo archive complements the GitHub repository by storing the large files that are required for full reproduction and inspection but are not suitable for direct inclusion in GitHub.

**GitHub repository:** `<GITHUB_REPOSITORY_URL>`

## Purpose of this archive

This archive is intended to provide long-term, versioned access to the large artifacts required to reproduce, inspect, and extend the TestHumanizer study.

It includes:

- raw and compilable LLM-refactored unit test suites;
- compiled benchmark layouts and Java dependency archives;
- the SIDE model artifact used for source-summary alignment;
- generated source-code summaries used by the summary-based refactoring configuration.

The Zenodo DOI ensures that these large artifacts remain citable and versioned independently from the GitHub repository.

## Archive structure

The archive is organized as follows:

```text
Refactored_data/
SIDE_Model/
Summary_generated/
Dependancies/
```

## 1. `Refactored_data/`

This directory contains the LLM-generated refactored unit test suites produced during the study.

```text
Refactored_data/
├── Raw_refactorings/
└── Compilable_refactorings/
```

### `Raw_refactorings/`

This directory contains raw LLM outputs before compilation filtering.

Expected files include:

```text
gpt4o_raw_refactored_tests.jsonl
gpt4o_raw_refactored_tests_metadata.csv
mistral_raw_refactored_tests.jsonl
mistral_raw_refactored_tests_metadata.csv
```

The `.jsonl` files contain the full raw refactored test-suite outputs.  
The `.csv` files provide flat metadata for indexing, filtering, and analysis.

### `Compilable_refactorings/`

This directory contains the subset of refactored test suites that passed the compilation stage.

Expected files include:

```text
gpt4o_compilable_refactored_tests.jsonl
gpt4o_compilable_refactored_tests_metadata.csv
mistral_compilable_refactored_tests.jsonl
mistral_compilable_refactored_tests_metadata.csv
```

These artifacts support analyses of refactoring feasibility, compilability, model behavior, and downstream metric computation.

## 2. `Dependancies/`

This directory contains compressed archives required by the TestHumanizer pipeline for full reproduction.

```text
Dependancies/
├── DEFECTS4J.zip
├── JARS.zip
└── SF-110.zip
```

### `DEFECTS4J.zip`

Contains the Defects4J source/class layout used by the pipeline.

The TestHumanizer reproducibility scripts expect Defects4J classes to be available in a layout compatible with:

```text
DEFECTS4J/SOURCES/<project>/<bug-id>/<package-path>/<ClassName>.java
DEFECTS4J/SOURCES/<project>/<bug-id>/<package-path>/<ClassName>.class
```

### `SF-110.zip`

Contains the SF110 source/class layout used by the pipeline.

The TestHumanizer reproducibility scripts expect SF110 classes to be available in a layout compatible with:

```text
SF-110/SOURCES/<project>/<package-path>/<ClassName>.java
SF-110/SOURCES/<project>/<package-path>/<ClassName>.class
```

### `JARS.zip`

Contains Java dependency jars used by the pipeline for EvoSuite generation, compilation, validation, coverage analysis, and metric computation.

These dependency archives are stored on Zenodo because they are large and because full reproduction requires compiled classes and project-specific classpaths.

## 3. `SIDE_Model/`

This directory contains the SIDE model artifact used during the source-code summarization stage.

```text
SIDE_Model/
├── hard-negatives-20260608T120328Z-3-001/
├── hard-negatives-20260608T120328Z-3-001.zip
└── README.md
```

The SIDE model is used to assess semantic alignment between generated natural-language summaries and the corresponding Java source code.

In TestHumanizer, these summaries support the **summary-based** refactoring configuration, where compact class descriptions are used instead of full source-code context to reduce prompt length and improve robustness.

## 4. `Summary_generated/`

This directory contains the generated source-code summaries used in the summary-based refactoring configuration.

```text
Summary_generated/
├── code_summary_dataset_flat.json
├── code_summary_dataset_structured.json
└── code_summary_mapping_report.json
```

The flat and structured JSON files contain generated class-level summaries.  
The mapping report documents how summaries are linked to dataset entries, projects, classes, and downstream refactoring inputs.

## Relationship with the GitHub repository

This Zenodo archive **does not replace** the GitHub replication repository.

The GitHub repository is the main entry point for:

- installing TestHumanizer;
- running the command-line pipeline;
- using the dataset experiment runner;
- accessing configuration templates;
- inspecting prompts and lightweight metadata;
- reading documentation;
- executing sample and full reproduction commands.

This Zenodo archive stores the large files needed by the GitHub codebase.

After downloading and extracting this archive, the expected high-level layout is:

```text
TestHumanizer/
├── Approache/
├── Datasets/
├── Prompts/
├── Results/
├── Refactored_data/
├── SIDE_Model/
├── Summary_generated/
└── Dependancies/
```

The main executable tool is located in:

```text
Approache/TestHumanizer/
```

The dataset experiment runner is located in:

```text
Approache/TestHumanizer/scripts/run_dataset_experiment.py
```

## Minimal usage after extraction

After cloning the GitHub repository and extracting this Zenodo archive into the expected repository layout, users can run sample experiments from the TestHumanizer tool directory.

### Defects4J sample run

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

### SF110 sample run

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

Full reproduction commands and detailed setup instructions are provided in the GitHub repository documentation.

## Notes on classpaths and dependencies

The TestHumanizer pipeline relies on compiled Java classes and project-specific classpaths when generating, compiling, and validating tests.

The dependency archives in `Dependancies/` provide the large compiled layouts and jars required for this process.

When using EvoSuite, avoid passing wildcard dependency paths directly, such as:

```text
/path/to/dependencies/*
```

EvoSuite validates classpath entries literally and may reject wildcard entries. The TestHumanizer runner expands dependency jars explicitly when needed and disables large global dependency directories by default to avoid incompatible Java bytecode versions.

## Citation

Please cite both the associated paper and this Zenodo artifact if you use these data or artifacts.

Recommended citation for this archive:

```text
Ouédraogo, W. C., Li, Y., Dang, X., Borsukiewicz, P., Bao, L., Koyuncu, A., Klein, J., Lo, D., & Bissyandé, T. F. (2026). TestHumanizer Large Artifact Package: Dependencies, Refactorings, SIDE Model, and Generated Summaries [Data set]. Zenodo. https://doi.org/10.5281/zenodo.20644343
```

BibTeX:

```bibtex
@dataset{ouedraogo2026testhumanizer_large_artifacts,
  title        = {TestHumanizer Large Artifact Package: Dependencies, Refactorings, SIDE Model, and Generated Summaries},
  author       = {Ouédraogo, Wendkûuni C. and Li, Yinghua and Dang, Xueqi and Borsukiewicz, Paweł and Bao, Lingfeng and Koyuncu, Anil and Klein, Jacques and Lo, David and Bissyandé, Tegawendé F.},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.20644343},
  url          = {https://zenodo.org/records/20644344}
}
```

## License

Unless otherwise stated, this artifact package is released under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** license.

Third-party software, benchmark projects, dependency jars, and pretrained model files may be governed by their own licenses. Users are responsible for complying with the licenses of the original third-party components.

## Contact

For questions about this artifact package, please contact:

**Wendkûuni C. Ouédraogo**  
University of Luxembourg

