# Trap-mediated niche robustness protocol v1

Date: 2026-10-07

Status: **frozen after discovery outcomes were opened, before the robustness outcomes below are inspected.**

## Discovery outcomes already opened

The following San Jacinto results are exploratory and cannot be presented as preregistered confirmation:

- all six focal species showed excess same-species succession at the same detector from one within-night check to the next;
- the excess partly persisted for different known conspecific individuals in DKR, PEMA and SKR;
- dominant kangaroo rat (DKR or SKR) -> LAPM same-detector transitions were below a trap × trapping-bout × check-pair date-shuffle reference, whereas LAPM -> kangaroo rat transitions were approximately null;
- censoring identifiable post-first-capture records reduced raw Czekanowski temporal overlap in most grid-seasons but did not reveal coarse early/middle/late temporal segregation in the preliminary RA3-style sensitivity.

These outcomes motivated, but do not determine, the tests below.

## Ecological question

Does the exploratory kangaroo-rat -> LAPM deficit behave like a highly local trap-history effect, or like a broader short-term spatial avoidance response?

The working interpretation is **trap-mediated interaction history**, not proven natural interference competition. Capture/release, residual odour, bait state, local activity and natural avoidance can all contribute.

## Frozen robustness tests

### R1. Spatial decay around the previous kangaroo-rat detector

For each focal trap and date, compare whether LAPM is observed at the next check at:

1. the same trap (distance 0);
2. an orthogonally adjacent trap (Manhattan distance 1 trap spacing);
3. Manhattan-distance-2 traps.

For each distance class, the reference permutes next-check outcomes among dates within **grid × focal trap × trapping bout × check pair**, preserving fixed local habitat, trap identity, bout-scale abundance and check position.

Primary contrast: observed / expected probability of at least one LAPM in the distance class after DKR/SKR occupancy of the focal trap.

Interpretation frozen before opening:
- strongest deficit at distance 0 only: more consistent with trap-specific history/odour or exact-site avoidance;
- deficit extending to adjacent traps: more consistent with local spatial avoidance around the dominant animal's recent location;
- no reproducible deficit outside the focal trap: do not generalize the same-trap result to natural neighbourhood avoidance.

### R2. Temporal decay

Estimate separately:
- EARLY -> MIDDLE;
- MIDDLE -> LATE;
- EARLY -> LATE.

Use the same trap × bout date-shuffle reference.

Interpretation:
- similar immediate effects in both adjacent check pairs support repeatability;
- attenuation by EARLY -> LATE supports a short-lived response;
- effect confined to only one check pair is weaker evidence and should be reported as heterogeneous.

### R3. Grid leave-one-out robustness

Recompute the KR -> LAPM same-trap observed/expected ratio after excluding each of the eight grids in turn.

Binding descriptive rule:
- report the full range;
- call the direction robust only if all eight leave-one-grid-out ratios remain <1.

### R4. Trapping-bout cluster bootstrap

Resample grid × trapping-bout blocks with replacement, retaining all traps/dates/checks in a sampled block. Use 20,000 replicates and seed 20261007.

Report percentile 95% intervals for:
- KR -> LAPM same-trap O/E;
- LAPM -> KR same-trap O/E;
- their log-ratio asymmetry contrast.

This is exploratory uncertainty, not a preregistered hypothesis test.

### R5. Directed-species matrix multiplicity audit

Compute the 6 × 6 directed species transition matrix under the same date-shuffle reference. Report standardized residuals and Benjamini-Hochberg FDR across the 30 heterospecific directed pairs.

The previously opened KR -> LAPM contrast remains hypothesis-motivated exploratory evidence and is not reclassified as confirmatory if it passes FDR.

### R6. Same-species identity decomposition

For each species, separate same-species succession into:
- same known individual;
- different known individual;
- unresolved identity.

The ecological interpretation of conspecific attraction/social aggregation is allowed only where the **different-known-individual** excess is directionally robust.

## Community-level propagation sensitivity

The original Chock et al. temporal-overlap analysis used all capture events including recaptures. Compare it with a representation retaining only the first identifiable capture per individual × grid × date, while retaining unknown-ID rows in the primary sensitivity.

Before claiming a changed community conclusion, reproduce the original temporal null procedure closely enough that the all-capture representation recovers the published qualitative endpoint (no temporal segregation and several cases of aggregation). Any discrepancy in the exact count of significant grid-seasons must be disclosed.

## Claim boundary

No robustness result may be described as:
- proof that residual scent caused the pattern;
- proof of natural direct encounters between species;
- proof of interference competition;
- a prospectively confirmed effect.

The strongest admissible ecological language is:
> Fine-scale trap-mediated sequence structure is consistent with short-term local avoidance by subordinate LAPM after kangaroo-rat occupancy, even though coarse whole-night activity niches remain overlapping.

