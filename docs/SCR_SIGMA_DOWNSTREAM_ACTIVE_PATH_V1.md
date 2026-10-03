# SCR sigma downstream programme — active path v1

## 2026-10-03 status update

The downstream question is no longer open-ended.

**Primary scientific result obtained:** the frozen empirical-transition consequence benchmark shows that stationary nightly collapse is approximately unbiased, whereas selecting an observation-conditioned displaced state instead of the canonical state changes fitted sigma by about 15–17% at the central 12.5 m simulation scale. Mirroring PRE versus POST reverses whether FIRST or LAST is larger, so the result is representative-state sensitivity rather than superiority of one rule.

**Numerical QA repair in progress:** two of 1,080 model fits were incorrectly counted as successful despite sigma >300 km and sigma SE = 0. The success rule now requires a finite positive sigma SE and ordered finite CI; generator, seeds and scientific cells are unchanged. The central 12.5 m result is unaffected.

**Only two supporting tasks remain:**
1. dependence-aware CHECK pilot (`g0 ~ Bk`) to answer whether finer occasions alone are sufficient;
2. post-stop exploratory PEMA FIRST/LAST fit, whose latest failure occurred only in multi-session sigma extraction after the fits completed.

The MEE integration is specified in `docs/MEE_V0_4_SCR_DOWNSTREAM_INTEGRATION_V1.md`.

No additional downstream biological endpoint or branch is authorized.

Date: 2026-10-01

## Single active question

Does within-night positional aliasing merely discard information when records are collapsed, or can it change the spatial scale parameter estimated by SCR when the within-night observation process contains more than one spatial state?

No additional biological endpoints are to be opened until this question is resolved.

## Authoritative hierarchy

### 1. Primary manuscript benchmark

**Empirically anchored SCR sigma consequence benchmark**

Files:
- `docs/SCR_SIGMA_CONSEQUENCE_SIMULATION_DESIGN_V1.md`
- `analysis/simulate_scr_sigma_consequence_v1.R`
- `.github/workflows/scr-sigma-consequence-simulation.yml`

Why primary:
- reproduces the actual 7 x 7, 6.25 m, three-check-per-night protocol;
- uses the already-opened pooled repeat-capture probability (592/1520);
- uses the already-opened conditional changed-location probability (426/592);
- resamples observed PEMA + PEER changed-night displacement vectors directly;
- includes a stationary SCR negative control;
- mirrors POST and PRE timing so FIRST is not privileged by construction;
- compares CHECK, FIRST, and LAST against known generating sigma.

If successful and consequential, this replaces the current binomial benchmark as main Figure 2.

### 2. Mechanism / counterargument check

**Targeted local-response pilot**

Files:
- `docs/SAN_JACINTO_SCR_SIGMA_SIMULATION_PILOT_V1.md`
- `analysis/san_jacinto_scr_sigma_simulation_pilot_v1.R`

Role:
- tests the objection that every trap check can simply be treated as an occasion;
- contrasts naive CHECK with a dependence-aware CHECK-Bk fit;
- is exploratory and cannot replace the primary benchmark.

### 3. Analytic sensitivity companion

**Observation-state mixture theory**

File:
- `docs/SCR_SIGMA_MIXTURE_THEORY_V1.md`

Role:
- identifies h/sigma as the natural dimensionless control parameter;
- provides the dense-detector second-moment benchmark
  sigma_eff/sigma ~= sqrt(1 + (p/2)(h/sigma)^2);
- explains why a data-preserving CHECK analysis need not target long-term sigma when observation changes state.

The earlier fixed-h simulation is retained for provenance/sensitivity only and is not the manuscript's primary simulation.

### 4. Empirical companion, explicitly exploratory

**PEMA post-stop FIRST/LAST SCR fit**

Files:
- `docs/SAN_JACINTO_PEMA_SCR_SIGMA_POST_STOP_V1.md`
- `analysis/san_jacinto_pema_scr_sigma_post_stop_v1.R`

The frozen two-species empirical gate remains stopped because PEER had only two eligible sessions. PEMA alone may be reported only as post-stop exploratory support.

## Invalid run

The first fixed-h downstream simulation output at commit `5327e07...` is implementation-invalid because detector identifiers did not match `make.capthist` expectations. It is provenance only, not a scientific result. See `docs/SCR_SIGMA_DOWNSTREAM_RUN1_INVALID_V1.md`.

## Stop rule for branching

Do not create another downstream-analysis branch or endpoint.

The next manuscript decision is determined only by:

1. the primary consequence benchmark;
2. the already-defined targeted pilot;
3. the already-defined PEMA post-stop exploration.

If the primary benchmark shows little sigma consequence across the empirical calibration, the paper must narrow its claim rather than search for a different downstream effect.
