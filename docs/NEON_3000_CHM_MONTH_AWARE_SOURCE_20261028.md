# NEON full 3,000 original trap stations and CHM month-aware source audit
28 October 2026. ONE integrated small-mammal spatial macroecology paper, PR #23, DRAFT/SUBMISSION HOLD.

## Empirical source status before opening this work

The canonical REST historical-position audit, GitHub Action #40610372312, successfully recovered all 3,000 original 30-grid x 100-station named location histories and validated all 34,800 original station x capture-day coordinate comparisons, including four historically documented geolocation-issue grids. This is geographic SOURCE GO, not ecological habitat or detection GO. Only 348 source station-day comparisons had directly reported coordinate uncertainty; the remaining geoNEON-adjusted radius is an assumption (median 3.1m, min 1.1m, max 3.42m), not measured precision.

The original five-anchor CHM source pilot read 150/150 exact named A1/A10/J1/J10/E5 station pixels, 93/150 zero, E5 zero in 19 plots, and a nonzero five-anchor height range in 14 of 30 plots. The original official AOP acquisition choice is latest available published month in 2015-2025 at each original site, with year counts 2022:1, 2023:5, 2024:8. These outcomes and selection remain fixed.

## Source-only current research decision

1. Preserve the original checksum-verified RELEASE-2026 mammal cohort: 58 season pairs, 30 plots, 14 independent physical sites; original six capture days per pair, and all four geolocation-issue grids. No genus spatial response or post-result site choice.
2. Re-fetch the exact 3,000 canonical NEON REST named locations with history=true and require all 34,800 original historical date-effective UTM/CRS source checks. A changing historic coordinate cannot be silently assigned one CHM pixel. Missing data or uncertain coordinates are never interpolated from A1/E5 and adjacent geometry.
3. Use the frozen source latest released AOP CHM month at each site. Require the original 2022/2023/2024 site distribution to reproduce, query released DP3.30015.001 site-month manifests, select unique exact filename-georeferenced tiles, and download only actual provider size/CRC32C/MD5-verified rasters. Deduplicate tiles, cap source retrieval at 280MB.
4. For all 3,000 original station points, inspect 1-m CHM pixels and source UTM/CRS/mask and record only aggregate counts. Also sample within adjusted uncertainty-window neighborhoods as a diagnostic; clipped windows are incomplete. Before reporting a novel full-station canopy aggregate, reproduce original 150/150 valid, 93 zero, 19 E5 zero and 14 plots with nonzero five-anchor range in this same new run. If any mismatch: STOP.
5. Calculate signed differences between original capture calendar months and selected AOP acquisition calendar months: 348 source paired-day attempts, 339 unique plot-day keys. Report coarse within 3, 12 and 24 months, after/before counts and full-six-day seasonal-pair counts, not an exact flight-day match. Duplicate season-pair dates are NOT independent.
6. Publish anonymous aggregate coverage only; no per-site/per-plot/per-station coordinate, source animal ID, private original capture date, tile URL, or per-plot canopy height leaves in-memory analysis.

NEON CHM is 1-m canopy-top height derived from AOP LiDAR, not a trap-scale shrub/grass cover measure or independently observed rodent habitat preference. The CHM workflow preserves vegetation heights above about 2m; a zero CHM value is NOT bare ground. The currently published original site AOP visits are mainly 2022-24 whereas mammal captures are 2015-24. Matching a single 1-m pixel with uncertain trap position or even a calendar month does not prove habitat history. Separate NEON DP1.10058.001 field plant-cover plots are not automatically located at the 100 mammal traps.

## Ecological claim boundaries

Observed season recurrence of genus-associated CAPTURE locations, original 14 sites mean Z+0.795 and exploratory exact-two group 30 sites mean Z+0.615, remains unchanged. Do not infer a detection-corrected spatial niche, habitat-driven recurrence, competition or demographic replacement. Historical 10m patch source-dependence nonsupport, density 5/8 (6 required), actual operability 18/158, temperature QC 79/80, and same-population coupling 12/58 remain stopped; do not retroactively loosen thresholds or change the sample. Keep one v0.8 manuscript DRAFT/SUBMISSION HOLD.

Reproducibility:
- Source-only aggregation: analysis/neon_3000_chm_source_qa_v1.py
- Actual source retrieval: analysis/run_neon_3000_chm_source_v1.py
- Synthetic tests: tests/test_neon_3000_chm_source_v1.py
- GitHub Action: .github/workflows/neon-3000-chm-source.yml
- Private-safe aggregate artifact: build/neon_3000_chm_source_20261028.json

The next biological test, if this acquisition passes, requires independent source-year-appropriate environmental measurements (especially low vegetation) AND an independent taxon-by-station detection/use stream in a genuinely held-out cohort. A source-only CHM positive result cannot identify the mechanism of the historical genus capture-location recurrence.

Official sources:
- https://data.neonscience.org/data-products/DP3.30015.001
- https://data.neonscience.org/api/v0/documents/quick-start-guides/NEON.QSG.DP3.30015.001v1?fallback=html&inline=true
- https://data.neonscience.org/data-products/DP1.10058.001
