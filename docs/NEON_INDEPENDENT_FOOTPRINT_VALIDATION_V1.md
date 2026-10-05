# NEON independent multi-night footprint validation v1

**Branch:** `ecology/neon-footprint-validation-v1`  
**Status:** Stage 0 support audit frozen before footprint-similarity outcomes are opened  
**Source:** NSF NEON Small Mammal Box Trapping, `DP1.10072.001`, `RELEASE-2026`

## Replication target

San Jacinto H4 found that multi-night trap-use footprints of conspecific individuals were more similar than those of heterospecific individuals after controlling for footprint size.

This branch asks one portable biological question:

> **Do species-specific recurring multi-night footprints also occur in an independent, continent-scale small-mammal dataset?**

The hypothesis and its direction were fixed from San Jacinto before any NEON individual-footprint overlap outcome is opened here.

## Independence and inferential status

NEON is independent of San Jacinto in geography, species composition, field crews, trap-grid design and study purpose. However, `RELEASE-2026` has already been used elsewhere in this repository for different coarse-scale endpoints. Therefore this branch is an **independent-dataset replication of the San Jacinto footprint hypothesis**, not a response-naive confirmatory test of all possible NEON ecology.

No prior NEON analysis in this repository has opened the individual-level conspecific-versus-heterospecific multi-night footprint-overlap endpoint used here.

## Fixed site universe

Use all 11 sites in the pre-existing response-blind frozen roster:

`SRER, STEI, STER, TALL, TEAK, TOOL, TREE, UKFS, WOOD, WREF, YELL`.

No site is added or removed on the basis of individual recapture outcomes.

## Stage 0 — support only

Before any footprint-overlap result is calculated, download and inventory the `mam_perplotnight` and `mam_pertrapnight` tables for the fixed sites and record only:

- file inventory, sizes and MD5 verification;
- table schemas;
- sampling-bout support from `eventID`;
- `mammalGridSamplingType` and `gridCompletion` availability;
- capture rows with non-empty `tagID`;
- taxon roster;
- number of distinct nights and trap coordinates per tagged individual within site × plot × eventID;
- number of multi-night individuals by taxon and unit;
- number of units containing at least two taxa with multi-night individuals;
- taxonomic inconsistency counts for tags assigned >1 taxon within a unit;
- uncertain/X trap-coordinate counts.

Stage 0 must not calculate:

- pairwise footprint overlap;
- conspecific-minus-heterospecific contrasts;
- footprint-assortativity Z scores;
- community C-scores;
- habitat associations;
- temporal persistence;
- species-pair effects.

## Capture/event construction

Join `mam_perplotnight` to `mam_pertrapnight` by `nightuid`.

A candidate capture record must:

- have `trapStatus` containing “capture” but not “no capture”;
- have non-empty `tagID`;
- have non-empty `taxonID`;
- have a canonical non-X `trapCoordinate`;
- map to a non-empty `eventID`.

A **multi-night individual** is a site × plot × eventID × tagID observed on at least two distinct `collectDate` values. Repeated use of the same trap still qualifies; Stage 0 reports distinct-trap counts but does not filter on them.

## Stage 1 boundary

Only after Stage-0 support is persisted will exact eligibility thresholds be frozen.

If support is adequate, Stage 1 will transfer the San Jacinto H4 test without searching alternatives:

- individual footprint = set of trap coordinates used across nights within one eventID;
- primary contrast = conspecific versus heterospecific footprint overlap within the same plot × event;
- null controls footprint size and unit;
- one global standardized statistic;
- one-sided positive test;
- equal-weight site-level robustness;
- no species-pair search if the global replication fails.

A null result is retained as failure of generalization.


---

# Stage 0 result

Support is ample for a strict transfer of the San Jacinto H4 test:

- 47,355 joined tagged capture rows;
- 9,020 multi-night individual × plot × event histories;
- 1,003 units with at least one multi-night individual;
- 678 units with at least two taxa represented by multi-night individuals;
- 357 units with at least three taxa represented by multi-night individuals.

There are 360 tag × unit histories with more than one taxon assignment. These are excluded from Stage 1 rather than resolved post hoc.

No footprint-overlap outcome was opened in Stage 0.

# Stage 1 — frozen independent footprint-assortativity replication

## Direct transfer from San Jacinto H4

The following choices are copied from the frozen San Jacinto individual-footprint test and are not tuned on NEON overlap outcomes:

- minimum distinct capture nights per individual: **2**;
- individual footprint: set of distinct trap coordinates used within site × plot × eventID;
- minimum multi-night individuals per species in a unit: **3**;
- minimum eligible species per unit: **3**;
- pair similarity: **Jaccard**;
- unit statistic: mean conspecific Jaccard minus mean heterospecific Jaccard;
- null: permute species labels only within **exact footprint-size strata** inside each unit;
- Monte Carlo permutations: **10,000**;
- direction: positive;
- alpha: **0.05**.

## Species and identity rule

Only records whose current `taxonRank` is exactly `species` enter the species-specific test. Species-group, genus, family and other coarser identifications are excluded.

Within a site × plot × eventID × tagID history, any tag assigned more than one species-level taxonID is excluded as taxonomically inconsistent. No majority-rule reassignment is allowed.

Only canonical non-X trap coordinates and non-empty eventID histories enter.

## Unit eligibility

A unit is site × plot × eventID.

Within each unit, retain species with at least three eligible multi-night individuals. The unit is analyzed only if at least three species remain.

This is deliberately the same support threshold as San Jacinto, despite NEON's much larger sample.

## Primary cross-system replication statistic

For each eligible unit (u), let (D_u) be the observed conspecific-minus-heterospecific Jaccard contrast. From the 10,000 within-size-stratum label permutations obtain its null mean (mu_u) and SD (sigma_u), and define

[
Z_u=(D_u-mu_u)/sigma_u.
]

Units with zero null SD are reported but do not contribute to standardized aggregation.

To avoid pseudo-replication from many bouts at the same physical site:

1. average (Z_u) across informative units within each NEON site to obtain (ar Z_s);
2. define the global statistic as the **equal-site mean** of (ar Z_s);
3. construct the Monte Carlo null by applying the identical unit standardization to every permutation replicate, averaging within site, then averaging equally across sites.

Primary replication requires:

- at least **6 informative physical sites**;
- global equal-site statistic (T>0);
- one-sided Monte Carlo (p<0.05).

## Required physical-site robustness

As a second, predeclared gate, perform an exact one-sided sign-flip test on the observed site means (ar Z_s), enumerating all (2^S) sign assignments.

A **strong independent replication** requires both:

- the primary equal-site Monte Carlo test to pass; and
- exact site sign-flip (p<0.05).

If the Monte Carlo test passes but the site sign-flip does not, report `unit_level_signal_without_site_robustness`, not successful generalization.

## Fixed secondary summaries

Report without additional hypothesis search:

- eligible/informative units and sites;
- total eligible multi-night individuals;
- footprint-size distribution;
- number and fraction of eligible units with raw (D_u>0);
- site mean Z values;
- unit-weighted global mean Z for direct numerical comparison with San Jacinto;
- results separately summarized by `mammalGridSamplingMethod`, descriptively only if the field can be assigned unambiguously at unit level.

No species-pair decomposition, habitat split, alternative overlap metric, alternative taxon grouping, or threshold search is opened after Stage 1.

## Claim if both gates pass

> **Across an independent standardized North American small-mammal network, individuals of the same species repeatedly use more similar multi-night trap-use footprints than individuals of different species, even after exact control for footprint size.**

This would replicate the organizational scale identified at San Jacinto, not the original San Jacinto species composition or mechanism.
