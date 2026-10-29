# NEON: exact original season-pair overlap of two independent environmental source systems

2026-10-28, one integrated mammal macroecology paper PR #23, DRAFT/SUBMISSION HOLD.

## Exact known data support

- Frozen original 58 mammal seasonal comparisons in 30 mammal grids across 14 independent NEON sites, using checksum-verified DP1.10072.001 RELEASE-2026. The original corrected 14-site genus-associated capture-location recurrence mean Z=+0.795 remains observational, not a causal habitat or detection claim.
- Original NEON AOP DP3.30015.001 environmental source: 51 original provider-size/checksum verified CHM tiles, 24,600 real original station×capture-date pixels, 36 of 58 original pairs all six days within +/-12 calendar months of the independently selected closest acquisition, across 12 physical sites/21 grids; 22 within +/-3 months; stricter prior/same-month 18 original pairs across only six independent sites.
- Original field-plant DP1.10058.001 source: 326 original MD5-verified 1m2 files, 355,486 dated rows, original exact same-site plotID vegetation survey present in 30/30 mammal grids. Two DISTINCT numerical percentCover field events within +/-365 days of respective mammal seasons: 51 original pairs across 14 sites/28 plots; stricter +/-90 days: 16 pairs in seven sites/11 plots.
- The prior inference of 29 to 36 original pairs with *both* loose sources was a mathematical set bound only. The exact intersection is not yet known. This single source-only audit will establish it.

## Exactly one source-only test; no biology refits

1. Reconstruct all 58 original source season-pair keys, six original actual capture dates per pair, 30 grid plotIDs and 14 physical sites. NEVER select animal source units by the previously inspected positive Z.
2. Query official released AOP site-month metadata and require its **original canonical SHA256 digest** plus 97 original site-month visits and 36/22/18/10 original time-eligibility counts. Use the original closest-calendar-month source rule with an earlier-month tie. The immutable prior actual raster receipt guarantees source 100/100 pixel status for all original source-eligible 36 pairs; do not re-download or reselect original CHM values simply for a pair-key join.
3. Retrieve the exact original plant provider manifest and require identical digest, file universe 326 and byte sum 131,730,791. Download only immutable original MD5/size-verified official plant files, parse original source plotID/endDate/eventID/numerical-cover *presence* exactly as in prior successful source test; require prior 51 and 16 pair totals to reproduce.
4. Compare individual source Boolean eligibility for EACH of the 58 original seasonal pairs, not aggregate estimates. For CHM source periods report within +/-12, +/-3, pre-/same-12, pre-/same-3 months. For field plant source report distinct numerical-cover observations at nearby base plots within +/-365 or +/-90 days. Export only class totals, independent site counts and mammal grid count; no site IDs, trap names, animal tags, dates, raw percent cover or source height arrays.
5. An exploratory descriptive **joint source** GO has unchanged minimum 20 original pairs, eight independent physical sites, 12 original grid plotIDs, and does NOT authorize causal ecological fitting or retrospective p-value hunting. Every strict temporal source failure remains visible.

## Critical spatial and causal distinction

NEON mammal grids and distributed plant-base plots with matching plotIDs typically lie 150 +/- 50 m apart. The plant field survey therefore measures surrounding landscape vegetation, not exact small mammal trap-level understory. CHM estimates tree canopy top, not low shrub or ground cover, and the 1m cell size is smaller than positional uncertainty. Neither source provides animal presence independent of the Sherman trap; NEON DNA barcode and pathogen data derive from the same captured animals. A detection-corrected latent spatial niche inference cannot be established from these environmental streams plus the known capture-space matrices alone.

Official NEON sampling descriptions:
https://www.neonscience.org/data-collection/small-mammals
https://data.neonscience.org/data-products/DP1.10058.001/RELEASE-2026
https://data.neonscience.org/data-products/DP3.30015.001

Code: analysis/neon_joint_environment_source_crosswalk_v1.py; analysis/run_neon_joint_environment_source_v1.py; tests/test_neon_joint_environment_source_crosswalk_v1.py; .github/workflows/neon-original-joint-environment-source.yml. Aggregate output build/neon_joint_chm_plant_exact_pairs_source_20261028.json.
