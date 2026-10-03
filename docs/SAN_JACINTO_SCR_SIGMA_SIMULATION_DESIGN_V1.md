# San Jacinto SCR sigma downstream-impact simulation — design v1

Date: 2026-10-03

Status: frozen before simulation results are opened.

## Purpose

The empirical first-versus-last SCR sigma programme was stopped before fitting because the prospectively frozen support rule required both held-out species to advance and only PEMA passed (19 eligible sessions; PEER 2). This simulation does not reopen that empirical gate.

It addresses the missing downstream question directly:

> When a repeated-check live-trapping protocol is analysed either at the actual trap-check scale or after collapsing each night to one detector location, how much can the estimated SCR spatial scale sigma change, and under what amount of post-capture displacement does that sensitivity become material?

## Protocol calibration

The data-generating design follows the published San Jacinto protocol rather than an abstract sampling scheme:

- 7 x 7 live-trap grid;
- 6.25 m detector spacing;
- three trap checks per night (early, middle, late);
- animals released at the point of capture after each check;
- three consecutive trapping nights per bout.

The empirical held-out diagnostic already established, before this simulation design, that first-to-last detector changes of at least one trap spacing occurred on 72.6% of repeat-capture PEMA nights and 69.2% of PEER nights. Median first-to-last span was 8.84 m and 6.25 m, respectively. Those values are used only to identify whether a simulated cell lies on an empirically relevant observation-process scale; no empirical SCR sigma estimate is opened.

## Data-generating model

Simulation uses the R package secr itself for the capture process.

For each replicate:

1. Generate a homogeneous population around the fixed 7 x 7 detector array.
2. Keep each individual's baseline activity centre fixed across the three-night bout.
3. At each of the three within-night checks, generate one multi-catch-trap SCR occasion with a half-normal detection function:
   - detectfn = HN;
   - g0 = 0.20;
   - true sigma in {6.25, 12.5, 25.0} m.
4. After a capture, optionally impose a transient post-release displacement on that animal before the next check. The transient centre is drawn around its baseline centre with isotropic Gaussian displacement. Displacement is reset to baseline at the start of each night.

Post-capture displacement RMS is varied over:

- 0 m (negative control: no handling-induced displacement);
- 6.25 m (one trap spacing);
- 12.5 m (two trap spacings);
- 25.0 m (four trap spacings).

The zero-displacement cell is essential: any systematic sigma difference there is attributable to temporal aggregation / representative-location choice and finite sampling, not handling displacement.

## Three analysis representations

Every simulated raw detection table is converted into three datasets.

### CHECK

Each actual trap check is an SCR occasion. Three nights x three checks = nine occasions. All generated detections are retained.

### FIRST

Each night is one SCR occasion. If an animal is captured more than once in that night, only its earliest capture detector is retained.

### LAST

Each night is one SCR occasion. If an animal is captured more than once in that night, only its latest capture detector is retained.

FIRST and LAST therefore mimic the one-location-per-night reduction required by an exclusive detector history when a night is treated as one occasion. CHECK implements the obvious alternative objection: make each field check its own occasion.

## Fitted model

Each representation is fitted with the same conditional-likelihood SCR model:

- detector type: multi;
- detectfn: HN;
- CL = TRUE;
- g0 ~ 1;
- sigma ~ 1;
- common 100 m trap-buffer mask.

The target is sigma, not density.

## Primary estimands

For representation r in {CHECK, FIRST, LAST}:

- relative sigma error = (sigma_hat_r - sigma_true) / sigma_true;
- absolute relative sigma error;
- convergence / finite-estimate rate.

Pairwise sensitivity:

- FIRST versus CHECK: sigma_FIRST / sigma_CHECK - 1;
- LAST versus CHECK: sigma_LAST / sigma_CHECK - 1;
- LAST versus FIRST: sigma_LAST / sigma_FIRST - 1.

A 10% absolute relative difference is retained as the previously frozen practical-materiality threshold.

## Observation-process calibration outputs

For each replicate the simulation also reports:

- fraction of captured individual-nights with >=2 captures;
- among repeat-capture nights, fraction whose first and last detectors differ by >=6.25 m;
- median first-to-last distance among repeat-capture nights.

These are not fitted targets. They show which simulation cells resemble the empirically observed San Jacinto observation process.

## Primary predictions frozen before results

1. In the zero-displacement control, CHECK should recover true sigma without systematic directional bias; FIRST and LAST should have similar central tendency to each other. Precision may differ because nightly collapse removes occasions.
2. If post-capture displacement is strong enough to move subsequent detections away from the baseline activity centre, LAST should be more vulnerable than FIRST because LAST preferentially represents a post-release state.
3. CHECK is not assumed to be automatically unbiased under handling displacement. It retains all information but a standard static SCR model may absorb transient post-release displacement into sigma.
4. Therefore the relevant methodological question is not simply "collapse versus no collapse"; it is whether the observation protocol and occasion definition feed a spatial state into SCR that is compatible with the model's static activity-centre assumption.

## Stopping / interpretation rules

- The stopped empirical two-species sigma gate remains stopped.
- No empirical first-versus-last sigma estimates are opened by this simulation.
- A simulation cell is called empirically scale-matched only descriptively, when both its repeat-capture shift fraction and median first-to-last span are reasonably close to the already published held-out diagnostics.
- Failure of a fit is retained and counted, not silently dropped.
- Simulation results may motivate manuscript revision, but do not retroactively become confirmatory empirical evidence.

## Why this resolves the main reviewer objection

The likely objection "make each trap check its own occasion" is now an explicit comparator rather than a paragraph-level argument. The design separates three possibilities:

- nightly collapse is harmless;
- nightly collapse changes sigma;
- finer occasions retain data but still change sigma when post-capture displacement violates the static SCR state model.

That downstream decision consequence is the quantity the current v0.3 manuscript lacks.
