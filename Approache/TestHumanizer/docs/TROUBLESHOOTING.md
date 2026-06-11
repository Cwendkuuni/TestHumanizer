# Troubleshooting

This document lists common TestHumanizer issues and how to debug them.

Use it when a pipeline phase fails, produces missing outputs, or gives unexpected results.

## 1. General Debugging Strategy

TestHumanizer is a phase-based pipeline. When something fails, identify the phase first.

`text id="mv5hzb" Phase 1     Target loading Phase 2     EvoSuite generation Phase 3     Original validation Phase 4     Refactoring input preparation Phase 4.5   Source summarization Phase 5A    Prompt preparation Phase 5B    LLM refactoring Phase 6     Java extraction Phase 7     Refactored validation Phase 8     CTSES Phase 9     Embeddings Phase 10    Readability Phase 11    CCTR Phase 12    PMD Phase 12.5  Candidate selection Phase 13    Report generation`

Then inspect the closest upstream output.

Example:

`text id="t1zubf" If Phase 7 fails:   inspect Phase 6 outputs first.`

Example:

`text id="ko7d85" If candidate selection fails:   inspect validation outputs and metric outputs first.`

## 2. Useful Debug Commands

### Inspect configuration

`bash id="edwt0l" testhumanizer inspect-config \   --config configs/experiments/evosuite_simple_project.yaml`

### Run with verbose logs

`bash id="g9bj6j" testhumanizer run \   --config configs/experiments/evosuite_simple_project.yaml \   --preset fast \   --verbose`

### Show per-item details

`bash id="9gmzee" testhumanizer run \   --config configs/experiments/evosuite_simple_project.yaml \   --preset fast \   --show-details`

### Show metric details

`bash id="nm5b58" testhumanizer run \   --config configs/experiments/evosuite_simple_project.yaml \   --preset fast \   --show-metrics`

### Avoid new LLM calls

`bash id="n306ns" testhumanizer run \   --config configs/experiments/evosuite_simple_project.yaml \   --preset fast \   --no-llm`

### Disable coverage temporarily

`bash id="yho9pf" testhumanizer run \   --config configs/experiments/evosuite_simple_project.yaml \   --preset fast \   --no-coverage`

## 3. Environment Problems

### Problem: `testhumanizer: command not found`

Possible causes:

`text id="s4ykjg" virtual environment is not activated package was not installed editable install failed`

Check:

`bash id="qqih23" source .venv/bin/activate pip install -e . which testhumanizer`

### Problem: Python import error

Possible causes:

`text id="sd1ae3" package not installed wrong virtual environment missing dependency local file name conflicts with package`

Check:

`bash id="vbvw1v" source .venv/bin/activate python -c "import testhumanizer; print(testhumanizer)"`

Also check:

`bash id="dy04z6" pip list`

### Problem: Java is not found

Possible causes:

`text id="ngy1xf" Java is not installed JAVA_HOME is not set java is not in PATH`

Check:

`bash id="l3em6x" java -version javac -version echo $JAVA_HOME`

## 4. Configuration Problems

### Problem: YAML file cannot be loaded

Possible causes:

`text id="njx1ek" wrong path invalid YAML indentation missing required section wrong data type`

Check:

`bash id="s7k3fd" testhumanizer inspect-config \   --config configs/experiments/evosuite_simple_project.yaml`

### Problem: Output directory is wrong

Possible causes:

`text id="f8k2m0" experiment.output_dir points to an unexpected path CLI --output-dir override was used relative path interpreted from repository root`

Check:

`yaml id="lq0bh9" experiment:   output_dir: outputs/evosuite_simple_project`

Also check the run command for:

`text id="l15uf8" --output-dir`

### Problem: CLI overrides do not behave as expected

Remember:

`text id="0nm72z" explicit CLI options override presets fast fills missing scenarios and iterations full fills missing scenarios and iterations ready uses the YAML as source of truth`

Examples:

`bash id="35c1wv" testhumanizer run --config config.yaml --preset fast`

