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
