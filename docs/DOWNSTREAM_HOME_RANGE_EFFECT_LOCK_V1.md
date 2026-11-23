# Downstream home-range sensitivity — effect lock v1

Date: 2026-09-29

Status: frozen before MCP areas or FIRST/LAST downstream differences are calculated.

## Question

Does choosing FIRST versus LAST capture as the single nightly spatial state materially change an individual-level home-range estimate?

## Eligibility

Use the previously frozen effect-blind eligibility rules:
- >=10 distinct capture nights;
- >=5 unique FIRST flags;
- >=5 unique LAST flags;
- non-collinear FIRST geometry;
- non-collinear LAST geometry.

The analysis proceeds only if the frozen species support gate is satisfied:
- PEMA >=20 eligible individuals;
- PEER >=15 eligible individuals.

## Primary downstream estimator

For every eligible individual, calculate the 100% minimum convex polygon area from all nightly FIRST locations and separately from all nightly LAST locations.

MCP is used here as a deterministic sensitivity diagnostic with no bandwidth or smoothing choice. It is not presented as the universally optimal biological home-range estimator.

Define area_ratio = max(area_FIRST, area_LAST) / min(area_FIRST, area_LAST).

A material individual-level change is prospectively defined as area_ratio >= 1.25.

Thus the representative-night choice must change MCP area by at least 25% multiplicatively to count as material.

## Species-level confirmatory rule

For each species:
- estimate the fraction of eligible individuals with area_ratio >=1.25;
- compute a two-sided 95% Wilson interval;
- calculate the median area_ratio.

Species passes only if:
1. lower 95% Wilson bound for the material-change fraction >0.25; and
2. median area_ratio >=1.25.

The downstream result is confirmed only if both PEMA and PEER pass.

Pass: confirm_downstream_home_range_sensitivity.
Fail: home_range_downstream_sensitivity_not_replicated.

## Secondary, non-rescuing summaries

- FIRST and LAST MCP area distributions;
- signed log area ratio log(area_LAST/area_FIRST);
- RMS radius from centroid under FIRST and LAST;
- RMS multiplicative ratio;
- grid-specific material-change fractions;
- leave-one-grid-out species summaries.

## Claim boundary

If confirmed:

> In two held-out Peromyscus species, choosing the first versus last within-night capture as the retained nightly location materially changes deterministic live-trap home-range area estimates for a substantial fraction of well-sampled individuals.

Not allowed:
- true home-range bias;
- statement that FIRST or LAST is biologically correct;
- SCR sigma claim;
- universal effect across all home-range estimators.

At this lock:
- MCP areas inspected: false
- MCP area ratios inspected: false
- RMS radius differences inspected: false
- ecological/model fits: 0
