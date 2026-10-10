# Multiscale density structural GO/STOP rule v1

**Date:** 2026-10-06  
**Status:** frozen before any W, B, or abundance-response effect is opened.

## Purpose

Decide whether the session-level multiscale-density hypothesis is structurally testable in NEON before opening spatial distances or ecological slopes.

## Mechanical prerequisite

Let (m_*) be the minimum repeat-supported individual count selected by the frozen synthetic rule in:

`analysis/simulate_multiscale_density_metric_support_v1.py`

The rule chooses the smallest candidate (m) passing every prespecified error criterion in both standard 10×10 latent-centre scenarios.

**Real-data scarcity may never lower (m_*).**

SRER uses a separately calibrated 7×7 geometry and cannot determine or lower the standard-grid (m_*).

## Primary structural pool

Only sessions satisfying all of the following may establish GO:

- RELEASE-2026 record;
- 2015-04 or later;
- standard 10×10 NEON geometry;
- pathogen sampling type;
- at least three trapping nights in the event;
- prospectively accepted `gridCompletion` semantics;
- at least (m_*) tagged individuals with coordinate-bearing captures on at least two distinct trapping nights;
- internally resolvable taxon concept under the frozen NEON taxonomy rule.

No spatial distance, W, B, density slope, habitat effect, or observed movement direction may enter eligibility.

## Replication dimensions inspected at the structural gate

For the primary pool, report without ecological effects:

1. eligible species/taxon × grid × event sessions;
2. eligible NEON taxon concepts;
3. resolved genera represented;
4. sites and plots represented;
5. for each taxon: number of eligible sessions and sites;
6. for each genus: number of eligible sessions and sites;
7. distribution of unique tagged individuals and repeat-supported individuals per session;
8. gridCompletion values;
9. taxonomy-integrity flags;
10. observation-pressure summaries needed to assess trap saturation.

## GO principle

Advance to metric/model development only if the primary pool supports **both taxonomic and geographic replication**, rather than one dominant taxon at one locality.

Exact confirmatory replication minima are chosen once from this effect-blind support table and then copied unchanged into the future-response contract. They cannot subsequently be relaxed after W, B, or abundance-response effects are viewed.

## STOP cases

Stop the current session-level W/B programme if any of the following occurs:

- no standard-grid synthetic (m_*) passes;
- the RELEASE-2026 primary pool has too few (m_*)-supported sessions to estimate repeated abundance responses;
- support is effectively confined to one taxon concept, one genus, or one site;
- taxonomy integrity cannot be frozen prospectively;
- grid completeness or trap saturation makes abundance and repeat support inseparable;
- the only way to continue is to admit diversity one-night sessions, legacy recapture sessions, SRER under the standard-grid calibration, or a wider temporal session.

A STOP is a data-identifiability result, not a negative ecological result.

## Effect boundary

At this decision stage:

- spatial distances opened: no;
- W opened: no;
- B opened: no;
- abundance-response slopes opened: no;
- habitat moderators opened: no.

The only permitted information is structural sampling support and observation-process metadata.
