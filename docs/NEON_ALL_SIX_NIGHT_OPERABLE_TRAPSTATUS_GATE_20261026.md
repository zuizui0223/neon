# NEON small-mammal ecological detection-process stress: truly set/empty or capture-coded trap nights
**One observational sensitivity locked on 26 October 2026, after old 3+ and exact-two positive genus×trap recurrence and after source-only recorded-station analyses, but BEFORE inspecting any new fully operable trap-night subgroup or ecological result.**

## The competing causal explanations

A persistent genus-to-exact-trap capture signature may represent **stable animal use of microhabitat** OR **stable genus-specific catchability**. The previous six-night "recorded trap station" control used row presence as a proxy for sampling opportunity; *record existence is not proof a trap was operating*. The official NEON box-trap `trapStatus` controlled vocabulary distinguishes:
- `4`: more than one capture in a trap;
- `5`: capture;
- `6`: trap set and empty;
- `0`: no data;
- `1`: trap not set or capture not processed;
- `2`: disturbed / closed but empty;
- `3`: door open with spoor.

**Single question:** Does the originally observed positive genus-to-same-station seasonal capture recurrence persist when only stations documented with `trapStatus ∈{4,5,6}` on **ALL SIX original sampling nights** are retained?

Source: [NEON small mammal Data Guide](https://data.neonscience.org/api/v0/documents/NEON_smammal_userGuide_vF?inline=true), [NEON official June 2026 tutorial](https://www.neonscience.org/resources/learning-hub/tutorials/mammal-data-intro) and [NEON small-mammal QC protocol status codes](https://data.neonscience.org/documents/10179/2403599/NEON.DOC.001244vA/216e7fc2-db72-4686-9302-e64d4cc42080?version=1.0). The semantics must be checked against downloaded categorical codes when available; numeric codes 0–6 are not a continuous measurement.

## Phase 1 — entirely effect blind and source fixed

1. Rebuild checksum/size-verified `DP1.10072.001 RELEASE-2026`, original **158** exact-two-genus season-pair source cohort in **30** independent physical sites/15 ecological domains with original shared-tag deletion, minimum two season-exclusive animals per genus and original ≥2 occupied stations per genus and season. Original **58** ≥3-genus results and historical W/B **5/8 vs6 FAIL** stay untouched.
2. Preserve original six `nightuid` sets (three consecutive nights per sampled bout) and exact original 10×10 trap names; do not impute lost trap rows. Derive each row's `trapStatus` primary one-digit canonical code. Noncode, missing or conflicting status is UNKNOWN. For any station×night with multiple source rows, retain only if **EVERY valid row** is one of 4/5/6; if any 0/1/2/3, UNKNOWN or inconsistent row appears, exclude the station×night conservatively.
3. Station common-operable set `E6=intersection_{all six nights} {stations whose ALL rows show 4,5,or6}`; report distribution of |E6| and aggregate status frequencies for all 158 original comparisons. A `6` row explicitly signifies "trap set and empty", not "no data"; a `4/5` capture does not prove the trap was operable for every minute but is evidence it functioned when checked.
4. For each original pair, restrict both tag-disjoint genus×station binary incidence matrices to `E6`. Keep only pairs with **|E6|≥90** and >=2 occupied stations in EACH season for both original genera. **Stop before new observed cross-season overlap** unless ≥**80** original pairs, ≥**18** physical sites and ≥**10** NEON ecological domains satisfy this unchanged source qualification. These thresholds are newly frozen post-result support safeguards, not retroactively part of the previous original 58/158 finding.
5. Report all source excluded pairs and reasons, including code frequency, missing/unknown and station-night conflicts; only aggregate counts, never animal tags, genus/source-site IDs, original dates/locations, URLs. A pair failing quality has **no valid estimand**, never zero ecological recurrence.
6. Do not inspect any new genus×season overlap or select source events by old positive Z, geographic latitude, temperature, or favorable taxon identity. `trapStatus` QC is the only new explanatory axis.

## Phase 2 — only if source stage GO

- On exactly the Phase 1 qualifying pairs, recompute the *same* exact uniform two-row genus×station fixed row/column-margin null of previously committed `analysis/neon_exact_two_row_fixedmargin_v1.py`. Before computing a new observed exact overlap, require **≥75%** positive exact-null variance, **≥40** informative pair units and **≥12** physical sites. If not, STOP and retain phase 1 receipt.
- Score `O=sum_{g,t} A[g,t] B[g,t]`, `Z=(O−E_0O)/SD_0O`; retain every sign, with equal weighting by original physical site rather than by trap/pair count.
- Calibrate one-sided excess via 20,000 exact-margin unit-product and 20,000 within-site perfectly rank-comonotone null draws, seeds **2026102662/63**. The second scenario is a dependence stress **not** an upper bound over all real site dependencies and neither approach models genus-specific catch probability or true habitat.
- Source-only leave-entire-physical-site-out reused site×plot×season-key sensitivity defined across all original 158 two-genus pairs **before** new O, conditional on ≥8 remaining independent physical sites and ≥20 informative original pairs. Otherwise report STOP. Do not choose alternative cutoffs after seeing effects.
- If positive site mean Z and both conditional p<0.05 and source-sensitivity positive as in the original, describe **recorded function-confirmed 4/5/6 station support** as compatible with the earlier positive capture-space recurrence. This would reduce a trivial "not set/disturbed trap" explanation, **but would not isolate habitat filtering from genus-dependent trap attractiveness/catchability**.
- Any negative or unsupported finding must be preserved as a limit, not trigger subgroup/year/threshold search or a different trapStatus interpretation.

## Mechanistic interpretation and single-paper boundaries

Codes 4–6 capture **operational status evidence** but do not estimate the probability of an individual being available for trapping, within-night closure/visit history, species-specific trap shyness, ground vegetation preferences or unobserved foraging movement. Repeated tags are still **observed**, not complete population census. If this test holds, **one observation-process confound is reduced**; if not, source record/operability heterogeneity remains a genuine alternative.

Neither result proves microhabitat use, spatial niche, interaction-driven coexistence, demographic turnover, territory or 10m patch generality. The previous **10m neighbor-scale test p=0.221** after reused-season site exclusion remains **not robust** and must not be rescued. The prior 79/80 temperature-QC source gate remains STOP; do not borrow flagged data or fit alternative weather.

This belongs in the **one NEON unified macroecological manuscript** `manuscript/NEON_SPATIAL_MACROECOLOGY_UNIFIED_V0_5.md`; the active next biological question remains *why* genus-conditioned capture-space occupancy recurs across individuals. A future true habitat-vs-catchability attribution requires an independently observed detection stream or measured station habitat at source-dated trap locations, not further null-model tuning on historically inspected captures.
