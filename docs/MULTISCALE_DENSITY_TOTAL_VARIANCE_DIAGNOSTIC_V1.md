# Multiscale density — post-result total-variance diagnostic v1

**Date:** 2026-10-06  
**Status:** post-result descriptive interpretation only. Not part of the frozen primary test.

## Motivation

The frozen development model estimated the density slopes of two additive spatial-variance components on the same squared-distance scale:

- within-individual short-term positional variance, (W);
- among-individual-centre variance, (B).

For a matched individual cohort, the law of total variance motivates the descriptive total

[
T = W + B.
]

This identity is not a methodological novelty. Analogous within + between decompositions are standard in niche-variation and variance-partitioning literatures.

The post-result question is whether the pooled development pattern reflects a large change in total spatial variance, or primarily a redistribution between its components.

## Frozen development estimates

From `results/multiscale_density_development_result_v1.json`:

[
\beta_W = -4.3948,
qquad
\beta_B = +4.9769
]

m² per unit genus MNKA.

Therefore, algebraically,

[
\beta_T = \beta_W + \beta_B = +0.5821
]

m² per MNKA, whereas

[
\Delta_\beta = \beta_B - \beta_W = +9.3718.
]

The cross-scale reallocation contrast is therefore about sixteen times larger in magnitude than the net total-variance slope.

## Descriptive interpretation

At the genus-balanced pooled level, rising abundance is associated much more strongly with a **change in how spatial variance is partitioned** than with a change in the total amount of spatial variance.

In plain ecological language:

> A population-level measure of overall spatial spread can appear nearly stable while its internal spatial organization changes substantially.

For the pooled development pattern, the within-individual component contracts while the among-centre component expands by a similar magnitude.

This resembles the logic of the Niche Variation Hypothesis, where a population niche can remain similar in total width while the contributions of within- and between-individual variation change. Here the decomposition is geometric space use rather than diet or habitat composition.

## Why this matters

Many density-space studies focus on one endpoint:

- home-range size;
- overlap;
- territory size;
- population density;
- nearest-neighbour spacing.

Those endpoints can miss compensatory changes at another spatial level.

The present development result suggests that a weak net change in population spatial variance does **not** imply weak density-dependent spatial reorganization.

## Boundary

This is post-result interpretation.

It cannot:

- replace the failed original 6/8 generality guard;
- be presented as a preregistered prediction;
- be called a new variance identity;
- establish that total spatial variance is biologically conserved;
- establish causality.

It can motivate a future preregistered prediction that density may alter the **allocation** of spatial variance more strongly than its total magnitude.
