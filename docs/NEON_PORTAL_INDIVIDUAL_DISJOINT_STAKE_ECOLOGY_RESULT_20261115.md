# Portal individual-disjoint small-mammal space-use test — actual ecological result (15 November 2026)

One NEON ecology manuscript, PR #23. Source lineage: independent Portal Project; already publicly analysed in other niche studies, so the present result is strictly **retrospective/exploratory**, not independent preregistered confirmation of a global NEON pattern.

## Source and the one frozen contrast

The actual source-only code was frozen before spatial-effect access: original Git source 2026-11-12 commit afd75933249ae60f3a5e9dab00b354f219e5e045, six files with original byte-level Git blob SHA validated. Source GO action #43677338828 verified **436 species×plot×same-month adjacent-year paired censuses** from 1996–2019: **227** control / **209** kangaroo-rat exclusion; 13 vs 11 treatment-associated plot IDs and **20 unique plots** overall (plots can change assigned treatment through time). Each pair had one original full-QC 48–49 trap-source census per year, and at least five species-captured individual IDs and at least three distinct station positions on each side after deleting IDs present in both years.

Precommitted downstream ecology protocol: docs/NEON_PORTAL_INDIVIDUAL_DISJOINT_SPATIAL_ECOLOGY_PROTOCOL_20261115.md, before exploratory output opened. Run #43677687501, original source read/verified and all outcome tests successful, archive SHA256 included in result JSON.

Actual source re-read retained **436/436** qualified pairs, and no conflicting same-census multistake individual IDs. The source records **1,794 pairwise shared observed-ID exclusions across repeated source comparisons**; this is NOT 1,794 unique biological animals with known deaths, replacement or dispersal. Fixed source and trap-grade quality did not change; no Portal source rows selected using observed R1 effect signs.

## Measured capture-space result, not a niche measurement

At each original 7×7 stake-grid plot, for focal species with disjoint captured IDs between adjacent same-month years, measure the probability that two randomly selected *captured* individuals, one from each year, were registered at exactly the same original source stake. Nominal original trap spacing is 6.25m. The SOURCE 49-stake uniform reference gives collision expectation **1/49=0.020408**. The stronger SOURCE annual plot×census species-blind encounter baseline is the dot product of ALL identified target-granivore observed capture fractions across the 49 stations in each of the two years, including the focal species. This background may conservatively absorb some genuine focal-species habitat association, but it also captures generic station-wide trap attractiveness/catchability. Neither source measures actual availability of each trap or all living rodents.

**Main source-frozen species-blind reference:** plot-equal mean cross-year collision EXCESS **−0.00006439 probability units** (−0.00644 percentage points); 10,000 draw fixed-seed whole-plot bootstrap **95% descriptive interval [−0.00154688,+0.00140097]** probability units (−0.15469 to +0.14010 percentage points). No clear positive excess beyond contemporaneous species-blind station capture propensities is established. The naive uniform 49-stake reference would show a plot-equal mean excess +0.00190817 probability units (+0.19082 percentage points), showing why an adequate source reference matters.

**Competitor treatment contrast:** plot-equal mean exclosure minus control on species-blind excess **−0.00052241** probability units (−0.05224 percentage points), whole-plot descriptive bootstrap **[−0.00469161,+0.00348649]** (−0.46916 to +0.34865 percentage points). Original plot-level treatment-specific means are 0.00030778 (exclosure) vs 0.00083019 (control) probability units, but some plots cross treatment states through years and overall plot-weighted mean is not the weighted arithmetic mean of separately stratified plot summaries. The contrast is not a causal randomized removal intervention and does not support a general competitive-release effect on this exact-stake capture persistence metric.

By species code, pair counts: PP 195, PB 137, DM 95, DO seven, PF two. Species-specific raw pair means are descriptive only; unequal plot/time support and already published Chaetodipus habitat-patch research prohibit post-hoc promotion of whichever source taxon is most positive.

## Ecological conclusion

This is a NEGATIVE OR NONRESOLVING finding about **recorded exact-stake spatial recurrence under a stronger species-blind observation source reference**, not evidence that rodents lack niches or that ecological niche structuring is absent. Stable recorded genus×trap associations in original NEON (corrected 14 physical-site Z+0.795) and the new single-landscape Portal absence of incremental species×stake collision cannot be pooled as same effect (different ranks, nulls, geography, seasons, effort, and underlying trap exposures).

Therefore the novel cross-study generalization cannot be "spatial niches are retained after individuals are replaced." The more defensible scientific question is: **when does apparent species-level spatial continuity provide information beyond background location-dependent observation opportunities, and how does its utility depend on real competitive/habitat state?**

The first condition was directly tested here: after conditioning on the background source, no convincing excess was found at the exact trap station. It does NOT establish that competition no longer matters at patch scales or that true species habitat use is random.

## What must be added before a mammal ecological mechanism claim

- Distinguish time-varying resources and habitat measured at original plot/quadrat with correct 1-m-offset / noncoincident census dates from stake-wide trap opportunity and bait attraction.
- Model individual movement/use with independent telemetry or cameras at matched dates/locations; ID-disjoint capture records alone do not calibrate trap-specific detection p.
- Evaluate a pre-frozen, genuinely unseen rodent cohort or new experiment with sufficient independent landscapes/sites, and separate spatial niche persistence from population growth, survival, extinction and colonization.
- Do not re-open or rerun historical NEON 58/158 or Structural 529/96/79 island-mammal responses to find a matching positive direction. Keep NEON density W/B 5/8 FAIL, patch after reuse exclusion p=.221 NONSUPPORT, operability 18/158 STOP and full manuscript SUBMISSION HOLD.

## Provenance
- Original Portal repo: https://github.com/weecology/PortalData
- Frozen source access: https://github.com/zuizui0223/neon/actions/runs/43677338828
- Frozen subsequent ecological analysis: https://github.com/zuizui0223/neon/actions/runs/43677687501
- Machine-readable result: results/neon_portal_disjoint_id_stake_ecology_receipt_20261115.json
- Prior art for Portal patch shifts: https://pmc.ncbi.nlm.nih.gov/articles/PMC6899716/
- Prior art for granivore resource partitioning: https://doi.org/10.1007/s00442-021-05104-5
