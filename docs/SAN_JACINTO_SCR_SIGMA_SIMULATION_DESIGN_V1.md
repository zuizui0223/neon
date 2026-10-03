# San Jacinto SCR sigma downstream simulation — design v1

Date: 2026-10-03  
Status: post-stop simulation lane; frozen before paper-level benchmark results are opened.

## Why this exists

The empirical SCR sigma programme was stopped before any FIRST/LAST sigma was fitted because the prospectively frozen support gate required both held-out species to pass; PEMA passed and PEER did not. That stop remains valid and is not reopened here.

The manuscript nevertheless needs a direct downstream consequence. This simulation asks how much the estimated SCR spatial scale `sigma` can change when repeated within-night live-trap detections are represented as:

1. FIRST capture per night;
2. LAST capture per night; or
3. each trap check as its own occasion.

The third representation directly addresses the expected objection that repeated checks can simply be redefined as finer SCR occasions.

## Geometry and empirical calibration

- detector array: 7 × 7 traps;
- trap spacing: 6.25 m;
- activity-centre mask: common 100 m buffer;
- primary true sigma: 12.5 m = two trap spacings;
- 5 nights × 4 checks per night;
- 1,000 simulated animals before conditioning on detection;
- same-trap short-time persistence: 0.30.

The persistence value is fixed before the benchmark because, with zero post-release displacement, it makes the simulated repeat-night first-to-last change frequency roughly comparable to the held-out San Jacinto result (~0.69–0.73) and gives changed-night distances on the same trap-scale order (~12.5–14 m). It is a phenomenological calibration device, not an estimate of a biological movement parameter.

## Generating detector process

Before capture, detections arise from a half-normal spatial competing-hazard process around a fixed activity centre. Within a check, at most one trap is recorded per animal.

After the first capture of a night, an optional capture-associated displacement vector is drawn. Its direction is uniform and its magnitude is Rayleigh distributed with a prespecified median. The shifted effective centre persists for the remaining checks of that night and resets before the next night.

This deliberately separates two facts:

- repeated within-night positions can differ even with no handling displacement;
- if capture/release changes the animal's short-term spatial state, retaining later checks does not automatically restore the assumptions of a static SCR model.

## Frozen handling-displacement grid

Median displacement after first capture, in metres:

`0, 3.125, 6.25, 9.375, 12.5, 15.625, 18.75`

Equivalently, relative to true sigma:

`0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5`.

The zero cell is the negative control. The trap-scale cells bracket the observed first-to-last distances but are not claimed to identify the true handling displacement.

## Fitted downstream model

Each representation is fitted with the same static conditional half-normal SCR likelihood:

- multi-catch competing-hazard detector model;
- common sigma;
- free baseline detection hazard;
- activity centres numerically integrated over the same 100 m mask;
- likelihood conditioned on an individual being detected at least once.

This targets sigma, not density.

## Primary downstream quantity

For each replicate:

`LAST-vs-FIRST = sigma_LAST / sigma_FIRST - 1`.

The pre-existing materiality threshold from the stopped empirical sigma design is retained unchanged:

`abs(relative difference) >= 10%`.

The benchmark reports the first displacement cell at which the mean LAST-vs-FIRST difference reaches 10% in magnitude.

A valid negative control requires the zero-displacement mean LAST-vs-FIRST difference to remain below 5% in magnitude.

## Finer-occasion comparison

The check-level fit is not treated as an oracle. Its comparison with FIRST tests whether redefining every check as an occasion removes the downstream effect under a process in which capture can alter subsequent spatial state.

## Claim boundary

This simulation can support:

> Capture-associated within-night state change at trap-scale magnitudes can make estimated SCR sigma depend materially on how repeated checks are represented, and redefining checks as occasions does not necessarily remove that sensitivity.

It cannot support:

- that San Jacinto animals were displaced by handling;
- that FIRST is the biologically correct location;
- that the simulated displacement distribution is the true movement process;
- that the observed San Jacinto aliasing magnitude alone identifies sigma bias;
- a density effect.

## Relationship to the empirical stop

The previous result `stop_scr_sigma_sensitivity_not_estimable` remains authoritative for confirmatory real-data SCR inference. This simulation is a separate downstream-consequence analysis motivated by the observed spatial scale, not a rescue of the stopped gate.
