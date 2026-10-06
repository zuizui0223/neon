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

- (W) denote individual-scale spatial variance;
- (B) denote between-individual spatial variance in individual session centres;
- (N) denote local abundance or density.

The central prediction is the cross-scale inequality

\[
\beta_W < \beta_B,
\]

where (\beta_W) and (\beta_B) are abundance responses measured on the same variance scale and, where supported, the same log-response scale.

The strongest pattern would be

\[
\beta_W < 0, \qquad \beta_B \ge 0,
\]

meaning that individuals contract their own spatial use as abundance rises while the dispersion of individual centres is maintained or expands.

This is **density accommodation by packing**.

The programme does not require that exact sign combination. The confirmatory target is the preregistered cross-scale contrast, not a post-hoc choice of whichever component is significant.

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

### Frozen spatial geometry boundary

The primary coordinate system is the **nominal NEON trap lattice encoded by `trapCoordinate`**.

- Standard NEON mammal grids: 10 × 10 traps at 10 m spacing, spanning 90 × 90 m.
- SRER is a protocol exception with a 7 × 7 grid and is excluded from the primary standard-geometry contrast.
- SRER may enter only as a separately calibrated secondary geometry.
- Historical latitude/longitude or Named Location coordinates are not used to define the primary within-grid distances.

This choice is prospective and design-based. It avoids allowing historical geolocation corrections or shifted Named Locations to create apparent ecological changes in within-grid variance. A geographic-coordinate sensitivity may be added only with current geoNEON/locations metadata and cannot replace the nominal-grid primary result.


## Candidate individual-scale metrics for development

No final metric is selected from an observed ecological effect.

The mechanically preferred coordinate-based candidate uses a pairwise U-statistic. For individual (i) with (k_i\ge2) valid capture locations (x_{ij}),

\[
W_i =
\frac{1}{2\binom{k_i}{2}}
\sum_{j<\ell}\|x_{ij}-x_{i\ell}\|^2.
\]

This is exactly the trace of the unbiased sample covariance of that individual's observed locations. The session-level (W) is the equal-individual mean of (W_i), so individuals with many recaptures do not automatically receive more weight.

A session-level SCR/SECR spatial scale remains an alternative only where the effect-blind support gate shows adequate spatial recaptures.

Singly captured individuals are **unresolved for (W)**, not zero movement. The structural audit must therefore quantify how much of each species × grid × session is represented by repeated-location individuals before this route can advance.

## Candidate population-footprint metrics for development

The footprint metric must not increase mechanically merely because (N) increases.

The mechanically preferred coordinate-based candidate is the half mean pairwise squared distance among (m\ge2) per-individual session centres (c_i):

\[
B =
\frac{1}{2\binom{m}{2}}
\sum_{i<r}\|c_i-c_r\|^2.
\]

This equals the trace of the unbiased sample covariance of the individual centres. Under iid sampling from an unchanged centre distribution, its expectation is independent of the number of sampled individuals (m). That removes the finite-(N) rise built into a variance computed with denominator (m), and is preferable to occupied-trap count as the primary footprint candidate.

The primary within-versus-between comparison uses the **same repeat-captured individual cohort** for both W and B. Thus B is calculated from the session centres of exactly the individuals contributing to W. An all-individual footprint, including singly captured animals, may be retained only as a frozen sensitivity because it has a different observation-support process.

A secondary candidate is effective occupied-trap number / entropy standardized against a null preserving:

- active trap set;
- trap-night effort;
- number of unique individuals;
- per-individual capture frequency where relevant.

Any footprint metric that is a deterministic or near-deterministic function of (N), occupied-trap count, nominal grid size or grid identity is rejected.

## Variance-scale interpretation and centroid uncertainty

The U-statistic definitions place (W) and (B) on the same units of squared distance and give them a direct variance interpretation.

For each eligible individual,

\[
c_i = \operatorname{mean}_j(x_{ij}).
\]

The observed centre (c_i) is itself estimated from finitely many captures. Under an iid repeated-location benchmark with finite second moments, centroid uncertainty has an exact expectation-level correction. If individual (i) has (k_i) captures and (W_i) is the unbiased within-individual covariance-trace estimator above, then the noise contribution of the estimated centroids to the between-centre statistic is

\[
C = \frac{1}{m}\sum_i \frac{W_i}{k_i}.
\]

Therefore define the prespecified de-biased sensitivity

\[
B_{\mathrm{debiased}} = B_{\mathrm{observed}} - C.
\]

In the iid benchmark, (E[B_{\mathrm{debiased}}]) equals the variance of the latent individual centres. The repository contains an exact finite-state enumeration test of this identity.

This correction is a **mechanical benchmark, not an assumption that live-trap locations are iid**. Before any density slope is opened, a trap-grid simulation must determine whether raw (B) and (B_{\mathrm{debiased}}) retain acceptable behaviour under discrete detectors, edge truncation and heterogeneous capture counts. The future confirmatory contract must then either:

1. choose one prospectively justified primary (B) estimator and freeze the other as sensitivity;
2. require the ecological direction to be robust to both; or
3. abandon the coordinate-decomposition route in favour of a model-based spatial scale.

No choice among these routes may depend on observed (\beta_W), (\beta_B) or (\Delta_\beta).