runs all scenarios with one iteration unless overridden.

`bash id="xle6qc" testhumanizer run --config config.yaml --preset fast --iterations 3`

uses three iterations because the explicit CLI value wins.

## 5. Phase 1: Target Loading Issues

### Problem: No targets found

Possible causes:

`text id="n0nr0f" dataset.targets_file path is wrong target CSV is empty CSV header is incorrect rows are malformed`

Check:

`bash id="t37abo" cat configs/experiments/targets_simple_project.csv`

Check YAML:

`yaml id="ui2p2p" dataset:   targets_file: configs/experiments/targets_simple_project.csv`

### Problem: Target source path is wrong

Possible causes:

`text id="0dtm5t" source_path does not exist path is relative to the wrong directory file was moved class name does not match file`

Check:

`bash id="k1e55l" ls -l path/to/MyClass.java`

### Problem: Fully qualified class name is wrong

Possible causes:

`text id="v0hdqp" test_class_fqdn does not match package declaration class_name is simple name but EvoSuite needs package name target CSV contains incomplete class name`

Check Java source:

`java id="dqahft" package com.example;`

Then target CSV should contain:

`text id="x967zr" test_class_fqdn = com.example.MyClass`

## 6. Phase 2: EvoSuite Generation Issues

### Problem: EvoSuite jar not found

Possible causes:

`text id="i4nkxi" wrong evosuite_jar path tools directory not present jar was not downloaded`

Check:

`bash id="j1zfne" ls -l tools/evosuite-master-1.2.1-SNAPSHOT.jar`

Check YAML:

`yaml id="dvevlw" test_generation:   evosuite_jar: tools/evosuite-master-1.2.1-SNAPSHOT.jar`

### Problem: EvoSuite cannot find the target class

Possible causes:

`text id="irno05" wrong test_class_fqdn wrong classpath compiled .class file missing package declaration mismatch`

Check compiled class:

`bash id="n7mq3n" find . -name "MyClass.class"`

Check target CSV fields:

`text id="fgqbg4" classpath test_class_fqdn class_files_dir`

### Problem: EvoSuite generates no usable suite

Possible causes:

`text id="x879rd" class has no testable methods constructor is inaccessible dependencies are missing search budget is too low EvoSuite crashed`

Try increasing:

`yaml id="sd3ml9" test_generation:   search_budget_seconds: 180   runs_per_class: 3`

## 7. Phase 3: Original Validation Issues

### Problem: Original test compilation fails

Possible causes:

`text id="fi8q79" missing JUnit jar missing Hamcrest jar missing EvoSuite runtime jar wrong project classpath generated imports cannot be resolved Java version mismatch`

Check tool paths in YAML.

Check generated test file under:

`text id="1xemhm" outputs/<experiment>/02_evosuite/generated/`

### Problem: Original JUnit execution fails

Possible causes:

`text id="tg2lnd" generated test exposes a real failing behavior missing runtime dependency wrong classpath at execution time EvoSuite scaffolding issue`

Inspect validation outputs under:

`text id="tfp3n3" outputs/<experiment>/05_validation/`

### Problem: Coverage fails

Possible causes:

`text id="56drkb" JaCoCo jar paths are wrong class_files_dir is wrong source_files_dir is wrong JUnit execution failed upstream`

Check:

`bash id="y0ggux" ls -l tools/jacoco-0.8.8/lib/jacocoagent.jar ls -l tools/jacoco-0.8.8/lib/jacococli.jar`

Temporarily skip coverage:

`bash id="8z9zmy" testhumanizer run \   --config configs/experiments/evosuite_simple_project.yaml \   --no-coverage`

## 8. Phase 4: Refactoring Input Preparation Issues

### Problem: `prepared_inputs.jsonl` is missing

Possible causes:

`text id="a56b7l" Phase 2 did not produce original_suites_metadata.csv preparation.refactoring_inputs is false original generated test files are missing`

Check:

