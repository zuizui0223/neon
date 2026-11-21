# Portal February–March greenness before spring captures — exploratory source-informed temporal diagnostic

**Date: 21 November 2026, one NEON ecology paper in Draft PR #23 / SUBMISSION HOLD.**

## Prior evidence and source timing correction

The fixed Portal 2020–2025 plant-count-change × competitor-access study contained 114 same-month adjacent-year plot-composition comparisons, 65 indexed to **2022→2023**. Omission of start-year 2022 reverses both model slopes. Original-source date audit established 43/65 2023 follow-up census pairs in **April–June**, 22/65 **October–November**. Thus July–September 2023 NDVI **postdates the 43 spring responses**. Do not use the previously independently verified 2022→2023 July–September decline (−0.10156) as their antecedent cause.

The source-only image coverage was inspected **after the ecological results were known**: original 2023 January lacks any qualifying Landsat8 USGS imagery, while each original calendar **February and March in 2021–2024** contains qualifying same-sensor observations (cloud ≤30%). February–March is chosen based on source availability and chronology, NOT independently preregistered. This is a **post-result, post-coverage feasibility lock before viewing source NDVI numerical values for that window**.

## Fixed source and environmental estimand

Read only `weecology/PortalData` at immutable original Git commit `afd75933249ae60f3a5e9dab00b354f219e5e045`, file `NDVI/ndvi.csv` with exact Git blob SHA `0a55a926712210ee786660517a1ae12285bb6303`. No rodent, plant quadrat, weather, camera or model response data may be loaded. Require original published CSV columns `date,sensor,source,ndvi,cloud_cover`, no duplicate keys, exact bounded source size <1,000,000 bytes, no HTML or malformed CSV.

For **all four years 2021, 2022, 2023, 2024**, use exactly **February 1–March 31**, `sensor=Landsat8`, `source=USGS`, finite NDVI within [−1,+1], cloud fraction 0–30 inclusive, with no interpolation, seasonal imputation or sensor switching. Require ≥1 valid original image in **both February and March for EACH year**, otherwise environmental source STOP and no NDVI means output. Source coverage at 2026-11-21 inspection already met this minimum; **do not increase it post-result**.

Average valid image NDVI *within February* and *within March* separately; give each month **equal weight 0.5** to prevent uneven image counts from biasing each annual metric. A record is one provider image statistic, NOT an independent biological plot. Report all four February and March source image counts, all four equal-month February–March annual means, and all three signed/absolute changes for **2021→2022, 2022→2023 and 2023→2024**. Rank absolute 2022→2023 against the other two; no p-value or statistical generality claim from three changes.

## Biological decision and prevention of post hoc rescue

The fixed 2022→2023 **February–March** environmental difference *precedes the April–June 2023 subset of 43 original mammal comparisons* and the corresponding April–June 2022 baseline. It is not a direct food, seed, vegetation biomass or canopy measurement; the index measures site greenness over ~1km, shared by all original Portal plot treatments. The 22 autumn comparisons can have additional unmeasured resource dynamics after March, so do not use this period to explain their total seasonal response.

- If 2022→2023 February–March greenness declines, it is **chronologically compatible external context**, not direct evidence that vegetation caused a negative/positive rodent composition coefficient or that competition buffered resources.
- If it does not decline, the **simple early-season greenness-decline explanation is not supported** by this independent index; do not search alternate NDVI intervals, cloud thresholds or sensors to recover it.
- If source coverage fails, report a scientific source STOP, not an NDVI null.

The 114 original mammal coefficients, source plant abundance, 2022 source-year omission effects, 43/22 capture timing, original summer NDVI and precipitation quality STOPs are immutable. NO fit of mammal vs NDVI, no repeated seasonal resource regressions and no learning/behavioral claim.

**End state**: Independently verified preceding greenness context (or explicit no-support), no submission-ready ecological mechanism. Subsequent genuine progress requires local independently measured rodent food resources and observation-process calibration in independent plot/year systems; keep unified NEON manuscript **SUBMISSION HOLD**.

Intended implementation: `analysis/run_portal_precapture_febmar_ndvi_context_v1.py`, `tests/test_portal_precapture_febmar_ndvi_context_v1.py`, `.github/workflows/neon-portal-precapture-febmar-ndvi.yml`, anonymous `build/neon_portal_precapture_febmar_ndvi_context_20261121.json`. Only aggregate environmental year/month means and source coverage; no original raw image URLs, animal IDs or plot coordinates in output.
