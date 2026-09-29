# San Jacinto SCR sigma sensitivity — estimability design v1

Date: 2026-09-29

Status: frozen before first-vs-last SCR sigma estimates are fitted.

## Focal species

- PEMA — Peromyscus maniculatus
- PEER — Peromyscus eremicus

These are the two held-out Cricetidae that independently confirmed strong intra-night positional aliasing.

## Source

Figshare article 18295520 v1, `year round trap data.csv`, SHA256 `ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301`.

## Session and occasion definitions

SCR session = species × grid × trapping bout.

Sampling occasion = distinct capture date within a bout, ordered chronologically.

Global trapping bouts are reconstructed from all source capture dates using the already-frozen rule: start a new bout when the gap between consecutive distinct dates exceeds 7 days.

Detector layout is the fixed 7×7 A1–G7 array at 6.25 m spacing.

## Effect-blind session support gate

Before sigma is fitted, session eligibility is determined from all valid raw detections without choosing first or last nightly location.

An eligible species × grid × bout session must have:

- at least 2 distinct sampling occasions;
- at least 10 unique individuals;
- at least 5 individuals detected on >=2 distinct occasions;
- at least 3 individuals with evidence of spatial recapture across different occasions, defined as having at least two dates whose observed raw trap-flag sets are not identical.

A species advances to sigma fitting only if it has >=5 eligible sessions across >=2 grids.

## Frozen one-location-per-night reductions

For each eligible session and individual × occasion:

- FIRST dataset: retain the earliest valid nocturnal capture;
- LAST dataset: retain the latest valid nocturnal capture;
- source-row order breaks exact time ties.

Both datasets must contain exactly the same eligible sessions, individuals and occupied occasions. They may differ only in TrapID.

## SCR model

Implementation: R package `secr`.

Capture-history format: one detection per individual per occasion.

Detector type: `multi`.

Detection function: half-normal (`HN`).

Likelihood: conditional (`CL = TRUE`) so the comparison targets the detection/spatial scale rather than density.

Model:
- g0 ~ b + grid + bout
- sigma ~ 1

Session covariates:
- grid = factor identifying the 1–8 source grid;
- bout = factor identifying the 1–12 trapping bout.

Habitat mask: trap-buffer mask with 100 m buffer, identical for FIRST and LAST.

Primary estimate for each species: one pooled sigma across all frozen eligible sessions.

## Frozen downstream-distortion metric

`sigma_ratio = sigma_LAST / sigma_FIRST`

`relative_change = (sigma_LAST - sigma_FIRST) / sigma_FIRST`

A practically material downstream effect is prospectively defined as:

- absolute relative change >= 10%.

The programme will classify the observed result as:

- `material_sigma_sensitivity_in_both_species` if both species exceed 10%;
- `material_sigma_sensitivity_in_one_species` if exactly one exceeds 10%;
- `sigma_sensitivity_below_10pct` if neither exceeds 10%.

This threshold is descriptive and cannot be changed after sigma is opened.

## Additional non-rescuing outputs

- FIRST and LAST sigma estimates with 95% CI;
- conditional log likelihood and AIC;
- number of sessions, animals, occasions, and spatially recaptured individuals;
- fit convergence / Hessian availability;
- sensitivity model without behavioural response: g0 ~ grid + bout, sigma ~ 1.

## Effect boundary

At this stage:
- species session-support counts inspected: false
- FIRST sigma inspected: false
- LAST sigma inspected: false
- sigma ratios inspected: false
- SCR models fit: 0