`bash id="swab96" ls -l outputs/<experiment>/02_evosuite/original_suites_metadata.csv`

Check YAML:

`yaml id="5msnzg" preparation:   refactoring_inputs: true`

### Problem: Prepared input has missing source context

Possible causes:

`text id="fbqh8n" source_path is wrong source file cannot be read target CSV metadata incomplete`

Check:

`bash id="z1hwp2" ls -l path/to/source/File.java`

## 9. Phase 4.5: Source Summarization Issues

### Problem: Summaries are not generated

Possible causes:

`text id="m7smtz" summarization.enabled is false API key missing source_path invalid summary already exists and skip_existing is true`

Check YAML:

`yaml id="xxpzjv" summarization:   enabled: true`

Check outputs:

`bash id="j4y78e" ls -l outputs/<experiment>/03_summaries/`

### Problem: Summary-based scenario does not use summaries

Possible causes:

`text id="8nfqkc" summarization.inject_into_summary_based is false no selected summary summary_store cannot match target metadata scenario is not summary-based`

Check prompt metadata:

`bash id="gkh376" csvcut -c scenario_id,summary_used,summary_source \   outputs/<experiment>/04_refactorings/prompts/refactoring_prompts_metadata.csv`

### Problem: LLM-SIDE score missing

Possible causes:

`text id="d8hzba" llm_side.enabled is false llm_side.use_for_selection is false LLM judge call failed metadata was generated before enabling LLM-SIDE`

Check:

`yaml id="imfpvx" summarization:   llm_side:     enabled: true`

## 10. Phase 5A: Prompt Preparation Issues

### Problem: `refactoring_prompts.jsonl` is missing

Possible causes:

`text id="yxn7yg" prepared_inputs.jsonl missing preparation.refactoring_prompts is false scenario configuration is empty or invalid model aliases are missing`

Check:

`bash id="t7wg3t" ls -l outputs/<experiment>/04_refactorings/prepared_inputs.jsonl`

Check YAML:

`yaml id="oxprqn" preparation:   refactoring_prompts: true`

### Problem: Prompt metadata has no summary for Scenario 3

Possible causes:

`text id="1gwk09" summaries were not generated summary injection disabled summary matching failed wrong scenario ID`

Check:

`bash id="qwyxwf" csvcut -c class_name,scenario_id,summary_used,summary_source \   outputs/<experiment>/04_refactorings/prompts/refactoring_prompts_metadata.csv`

## 11. Phase 5B: LLM Refactoring Issues

### Problem: Raw LLM output is missing

Possible causes:

`text id="5ryqam" llm_execution.refactoring_outputs is false --no-llm was used prompts file missing API call failed all outputs already skipped but file was removed`

Check:

`bash id="noyxlw" ls -l outputs/<experiment>/04_refactorings/llm_outputs/raw_refactoring_outputs.jsonl`

### Problem: OpenAI call fails

Possible causes:

`text id="s9zbk4" API key missing wrong api_key_env model name invalid network problem timeout too short rate limit`

Check:

`bash id="qtgz71" echo $OPENAI_API_KEY_1`

Check YAML:

`yaml id="oxhvrb" api_key_env: OPENAI_API_KEY_1`

### Problem: Mistral call fails

Possible causes:

`text id="93tsy1" API key missing wrong api_key_env model name invalid network problem timeout too short rate limit`

Check:

`bash id="p4fj3t" echo $MISTRAL_API_KEY_2`

### Problem: LLM output is not valid Java

Possible causes:

`text id="tm3l0z" model ignored requested format output was truncated prompt too long response contained explanation but no code code fence missing`

This is usually handled in Phase 6 by extraction statuses.

## 12. Phase 6: Java Extraction Issues

### Problem: Extraction fails

Possible causes:

`text id="j9d1et" raw output contains no Java code code fence missing class declaration missing LLM returned partial code LLM returned explanation only`

Check:

