# Heteromyid sex-specific recapture validation — design lock v1

Date: 2026-09-29

Status: frozen before sex-specific recapture displacement magnitudes are inspected.

## Purpose

This is an independent biological validation of the population-packing
analysis. It cannot redefine Delta_sex_packing and cannot rescue a failed
Phase-3 primary decision.

Question:

> Within the same NEON pathogen-grid trapping event, do recaptured male
> heteromyids show greater successive-night displacement than recaptured
> females?

## Data

NSF NEON small-mammal box trapping:
- DP1.10072.001
- RELEASE-2026
- expanded package
- pathogen grids only

Taxonomic scope:
- Heteromyidae
- species-rank, unambiguous target taxa only

## Effect-blind estimability stage

Before any male-female displacement magnitude is summarized, count only
whether an individual has enough valid repeated locations.

An individual is recapture-eligible within an event when:
- tagID is present;
- sex resolves to male or female;
- at least two distinct trapping nights have valid trap coordinates;
- species identification passes the frozen taxonomic rule.

A paired event is primary-estimable when:
- >=3 recapture-eligible males;
- >=3 recapture-eligible females.

Sensitivity:
- >=2 per sex;
- >=5 per sex.

No displacement distance, median, sign, coefficient, CI, or p-value is
opened during the estimability stage.

## Validation advance gate

The movement validation advances only if at least two of the frozen
cross-source packing species each have:
- >=5 primary paired pathogen events;
- representation at >=2 NEON sites.

If this gate fails, movement validation is recorded as non-estimable and
the Phase-3 packing result stands alone.

## Outcome if the gate passes

For each recapture-eligible individual:
1. retain one location per night under deterministic night ordering;
2. sort nights by collection date and night ID;
3. calculate successive-night Euclidean displacements;
4. summarize the individual by the median successive-night displacement;
5. transform as log1p(displacement_m).

Within each paired event:

Delta_sex_movement =
median(log1p displacement) among males
minus
median(log1p displacement) among females.

Positive values indicate greater male successive-night displacement.

## Hierarchical estimator

For each frozen eligible species:
- event contrasts are averaged within site;
- site means are averaged with equal site weight to form the species effect.

The validation family effect is the equal-weight mean over the frozen
eligible species.

Uncertainty is Student-t over site means for species effects and over
species effects for the validation family effect.

## Concordance rule

Movement is directionally concordant only if:
- validation family effect > 0; and
- at least half of the frozen eligible species have positive species
  effects.

This is descriptive validation. It does not change
replicated_positive_support / no_replicated_positive_support from Phase 3.

## Claim boundary

Allowed:
- sex difference in repeated-night displacement within pathogen trapping
  events.

Not allowed:
- natal dispersal;
- breeding dispersal;
- territory size;
- home-range size;
- causal attribution to mating or reproduction.

At this lock:
- sex-specific movement magnitudes inspected: false
- movement effect models fit: 0
