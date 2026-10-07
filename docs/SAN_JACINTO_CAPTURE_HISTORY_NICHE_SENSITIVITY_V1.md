# San Jacinto capture-history niche sensitivity v1

Date: 2026-10-07

## Ecological question

Does within-night capture history propagate into the published community-level inference about spatial partitioning and temporal activity overlap?

This is deliberately different from the temporal-aliasing methods paper. The response is ecological: the original Chock et al. analysis included all captures, including recaptures, when constructing spatial C-score and temporal Czekanowski matrices.

## Contrast

Two representations are compared on the same six focal species and 32 grid-seasons:

1. **ALL** — the original-style representation using all capture rows.
2. **FIRST-ONLY** — retain the earliest capture per identifiable individual × grid × night; later within-night recaptures are removed. Records without a resolvable individual identity are retained rather than guessed to be recaptures.

FIRST-ONLY is a sensitivity representation, not a reconstruction of undisturbed behavior.

## Null models

Use EcoSimR directly, matching the published methods:

- spatial: `cooc_null_model(..., algo="sim9", metric="c_score")`;
- temporal: `niche_null_model(..., algo="ra3", metric="czekanowski")`.

Both lanes use the same Monte Carlo replication count and deterministic but independent seeds.

## Primary readout

For each of 32 grid-seasons:

- spatial C-score SES and classification;
- temporal Czekanowski SES and classification;
- whether classification changes between ALL and FIRST-ONLY.

The first scientific question is not whether one lane has a smaller p-value. It is whether the published ecological direction—spatial segregation and temporal overlap—depends materially on repeat captures of the same individuals within a night.

## Claim boundary

This is post-result ecological sensitivity. It does not identify handling, scent, trap attraction or release-site persistence as the cause. A positive sensitivity would show propagation of capture history into community inference, not a specific behavioral mechanism.
