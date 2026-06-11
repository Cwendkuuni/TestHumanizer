# TestHumanizer Documentation Plan

## 1. User Documentation

### README.md

Main entry point for GitHub users.

Content:

- Project overview
- What TestHumanizer does
- Pipeline summary
- Main features
- Installation
- Quickstart
- Running the example project
- Running custom Java projects
- CLI presets
- Output structure
- Metrics summary
- Troubleshooting
- Citation / research context

### docs/INSTALLATION.md

Detailed installation guide.

Content:

- Python environment
- Java requirements
- EvoSuite setup
- PMD setup
- Scalabrino readability model setup
- CodeBLEU environment
- OpenAI / LLM API keys
- Optional GPU configuration

### docs/QUICKSTART.md

Minimal reproducible run.

Content:

- Run the included simple Java project
- Expected command
- Expected output
- Main output files
- How to inspect results

### docs/CONFIGURATION.md

YAML configuration guide.

Content:

- Project section
- Target classes
- Models
- Scenarios
- Iterations
- Validation
- Summarization
- Metrics
- Candidate selection
- Reports
- Logging

### docs/CUSTOM_PROJECTS.md

Guide for using TestHumanizer on user-defined Java projects.

Content:

- Required Java project structure
- How to define targets
- Required classpath fields
- Coverage configuration
- Common errors
- Example custom configuration

## 2. Technical / Developer Documentation

### docs/ARCHITECTURE.md

Internal architecture of TestHumanizer.

Content:

- Pipeline phases
- Main modules
- Data flow
- Output flow
- Metadata files
- Where each phase reads/writes

### docs/PIPELINE_PHASES.md

Detailed explanation of each phase.

Content:

- Phase 1: target loading
- Phase 2: EvoSuite generation
- Phase 3: original validation
- Phase 4: refactoring input preparation
- Phase 4.5: source summarization
- Phase 5A: prompt preparation
- Phase 5B: LLM refactoring
- Phase 6: Java extraction
- Phase 7: refactored validation
- Phase 8: CTSES
- Phase 9: embedding similarity
- Phase 10: readability
- Phase 11: CCTR cognitive complexity
- Phase 12: PMD complexity and maintainability
- Phase 12.5: candidate selection
- Phase 13: synthetic report

### docs/METRICS.md

Detailed metric documentation.

Content:

- CTSESAVG, CTSES_1, CTSES_2
- CodeBLEU
- METEOR
- ROUGE-L
- CodeBERT cosine similarity
- GraphCodeBERT cosine similarity
- OpenAI embedding cosine similarity
- Scalabrino readability
- CCTR cognitive complexity
- PMD cyclomatic complexity
- Maintainability index
- Candidate selection criteria

### docs/EXTENDING.md

Developer guide for customizing or extending TestHumanizer.

Content:

- Adding a new LLM provider
- Adding a new prompt scenario
- Adding a new metric
- Adding a new Java dataset adapter
- Adding a new report figure
- Adding a new selection policy
- Logging conventions
- Output metadata conventions

### docs/TROUBLESHOOTING.md

Common issues and fixes.

Content:

- EvoSuite not found
- Java compilation failures
- JUnit failures
- JaCoCo coverage issues
- CodeBLEU environment issues
- NLTK / METEOR issues
- OpenAI API key issues
- PMD issues
- Scalabrino readability issues
- GPU / CUDA embedding issues
- Output cache / stale result issues
