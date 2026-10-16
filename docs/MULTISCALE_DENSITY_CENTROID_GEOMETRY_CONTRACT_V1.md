# Frozen exploratory centroid-geometry audit (v1)

**Frozen prior to opening new nearest-neighbour/edge × MNKA results on 2026-10-08.** This is a *post-hoc mechanism check in RELEASE-2026 development data*, not a prospective confirmation or a revision of the failed 6/8 genus generality result.

## Ecological problem

Existing positive genus-balanced B slope expresses expansion of the *variance of the distribution of repeatedly captured individuals' centroids*. This does **not** identify greater nearest-neighbour spacing, territorial exclusion, or repulsion. At the same time, nearest-neighbour distances decrease mechanically when more animals are sampled in the same finite area.

Does the positive B relationship coincide with *local spacing that exceeds observation-geometry references*, or is it adequately described as greater population-level positional footprint with unchanged/tighter local packing?

## Input and integrity

Use the exact existing NEON RELEASE-2026 three-night 10 × 10, target, <=30% saturation, m>=5 frozen cohort, genus-level MNKA, 167 within-population series and 8 frozen genera. Do not change taxon nomenclature, m, abundance proxy, W, B, or weighting. Request centroid coordinates from the frozen metric scorer by **optional opt-in only**; the default scorer's keys and numeric results stay unchanged. Join the same 1326 analysis rows used in the frozen development analysis.

A mandatory invariant is reproduction to 1e-8 of genus-balanced frozen Δ=+9.37176547246767 m² per MNKA and 1326 rows, before publishing any new spatial slopes. Fail closed if any centroid-derived B differs from frozen B_observed by more than 1e-8 or the cohort size differs.

## Geometry metrics

For m>=5 centroids in a session on a nominal 0–90m lattice:

- **raw local spacing** = mean over individuals of squared Euclidean distance to each individual's closest *other* centroid, in m².
- **observed population spread** = B_observed, unchanged; B_debiased stays the frozen quantity.
- **edge fraction** = proportion of centroids within 10m of any one of the 0m/90m plot borders. Edge fraction is a coarse footprint diagnostic, NOT true dispersal.
- **null A, within-session x/y reassignment:** hold the entire x-coordinate and y-coordinate multisets separately (and m, B_observed) *exactly fixed*, randomly shuffle which y belongs to which x; calculate expected squared nearest-neighbour statistic. This breaks x-y spatial coupling but preserves the marginal coordinate distributions, so deviation only establishes an unusual two-dimensional arrangement relative to an axis-independent null.
- **null B, series-pool reference:** draw m centroids without replacement from the other sessions in the same taxon×site×plot series, retaining repeated observations as repeated opportunity weights. Require enough candidate centroids or mark missing; do not substitute sampling with replacement. This controls the observed series-level trap/centroid distribution and m, not changes in trapping effort within the series.

Run 199 seeded random draws per eligible session for both nulls (seed 20261008), record counts of undefined comparisons. Define null excess in m² as observed nearest-neighbour squared distance minus the randomization average for each null. Null distributions *do not reproduce all individual detection processes*; interpreting a positive excess as actual biological repulsion is forbidden.

## Predefined exploratory outcomes

1. For the five multisite modes separately, slope of raw nearest-neighbour² against genus MNKA and slope of edge fraction, using **same taxon×plot, site×month, year** fixed effects.
2. Slopes of nearest-neighbour excess versus MNKA against both null A and null B, requiring agreement in direction before talking about a candidate local-spacing signal.
3. Report both null support/coverage, m and B_obs validation, genus slopes, and separately enumerate pooling limitations.
4. If sign of the local-spacing association disappears under either null, label "**observation geometry compatible / no coherent local-spacing evidence**". If signs agree, label "**exploratory candidate only**"; never territoriality.
5. Only future observations excluded from RELEASE-2026 can independently confirm. Preserve the existing seven-taxon and five-genus future mode contracts without adjustment.

The null is not conditionally exchangeable under temporal autocorrelation, spatially heterogeneous density, missing individuals, or trap-specific detection changes, and x/y shuffling can create biologically unreachable combinations. These are *diagnostic references*, not calibrated causal nulls.

## Run

```sh
python -m unittest discover -s tests -p 'test_multiscale_density_centroid_geometry_v1.py' -v
NEON_API_TOKEN=... python -m analysis.audit_multiscale_density_centroid_geometry_v1
```

Output: `build/multiscale_density_centroid_geometry_v1.json`.