`bash id="f8ar9b" ls -l outputs/<experiment>/04_refactorings/llm_outputs/raw_refactoring_outputs.jsonl`

Check extraction metadata:

`bash id="0iixxu" csvcut -c id,extraction_status,error \   outputs/<experiment>/04_refactorings/extracted_suites/extracted_refactored_suites_metadata.csv`

### Problem: Extracted Java file has wrong class name

Possible causes:

`text id="o24r4y" LLM renamed the class incorrectly reconstruction did not enforce expected name prompt allowed too much freedom`

Check the extracted Java file under:

`text id="ahjz07" outputs/<experiment>/04_refactorings/extracted_suites/`

## 13. Phase 7: Refactored Validation Issues

### Problem: Refactored compilation fails

Possible causes:

`text id="lacqst" invalid Java syntax missing imports wrong package declaration wrong class name missing dependencies LLM removed required scaffolding`

Check compilation metadata under:

`text id="xkc1lh" outputs/<experiment>/05_validation/`

Inspect the extracted file directly.

### Problem: Refactored JUnit fails

Possible causes:

`text id="y7njy7" LLM changed test behavior assertions were modified incorrectly test data changed expected exception removed setup logic changed test order assumptions introduced`

Check JUnit logs under:

`text id="tuc9yl" outputs/<experiment>/05_validation/`

### Problem: Refactored coverage drops

Possible causes:

`text id="lduswp" LLM removed test cases LLM simplified inputs too aggressively assertions or method calls were changed coverage config is wrong`

Compare original and refactored validation outputs.

## 14. Phase 8: CTSES Issues

### Problem: CodeBLEU error

Possible causes:

`text id="q7hsuf" CodeBLEU virtual environment missing codebleu_python path wrong CodeBLEU package not installed language parser dependency missing`

Check:

`bash id="qdetb9" ls -l .venv-codebleu/bin/python`

Check YAML:

`yaml id="ezvjgh" metrics:   ctses:     codebleu_python: .venv-codebleu/bin/python`

### Problem: NLTK resource download appears every run

Possible causes:

`text id="e09e6u" NLTK cache path not persisted resource check always triggers download message permission issue in cache directory`

Check:

`bash id="bfvoqg" ls -l ~/.cache/testhumanizer/nltk_data`

This is usually not fatal if CTSES completes successfully.

### Problem: CTSES score is low

Possible causes:

`text id="ib1xqk" refactored code changed too much assertions removed test data changed large structural rewrite extraction mismatch`

Check:

`text id="xu5s6t" CodeBLEU METEOR ROUGE-L CTSES_score_1`

Also inspect original and refactored test code manually.

## 15. Phase 9: Embedding Issues

### Problem: HuggingFace model loading fails

Possible causes:

`text id="qxu74n" model not downloaded network issue transformers dependency missing CUDA issue insufficient memory`

Try CPU mode in YAML:

`yaml id="cfiwk4" metrics:   embeddings:     codebert:       device: cpu     graphcodebert:       device: cpu`

### Problem: OpenAI embedding fails

Possible causes:

`text id="tr3ec9" OPENAI_API_KEY missing wrong api_key_env model name invalid network issue timeout rate limit`

Check:

`bash id="dve8tq" echo $OPENAI_API_KEY_1`

### Problem: Embedding similarity is unexpectedly low

Possible causes:

`text id="wpy01r" LLM changed test behavior preprocessing removed too much extracted refactored code is incomplete wrong original/refactored matching`

Check:

`text id="asoi27" embedding_model_alias cosine_similarity original_truncated refactored_truncated status error`

## 16. Phase 10: Readability Issues

### Problem: Scalabrino readability fails

Possible causes:

`text id="vwn2ws" rsm.jar not found Java command not found timeout too short input Java file missing readability model directory wrong`

Check:

`bash id="t3g0nr" ls -l tools/Readability-model/rsm.jar`

Check YAML:

`yaml id="ebvy12" metrics:   readability:     rsm_dir: tools/Readability-model     rsm_jar: rsm.jar`

