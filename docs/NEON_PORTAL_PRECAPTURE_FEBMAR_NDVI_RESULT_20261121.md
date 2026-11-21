# NEON / Portal: no measured pre-spring site greenness decline in 2022→2023

**Verified 21 November 2026 — original-source environmental diagnostic, not a new mammal effect.** NEON continues as ONE Draft PR #23; **SUBMISSION HOLD**.

## Precise problem addressed

The original Portal plant-count-change × kangaroo-rat-exclosure capture-community result is highly dependent on start-year 2022. Among 65 matched 2022→2023 comparisons, **43 follow-up captures occurred in April–June 2023**, long BEFORE the previously observed July–September 2023 satellite NDVI decrease (−0.10156). Summer NDVI cannot act as an already-observed cause of those spring captures.

To avoid inventing a later environmental cause, we used the already-published original site NDVI data to inspect February–March in each year. This period **precedes the April–June capture responses**. The February–March window was selected **after the rodent and summer NDVI results were known** and **after a source-only check** showed that all four 2021–24 years had at least one valid original Landsat8 USGS image in both months; January 2023 did not. This is a source-informed **retrospective exploratory** diagnostic, not independently prespecified confirmation.

## New original-source result

Source: original `weecology/PortalData@afd75933249ae60f3a5e9dab00b354f219e5e045`, original `NDVI/ndvi.csv` exact Git blob SHA `0a55a926712210ee786660517a1ae12285bb6303`, original bytes 252,370; raw SHA256 `3f043603693c53a92eff1376d51f07e16678e19a56142fc2f5b7f4ff4df5910c`. Sensor/provider strictly `Landsat8 / USGS`, original cloud percentage ≤30, NDVI finite [−1,+1]. February and March image values are averaged **separately, then given equal 50% weight** in each year to account for uneven image counts.

| Year | February images | March images | Equal-month Feb–Mar site NDVI |
|---|---:|---:|---:|
| 2021 | 3 | 3 | **0.145096** |
| 2022 | 2 | 4 | **0.145309** |
| 2023 | 1 | 2 | **0.148276** |
| 2024 | 2 | 1 | **0.155456** |

All three consecutive differences preserved: 2021→22 **+0.000212**, 2022→23 **+0.002967**, 2023→24 **+0.007180**. The spring-leading 2022→2023 contrast is a **small increase**, not a decrease; its absolute magnitude ranks second of the three. The previously observed 2022→2023 July–September decline **−0.101558** is a true observed later-period environmental change, but it is **not a preceding February–March decline**.

The cross-implementation check used original GitHub connector source and standalone JavaScript image averaging; its means matched the independent Python GitHub Actions source runner exactly to normal floating-point precision. [Original executed CI 44853409600](https://github.com/zuizui0223/neon/actions/runs/44853409600) passed **5 synthetic tests**, original Git SHA reconstruction, raw source-byte SHA256 and both months for all years; artifact 14686132857. Aggregate machine receipt: `results/neon_portal_precapture_febmar_ndvi_context_20261121.json`. No rodent data, plot vegetation counts or prior response-model coefficients were read in the source-runner.

## Mechanism verdict: no positive biomass/competition/learning inference

**The simple antecedent site-wide vegetation-greenness-decline explanation for the April–June 2023 rodent response is NOT supported by the fixed source-filtered February–March NDVI index.** A 2023 February NDVI dip (one usable image) and a March NDVI rise (two images) combine to a near-flat/slightly positive equal-month index; do not select a favorable single month. There are too few images in 2023 to demonstrate the absence of all possible preceding vegetation changes.

This result does not disprove unobserved winter seed-bank depletion, plant species turnover, seed crop, nutrient quality, nocturnal cover or rodent density responses: **NDVI is not seed availability or edible biomass**. It cannot distinguish predation, long-term competitive release and animal habituation; capture-based species composition also does not measure learning. Four annual site-wide values are not independent plot-level resources or sufficient for general ecological inference.

Importantly, the original resource×competitor observation remains **temporally non-generalizable**: 65/114 pairs in the 2022-start-year transition, sign reversals when omitting that start-year, and no demonstrated detector-corrected rodent space use. No subgroup rescue, alternate cloud threshold, changed model or other time window is pursued.

**Decision:** the existing narrative must not imply a measured pre-capture resource crash. Keep both the genuine later-summer greenness decline and the new preceding near-flat satellite greenness result clearly separated. The NEON integrated ecological paper remains Draft, **SUBMISSION HOLD**, awaiting truly plot-level food/biomass and independent animal-use/detection data. All original NEON conditional spatial recurrence, historical Portal non-support and Finnish capture-geometry results remain unchanged.

## Links and frozen source protocol

- Original source-informed feasibility lock: `docs/NEON_PORTAL_PRECAPTURE_FEBMAR_NDVI_CONTEXT_FROZEN_20261121.md`
- Executed code: `analysis/run_portal_precapture_febmar_ndvi_context_v1.py`
- Unit tests: `tests/test_portal_precapture_febmar_ndvi_context_v1.py`
- GitHub Actions: `https://github.com/zuizui0223/neon/actions/runs/44853409600`
- Source-verified result: `results/neon_portal_precapture_febmar_ndvi_context_20261121.json`
- Previous original capture date audit: `results/neon_portal_ndvi_capture_chronology_20261121.json`
