# Original 2026 Penobscot vole/mouse repeated patch-use SOURCE gate — prior resource experience versus new patch

**Date 22 November 2026.** Current unified NEON ecology PR #23 Draft, SUBMISSION HOLD. This test design is frozen **after the original Merz et al. (2026) Figshare source structure was already known**, but BEFORE opening any new within-PIT repeated-patch support, visit-time sequencing, availability effects or resource/animal response coefficients.

## Biological problem

Mammal space use can be drawn repeatedly to a known profitable patch either because of **spatial learning, an unchanged resource distribution, inherited home-range overlap or observational/camera attractiveness**. To distinguish mechanism, a genuine *within-individual* return needs (a) known previous visits, (b) actual same physical patch locations, (c) their documented availability on later nights, (d) alternative simultaneously offered patch opportunities, and (e) an independent camera-effort measure. An observed *return* would be **a proxy for prior encounter**, not experimental memory. The Merz et al. 2026 paper already published personality, resource/seed finding and environmental models; those effects are PRIOR ART.

## Fixed authoritative source, before structural values

Same Figshare `28207769 v2`, original 5 exact MD5/SHA256/row-pinned CSVs as [source v2 GO](../results/neon_figshare_2026_station_event_capture_source_GO_20261122.json). Exact original `All Foraging Clean.csv` (3,243 source interaction rows), `All Station Nights.csv` (288 original confirmed keyed experimental records + 3 verified final mathematical footer summaries) and original `2016-2023 Capture Data.csv` PIT source. Do not reimport other studies or alter any original records.

## Source definition, not the mammal ecological response

- The original **event/visit unit** is the literal complete tuple `(Grid,Site,Session,Night,Visit.ID)`; **3,243 rows are interactions, not 3,243 visits or animals**. Count exact distinct visit IDs and repeated rows per visit; inspect whether original PIT, Date and Time.start are consistent WITHIN each visit, with conflicting keys flagged and excluded from a *future* source-eligible visit population. No probabilistic PIT aliases. Do not export literal original tags or station names.
- The original location for a potential repeated visit is `(Grid,Site)`, but **repeated labels must be independently validated as stable physical patch coordinates across distinct nights**, else they are only repeated literal location keys. This source gate will use exact literals and explicitly NOT claim physical continuity.
- Use original source `Date` only as published. Preserve 789 known same-event vs station-record source date discrepancies as a non-resolved separate source metadata issue; never infer ±1 day shifts. Original station `Night.set` and `Morning.check` are source dates, not camera-on timestamps; never use them as verified camera uptime or independent animal absence.
- For each **source PIT**, count distinct original visit IDs, distinct source station-night keys, distinct event-record dates, and whether two exact visits to the SAME `Grid×Site` appear on at least two DISTINCT source dates (not the same video/seed interaction repeated). Count number of source PITs with such repeated-patch use and number of grids, and only event rows with original numerical `WP.available.OBS` or `RO.available.OBS` available. Do not inspect actual availability magnitudes yet.
- For each original source `Grid×Session×Night` with at least one observed PIT visit, count whether there were **two or more simultaneously installed original station/site keys** in the 288 validated station rows. This establishes structural possible alternative stations, not that individual animal could perceive or reach them.
- Original `Time.start` and `Time.end`: **only inspect patterns, parseability and within-composite-visit consistency**. Report coarse formatting classes and counts, not timestamps, durations, source hours, event outcomes or animal data. Do NOT treat `Visit.ID` numeric ordering as chronological unless author source verifies it.

**Original pre-outcome feasibility GO only if all:**
1. ≥100 source visit composites with one nonempty PIT and unambiguous original `Date`/start-time metadata.
2. ≥15 original PITs seen across ≥2 original source visit composites in ≥2 distinct station-night keys.
3. ≥8 original PITs seen at the SAME literal `Grid×Site` on ≥2 different event dates, spread over ≥3 original grids.
4. ≥50 original PIT-linked *repeated-patch visit composites* with numeric original observed source seed availability at those repeat events.
5. ≥20 original `Grid×Session×Night` source occasion groups containing ≥2 different station-night `Site` keys so alternatives could exist.
6. At least 80% of source visits with nonempty PIT have internally consistent single PIT + Date + `Time.start`; and ≥80% of those have a syntactically parseable local clock (ISO full-time or 24-h HH:mm[:ss], or AM/PM 12-hour).

These thresholds test suitability for future within-individual resource-mediated return analysis, **not statistical significance**. If any fail: explicit SOURCE STOP, no post-result threshold rescue. Even if all pass, a causal *learned* memory interpretation still requires bait randomization/reward reversals and known station opportunities/continuous operation.

## No ecological effect unsealing

Do not use `Seed.Found..Y.N.`, `Time.searching`, `Eat..disperse..reject..or.move`, or any response. Do not estimate observed vs expected return effects, niche stability, seed-biomass effects, individual cognition, social attraction, competition or between-species differences. Do not use original 2023 (2018) study as an independent replicate (both Merz papers from same forest). Primary target is **source eligibility for nontrivial mechanistic sequencing**, not another method-only paper or unconstrained data search.

Code: `analysis/audit_neon_figshare_2026_repeat_patch_visit_support_v1.py`; tests; GH Action; anonymous aggregate source receipt. Draft / SUBMISSION HOLD regardless.
