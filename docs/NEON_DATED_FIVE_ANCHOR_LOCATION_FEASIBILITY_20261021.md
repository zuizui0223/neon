# NEON historical capture-day location validity: five named station pilot
## Effect-blind source gate frozen before opening historic position coverage

**Created 2026-10-21 after the official geoNEON date-effective-location
contract and its synthetic unit tests; BEFORE querying the live original
site×plot×anchor histories against real capture dates.**

### Scientific purpose

The observed genus-associated trap recurrence was measured on nominal
station labels, not 1-m absolute geolocations. A canopy-habitat mechanism
cannot be claimed using the **current** NEON A1/A10/J1/J10/E5 coordinates
alone. The current API's 150 original five-anchor documents have one
location-history record apiece; whether these histories cover the actual
2015–2026 trapping events has not been measured.

We will determine whether the original 58 cross-season pairs across 30 plots
and 14 sites contain two 3-night trapping bouts for which the station's
**original location history has exactly one [start,end) date-valid record**.
We will use all 58 pairs, the original plotted capture dates and exactly
the five literal NEON locations A1/A10/J1/J10/E5. Do not infer the
remaining 95 trap locations or a survey instrument's absolute accuracy.
Do not modify the original ecological 14-site 58-pair result.

### Inputs and source rules

1. Retrieve the original checksum-verified NEON RELEASE-2026 mammal capture
   files and exactly rebuild the frozen 58 pairs / 30 plots / 14 sites.
   The existing source population code must preserve three private actual
   `collectDate` values from *each* source event; assert 3+3 dates,
   consecutive meteorological seasons, and that the public aggregate receipt
   still has no animal, source plot, station or date identifiers.
2. Query the live official NEON location API `locations/<exactSourceName>?history=true`
   for each of the 150 original source-named anchors. The source plot base
   name comes from the original `mam_pertrapnight.namedLocation` field;
   no station coordinate is generated from other anchors or from E5.
3. Accept only historical `locationHistory` entries with an original
   `locationStartDate` and optional `locationEndDate`. On each of the
   source event's six exact actual capture dates, require exactly one record
   with `start <= captureDate < end`. A missing match, overlapping match,
   invalid interval or unknown source history remains a recorded FAILURE
   for that anchor×date; never substitute current coords or the latest
   record.
4. The API location history is an external evolving source and not frozen
   by NEON RELEASE-2026. Save only a set digest of the original full JSON
   documents, retrieval time, aggregate history length and temporal
   validity counts. Do not serialize actual locations, animal/tag IDs,
   capture day keys, source site codes, or plot names.
5. Report all 58×6×5=**1,740** anchor–day attempts, number with exactly
   one date-valid record, all-five-valid seasonal pair counts, source
   sites/plots with all named-anchor date validation, distribution of
   original capture years, and reason categories for any absence or
   ambiguity. Count duplicated pair-day source uses only as **attempts**,
   not 1,740 independent observations.
6. Diagnostic threshold for proceeding to the full 3,000 named-location
   API requests: require ≥20 of original 30 plots and ≥8 of 14 original
   sites to have all five anchor date-matches for their original source
   pair days, and ≥40 of 58 pairs with all six×five matches. This is a
   *source-effort feasibility* criterion, not a biological p threshold.
   A failure is a source STOP; do NOT relax it after inspecting coverage
   or switch to only favorable plots to fit an environmental effect.

### Scope and uncertainty

- Date-validity is a necessary but **not sufficient** condition for
  geospatial confidence. Four original plots have NEON-documented
  geolocation/orientation issues. The geoNEON U+1 / max(U)+3 rule is a
  source-convention for uncertainty, not an empirically calibrated bound.
  The present gate does not yet extract historical 100-trap canopy
  measurements or classify habitat effects.
- A date-valid *geographic* position does not mean CHM imagery was
  acquired on the capture date. Latest per-site CHM acquisitions are
  2022–2024 and cannot be retrospectively treated as the actual
  2015–2026 vegetation state.
- Original corrected positive genus trap-recurrence and 14-site site-level
  inference remain immutable. Original 8-genus density W/B criterion
  FAILED (5/8 < 6/8), provisional Peromyscus was not confirmed, historic
  F/C fixed-total matched comparisons were zero under uncertain taxonomy,
  and MOSA W/B ecological outcomes remain SEALED.
