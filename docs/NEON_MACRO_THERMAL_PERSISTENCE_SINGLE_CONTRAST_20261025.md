# Single historical macroecological environmental contrast: seasonal thermal displacement

**Design committed on 25 October 2026 after two-genus conditional ecological recurrence and the temporal-gap regression's rank-deficient STOP were both observed, but BEFORE reading more than the one nonoutcome pilot month's instrument temperature values or any across-site/site-season temperature contrasts.**

## Biological question and one prediction

**Among physical NEON sites, is the persistence of genus-associated exact-trap capture-space signatures lower in sites where the original paired sampling seasons undergo larger local TOWER air-temperature changes?**

One predeclared explanatory axis: the **absolute difference in original released, independently observed, QC-filtered 30-minute monthly tower air temperature between the source's season-A and season-B sampling months**. This is the cross-season *thermal displacement* or meteorological exposure contrast, not a shrub/ground or trap-level microclimate measurement and not observed station habitat change. Thermal displacement uses °C; predict a *negative* association of conditional two-genus spatial recurrence standardized Z with thermal displacement. A zero/positive/imprecise result is equally acceptable and does not disprove stable habitat selection.

**No hypothesis rescue:** The previous actual-date temporal-gap test STOPPED because site+transition fixed effects were rank deficient. This site-level environmental design differs deliberately and does NOT re-estimate, replace, or claim success for that stopped same-site temporal duration estimand.

## Source/cohort

Use **only** original NEON RELEASE-2026 DP1.10072.001 exact-two genus pair population: 158 original adjacent-season source comparisons from 30 physical sites, source cohort in `results/neon_exact_two_genus_source_receipt_20261025.json`, with 150 exact two-row uniform fixed-margin informative effect scores from `results/neon_exact_two_genus_ecological_receipt_20261025.json`. Verify all 30 anonymous sorted site means against original receipt by exact source reconstruction BEFORE performing any climatic exposure join. Original three-plus genus 58 comparisons are historical reference only, **not added**.

External measurement: independently authored NEON RELEASE-2026 `DP1.00002.001` SAAT_30min, **`tempSingleMean`**, same deterministic **first lexicographically sorted 30-min sensor file** at a site and month. This position is an instrument level, not a verified 2m at the rodent grid; require exactly the same filename-derived position key for the two monthly observations, no height interpolation or sensor switching. Source fields `finalQF=0`, valid finite temp -90 to +65 °C; no missing/QF1 imputation.

Pair eligibility is defined **before opening matched temperature values**:
- Both original 3-night bout calendars must lie within exactly one month *per bout*, and their months must differ.
- Both site months must exist in the EXACT `RELEASE-2026` product availability, never current/latest unversioned data.
- Source provider monthly 30min file and MD5/size verified, same instrument vertical index in both months, `tempSingleMean` and `finalQF` present; per selected source site-month >=70% of that calendar month's expected 48 per day 30-minute records must have finite and finalQF=0 values. No weather file or month is selected based on ecological Z.
- Each pair's climate exposure is `T_u=abs(monthly mean temp_B − monthly mean temp_A)`. No secondary VPD, precipitation, radiation, mean temperature, season-specific subgroup, threshold splitting, alternative sensor, or variable-search endpoints.

An original source-only weather availability census found **144/158 original pair months complete** across 28 physical sites for this product; this is *availability*, not QC. A one-month independent provider-checksum and schema pilot returned 1,408 QF0 rows / 1,488 total for temperature (file MD5 verified). No other 2026 release weather values are assumed valid.

## Structural effects-before-values gate and model

Before climate effect estimation, require:
- at least **80 original exact-two genus seasonal pairs** with both qualified temperature months AND nondegenerate exact uniform null Z,
- at least **18 independent physical NEON sites**, and at least **10 ecological domains** among those sites,
- valid latitude from official release `/sites` for all included physical sites, original source date/taxonomic margins reproduce, and the mean of original 30 site-effect Zs matches the prior exact-two receipt to 1e-8.
- for a site, include **all** source-pair temperature-verified data; compute `Y_site = mean(Z of included pairs)`, `X_site = mean(T_u)`, and `q_site = fraction of included pairs with summer→autumn transition (original meteorological season ordinal modulo 4 = 2)`. This is one site-level X and Y point, not hundreds of pseudo-independent trap pairs.

**Primary model (only if the above gate passes):**
`Y_site = α + β_T (X_site / 5°C) + β_L ((latitude_site-40°N)/10°) + β_Q q_site + ε_site`.
OLS with **equal physical-site weights** (not per-season-pair weights). Distinct site-level covariance design must have full numeric rank; otherwise STOP. The predeclared ecological sign is β_T<0. Under historical same-release outcome exploration, compute whole-physical-site bootstrap 2,000 resamples with fixed seed **2026102521** and 95% percentile CI; require >=95% valid bootstrap models and all leave-one-physical-site-out models estimable, otherwise STOP without changing predictors or filtering outcomes. Use CI and leave-one-site-out sign consistency as *descriptive confidence*, not new preregistered independent p.

No post-result latitude subgroup, domain fishing, body mass, competition proxies, precipitation predictor substitution or baseline redefinition. If the climate predictor CI is compatible with zero/positive, report **no established macrothermal association**, preserving positive conditional recurrence. Even if negative, the result remains **exploratory covariation** between site-level conditions and capture-space genus recurrence, not an environmental mechanism (microhabitat/genus-specific detectability unmeasured).

## Data and QC boundaries

The field trapping was conducted in fixed 3-night observed bouts; the weather station measures site tower air temperatures, often at nonidentical locations and heights relative to mammal grids. Monthly averages ignore exact local trapping-day night temperatures and use timezone-independent provider month boundaries. Seasonal transition composition and latitude are statistical controls, not proof of causality. Interpolating, imputing gaps, substituting precipitation gauges, pooling with already positive three-plus-genus site effects, interpreting absence of genera as ecological losses, or upgrading the original historical W/B generality 5/8 FAIL are **forbidden**.

A record with missing provider weather/QF is excluded from this *observational climate association* and counted in the denominator, not assigned ΔT=0 or genus recurrence=0. Study selection must be reported by site/domain and the original 158 and 150 cohorts. A NEON tower temperature monthly contrast is not a full seasonal resource-stability index. Future independent new-release marked-animal data and trap-grid habitat/detection observations are necessary for high-impact macro ecological conclusions.

## Implementation and stop rules

`analysis/run_neon_macro_weather_pilot_v1.py` proves that the 30-minute source instrument files and `finalQF` metadata are readable. The full source-controlled climate linkage must re-run provider MD5/size verification per file and write only aggregate source QC counts (not site names, animal tags, capture dates, file URLs or seasonal R/Z pairs), the fitted site-level β/CI if the predeclared gate passes, and exact explanatory limitations. If any source, model, or numerical invariant fails, stop with sanitized failure category and without claiming climate causation.

No external Daymet fallback: ORNL DAAC Daymet downloads can require NASA Earthdata login and are not silently available. Precipitation product split into DP1.00044/00045/00046 remains a **separate** question; precipitation values are not included in this single thermal contrast.
