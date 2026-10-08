# Empirical-scale sigma mixture benchmark v1

Date: 2026-10-01

Status: analytic benchmark from already-opened held-out observation-process data; not an SCR fitted result.

## Provenance

The held-out San Jacinto positional-aliasing workflow produced a repeat-night artifact:

- workflow run: 36580451294
- artifact: 11040165514
- artifact digest: sha256:65b60354049c4e174b434a7468f1792ba44c63ec92e7fe5b1cb60a4fbac8708e
- repeat-capture individual-nights: 592
- PEMA: 485
- PEER: 107

The frozen denominator audit gives 1,520 valid captured individual-nights in the two held-out species.

Among the 592 repeat nights, 426 had FIRST-to-LAST displacement >= one trap spacing (6.25 m).

## Empirical transition kernel

For the 426 non-zero/material displacement vectors:

- RMS displacement length: **16.9386 m**
- mean squared displacement: **286.9168 m^2**
- mean vector: approximately (-0.279, +0.029) m
- mean-vector magnitude: **0.280 m**
- covariance eigenvalue ratio: **1.38**

The mean displacement is therefore negligible relative to the RMS scale. The vector kernel is not perfectly isotropic, but the isotropic second-moment approximation is reasonable as a scalar benchmark.

The exact injected transition probability in the consequence benchmark is

q = (592 / 1520) * (426 / 592)
  = 426 / 1520
  = **0.280263**.

This is an empirical calibration of the simulation observation process, not an estimate that all singly observed nights had zero movement.

## Scalar second-moment benchmark

For an isotropic baseline half-normal spatial scale sigma and a zero-mean random transition H,

sigma_eff / sigma ~= sqrt(1 + q E[R^2] / (2 sigma^2)).

Using the empirical vector kernel:

| baseline sigma | predicted sigma_eff / sigma | predicted inflation |
|---:|---:|---:|
| 6.25 m | 1.4245 | +42.45% |
| 12.5 m | 1.1213 | +12.13% |
| 25.0 m | 1.0317 | +3.17% |

Using the tiny observed non-zero mean vector to compute the exact mixture covariance changes these ratios by less than 0.003 percentage points.

## Ten-percent boundary

Solving

sqrt(1 + q E[R^2] / (2 sigma^2)) = 1.10

gives

**sigma ~= 13.84 m**.

Thus the same empirically observed within-night transition kernel is predicted to be materially consequential for a baseline SCR spatial scale below about 14 m, but much less consequential when baseline sigma is substantially larger.

This is the central scale-free criterion:

> downstream consequence depends on the within-occasion transition variance relative to baseline sigma squared, not on raw displacement alone.

Equivalently, the effective all-night RMS transition scale is

sqrt(q E[R^2]) = **8.967 m**,

and the relevant dimensionless quantity is approximately 8.967 / sigma.

## Why this matters for the simulation

The frozen consequence benchmark uses true sigma values 6.25, 12.5 and 25 m. Before any fitted simulation output is interpreted, the analytic benchmark therefore predicts three qualitatively different regimes:

1. strong consequence (6.25 m);
2. near the pre-specified 10% materiality boundary (12.5 m);
3. weak consequence (25 m).

The discrete 7 x 7 trap array, finite sampling, capture conditioning, detector competition, edge effects, FIRST/LAST selection, and behavioural-response fitting can all move the fitted estimates away from this continuous-limit prediction. Those departures are exactly what the full `secr` simulation is intended to measure.

## Claim boundary

This benchmark does not:
- estimate empirical PEMA or PEER sigma;
- prove handling caused the observed transitions;
- imply singly observed nights had no transition;
- replace the frozen `secr` consequence simulation.

It provides an interpretable pre-fit prediction and a dimensionless boundary against which the simulation can be checked.
