# NEON 28 October source-verified environmental pattern — one manuscript, no mechanism inferred

## 1. Actual completed source retrieval (NOT just a planned model)

The prior 3,000 canonical NEON REST original station histories were a direct full population source success: 3,000/3,000 unique original named stations; 34,800/34,800 original 58 seasonal pairs × six actual trapping dates × 100 spatial positions date-valid, across 30 plots/14 physical sites. All four historic geolocation issue grids remained. This is a source-position GO, not an ecological habitat effect.

New 28 October SOURCE-ONLY all-station CHM extraction, verified GitHub Actions run 40612115870:
- The same original 58 pairs/30 grids/14 sites reconstituted from checksum-verified RELEASE-2026 mammal original files. Only the previously frozen latest available 2015–2025 AOP month at each site was used, which for these 14 sites meant 2022 (1 site), 2023 (5) and 2024 (8). No new AOP visit year was selected using the mammal effect or canopy pixel values.
- All 34 original GeoTIFFs were downloaded and validated using provider byte size and checksum. 3,000/3,000 exact named original station pixels were successfully read; 1,894 (63.1%) were CHM height 0, not evidence of vegetation absence; negative values 0.
- **Within-grid measured CHM range >0 at 25/30 plots**, whereas the precommitted prior *five-anchor subset only* found 14/30. Median measured full-100 trap CHM range was 0.9385 m (max 36.904 m); five plots had all 100 measured stations equal to CHM zero. E5 zero but at least one other original station positive in 14 plots. The original five-anchor 150 valid/93 zero/19 zero E5/14 nonzero-range results were exactly reproduced in the same source run.
- Under documented geoNEON-adjusted assumed positional uncertainty (not calibrated 95% precision), 575 zero-centre pixels had positive CHM somewhere in the surrounding window, and 1,681 of 3,000 had a nonzero window range. 30 windows were clipped by the 1-km tile boundary: such ranges are not complete source error bounds. Neither window variation nor measured CHM implies animal habitat selection.
- With the *fixed latest visit* AOP month compared with actual 348 source paired-day attempts, acquisition was later than the historical capture calendar month in 276, earlier in 63 and the same month in nine; median absolute gap was **70 calendar months**. Only 9 of the original 58 seasonal pairs had all six capture days within 12 months of that latest visit; four pairs within three months. Thus the latest snapshot is generally **temporally unsuitable** for attributing original capture-space recurrence to contemporaneous canopy structure.

A second source-only historical AOP month-availability census, verified GitHub Action 40612718442:
- The ORIGINAL same 58 mammal seasonal pairs/339 distinct plot-day keys remained. The official released DP3.30015.001 site metadata provides **97 unique site×flight-month acquisitions across all 14 original sites** (5 to 10 months per site, median 6.5).
- If the flight month is chosen solely by **minimum capture/flight calendar-month distance** (a preregistered source-metadata choice; ties prefer the earlier month, no canopy pixels read), 153/348 source paired-day attempts have a listed AOP acquisition within three months; 252/348 within 12 months. **22/58 pairs** have all six days within three months and **36/58** within 12 months; the stricter prior-or-same-month matches are 10/58 within three months and 18/58 within 12 months. These are **metadata availability** counts, NOT verified historic raster coverage or flight dates.
- This creates a concrete route to contemporaneous environmental coverage using past AOP visits without retrofitting the old CHM choice after observing animal results.

## 2. Ecological contribution without an unsupported positive mammal claim

**Supported by measured environmental sources:** NEON mammal 90×90m trap grids contain heterogeneous canopy-top structure at 25/30 source plots, including structure missed by sampling only the E5 or four corners. The discrepancy matters because a positive genus-to-same-trap capture signature can arise from a persistent environmental template OR taxon-dependent trap catchability. Our independent synthetic fixed-margin counterexample already demonstrated this confounding mathematically.

**Not established:** The CHM selected from 2022–2024 does not establish vegetation structure at all original mammal trapping dates (2015–2024). It is a canopy-top height model rather than direct ground and shrub cover, and a 1m pixel has finer nominal resolution than the median 3.1m geoNEON-assumed location uncertainty. Moreover, no independent genus-specific detection rate or animal habitat use has been estimated, so the old positive recurrence Z cannot be attributed to canopy, vegetation, competitive niche or ecological memory. A biologically interesting hypothesis is now measurable in principle, but not yet tested.

**Historical biology held fixed:** original corrected >=3-genus 14-site Z+0.795, exact-two-genus exploratory 30-site Z+0.615, 10m patch source-reuse non-support p=0.221, density W/B 5/8 (guard 6), trap-operability 18/158 STOP, tower temperature 79/80 QC STOP, matched R–W/B 12/58 STOP. Do not reinterpret the source-only CHM result as new confirmation of old animal effects; both effects arise from already inspected RELEASE-2026.

## 3. Next single biological gate

Source-only first: for each original 58-pair event and original site, query all **available historical AOP flight-year CHM manifests** at a selected source month based only on the site/date matching rule; verify provider checksum, the actual sampled trap pixel, CRS, geoNEON uncertainty, within-year acquisition dates and paired-season support. Do not substitute metadata month support for verified raster availability and do not pick visits by canopy values or observed genus recurrence. Freeze support thresholds and the independent detection/effect model before opening any new ecological response in a later genuinely unseen cohort.

If exact source-year canopy and independent trap-level detection data cannot be jointly measured, the paper remains a defensible **conditional genus-associated capture-space recurrence**, not a causal habitat-selection or ecological-memory paper. Continue as ONE integrated NEON macroecology manuscript v0.8 DRAFT/SUBMISSION HOLD, not a second methods paper.

Machine-checkable original receipts:
- results/neon_3000_rest_historical_source_receipt_20261028.json
- results/neon_3000_chm_month_aware_source_receipt_20261028.json
- results/neon_aop_multiyear_month_coverage_receipt_20261028.json
- docs/NEON_3000_CHM_MONTH_AWARE_SOURCE_20261028.md
- docs/NEON_AOP_HISTORICAL_MONTH_COVERAGE_20261028.md
