# Trap-sequence interaction hierarchy — ecological boundary v1

Date: 2026-10-07

Status: post-result exploratory synthesis. Do not describe as preregistered or causal.

## Ecological question

Can the **direction** of short-term previous-occupant effects recover an interspecific interaction ordering that is hidden by symmetric niche-overlap summaries?

The original San Jacinto analysis used symmetric spatial and temporal overlap statistics. Those statistics can show that two species segregate or overlap, but by construction they cannot identify whether A affects B more strongly than B affects A.

Repeated within-night live-trap checks add a directional datum: species A can be the previous occupant and species B the next occupant of the same detector.

## Prior-art boundary

This study does **not** discover previous-occupant effects.

Brouard et al. (2015; PLOS ONE, doi:10.1371/journal.pone.0145006) showed that previous trap occupants can alter subsequent rodent capture, including strong conspecific effects, and reviewed evidence that social rank and heterospecific odour can influence trap entry.

Cachelou et al. (2026; Oikos, doi:10.1002/oik.11715) argue that immediate trap-dependence can contain biological information rather than being only statistical nuisance.

This study also does **not** discover body-size dominance in this guild. Chock et al. (2018; Animal Behaviour 137:197–204, doi:10.1016/j.anbehav.2018.01.015) used simulated territory intrusions and found that body-size asymmetry predicted interspecific dominance of little pocket mice. D. simulans, C. fallax and P. maniculatus were dominant to P. longimembris.

The surviving gap is narrower:

> **Can ordinary repeated live-trapping sequences reveal directional community structure that symmetric niche-overlap summaries miss, and is that structure stable or reconfigured within a night?**

## Current evidence

### 1. Date-shuffle observed/expected network

A trap × trapping-bout date-shuffle null preserves detector identity and bout context while asking whether directed heterospecific succession exceeds or falls below expectation.

Ranking A above B when A→B observed/expected is lower than B→A gives one best six-species ordering:

**SKR > DKR > PEMA > CHFA > LAPM > PEER**

The optimal ordering satisfies 14 of 15 directed dyads. The only discordant edge is SKR–PEER.

The empirical body-mass order is:

**SKR > DKR > CHFA > PEMA > PEER > LAPM**

It satisfies 12 of 15 directed dyads; only 2.78% of all 720 possible species orders score at least this well.

### 2. Trap + grid-date-transition fixed effects

Target-specific binomial models with trap fixed effects and grid-date-transition fixed effects give the **same unique optimal ordering**:

**SKR > DKR > PEMA > CHFA > LAPM > PEER**

Here the optimal ordering satisfies 15 of 15 dyads.

The body-mass order satisfies 13 of 15 dyads; 20/720 = 2.78% of possible orders score at least this well.

Removing exact same-individual recurrence before refitting leaves the same unique 15/15 pooled ordering.

### 2b. Within-night interval split is not evidence for temporal rewiring

The pooled ordering is **not** stable when the two adjacent check intervals are analysed separately under the same trap × bout date-shuffle reference.

- EARLY→MIDDLE has one 14/15 optimum: **SKR > DKR > PEMA > LAPM > CHFA > PEER**.
- MIDDLE→LATE has a maximum score of only 12/15 and three alternative optimal orders.
- Only **9/15 dyads keep the same direction** across the two intervals.
- Body-mass direction agrees with **12/15 dyads early→middle but only 8/15 middle→late**.

A post-result block-bootstrap audit found that none of 15 dyad interval contrasts excluded zero (0/15; exploratory BH q < 0.10 in 0/15). The alternative interval-specific rankings are descriptive estimates, not evidence of biological rewiring. The pooled ranking must not be described as an identified social/dominance hierarchy.

### 3. Independent behavioural concordance

Chock et al. (2018) experimentally tested P. longimembris against three species also present in the San Jacinto data: D. simulans, C. fallax and P. maniculatus. All three were behaviourally dominant to P. longimembris.

The transition-derived ordering places all three above LAPM:

**DKR > PEMA > CHFA > LAPM**

This is external behavioural concordance, although the experiments and trapping study come from the same broader research system and should not be treated as independent replication across systems.

### 4. Spatial scale of the signal

The kangaroo-rat → pocket-mouse asymmetry is restricted to the exact detector. It disappears at adjacent traps (6.25–8.84 m) and wider rings.

Therefore the sequence signal should not be described as direct evidence that dominant rodents exclude subordinate rodents from a 6–9 m neighbourhood.

The defensible interpretation is a **trap-mediated interaction or cue-response ordering**, potentially involving residual odour, capture-point release, trap attraction/avoidance, local animal presence, or combinations of these mechanisms.

### 5. What the stronger fixed-effect model rejects

The pooled statement “kangaroo rats generically suppress all smaller species on the next check” is not supported after strong fixed effects.

Species-specific coefficients include both deficits and excesses. The ecological signal lies in the **relative direction across pairs**, not in a universal negative kangaroo-rat coefficient.

## Why this is more ecological than the aliasing result

A symmetric overlap index asks whether species use similar places or times.

A directional sequence asks **who tends to follow whom**.

These are not equivalent ecological questions. Asymmetric competition can coexist with substantial niche overlap, and population-level overlap need not reveal the direction of competitive effects.

The San Jacinto data therefore offer a possible bridge from:

**coarse niche partitioning → fine-scale ordered interaction network**

rather than another observation-bias paper.

## Claim boundary

Use:

- **directional trap-mediated capture-sequence network**
- **directional cue-response structure**
- **pooled sequence-derived interaction order**

Use `hierarchy` only for the mathematical ordering summary, not as a claim of a fixed biological dominance hierarchy.

Do not yet use as the headline:

- natural dominance hierarchy;
- direct interference competition;
- competitive exclusion;
- scent-mediated dominance;
- causal response to the previous occupant.

The protocol did not experimentally randomize previous occupant identity, trap cleaning, release treatment or odour cues.

## Decisive robustness test

The strongest remaining test is spatial replication of the fixed-effect ordering.

Refit the six target models after omitting each of the eight trapping grids in turn and report:

1. maximum pairwise hierarchy score;
2. whether the full-data optimal order remains among the optimal orders;
3. body-mass-order score;
4. number of unique optimal orders.

Spatial leave-one-grid-out refits remain valuable for asking whether the **pooled** network summary is dominated by one grid. The pooled ordering is spatially reproducible, but the interval split has insufficient statistical resolution to establish or reject time-invariant biological interactions.

## Candidate one-sentence result

> **A rodent guild showing coarse temporal overlap contains detector-local directional capture-sequence asymmetries, some concordant with known body-size dominance, without proving natural interference or within-night network rewiring.**
