# San Jacinto SCR sigma distortion simulation — design v1

Date: 2026-10-03

Status: frozen before simulated sigma effects are inspected.

## Purpose

The empirical San Jacinto programme established that repeated captures within a nominal night often occur at different traps, but the prospectively planned real-data SCR sigma comparison stopped because PEER had only two eligible sessions. That stop remains binding.

This simulation is the single authorized downstream-impact analysis. It asks when a one-location-per-night reduction changes the spatial scale estimated by a standard half-normal SCR model, and whether redefining each within-night trap check as its own occasion necessarily solves the problem.

No real-data FIRST/LAST sigma estimate is opened by this analysis.

## Empirical calibration targets

Only already-opened observation-process summaries may calibrate the simulation.

PEMA:
- repeat-observed nights / all valid individual-nights = 485 / 1219 = 0.3979;
- >= one-trap-spacing FIRST-to-LAST shift among repeat nights = 352 / 485 = 0.7258;
- median FIRST-to-LAST span = 8.8388 m.

PEER:
- repeat-observed nights / all valid individual-nights = 107 / 301 = 0.3555;
- >= one-trap-spacing FIRST-to-LAST shift among repeat nights = 74 / 107 = 0.6916;
- median FIRST-to-LAST span = 6.25 m.

These values calibrate the observation process only. They are not treated as undisturbed movement distances or home-range estimates.

## Generative model

Detector geometry is the San Jacinto 7 x 7 array with 6.25 m spacing and detector type `multi`.

Each simulated animal has a fixed baseline activity centre. Before the first capture of a night, detection is generated from a standard half-normal SCR kernel with generating sigma `sigma_true`.

After the first capture of an animal within a night, its temporary within-night detection centre becomes

`centre_after = (1-rho) * baseline_centre + rho * release_trap + e`

where:
- `rho` is short-term persistence at the release/capture location;
- `e` is an isotropic Normal perturbation with coordinate SD `release_jitter_sd_m`.

The temporary centre is reset to the baseline activity centre at the start of each new night.

This deliberately represents an observation-process/handling sensitivity model, not a claim about natural undisturbed movement. The zero-perturbation cell (`rho=0`, `release_jitter_sd_m=0`) is a negative control in which each check follows the ordinary static SCR model.

## Three analyses of the same simulated raw detections

1. FIRST-night: each animal-night is represented by its first capture.
2. LAST-night: each animal-night is represented by its last capture.
3. CHECK-level: every trap check is retained as a separate SCR occasion.

FIRST and LAST have the same animals and occupied nights by construction. CHECK-level retains the finer temporal information.

## Fitted model

R package: `secr`.

For each representation:
- detector type: `multi`;
- detection function: half-normal;
- conditional likelihood: `CL = TRUE`;
- model: `g0 ~ b`, `sigma ~ 1`;
- mask buffer: 100 m.

The learned-response term is retained because a capture itself occurs before the post-capture state perturbation.

## Frozen simulation grid

Common:
- 7 x 7 traps;
- spacing = 6.25 m;
- 5 nights;
- 4 checks per night;
- 120 simulated animals in the buffered population;
- generating sigma levels = 5, 10, 15 m;
- rho levels = 0, 0.5, 1.0;
- release-jitter SD levels = 0, 1.5, 3.125, 6.25, 12.5 m.

Empirical-anchor detection intercepts:
- PEMA-like: g0 = 0.09;
- PEER-like: g0 = 0.08.

The two g0 values were selected only from an effect-blind pilot targeting the already-opened repeat-observation frequencies; they are not fitted to any real-data sigma estimate.

Full run target: 100 Monte Carlo replicates per cell. A smoke run with fewer replicates is permitted solely to debug implementation.

## Primary outputs

For each cell and representation:
- fitted sigma;
- relative sigma error `(sigma_hat - sigma_true) / sigma_true`;
- convergence/fit-success fraction;
- empirical 95% CI coverage of `sigma_true`.

For each cell:
- LAST/FIRST sigma ratio;
- CHECK/FIRST sigma ratio;
- median and 2.5–97.5% Monte Carlo intervals of those ratios;
- simulated repeat-observed fraction;
- simulated >= one-spacing FIRST-to-LAST fraction;
- simulated median FIRST-to-LAST span.

## Interpretation rules

The zero-perturbation negative control must show no systematic FIRST-versus-LAST distortion. Failure of this control invalidates the simulation implementation.

A downstream effect is descriptively material when the median absolute FIRST-versus-LAST relative sigma change is >=10%; the threshold is fixed before results.

CHECK-level is not assumed to be correct. It is evaluated against generating sigma. If CHECK-level remains biased under post-capture state perturbation, the conclusion is that finer occasion definition preserves records but does not by itself repair a misspecified static-centre model.

## Claim boundary

Permitted:
- quantify when temporal reduction changes SCR sigma in a controlled generative model;
- identify direction changes caused by release-location persistence versus random post-release perturbation;
- test whether check-level occasion definition removes or retains downstream distortion;
- compare empirical observation-process summaries with simulated calibration summaries.

Not permitted:
- infer the actual San Jacinto home-range sigma from this simulation;
- claim that observed within-night shifts are natural movement;
- claim that handling caused the empirical shifts;
- reopen PEER real-data sigma fitting after its frozen support failure;
- lower the prior real-data estimability threshold.



## Estimability amendment after smoke v1

Smoke v1 was treated as an implementation/estimability check, not as a scientific result. With 120 simulated animals, the exact static negative-control cell (`rho=0`, `release_jitter_sd_m=0`) produced 0/3 successful FIRST, LAST and CHECK fits. Most other smoke cells were similarly non-estimable. Therefore no sigma-effect direction from smoke v1 is used for inference.

Before any primary simulation is run, the simulated buffered population is increased from 120 to 600 animals. This amendment changes only statistical support. The generating sigma grid, release-location persistence grid, jitter grid, PEMA-like/PEER-like detection profiles, three representation rules, fitted SCR model and 10% materiality threshold are unchanged.

The negative-control implementation gate is also repaired: a control cell cannot pass merely because all fitted ratios are missing. A valid full run now requires >=80% successful FIRST and LAST fits in each zero-perturbation control cell, a finite median LAST/FIRST ratio, and |median ratio - 1| < 0.10.

Smoke-v1 files remain in repository history as an audit record.
