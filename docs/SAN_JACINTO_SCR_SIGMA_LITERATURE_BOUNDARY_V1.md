# Literature boundary — nightly collapse and SCR sigma v1

Date: 2026-09-29

## What standard SCR input assumes

The standard `secr` capture-history format is Session–AnimalID–Occasion–TrapID. For exclusive physical-trap detector types, only one detection is allowed per animal per occasion. The package verification/update machinery discards or rejects supernumerary within-occasion detections for exclusive detector types.

Current `secr` documentation also distinguishes detector classes: physical traps detain an animal and therefore produce at most one detection per animal per occasion, whereas proximity/count detectors may record repeated within-occasion detections.

Thus, when a field protocol yields repeated captures of the same animal within one nominal night but the analysis defines a night as one SCR occasion, the analyst must reduce those captures to one detector state or redefine the occasion/detector model.

## Small-mammal examples

Published small-mammal SCR studies commonly use consecutive nights/days as capture occasions.

- Romairone et al. (2018, PLOS ONE 13:e0198766) used live-trapped common voles in an SCR model. Their sessions comprised consecutive trapping days treated as capture occasions even though traps were checked twice per day.
- Bias et al. / salt-marsh harvest mouse long-term SCR work treated consecutive trapping nights as capture occasions in a 10×10 Sherman-trap grid.

These examples establish that collapsing repeated within-day/night handling records into a single occasion-level capture history is not a contrived downstream analysis; it is compatible with standard small-mammal SCR practice.

## Why compare sigma

In half-normal SCR, sigma is the spatial detection scale governing the decline in detection probability with distance from the latent activity centre and is routinely interpreted as a space-use / movement-scale parameter.

The present sensitivity analysis asks:

> Holding the animals, sessions, detector grid, SCR model, and occasion definition fixed, how much does estimated sigma change if each repeat-capture night is represented by the first versus the last observed trap location?

## Scope boundary

This is not a test of which first/last rule is biologically correct. Both are deliberately plausible one-location-per-night reductions of the same raw repeated-check data.

The target is the **downstream inferential sensitivity caused by temporal collapse**.

References used for this boundary:
- Borchers et al. 2014, Methods in Ecology and Evolution 5:656–665, DOI 10.1111/2041-210X.12196.
- Efford 2019, Methods in Ecology and Evolution 10:1529–1535, DOI 10.1111/2041-210X.13239.
- Romairone et al. 2018, PLOS ONE 13:e0198766.
- current `secr` read.capthist / detector / multisession documentation.
