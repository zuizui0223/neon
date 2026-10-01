# SCR sigma downstream-impact simulation — locked design v1

Date: 2026-10-01

Status: **locked before simulation sigma estimates are inspected**

## Purpose

The empirical PEMA/PEER SCR-sigma programme stopped at its pre-specified support gate because PEER had only two eligible sessions. This simulation is not a rescue of that stopped test. It addresses the missing methodological question directly:

> When repeated within-night live-trap records are reduced to one detector location per night, under what conditions does the reduction change the estimated SCR spatial scale (sigma), relative to retaining each trap check as an occasion?

The simulation is designed so that a null result is informative. Under a stationary SCR observation process, FIRST/LAST nightly collapse may mainly reduce information rather than systematically bias sigma. A downstream shift should emerge only if within-night state dependence is large enough to matter.

## Empirical calibration only

The San Jacinto held-out data are used only to set an externally observed scale for interpretation:

- trap spacing: 6.25 m;
- repeat-capture-night material-shift fraction: 0.726 (PEMA), 0.692 (PEER);
- median first-to-last distance among changed nights from the earlier locked validation: about 14.0 m (PEMA), 12.5 m (PEER).

No empirical FIRST/LAST SCR sigma estimate has been opened.

## Detector geometry and sampling schedule

- fixed 7 x 7 detector array;
- spacing = 6.25 m;
- detector process = multi-catch;
- 5 nights;
- 4 checks per night;
- rectangular activity-centre region = detector bounding box + 100 m on each side;
- exact population size = 350 per replicate;
- baseline hazard intercept lambda0 = 0.10 per detector per check.

The data-generating detector model is hazard half-normal (HHN). For animal centre x and detector k,

lambda_k(x) = lambda0 * exp(-d_k(x)^2 / (2 sigma^2)).

For a multi-catch detector array on one check, total hazard is Lambda = sum_k lambda_k. Capture occurs with probability 1-exp(-Lambda); conditional on capture, detector k is selected with probability lambda_k/Lambda.

## Baseline sigma axis

True long-term sigma is varied relative to trap spacing:

- 0.5 spacing = 3.125 m;
- 1 spacing = 6.25 m;
- 2 spacings = 12.5 m.

This axis spans a detector array that is coarse, matched, or fine relative to the underlying spatial scale.

## Post-release state-shift axis

The principal sensitivity axis is a stylized post-capture state displacement.

After the first capture of an animal within a night, a Bernoulli response is drawn once. With probability 0.70, the effective centre used for subsequent checks is shifted in a uniformly random direction by h; otherwise it remains at the long-term centre. The shift persists for the remainder of that night and resets before the next night.

h is varied as:

- 0 spacing;
- 1 spacing = 6.25 m;
- 2 spacings = 12.5 m;
- 3 spacings = 18.75 m.

The 0.70 response probability is an empirical-scale stress-test setting motivated by the approximately 69-73% observed changed-location fraction. It is **not** interpreted as an estimate of a handling-effect probability.

The h=0 cells are the stationary-SCR null. The h>0 cells represent increasing within-night state dependence after handling/release. This mechanism is deliberately explicit because the empirical second and later positions occur after capture and release.

## Three analysis representations

Each simulated raw record set is analysed three ways.

1. **CHECK**: every trap check is a separate SCR occasion (20 occasions).
2. **FIRST**: one SCR occasion per night, retaining the first capture of each animal-night.
3. **LAST**: one SCR occasion per night, retaining the last capture of each animal-night.

All representations use the same detector array, long-term activity-centre mask, HHN detection function, and conditional likelihood.

Fitted model:

- lambda0 ~ 1
- sigma ~ 1
- CL = TRUE

CHECK is a data-preserving comparator, not assumed to be biologically correct when h>0. The generating long-term sigma is the truth target for estimator bias.

## Replication

Primary run: 12 independent replicates per 3 x 4 = 12 parameter cells (144 simulated datasets; up to 432 SCR fits).

The random seed sequence is fixed from base seed 20261001.

If runtime proves prohibitive, only computational engineering may change (parallelization or identical-seed batching). Parameter cells, estimands and decision thresholds may not be changed after results are opened.

## Primary estimands

For each representation R in {CHECK, FIRST, LAST}:

relative_bias_R = (sigma_hat_R - sigma_true) / sigma_true.

Relative to CHECK:

delta_FIRST_CHECK = (sigma_FIRST - sigma_CHECK) / sigma_CHECK

delta_LAST_CHECK = (sigma_LAST - sigma_CHECK) / sigma_CHECK.

FIRST-vs-LAST sensitivity:

delta_LAST_FIRST = (sigma_LAST - sigma_FIRST) / sigma_FIRST.

For each parameter cell report:

- median and mean relative bias;
- median absolute relative bias;
- RMSE of sigma;
- median FIRST-CHECK and LAST-CHECK relative differences;
- fraction of successful paired fits with absolute difference >=10%;
- FIRST-vs-LAST >=10% fraction;
- fit-failure fraction.

The 10% threshold is a pre-specified practical-effect threshold, not a significance test.

## Observation-process summaries

For every simulated dataset also compute:

- fraction of detected animal-nights with >=2 captures;
- fraction of repeat-capture nights whose FIRST-to-LAST detector distance is >=1 trap spacing;
- median FIRST-to-LAST distance across all repeat-capture nights;
- median FIRST-to-LAST distance among changed-location nights.

These quantities are used only to identify which simulated regimes resemble the empirical observation scale. They are not used to tune parameters after the run.

An empirical-scale descriptive region is defined before opening results as:

- mean material-shift fraction between 0.60 and 0.80; and
- mean median changed-night distance between 1.5 and 2.5 trap spacings.

## Interpretation rules

1. If h=0 cells show small median bias and <10% paired differences in most replicates, nightly reduction is not claimed to intrinsically bias sigma under stationary SCR.
2. If h>0 cells show increasing sigma distortion with h/sigma, the main result is a **boundary condition**: positional aliasing becomes inferentially consequential when within-night state displacement is large relative to the SCR spatial scale.
3. If h>0 cells do not materially change sigma, the paper must not claim downstream SCR distortion from the observed aliasing diagnostic alone.
4. Fit failure is retained as an outcome; failed fits are not replaced by easier parameter cells.
5. No empirical PEMA or PEER FIRST/LAST sigma estimate may be used to choose or alter simulation settings.

## Claim boundary

This simulation does not establish that San Jacinto animals actually undergo a handling-induced centre shift of magnitude h. It uses handling response as a transparent sensitivity mechanism because post-release movement is a known interpretive ambiguity in the raw protocol.

The simulation can support statements about **when temporal aggregation changes SCR inference under specified observation processes**. It cannot by itself identify natural movement, a handling effect, or the biologically correct representative location.
