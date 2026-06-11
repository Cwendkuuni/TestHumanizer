# TestHumanizer Synthetic Report

## 1. Experiment overview

- Output directory: `/home/e113/Documents/Humanization-Project/HUMANIZATION/For_GitHub/TestHumanizer/Approache/TestHumanizer/outputs/reproducibility/defects4j/sample_2_seed_42/testhumanizer_outputs`
- Number of targets: **2**
- Number of prompts: **2**
- Number of generated summaries: **2**
- Number of evaluated candidates: **2**
- Number of selected candidates: **2**

- Scenarios: `Scenario-1`
- Models: `gpt4o`

## 2. Prompt and token usage

- Total prompt tokens: **2775**
- Mean prompt tokens: **1387.50**
- Max prompt tokens: **1821**

## 3. Summarization and SIDE diagnostics

- LLM-SIDE mean: **0.8750**
- LLM-SIDE min: **0.8500**
- LLM-SIDE max: **0.9000**

## 4. Candidate selection

- Threshold pass: **1/2** (50.00%)
- Selected OpenAI cosine mean: **0.9169**
- Selected OpenAI cosine min: **0.8776**
- Selected OpenAI cosine max: **0.9563**
- Selected CTSES mean: **0.5454**
- Selected CTSES min: **0.5000**
- Selected CTSES max: **0.5907**

## 5. Generated figures

- `candidate_selection_scatter`: `figures/candidate_selection_scatter.html`
- `selected_cosine_by_scenario`: `figures/selected_cosine_by_scenario.html`
- `selected_ctses_by_scenario`: `figures/selected_ctses_by_scenario.html`
- `threshold_pass_by_scenario`: `figures/threshold_pass_by_scenario.html`
- `prompt_tokens_by_scenario_model`: `figures/prompt_tokens_by_scenario_model.html`
- `llm_side_by_class`: `figures/llm_side_by_class.html`
- `embedding_similarity_by_model`: `figures/embedding_similarity_by_model.html`
- `ctses_all_candidates`: `figures/ctses_all_candidates.html`
- `maintainability_index`: `figures/maintainability_index.html`

## 6. Selected candidates table

| class_name   | testsuite_id   | scenario   | model_alias   |   iteration |   selection_cosine_score |   selection_ctses_score | passes_all_thresholds   | selection_reason                                |
|:-------------|:---------------|:-----------|:--------------|------------:|-------------------------:|------------------------:|:------------------------|:------------------------------------------------|
| PosixParser  | testsuite_1    | tests-only | gpt4o         |           1 |                 0.877597 |                  0.5    | False                   | best_candidate_but_validation_failed_or_missing |
| Entities     | testsuite_1    | tests-only | gpt4o         |           1 |                 0.956257 |                  0.5907 | True                    | first_candidate_passing_all_thresholds          |
