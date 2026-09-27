# Project boundary

## Current scientific mainline

The repository is no longer submission-led.

The active goal is a **small-mammal population and within-grid space-use analysis** using NEON mark-recapture structure, repeated sampling, effort, individual identity, taxonomic uncertainty and habitat.

See:

- `docs/MAMMAL_ECOLOGY_VALIDITY_AUDIT_V1.md`
- `docs/MAMMAL_ECOLOGY_REDESIGN_V1.md`

## Archived coarse-scale endpoint

The original 16-site and fresh 11-site programmes are closed and auditable.

Their endpoint asks whether every positive trap has another positive trap within a site-specific structural adjacency threshold.

A post-package geometry audit showed that those thresholds are overwhelmingly coarser than the mammal-grid geometry:

- 93/94 canonical worlds connect every same-grid trap pair;
- 26/27 sites do so even at the smallest threshold.

The endpoint is therefore retained as a coarse **grid-allocation / no-isolated-occurrence** result, not as a measure of mammal-scale movement or within-grid spatial organization.

## Carrier-turnover boundary

Raw carrier-set Jaccard near zero is not a current ecological claim.

In the independent fresh 11-site panel, a species-pool-conditioned null found no evidence that carrier overlap was lower than expected from site species pools and carrier counts (p = 0.7568).

The original 16-site response is not reopened to rescue this claim.

## Theory boundary

The closed programmes do not falsify spatial-insurance theory and do not establish habitat filtering, dispersal, demographic coupling or functional redundancy.

## Submission boundary

The V6 Oikos package is on **HOLD**.

The branch `submission/oikos-v6-2026-09-27` preserves the pre-audit state for provenance only.

Author metadata are not the current blocker; scientific redesign is.

## Data boundary for the redesign

RELEASE-2026 is treated as response-consumed development data.

Any future confirmatory test must use previously unseen small-mammal observations obtained only after the final mammal-scale protocol and analysis code are frozen.

## Out of scope

- generic EOG framework development
- world-survival identifiability Paper C
- NEON camera-trap work
- relabelling the closed carrier/cohesion programme as mammal movement ecology
