# NEON external spatial-template feasibility — V1

**Status:** support-only external replication screen; RELEASE-2026 is already response-consumed development data  
**Parent biological result:** San Jacinto Stage 9  
**Data product:** NEON Small Mammal Box Trapping, DP1.10072.001, RELEASE-2026

## Purpose

The San Jacinto analysis suggests that fine-scale species × place structure can recur after every marked individual shared between compared time windows is excluded. The next scientifically useful step is an **independent field system**, not another endpoint from San Jacinto.

NEON provides a standardized mark–recapture design with tagged individuals, trap coordinates, sampling-bout identifiers and repeated multi-night trapping. This screen asks only whether a previously fixed, geographically distributed set of NEON sites contains enough support to attempt the same identity-exclusion recurrence test.

Because DP1.10072.001 RELEASE-2026 has already been opened elsewhere in this repository, any later ecological effect estimated from it is **exploratory external replication**, not confirmatory evidence. A future NEON release not contained in RELEASE-2026 remains the confirmatory target.

## Fixed site panel

Use the 11 sites already selected response-blind for the independent carrier-mechanism programme, before the present spatial-template question was formulated:

`SRER, STEI, STER, TALL, TEAK, TOOL, TREE, UKFS, WOOD, WREF, YELL`.

No site may be added or removed after this feasibility screen on the basis of species × place recurrence.

## Data tables and fields

Use the basic-package tables:

- `mam_perplotnight`: `nightuid`, `plotID`, `collectDate`, `eventID`, `mammalGridSamplingType`;
- `mam_pertrapnight`: `nightuid`, `plotID`, `collectDate`, `trapCoordinate`, `trapStatus`, `taxonID`, `tagID`.

Join tables by `nightuid`.

Use only official NEON **target** small-mammal species from the current taxonomy endpoint.

## Identity rule

For the external replication, an individual must have a non-empty `tagID`. Untagged captures and `individualCode`-only records are retained only in file/quality counts and cannot establish shared or disjoint identity across bouts.

Within a site, a tag observed with more than one target-species `taxonID` is treated as taxonomically ambiguous and excluded from the identity-based support screen.

## Spatial and sampling rule

Use only canonical trap coordinates matching `[A-Z][0-9]+`; coordinates containing `X` are excluded.

Use only sampling records classified as **pathogen** grids because those grids are normally sampled for three consecutive nights per bout; diversity grids are normally one-night samples and cannot estimate a multi-night footprint comparably.

A plot × event is usable only if it contains at least **two distinct trapping nights** with tagged target-species captures after the rules above.

## Adjacent-bout comparison

Within each physical `plotID`, order usable pathogen-grid events by their first collection date. Candidate comparisons are only immediately adjacent usable events.

For each adjacent pair:

1. identify every tagged individual observed in both bouts and remove it from both;
2. for each species, count the remaining bout-A-exclusive and bout-B-exclusive tagged individuals;
3. a species is eligible only if it retains at least **2 exclusive tagged individuals in each bout**;
4. a comparison unit is eligible only if at least **3 target species** satisfy that rule.

This exactly mirrors the identity-support threshold used by San Jacinto Stage 9, while adapting seasons to NEON sampling bouts.

## Feasibility output — outcomes that may be opened now

The support screen may report only:

- downloaded file / row counts and schema checks;
- target-capture and tagged-target-capture counts;
- ambiguous-tag and noncanonical-coordinate exclusions;
- number of usable pathogen plot-events;
- number of adjacent-bout candidate pairs;
- numbers of shared tagged identities removed;
- exclusive individual counts by species;
- number of eligible species per pair;
- number of eligible adjacent-bout units, physical plots and sites.

It must **not** calculate:

- observed species × trap recurrence;
- any trap-overlap statistic;
- C-score or checkerboard structure;
- a spatial null distribution;
- standardized recurrence effects;
- effect direction or p-values.

## Advance rule

An exploratory external recurrence test is authorized only if the support screen yields at least:

- **12 eligible adjacent-bout units**;
- distributed across at least **6 physical NEON sites**;
- and at least **8 distinct physical plots**.

Otherwise this external route stops.

## Frozen effect test if support passes

If the support gate passes, the next script may be implemented without changing the endpoint:

- representation: all valid tagged target-species capture traps within each three-night pathogen bout;
- shared-identity rule: remove every tagged individual observed in both adjacent bouts from both;
- eligible species/unit: exactly the support rules above;
- observed statistic: matched species × trap incidence between bout A and bout B;
- null: bout A fixed; bout B randomized by a fixed-fixed curveball preserving bout-B species trap-occupancy totals and trap species-richness totals;
- 10,000 null replicates after 500 burn-in swaps;
- unit effect: standardized recurrence (Z);
- primary aggregation: equally weight physical plots first, then sites, so plots or repeated bout pairs from one site cannot dominate;
- primary direction: positive recurrence;
- site-level robustness: report number of positive site means and an exact sign-flip p-value when the number of informative sites permits it.

Because RELEASE-2026 is development data, even a passing result will be labelled **exploratory cross-system replication**. No failed result may trigger species-pair selection, alternative overlap metrics, relaxed identity thresholds or non-adjacent bout searches.

## Biological interpretation if later supported

The external result would not establish a shared causal mechanism between San Jacinto and NEON. It would show that **species × trap recurrence across disjoint observed identity sets is not unique to one rodent guild or one trapping design**, materially increasing empirical generality of the spatial-template phenomenon.
