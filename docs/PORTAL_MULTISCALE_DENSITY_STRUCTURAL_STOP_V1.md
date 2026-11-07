# Portal multiscale-density structural stop v1

**Date:** 2026-10-06  
**Status:** STOP before any Portal spatial effect extraction.

## Question

Can the pinned Portal Project rodent data support the same biological estimand as the NEON multiscale-density programme: within-individual spatial variance (W) and among-centre variance (B) measured within one standardized sampling session?

## Pinned source

- Repository: `weecology/PortalData`
- Commit: `72d7ff8568052763bf6899dc462e285684cf20f6`
- Protocol source: `SiteandMethods/Methods.md`

## Effect-blind structural finding

Portal has an excellent fixed spatial design: 24 plots, each with a permanent 7×7 rodent trapping grid of 49 stakes at 6.25 m spacing. Rodents are surveyed approximately monthly.

The blocking fact is temporal. A monthly survey spans two nights across the experiment, but **each plot is trapped for one night**. Therefore a species × plot × monthly-survey unit does not contain repeated trapping nights from which the same individual's within-session (W) can be estimated.

The database has a long-term unique individual `id`, so between-month movement could be studied. That would be a different temporal estimand.

## Decision

**STOP the Portal route for the current W/B paper.**

Do not rescue it by:

- joining successive monthly surveys into a wider "session";
- redefining (W) as between-month displacement;
- pooling plots across different survey nights;
- using Portal (B) alone as if it were a cross-scale replication.

Those changes would alter the biological question after seeing that the intended session is not estimable.

## Evidence boundary

No Portal:

- spatial distances;
- (W);
- (B);
- abundance slope;
- density effect

was opened for this decision.

Portal remains a possible source for a separately preregistered between-month movement/density study, not for the present same-session multiscale-density hypothesis.
