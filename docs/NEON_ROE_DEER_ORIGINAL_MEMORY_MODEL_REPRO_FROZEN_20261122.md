# Reproduce original Ranc et al. PNAS 2021 fitted memory/perception/omniscience scores (prior-art mechanistic comparator)

**22 November 2026.** This is a reproduction of the original peer-reviewed cognitive/foraging models as a **known experimental positive control**, NOT a NEON result or a fit to NEON mammals, and not a newly specified cognition hypothesis. One existing NEON ecology Draft PR #23, submission HOLD. The goal is to distinguish empirical *resource site use* from independent model evidence of *memory*.

## Public original source pinned before executing models

Original published PNAS paper [10.1073/pnas.2014856118](https://doi.org/10.1073/pnas.2014856118) and original author public Zenodo [10.5281/zenodo.4609649](https://doi.org/10.5281/zenodo.4609649); canonical original public GitHub `ranc-n/Ranc-et-al.-PNAS-2021` immutable tag v1.0 commit `58cd85c863d50346df0c7b0d3ecfde97f8a5dfdb`. Validate exact original checkout HEAD before compiling any original C++.

The previous checksum-verified reproduction already accepted two original Git blob data hashes: time-series `18bebe5527828a9ff975d3f35c6b7553d67a3064` (26,841 hourly records, 25 `exp_id` animal-years) and initialization `918f5b981b4dc55c71347549d72815cf0b8db497` (25 rows). No data file modifications, no refitting, no reweighting animal-years, no subset selection.

**Original fitted model configurations:** compile original `Code/{Main,Calculate_attraction,Calculate_probability,Likelihood,Load_config_parameters,Load_other_inputs,Load_time_series,Memory_dynamics}.cpp` with `g++ -std=c++11 -O2` into an **untracked build executable**. Use exact original config file bytes (verify their original Git blob SHA) as follows:

| Published model | Original config | Git blob SHA1 | Declared `model_type` |
|---|---|---|---:|
| Omniscience | `Configuration_files/config_omniscience_best.txt` | `5578459a7ee89b4222bce884f377aecc6a0f2b5e` | 0 |
| Perception | `Configuration_files/config_perception_best.txt` | `02fe4c97cdae83eb0b32faf1931ba23b97d96c3f` | 1 |
| Spatial+attribute memory | `Configuration_files/config_memory_best.txt` | `f7da45032f81013c17e04bb63c9549cb65da1eab` | 3 |

Copy each original config to a distinct untracked build path, changing ONLY its three local file system path fields: output directory, time-series path, initialization path. **Retain all original numeric parameters and original model_type exactly byte-for-byte**. Run each model once in separate output directory. Check original `objective_function.csv` exists and is one finite numeric objective; no negative source probabilities, invalid model output or missing file is repaired. Do not run any new optimizer or modify source C++ to obtain a favorable fit.

Primary reported **previously fitted source quantity**: original three log-likelihood `objective_function.csv` values and pairwise differences `memory minus perception`, `memory minus omniscience`, with consistent same 25-source-year dataset and original optimized configs. No model parameter-count inference, AIC/BIC or statistical significance invented from configuration files alone; the peer-reviewed original paper's mechanistic model-selection results are PRIOR ART, and this is reproduction only. Any discrepancy or failure is original SOURCE/MODEL STOP; do not fit alternatives.

**Technical safety:** public exact pinned repository only, GitHub ephemeral runner with read-only permissions and no secrets, no execution of raw external network data from outside source checkout. Outputs private to build except anonymous original model scores. No per-individual GPS track IDs, location coordinates, source hourly states, memory parameter optimization or original source executable shared to NEON artifact.

## Interpretation

If memory's original fitted log likelihood is higher than perception and omniscience this reproduces the ordering of previously reported fits, but DOES NOT itself establish out-of-sample superior inference, model complexity adjustment or mechanistic identifiability from NEON. The original article's experimental loss of food access while sensory cues remained and its model comparisons already supported learning. Our current NEON small-mammal `Visit.ID` temporal consistency source gate remains STOP (62.5% versus frozen 80%), so we do NOT transfer a numeric learning coefficient to small mammals or claim a universal mammal law.

The compiled original code and analysis can be audited with `analysis/reproduce_ranc_2021_published_memory_models_v1.py`, tests and GitHub Action. Keep one NEON Draft / SUBMISSION HOLD.

## Actual author-code reproduction result, after original source/design freeze

Original [GitHub Actions run 45013361817](https://github.com/zuizui0223/neon/actions/runs/45013361817) PASSED **8 synthetic integrity tests**, compilation of original immutable v1.0 PNAS C++ and all THREE original best-parameter model executions (each outputs 26,841 original-state probabilities; these large original outputs are NOT committed). The first run [45013195629](https://github.com/zuizui0223/neon/actions/runs/45013195629) SOURCE STOPPED before any model score because the original three config files have terminal blank lines that the strict local parser rejected. The correction preserves those original blank lines exactly; no numeric parameters, original data, model type or target cohort were changed.

| Original published author fitted configuration | Same original time-series log-likelihood (`objective_function.csv`) |
|---|---:|
| `config_memory_best.txt`, original model type 3 | **−10,120.2669944** |
| `config_omniscience_best.txt`, original model type 0 | −10,537.1780702 |
| `config_perception_best.txt`, original model type 1 | −10,669.7566681 |

Raw original optimized model log-likelihood **memory − perception = +549.4896737**, **memory − omniscience = +416.9110758**. Scores are on the identical input and use original fitted parameters; they are NOT new optimizations or out-of-sample predictions, and the three model families differ in complexity. We did NOT calculate AIC, BIC, Bayes factors or p-values, nor rerun author parameter uncertainty or claimed cognitive half-lives. Any adjusted model comparison remains the published paper's responsibility; current code only independently checks the original author C++ and configured log-likelihood outputs.

The originally observed **31.26% → 5.17% → 19.56%** manipulated-site occupancy across 25 animal-year sources is reproduced separately under `results/neon_ranc2021_original_resource_closure_positive_control_20261122.json`. The original model comparison establishes **published mechanistic memory evidence in roe deer**, NOT direct learning or resource causation in NEON small-mammal genus capture-station recurrence. Complete source receipt `results/neon_ranc2021_original_memory_model_likelihoods_20261122.json`. Same one NEON paper Draft/SUBMISSION HOLD; no abstract promotion.
