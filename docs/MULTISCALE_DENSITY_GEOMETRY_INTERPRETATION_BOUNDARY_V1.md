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

## Prior-art update and logical counterexample (2026-10-08)

**Nearest-neighbour distances from live-trap centroids are not novel in themselves.**
For example, *My niche: individual spatial niche specialization affects within-
and between-species interactions* (2020; https://pmc.ncbi.nlm.nih.gov/articles/PMC7003455/)
used capture-mark-recapture coordinates to estimate individual spatial centres
and nearest conspecific/heterospecific neighbors. A second methodological
reference (2022; https://pmc.ncbi.nlm.nih.gov/articles/PMC9418289/) illustrates
how trapping-derived spatial-use networks require a calibrated observation model.

Recent macro-level context:
- 2025 *Nature Ecology & Evolution* (https://doi.org/10.1038/s41559-025-02843-z):
density often increases network connectedness across wild animals, commonly
with nonlinear effects.
- 2026 *Journal of Mammalogy*
(https://academic.oup.com/jmammal/article/107/4/848/8725976):
kinship and local density jointly influence overlap in a largely solitary
ground squirrel.

Thus the **remaining empirical hypothesis** is not that density alters spatial
association, not that neighboring centers can be estimated from CMR, and not
that some species have different responses. It is whether the frozen within/between
variance allocation relates to independently interpretable **local geometry
after accounting for cohort size, marginal spatial footprint and detection**.

A simple equal-m logical counterexample: ten centroids regularly spaced
within a grid yield B_observed=333.33 m² and mean squared nearest-neighbor
distance=100 m². Ten centroids arranged as two groups of five coincident
points at opposite grid corners yield B_observed=3555.56 m² but mean squared
nearest-neighbor distance=0 m². This is an illustration only, **not** an
empirical NEON result. The geometry unit test implements this counterexample.

Scope guard: if both local-spacing randomization references explain away
all apparent signal, retain a *descriptive footprint-variance change*, not
a biological spatial-repulsion story. Even agreement is not proof of
competition, territoriality, or socially driven space use.
