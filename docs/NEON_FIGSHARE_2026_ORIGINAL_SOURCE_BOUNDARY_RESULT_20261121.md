# NEON × Figshare 2026: measured seed-use observations versus field-capture histories — source audit verdict

> **22 November 2026 correction.** The three trailing keyless records have now been verified as totals, differences and rounded fractions, matching the 288 actual station-nights and the published paper. The old all-291-observation gate failure remains historical; it is not evidence for three missing station observations. Moreover, 53 of the 152 nights absent from All Foraging are labeled Visitors in the station file and account for 556 of the 806 missing seed units. Absence from the deposited event table does not establish absence of footage. See the [current reconciliation, independent seed-fate comparison and reproducible results](NEON_SEED_EVENT_FATE_RECONCILIATION_20261122.md). The material below preserves the 21 November interpretation for provenance.


**Date: 21 November 2026. Source-only original-data audit, NOT a newly discovered mammal mechanism. Single integrated NEON PR #23 Draft, SUBMISSION HOLD.** Original article Merz, Record & Mortelliti (2026), *Ecology*, DOI `10.1002/ecy.70312`, Figshare article `28207769 v2`. Same Penobscot Experimental Forest as the 2018 experiment published in 2023; **NOT an independent geographic replication**.

## Completed source originals

