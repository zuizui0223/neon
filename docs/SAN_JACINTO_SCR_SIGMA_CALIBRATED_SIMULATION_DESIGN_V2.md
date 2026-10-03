# San Jacinto SCR sigma downstream-impact simulation — calibrated design v2

Date: 2026-10-03

Status: frozen after v1 feasibility results, before any v2 downstream sigma results are opened.

## Why v2 is needed

Simulation v1 established that FIRST, LAST and check-level SCR fits can diverge materially, especially when post-capture displacement is large. However, its fixed parameter grid did not closely reproduce the San Jacinto observation process: the simulated fraction of repeat-capture nights with a >=1-spacing first-to-last change was generally higher than the held-out empirical value.

The next step is therefore **not** to search sigma outcomes for a dramatic cell. It is to calibrate the simulation using observation-process summaries only, then open downstream sigma effects in independent simulation replicates.

## Empirical calibration targets fixed before v2

Targets come from the already-opened held-out Cricetidae diagnostics.

Across PEMA and PEER, use the mean of the two species summaries:

- repeat-capture fraction among captured individual-nights: target = 0.3765 (39.8% and 35.5%);
- >=1 trap-spacing first-to-last shift among repeat-capture nights: target = 0.70868 (72.6% and 69.2%);
- median first-to-last distance among **changed** repeat-capture nights: target = 13.25 m (14.0 and 12.5 m).

No empirical SCR sigma estimate is used in calibration.

## Protocol

As in v1:

- 7 x 7 multi-catch live-trap array;
- 6.25 m spacing;
- three checks per night;
- three consecutive nights;
- half-normal capture process generated with `secr::sim.capthist`;
- transient post-capture displacement can affect later checks in the same night;
- baseline activity centre is restored at the start of the next night.

## Stage A — observation-process calibration

Stage A generates data and computes only raw observation summaries. **No SCR model is fitted in Stage A.**

Candidate grid:

- true sigma: 3.125, 4.0, 5.0, 6.25 m;
- g0: 0.12, 0.16, 0.20;
- handling RMS displacement: 0, 12.5, 25.0 m;
- probability that a capture induces the transient displacement: 0 for the 0-m control; otherwise 0.25, 0.50, 0.75, 1.00.

Population density is 40 animals/ha to stabilize downstream fits without changing the within-individual calibration target.

Each calibration cell uses 12 independent replicates.

### Frozen calibration score

For each cell compute the mean/median observation summaries and

[
S =
\left(\frac{q_{repeat}-0.3765}{0.10}\right)^2+
\left(\frac{q_{shift}-0.70868}{0.10}\right)^2+
\left(\frac{m_{changed}-13.25}{6.25}\right)^2.
]

The three cells with the smallest finite S are selected automatically.

Selection code is executed before any downstream SCR fits exist.

## Stage B — downstream sigma test

For each of the three selected cells, generate 20 new independent replicates using a disjoint seed range.

Fit the same three representations as v1:

- CHECK: nine actual trap-check occasions;
- FIRST: three nightly occasions, earliest capture detector retained;
- LAST: three nightly occasions, latest capture detector retained.

Fit:

- detector = multi;
- detectfn = HN;
- CL = TRUE;
- g0 ~ 1;
- sigma ~ 1;
- 100 m buffer mask.

## Primary outcomes

For each representation:

- relative sigma error vs generating sigma;
- fit rate.

Pairwise:

- FIRST/CHECK - 1;
- LAST/CHECK - 1;
- LAST/FIRST - 1.

The already frozen 10% absolute relative-difference threshold defines a practically material representation effect.

## Interpretation

The primary v2 question is:

> Under simulation conditions selected solely because they reproduce the observed San Jacinto repeat-capture frequency and within-night spatial change, does reducing a night to FIRST or LAST materially alter fitted SCR sigma relative to the actual check-level representation?

A secondary question is whether check-level SCR itself is biased when post-capture displacement violates the static activity-centre assumption.

## Claim boundary

- The empirical two-species SCR sigma gate remains stopped.
- V2 is simulation evidence about downstream inferential sensitivity.
- Calibration to the empirical observation process does not make the simulated sigma effect an empirical sigma estimate.
- The selected calibration cells and their Stage B effects must all be reported; cells cannot be discarded after sigma outcomes are opened.
