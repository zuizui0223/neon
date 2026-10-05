# Multiscale density accommodation in NEON small mammals — design v1

**Date:** 2026-10-05  
**Status:** ecological redesign lane; no new RELEASE-2026 spatial effect is claimed by this document.  
**Relationship to PR #21:** separate paper line. The live-trap aliasing/MEE paper is not reinterpreted as a mammal-behaviour paper.

## Biological question

> **When local abundance rises, where does the extra crowding go?**

Small-mammal populations can accommodate more individuals in at least two spatially different ways:

1. **individual compression** — each animal uses less space;
2. **population expansion** — individual centres occupy a broader part of the trapping grid.

These responses need not have the same sign.

The primary ecological target is therefore not another home-range-versus-density correlation. It is the **cross-scale allocation of spatial variance with changing abundance**.

## Why this question is distinct from existing NEON work

O'Fallon, Pinter-Wollman & Mabry (2025, *Oecologia*, doi:10.1007/s00442-025-05731-2) already used 10 years of NEON *Peromyscus* data from 36 sites and showed that individual home-range area decreases with increasing density, with habitat, latitude and density interactions.

Therefore this programme must not claim novelty for:

- density dependence of individual home-range size;
- habitat effects on *Peromyscus* space use;
- latitude effects on home-range size;
- using NEON to study deer-mouse home ranges.

The unresolved question is one level higher:

> **Does density-dependent contraction of individual space use coincide with contraction, stability or expansion of the population spatial footprint?**

A population can contain more animals even while individuals use less space. That cross-scale response determines whether higher density is accommodated primarily by **packing** or by **spatial expansion**.

## Core hypothesis

Let:

- (W) denote an individual-scale spatial-use metric;
- (B) denote a between-individual / population-footprint metric;
- (N) denote local abundance or density.

The central prediction is a cross-scale inequality:

[
eta_W < eta_B,
]

where (eta_W) and (eta_B) are the abundance responses of individual-scale and population-footprint spatial extent on comparable standardized/log scales.

The strongest pattern would be:

[
eta_W < 0,qquad eta_B ge 0,
]

meaning that individuals contract their space use as abundance rises while the population footprint is maintained or expands.

This is **density accommodation by packing**.

The programme does not require that exact sign combination. The confirmatory target is the cross-scale contrast, not a post-hoc choice of whichever component is significant.

## Ecological interpretation

The general principle being tested is:

> **Density dependence can be redistributed across spatial scales. More animals do not necessarily require proportionally more population space if individual space use contracts.**

This connects individual behavioural plasticity to population spatial organization without assuming that either scale alone determines the other.

## Data boundary

### RELEASE-2026

Already response-consumed.

May be used only for:

- schema and effort audit;
- structural estimability;
- mechanical validation of candidate metrics;
- model development;
- taxonomy sensitivity development;
- exploratory ecological estimation clearly labelled as development.

No RELEASE-2026 ecological effect may be relabelled confirmatory.

### Confirmatory response

The first future NEON small-mammal observations not contained in RELEASE-2026.

Before opening that response, freeze:

- eligible sampling types;
- species rule;
- taxonomy rule;
- abundance metric;
- individual-scale spatial metric;
- population-footprint metric;
- effort model;
- minimum-support thresholds;
- model formula;
- primary cross-scale contrast;
- all stop rules.

## Native hierarchy

Retain:

1. site;
2. mammal grid / plotID;
3. year;
4. sampling bout / eventID;
5. trapping night / nightuid;
6. trap coordinate;
7. resolved individual;
8. capture event.

The primary ecological unit is **species × grid × sampling session**.

## Sampling design boundary

Individual-scale movement inference requires repeated locations. Therefore:

- three-night pathogen/recapture-compatible sessions are the primary development pool;
- one-night diversity grids can contribute to population-footprint development only if their effort semantics are compatible, but cannot independently identify within-session individual spatial use;
- primary confirmatory cross-scale inference must use sessions where both scales are estimable under the same frozen rule.

Active trap-nights, not nominal grid size, form the observation denominator.

## Candidate individual-scale metrics for development

No final metric is selected here from an observed ecological effect.

Candidate family:

1. mean / median successive recapture displacement among resolved individuals;
2. within-individual squared radial spread around the individual's session centroid;
3. session-level SCR/SECR spatial scale where the support gate is met.

