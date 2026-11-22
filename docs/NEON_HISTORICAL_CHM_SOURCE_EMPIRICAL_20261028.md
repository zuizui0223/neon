# NEON historical canopy source: completed actual pixels, 28 October 2026

**This is a documented environmental SOURCE GO, not an ecological-effect GO.** The single NEON small-mammal macroecology paper remains DRAFT/SUBMISSION HOLD.

## Successfully retrieved, immutable original-source scope

- Original corrected >=3-genus RELEASE-2026 mammal source cohort remains exactly **58 adjacent-season pairs at 30 mammal grids / 14 independent physical sites**. Four geolocation-issue grids retained. The previous canonical REST location source already returned **3,000/3,000** historical station records with **34,800/34,800** date-valid original capture-day station checks.
- The precommitted AOP calendar-month selection was made **before reading the historical canopy pixels**: one nearest published acquisition month per original plot×capture day, with earlier acquisition chosen on a tie. A complete original source census of 97 distinct site-month visits had yielded 36/58 pairs within ±12 months, 22/58 within ±3, 18/58 with all six days matched to prior/same-month acquisitions within 12 months, and 10/58 within three months. These temporal categories were never changed based on observed canopy or old mammal Z.
- Official historical AOP CHM manifests were available for **31/31 selected site-months**, including **28/28** site-months used by the ±12-month subset. The source used **51 actual verified GeoTIFFs** with exact georeferenced tile filenames, source byte sizes and published checksums; a total **35,817,831 source bytes**, below the frozen 350 MB cap. No monthly metadata failures, no checksum failures, no missing station tile matches.
- Exactly **246 original plot×capture-day keys within ±12 months × 100 historically valid named trap stations = 24,600** actual date-associated canopy-height pixels were read and passed source raster CRS, nodata and finite-value checks. These station×date attempts are **not 24,600 statistically independent samples** and no per-station canopy heights are exported.
- Applying the frozen criterion to every original seasonal pair (all six days each with >=95/100 actual-source CHM pixels), **36/58 pairs across 12 independent sites and 21 grids qualified**. The declared descriptive source-coverage rule **>=20 pairs, >=8 independent sites, >=12 grids** is met without lowering thresholds. The ±3-month class retained **22/58 across 12 sites / 15 grids**.
- The stricter prior/same acquisition class retained **18/58 pairs across only 6 independent sites / 10 grids** within 12 months, and 10/58 across 6 sites / 7 grids within three months. This is an independent severe limitation; do NOT call the prior-only class a macroecological validation meeting the original 8-site rule.
- Source geoNEON-adjusted coordinate uncertainty windows had **8,637** station×date observations with nonzero within-window canopy-height range; **300** window samplings were clipped by 1-km raster boundaries. These source resolution/uncertainty facts prevent treating one nominal 1m pixel as a certainty about mammal-level vegetation.

## Ecological significance and strict interpretation

The new result **removes the previous source-availability excuse** for not building an independently measured canopy environmental covariate across a large fraction of the original small-mammal seasonal study: official historical CHM images exist, are checksummed, cover the dated original trap coordinates, and are relatively close in calendar time for 36/58 original seasonal comparisons.

It does **not** measure how vegetation changed between capture seasons, establish that 12-month old/future canopy is time-invariant, represent grasses or shrub structure (CHM suppresses height below about 2m), or estimate individual use/detection probability. The AOP site visit month is not an exact aircraft flight day. An acquisition AFTER the trapping date does not become a prior environmental predictor simply by geographic alignment. The 18 original strictly non-future-acquisition pairs lack sufficient independent site coverage for a strong general macro claim. A stable genus-specific trapping/catchability template can also create excess capture-location recurrence, as demonstrated by the source-free exact fixed-margin counterexample.

**Thus the biological outcome remains conditional genus-associated CAPTURE-location recurrence** despite nonshared observed tag identities (14-site original Z +0.795, exploratory exactly-two 30-site Z +0.615). Persistent true-use niche/habitat filtering, competition and demographic replacement remain unconfirmed.

## Next single biological discriminator

Use this SOURCE coverage as a frozen environmental exposure readiness result, not as a license to regress already inspected positive mammal Z until significance. For a genuine causal niche mechanism, collect a new **held-out** mammal capture/detection cohort with independently calibrated genus-by-station detection and dated local microhabitat. At minimum separate tree canopy (verified AOP CHM), ground and shrub cover (not estimated by CHM), operational trap nights and firstnight release availability; use an identified repeated-occasion model only where sufficient recaptures/stations exist. Precommit site/season splits and mechanistic contrasts before viewing future response.

Do not revive any failed old result: density W/B 5 of 8 versus 6 required, original within-10m patch p=.221 after season reuse exclusion, code4/5/6 trap operability source 18/158 versus 80 required, tower weather 79/80 QC STOP, same-cohort R-W/B source 12/58 STOP, released-only reencounter source 1 of 7 sites. These remain historical null/STOP boundaries.

## Provenance and reproducibility

- Action https://github.com/zuizui0223/neon/actions/runs/40614320719
- Machine-readable source receipt: results/neon_historical_chm_actual_pixel_source_receipt_20261028.json
- Frozen design: docs/NEON_HISTORICAL_CHM_ACTUAL_PIXELS_20261028.md
- Source implementation: analysis/run_neon_historical_chm_pixel_source_v1.py
- Pure source-support checks: analysis/neon_historical_chm_source_support_v1.py
- NEON AOP ecosystem structure documentation: https://data.neonscience.org/api/v0/documents/quick-start-guides/NEON.QSG.DP3.30015.001v1?fallback=html&inline=true

All exported results are anonymous aggregates; per-site/plot/station/time coordinates and raw canopy matrices remain private to source workflow memory.
