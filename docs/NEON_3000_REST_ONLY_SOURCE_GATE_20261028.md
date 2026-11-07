# Original NEON 3000 trap stations: canonical REST-only history validation

28 October 2026. One integrated NEON small mammal macroecology paper, draft only. A new SOURCE-ONLY historical position audit, not a new biological effect.

Previous 2026-10-22 GraphQL/REST 5-name equivalence STOP remains unchanged: 5/5 original source names had schema/canonical parsing differences. Separate earlier canonical REST queries had successfully retrieved source date-effective histories for the original 150 fixed named anchor points (A1/A10/J1/J10/E5 in 30 plots) and passed 1740/1740 capture-day tests.

This new route uses the official NEON locations REST endpoint with history=true, not GraphQL. It fetches 3000 literal named trap locations, made from each source plot namedLocation plus original A1-J10 trap labels. No 100-station geometrical interpolation or use of current-only coordinates is permitted. Eight concurrent source requests and bounded 429/transient retries are declared; missing 400/404 location/history is recorded without imputation.

Source set stays 58 adjacent-season pairs in 30 grids/14 NEON sites (NEON RELEASE-2026), including four source geolocation-issue plots. The 150 original REST anchor source days must independently reproduce all 1740 successes before the full 34800 original station-by-capture-day source comparisons are opened. Previously declared GO gate is unchanged: at least 20 of 30 plots with 95 time-valid stations on all source days, at least 8 physical sites with a qualifying plot, and at least 40 of 58 comparisons with at least 95 time-valid stations per original capture day. Historical location date intervals are half-open. Original NEON datum/UTM and directly measured uncertainty are required; the source-defined geoNEON adjusted uncertainty is ASSUMED and not a calibrated 95% confidence bound.

A successful geolocation check is NOT evidence of genus habitat selection. Independently sourced CHM imagery (2022-2024) does not automatically represent capture events from 2015-2026; understory/ground vegetation is not established by zero canopy pixels. Independent trap-level genus detection still needs validation. No R, W/B, 10-m patch, temperature, operability, sex or EOG ecological endpoints are refitted. Prior negative gates remain STOP.

Files:
- analysis/run_neon_3000_station_dated_rest_v1.py
- tests/test_neon_3000_station_rest_only_v1.py
- .github/workflows/neon-3000-original-rest-only-source.yml
- source receipt build/neon_3000_station_dated_rest_v1.json (Actions artifact)
