# Portal 2022-sensitive rodent result: independent site-climate / canopy-greenness adjudication

**Date 2026-11-21. One existing NEON ecological paper, PR #23. Draft/SUBMISSION HOLD.** This design is explicitly POST-RESULT because the original 2020–25 Portal rodent-composition model and its 2022-start-year omission reversal were already opened. It is a mechanism *diagnostic*, **not preregistered independent biological validation**.

## Known ecological outcome (unchanged)

Portal 2020–25 temporal-holdout fixed original analysis: 114 plot×month×adjacent-year captured community composition total-variation comparisons at 18 original physical plots. Control change-in-plant-count slope −0.11064, exclosure interaction +0.12954. Omitting 2022 start-year leaves 49 of the 114 and reverses control to +0.16391 and interaction to −0.66466. Hence **65/114 comparisons (57.0%) belong to start-year 2022**. The original 3 start-years give poor temporal generality; plot bootstrap ignored independent year-cluster uncertainty. We must NOT search alternate effects to restore positive significance.

## Original independent environmental measurements

One fixed publicly accessible PortalData commit `weecology/PortalData@afd75933249ae60f3a5e9dab00b354f219e5e045`, independent of the original tagged-rodent/plant response tables:

1. `Weather/Portal_weather.csv`: original Git blob SHA `bc9d999db496b55e04281c1317a98b3ff3304eed`, bounded read up to 150 MB. The original station is ONE site-level meteorological station; its hourly `year,month,day,hour,precipitation` field measures rainfall in mm, with documented occasional station blending.
2. `NDVI/ndvi.csv`: original Git blob SHA `0a55a926712210ee786660517a1ae12285bb6303`, bounded read up to 1 MB. Original raw normalized difference vegetation index around 1 km of Portal, **not** food biomass or plot-scale resources. Restrict to `sensor=Landsat8`, `source=USGS`, nonmissing finite NDVI, provider cloud_cover <= 30%; do not pick Landsat9 or change cutoff after observing result. Landsat8 alone avoids between-sensor calibration drift. Do not use legacy monthly NDVI because the README states it is 1981–2013 only.
3. `Weather/README.md` original SHA `40939be250fe80067c57c0ff60f3edcab2260f2a`; `NDVI/README.md` SHA `7589e6de71a1eb39c4fcb2a3f378ce3d42ec7cd3`; documentation provenance.

No original `Portal_rodent.csv`, plant-quadrat counts, original environmental regressions or earlier NEON/Finland/Structural outcomes are accessed by these environmental scripts.

## Fixed environmental window and estimands before viewing climate values

For each of calendar years **2021, 2022, 2023, 2024** and ORIGINAL local **July 1–September 30** window (92 days), calculate:
- `P_y` = total measured hourly precipitation in mm from ORIGINAL weather row timestamps.
- `G_y` = arithmetic mean of qualifying cloud-filtered **Landsat8** NDVI records (each image one record). It is observed site-scale greenness, not 18 independent plots.
- Adjacent year changes `ΔP_y = P_{y+1}-P_y`, `ΔG_y=G_{y+1}-G_y` for 2021→22, 2022→23, 2023→24; report signed and absolute values of ALL THREE, not a selected period.
- For each of the two climate indicators, print whether the **2022→23 absolute change** ranks first, second or third among these three. With only three transitions this is DESCRIPTIVE, not a p-value.

Why this window: monsoon rainfall can drive desert annual plant pulses, and 2022→23 is the transition indexed by the previously anomalous rodent start year; this is post hoc ecological context, not a confirmatory causal inference.

## Strict source and quality gates

- Original Git blob SHA-1 for BOTH raw files must match byte-for-byte. Stop on HTTP, HTML challenge, missing original header, empty file, oversized source, invalid datetime formatting, duplicate same-hour records with different precipitation values, negative numeric precipitation or impossible satellite NDVI outside [-1,1].
- Hourly window per year has 2208 expected slots. Record nonmissing valid precipitation hours and missing fraction each year. Only if >=90% of expected hourly slots have valid measured precipitation in **ALL four years** may the precipitation annual sums be reported. Otherwise precip quality STOP rather than treating missing values as zero; no gap fill or provider replacement.
- NDVI `G_y` may be reported only if there are >=2 raw Landsat8 valid cloud<=30% images in **EACH four monsoon windows**. Otherwise **NDVI_SOURCE_STOP** separately, no substitution by Landsat9, GIMMS or a lower cloud threshold. NDVI quality failure cannot void a valid rainfall source or rescue old mammal ecology.
- Bounded memory; original weather rows outside 2021–2024 can be skipped for calculations, while original full raw byte hash remains checked. Source receipts are aggregate year-level values only, no exact site/animal captures, individual trap stations or plant composition outcomes.

## What cannot be inferred

Rainfall and satellite NDVI vary over time at this ONE site. They are shared by all 18 experimental plots, so no such aggregate environmental series can directly identify the observed `plant_count_change × exclosure` coefficient or isolate competitive buffering. Even if 2022→23 has an extreme environmental shift, the result is at most **plausible independent context** for an already-known 2022-weighted effect, not proof a rainfall pulse caused it. If it does not, one suggested environmental story loses support. Both outcomes must be reported.

No further same-dataset post hoc rodent species/sex/season/plant functional-group searches, no refit under weather/NDVI controls, and no publication promotion. Learning and memory are not measured.

## Files

`analysis/audit_portal_2022_site_climate_source_v1.py`: hash-locked source validation and neutral source-coverage counts with no climate values exported; `analysis/run_portal_2022_environment_context_v1.py`: only when the source gate passes, fixed annual rainfall + NDVI temporal contrast; tests and GH workflows record SOURCE GO/STOP and diagnostics. Original ecological results at `results/neon_portal_plant_change_competitor_ecology_20261120.json` and `results/neon_portal_resource_competitor_year_stability_20261120.json` remain immutable.