This route is a scale decomposition, not a claim that trap captures reconstruct complete movement paths.

## Abundance candidates

Development may compare:

- resolved unique individuals per complete species × grid × session;
- effort-standardized capture rate;
- closed/SCR density where estimable.

The primary (N) must describe the session population rather than the number of individuals eligible for (W). Repeated-location support is an observation/support quantity and must not be substituted for abundance.

The final abundance variable, any offset/effort term and the handling of zero-valued spatial metrics must be frozen before future response access.

## Primary model concept

For the mechanically validated final metrics, estimate the abundance response at both scales with matched species/site/year structure. A schematic form is

\[
g(W_{gst}) = \alpha_s + \beta_W g_N(N_{gst}) + u_{site} + u_{year} + \epsilon,
\]

\[
g(B_{gst}) = \gamma_s + \beta_B g_N(N_{gst}) + v_{site} + v_{year} + \eta,
\]

where the transformations (g) and (g_N) are frozen before confirmation. If both metrics are positive and log-transformed, (\beta_W) and (\beta_B) are directly comparable elasticities.

The primary ecological contrast is

\[
\Delta_\beta = \beta_B-\beta_W.
\]

Primary prediction:

\[
\Delta_\beta > 0.
\]

The analysis must retain species-level effects rather than allow one abundant taxon to define the result.

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
- edge/grid truncation audit on the standard 10×10 geometry, including a fixed-footprint null in which individual centres are sampled from an unchanged grid-scale distribution across varying N;
- separate mechanical calibration for the SRER 7×7 exception; it cannot lower the primary standard-grid support threshold;
- audit of repeated-capture support versus session abundance so that W estimability is not mistaken for a density response;
- observed multi-coordinate or movement status must not enter primary eligibility;
- no pooling of one-night and three-night sessions if their estimands are not comparable.

## Literature boundary

Already established:

- individual home ranges often contract with density;
- *Peromyscus* home-range size in NEON decreases with density;
- density and SCR movement scale can be structurally linked through home-range overlap;
- high-density small-mammal phases can combine smaller ranges with greater overlap;
- animal space use can be partitioned into within- and between-individual components;
- animal spatial-network connectedness generally increases with density across many taxa;
- multi-scale responses can differ.

Candidate contribution:

> **A standardized, multi-site test of how changing small-mammal abundance is accommodated jointly at individual and population spatial scales within the same sampling sessions.**

The novelty is the **cross-scale density response**, not the variance identity or the existence of density dependence.

## Frozen ecological decision map

The paper-level interpretation is determined by the **joint sign structure** of the two preregistered abundance responses, not by selecting whichever single slope is significant.

### A. Cross-scale accommodation supported

If

\[
\Delta_\beta = \beta_B-\beta_W > 0
\]

with the frozen taxonomic and geographic replication requirements satisfied, then higher abundance is accommodated disproportionately at the individual scale relative to the population-footprint scale.

The strongest biological form is

\[
\beta_W<0,\qquad \beta_B\ge0.
\]

Allowed interpretation:

> **As local abundance rises, individuals compress their own spatial use more strongly than the population footprint contracts; crowding is absorbed by within-population packing rather than by proportional loss of population space.**

This is the focal hypothesis.

### B. Scale-conserved density response

If

\[
\Delta_\beta \approx 0
\]

within the preregistered uncertainty criterion, density dependence is approximately conserved across the two measured spatial scales.

Allowed interpretation:

> Individual-scale contraction is accompanied by a comparable population-footprint response; the data do not support redistribution of density dependence across scales.

This falsifies the focal cross-scale accommodation hypothesis.

### C. Whole-population spatial compression

If both slopes are negative and

\[
\beta_B < \beta_W,
\]

population centres contract at least as strongly as individual space use.

Allowed interpretation:

> Increasing local abundance coincides with spatial compression at both levels, opposite to the packing-first prediction.

This is a biologically informative falsification, not a rescue target.

### D. Population expansion dominates

If (\beta_B>0) while (\beta_W\ge0), higher abundance is accommodated primarily by expansion of the population footprint rather than individual compression.

This is also a prespecified alternative outcome and must not be renamed “packing”.

### E. Taxonomic or geographic replication fails

Even if the pooled (\Delta_\beta) is positive, no general cross-scale claim is allowed if the frozen taxonomic or geographic replication gate fails.

No species-specific, site-specific or habitat-specific subgroup may rescue the general claim.

## Why this is an ecological question rather than a variance identity

The total spatial variance of capture locations can be decomposed algebraically into within- and between-individual components, but the hypothesis does **not** follow from that identity.

The empirical claim concerns how the two separately estimated components respond to a third variable, abundance, across repeated species × grid × session observations. The algebra imposes no requirement that (\beta_W<\beta_B), nor any required sign for either slope.

The mechanical validation therefore has two jobs:

1. remove finite-sample dependence of (B) on the number of observed individuals;
2. quantify observation-support and grid-edge effects that could otherwise create a spurious cross-scale contrast.

Only after those checks is (\Delta_\beta) interpretable as an ecological density-response contrast.

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
- counts of coordinate-bearing capture nights per individual;
- site/year/session coverage.

Do not calculate (W), (B), density slopes or habitat effects until that support audit is frozen.
