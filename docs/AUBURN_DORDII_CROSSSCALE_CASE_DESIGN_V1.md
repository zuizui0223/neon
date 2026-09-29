# Auburn D. ordii cross-scale case study — estimability design v1

Date: 2026-09-29

Status: frozen before appendix support counts are opened.

## Role

This is a **single-population mechanistic case study**, not a replacement for multi-site external replication.

The same Nebraska population is represented in Appendix 2 (three-night live trapping) and Appendix 4 (short-term burrow use), and tag IDs overlap between the tables.

## Seasons

Only Summer 2006 and Summer 2007 are eligible because both trapping and burrow-use appendices are available for those summers.

## Sex reconstruction

The PDF-to-text companion corrupts the printed Sex symbols as `?`. Those symbols are not used.

Analysis is restricted to adults whose reproductive condition identifies sex unambiguously:
- male: scrotal or non-scrotal;
- female: estrus, pregnant, lactating, lactating/pregnant, post-lactating, or post-lactating+estrus;
- non-reproductive or otherwise ambiguous adults are excluded.

This rule is frozen before support counts are calculated.

## One-night population configuration

Appendix 2 records a fixed trap location per captured animal and X/- capture history over three nights on a 1-ha grid of 100 Sherman traps at 10 m spacing.

For each summer × night, a primary configuration is estimable only with N_male>=3 and N_female>=3 among adult sex-diagnostic D. ordii.

At least two usable nights are required in **each** summer.

If effects are later authorized, the primary population statistic is MPD_male - MPD_female standardized against an exact sex-label permutation over the pooled captured focal animals for that night. Because trap type and bait are uniform in this appendix design, no detector-stratum adjustment is needed.

## Individual short-term space-use breadth

Appendix 4 reports the number of burrows used during 4 nights and 7 nights. The primary individual endpoint is **number of burrows used during 4 nights**, because it is consistently defined and closest in temporal scale to the capture session.

Each summer requires at least 3 adult sex-diagnostic individuals of each sex with a recorded 4-night burrow count.

Distances among burrows are not a primary endpoint because the appendix distances can reflect the longer tracked sequence and are not guaranteed to correspond exactly to the first four nights.

## Linkage gate

Tag IDs in Appendix 2 are matched to Appendix 4 IDs within summer. Each summer must contain at least 2 linked adult sex-diagnostic males and 2 linked adult sex-diagnostic females.

This ensures the two spatial scales are not merely from the same population but share identifiable individuals.

## Advance rule

Both summers must pass all three gates:
1. packing nights;
2. 4-night burrow-use sample;
3. individual tag linkage.

Failure -> `stop_auburn_case_not_estimable`.

Pass -> `authorize_auburn_case_effect_lock`, followed by a second lock before any sex effect is calculated.

## Current status

- species/sample counts inspected: false
- sex-specific support counts inspected: false
- packing effects inspected: false
- burrow-use effects inspected: false
- ecological effect models fit: 0
