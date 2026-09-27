# Public Mammal Spatial Packing Phase 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fit the amended, estimability-approved Portal and NEON ecological models on the frozen Phase-1 spatial-packing sessions, run all prespecified robustness checks, and freeze a model-result gate without changing the Phase-1 response.

**Architecture:** Phase-2 workflows download the exact frozen Portal and NEON development artifacts referenced by `estimability_gate_v1.json`; they do not rebuild the primary session tables. A shared model utility module owns deterministic standardization, design-matrix rank checks, confidence intervals and FDR. Portal and NEON primary models remain separate, then a result-gate script decides which ecological claims are supported and whether a manuscript should advance.

**Tech Stack:** Python 3.12; NumPy 2.1.1; pandas 2.3.x; SciPy 1.16.x; statsmodels **0.15.0**; GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-27-public-mammal-space-use-phase2-amendment.md`

## Global Constraints

- Phase-1 `Packing_z`, session builders, N flags and source manifests are frozen and may not be retuned after Phase-2 coefficients are opened.
- Phase-2 inputs must come from artifact IDs/digests frozen in `validation/public_mammal_space_use_v1/estimability_gate_v1.json`.
- Portal primary species = `Chaetodipus penicillatus`; N >= 5; control vs kangaroo-rat exclosure; 2009-08 through 2015-03.
- NEON primary species = `Myodes rutilus`; sites = BONA + DEJU; habitats = forest + shrub_scrub; N >= 5.
- Portal model = `Packing_z ~ treatment * z_logN` with crossed plot and census-period random intercepts.
- NEON primary model = `Packing_z ~ habitat + z_logN + site`; forest reference; BONA/DEJU site blocking.
- `z_logN = (log(N) - mean(log(N))) / population_sd(log(N))` with ddof = 0 inside the exact retained primary dataset.
- statsmodels is pinned to 0.15.0; Portal mixed-model fitting uses REML and a frozen optimizer sequence; no formula simplification after seeing results.
- No secondary species may replace either primary analysis as the headline result.
- Peromyscus is not a headline NEON taxon; the maniculatus–leucopus complex sensitivity is mandatory for any secondary Peromyscus result.
- Primary and secondary null/negative results are always retained.

## Review Focus

- Mixed-model convergence: workflow must fail rather than silently simplify random effects.
- Design-matrix aliasing: NEON habitat effects are non-estimable if habitat is rank-aliased with site.
- Input drift: Phase-2 must reject source artifacts whose IDs/digests/run SHAs differ from the estimability gate.
- Residual mechanical N-dependence: a null simulation check must show Packing_z does not acquire a strong relationship with N by construction.
- Sensitivity promotion: secondary/robustness analyses must never overwrite the frozen primary coefficient family.

---

### Task 1: Freeze Phase-2 Analysis Lock

**Files:**
- Create: `validation/public_mammal_space_use_v1/phase2_analysis_lock_v1.json`
- Create: `tests/test_public_mammal_phase2_lock.py`

**Interfaces:**
- Consumes: estimability gate + Phase-2 amendment spec.
- Produces: immutable artifact IDs/digests, primary species/site/habitat sets, formulas, z-logN rule, statsmodels version, optimizer sequence, sensitivity families.

- [ ] Write RED tests asserting the exact lock contents.
- [ ] Verify RED because lock is absent.
- [ ] Create the lock with:
  - Portal artifact ID 10929728652, digest `sha256:eb031608a547092340592a0127361283a2560ca22db9a1b3dc9a368fbef07686`, run 36314012402;
  - NEON artifact ID 10931291060, digest `sha256:865880ceac9cd0dbaffa160b515165c909380c2bd67eea14c70ab76756636cc9`, run 36315906620;
  - Portal primary species/treatments/formula;
  - Myodes BONA/DEJU forest/shrub formula;
  - secondary within-site contrasts;
  - optimizer sequence `lbfgs,bfgs,cg`;
  - `reml=true`;
  - N thresholds 3/5/8.
- [ ] Run tests GREEN.
- [ ] Commit: `Freeze public mammal Phase-2 analysis lock`.

### Task 2: Shared Modeling Utilities

**Files:**
- Create: `analysis/public_mammal_phase2_utils_v1.py`
- Test: `tests/test_public_mammal_phase2_utils.py`

**Interfaces:**
- Produces:
  - `z_log_n(values) -> np.ndarray`;
  - `assert_full_rank(X, columns) -> None`;
  - `bh_adjust(p_values) -> list[float]`;
  - `coefficient_record(result, term) -> dict`;
  - `verify_phase2_artifact_metadata(lock, label, api_metadata) -> None`.

- [ ] RED tests: ddof=0 standardization, constant-N failure, rank-deficiency failure, BH known values, artifact-digest mismatch failure.
- [ ] Implement minimal utilities.
- [ ] GREEN focused tests + full suite.
- [ ] Commit: `Add public mammal Phase-2 modeling utilities`.

### Task 3: Portal Primary Mixed Model

**Files:**
- Create: `analysis/fit_portal_cpen_phase2_v1.py`
- Create: `.github/workflows/public-mammal-phase2-portal.yml`
- Test: `tests/test_portal_cpen_phase2.py`
- Runtime outputs:
  - `results/generated/portal_cpen_phase2_primary_v1.json`
  - `results/generated/portal_cpen_phase2_primary_predictions_v1.csv`

**Interfaces:**
- Consumes exact frozen Portal session artifact.
- Produces P1 treatment main effect and P2 treatment×z_logN coefficient with CI, model convergence metadata, sample counts, plot counts and predictions.

- [ ] RED synthetic tests enforce:
  - only *C. penicillatus*;
  - N >= 5;
  - control/exclosure;
  - z-logN ddof=0;
  - groups = plot;
  - census period as crossed variance component;
  - exact primary formula;
  - no model selection.
- [ ] Implement input preparation.
- [ ] Implement `statsmodels.formula.api.mixedlm`:
  - formula `packing_z ~ C(treatment, Treatment(reference='control')) * z_logN`;
  - groups = constant vector of ones over all retained rows;
  - re_formula = `0`;
  - vc_formula = `{"plot": "0 + C(plot_id)", "period": "0 + C(period)"}`;
  - REML = true;
  - optimizer sequence frozen in lock;
  - require `result.converged`.
- [ ] Workflow verifies frozen artifact metadata before download, installs statsmodels 0.15.0, fits once and uploads outputs.
- [ ] Focused GREEN + full suite.
- [ ] Commit: `Fit Portal C penicillatus Phase-2 primary model`.

### Task 4: NEON Myodes Primary Habitat Model

**Files:**
- Create: `analysis/fit_neon_myodes_phase2_v1.py`
- Create: `.github/workflows/public-mammal-phase2-neon.yml`
- Test: `tests/test_neon_myodes_phase2.py`
- Runtime outputs:
  - `results/generated/neon_myodes_phase2_primary_v1.json`
  - `results/generated/neon_myodes_phase2_primary_predictions_v1.csv`

**Interfaces:**
- Consumes exact frozen NEON session artifact + frozen NLCD grouping.
- Produces shrub-vs-forest effect with HC3 CI, BONA/DEJU site coefficient, z-logN coefficient and site-specific descriptive effects.

- [ ] RED tests freeze:
  - species = *Myodes rutilus* only;
  - BONA + DEJU only;
  - forest + shrub_scrub only;
  - N >= 5;
  - formula `packing_z ~ C(habitat_group, Treatment(reference='forest')) + z_logN + C(site)`;
  - full-rank audit before fit.
- [ ] Implement preparation and rank audit.
- [ ] Fit OLS with HC3 covariance; fail if requested habitat contrast is aliased.
- [ ] Add descriptive BONA and DEJU habitat contrasts without promoting them to primary.
- [ ] Workflow verifies frozen NEON artifact metadata and runs once.
- [ ] GREEN focused + full suite.
- [ ] Commit: `Fit NEON Myodes Phase-2 primary habitat model`.

### Task 5: Prespecified NEON Within-Site Generalization Family

**Files:**
- Create: `analysis/fit_neon_secondary_habitat_phase2_v1.py`
- Test: `tests/test_neon_secondary_habitat_phase2.py`
- Runtime output: `results/generated/neon_secondary_habitat_phase2_v1.json`

**Frozen contrasts:**
- *Chaetodipus hispidus*, OAES: grassland_herbaceous vs shrub_scrub;
- *Perognathus parvus*, ONAQ: forest vs shrub_scrub;
- *Peromyscus boylii*, SJER: forest vs grassland_herbaceous.

**Model per contrast:**
`packing_z ~ habitat + z_logN`.

- [ ] RED tests assert exact species/site/habitat family and no dynamic species discovery.
- [ ] Implement three separate OLS HC3 fits.
- [ ] Apply BH FDR across exactly the three frozen habitat coefficients.
- [ ] Persist all coefficients regardless of p/q.
- [ ] GREEN + full suite.
- [ ] Commit: `Fit frozen NEON secondary habitat contrasts`.

### Task 6: Portal Robustness Family

**Files:**
- Create: `analysis/portal_cpen_phase2_sensitivity_v1.py`
- Test: `tests/test_portal_cpen_phase2_sensitivity.py`
- Runtime output: `results/generated/portal_cpen_phase2_sensitivity_v1.json`

- [ ] RED tests freeze N>=3, N>=8, long-term plots, PIT-reliable subset, leave-one-plot-out, leave-one-period-out.
- [ ] For N thresholds and LOO checks use the frozen Phase-1 session table.
- [ ] For PIT-only and alternative geometry statistics, rebuild a **separate sensitivity table** from the pinned Portal commit without changing the primary Phase-1 table.
- [ ] Implement null-standardized radius of gyration and nearest-neighbour alternatives with the same N/geometry conditioning.
- [ ] Report whether P1/P2 direction reverses under any sensitivity; never replace primary coefficients.
- [ ] GREEN + full suite.
- [ ] Commit: `Add Portal Phase-2 robustness analyses`.

### Task 7: NEON Robustness, Site Context and Taxonomy Sensitivity

**Files:**
- Create: `analysis/neon_phase2_context_sensitivity_v1.py`
- Test: `tests/test_neon_phase2_context_sensitivity.py`
- Runtime output: `results/generated/neon_phase2_context_sensitivity_v1.json`

- [ ] RED tests freeze the ten species with >=5 N>=5 sessions at >=2 sites.
- [ ] Estimate adjusted site means after z_logN control; report site spread only, not site mechanism.
- [ ] Add N>=3/N>=8 and leave-one-year/site sensitivity for primary Myodes.
- [ ] Build the mandatory *P. maniculatus–P. leucopus* aggregated sensitivity from public RELEASE-2026 capture data using the already-frozen taxonomy rule; do not mutate primary session files.
- [ ] Any habitat model first runs full-rank alias audit.
- [ ] GREEN + full suite.
- [ ] Commit: `Add NEON Phase-2 context and taxonomy sensitivity`.

### Task 8: Individual-Movement Validation

**Files:**
- Create: `analysis/neon_recapture_validation_phase2_v1.py`
- Test: `tests/test_neon_recapture_validation_phase2.py`
- Runtime output: `results/generated/neon_recapture_validation_phase2_v1.json`

**Interfaces:**
- Consumes public RELEASE-2026 pathogen-grid multi-night captures.
- Produces session-level median successive displacement and association with session Packing_z.

- [ ] RED tests freeze recapture eligibility before outcomes:
  - resolved individual;
  - >=2 capture locations within event;
  - valid coordinates;
  - pathogen grid;
  - same species/taxonomy rule.
- [ ] Implement successive displacement and per-session median.
- [ ] Join to population Packing_z only after both are independently computed.
- [ ] Fit prespecified association model with species and site controls; report as validation only.
- [ ] GREEN + full suite.
- [ ] Commit: `Validate population packing with NEON recapture displacement`.

### Task 9: Mechanical-Null Diagnostic

**Files:**
- Create: `analysis/audit_packing_n_independence_v1.py`
- Test: `tests/test_packing_n_independence.py`
- Runtime output: `results/generated/packing_n_independence_v1.json`

- [ ] RED test simulates random placements over Portal and NEON representative geometries for N across the observed range.
- [ ] Verify expected mean Packing_z approximately zero and no strong monotonic relationship with N.
- [ ] Freeze failure rule: absolute Spearman rho > 0.2 in either source is a design warning that blocks headline abundance-conditioned interpretation.
- [ ] GREEN + full suite.
- [ ] Commit: `Audit mechanical independence of Packing_z from abundance`.

### Task 10: Freeze Phase-2 Results and Manuscript Advance Gate

**Files:**
- Create: `analysis/freeze_public_mammal_phase2_results_v1.py`
- Test: `tests/test_public_mammal_phase2_result_gate.py`
- Runtime/persisted:
  - `results/public_mammal_phase2_summary_v1.json`
  - `validation/public_mammal_space_use_v1/phase2_result_gate_v1.json`
  - `docs/PUBLIC_MAMMAL_PHASE2_RESULT_V1.md`

**Advance-gate logic:**
- preserve Portal P1/P2 and Myodes primary regardless of sign/significance;
- record whether Portal result is robust to plot/year influence;
- record whether Myodes habitat result is estimable and robust;
- record whether any frozen secondary NEON contrast generalizes context dependence;
- record movement validation;
- record Packing_z mechanical-N audit;
- stop if the amendment's stopping rules are met.

- [ ] RED tests encode the stopping rules from the amendment spec.
- [ ] Implement summary/gate without changing any fitted model.
- [ ] Full repository test suite and workflow verification.
- [ ] Persist fingerprints of all Phase-2 source artifacts and results.
- [ ] Commit: `Freeze public mammal Phase-2 ecological result gate`.

No manuscript rewrite is included in this plan. A manuscript plan is written only if the Phase-2 result gate authorizes advancement.
