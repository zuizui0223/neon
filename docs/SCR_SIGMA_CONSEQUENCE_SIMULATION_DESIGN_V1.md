# SCR sigma consequence benchmark v1

Date: 2026-10-01

Status: prospective simulation design; no simulated sigma results have been inspected at freeze.

## Purpose

The paper currently establishes that repeated within-night captures often occupy different trap positions, but the two attempted empirical downstream analyses stopped at pre-specified support gates. This benchmark targets the missing question directly:

> When repeated within-night trap positions are reduced to one nightly location, under what observation-process conditions does that choice materially alter the SCR spatial scale parameter sigma?

The benchmark is deliberately consequence-focused. It does not test binomial coverage, prove the triangle inequality, or treat positional aliasing itself as sufficient evidence of downstream bias.

## Empirical anchor

The San Jacinto protocol used a fixed 7 x 7 live-trap grid with 6.25 m spacing and three trap checks per night. Animals were released at the point of capture after each check.

Already-opened held-out Cricetidae results provide the observation-process calibration:

- PEMA: 485 repeat-capture nights among 1,219 valid captured individual-nights; 352 / 485 first-to-last shifts >= one trap spacing.
- PEER: 107 repeat-capture nights among 301 valid captured individual-nights; 74 / 107 first-to-last shifts >= one trap spacing.
- pooled repeat-capture probability among captured individual-nights = 592 / 1,520 = 0.38947.
- pooled material-change probability among repeat-capture nights = 426 / 592 = 0.71959.
- changed-night displacement vectors are resampled directly from the already-opened PEMA + PEER first-to-last trap vectors rather than replaced by a parametric distribution.

The public source file and its previously frozen SHA256 are reused only to reconstruct this already-opened displacement kernel. No empirical SCR sigma is fitted in this simulation branch.

## Two simulation families

### 1. Correctly specified stationary SCR negative control

A standard half-normal multi-catch SCR process generates nine check-level occasions (3 nights x 3 checks) on the San Jacinto 7 x 7 grid.

The same simulated records are encoded three ways:

1. CHECK: each trap check is an SCR occasion;
2. FIRST: each night is one SCR occasion represented by the first detection that night;
3. LAST: each night is one SCR occasion represented by the last detection that night.

Under this family there is no additional within-night transition process. Any systematic sigma difference among encodings would therefore indicate a problem with the benchmark itself or finite-sample/model-fitting effects, not positional aliasing.

This family is essential: aggregation is not assumed a priori to bias sigma.

### 2. Empirically anchored within-night transition

A standard three-occasion nightly SCR process first generates one canonical capture state per animal-night.

For each captured individual-night:

- with probability 0.38947, a second within-night record is added;
- conditional on a repeated record, with probability 0.71959 the second state is displaced by a non-zero first-to-last vector resampled from the pooled San Jacinto PEMA + PEER changed-night vector distribution;
- otherwise the repeated state is at the same trap.

The two observed states are assigned to early and late checks in a three-check night. Singly observed nights occupy one randomly selected check.

Two mirrored timing mechanisms are simulated:

- POST: the canonical SCR state is FIRST and the empirical transition is applied to LAST. This is compatible with a capture-triggered / post-handling perturbation, but does not assert that handling caused the San Jacinto pattern.
- PRE: the canonical SCR state is LAST and the same empirical transition is applied to FIRST. This mirror control prevents FIRST from being privileged by construction.

Thus the benchmark asks whether the representative-location rule and check-level encoding recover the known generating sigma when one within-night state contains an extra transition process.

## SCR design

Detector geometry:
- 7 x 7 multi-catch detectors;
- 6.25 m spacing;
- 100 m state-space buffer.

Generating detection function:
- half-normal;
- g0 = 0.15;
- true sigma in {6.25, 12.5, 25.0} m.

Population:
- homogeneous Poisson population;
- D = 20 animals / ha;
- 100 m simulation buffer.

Analysis model for every encoding:
- secr::secr.fit;
- detector type multi;
- half-normal detection function;
- conditional likelihood (CL = TRUE);
- g0 ~ b;
- sigma ~ 1;
- common 100 m mask.

The density parameter is not a target.

## Replication

Frozen Monte Carlo replication:
- 40 replicates per sigma x simulation-family x timing-mechanism cell.

Primary empirical-transition cells:
- 3 true sigma values x 2 timing mechanisms = 6 cells.

Stationary negative-control cells:
- 3 true sigma values.

Each replicate is fitted independently under CHECK, FIRST and LAST encodings.

## Primary outputs

For every cell and encoding:

- successful-fit count and fit-failure fraction;
- median and mean sigma estimate;
- median and mean relative bias: (sigma_hat - sigma_true) / sigma_true;
- RMSE;
- 95% CI coverage of the generating sigma;
- median relative CI width;
- fraction of successful replicates with absolute relative bias >= 10%.

Paired within-replicate contrasts are also reported:

- LAST / FIRST sigma ratio;
- CHECK / FIRST sigma ratio;
- CHECK / LAST sigma ratio.

The 10% threshold is descriptive and was inherited from the previously frozen empirical sigma-sensitivity design; it is not used to stop or rescue the simulation.

## Calibration outputs

The simulation reports, for the empirical-transition family:

- realized repeated-record fraction among captured individual-nights;
- realized first-to-last changed fraction among repeated nights;
- median first-to-last distance among changed nights;
- q90 first-to-last distance.

These are checked against the empirical anchor so readers can see how faithfully the injected transition reproduces the observed protocol-scale pattern.

## Interpretation rules fixed before results

1. Stationary null:
   - If CHECK, FIRST and LAST are approximately unbiased, the manuscript must explicitly state that nightly aggregation alone does not imply sigma bias under a correctly specified stationary SCR process.
   - If a systematic difference >10% appears, diagnose the benchmark before making a biological claim.

2. Empirical transition:
   - A method is not called "correct" merely because it uses finer temporal resolution.
   - Bias is evaluated against the known generating sigma.
   - POST and PRE are interpreted together. A result in which the encoding containing the perturbed state is biased while its mirror is not supports representative-rule sensitivity, not intrinsic superiority of FIRST or LAST.
   - CHECK may itself be biased if it treats capture-affected or otherwise nonstationary positions as exchangeable stationary SCR detections. This directly addresses the objection that "each check can simply be made an occasion."

3. Scope:
   - The empirical San Jacinto displacement kernel is an observation-process calibration, not a mechanistic estimate of natural movement or handling effects.
   - The benchmark does not claim that the real San Jacinto sigma is biased by any specific amount.
   - The stopped empirical sigma branch remains stopped; no real-data sigma estimates are opened.

## Manuscript decision

If the empirically anchored transition produces material sigma distortion in at least one timing mechanism while the stationary null remains approximately unbiased, replace the current binomial simulation as the main Figure 2 and move the old diagnostic simulation to Supplementary Information.

If the transition benchmark shows little sigma consequence across the calibrated range, do not use sigma as the paper's missing downstream consequence; the result should instead narrow the claim and trigger reconsideration of MEE fit.

## Freeze state

At creation of this design:

- stationary simulation sigma results inspected: false
- empirical-transition sigma results inspected: false
- empirical real-data sigma results inspected: false
- result-driven tuning of g0, D, sigma grid, repeat probability, change probability or timing mechanism: prohibited
