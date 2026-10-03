# San Jacinto SCR sigma simulation v1 — interpretation

Date: 2026-10-03

Status: completed exploratory downstream simulation; not yet the manuscript-final simulation.

## What v1 established

The stopped empirical two-species SCR sigma gate was not reopened. Instead, the frozen v1 generative simulation used the published San Jacinto geometry (7 x 7 grid, 6.25 m spacing, three checks per night, three nights) and `secr` 5.4.3 itself to generate and fit half-normal multi-catch SCR histories.

Three representations of the same generated detections were compared:

- CHECK: all nine field checks treated as occasions;
- FIRST: each night collapsed to its first capture location;
- LAST: each night collapsed to its last capture location.

Post-capture displacement was added only after a capture and reset at the start of each night.

## Main result

The downstream sigma estimate can change materially with the temporal representation.

A clear example is the cell with true sigma = 12.5 m and post-capture displacement RMS = 12.5 m:

- CHECK median relative sigma error: +17.6%;
- FIRST: +7.2%;
- LAST: +22.6%;
- median LAST/FIRST difference: +16.2%;
- 8/8 fitted replicates exceeded the pre-frozen 10% materiality threshold for LAST versus FIRST.

At stronger displacement (true sigma = 12.5 m; displacement RMS = 25 m):

- CHECK: +18.1%;
- FIRST: -9.7%;
- LAST: +26.1%;
- median LAST/FIRST difference: +43.2%;
- 8/8 replicates exceeded 10% for LAST versus FIRST.

At true sigma = 6.25 m and displacement RMS = 25 m, the divergence was extreme among fitted replicates:

- CHECK: +60.7%;
- FIRST: -6.1%;
- LAST: +91.3%;
- median LAST/FIRST difference: +97.2%.

This small-sigma cell had only 75% fit success and is therefore a sensitivity example, not a headline estimate.

## The important conceptual result

The obvious reviewer solution — "make each trap check its own SCR occasion" — is not automatically a full correction.

When post-capture displacement is present, CHECK retains the full field record but standard static SCR can absorb that transient displacement into sigma. In the 12.5/12.5 m cell CHECK itself was +17.6% above the generating sigma.

The methodological problem is therefore better stated as:

> Does the observation/handling process create within-session spatial states that violate the state process assumed by the downstream SCR model, and how much does the chosen temporal representation change the fitted spatial scale?

That is stronger and more general than "information is lost by nightly collapse."

## Zero-displacement control

Without handling displacement, CHECK was close to the generating sigma at the cell-median level:

- maximum absolute median CHECK bias across the three true-sigma cells: 8.8%.

However, FIRST and LAST could still differ because collapsing nine field checks into three nightly occasions discards spatial recaptures and makes the representative detector stochastic. The maximum absolute median FIRST/CHECK difference across zero-displacement cells was 21.9%, and the maximum LAST/FIRST difference was 20.3%.

This is evidence that the aggregation choice can matter even without handling-induced displacement, but v1 had only eight replicates per cell and the smallest-sigma cell had low fit rate. These values should not be promoted as final performance estimates.

## Why v1 is not yet enough

The v1 parameter grid was deliberately broad, but its observation process was not tightly matched to the empirical held-out Cricetidae data. The closest v1 cell still had:

- simulated >=1-spacing shift fraction: 79.2%;
- empirical mean held-out value: 70.9%;
- simulated median first-to-last span: 10.67 m versus empirical all-repeat median target ~7.54 m.

Therefore v1 answers "can downstream sigma be sensitive?" but not yet the sharper question "under conditions that reproduce the observed San Jacinto capture process, how sensitive is sigma?"

## Frozen next step

`SAN_JACINTO_SCR_SIGMA_CALIBRATED_SIMULATION_DESIGN_V2.md` fixes a two-stage procedure:

1. choose three parameter cells using only repeat-capture frequency, >=1-spacing shift frequency and changed-night first-to-last distance;
2. generate independent replicates for those cells and only then fit CHECK/FIRST/LAST SCR sigma.

No sigma outcome enters the calibration step.

## Current paper implication

Figure 2 of manuscript v0.3 should eventually be replaced by the calibrated downstream simulation, not merely supplemented by it.

The old binomial/Wilson benchmark can remain as a small supplement or software-consistency test. The paper's main simulation should answer the decision consequence:

> When does a one-location-per-night reduction materially change the SCR spatial scale that an ecologist would report?