### Problem: Readability score missing

Possible causes:

`text id="c7z5mp" readability runner failed Java file path invalid result could not be parsed timeout`

Check:

`text id="c9fa0w" readability_ok readability_score returncode error stdout stderr`

## 17. Phase 11: CCTR Issues

### Problem: CCTR fails on a Java file

Possible causes:

`text id="nofry7" Java file not found Tree-sitter parsing issue invalid Java syntax encoding issue`

Check:

`text id="8e0y6n" cctr_ok cognitive_complexity error`

### Problem: CCTR complexity is unexpectedly high

Possible causes:

`text id="33x884" many test methods many assertions nested control flow parameterized tests helper calls and chained method calls`

CCTR is a diagnostic metric. Interpret it together with readability and semantic preservation.

## 18. Phase 12: PMD Issues

### Problem: PMD fails

Possible causes:

`text id="dskssa" PMD directory is wrong PMD executable not found ruleset invalid Java file path invalid timeout`

Check:

`bash id="e00j2g" ls -l tools/pmd-bin-7.0.0-rc4`

Check YAML:

`yaml id="b3gj4l" metrics:   complexity:     pmd:       enabled: true       pmd_dir: tools/pmd-bin-7.0.0-rc4`

### Problem: PMD produces no metrics

Possible causes:

`text id="jum3su" ruleset does not include expected rules PMD output parser mismatch PMD version mismatch all files skipped`

Check PMD raw output if available.

## 19. Phase 12.5: Candidate Selection Issues

### Problem: No candidate selected

Possible causes:

`text id="786t8p" all refactored suites failed compilation all refactored suites failed JUnit cosine similarity below threshold CTSES below threshold metric files missing candidate matching failed`

Check:

`bash id="i8p7tw" ls -l outputs/<experiment>/06_metrics/selection/`

Inspect:

`text id="x6zwml" selected_candidates.csv`

Also inspect:

`text id="76cq3y" 05_validation/ 06_metrics/ctses/ctses_results.csv 06_metrics/embeddings/embedding_similarity_results.csv`

### Problem: Candidate selected but thresholds not passed

Possible causes:

`text id="t8qpr2" policy falls back to best valid candidate threshold too strict some metrics missing`

Check fields:

`text id="0jgn4c" passes_all_thresholds selection_reason selection_cosine_score selection_ctses_score`

### Problem: Wrong candidate selected

Possible causes:

`text id="f5xk8j" ranking weights not configured as expected primary embedding alias mismatch CTSES metric alias mismatch iteration metadata mismatch`

Check YAML:

`yaml id="emc6ch" selection:   ranking:     cosine_weight: 0.60     ctses_weight: 0.40`

## 20. Phase 13: Report Issues

### Problem: Report is not generated

Possible causes:

`text id="54t9vq" reports.synthetic.enabled is false selection output missing metric files missing report generator crashed`

Check:

`bash id="iu0m46" ls -l outputs/<experiment>/07_reports/`

Check YAML:

`yaml id="dnmj75" reports:   synthetic:     enabled: true`

### Problem: PNG figures are missing

Possible causes:

`text id="qow1nc" Kaleido not installed export_png is false Plotly export failed`

Check YAML:

`yaml id="vnrjbg" reports:   synthetic:     export_png: true`

If HTML figures exist, report generation is still mostly successful.

## 21. Cache and Stale Output Issues

### Problem: Old outputs are reused unexpectedly

Possible causes:

`text id="ogxmcc" skip_existing enabled raw outputs already exist summary outputs already exist embedding cache enabled same output_dir reused`

For a fresh run:

`bash id="tgqnsp" rm -rf outputs/evosuite_simple_project`

Then rerun:

`bash id="c1zrxb" testhumanizer run \   --config configs/experiments/evosuite_simple_project.yaml \   --preset fast`

### Problem: LLM outputs are skipped

Possible causes:

`text id="w1kwks" raw output already exists skip_existing is true same prompt ID already processed`

