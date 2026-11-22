# E5 reference-point / CHM actual raster access pilot — 2026-10-20

This is a post-result source-access experiment, NOT a habitat-effect model. The corrected seasonal recurrence result is unchanged. The 30-grid orientation audit observed A1→A10 south and A1→J1 east at all 30 current API grids, whereas the product issue narrative describes a westward letter axis. No coordinate is rotated, relabelled, or declared historically correct to eliminate this discrepancy.

## Scope fixed before reading any canopy pixels

1. Reconstruct the same RELEASE-2026 58 seasonal comparisons / 30 plots / 14 sites with the existing checksum-verified source loader. Obtain each plot's literal source namedLocation and query its E5 location, not the plot centre as a surrogate for all traps.
2. E5 is a reference point, not the complete 100-station grid. NEON's published small-mammal issue log states E5 is unaffected by the listed layout errors. This permits a limited current-reference-point access pilot, but does not establish historical coordinate validity or habitat exposure for every trapping event.
3. From product DP3.30015.001 metadata choose the latest advertised acquisition month during 2015–2025 separately for each original site. The cutoff and latest-month rule are fixed before reading values. Request ONLY the exact RELEASE-2026 package for that site/year and chosen month, with provisional inclusion disabled. No substitution with another release or year if a tile is unavailable.
4. Candidate CHM tiles are selected by the source filename's documented 1-km lower-left projected coordinates containing E5. Ambiguous tile keys stop that plot. Require original byte size and MD5 before opening a GeoTIFF. Cap total selected downloads at 280 MB, use at most four download workers, and deduplicate shared tiles.
5. Read the actual GeoTIFF CRS, bounds, resolution and validity mask. Require an explicitly recognized coordinate datum and matching UTM CRS, one band and 1-m resolution. Never infer WGS84 from a UTM zone alone. Sample only E5, and separately report the range/validity of a square neighbourhood based on any published coordinate uncertainty (not a statistical confidence interval). Unknown uncertainty stays unknown, not zero.
6. A zero CHM value is distinct from nodata and is NOT evidence of bare ground. This product can truncate low vegetation. The latest selected canopy year is NOT assumed synchronous with every historical mammal observation.
7. Export aggregate counts, selected acquisition-year counts, byte/checksum provenance, raster-validity categories and broad height summaries only. No animal IDs, site codes, named-location strings, actual coordinates, raster tiles or per-animal measurements are exported.

## Decision

A successful E5 pixel demonstrates an operational link from an exact source reference coordinate to a released raster. It does NOT authorize the within-grid genus×habitat regression. Full station orientation, historical date linkage, location uncertainty and relevant vegetation structure remain separate requirements. Failure or missing coverage is reported for the fixed 30-plot denominator; no favourable subset is labelled representative.

Sources: NEON DP1.10072.001 issue log; NEON DP3.30015.001; official byTileAOP coordinate-selection tutorial; rasterio masks documentation. All causal habitat-filtering, detection, competition and historical W/B claims remain untested by this pilot.
