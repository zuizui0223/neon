# Seed-event coverage and seed-fate evidence: source reconciliation

**22 November 2026. Current interpretation for the single NEON manuscript, Draft / SUBMISSION HOLD.**

## 1. Decision

The three keyless rows in the Merz et al. station file are verified summaries, not three missing station-nights. The older strict test failed because it assumed that all 291 records were observations. Its historical failure remains recorded. The corrected source contains 288 unique station-nights followed by totals, differences and fractions.

The previously reported 806/2,581 = 31.23% quantifies seed-count loss on nights absent from the deposited **All Foraging Clean.csv** table. It is not the fraction of seed removal without footage. The station file labels 53 of those nights **Visitors**, accounting for 556 of the 806 units. The deposited tables have different coverage.

A geographically independent archive from Gu et al. (2025) separates two other recording states: an unassigned consumer and an unknown seed fate. These records support a measurement distinction. They do not identify the cause of NEON's seasonal capture-location recurrence. No NEON, Portal or Finnish biological effect was refitted.

## 2. Merz et al.: a resolved row classification and a corrected interpretation

### Source and arithmetic

Source: Merz, Record & Mortelliti (2026), [Ecology article](https://doi.org/10.1002/ecy.70312); [Figshare 28207769 version 2](https://doi.org/10.6084/m9.figshare.28207769.v2). Source files were retrieved from public provider endpoints and verified against version 2 file IDs, byte lengths and MD5 digests. The new receipt also records SHA-256.

The source inventory has 288 unique complete Grid × Site × Session × Night keys. Every one of the 3,243 All Foraging rows maps to one of 136 of these keys. The following three source records contain only summary fields:

| Summary row | White pine | Red oak |
|---|---:|---:|
| Offered / remaining totals | 4,280 / 2,049 | 955 / 605 |
| Difference | 2,231 | 350 |
| Difference / offered, source rounding | 0.521261682 | 0.366492147 |

The new code independently recomputes all these quantities from the 288 keyed rows, requires exact integer totals and differences, and verifies the rounded fractions within 10⁻⁹. A keyless row elsewhere, a partial key, a duplicate station key, an incorrect footer, or extra populated metadata on a footer causes failure. This is evidence for classifying these particular three rows. It is not a general rule for dropping incomplete observations.

The article reports 288 active station-nights and the same species-specific seed totals. Its author code, **Main Analysis - Clean.R**, calculates offered minus remaining at lines 1260–1264 and joins the station table by Grid_Month at line 1284. This inner join does not admit the summary rows. The community regressions additionally filter out seed-specific visitor values of None, zero deployment and missing responses at lines 1288–1289 and 1432–1433. The full field inventory and those regression samples should not be equated.

### Event-table coverage versus the station's visitor record

| Match in All Foraging | Literal Visitors? value | Station-nights | Nights with ≥1 missing unit | Pine missing | Acorns missing | Combined missing units |
|---|---|---:|---:|---:|---:|---:|
| Yes | Visitors | 136 | 131 | 1,564 | 211 | 1,775 |
| No | Visitors | 53 | 51 | 447 | 109 | 556 |
| No | None | 98 | 68 | 212 | 30 | 242 |
| No | NA | 1 | 1 | 8 | 0 | 8 |
| **Total** | | **288** | **251** | **2,231** | **350** | **2,581** |

The 152 nights without a matched event row still account for 806 missing units on 120 nights. But 556/806 = **68.98%** of these units are on nights explicitly labeled Visitors. Neither None nor NA is recoded into verified animal absence. We retain these exact source labels.

The new interpretation supersedes wording that could equate absence from the event file with absence of video. The source does not show whether a nonmatching record arose from inclusion rules, processing, annotation, an unrecorded visit, or a detector issue. The fraction combines pine seeds and acorns as counts, not food mass or energy.

### What remains unresolved

The methods describe evening deployment, motion-triggered images and 30-second video, and morning seed checks. Night.set and Morning.check are dates rather than time-of-day uptime logs. They establish scheduled overnight deployment, not uninterrupted detector operation. The raw event notes include a camera malfunction and proposed rain loss or unfilmed removal, but those notes cannot assign causes to the 806 units on different nights.

The article explicitly includes field losses with unknown removers in its community-level definition. It restricts its individual-level analyses to confidently identified on-camera interactions. These distinctions are published prior art. The earlier Date parsing discrepancies are not corrected by changing the interpretation of the footer, and no dates or identities were shifted here.

The old all-291-row gate and its archived outputs are preserved. Its row-type assumption is now diagnosed; it is no longer evidence that three station observations are missing. Continuous camera exposure and an event-table construction rule remain unverified.

## 3. Gu et al.: consumer identity and resource fate are different observations

Source: Gu, Yang, Dirzo & Zhang (2025), [Ecology and Evolution article](https://doi.org/10.1002/ece3.72409), [Figshare 29815622 version 2](https://doi.org/10.6084/m9.figshare.29815622.v2). The field study combined PIT tags on rodents and seeds, cameras, and searches for displaced seeds in a 30 m radius. Its published trait-matching results are prior art.

The public workbook has a Dispersal sheet and a separate Rodent survey sheet. The seed sheet records species in Dispersers but has no individual PIT column. A PIT column in the separate rodent sheet does not provide a seed-to-individual join.

All counts below are **archive rows**, not independent seeds, visits or animals:

| Dispersers record | Intact in situ (IIS) | Eaten in situ (EIS) | Eaten after removal (EAR) | Primary scatter-hoard (SHI) | Missing (M) | Blank fate | Rows |
|---|---:|---:|---:|---:|---:|---:|---:|
| Assigned species | 0 | 23 | 310 | 46 | 157 | 0 | 536 |
| Literal Not triggered | 0 | 2 | 54 | 4 | 23 | 0 | 83 |
| Blank | 106 | 0 | 0 | 0 | 0 | 13 | 119 |
| **Total** | **106** | **25** | **364** | **50** | **180** | **13** | **738** |

Thus **60 of the 83 Not triggered rows still have an assigned fate of eating or scatter-hoarding**, while **157 rows name a consumer species but have unknown seed fate**. The README does not define which sensor the Not triggered label refers to. It cannot be translated into a camera miss, animal absence or a detection probability.

The workbook contains **738 rows and 735 distinct seed codes**. Three codes each occur twice with nonidentical rows: one pair differs in dates and two in dates and fate. All rows are retained. We do not choose a first or last row as the true endpoint, infer a documented sequence of distinct encounters, or use 738 as a seed denominator. The published paper describes 736 seeds, while the supplied R code uses explicit count vectors without importing the workbook. These files do not document a mapping from the workbook rows to that analysis population. The discrepancy is a limit on reanalysis, not evidence of a particular source error or of invalid published results.

No new species-comparison coefficient, mechanism, seed-fate rate or individual-turnover effect was estimated.

## 4. Independent source screening and the next research boundary

Three systems independent of the Penobscot study were screened for original files and joinable observations. This is a bounded screen, not an exhaustive claim about all available data.

The [screening receipt](../results/neon_seed_fate_source_screen_20261122.json) records the Austrian and Panamanian original file checksums, headers, row counts and aggregate identifier counts. The Gu receipt below records the third system in detail.

| System and original source | Information actually available | Suitable use and missing connection |
|---|---|---|
| Sichuan, Gu et al. 2018–2019, Figshare 29815622 v2 | Seed-code rows, fate codes, disperser species, separate rodent PIT survey | The two-dimensional recording-state comparison above. No individual actor field in seed rows and a single seed station prevent a spatial actor-turnover test. |
| Austria, Sachser et al., four trial cohorts, [Biology Letters](https://doi.org/10.1098/rsbl.2024.0586), [S5 dataset](https://doi.org/10.6084/m9.figshare.28054281.v1) | S5 is a 32-row table of TRIAL, FATE, INEXSITU, NTOTAL and N; cohort totals 99 + 180 + 180 + 180 = 639 | Cohort-level fate summaries are possible. The released fate table lacks dish and seed IDs needed to join to individual camera deployments. Annual associations alone would not identify a patch mechanism. |
| Panama, Jansen et al., [Movebank archive](https://doi.org/10.5441/001/1.9t0m888q) | 1,649 timed locations of 224 radio-tagged seeds; movement-table identifier refers to the seed | Seed trajectories can be studied. This deposit does not contain the transporting mammal's identity or a row-level fate/termination crosswalk, so it cannot establish animal replacement at caches. |

**Current scientific action:** retain the seed studies as a bounded observation-process appendix. Do not add another ecological coefficient from the present event counts merely to obtain a mechanism. The main manuscript remains about taxon-associated capture-location recurrence among different observed animals.

The mechanistic comparison needed for that main question is specific: does a patch retain taxon-associated use when observed individuals change because its independently measured resource state persists, or because animals repeatedly transport resources there? A test requires spatial patch identity, dated resource state or tracked fate, and linked actor identity, with observation exposure appropriate to the question. None of the three deposits checked here supplies that complete linkage. The source search and distinctions are complete for this iteration; attribution of NEON recurrence remains open.

## 5. Reproduction and evidence

New reproducible code and aggregate results:

- [Merz reconciliation script](../analysis/reconcile_neon_figshare_2026_station_summaries_v1.py), [regression tests](../tests/test_neon_figshare_2026_station_summaries_v1.py), and [aggregate receipt](../results/neon_figshare_2026_station_summary_reconciliation_20261122.json).
- [Gu archive inspection script](../analysis/inspect_neon_gu2025_seed_fate_archive_v1.py), [regression tests](../tests/test_neon_gu2025_seed_fate_archive_v1.py), and [aggregate receipt](../results/neon_gu2025_seed_fate_archive_20261122.json).

The Merz script can retrieve its pinned public sources into a separate input directory. The Gu script reads the published workbook with openpyxl (verified with 3.1.5). Its input files are listed with IDs, URLs, byte lengths, MD5 and SHA-256 in the receipt. Save the versioned metadata response as Gu_v2_metadata.json.

~~~bash
python -m analysis.reconcile_neon_figshare_2026_station_summaries_v1 \
  --source-dir build/source/merz2026 --download \
  --output build/merz2026_station_reconciliation.json
python -m analysis.inspect_neon_gu2025_seed_fate_archive_v1 \
  --source-dir build/source/gu2025 \
  --output build/gu2025_seed_fate_archive.json
python -m unittest discover -s tests -p 'test_neon_figshare_2026_station_summaries_v1.py' -v
python -m unittest discover -s tests -p 'test_neon_gu2025_seed_fate_archive_v1.py' -v
~~~

Both reports were regenerated from provider-verified files and checked by a separate reviewer. The 13 focused tests cover footer reconciliation, inconsistent keys/counts, preservation of repeated seed-code rows and unknown categories, altered source bytes/version, and protection against overwriting source files through ordinary paths, symlinks or hardlinks. No original animal IDs, seed IDs, station keys, coordinates or raw source tables are re-exported in the receipts.

Historical results, including the 21 November 31.23% count, remain archived unchanged. The semantic correction is recorded here and in the current README/manuscript. The datasets' prior biological findings remain attributed to their original authors. No merge or submission.