This is usually expected behavior when rerunning the same experiment.

Use a new output directory for a completely independent run.

## 22. Performance Issues

### Problem: Pipeline is slow

Possible causes:

`text id="pqyxyy" EvoSuite search budget is high many target classes many scenarios many models many iterations LLM API latency CodeBERT/GraphCodeBERT loading OpenAI embedding calls PMD and readability external processes coverage enabled`

For faster debugging:

`bash id="b7g3c4" testhumanizer run \   --config configs/experiments/evosuite_simple_project.yaml \   --preset fast \   --models gpt4o \   --scenarios tests-only \   --no-coverage`

### Problem: GPU memory issue

Possible causes:

`text id="jb0jj4" embedding model too large other GPU processes are running batching or model loading uses too much memory`

Try CPU mode for embeddings:

`yaml id="3j80gz" metrics:   embeddings:     codebert:       device: cpu     graphcodebert:       device: cpu`

## 23. Cleaning Generated Files

To remove Python caches:

`bash id="dhjnhx" find . -name "__pycache__" -type d -prune -exec rm -rf {} + find . -name "*.pyc" -delete`

To find backup or copy files before publishing:

`bash id="xpz6da" find . -name "*copy*" -print find . -name "*.bak" -print`

To remove an experiment output:

`bash id="b58ua4" rm -rf outputs/<experiment>`

## 24. Minimal Debug Checklist

When something fails, check:

`text id="fay3gm" [ ] Is the correct virtual environment active? [ ] Does the YAML load with inspect-config? [ ] Does the target CSV exist? [ ] Do source_path values exist? [ ] Do compiled .class files exist? [ ] Does EvoSuite jar exist? [ ] Do JUnit and Hamcrest jars exist? [ ] Do JaCoCo jars exist if coverage is enabled? [ ] Are API keys exported if LLM calls are enabled? [ ] Does the previous phase output exist? [ ] Does the current phase output contain status/error fields? [ ] Is the output directory stale? [ ] Did CLI overrides change the expected behavior?`

## 25. When to Use Each CLI Mode

### Normal run

`bash id="agw928" testhumanizer run --config configs/experiments/evosuite_simple_project.yaml`

### Fast sanity run

`bash id="sudr0j" testhumanizer run \   --config configs/experiments/evosuite_simple_project.yaml \   --preset fast`

### Full run

`bash id="4qxq91" testhumanizer run \   --config configs/experiments/evosuite_simple_project.yaml \   --preset full`

### Debug run

`bash id="biwu9g" testhumanizer run \   --config configs/experiments/evosuite_simple_project.yaml \   --preset fast \   --verbose`

### Metrics debug run

`bash id="tyeao3" testhumanizer run \   --config configs/experiments/evosuite_simple_project.yaml \   --preset fast \   --show-metrics`

### Later-phase rerun without LLM calls

`bash id="f0yf15" testhumanizer run \   --config configs/experiments/evosuite_simple_project.yaml \   --preset fast \   --no-llm`

## 26. Reporting a Bug

When reporting a bug, include:

`text id="6l3j81" 1. The command you ran 2. The YAML configuration 3. The phase that failed 4. The terminal error 5. The relevant output directory 6. The relevant CSV/JSONL row with status/error 7. Java version 8. Python version 9. Tool versions, if relevant`

Useful commands:

`bash id="l2h929" python --version java -version javac -version testhumanizer inspect-config --config <config.yaml>`

Do not share API keys or private source code unless necessary.

## 27. Summary

Most TestHumanizer issues come from one of four sources:

`text id="lfjxcn" configuration paths Java classpath external tool setup LLM/API settings`

The fastest debugging method is:

`text id="vs8ux6" 1. Identify the failing phase. 2. Inspect the previous phase output. 3. Inspect the current phase status/error fields. 4. Run with --verbose or --show-metrics. 5. Fix the configuration or input artifact. 6. Rerun with the same output directory or a fresh one.`
