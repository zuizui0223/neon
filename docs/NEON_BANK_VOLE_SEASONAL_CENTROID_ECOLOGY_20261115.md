# 15 November 2026: bank vole individual seasonal captured-location shifts

One integrated NEON mammal ecology paper PR #23. Independent 2021 Finland field system, original 2024 Journal of Animal Ecology published prior art. This is a RETROSPECTIVE observational reanalysis and not a new causal niche mechanism.

## Actual original pinned source and independent sites

Original GitHub jmistrick/vole-spatial-manuscript commit 47dc1e9b1f83ec2faaf7ba232e02e00f9e4cffb4: original fulltrap21_volecapturedata.csv and site_trts.csv exact Git source blobs both validated. There are 2012 capture rows (summer 905; fall 1107), 742 site×tag individuals and 120 observed in both seasons. The original SOURCE-only gate, opened before any spatial x/y shift, froze ALL 51 individuals with at least two recorded catches each summer and autumn. Four factorial cells fed/control=16, fed/deworm=12, unfed/control=15 and unfed/deworm=8, each across exactly three physical study sites. Total sampled biological sites are 12 (the treatment lookup has one additional site with no original 2021 captures). Original source names, animal tags and coordinates are not exported. Original site×trap coordinate identity checks passed for 563 visited site-specific traps.

## Ecological observation, not independent space-use inference

Each individual's summer and autumn capture centroids were calculated in ORIGINAL SOURCE GRID COORDINATE UNITS, not converted to metres. The within-individual null reallocates the same pooled observed capture coordinates between summer and autumn preserving original counts, 2000 fixed-seed draws per individual. This explicitly tests additional separation beyond the finite-capture sampling effect conditional on a common pooled captured-location distribution; it does NOT preserve temporal clustering within a season, model trap detection or estimate independently observed movement.

Across all 51, average observed centroid separation was 2.1695 source grid units and the mean within-individual pooled reallocation expected separation was 1.4820. The predeclared primary gives EACH of the 12 physical sites equal weight: observed 2.1607 grid units, reference 1.5450 grid units, **site-equal excess +0.61571 original grid units**. The fixed 5000-resample factorial-stratified site-bootstrap descriptive 95% interval was **[+0.42077,+0.83422]**. There were 38 individuals with positive raw excess, 12 negative and one zero, but **only three of 51** exceeded their own personal randomization 97.5th percentile. Do not confuse a descriptive site-aggregate shift with a set of independently significant individual movements.

Predicted resource-treatment effect was Fed−Unfed negative. Observed contrast instead **+0.11117 grid units**, bootstrap **[−0.28732,+0.53292]**. Predicted helminth-treatment effect Deworm−Control positive. Observed contrast **−0.02641**, bootstrap **[−0.46127,+0.35939]**. Both factor contrasts are NONSUPPORT; all four experimental cell means retained without subgroup optimization. Original 3 replicates per cell limit causal generality and the treatment groups may differ in total density/catchability. Published 2024 original food/shrinking-range and deworm/expanding-range findings remain PRIOR ART, and these new centroid contrasts are different observational estimands, not contradiction or confirmation.

## Ecological interpretation in one programme

NEON original 14-site observed taxon×capture station recurrence remains conditionally positive (Z+0.795). A separate Portal rodent field system did not exhibit extra exact-stake capture-location recurrence beyond a strong contemporaneous species-blind capture reference after disjoint observed IDs, across 436 retrospective same-month/year pairs. Finland provides positive descriptive WITHIN-INDIVIDUAL change of captured centroid location between breeding and autumn seasons under a conditional sampling reallocation null, but it has NOT established how populations replace other individuals or how true habitat movement occurs.

Together the results show NOT a universal stable niche but **different temporal dynamics at different biological grains**, and a strong sensitivity to the observation/reference model. Individual seasonal capture centroids may change while the group-level taxon/capture-station pattern can still appear stable across turnover in another system. That is a cross-system HYPOTHESIS, not an identified shared process.

A biological mechanism must distinguish resources/vegetation, competitors and trap-specific observation for the same animal use/movement outcome in independently validated space-time. Direct VHF/telemetry source or synchronized cameras with trap operating effort is needed; do not call these captures true space use. Structural global island graph is geographically constructed from range-map-derived species occurrences; source influence is not measured dispersal. No combined effect sizes or animal survival inferred.

## Source and audit

GitHub original source: https://github.com/jmistrick/vole-spatial-manuscript
Published ecological study: https://doi.org/10.1111/1365-2656.14067
Pre-outcome protocol: docs/NEON_BANK_VOLE_SEASONAL_CENTROID_FROZEN_20261115.md
Successful source+outcome Action #43679092353: https://github.com/zuizui0223/neon/actions/runs/43679092353
Verified machine receipt: results/neon_bank_vole_seasonal_centroid_receipt_20261115.json
One manuscript remains DRAFT/SUBMISSION HOLD and all original failed controls are retained.
