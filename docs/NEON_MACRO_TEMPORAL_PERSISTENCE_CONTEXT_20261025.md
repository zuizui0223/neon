# Macro ecological next step: temporal persistence versus environmental and detection context

**Frozen design — 2026-10-25 (after all 3+ and exactly-2 genus seasonal recurrence effects were seen; BEFORE any new temporal-lag or climate-by-effect outcome)**

## One ecological question
**Does genus-associated capture-station recurrence among nonshared observed animals decay with the actual elapsed time between three-night sampling bouts, after separating physical-site and meteorological-season-transition composition?**

This is an **exploratory within-RELEASE-2026 mechanism-discriminating observation**, not new confirmation or a test of true demographic turnover. The already positive source-specific 14-site (3+ genera), 30-site (exact-two), and 17 geographically nonoverlap sensitivity are **not refitted as independent confirmations**.

Predictions fixed in advance:
- **Temporal-decay hypothesis (H1)**: conditional exact-two genus station recurrence Z decreases as time between original adjacent-season trapping bouts increases, after adjustment for physical-site and transition-season type. Report negative slope with physical-site resampling uncertainty if found; do not claim a biological memory half-life, causal replacement, competition or microhabitat origin.
- **Stable template alternative (H2)**: zero/positive slope or imprecisely estimated negative slope indicates **no resolved negative time-decay in this observation sample**, which is consistent with persistent local habitat *or* persistent taxon-dependent catchability. Do not claim proven invariant recurrence if CI spans zero.
- **Pure observation-process alternative (H0)**: taxon-specific station catchability can produce positive recurrence at all measured lags. This analysis cannot exclude H0, so climate/habitat data and independent detection are separate necessary follow-ups.

## Source-only pre-effect audit (must run first)

Rebuild original checksum-pinned DP1.10072.001 RELEASE-2026 (2015-04..2026-09) 3,547 original files, 1,773 plot-night and 1,707 trap-night files, 21,363 plot-night rows and 1,505,827 trap-night rows, **58 original >=3 genera and 158 exact-two seasonal pair source cohorts**, exactly 216 distinct pair keys, from unchanged original event protocol and shared-observed-tag exclusion. Capture-day source tuple is preserved for each of two consecutive seasons; define **day gap** `G=(min(B original three dates)-min(A original three dates)).days`, with no midpoint imputation. Fail if G <= 0 or G >= 400 days. Retain exact original season ordinal `q` and transition category `q modulo 4` for differences from winter→spring, spring→summer, summer→autumn, autumn→winter. The four categories must not be pooled into one single undifferentiated climate process.

Before looking at any G-vs-Z relationship, publish only aggregate gap distribution, site counts, site-level gap support, counts and site variations across *both* exactly-two and 3+ cohorts, original source season-key reuse and site/domain coverage. Do not print the original capture date, genus, physical site code, animal identity or trap coordinate. A source-only audit of independent NEON temperature and precipitation monthly product availability is allowed, but mere product availability is not an actual temperature/precipitation measurement. NOAA/Daymet download credentials are not assumed. Provider products: NEON DP1.00002.001 temperature, DP4.00001.001 weather summaries where published, weighing-gauge DP1.00044.001, tipping-bucket DP1.00045.001, and historic DP1.00006.001 (retired). Product availability may vary by release and month; validate corresponding original capture months and not current availability. Weighing gauge / tipping / throughfall are not interchangeable.

## Effect opening feasibility gate

Two-row Z marginal effect values have been observed overall; **temporal lag correlation has not**. We may use the frozen exact-two unit Z model code to reproduce the same original 150 informative units, original 30 physical sites, positive site mean 0.6147113767599713, and source sorted site means *before* opening their G/Z link. This source Z replay is a correctness check, not a new ecological effect.

Open the time-lag association only if:
1. at least 100 original exactly-two units have nondegenerate conditional Z and finite gap;
2. at least 15 independent physical sites have ≥2 informative pairs with nonidentical gap and at least 8 physical sites have within-site G range >=30 days;
3. transition-season type is observed in ≥3 distinct categories among eligible units;
4. all 150 informative unit Zs produce site means with the same sorted receipt distribution within numerical tolerance of `results/neon_exact_two_genus_ecological_receipt_20261025.json` (absolute per-site <= 1e-8), and no original site season key is silently changed;
5. no zero-variance units are dropped from original source denominators (they simply have no Z).

**If any condition fails, STOP lag-effect analysis and report quantitative support deficit. No loosening after knowing an effect sign.**

## One fixed model and transparent inference

For each exact-two unit `u` at site `s`, observed outcome is original site-specific unit Z from the **exact finite uniform fixed-margin** two-row null. Predictor is original capture start-to-start gap in **30-day units**, centred. Fit weighted least squares:
`Z_u = α_s + δ_(season transition category) + β_G (G_u / 30) + ε_u`,
with **full physical-site fixed intercepts, transition-type fixed effects**, and pair weight **1/n_s** within a physical site, so sites with many comparisons cannot dominate. Do not treat 150 seasonal pairs as independent geographic sites.

If the site/transition fixed-effect design is rank-deficient, STOP and return the rank-deficiency count, not an invented slope.

Report β_G standardized Z per 30 elapsed days, site-cluster bootstrap percentile interval **from 2,000 whole physical-site resamples**, seed **2026102516**, plus deterministic leave-one-site-out min/max and fraction of site omissions preserving its sign. Resample whole physical-site sequences, not individual pair rows, and maintain fixed site + transition effects within resamples. Do not select subgroup by p. Report descriptive within-site Pearson gap-vs-Z direction without model as supplementary only. No one-sided p-value is obligatory or allowable as new preregistered inference from the consumed release.

Independent source reuse sensitivity: remove **all seasonal pair units at every physical site containing any repeated site×plot×season key anywhere in original exact-two cohort**, regardless of observed β or Z; fit the same pre-specified slope only if ≥8 sites and ≥30 informative pairs with at least 5 sites providing within-site G variation. Else STOP. This is a newly frozen source-only support condition, not a rescue threshold.

## Climate/environment feasibility

A second, non-effect output will count whether NEON tower atmospheric sensor weather months are in RELEASE-2026 at both original observed three-day bouts by physical site and year-month, grouped separately for temperature and rainfall products. NEON /sites?release=RELEASE-2026 source metadata is authority for **availability only**. A link to a tower 30-minute temperature and precipitation month does not validate daily values or local trap-grid vegetation. Daymet single-pixel download now may require Earthdata auth and must **not** be used as a fallback without explicit source authentication. Do not fabricate climates.

If weather-month coverage passes ≥20 sites / ≥100 exact-two seasonal comparisons under temperature and one declared precipitation product, freeze an independent **single** climate hypothesis before downloading/reading environmental values or fitting an ecological environment response. The same-response 2026 release still cannot become an independent confirmation merely through climate covariates.

## Research validity boundaries

Novelty is potentially in the *temporal persistence scale of a taxon-to-exact-trap signature*, which differs from general temporal abundance/occupancy established in earlier NEON publications; however a positive seasonal recurrence does not automatically imply a time-decay slope. Neither unobserved demographic turnover nor species/genotype resolution, true occupancy, behaviour or competition is proven. All outcomes are integrated within **one** macroecology paper, with the historical failed 8-genus W/B generality rule (5/8 versus 6 needed) never recoded as positive.

**Provenance:** source-original support `results/neon_exact_two_genus_source_receipt_20261025.json`; exploratory exact-null effect `results/neon_exact_two_genus_ecological_receipt_20261025.json`; original 3+ `results/neon_uniform_null_correction_receipt_20261020.json`; no new null direction or richness subset.
