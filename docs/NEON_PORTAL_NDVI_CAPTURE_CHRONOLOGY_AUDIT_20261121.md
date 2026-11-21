# Portal 2022→2023 NDVI versus capture chronology: fixed source-only falsification audit

Date: 2026-11-21; Draft NEON PR #23. **This chronology audit is explicitly after observing both the 2020–25 rodent outcome and the site-level Landsat8 2022→23 NDVI decline. It is a check of causal ordering only, not a preregistered ecological test or a new biological finding.**

## Problem

The earlier note linked the **start-year 2022→2023** dependence of a captured-rodent community composition model to the **July–September 2022 versus July–September 2023 site-wide NDVI** difference (2023–2022 = −0.10156). This may be a **chronological error**: some 2023 capture dates may precede or overlap the 2023 July–September satellite observation interval. A later environmental measurement cannot be offered as a preceding cause of an earlier capture-composition change.

This audit examines only source census dates, plant survey seasons and original **identity-eligibility counts**; it does NOT compute any rodent taxon-composition response Y, plant-count predictor X, old regression coefficient, per-plot biomass, learned memory or station recurrence.

## Immutable source, unchanged cohort

Original `weecology/PortalData` immutable commit `afd75933249ae60f3a5e9dab00b354f219e5e045`, all EIGHT original file Git blob checksums verified using `analysis/portal_external_id_niche_source_v1.py` plus `analysis/audit_portal_resources_competition_learning_source_v1.py`. The original 203 plot×same-month adjacent-year source pairs have >=12 actually censused 0.25m² plant quadrats in a field survey completed before each capture and within the preceding 90 days. Apply original `fixed_capture_events`, `strict_plant_match`, original authoritative target granivorous taxon codebook, exact capture IDs/stakes and >=5 distinct valid tagged target individuals **in BOTH** original censuses to recover **exactly the same 114 model-entry plot-month-year pairs at 18 original plots**. Exclude source IDs with conflicting taxon assignments within a census as the original model did; do NOT remove cross-year shared IDs for this whole-community response because the original model did not. Require the original 65/114 2022 start-year split and 203 pre-animal source denominator. Scientific STOP on any mismatch, with no relaxation.

## Frozen chronology categories; do not select a favorable subperiod

For ALL 114, report by original start year (2021, 2022, 2023) the number of pairs and 2023 (or corresponding followup-year) capture-month counts, separately from original plant survey season.

For exactly the 65 start-year **2022→2023** original pairs, classify their **FOLLOWUP 2023 capture date**:
- **PRE_MONSOON (2023-01-01 through 2023-06-30)**: ALL original July–September 2023 NDVI measurements happened **after** the captured-community followup and cannot precede the measured response.
- **DURING_MONSOON (2023-07-01 through 2023-09-30)**: the *full July–September mean* includes future images relative to the followup capture. Cannot treat the whole mean as a preceding exposure even if some images were earlier.
- **POST_MONSOON (2023-10-01 through 2023-12-31)**: the full monsoon NDVI source window predates the followup capture; chronology alone is not causal evidence.

Also report 2022 baseline captures in the same PRE/DURING/POST windows for completeness, their original plant survey season categories, the number of independent original plots in each category, and the number of matched plot pairs where **both** baseline 2022 and followup 2023 captures occur after Sep 30, so the 2022 and 2023 full monsoon NDVI windows both precede the respective captures.

There are **no** new temporal thresholds fitted to outcomes. Site-climate NDVI was measured over ~1km radius and is not same-plot food/biomass, and all plants were measured in quadrats rather than rodent traps. A positive temporal ordering would at most make NDVI chronologically possible, not identify the resource-by-competition pathway. An early capture invalidates causality of a *later measured satellite decline*, not the biological possibility of earlier unmeasured drying.

## Audit output

`analysis/audit_portal_2022_ndvi_capture_chronology_v1.py`, `tests/test_portal_2022_ndvi_capture_chronology_v1.py`, GitHub Actions workflow, and anonymous aggregate source receipt. No exact coordinates, plot IDs, animal tags, individual taxon counts, dates, original 114 X/Y or response effects are exported. Original fitted result, NDVI context, and all 2022 omitted-year coefficients remain frozen.

**Scientific decision rule:** If 2023 followup captures in PRE or DURING dominate, revise manuscript and README immediately to state that the large July–September 2023 NDVI decline cannot explain the timing of most of the 2022→23 response, instead of calling it a candidate driver. If POST dominates, retain only a qualified temporal coincidence. In either case **SUBMISSION HOLD**, no mechanism promotion, no learning or biomass claim.
