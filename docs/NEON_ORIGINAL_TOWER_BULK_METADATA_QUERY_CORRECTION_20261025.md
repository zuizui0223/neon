# NEON original tower temperature bulk API metadata mismatch: source correction
**25 October 2026, source/QC repair after a complete pre-effect STOP, not a thermal-hypothesis change or post hoc alternative covariate selection.**

## Error and observed state

A source-verified full original-release tower-temperature workflow was first run as GitHub Actions [40179253423](https://github.com/zuizui0223/neon/actions/runs/40179253423) at code revision `fb9a69e4992a72c77ec55e8d4bf0fa0ac81b88b1`. Its source-only prerequisites found **140** of the 158 original exactly-two genus pairs had both site-months in release availability; these pairs involved 28 sites and 15 domains, requiring **205 unique original site×month SAAT_30min file checks**.

The runner queried the whole span of original years for those 28 sites in one `/data/query` call. The resulting release/package parsing matched **0/205** required exact site×month 30-minute files. Consequently every one of the 140 candidate original seasonal pairs was rejected at `NO_ARCHIVE_MONTH`, and the planned environmental regression was never fitted:

`STOP_ORIGINAL_TOWER_TEMPERATURE_QC_OR_DOMAIN_SUPPORT`, `climate_effect_opened=false`.

This is a **data retrieval/metadata association mismatch**, NOT evidence of zero temperature change, absent meteorological records, no thermal effect, or ecological falsification. Source: immutable `results/neon_macro_tower_bulk_query_STOP_20261025.json`.

## Why a source correction is warranted

The earlier provider-checksum-verified *single site×single month* source probe had succeeded for official released SAAT_30min `tempSingleMean`: one original month, **1,488** half-hour rows, **1,408 finalQF=0**. The official NEON product also documents tower-level 1- and 30-minute SAAT products with sensor height positions, not mammal-grid microclimate. The original-site monthly availability census predicted source months would exist. The bulk multi-year response returned no matching files but supplied no evidence that the same individual release-month queries would be absent.

## Correction, before any thermal effect is opened

- Query the **same immutable set of 205 originally required site×month keys** using one site/month per fixed-`RELEASE-2026` `/data/query` request, matching the successful single-month pilot request shape.
- Keep exactly the original external source product `DP1.00002.001`, `SAAT_30min`, `tempSingleMean`, `finalQF=0`, ≥70% monthly QC threshold, lowest lexicographic source sensor-position index, exact matching sensor position between seasons.
- Preserve original 158/150 mammal units, same site inclusion and source 80-pair/18-site/10-domain gate, same site-level `abs(Temp_monthB-Temp_monthA)/5°C` slope with latitude and summer-to-autumn transition-fraction covariates, same 2,000 whole-site bootstrap and LOSO QC.
- If the **new individual original-month source query still fails**, emit a *separate sanitized provider metadata error STOP* with no weather effect. Never treat metadata transport errors as temperature zero or missing biological effect. Never select any alternate climate product, precipitation, towers, seasons or favourable subset because of the original STOP.
- Verify pure unit tests of the exact one-site one-month query body, provider release metadata parser, absent record handling and private original site/date/URL sanitization before running any original NEON observations.

**Statistical and biological boundaries unchanged:** Any resulting temperature association would be *historical same-RELEASE-2026 exploratory* and correlational, not independent confirmation or site-grid climate causality; original 14-/12-site and exact-two 30-/17-site positive genus station recurrence results remain intact. Universal density W/B generality still FAILED (5 of 8), and the direct matched R/W/B support STOP remains.
