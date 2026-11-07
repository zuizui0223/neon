# NEON full 3,000 named trap positions — historical/date-effective source-only gate

**Frozen 2026-10-21 after 1,740/1,740 original capture day×five-anchor
history comparisons passed, BEFORE querying other 95 source trap labels or
opening any new habitat-linked mammal recurrence effect.**

## Source population and positive pre-check

- **Exactly** 58 original season-pair contrasts, 30 source namedLocation
  plots and 14 independent physical NEON sites are held fixed; all 58×6
  original capture days have been recovered and validated.
- The original source [five-anchor receipt](../results/neon_dated_five_anchor_feasibility_receipt_20261021.json)
  found **150/150** named stations with one source history record and
  **1,740/1,740** date-valid capture-day comparisons, including the four
  known NEON geolocation-issue plots in the 30-plot cohort. This authorizes
  an *additional source-feasibility audit*, not a habitat mechanism test.
- All 100 station suffixes per plot are the literal original A1–J10
  nominal trap labels; no E5 orientation, corner interpolation or map
  projection is used to invent station positions.

## Efficient canonical API retrieval and provenance

- Use the official NEON GraphQL `POST https://data.neonscience.org/graphql`
  public `findLocations(query:{locationNames:[...]})` API. Official
  `LocationQuery` supports up to 1,000 named sites per call; cap each
  verified batch at **500 station names**, for six controlled batches.
  Query locationName, station's projected easting/northing, UTM zone and
  hemisphere, `locationHistory` with start/end and source
  `locationProperties`.
- **Before using any GraphQL result**, query precisely the first five
  source station names with the already-validated NEON REST
  `/api/v0/locations/<name>?history=true`; compare exact
  original `locationName` and each history start/end/current/projected
  easting/northing/UTM zone/hemisphere tuple against GraphQL. Any schema
  incompatibility or missing/duplicate identity is an explicit STOP,
  not permission to substitute fabricated station geometry.
- The NEON locations endpoint is a LIVE external API, not part of
  the RELEASE-2026 pin. Record retrieval time, six batch response digest
  hashes and provider property/record-count distributions, but NEVER
  publish raw station names, animal tag IDs, site/plot identifiers,
  projected or lat/lon coordinates or source-side API URLs in artifacts.
- Missing GraphQL names are **not** filled by interpolation or from
  current E5; document their exact number as source failures. A half-open
  historical interval has `start<=collectDate<end`, never a fallback to
  latest records.

## Original-date-effective geographical feasibility metrics

Across the frozen **58×6×100 = 34,800** season-pair source
capture-day×station comparisons, record aggregate:
- source named station documents found (out of 3,000), original
  history-record multiplicity and missing date-valid histories;
- valid historical projected UTM positions with declared datum/CRS,
  latitude/longitude if provided but NOT exported, and number of
  distinct source historical coordinate versions;
- for each fixed physical site×plot×event, how many of the original
  100 station positions are valid at all six source capture days;
  plot coverage min/median/max and number of plots with >=95 valid
  stations; number of original 14 sites that have at least one such plot;
- known direct coordinate-uncertainty values separate from missing
  values; the official geoNEON reported U+1 m / max grid U+3 m
  *assumed adjustment* may be applied only if >=1 directly reported
  U in that plot at each event date. Record its range and source counts,
  never call it empirically calibrated position accuracy.
- original four published geoNEON-issue plots remain in ALL
  denominators with their own aggregate count, not deleted or recoded.

**Predeclared source support to proceed with any full-trap CHM check:**
>=20/30 original plots with >=95/100 official station positions
valid on ALL original capture-day source pairs; >=8/14 sites with at
least one qualifying original plot; and >=40/58 pairs with >=95 stations
valid at each original capture day. If source coverage falls below,
publish STOP without relaxing thresholds or selecting positive sites.
Even if support passes, a prospective canopy/habitat ecological model
requires environmental acquisition dates appropriate to trapping,
source datum and positional uncertainty QA, missing/understory cover,
genus-specific capture/detection calibration and a **separate pre-effect
environmental hypothesis**. Existing 2022–2024 CHM cannot automatically
be called 2015–2026 habitat exposure.

Original corrected positive genus trap recurrence, original density W/B
8-genera generality FAIL, source-only F/C direct-matching STOP and
MOSA W/B effect seal are preserved, not reanalysed.
