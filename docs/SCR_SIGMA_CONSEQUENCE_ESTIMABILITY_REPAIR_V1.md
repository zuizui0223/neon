# SCR sigma consequence benchmark — estimability-only repair v1

Date: 2026-10-03

Status: frozen after the original benchmark completed simulation but failed its pre-specified fit-success contract; frozen before the repaired benchmark is run.

## Original run failure

The empirically anchored consequence benchmark completed all simulation cells, but the workflow rejected the result because the empirical-transition cells at the smallest true spatial scale (sigma = 6.25 m) exceeded the frozen 25% fit-failure ceiling.

Observed fit failure in that boundary cell was 37.5–45%, depending on encoding and PRE/POST orientation. The 12.5 m and 25 m cells were substantially more stable.

This is an **estimability failure**, not a negative biological result. The failed run remains provenance and must not be silently reclassified as a successful primary benchmark.

## Repair principle

The repair may increase per-replicate information, but may not alter the effect-generating mechanism or the manuscript decision boundary.

Exactly one simulation input changes:

- population density used only to generate the simulated population: **20 -> 60 animals/ha**.

This raises the expected number of captured individuals per replicate while preserving the conditional SCR estimand.

The fitted models use `CL = TRUE`; density is not the downstream parameter being estimated.

## Frozen quantities that do not change

- detector geometry: 7 x 7;
- trap spacing: 6.25 m;
- state-space buffer: 100 m;
- 3 nights x 3 checks;
- half-normal generating detection function;
- g0 = 0.15;
- true sigma = 6.25, 12.5, 25 m;
- empirical repeat-record probability = 592 / 1520;
- empirical conditional material-change probability = 426 / 592;
- direct resampling of the already-opened PEMA + PEER material displacement vectors;
- POST and PRE mirrored timing mechanisms;
- stationary negative-control family;
- fitted model: `CL=TRUE; HN; g0 ~ b; sigma ~ 1`;
- CHECK, FIRST and LAST representations;
- 40 Monte Carlo replicates per cell;
- 10% practical relative-change threshold;
- 25% maximum cell-level fit-failure fraction.

No result-dependent tuning of sigma, transition scale, transition probability, model formula or practical-effect threshold is authorized.

## Interpretation rule

The repaired benchmark is usable as the primary manuscript benchmark only if:

1. every method x family x sigma x orientation summary has fit-failure fraction <=25%;
2. the stationary null does not show a systematic representation-induced sigma shift that invalidates the comparison;
3. empirical-transition effects are interpreted jointly with PRE/POST mirror controls rather than as evidence that FIRST or LAST is intrinsically correct.

If the density-only repair still fails the fit-success contract, the 6.25 m cell is treated as an estimability boundary. No second tuning step is authorized without first narrowing the primary benchmark claim.

## Why this is not effect tuning

Increasing population density changes Monte Carlo information, not the injected transition kernel. It is analogous to increasing the number of independent marked animals in a simulation study so the planned estimator can be evaluated. The original D=20 run and its failure remain documented.
