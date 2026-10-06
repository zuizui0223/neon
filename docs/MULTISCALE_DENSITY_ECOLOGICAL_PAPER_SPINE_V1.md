# Multiscale density accommodation — ecological paper spine v1

**Date:** 2026-10-06  
**Status:** frozen narrative boundary before the first RELEASE-2026 W/B × MNKA development result.

## One biological question

> **When local abundance rises, where does the extra crowding go?**

A population can change its spatial organization at two nested levels:

1. individuals can change the spatial variance of their own short-term space use;
2. individual centres can change their dispersion across the local population footprint.

The ecological object is the **allocation of density dependence across these two spatial levels**.

## Theoretical hook

The programme sits at the intersection of:

- classical density dependence and intraspecific competition;
- home-range / overlap ecology;
- the Niche Variation Hypothesis;
- spatial individual specialization.

The old niche-variation question is whether competition changes within-individual niche breadth, between-individual differentiation, or both.

The spatial version tested here is deliberately geometric:

- (W): within-individual positional variance;
- (B): among-individual-centre variance.

Both are measured on the same squared-distance scale.

## Primary prediction

[
\Delta_\beta = \beta_B - \beta_W > 0.
]

This means abundance affects the two spatial levels asymmetrically, with the within-individual component becoming more compressed or less expansive than the among-centre component.

### Strong-form packing

[
\beta_W < 0, \qquad \beta_B \ge 0.
]

Allowed biological statement:

> **Higher local abundance is absorbed by contraction of individual short-term space use while the dispersion of individual centres is maintained or expands.**

This is the cleanest form of **density accommodation by spatial packing**.

## What is already known and therefore not the paper

Do not headline:

- home ranges shrink with density;
- overlap changes with density;
- spatial connectedness rises with density;
- animals become habitat specialists at high density;
- within- and between-individual niche components exist;
- live-trap data need careful observation-process controls.

Those are literature or methods context.

## What would be new if replicated

> **Density dependence is not a single-scale property of animal space use: the same increase in local abundance can be absorbed differently within individuals and among individual centres.**

The multi-genus NEON design matters because it asks whether this is a repeated spatial-organizational response rather than a single-species home-range result.

## Evidence sequence in the paper

1. **Question and theory:** density dependence can be allocated across nested spatial scales.
2. **Standardized empirical system:** exact 3-night, standard-grid NEON small mammals across many sites and genera.
3. **Primary result:** genus-balanced (Delta_\beta).
4. **Mechanistic sign structure:** separate (eta_W) and (eta_B).
5. **Generality:** frozen eight-genus replication and leave-one-genus-out stability.
6. **Observation-process limits:** short-term live-trap space-use variance, not complete home ranges.
7. **Future confirmation:** first post-RELEASE-2026 NEON observations under the frozen contract.

The structural audits, saturation guard, taxonomy lock, centroid correction and synthetic support work belong in Methods / Supplement, not in the title or ecological claim.

## Prespecified outcome map

### A. Strong packing

Conditions:

- (Delta_\beta > 0);
- replication guard passes;
- (eta_W < 0);
- (eta_B \ge 0).

Story:

> More mammals fit into local space primarily by compressing individual short-term space use rather than by proportionally expanding population-centre dispersion.

### B. Cross-scale redistribution without individual contraction

Conditions:

- (Delta_\beta > 0);
- replication guard passes;
- strong-form signs fail.

Story:

> Density dependence differs between spatial levels, but the data do not support individual compression as the mechanism.

Do **not** call this packing.

### C. Scale-conserved or reverse response

Condition:

- (Delta_\beta \le 0) or effectively null under the frozen model.

Story:

> The predicted redistribution of density dependence across spatial scales is not supported.

This is a direct falsification.

### D. Taxonomically heterogeneous response

Condition:

- pooled (Delta_\beta > 0) but frozen genus replication / leave-one-genus-out guard fails.

Story:

> Cross-scale density responses are lineage- or context-dependent rather than a general small-mammal principle.

Do not rescue with post-hoc habitat, body-size or latitude subgroups.

## Claim ceiling

Even under Outcome A:

- say **short-term space-use variance**, not home-range size;
- say **association with local abundance**, not experimentally demonstrated causation;
- do not infer natural movement from every capture-to-capture transition;
- do not claim all mammals generalize from NEON box-trappable small mammals.

## Candidate title family after development result

