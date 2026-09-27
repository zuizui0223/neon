# Oikos readiness — V4 HOLD

## Status

# HOLD — DO NOT SUBMIT V6

The V6 package is technically reproducible but failed a post-package mammal-ecology validity audit.

The pre-audit snapshot remains at:

`submission/oikos-v6-2026-09-27`

This branch is provenance only, not the recommended submission state.

## Why the hold was triggered

### Scale validity failure

Across 27 sites and 94 canonical adjacency worlds:

- **93/94** worlds connect every same-grid trap pair;
- **26/27** sites have complete within-grid adjacency even at the smallest canonical threshold;
- the remaining site, TOOL, still admits 99.394% of same-grid pairs at its smallest threshold.

Therefore the V6 within-grid null result is nearly forced by the geometry and is not an independent mammal-ecology mechanism finding.

### Biogeographic confounding

In the independent fresh 11-site panel, carrier turnover was compared against a null that fixed each site's eligible species pool and observed carrier count.

Observed mean carrier Jaccard = 0.03985; pool-conditioned null mean = 0.03102.

The one-sided probability of carrier overlap being lower than the null expectation was **p = 0.7568**.

Thus the raw median carrier Jaccard of zero does not establish carrier-specific turnover beyond ordinary species-pool turnover.

### Mammal-specific information loss

The response was collapsed to ever-positive species × trap incidence across the whole release, despite DP1.10072.001 providing mark-recapture identities, repeated bouts, trap-night effort, grid sampling type and identification uncertainty.

## Consequence for claims

Do not submit statements that:

- within-grid organization is negligible in small mammals;
- the 66/68 grid-conditioned result identifies an ecological mechanism;
- carrier turnover is unusually high after biogeography is controlled;
- trophic diversity of carriers demonstrates convergence beyond local pool composition;
- the old metric represents mammal movement or connectivity.

## Next scientific programme

See:

- `docs/MAMMAL_ECOLOGY_VALIDITY_AUDIT_V1.md`
- `docs/MAMMAL_ECOLOGY_REDESIGN_V1.md`

The next paper must use mammal-relevant within-grid scales, effort, repeated sampling, individual identity, taxonomy uncertainty and habitat information.

## Administrative submission state

Author metadata are **not the blocker anymore**.

The blocker is scientific redesign and validation.
