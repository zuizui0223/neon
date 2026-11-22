# NEON five-anchor canopy heterogeneity source pilot — frozen 20 October 2026

**Outcome-blind environmental-source feasibility check.** We are asking whether measured
1-m canopy height varies across the *same* NEON live-trap grid, not whether
canopy explains the observed positive genus trap-location recurrence. No
genus, abundance, trap occupancy, seasonal Z or W/B response is joined
to environmental pixel values in this pilot.

## Source verification held fixed

- EXACT original RELEASE-2026 seasonal lineage-recurrence cohort: 58
  consecutive-season comparisons, 30 named mammal plots, 14 geographic NEON
  sites, reconstructed from checksum-verified original capture CSVs.
- Same source product DP3.30015.001 CHM, **latest advertised month in
  2015–2025 per site**, with the exact RELEASE-2026 monthly endpoint, no
  alternate date/release selection to improve availability.
- The preceding [E5 receipt](../results/neon_e5_chm_reference_pixels_receipt_20261020.json)
  verifies 30 valid E5 reference pixels from 29 provider CRC32C/size-checked
  tiles totaling 36.3 MB. This is a **fixed external validation target**:
  the 30 E5 validity count, source monthly selection, and E5 zero count
  must be reproduced by this new five-anchor source pilot. Unlike the E5
  original JSON, per-plot heights cannot be compared across different
  outputs because those are deliberately private.

## Five source anchors, never synthesized

For every one of the 30 unchanged plots, use only the five *literal*
source anchor station names A1, A10, J1, J10 and E5 constructed under the
official source namedLocation plus dot plus trap label rule. Query **the
official current NEON locations API** for each of these 150 names and
accept only one uniquely current projected coordinate with explicit UTM
zone/hemisphere and recognized geodetic datum. Do not rotate,
interpolate, spatially buffer the E5 to invent other locations or infer
any of the 95 other stations. A missing historical date/uncertainty is a
separate limitation, never a zero estimate.

For each anchor choose the unique filename-georeferenced 1-km CHM tile
containing that projected point. Use the exact source monthly inventory,
size, MD5/CRC32/CRC32C verified actual bytes and local SHA256 audit; never
treat CRC-short-string parsing as permission to bypass a failed checksum.
Bound downloads at 280 MB across the source 30-plot cohort, deduplicate
a tile referenced by multiple anchors and use at most four download
workers. Assert the raster's actual CRS matches the source point's
declared datum, with one band and 1-m resolution. An explicitly known
coordinate uncertainty can support a *descriptive* local window, not
a calibrated confidence interval. An unknown uncertainty remains
unknown. A zero CHM height is **valid** and not the same as nodata,
nor proof that shrubs, ground cover or low vegetation are absent.

## Permitted aggregate outputs

Report for all 30 fixed plots and 150 anchor requests:
- queried/parsed anchor count, unique tile keys and downloaded
  size/checksum-verified GeoTIFFs, actual valid or masked/no-tile/CRS-error
  point counts, and reference E5 validity (must match original 30).
- plots with >=2 valid anchor heights, >=2 *different* valid heights,
  all five positions valid, and plot-level five-point canopy range
  summarised by min/median/max and percentage with nonzero within-plot
  range; count plots where E5=0 but at least one other literal anchor>0.
- count plots containing anchors with known geospatial uncertainty,
  separate from unknown uncertainty; overlap with published four
  georeferencing-problem plots, retained in denominator not silently
  removed. Aggregate only; no raw station IDs/sites, coordinates,
  raw canopy pixel values per plot, animal tags or source file URLs.

## Decision rules

This is NOT the planned habitat-mechanism test. A nonzero within-plot
range establishes only that the available 1-m CHM distinguishes canopy
environments somewhere inside the source grid; it does not prove
relevant understory variation, genus-specific microhabitat sorting, or
stable habitat across the exact mammal capture seasons. A zero range
over five anchors cannot prove the *other 95 stations* are homogeneous.

A later within-grid ecological analysis requires a fully verified
100-station geospatial/time crosswalk (with special handling for the four
published geolocation-issue grids), actual date-suitable environmental
layers and separately frozen genus/detection-calibration hypotheses.
The original corrected seasonal recurrence result, the failed 8-genus
density W/B generality result (5/8<6/8), the source-only F/C matched
comparison STOP and external MOSA W/B seal remain unchanged.
