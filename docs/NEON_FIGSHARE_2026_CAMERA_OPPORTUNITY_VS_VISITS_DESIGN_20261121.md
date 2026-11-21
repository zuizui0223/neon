# Camera source-opportunity identifiability: original station-night event/metadata cross-tab

Date 2026-11-21. **After** source-only Figshare 2026 five-file original MD5/schema GO, the separately frozen all-291-station-row structural SOURCE STOP, and the diagnostic that exactly 3 source rows are keyless but have other populated cells. Before any original foraging seed-finding or species/animal outcome is computed. One NEON Draft PR #23, SUBMISSION HOLD.

## Scientific decision
A table called "All Station Nights" is **not automatically 291 independent camera-on zero/positive nights**. Need determine whether non-visit station-nights have contemporaneous original night setup and morning check evidence and whether the row Date is observed independently of visit recording. A camera/seed-visit event file built from positive video clips cannot be used to assign absences unless original non-visit exposure was known and effort-complete.

## Source-only exact original data
Figshare public original article `28207769 v2`, published paper DOI `10.1002/ecy.70312`. All five already-pinned original CSV file IDs, original byte-size/MD5 check each run. In `All Station Nights.csv` use the **literal exact** trimmed `(Grid,Site,Session,Night)` source key, require 288 unique full-key rows, 3 keyless original records with 2/2/4 other populated cells (no unilateral source drop). `All Foraging Clean.csv` provides 3,243 video/event rows and 136 exact source keys known by previous diagnostics.

**Frozen before opening this cross-tab:**
- For 288 complete original station keys, stratify by whether that exact source key occurs in original All Foraging events, then report only **number of station-night keys** for each group with (a) original Date parseable, (b) nonmissing Night.set, (c) nonmissing Morning.check, (d) both Night.set and Morning.check, (e) numeric `WP.seeds.set` and `RO.seeds.set` availability (not actual seed quantity).
- For the 3 keyless original rows, report ONLY the names of their nonempty columns and source row index/order, not values, original IDs, amounts, dates or individual names. This is a transparent diagnostic of record types, NOT a retrospective permission to delete source data.
- A **predeclared independent camera-opportunity admission** would require >=100 original keys WITHOUT known visits with both setup and morning check nonmissing, and direct verified camera-on times/exposure for each. This diagnostic only tests the first **necessary** condition; raw camera downtime still unknown. Even if setup/check are complete, still no detection probability or natural forest rodent occupancy.
- **Particularly important:** if original `Date` is populated only on records known to have event visits and is mostly missing for original no-event station nights, then this `Date` is **outcome-conditioned metadata** and cannot be used to construct an unbiased time-dated station opportunity frame; record that as source/data-model limitation, not generalize from positive-only camera sample.

No species, no PIT, no event duration, no seed found/predation/consumption, no capture data, no learning model, no original mouse/vole foraging effects; no causal ecological inference. Original "301/291/288" cardinality and STOP maintained, no source rescue by dropping 3 keyless records. Source R original code and official paper methods may be used to verify timestamp semantics before any substantive analysis.

Code `analysis/diagnose_neon_figshare_2026_station_effort_vs_visits_v1.py`, workflow and aggregate receipt. Any source-only finding is an observation-validity condition only; one NEON manuscript Draft/SUBMISSION HOLD.