Only choose after the frozen outcome is known.

If A:
- *Crowding is absorbed across spatial scales in small-mammal populations*
- *Density compresses individual space use before population spatial extent*

If B:
- *Density dependence is redistributed across nested scales of mammal space use*

If C/D:
- retain a falsification/heterogeneity title rather than reframing the endpoint.


## 2026-10-06 development update: the universal packing hypothesis failed, revealing response modes

The first frozen RELEASE-2026 development fit did **not** satisfy the preregistered 6/8 genus generality guard. That failure is retained.

However, the failure was structured rather than a collapse of the pooled signal.

Genus-balanced estimates were:

- beta_W = -4.395 m^2 / MNKA;
- beta_B = +4.977 m^2 / MNKA;
- Delta_beta = +9.372 m^2 / MNKA.

All eight leave-one-genus-out Delta estimates remained positive, but only 5/8 genus-specific estimates were positive.

Post-result diagnostics identified two repeated multi-site modes:

### Mode 1 — individual packing with centre maintenance/dispersion

Development genera:

- Chaetodipus;
- Myodes;
- Peromyscus.

Pattern:

- W decreases;
- B is maintained or increases;
- Delta > 0;
- raw-B and debiased-B agree in direction;
- every leave-one-site-out Delta remains positive.

Interpretation:

> Rising abundance is accommodated mainly by reducing the spatial variance of each individual's short-term use while preserving or increasing the dispersion of individual centres.

### Mode 2 — population-footprint compression

Development genera:

- Dipodomys;
- Sigmodon.

Pattern:

- B decreases;
- Delta < 0;
- raw-B and debiased-B agree in direction;
- every leave-one-site-out Delta remains negative.

Interpretation:

> Rising abundance is accommodated partly by compressing the arrangement of individual centres themselves, shrinking the local population footprint rather than maintaining centre spacing.

The original universal-packing hypothesis therefore remains failed. The candidate discovery is **heterogeneity in the spatial level at which density is accommodated**.

## Updated literature boundary

The following ideas are already established and are not novelty claims:

- population density changes home-range size and overlap;
- territoriality changes density–home-range–overlap relationships;
- density can alter territory size and territorial intrusion;
- density can alter habitat specialization;
- within- and between-individual variation can respond differently to density;
- the Niche Variation Hypothesis partitions population niche variation into within- and between-individual components.

The candidate conceptual contribution is narrower:

> **Animal populations may possess alternative spatial density-accommodation modes that differ in whether crowding is absorbed within individual space use or by compression/dispersion of the arrangement of individual centres.**

This is a geometric population-organization claim, not a claim that density dependence, territorial plasticity, or within/between-individual decomposition is new.

## Observation-process challenge and falsification

A real density-dependent recapture-selection process was detected:

- unique tagged individuals increase by +0.931 per MNKA;
- repeat-supported individuals increase by only +0.268 per MNKA;
- repeat-supported fraction decreases by -0.00829 per MNKA;
- the fraction slope is negative in all eight genera.

Therefore the live-trap observation process becomes more selective at higher abundance.

A broad density-invariant single-catch null reproduced this decline in repeat support but generated much smaller spatial slopes:

- maximum simulated Delta_beta across 36 single-catch cells = +2.135;
- minimum simulated beta_W = -0.478;
- observed Delta_beta = +9.372;
- observed beta_W = -4.395.

The closest cells to the observed support-process slopes produced Delta between roughly -0.43 and +1.32, not +9.37.

Allowed conclusion:

> Simple three-night single-catch competition and repeat-support selection are insufficient to explain the magnitude of the pooled development pattern under the simulated density-invariant spatial null.

Not allowed:

- claim that all detection bias is excluded;
- claim causality;
- use the null to reverse the original 5/8 generality failure.

## Prospective test generated by the development result

A separate future-response contract now freezes the two-mode prediction before any post-RELEASE-2026 response is opened:

`results/multiscale_density_future_mode_confirmation_contract_v1.json`

Packing-mode directional confirmation:

- Chaetodipus;
- Myodes;
- Peromyscus.

Footprint-compression directional confirmation:

- Dipodomys;
- Sigmodon.

Microtus, Napaeozapus and Onychomys are excluded from the confirmatory mode classification because the development evidence was site-sensitive or single-site.

The future confirmation is a **new hypothesis test generated by the failed universal hypothesis**, not a rescue of that hypothesis.
