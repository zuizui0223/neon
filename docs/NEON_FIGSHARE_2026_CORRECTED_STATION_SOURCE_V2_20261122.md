# Corrected original Figshare 2026 source ontology and capture-year format: station × foraging × PIT structural v2

**22 November 2026. A CORRECTED, DISTINCT source-admissibility audit after original source-ontology forensics; no ecological outcomes opened.** The original immutable 21 Nov v1 all-291-station-rows gate **FAILED** and its red workflow, output receipt and design remain archived. We do **not** retroactively claim it passed. The corrected estimand is source-observation linkage, not a known camera-operable negative or a biological result.

## Why v1 is defective

The original article Merz, Record & Mortelliti 2026 *Ecology* DOI `10.1002/ecy.70312` reports **288 active station-nights**. The public original `All Station Nights.csv` has **291** rows: exactly **288 unique original `Grid×Site×Session×Night` records** FOLLOWED BY **three original source arithmetic summaries**. Our separate MD5-verified forensic validator `analysis/reconcile_neon_figshare_2026_station_summaries_v1.py` proves the three last rows are (a) offered/left totals, (b) differences, and (c) fractions, ALL numerically reproduced from the 288 station rows. They are not missing experimental observations, and do not enter the observed opportunity denominator. Any changed footer, duplicated complete station key, extra keyless row or bad seed count STOPS. Old v1 wrongly assumed all 291 were station observations.

The original `2016-2023 Capture Data.csv` uses literal `YEAR` values **16,17,...,23** and its original `DATE` values verify that these correspond to **2016..2023 for all 11,614 capture rows**. An old 4-digit parser produced 0 capture/foraging PIT×grid×year matches; source-verified year correction yields 2,077 matched video-event records. This is an observed SOURCE CODEBOOK correction, not an effect-driven recoding of animal identity.

## Exact unchanged source inputs and frozen quantitative criteria

Original public Figshare article `28207769 v2`: same original *five* MD5/byte-pinned CSVs and exact names/rows as source v1, full provider metadata version 2 verified EVERY run. This v2 code loads those originals through the existing checksum-pinned `load_five`. It reuses source-station footer validation from the independent reproducibility script, but never changes original source row/order/metadata. It is permitted to make a new representation `station_rows[:288]` only after the footer arithmetic and exact-row-position check succeeds.

**ALL original numeric source gates retained verbatim from the v1 design**:
1. >=100 unique original station-night keys with source Date parsed; ≥100 exact station-matched All Foraging events from ≥3 original forest grids.
2. >=30 original All Foraging events with exact original animal PIT×GRID×**verified calendar year** matching original capture history.
3. >=60 stations with numeric original WP and RO offered amounts; >=30 matched events with ≥1 numeric OBS seed availability.
4. >=50% of matched records with both original event and station Date parseable have EXACT source dates equal. NEVER recode ±1-day disagreements as matches.
5. Source camera-view mouse and vole subset files each contain ≥1 exact `Grid,Site,Session,Night,Visit.ID` key occurring in the combined All Foraging original events.

The original supplemental station summary check (WP 4,280 offered and 2,049 left; RO 955 offered and 605 left; corresponding differences 2,231 and 350) is exact numeric arithmetic. ALL 3 original footer rows must reproduce exactly with the strict validator, rather than trusting a given row count and dropping unknown observations.

## Corrected source-only interpretation

A v2 `SOURCE_GO` verifies **joinability of source-provided observation records**. It CANNOT establish video camera operational uptime, no animal presence on no-event nights, within-visit PIT sequencing, a valid animal-to-cache causal effect, independently measured natural food biomass, resource-driven seasonal NEON station recurrence, interspecific competition or learning. Original event data are 2023; original capture series 2016–23; two source files' date column semantics and ±1-day discrepancies remain unresolved. Same forest as the Gu paper? No: the Maine 2023 and 2026 *Merz* papers share Penobscot Experimental Forest, while Gu 2025 is in Sichuan. The two Merz studies are NOT independent geographical systems. Counts of mouse and vole taxon-specific views are subsets of All Foraging, not additional independent samples.

The code is versioned **v2**, retains old v1 result and red source-stop workflow unchanged and reports it as `historical_source_gate_stopped_due_to_invalid_row_and_year_model`. Failure of any corrected numeric threshold produces explicit v2 `SOURCE_STOP`. No probability model, source outcome `Seed.Found`, actual seed disappearance/consumption, animal position Z, p, regression coefficient or spatial niche discovery is computed.

Implementation `analysis/audit_neon_figshare_2026_station_event_capture_source_v2.py`; tests `tests/test_neon_figshare_2026_station_event_capture_source_v2.py`; workflow `.github/workflows/neon-figshare-2026-station-event-source-v2.yml`. Expected result output `build/neon_figshare_2026_station_event_capture_source_v2.json`, archived result `results/neon_figshare_2026_station_event_capture_source_GO_20261122.json` only if original MD5, source footer and strict v2 criteria pass. ONE NEON Draft/SUBMISSION HOLD.

## Actual original-source verification result (22 November 2026)

The [real Figshare v2 original-data Action 45009787639](https://github.com/zuizui0223/neon/actions/runs/45009787639) PASSED all nine synthetic v2 source-ontology tests and the original five source-file MD5/byte gates. The result was **`CORRECTED_SOURCE_JOIN_GO_NOT_DETECTOR_OPERATION_OR_BIOLOGICAL_EFFECT`**. This is a corrected **source feasibility GO**, not a correction to an animal effect.

- Original `All Station Nights.csv`: **291** source CSV records = **288** source-keyed station-nights + **three exact verified summary/footer rows**; **136** station-nights contain deposited event rows and **152** do not. All **288** have scheduled setup/check and numerical paired seed-offering fields; **136** have parseable `Date` metadata.
- Original `All Foraging Clean.csv`: **3,243/3,243** event records have exact keys in the verified 288 station roster, over **six** original forest grids. Among them **3,242** have at least one numeric observed WP/RO availability value, and **2,182** have a source original PIT tag (tag presence is not individual identity verification).
- Original capture history: **11,614/11,614** rows have verified source `YEAR 16..23` matching their own original `DATE` calendar year. **2,077** event records match original `PIT×GRID×calendar year` capture history; these are events, NOT 2,077 independent animals.
- For **3,232** event-to-station records with both source `Date` fields parseable, **2,443** exact day matches and **789** disagreements. The date-equality criterion is ≥50%; **75.59%** exact matched, so the unchanged threshold PASSES but does not resolve the disagreements. No ±1 day shift was imposed. Mouse view **883/883** and vole view **951/951** rows overlap the combined original event file by source keys; view files are not independent additional observations.
- Every original v1 numerical support threshold **9/9 PASSED** after correcting ontology and source-year encoding; original v1's red `SOURCE_STOP_ORIGINAL_STATION_NIGHT_KEY_MISSING` and original Python source are retained for provenance. The **archived v1 workflow** is now manual-only to avoid automatically rerunning an invalid observation-row assumption, while the **corrected v2 workflow is an active push/PR check**. No true animal absence, independent camera functioning, natural resource biomass, memory, social contact, competition or animal spatial niche is inferred.

Permanent anonymous JSON receipt: `results/neon_figshare_2026_station_event_capture_source_GO_20261122.json`.
