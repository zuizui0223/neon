# Temporal-aliasing diagnostic — simulation benchmark plan v1

Date: 2026-09-29

Purpose: evaluate the generic diagnostic independently of the San Jacinto empirical values.

## Data-generating process

For each simulated individual-night:
- latent first position is arbitrary and irrelevant to the span threshold;
- latent last position differs by a 2-D Gaussian shift with component SD `shift_sigma`;
- material spatial scale is fixed to 1 simulation unit;
- the latent material event is first-to-last Euclidean span >=1.

## Observation process

Only nights with repeated observations expose the first-to-last span.

Three repeat-observation mechanisms are compared:
- MCAR: repeat probability independent of span;
- span-enriched: larger spans increase repeat-observation probability;
- span-depleted: larger spans decrease repeat-observation probability.

The latter two are deliberate failure modes. The method does not claim that repeat-capture-conditioned proportions identify latent all-night movement when repeat observation is informative.

## Parameter grid

- n nights: 100, 500
- shift_sigma/material_scale: 0.25, 0.5, 1.0, 2.0
- baseline repeat probability: 0.25, 0.5, 0.75
- repeat-span slope beta: -1, 0, +1
- 400 replicates per cell

## Outputs

For each cell:
- latent material-shift fraction;
- repeat-conditioned observed fraction;
- bias of repeat-conditioned fraction;
- Wilson 95% coverage for the latent fraction;
- all-night directly observed lower-bound fraction;
- frequency with which that lower bound exceeds the latent fraction (must be zero up to floating precision);
- mean number of repeat-observed nights.

## Interpretation

Under beta=0, repeat-observed nights are a random subsample and the conditional fraction should be approximately unbiased with near-nominal Wilson coverage.

Under beta != 0, the conditional fraction is allowed to be biased. This is a feature of the observation process, not a defect the diagnostic claims to correct.

The all-night directly observed fraction remains a lower bound regardless of the repeat-observation mechanism because it counts only material shifts that were actually exposed by repeated observation.
