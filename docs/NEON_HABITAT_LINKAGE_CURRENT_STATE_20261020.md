# Environmental linkage after the corrected seasonal recurrence analysis

20 October 2026. This source-linkage task follows the existing environmental discrimination plan, not a new favorable endpoint or an environmental regression. The active numerical inference is `results/neon_uniform_null_correction_receipt_20261020.json`; earlier accepted-swap p-values are historical and are not restored by this work.

## Biological question

Do recurring genus-associated capture locations correspond to persistent measured habitat structure, rather than only genus-dependent capture propensity? Neither explanation is established by the corrected positive recurrence result. This stage repairs the missing environmental coverage module and checks whether independent habitat data and actual mammal station coordinates can be linked to the unchanged 58 seasonal comparisons, 30 plots and 14 physical sites.

## Source distinction that changes the implementation

NEON's small-mammal issue log, checked 20 October 2026, identifies **18 mammal grids across seven sites**, not 18 individual stations and not all grids at those seven sites. It describes an orientation mismatch between nominal trap labels and database spatial coordinates, with a special layout at TEAK_004. Field trap labels and ordinary E5-based plot-level data are not affected. Therefore this issue does not on its own invalidate the original nominal A1–J10 recurrence statistic, but is material to linking those labels to canopy pixels.

The log lists a 31 December 2026 release-resolution date (future relative to this audit) while its resolution text describes updated Named Locations records. We do not equate a future release date with completed correction in historical files, or assume archived downloadable shapes equal today's registry. Current named locations must be queried and time-stamped independently.

Authoritative issue source: https://data.neonscience.org/data-products/DP1.10072.001/RELEASE-2021 (shared product issue log, including the 4 September 2026 report). Source-read coordinate semantics: `NEONScience/NEON-geolocation`, `geoNEON/R/getLocMAM.R`, blob `a1ca2f9b35a0be79fb1c32a2f427323ee180c995`; `getLocValues.R`, blob `a9786d94963ac8bf13b75303293e10999f04b6ab`; `getLocProperties.R`, blob `db5de48eca10387cdede47a058173cda55fa22a9`.

## Actual source operations

1. Reconstruct the original cohort from checksum-verified RELEASE-2026 capture files. Preserve the 58-unit/30-plot/14-site source gate. The inventory has 3,547 files; 1,773 plot files and 1,707 trap files are actually downloaded and verified (3,480), so inventory count is not mislabeled as downloaded count.
2. Check product metadata for canopy height (DP3.30015.001), vegetation structure (DP1.10098.001) and plant cover (DP1.10058.001). Availability of a product at a site is not proof of matched pixels, years or vegetation plots.
3. Read actual `namedLocation` values from source capture CSVs. If a plot has no source name or conflicting names, do not invent a replacement. Construct station names only by the official `namedLocation + '.' + trapCoordinate` convention.
4. For each uniquely linked plot, query five fixed anchor stations: A1, A10, J1, J10 and E5, with location history requested. Parse only a uniquely current projected coordinate and declared UTM zone/hemisphere. Record absence/ambiguity separately. Do not silently fill absent coordinate uncertainty with zero.
5. Report source-only geometry diagnostics: edge lengths, approximate rectangularity, cardinal orientation and historical issue-grid intersection. The broad diagnostic bounds (70–110 m sides, <=5 m closure/E5 residual, absolute cosine <=0.1) are layout checks, NOT a claim of 1 m positional accuracy or an ecological selection rule. No grid is dropped from the mammal ecological result.

## What a successful source check does NOT establish

Five anchors do not verify all 100 actual stations. A current coordinate does not verify which historical coordinate applies on each capture date. Product metadata does not demonstrate that a CHM tile covers a trap or that raster dates match capture dates. The public CHM has 1 m pixels in 1 km tiles, but pixel resolution is not point-location accuracy. The official geoNEON mammal code adds location uncertainty and distinguishes monumented from tape-laid stations; later habitat extraction must retain that uncertainty rather than assign every trap to one allegedly exact pixel.

No environmental response coefficient, habitat-conditioned recurrence, detection correction or competition effect is estimated here. Later extraction must use actual source-dated station records and declared raster CRS, cover and uncertainty; it must not synthesize trap positions by rotating an assumed grid around a plot centre.

## Repair verification

The four previously committed site-coverage tests first failed locally because the imported implementation was absent. The new implementation satisfies them without altering or removing those tests. Eight additional source-only tests cover named-location identity, ragged data, ambiguous history, unknown uncertainty, orientation checks and grid-specific issue counting. The dedicated workflow runs these tests before source retrieval; repository-wide checks remain a distinct verification.
