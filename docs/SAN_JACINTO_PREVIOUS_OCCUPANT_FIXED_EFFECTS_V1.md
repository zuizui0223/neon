# Previous-occupant fixed-effect analysis v1

Date: 2026-10-07

## Ecological hypothesis

If short-term interference, avoidance, attraction or trap-centred information use contributes to community spatial structure, the species occupying a trap at one check should alter the composition of captures at the same trap during the next check.

The strongest targeted prediction is that a recent kangaroo-rat capture (DKR or SKR) reduces the odds that a smaller rodent species is captured at that trap in the next interval.

## Design

Use only grid-nights for which EARLY, MIDDLE and LATE labels are all represented in the raw capture file. Within those nights, all 49 trap positions are reconstructed at each check as EMPTY or one of the six focal species. Trap-check cells containing multiple species or only non-focal species are excluded.

For each target species, fit a binomial fixed-effect model:

`next target capture ~ previous trap state | trap_id + grid_date_transition`

with standard errors clustered by grid-date.

- trap fixed effects control persistent local microhabitat/trap propensity;
- grid-date-transition fixed effects control the overall abundance/activity state at that check.

The primary ecological contrasts are previous DKR or SKR versus previous EMPTY for next captures of CHFA, PEMA, PEER and LAPM.

## Interpretation boundary

This is observational. A previous occupant can proxy transient animal presence, scent, trap response or other short-lived local conditions. Even with fixed effects, the analysis does not identify scent-mediated avoidance or interference competition causally.

A second lane removes exact same-individual recurrence from same-species transitions to distinguish direct recapture persistence from different-individual conspecific recurrence.
