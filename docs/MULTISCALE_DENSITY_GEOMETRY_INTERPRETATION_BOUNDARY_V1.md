# Geometry and ecological interpretation boundary for W/B modes

**Audit introduced 2026-10-08 after development W/B slopes were known.**
**Status:** interpretation correction and a new falsification target; not confirmatory.

## The mathematical distinction

The repository's frozen `W` estimates the mean within-individual coordinate variance across **two or three different trap nights**, not full home-range area.

The frozen `B` estimates the debiased trace of the covariance matrix of the **observed individual trap-location centroids**.

Therefore:

- B increasing means that the **distribution of the sampled centroids widens** on the common fixed 10 × 10 grid.
- B increasing does **NOT** imply that each animal is farther from its nearest conspecific.
- B increasing does **NOT** measure territory exclusion, behavioral avoidance, or non-overlap of home ranges.
- W decreasing does **NOT** establish a contraction of undisturbed individual movement or territory.

A population can have many more tightly spaced centers while its overall centroid footprint expands into previously unoccupied peripheral traps. In that case, B may increase while nearest-neighbor distances **decrease**. Treating these as equivalent is a logical error.

As a consequence, the provisional phrase **'packing-like mode'** is only a label for a pattern of W down and B up. Do not write 'territorial packing', 'greater spacing between neighbors', 'behavioral exclusion' or 'competitive segregation' as findings.

## A high-value falsification: perimeter expansion versus local spacing

A separate exploratory comparison of already frozen cohort centroids can distinguish two pattern types:

1. **Spatial-footprint expansion**: rising B accompanied by an increasing fraction of centroids near plot edges or by increasing squared radial distance; nearest-neighbor spacings need not rise.
2. **Regularized spacing**: nearest-neighbor distances are larger than a spatially and sample-size matched null distribution (i.e. unusually even spacing), not merely large in raw meters.

The nearest-neighbor null must preserve m (repeat-supported individuals) and opportunity in the 10×10 finite lattice, and must account for centroid location error and trap-specific availability. A uniform complete-lattice null alone is insufficient because of spatially heterogeneous habitat and capture propensities.

Before interpreting spatial repulsion:

- reproduce original W, B, m and Δ results **without modifying the frozen estimators**;
- verify that centroids are taken from exactly the same matched repeat-supported cohort;
- compare observed local regularity to an abundance-, cohort-size-, and spatially matched observation-process reference;
- require agreement across multiple sites within each development genus;
- treat all RELEASE-2026 local-spacing outcomes as **post-result exploratory**;
- obtain independent observational or experimental data to claim real territorial mechanisms.

## Link to population-history experiment

The support-only phase check is kept separate. A passed phase support gate does not infer spatial spacing or validate a density-memory mechanism, and no two weak post-result explorations may be combined into a fictitious independent confirmation.

## Scientific priority

Publishable biological proposition, if it survives future independent testing:

> Under increasing abundance, taxa may differ not just in the amount of capture-derived space use, but in whether spatial accommodation occurs by **population footprint expansion** or by **local spacing change**.

The released data have *not yet* demonstrated the latter. The present B result is only a centroid-footprint statistic.
