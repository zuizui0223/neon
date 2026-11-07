# NEON mammal true 100-station historical geolocation source gate — 20 October 2026

**Prepared after** the source-only 30-grid/150-point canopy pilot, and
**before** any genus×canopy ecological model. Existing corrected 14-site
positive lineage recurrence, previous original W/B generality FAIL and
sealed MOSA effects remain unchanged.

## Verified source and observed problem

All 150 literal A1/A10/J1/J10/E5 station names in the unchanged 30 NEON
plots have current projected locations and source-verified CHM pixels.
But the raw location API supplies a coordinate-uncertainty value at the
30 monumented E5 reference positions only; the 120 sampled non-E5
anchors have missing raw uncertainty. Four original plots intersect
NEON's published historic geolocation/orientation issues. The 1-m
raster resolution is NOT 1-m true trap-position accuracy.

Official NEON geoNEON implementation:
- https://github.com/NEONScience/NEON-geolocation/blob/main/geoNEON/R/getLocMAM.R
- https://github.com/NEONScience/NEON-geolocation/blob/main/geoNEON/R/findDateMatch.R

## Official nonmonumented uncertainty convention

The geoNEON getLocMAM implementation reads the uncertainty measured at
monumented reference points for each original grid. For any raw
uncertainty U_i actually present, it uses **U_i + 1 m** as adjusted
coordinate uncertainty. For a nonmonumented station lacking its own
uncertainty value, it uses **max(U_monumented within this grid) + 3 m**.
This is a source-defined **assumed adjustment**, not an independently
measured error or a 95% confidence bound. If there is no known
monumented U anywhere in the grid, STOP; never set unknown=0.

A source-only next run may attach this adjusted **radius** to a
separately retrieved original official station position, to examine
the CHM range in a window that contains candidate positional error.
Never rotate or synthesize the A1–J10 station locations from E5 or
from the four corners. In particular, the 4 original published
geoNEON-issue grids must be reported separately without silently
dropping them from the original recurrence cohort.

## Capture-date effective location history

The official findDateMatch source chooses a history record for which
original collectDate meets:

- locationStartDate <= collectDate
- collectDate < locationEndDate, OR no end date recorded.

When multiple or zero date-valid records exist, or when dates cannot
be interpreted, this research pipeline must **STOP** for those
station-event records rather than silently borrowing the source's
latest valid location (which the general-purpose R utility sometimes
uses with a warning). A current location alone must never be claimed
valid throughout the entire 2015–2026 NEON capture history.

## Next source-only empirical test, fixed scope

1. Preserve the exact 58 eligible genus seasonal pairs, 14 physical
   sites and 30 plots and all original capture events.
2. Retrieve precisely the 100 official A1–J10 named source station
   coordinates for each plot, with their published history records.
   If one station name lacks a valid date-relevant source location,
   mark it unavailable without imputing a position. Ignore X traps
   whose real locations are not credible.
3. For each fixed seasonal pair, check the source capture dates
   against the effective-date history of each occupied station;
   count coverage by plot, site and year, with no taxon×CHM effects.
4. Apply the geoNEON U+1/max U+3 convention only after the source
   grid's monumented values are verified. Report direct versus
   algorithmically assigned uncertainty separately, and do not
   call the latter source-measured.
5. Match raster acquisition month/year and plot/station datum and
   raster CRS without changing previously fixed acquisition rules
   to cherry-pick habitat conditions. Report 0–100 station
   percentage coverage by the original 30 plots; do not select a
   favorable canopy subset for causal inference.
6. Publish ONLY aggregate source coverage, uncertainty categories,
   time-valid sample fractions and source checksum digests, not raw
   site coordinates, animal IDs, observed genus×trap occupancy,
   or habitat coefficients.

**Scientific STOP:** Even a complete 100-station linkage with assumed
uncertainty does not establish that CHM explains genus reappearance.
Ground/understory vegetation and independent capture-detection
calibration remain needed. Another source-specific causal analysis
requires prospectively fixed explanatory tests separate from the
existing already-opened positive seasonal recurrence result.
