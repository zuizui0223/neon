# Trap-mediated niche analysis — exploratory v1

Status: post-hypothesis exploratory study, separate from the held-out MEE aliasing-paper programme.

## Ecological question
Does the species previously caught at a trap predict the species caught at its next check, beyond species abundance and persistent trap affinity? Does removing later within-night recaptures change published estimates of community temporal niche overlap?

## Data and scope
Public source Chock et al. 2022, Figshare DOI 10.6084/m9.figshare.18295520.v1. Original CSV checksum pinned. Eight 7x7 grids, three time_bin categories (early, middle, late). Main trap-transition lane uses only grid-dates in which all three check bins had at least one recorded capture somewhere in the grid. This is a *capture-supported subset*, not a verified effort-complete sample.

A trap/check with no recorded capture on such a grid-date is represented as EMPTY. All duplicate trap/check cells and rare/unrecognized species are excluded from transition pairs touching them. Six focal species are CHFA, DKR, LAPM, PEMA, PEER and SKR.

## Outcomes frozen before looking at transition results
1. Adjacent-check seven-state matrix, EMPTY + six focal species.
2. Distinguish same-individual recurrence from other conspecifics and heterospecific succession. Individual matching uses nonmissing IDs and is imperfect.
3. Pre-specified focal contrast: kangaroo rats DKR+SKR followed by pocket mice CHFA+LAPM, and SKR followed by CHFA.
4. Null A (499 replicates): shuffle next-check state across traps within each grid/date/check pair, preserving species totals and sampling period, but **not** trap-specific suitability.
5. Null B (499 replicates): shuffle next-check nights via derangements within grid × monthly trapping bout, preserving the same trap location and check pairing; excludes bouts with only one supported grid-night. This controls stable site preferences better, though not dynamic night-specific factors.

## Reanalysis of published ecological endpoints
Independently, reconstruct 32 grid-season mean pairwise Czekanowski temporal overlaps from all captures (published representation) and compare with earliest check per identifiable individual-night. Repeat the authors' RA3 concept (row-wise bin-label permutation, 999 iterations per grid-season) and check whether the original 7/32 temporal-aggregation and 0/32 segregation counts are approximately reproduced. If not reproduced, do not claim overturning the original paper. Report unstandardized spatial C-scores descriptively only; the published spatial test used a different fixed-fixed SIM9 null not reproduced in this route.

## Non-negotiable boundaries
Capture at a trap is not direct evidence of natural movement, location attraction, trap scent, competitive exclusion, or causal effects of handling.
Night × trap independence is false, so raw transition counts are not valid independent trials.
Changes after removing recaptures could reflect reweighting or information loss rather than behavior caused by trapping.
No confident "kangaroo rat displaces pocket mouse" claim without a contrast surviving the trap-preserving null and explicit accounting for detection/effort. Main study remains post-result exploratory.
