# Fixed-shift SCR sigma sensitivity — result interpretation v1

Date: 2026-10-01

Status: successful repaired run; **supplementary/mechanism result**, not the primary empirical-vector benchmark.

Authoritative result:
- `results/scr_sigma_downstream_simulation_v1.json`
- generated 2026-10-01 03:16:05 UTC
- 12 replicates per cell
- 12 parameter cells
- 144 simulated datasets
- all CHECK/FIRST/LAST fits successful

## What this simulation establishes

The simulation separates two questions that were confounded in manuscript v0.3:

1. Does reducing checks to one record per night intrinsically bias sigma under a stationary SCR observation process?
2. Does the reduction become consequential when the observation process changes spatial state after the first within-night capture?

The answer is **no for the first in adequately resolved grids, yes for the second when the state shift is large relative to sigma**.

## Stationary negative control: h = 0

When true sigma was at least one trap spacing, all three encodings were approximately unbiased in median:

### sigma = 6.25 m = 1 spacing

- CHECK median bias: -1.6%
- FIRST median bias: approximately 0.0%
- LAST median bias: -3.1%
- LAST vs FIRST median difference: -2.4%

### sigma = 12.5 m = 2 spacings

- CHECK median bias: -0.1%
- FIRST median bias: -2.3%
- LAST median bias: -3.5%
- LAST vs FIRST median difference: -2.8%

Thus nightly reduction did not create a systematic spatial-scale shift under a stationary process at these resolutions. It mainly reduced information.

The sigma = 3.125 m cell is a deliberate detector-resolution boundary case: trap spacing is 2 sigma. All representations were strongly biased downward, including CHECK. Crucially, FIRST and LAST still agreed with each other (median LAST-vs-FIRST difference about 0.0%). This is a sampling-geometry problem, not temporal positional aliasing.

## State shift: consequence grows with h / sigma

### true sigma = 6.25 m

| shift h | h / sigma | CHECK bias | FIRST bias | LAST bias | LAST vs FIRST |
|---:|---:|---:|---:|---:|---:|
| 0 m | 0 | -1.6% | ~0.0% | -3.1% | -2.4% |
| 6.25 m | 1 | +6.0% | -3.1% | +7.0% | +9.3% |
| 12.5 m | 2 | +25.7% | +2.9% | +33.1% | +28.7% |
| 18.75 m | 3 | +39.4% | +0.5% | +50.2% | +46.0% |

The FIRST encoding remains close to the baseline sigma because the simulated state shift occurs after the first capture. LAST increasingly estimates the displaced state.

### true sigma = 12.5 m

| shift h | h / sigma | CHECK bias | FIRST bias | LAST bias | LAST vs FIRST |
|---:|---:|---:|---:|---:|---:|
| 0 m | 0 | -0.1% | -2.3% | -3.5% | -2.8% |
| 6.25 m | 0.5 | +2.1% | +2.5% | +2.2% | -5.2% |
| 12.5 m | 1 | +6.8% | -0.4% | +7.3% | +8.7% |
| 18.75 m | 1.5 | +14.8% | +1.9% | +20.0% | +18.2% |

The transition crosses the pre-specified 10% practical scale only when h becomes comparable to or larger than sigma.

## Why “just use each check as an occasion” is not a universal solution

CHECK is the information-preserving encoding, but under the state-shift mechanism it contains both pre- and post-response detections.

For true sigma = 6.25 m:

- h = 12.5 m: CHECK median bias +25.7%;
- h = 18.75 m: CHECK median bias +39.4%.

For true sigma = 12.5 m:

- h = 18.75 m: CHECK median bias +14.8%.

Therefore finer occasioning solves the information-loss problem but not necessarily the **state-mixture problem**. If the observation protocol changes the state being sampled, a stationary check-level SCR model may estimate a mixture spatial scale.

This does not mean CHECK is wrong. It means its estimand can differ from the baseline long-term sigma under nonstationarity.

## Relation to the analytic benchmark

The qualitative pattern matches the second-moment prediction:

sigma_eff / sigma increases with the transition scale relative to baseline sigma.

The empirical-vector benchmark is preferred for the manuscript because it uses:
- the actual three-check San Jacinto protocol;
- the observed repeat probability;
- the observed changed-location probability;
- the observed first-to-last vector distribution;
- mirrored PRE and POST transition timing.

This fixed-h result should be used to show generality and the h/sigma boundary, not as the headline empirical calibration.

## Claim boundary

Supported:
- stationary nightly collapse need not systematically shift sigma;
- the same collapse can become consequential when within-occasion state displacement is large relative to sigma;
- splitting checks into occasions does not automatically recover baseline sigma when checks span different observation-conditioned states;
- detector spacing itself creates a separate failure mode when sigma is too small relative to the grid.

Not supported:
- that San Jacinto displacement was caused by handling;
- that FIRST is biologically correct;
- that the fixed-h mechanism is the unique process behind the observed data;
- empirical PEMA/PEER sigma effects.
