# Literature boundary — nightly collapse and SCR sigma v1

Date: 2026-10-03

## What standard SCR input assumes

The standard `secr` capture-history format is Session–AnimalID–Occasion–TrapID. Current `secr` documentation distinguishes single-catch, multi-catch, proximity and count detector types. For trap-based binary/multinomial histories, an animal contributes at most one detector state per occasion; proximity/count detectors allow different within-occasion observation structures.

Thus, when a field protocol yields repeated captures of the same animal within one nominal night but the analysis defines a night as one SCR occasion, the analyst must reduce those captures to one detector state or redefine the occasion/detector model.

## Small-mammal example showing nightly/day-level collapse is realistic

Romairone et al. (2018, PLOS ONE 13:e0198766) used live-trapped common voles in an SCR model. Their trapping periods contained eight capture occasions defined by trapping days, while traps were checked twice per day (09:00 and 16:00) and animals were released where captured.

This establishes that a day/night-level SCR occasion despite repeated trap checks is not a contrived downstream analysis. It is an explicit published small-mammal SCR design.

## The expected objection: why not make each check an occasion?

That is a legitimate alternative and should not be dismissed. If traps are reset and an animal is again available for capture, each check interval can in principle be represented as a finer occasion.

However, redefining the occasion does two things at once:

1. it retains more temporal information;
2. it changes the biological observation model by treating post-release detections as repeated observations under the fitted SCR process.

The second point matters when capture, handling or release changes short-term spatial state or detectability. A finer occasion definition does not by itself guarantee that a static activity-centre / half-normal SCR model is now correctly specified.

Borchers et al. (2014) made the broader point for SECR that temporal aggregation can discard information and that estimates can be sensitive to occasion length when detections are spatiotemporally correlated. Their continuous-time treatment is primarily developed for continuously sampling proximity detectors, but the general warning is relevant here: changing temporal resolution does not eliminate dependence created by movement.

Therefore the post-stop simulation compares three representations of the same repeated-check process:

- FIRST capture per night;
- LAST capture per night;
- each check as an occasion.

The check-level representation is treated as a competing analysis, not as an oracle.

## Why compare sigma

In half-normal SCR, sigma is the spatial detection scale governing the decline in detection probability with distance from the latent activity centre and is routinely interpreted as a space-use / movement-scale parameter.

The downstream question is:

> Holding the detector geometry and fitted static SCR form fixed, how much can estimated sigma change solely because repeated within-night detections are represented differently?

The simulation includes a zero post-release-displacement control and then increases capture-associated displacement across a trap-scale range. This directly tests when the representation choice becomes materially consequential.

## Scope boundary

The empirical San Jacinto sigma gate remains stopped; no confirmatory FIRST/LAST sigma was opened because both held-out species did not meet the frozen support gate.

The simulation does **not** establish that handling caused the observed San Jacinto first-to-last movements. It asks a narrower methods question: if capture-associated state change exists at plausible trap-scale magnitudes, can nightly collapse or finer-occasion recoding materially change downstream sigma?

References used for this boundary:
- Borchers et al. 2014, Methods in Ecology and Evolution 5:656–665, DOI 10.1111/2041-210X.12196.
- Efford & Boulanger 2019, Methods in Ecology and Evolution 10:1529–1535.
- Romairone et al. 2018, PLOS ONE 13:e0198766.
- current `secr` detector / capture-history documentation.