The final candidate must pass an effect-blind support audit and simulation/mechanical validation before future confirmation.

## Candidate population-footprint metrics for development

The footprint metric must not increase mechanically merely because (N) increases.

Candidate family:

1. effort-conditioned mean pairwise distance among per-individual session centres;
2. effort-conditioned spatial variance of individual centres;
3. effective occupied-trap number / entropy standardized against a null preserving:
   - active trap set,
   - trap-night effort,
   - number of unique individuals,
   - per-individual capture frequency where relevant.

A metric that is a deterministic or near-deterministic function of (N), occupied-trap count or grid identity is rejected.

## Exact decomposition route

Where support permits, use capture coordinates (x_{ij}) for individual (i), capture (j).

For individual (i):

[
c_i = operatorname{mean}_j(x_{ij}).
]

Define equal-individual-weight within-individual spread:

[
W = operatorname{mean}_ileft[operatorname{mean}_j |x_{ij}-c_i|^2ight],
]

and between-individual spread:

[
B = operatorname{mean}_i|c_i-ar c|^2.
]

This gives an interpretable within-versus-between spatial decomposition on the trapping grid. Because singly captured individuals have unresolved within-individual spread, this route requires an explicit recapture-support rule and sensitivity analysis rather than silently treating singletons as zero movement.

## Abundance candidates

Development may compare:

- minimum number known alive / resolved unique individuals per session;
- effort-standardized capture rate;
- closed/SCR density where estimable.

The final abundance variable must be frozen before future response access.

## Primary model concept

Within eligible species:

[
log W_{gst} = alpha_s + eta_W log N_{gst} + u_{site} + u_{year} + epsilon,
]

[
log B_{gst} = gamma_s + eta_B log N_{gst} + v_{site} + v_{year} + eta,
]

or the analogous model for the mechanically validated final metrics.

The primary ecological contrast is:

[
Delta_eta = eta_B-eta_W.
]

Primary prediction:

[
Delta_eta > 0.
]

The analysis should retain species-level effects rather than allow one abundant taxon to define the result.

## Replication requirement

Future confirmation must demonstrate both:

- **taxonomic replication** — the cross-scale direction is not carried by one species;
- **geographic replication** — it is not carried by one site/domain.

Exact minimum counts will be frozen after the response-blind RELEASE-2026 structural audit and then copied unchanged to the future-response contract.

## Required controls

- active trap-night effort explicitly represented;
- preserve per-individual capture frequency in spatial randomization;
- leave-one-individual-out influence audit;
- leave-one-night-out audit for multi-night sessions;
- stratify or control mammalGridSamplingType;
- cryptic *Peromyscus* sensitivity using identificationQualifier / identification history;
- edge/grid truncation audit;
- no pooling of one-night and three-night sessions if their estimands are not comparable.

## Literature boundary

Already established:

- individual home ranges often contract with density;
- *Peromyscus* home-range size in NEON decreases with density;
- animal space use can be partitioned into within- and between-individual components;
- multi-scale responses can differ.

Candidate contribution:

> **A standardized, multi-site test of how changing small-mammal abundance is accommodated jointly at individual and population spatial scales within the same sampling sessions.**

The novelty is the **cross-scale density response**, not the variance identity or the existence of density dependence.

## Stop rules

Do not advance the future confirmatory programme if RELEASE-2026 development shows that:

- the two spatial scales cannot be estimated together for enough species/sites;
- the population-footprint metric is mechanically driven by abundance;
- individual-scale estimates are dominated by one or two recaptured animals;
- results depend on one arbitrary spatial metric with no robust alternative;
- taxonomy or effort semantics cannot be resolved prospectively.

Do not rescue a failed future confirmation with:

- new taxa subsets;
- new abundance thresholds;
- new habitat interactions;
- alternative response metrics chosen after seeing effects;
- combining incompatible one-night and three-night designs;
- post-hoc environmental moderators.

## Current next step

Run an **effect-blind structural estimability audit** on RELEASE-2026 using only:

- identifiers;
- sampling type;
- active trap-night effort;
- counts of unique individuals;
- counts of repeated individuals;
- number of distinct capture coordinates;
- site/year/session coverage.

Do not calculate (W), (B), density slopes or habitat effects until that support audit is frozen.
