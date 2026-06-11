# TestHumanizer Synthetic Report

## 1. Experiment overview

- Output directory: `/home/e113/Documents/Humanization-Project/HUMANIZATION/For_GitHub/TestHumanizer/Approache/TestHumanizer/outputs/evosuite_simple_project`
- Number of targets: **2**
- Number of prompts: **12**
- Number of generated summaries: **2**
- Number of evaluated candidates: **36**
- Number of selected candidates: **12**

- Scenarios: `Scenario-1, Scenario-2, Scenario-3`
- Models: `gpt4o, mistral`

## 2. Prompt and token usage

- Total prompt tokens: **15406**
- Mean prompt tokens: **1283.83**
- Max prompt tokens: **1545**

## 3. Summarization and SIDE diagnostics

- LLM-SIDE mean: **0.9000**
- LLM-SIDE min: **0.9000**
- LLM-SIDE max: **0.9000**

## 4. Candidate selection

- Threshold pass: **12/12** (100.00%)
- Selected OpenAI cosine mean: **0.9477**
- Selected OpenAI cosine min: **0.9308**
- Selected OpenAI cosine max: **0.9574**
- Selected CTSES mean: **0.6170**
- Selected CTSES min: **0.5887**
- Selected CTSES max: **0.6485**

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

| class_name       | testsuite_id   | scenario      | model_alias   |   iteration |   selection_cosine_score |   selection_ctses_score | passes_all_thresholds   | selection_reason                       |
|:-----------------|:---------------|:--------------|:--------------|------------:|-------------------------:|------------------------:|:------------------------|:---------------------------------------|
| Calculator       | testsuite_1    | tests-only    | gpt4o         |           1 |                 0.957365 |                  0.619  | True                    | first_candidate_passing_all_thresholds |
| Calculator       | testsuite_1    | tests-only    | mistral       |           1 |                 0.95299  |                  0.613  | True                    | first_candidate_passing_all_thresholds |
| Calculator       | testsuite_1    | code-centric  | gpt4o         |           1 |                 0.957351 |                  0.6233 | True                    | first_candidate_passing_all_thresholds |
| Calculator       | testsuite_1    | code-centric  | mistral       |           1 |                 0.949941 |                  0.622  | True                    | first_candidate_passing_all_thresholds |
| Calculator       | testsuite_1    | summary-based | gpt4o         |           1 |                 0.955349 |                  0.6197 | True                    | first_candidate_passing_all_thresholds |
| Calculator       | testsuite_1    | summary-based | mistral       |           1 |                 0.951104 |                  0.6172 | True                    | first_candidate_passing_all_thresholds |
| StringNormalizer | testsuite_1    | tests-only    | gpt4o         |           1 |                 0.947053 |                  0.5937 | True                    | first_candidate_passing_all_thresholds |
| StringNormalizer | testsuite_1    | tests-only    | mistral       |           1 |                 0.937819 |                  0.6035 | True                    | first_candidate_passing_all_thresholds |
| StringNormalizer | testsuite_1    | code-centric  | gpt4o         |           1 |                 0.942313 |                  0.6485 | True                    | first_candidate_passing_all_thresholds |
| StringNormalizer | testsuite_1    | code-centric  | mistral       |           1 |                 0.930832 |                  0.6133 | True                    | first_candidate_passing_all_thresholds |
| StringNormalizer | testsuite_1    | summary-based | gpt4o         |           1 |                 0.946884 |                  0.6423 | True                    | first_candidate_passing_all_thresholds |
| StringNormalizer | testsuite_1    | summary-based | mistral       |           1 |                 0.943101 |                  0.5887 | True                    | first_candidate_passing_all_thresholds |
