# NEON small-mammal ecology

Independent repository for the NEON small-mammal ecological programme.

## Current status: SUBMISSION HOLD

**Do not submit V6 to Oikos in its current form.**

The pre-audit V6 snapshot is preserved at:

`submission/oikos-v6-2026-09-27` → `d7c24907bd6bb3f64905c0052141e537706d1792`

It is retained for provenance only.

The active scientific state is the post-package mammal-ecology validity audit and redesign:

- `docs/MAMMAL_ECOLOGY_VALIDITY_AUDIT_V1.md`
- `docs/MAMMAL_ECOLOGY_REDESIGN_V1.md`
- `submission/OIKOS_READINESS_V4_HOLD.md`
- `results/mammal_ecology_validity_audit_v1.json`

## Why V6 is on hold

### 1. The adjacency scale collapses within-grid mammal geometry

A metadata-only audit reconstructed all 27 sites from the two frozen response programmes.

Across **94 canonical adjacency worlds**, **93/94** made every same-grid trap pair adjacent.

At the smallest threshold:
- **26/27 sites** already had 100% same-grid pair adjacency;
- TOOL, the sole exception, still had **99.394%**.

Observed within-grid maximum trap separation was about **127 m**, whereas minimum canonical thresholds ranged from **112.6 to 1569.7 m**.

Therefore the former result “within-grid organization ≈ 0” is predominantly a consequence of the declared geometry, not an independent biological result about small mammals.

### 2. Carrier turnover is not independent of biogeography

In the independent fresh 11-site panel:

- species-pool Jaccard median = **0**;
- carrier Jaccard median = **0**;
- 35/55 site pairs shared no eligible species at all.

A null that fixed each site's eligible species pool and observed carrier count gave:

- observed mean carrier Jaccard = **0.03985**;
- null mean = **0.03102**;
- null 95% interval ≈ **0.00835–0.06948**;
- p for carrier overlap being lower than the pool-conditioned null = **0.7568**.

Thus raw carrier-set turnover does not establish carrier-specific taxonomic replacement beyond ordinary species-pool turnover.

### 3. The response discarded mammal-specific information

The old analyses reduced DP1.10072.001 to ever-positive species × trap incidence across RELEASE-2026.

The NEON product is designed around mark-recapture and repeated sampling, including:
- individual identities;
- repeated bouts;
- trap nights;
- grid sampling type;
- survey completeness;
- taxonomic identification qualifiers/history;
- habitat-linked grid placement.

Those variables now define the next scientific mainline.

## New mammal-ecology mainline

Primary question:

> **Within the same small-mammal species, how does within-grid space use vary among sites, years and habitats after sampling effort and local population size are accounted for?**

The redesign uses:
- within-grid scales of 10, 14.14, 20 and 30 m;
- species × grid × year/bout units;
- active trap-night effort;
- individualID / recapture histories;
- abundance or density estimation;
- `identificationQualifier` and identification history;
- `nlcdClass` and declared habitat covariates.

RELEASE-2026 is already consumed and may be used only for retrospective development. Confirmatory validation must use future, previously unseen NEON small-mammal observations after the final model is frozen.

## Historical V6 result

The original 16-site and independent 11-site programmes remain fully reproducible historical results. They are useful as a negative design lesson:

> response-blind freezing and perfect auditability do not guarantee that the frozen estimand is biologically informative at the scale of the target organism.

They are no longer the active manuscript claim.

## Project boundary

- **Active:** mammal-scale population / space-use redesign
- **Archived:** V6 local-cohesion submission package
- Paper B: deferred
- world-survival/EOG methods work: outside this repository
- NEON camera-trap programme: excluded

Historical `eog.*` schema names remain in immutable provenance where needed.
