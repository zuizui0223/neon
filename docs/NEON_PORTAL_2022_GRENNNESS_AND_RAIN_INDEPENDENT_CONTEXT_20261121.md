# Portal 2022–23 greenness transition: independent context, not a mechanism (21 November 2026)

**Status:** New verified site-environment context only; no new mammal response, competition or biomass effect. ONE NEON unified Draft PR #23 and **SUBMISSION HOLD**.

## Biological question inherited from immutable ecological result

The original pre-frozen Portal 2020–25 plot-level captured-community analysis had 114 same-month adjacent-year plot pairs, with **65/114 (57.0%) indexed to start-year 2022→2023**. At full data, plot/month/year-adjusted association between plant-count change and captured rodent composition distance was negative in control (−0.11064) and almost zero in kangaroo-rat exclusion (+0.01890), so exclusion×resource interaction +0.12954. When start-year 2022 is omitted, control becomes +0.16391 and interaction −0.66466 (49/114 remain). **This is not temporally general and may reflect sample support**, as already frozen 20 November. No model is refit here.

## Independent original site environmental source

From exact original `weecology/PortalData` Git commit `afd75933249ae60f3a5e9dab00b354f219e5e045`, each byte-verified with original Git blob SHA:

- Original `NDVI/ndvi.csv`, SHA `0a55a926712210ee786660517a1ae12285bb6303`; fixed Landsat8, USGS, 7–9 month, original cloud<=30%, nonmissing NDVI. Original sensor same each year. Original surface coverage is about a 1km radius, NOT each experimental plant quadrat, mammal trap station, seed availability or biomass.
- Original `Weather/Portal_weather.csv`, SHA `bc9d999db496b55e04281c1317a98b3ff3304eed`, 28,416,223 original bytes; years 2021–24 monsoon (July–Sep) expected 2,208 hourly precipitation entries per year. Original source hour label format is **0100,0200,...,2400**, with source timestamp hour 01,02,...,00; validated for all 8,832 label records, no guessed date shifting.

Technical QA sequence was fail-closed: parser initially expected 0–23, then still failed with 0–24; we switched to an immutable original hour-schema diagnostic **without opening precipitation values** ([Action 44848725262](https://github.com/zuizui0223/neon/actions/runs/44848725262)). Corrected original 100..2400 labels, preserved original date and re-ran source-only [Action 44848797785](https://github.com/zuizui0223/neon/actions/runs/44848797785): checksum and synthetic tests PASS. This technical repair did not change original source, 90% valid-hour minimum or ecological results.

## New result from independent satellite observations

Fixed original image-level 7–9-month mean Landsat8 NDVI:

| Year | Valid images (cloud<=30%) | Original mean NDVI | July/Aug/Sept valid images |
|---|---:|---:|---|
| 2021 | 8 | 0.267391 | 3 / 3 / 2 |
| 2022 | 9 | 0.282297 | 4 / 2 / 3 |
| 2023 | 6 | 0.180738 | 3 / 2 / 1 |
| 2024 | 5 | 0.166778 | 2 / 2 / 1 |

Predeclared ALL THREE adjacent-year site-level NDVI changes: 2021→2022 **+0.014906**, 2022→2023 **−0.101558**, 2023→2024 **−0.013960**. Absolute **2022→2023 is largest among the three**, not a significance test based on only three transitions.

As explicitly **post-result image timing sensitivity**, July, August and September were each given equal weight within year, since all four years had at least one qualifying image in each month. The site-year equal-month means were 2021 **0.272369**, 2022 **0.289554**, 2023 **0.187151**, 2024 **0.167358**; 2022→23 change **−0.102403**, still largest. This controls unequal MONTH representation but not cloud/time-of-month selection, NDVI sensor artifacts, or biological ground plant access. It is not another independent ecological cohort.

Original verified [environmental context Action 44848797764](https://github.com/zuizui0223/neon/actions/runs/44848797764) / artifact 14684831215. Machine receipt `results/neon_portal_2022_independent_monsoon_NDVI_and_rain_QC_20261121.json`. The original source QC run/action may be green while the rainfall subgate remains STOP.

## Rainfall: two explicit evidence-quality STOPS

On-site hour-source valid nonnegative precipitation hours out of 2,208 expected:
2021 **1,169 (52.94%)**, 2022 **1,354 (61.32%)**, 2023 **2,208 (100%)**, 2024 **2,208 (100%)**. The pre-fixed >=90% all four years site-rain quality gate **FAILED**: no 2021–24 site monsoon precipitation totals or 2022→23 rainfall contrasts reported, no interpolation/zero-fill.

A *separate post-result and non-substitutive* regional check used exact source original SHA for two PortalData regional CSVs. Provider [header diagnostic 44849288953](https://github.com/zuizui0223/neon/actions/runs/44849288953) established:
- Rodeo original `Rodeo_regional_weather.csv`, 48,912,736 bytes, SHA `dcbcd3f7e414a51ff74d31b17891f8e0593506fc`, is hourly PWS with `stationid, hour, preciptotal`, **NOT** a daily GHCN source; do not pretend `preciptotal` is `prcp`.
- SanSimon original `Sansimon_regional_weather.csv`, 217,442 bytes, SHA `0f905f95d788378e3415a1482e4abfa73a2ea3b6`, is GHCN daily, but valid precipitation only **35/92 days (2021), 36/92 (2022), 20/92 (2023), 16/92 (2024)**; fails >=90% each-year quality gate.
- Original Rodeo 30 MB limit was corrected using independent GitHub original file size metadata to 60 MB, before opening rainfall values. After source schema discrepancy was diagnosed using headers ONLY, no incompatible source was converted.

[Final regional action 44849401744](https://github.com/zuizui0223/neon/actions/runs/44849401744) succeeded in recording **scientific SOURCE STOP on both stations**, not available rainfall totals. Artifact 14684872087. These regional files were never substitutes for the original failed on-site source. **No rainfall mechanism has been demonstrated.**

## Scientific interpretation

There is a verified **site-wide** unusually large NDVI decline between 2022 and 2023, matching the specific ecological time transition that dominates the open plot-level plant-change×competitor result. This is an independent environmental *coincidence/context*, not identified causation. NDVI is not plant biomass or seed food; one shared site environmental time series cannot by itself identify why control and kangaroo-rat exclusion plots had different captured-rodent responses. Three temporal transitions cannot support a general regime-switch theory. Importantly, >half the 114 original comparisons stem from start-year 2022, so sample leverage remains viable.

No retuning of years, taxa, treatment labels, NDVI cloud threshold or earlier ecological coefficients is permitted. To establish the mechanism would require genuinely independent *plot-specific* food/resources, effort-corrected capture/use or activity observations, and more than three independently sampled environmental transitions. Do not call this "competition dampens resource effects", biomass coupling, learned spatial fidelity, or a universal mammal niche principle.

**Decision:** Preserve the satellite observation in an ecological evidence/limitation addendum. NEON main abstract and all previous conditional positive/negative mammal estimates unchanged; no submission promotion. Source freezes and code:
`docs/NEON_PORTAL_2022_ENVIRONMENT_POSTRESULT_DESIGN_20261121.md`,
`docs/NEON_PORTAL_2022_REGIONAL_RAIN_CONTEXT_POSTRESULT_20261121.md`,
`analysis/audit_portal_2022_site_climate_source_v1.py`,
`analysis/run_portal_2022_environment_context_v1.py`,
`analysis/audit_portal_2022_regional_rain_context_v1.py`.
