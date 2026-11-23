# Downstream home-range sensitivity — estimability lock v1

Date: 2026-09-29

Status: frozen before first-vs-last home-range areas or spatial-scale differences are calculated.

## Purpose

Test whether collapsing a repeatedly observed night to one representative trap location can materially alter a familiar downstream spatial analysis, rather than only changing the raw within-night position.

## Focal taxa

- PEMA — Peromyscus maniculatus
- PEER — Peromyscus eremicus

## Frozen nightly representations

For every valid individual-night:
- FIRST = earliest valid nocturnal capture;
- LAST = latest valid nocturnal capture;
- single-capture nights have the same FIRST and LAST location;
- source-row order resolves exact time ties.

Identity is grid × species × unique_ID. Individuals are not linked across grids.

## Effect-blind individual eligibility

An individual is home-range estimable only if all are true:
- >=10 distinct valid capture nights;
- >=5 unique trap flags under FIRST;
- >=5 unique trap flags under LAST;
- FIRST locations include at least three non-collinear coordinates;
- LAST locations include at least three non-collinear coordinates.

Eligibility is determined before any home-range area or FIRST/LAST difference is calculated.

The downstream effect analysis advances only if:
- PEMA has >=20 eligible individuals;
- PEER has >=15 eligible individuals.

Fail: stop_downstream_home_range_not_estimable.
Pass: authorize_downstream_home_range_effect_lock.

## Planned downstream metrics after this gate

Primary:
- 100% minimum convex polygon (MCP) area in m² under FIRST and LAST.

Secondary:
- RMS radius from the individual centroid under FIRST and LAST.

MCP is used as a deterministic sensitivity diagnostic with no bandwidth tuning. It is not claimed to be the universally preferred home-range estimator. The high-information eligibility rule is intended to avoid interpreting very sparse polygons.

At this lock:
- FIRST home-range areas inspected: false
- LAST home-range areas inspected: false
- FIRST/LAST area differences inspected: false
- RMS-radius differences inspected: false
- ecological/model fits: 0
