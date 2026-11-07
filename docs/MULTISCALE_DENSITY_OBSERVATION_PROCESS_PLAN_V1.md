# Multiscale density observation-process plan v1

**Date:** 2026-10-06  
**Status:** pre-effect plan; no W, B, or density-response slope has been opened.

## Why this guard is necessary

NEON small mammals are sampled with live box traps. The same observation process generates:

- the abundance index;
- the repeated locations needed for (W);
- the individual centres needed for (B).

A naive relation between observed capture count and observed space use could therefore be produced partly by detection, trap availability, or recapture support rather than by ecological density accommodation.

The primary analysis must separate the **population-state predictor** from the **observation-support process**.

## Primary abundance candidate: event-level MNKA

The preferred development candidate is minimum number known alive (MNKA), following the direct NEON precedent of O'Fallon et al. (2025).

For each frozen taxon × plot × event series:

1. resolve individual identity prospectively;
2. identify each individual's first and last eligible sampling events at that plot;
3. count the individual as known alive at every eligible event between those bounds;
4. calculate taxon-specific MNKA for each event.

MNKA is an abundance index, not true density.

The final taxonomy rule for individuals whose published identification changes through time must be frozen from NEON identification-history metadata before spatial effects are opened.

## Observation-pressure quantities

Before W or B is calculated, report for every structurally eligible event:

- active trap-nights;
- number of traps/nights represented by the event;
- unique trap-nights with at least one small-mammal capture;
- all-small-mammal capture-trap-night fraction;
- target-taxon capture-trap-night fraction;
- unique tagged individuals;
- repeat-supported tagged individuals;
- repeat-supported fraction among tagged individuals;
- gridCompletion status;
- tagged non-capture status inconsistencies;
- taxonomy conflicts within event × individual.

These are observation-process diagnostics, not ecological response endpoints.

## Trap-saturation boundary

The primary analysis may not interpret a density effect if the apparent abundance gradient is inseparable from trap saturation.

No numerical saturation threshold is chosen from W, B or Delta_beta.

The threshold/model treatment is frozen after the effect-blind observation-pressure distribution is inspected and before any spatial distance is calculated.

Allowed routes are:

1. demonstrate that the primary support lies comfortably below a prespecified saturation boundary;
2. condition/model explicitly on the observation-pressure quantity;
3. restrict to an observation-pressure range using an effect-blind rule;
4. STOP if abundance and observation pressure cannot be separated.

## Effort sensitivity

A secondary abundance proxy may use unique observed individuals per active trap-night.

It cannot replace MNKA merely because it yields a more favourable ecological result.

## Relationship to W/B support

The primary abundance (N) describes the population state.

The number of repeat-supported individuals (m) describes whether W/B can be estimated reliably.

(m) must never substitute for (N), and sessions cannot be selected on observed W/B magnitude or movement direction.

## Evidence boundary

At this stage:

- W: unopened;
- B: unopened;
- Delta_beta: unopened;
- habitat moderators: unopened;
- taxonomic subgroup effects: unopened.

Only abundance-support counts and observation-process diagnostics may be used to finalize the detection/saturation contract.
