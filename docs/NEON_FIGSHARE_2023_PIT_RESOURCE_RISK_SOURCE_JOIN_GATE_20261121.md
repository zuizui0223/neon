# 2023 Figshare voles: effect-blind resource × risk × individual source linkage gate

**21 November 2026; frozen after original three CSV MD5+header GO, BEFORE examining source biological response values or any outcome association.** The original 2023 analysis already published personality, resource availability and predation-risk results. This audit is only a concrete independent biological *measurement feasibility* check for the NEON ecological mechanism programme. The ONE unified NEON manuscript stays Draft / SUBMISSION HOLD.

## Original source lock

Use official Figshare article **21512436 v1** only, exact three original files and provider MD5/bytes pinned at `docs/NEON_FIGSHARE_2023_ORIGINAL_CSV_SCHEMA_GATE_20261121.md` and `results/neon_figshare_2023_original_csv_source_GO_20261121.json`. These original 2023 files contain:
- `2018 Vole Seed Data.csv`: original **603** event rows, original **26 named columns**, notably `PIT` (animal identifier), `SESSION`, `GRID`, `SITE_ID`, `TREAT`, `WP`, `BF`, `PercWP`, `PercBF`, `PropWP`, `PropBF`, `Moon`, `PRED_PRES`; do not infer units from abbreviations.
- `Vole BLUPS.csv`: original **1069** rows, `PIT` + seven original behavioral BLUP variables; a single unlabeled first CSV column excluded from biological joining, with original CSV preserved.
- `Vole Personality Data.csv`: original **3712** rows, `PIT`, `SESSION`, `YEAR`, `GRID.x` and original behavioral testing fields.

Original primary article describes six grids, paired seed-access patch treatments, 603 small mammal visits, 306 seed selection events by 16 known-personality voles; those numbers are **published prior art**, NOT verified sample joins. Published 2023 personality and patch-risk effects are prior art. Original source only for one 2018 experiment; 1069 BLUPS are NOT 1069 seed-using individual voles.

## Fixed source-only support checks

Download only the same exact source bytes and MD5 using existing `analysis/audit_neon_figshare_2023_original_csv_schema_v1.py`. After verifying original row counts, extract **structural join keys and non-response availability only**. Never compute mean response, seed choice, effects or conditional preference.

- Treat the exact literal `PIT` as an animal identifier after trimming whitespace; absent/NA/NAN/NULL/N/A/UNK/UNKNOWN (case-insensitive) excluded. Do not coerce numeric identifiers, strip leading zeroes or infer aliases. Count original exact PIT matches event→BLUPS, event→personality, and all three. **Do not export any original PIT or exact capture coordinates.**
- An original event-eligible structural record requires nonempty `SESSION,GRID,SITE_ID,TREAT`; valid literal PIT, and BOTH `WP` and `BF` parsable as finite nonnegative source numbers. These source fields are potential quantities but NO units or availability semantics inferred; preserve headers and their documented categories only, no mean values. Note `WP`/ `BF` may be quantities of separate original offered seeds, not individual natural food supply.
- Count exact original `SESSION` categories, `GRID` categories, `SITE_ID`-within-`GRID` station keys, `TREAT` categories and original independent PIT IDs. A 603-row table is a record of events, not 603 separate individuals. Original `SITE_ID` might represent a paired manipulation vs distinct physical patch; do not interpret it as an independent wild home range.
- Require >=8 distinct original PIT IDs in eligible events with BLUPS and original personality records; >=30 eligible exact-PIT matched original event rows, >=3 original grids, >=10 original `GRID×SITE_ID` source location keys, >=2 `TREAT` categories, >=2 distinct `SESSION` categories, and >=30 event rows with numeric both seed availability fields. If not, **SOURCE STOP**. These permissive feasibility minima are fixed BEFORE the actual row support values are opened. They are NOT significance gates.
- Additional strict structural audit: each original first-blank BLUPS unnamed column ignored; `PIT` may appear in multiple BLUPS rows, in which case report duplicate PIT count and **do not claim one-to-one** personality effects. `PIT` in personality records may have repeated SESSIONs; no merging by SESSION unless the original code describes exact keys. Species/raw seed-selection/camera outcome fields `Seed_Choice`, `Choice_YN`, `Amt_Consumed`, `Dispersed` and risk-associated outcomes will **not** be opened or exported.

## Consequence, regardless of source GO

SOURCE GO means physically matchable animal ID, recorded seed information and patch/risk labels in published 2018 field experiment. It **does NOT demonstrate competition**, since this source manipulates cover/risk rather than species competitor abundance; **does NOT demonstrate learning**, since randomized experience/reward change is unavailable; **does NOT demonstrate repeated animal space-use independently of capture** across seasons, since cameras/RFID at food baits are only local stations and this event table has no explicit dated per-visit timestamp or camera-active exposure denominator.

The strongest possible claim from this source is observational and mechanistic *measurement feasibility* in a small independent experiment, with all source ecological directions already published. Do not pool 2023 animal events with the 2026 Figshare paper's 2016–2023 voles as independent replicates without original PIT/time overlap audit. The original NEON site-station Z, Portal site-stake reference null and 2022 temporal-year failure remain intact.

The source-only runner `analysis/audit_neon_figshare_2023_individual_resource_risk_join_v1.py`, synthetic tests and separate workflow should export only anonymized structural counts and exact source receipt. After source STOP or GO the one integrated manuscript remains **SUBMISSION HOLD**.
