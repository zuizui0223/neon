# SCR downstream consequence synthesis v3

Date: 2026-10-03

Status: decision memo. This does not reopen the stopped two-species empirical SCR programme.

## Binding empirical status

The prospectively defined two-species SCR sigma programme remains stopped because PEER did not satisfy the frozen session-support gate.

- PEMA: 19 eligible sessions across 5 grids
- PEER: 2 eligible sessions across 2 grids
- binding decision: `stop_scr_sigma_sensitivity_not_estimable`

No result below changes that confirmatory decision.

## Post-stop PEMA empirical companion

A repaired multisession `secr` fit was completed for PEMA only after the programme stop and is therefore exploratory.

The FIRST and LAST datasets contain identical individual x occasion support:

- 19 frozen eligible sessions
- 5 grids
- 525 occasion-level observations in each representation

Primary model:

`g0 ~ b + grid + bout; sigma ~ 1`

Results:

- FIRST sigma = 8.8515 m (95% CI 8.0310–9.7559)
- LAST sigma = 8.5625 m (95% CI 7.7806–9.4229)
- LAST / FIRST = 0.9673
- relative change = -3.27%
- the pre-existing 10% contextual materiality threshold is not crossed

This is the important empirical result: strong within-night positional aliasing does not automatically imply a material change in pooled SCR sigma.

The result must remain labelled post-stop exploratory. It is not a rescued confirmatory test, and the overlapping marginal intervals are not a formal paired equivalence test.

## Calibrated simulation v2

The two-stage v2 calibration ran successfully in CI.

Stage A selected three parameter cells using only observation-process summaries, before any downstream sigma fits were opened.

Empirical targets:

- repeat-capture fraction = 0.3765
- >=1-spacing change among repeat nights = 0.70868
- median changed-night first-to-last distance = 13.25 m

Selected cells:

1. sigma=4 m, g0=0.20, response RMS=12.5 m, response probability=0.50
2. sigma=5 m, g0=0.16, response RMS=25 m, response probability=0.25
3. sigma=4 m, g0=0.16, response RMS=12.5 m, response probability=0.25

However, the selected Stage-A cells did not jointly reproduce the empirical targets well enough to justify the label “empirically matched”:

- repeat fractions = 0.327, 0.359, 0.300
- changed fractions = 0.725, 0.762, 0.718
- changed-night medians = 8.84, 8.84, 7.54 m

The largest mismatch is the changed-night distance target (13.25 m).

Independent Stage-B replicates also showed calibration drift:

- repeat fractions = 0.293, 0.368, 0.260
- changed fractions = 0.801, 0.806, 0.795
- changed-night medians = 8.84, 8.84, 6.25 m

Therefore v2 must not be promoted as a quantitative San Jacinto calibration.

### Downstream results from all three selected cells

Median LAST/FIRST sigma differences were:

- rank 1: +9.3%
- rank 2: +20.7%
- rank 3: +7.4%

Only one of the three selected cells crosses 10% at the median.

CHECK median relative error versus generating sigma was:

- rank 1: +19.1%
- rank 2: +16.1%
- rank 3: +5.4%

These results show that representation sensitivity can occur, but they do not establish a robust, empirically calibrated magnitude across all selected conditions.

## What the combined evidence now supports

The strongest interpretation is a two-stage one.

### Stage 1 — observation-process aliasing

The held-out empirical result shows that within-night detector state is frequently non-unique:

- PEMA: 72.6% of repeat nights shifted >=1 trap spacing
- PEER: 69.2%

This is a property of the observation process.

### Stage 2 — estimand stability

The downstream question is separate: does a plausible temporal representation materially change the quantity the ecologist reports?

The exploratory PEMA result says “not necessarily”: FIRST and LAST pooled sigma differed by only 3.3%.

Synthetic state-shift simulations say “it can”: when the within-night process systematically changes the spatial state sampled after capture, FIRST, LAST and CHECK can target different effective spatial scales.

Thus raw positional aliasing is a warning flag, not a bias estimate.

## Mechanistic interpretation

The empirical PEMA result is consistent with the possibility that much of the observed first-to-last detector change is exchangeable sampling around a common spatial kernel rather than a systematic directional post-capture state shift.

This is not proof that handling has no effect. It means the current data do not support a claim that handling causes a directional sigma distortion.

A useful diagnostic should therefore separate:

1. **positional non-uniqueness** — are multiple materially different detector states observed within one nominal occasion?
2. **estimand instability** — does changing the temporal representation materially alter the downstream parameter?

Conflating these two stages would overstate the empirical evidence.

## Manuscript consequence

Do not write:

> San Jacinto positional aliasing biased SCR sigma.

Do write, if the remaining robustness work is satisfactory:

> San Jacinto demonstrated frequent within-night positional non-uniqueness, while the post-stop PEMA fit showed that this did not automatically translate into a material FIRST-versus-LAST change in pooled sigma. Generative SCR simulations identified the additional condition under which representation becomes consequential: systematic within-occasion state change relative to the baseline spatial kernel.

This is more informative than a one-direction “aggregation causes bias” story because it identifies when the diagnostic should trigger concern and when a downstream stability check can clear it.

## Pending arbiter

The sequential dynamic-state robustness benchmark (`SCR_SIGMA_DYNAMIC_STATE_ROBUSTNESS_V2`) is the remaining high-value simulation.

It removes the conditional record-expansion component of the earlier stress test by generating every check through `secr::sim.capthist` and changing only the within-night state centre after capture.

Use that result to decide whether the “each check as an occasion” objection has been answered cleanly.

No new biological-effect branches should be opened before that benchmark is interpreted.
