# Wisconsin independent multi-night footprint validation v1

**Branch:** `ecology/wisconsin-footprint-validation-v1`  
**Status:** Stage 0 feasibility audit frozen before any footprint-assortativity or temporal-persistence outcome is opened  
**Independent source:** Jolly & Pauli (2024), Dryad DOI `10.5061/dryad.zpc866thw`

## Why this dataset

The San Jacinto analysis localized community spatial partitioning to recurring multi-night space-use footprints rather than within-night movement direction or one point-like seasonal centre. An independent system is needed before making a broader ecological claim.

The Wisconsin dataset is suitable in design because it contains:

- 9-day live-trapping sessions;
- 25 fixed traps in a 5 × 5 grid at each site;
- individual marking;
- initial capture date and trap;
- up to eight recapture dates and traps;
- multiple small-mammal species;
- replicated sites, forest types, seasons and years.

It is independent of the San Jacinto study in geography, habitat, sampling design and species composition.

## Independent validation question

> **Do species-specific recurring multi-night footprints emerge in a second small-mammal community?**

The primary target is the individual-footprint result, because it is the most portable biological component of the San Jacinto evidence chain and does not require matching the original San Jacinto community C-score design.

## Stage 0 — feasibility only

Before any overlap, assortativity, persistence or community-structure outcome is computed, record only:

1. Dryad file inventory and checksum;
2. raw column names and wide recapture schema;
3. species roster;
4. sites, seasons and session identifiers;
5. reconstructed capture-event counts;
6. individually identifiable animals;
7. number of distinct capture nights per individual;
8. number of distinct traps per individual;
9. counts of multi-night individuals by species × site × season/session;
10. number of units containing at least two species with multi-night individuals.

Stage 0 must **not** calculate:

- within-individual footprint overlap;
- conspecific-versus-heterospecific overlap;
- C-scores or co-occurrence nulls;
- early-versus-late persistence;
- turnover persistence;
- species-pair effects;
- habitat-specific outcome contrasts.

## Identity rule

Each wide row in `CaptureMaster.csv` represents an initially captured animal and its within-session recaptures. For rodents with ear tags, the row itself is treated as the individual capture history represented by that record. Records flagged `Remove == 1` are excluded from future inferential analyses.

Stage 0 reports marked/unmarked support explicitly and does not silently infer cross-row identity from incomplete tag fields.

## Candidate Stage 1, to be frozen only after Stage 0 support counts

If support is adequate, the primary independent validation will ask whether individual multi-night trap-use footprints are more similar within species than between species while controlling exactly for footprint size, using the same conceptual null family as the San Jacinto footprint-assortativity test.

Eligibility thresholds and the exact unit definition will be frozen from Stage-0 support only, before any footprint-overlap outcome is opened.

## Success standard

This branch is not allowed to rescue the San Jacinto result by searching metrics.

A successful independent validation must use:

- one predeclared footprint metric;
- one predeclared null;
- one primary global statistic;
- physical site-level robustness;
- no species-pair search if the global test fails.

A null result is retained as a genuine failure of generalization.