Original provider metadata and all 5 original Figshare CSV byte lengths/MD5 were verified in [GitHub Actions 44855895483](https://github.com/zuizui0223/neon/actions/runs/44855895483). The original original-data census is exactly:
- **11,614** individual-capture rows, 2016–2023, with original `PIT, GRID, YEAR, DATE`.
- **3,243** combined foraging camera-event rows, **all original event dates in 2023**, containing `PIT, Grid, Site, Session, Night, Visit.ID` and observed/predicted seed availability.
- **291** station×night-source rows containing station/night identity, seed-set values and date metadata.
- **883 mouse** and **951 vole** foraging rows, which are **overlapping views of the 3,243 original combined foraging rows**, not additional independent events (exact original station/visit-key matching showed 883/883 and 951/951 belonged to combined table).

Frozen original five-file header/byte receipt: `results/neon_figshare_2026_mouse_vole_original_CSV_schema_GO_20261121.json`.

## Source structure and why pre-frozen data admission STOPPED

The original STRICT source gate `docs/NEON_FIGSHARE_2026_STATION_NIGHT_ID_SEED_SOURCE_GATE_20261121.md` required every one of 291 `All Station Nights.csv` rows to provide original `Grid×Site×Session×Night` keys without duplication.

[First source workflow 44856095291](https://github.com/zuizui0223/neon/actions/runs/44856095291) failed closed at `ORIGINAL_STATION_NIGHT_KEY_MISSING`. Two separate MD5-pinned original-source diagnostics, including the [repeat after header-check 44856270587](https://github.com/zuizui0223/neon/actions/runs/44856270587), established:
- **288/291** station-night records have all four keys and **zero duplicate keys**. **3** rows have *none* of the four key components but DO contain nonempty values in other columns: two have **2** other nonempty cells and one has **4**. These are **not safe to discard as blank rows** without documented provider handling.
- Only **136/288** keyed station-night source rows have parseable original dates. Thus 291 original records are not the same as 291 independently verified dated operational camera nights.
- All original **3,243 combined foraging event rows** had complete key source fields and matched one of **136 distinct** original keyed station-night records across **six** original field grids. This is a valuable structural mapping, but does NOT change the strict 3-keyless-row source STOP.
- Source seed-set fields `WP.seeds.set` and `RO.seeds.set` were both numeric in **288** keyed station-night rows; **3,242/3,243** original events had at least one numeric *observed* seed-availability field `WP.available.OBS` or `RO.available.OBS`. These are experimentally set baited seed tray offerings and recorded quantities, **NOT natural standing plant biomass or rodent food availability across the forest**.
- Of **3,232** foraging records with both original event and station-night dates parseable, **2,443** original dates were equal, **434** event dates were exactly +1 day, **333** were −1 day, and **22** differed by >3 days; 11 original event comparisons lacked at least one date. A ±1-day shift may involve overnight camera timing but has **NOT** been imposed, and >3-day discrepancies remain unresolved.
- Of event records, **2,182** had original source PIT; across combined events there were **47 literal original PIT identities**. **44** of those original PIT values were also present in the original capture table. Original mouse and vole foraging files overlap the same combined table, not independent replicate experiments.

All these are anonymous *source metadata* counts, without any seed-choice, seed-finding, behavior, risk, personality or ecological effect estimate. Preserved source results: `results/neon_figshare_2026_original_station_key_diagnostic_20261121.json`, `results/neon_figshare_2026_after_stop_structural_coverage_20261121.json`.

## Original capture YEAR encoding: a source-format error, not no animal overlap

An initial strictly literal `PIT×GRID×4-digit YEAR` source join reported 0, which would have been misleading. Re-reading the original **DATE** metadata for all 11,614 capture rows proved original source `YEAR` uses two-digit **16,17,18,19,20,21,22,23**, matching calendar **2016,2017,2018,2019,2020,2021,2022,2023** exactly (corresponding rows 2,268 / 963 / 2,264 / 522 / 2,994 / 942 / 1,009 / 652). The original 2026 foraging events all have calendar year **2023**. An independent, post-STOP source-format diagnostic used ONLY source-verified `YEAR` ↔ `DATE.year` agreement to construct equivalent calendar-year source keys and found **2,077/3,243 combined foraging events match an original capture record by PIT×GRID×calendar year**, and **2,125** event rows match an original capture PIT alone. This verifies source linked animal identification, NOT the order or nature of an individual’s history, learning, survival, site fidelity, or independent camera detection.

Original diagnostic [run 44856690988](https://github.com/zuizui0223/neon/actions/runs/44856690988), original two-digit metadata verification [run 44856629132](https://github.com/zuizui0223/neon/actions/runs/44856629132); machine receipt `results/neon_figshare_2026_capture_PIT_year_format_diagnostic_20261121.json`. **The original strict station-night source STOP has NOT been relaxed or retroactively claimed passed**.

## Ecological interpretation: what is measurable and what remains unknown

This real field series offers independently recorded **baited food-patch visits, known offered seed states, captured PIT individuals and potential camera night metadata**. The original 2026 article already analyzed seed-finding effectiveness and environmental/individual differences; those published relationships are PRIOR ART. The source tests currently establish *feasibility of aligning identifiers* for a future **bounded** detector/foraging question only. They DO NOT:
- identify direct naturally occurring rodent food/seed biomass or vegetation resources at NEON trap locations;
- provide continuous independently verified at-risk and operational camera observation effort or show no-visit = true absence at each station-night;
- demonstrate interspecific competition, learned spatial memory, social interactions or true unbaited home-range movement;
- justify pooling the 2018 Figshare 2023 seed type `WP/BF` study and 2023 Figshare 2026 `WP/RO` source as identical resource treatments, nor treat those overlapping same-forest studies as geographically independent replications;
- replicate the NEON 14-site genus fixed-margin capture-station Z or revive the failed density 5/8 genus generality rule.

**Scientific decision:** do not fit an ecological effect on a source STOP as though it were confirmed camera-effort-calibrated spatial use. Keep the corrected original available-data distinction in one unified manuscript appendix/source audit, leave main positive/negative NEON/Portal/Finland claims intact, and remain **SUBMISSION HOLD**. A transferable resource×competition×learning principle will require independently measured natural food resources, matched true use/detection effort and testable individual experience in *geographically independent* systems.

## Evidence and code

- `docs/NEON_FIGSHARE_2026_MOUSE_VOLE_FORAGING_SCHEMA_GATE_20261121.md`
- `docs/NEON_FIGSHARE_2026_STATION_NIGHT_ID_SEED_SOURCE_GATE_20261121.md`
- `analysis/audit_neon_figshare_2026_original_foraging_schema_v1.py`
- `analysis/audit_neon_figshare_2026_foraging_station_effort_ID_source_v1.py`
- `analysis/diagnose_neon_figshare_2026_missing_station_night_keys_v1.py`
- `analysis/diagnose_neon_figshare_2026_after_source_STOP_join_support_v1.py`
- `analysis/diagnose_neon_figshare_2026_PIT_capture_date_key_format_v1.py`
- `results/neon_figshare_2026_mouse_vole_original_CSV_schema_GO_20261121.json`
- `results/neon_figshare_2026_original_station_key_diagnostic_20261121.json`
- `results/neon_figshare_2026_after_stop_structural_coverage_20261121.json`
- `results/neon_figshare_2026_capture_PIT_year_format_diagnostic_20261121.json`
