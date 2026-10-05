# San Jacinto spatial-regime ecology paper architecture v1

**Branch:** `ecology/san-jacinto-transition-niche-v1`  
**Status:** analysis route closed; manuscript architecture frozen from current evidence  
**Primary journal fit:** *Journal of Animal Ecology*  
**Secondary fit:** *Movement Ecology* / *Oikos*  
**Not currently justified:** *Ecology Letters* without an independent system or direct habitat/mechanism closure

## Working title

**Spatial niche partitioning is encoded in recurring multi-night footprints rather than movement steps in a rodent guild**

Alternative:

**Community spatial segregation persists beyond individual identity but not at the scale of movement steps**

## One question

> **At what temporal and organizational scale is spatial niche partitioning encoded in a mobile mammal community?**

This is the only main question.

The paper does not ask whether temporal aggregation biases an estimator. It asks where the biological spatial structure actually resides.

## Competing ecological hypotheses

### H1 — step-level avoidance

Spatial segregation is continually maintained because within-night movements are directed so as to preserve separation among species.

**Prediction:** for exactly the same origin and movement length, observed movement directions should preserve higher community C-score than feasible random directions.

**Result:** rejected.

- 18 informative grid-seasons
- 1,968 randomized repeat nights
- global standardized excess = −0.197
- one-sided p = 0.800

### H2 — stable point-like individual centres

Spatial segregation is encoded mainly in species-specific placement of stable individual seasonal centres.

**Prediction:** one seasonal point per individual should retain non-random species segregation.

**Result:** rejected under the frozen anchor-label null.

- 1,334 individual seasonal anchors
- 30/30 informative public-data grid-seasons
- global T = −0.012
- p = 0.532

### H3 — recurring multi-night space-use footprints

Spatial segregation is encoded in the **distributed set of locations repeatedly used across nights** rather than in one point or in each movement step.

**Prediction:** removing later same-night recaptures should retain the segregation signal, whereas collapsing multi-night use to one point should destroy it.

**Result:** supported.

On the separately frozen 30-unit public-data universe:

- ALL captures: 8 segregated, 0 aggregated
- NIGHT-FIRST: retained 7/8 reference segregation signals
- ANCHOR: retained 0/8
- ALL vs NIGHT-FIRST SES r = 0.947
- ALL vs ANCHOR SES r = 0.109

Frozen classification: **between-night footprint**.

### H4 — species-specific recurring-use domains among individuals

If the community result is genuinely carried by recurring footprints, different individuals of the same species should use more similar multi-night footprints than heterospecific individuals even after controlling for how many traps each footprint contains.

**Result:** supported.

- 928 multi-night individuals
- 22/22 informative grid-seasons
- 20/22 raw conspecific-minus-heterospecific overlap contrasts positive
- global standardized footprint assortativity T = 2.315
- p = 0.00010
- correlation with NIGHT-FIRST community segregation SES r = 0.694

Post-result equal-grid robustness:

- 6/7 physical grids positive
- exact sign-flip p = 0.015625

### H5 — spatial template beyond individual identity

Seasonal persistence may still be a trivial consequence of repeatedly observing the same site-faithful individuals.

**Prediction:** species × trap recurrence should remain above a fixed-fixed null after removing every individual observed in both the EARLY and LATE seasonal halves.

**Result in the fixed segregated reference regimes:** supported.

- 188 bridge individuals removed
- 8/8 reference units informative
- 7/8 positive
- T = 1.037
- p = 0.00160

The signal is much weaker than with bridge individuals retained (original temporal-persistence T = 4.091), so individual site fidelity is an important amplifier rather than an irrelevant nuisance.

## Generalization boundary

A post-result generalization audit applied the identical turnover rule to the broader pre-existing temporal-persistence universe.

Support:

- 18 eligible grid-seasons
- 6 physical grids

Grid-season result:

- 13/18 positive
- mean Z = 0.752
- global p = 0.00080

But physical-grid robustness failed the frozen criterion:

- 5/6 grid means positive
- exact six-grid sign-flip p = 0.125

Decision:

`broader_turnover_generalization_not_supported`.

Therefore the supra-individual template is demonstrated **within the strongly segregated regimes**, not generally across every grid.

## Biological answer

The results reject two simple mechanisms:

1. the community is not kept segregated by continual directional avoidance at every within-night move;
2. the segregation is not recoverable as one fixed spatial centre per individual.

Instead, the signal resides at an intermediate scale:

[
	ext{movement step}
;<;
mathbf{recurring multi-night spatial footprint}
;<;
	ext{seasonal community pattern}.
]

Within that middle scale there are at least two layers:

[
	ext{persistent grid/species template}
;+;
	ext{individual site fidelity amplification}.
]

The strongest defensible statement is:

> **Spatial niche partitioning in this rodent guild is carried by persistent species-associated domains of repeated multi-night space use. Individual site fidelity strengthens those domains, but the pattern can persist after complete individual turnover within the strongly segregated spatial regimes.**

## General principle

Do not sell “movement matters”, “scale matters”, “animals have home ranges”, or “memory creates stable space use” as new.

The more specific principle is:

> **Community spatial structure can be organized at an intermediate temporal scale that is invisible both to moment-to-moment movement rules and to one-point summaries of individuals.**

A second, more tentative principle from the turnover result is:

> **Persistent community spatial structure can outlive the individuals that expressed it, while still being amplified by individual site fidelity.**

The second statement must remain conditioned on the fixed segregated regimes because broader physical-grid generalization did not pass.

## Why the result is surprising

The original system already contains direct evidence of interspecific dominance/avoidance and published spatial niche partitioning.

A natural expectation is therefore that the spatial pattern should be visible either:

- in short-term movement direction away from heterospecific space; or
- in stable species-specific individual centres.

Neither prediction was supported.

The spatial pattern instead requires **distributed repeated use across nights**.

That is the conceptual pivot of the paper.

## Nearest literature boundary

The manuscript should explicitly acknowledge:

- Chock, Shier & Grether (2018) — direct dominance and heterospecific avoidance in this system.
- Chock, Shier & Grether (2022) — the original temporal overlap, spatial segregation and resource-selection result.
- Schlägel et al. (2020) — movement-mediated community assembly and coexistence.
- Schirmer et al. (2020) and Stiegler et al. (2026) — individual spatial niche / space-use variation and spatial interactions in rodent communities.
- Potts & Börger (2023) — scaling movement decisions to emergent space-use distributions.
- Aarts et al. (2021) — individual memory can generate spatial segregation.
- Verzuh et al. (2025) — habitat and memory can be comparable drivers of animal space use.

These papers mean that neither individual memory nor individual spatial niche is itself novel.

The distinctive contribution is the **within-system causal-scale falsification sequence**:

[
	ext{step direction: no}
ightarrow
	ext{one-point centre: no}
ightarrow
	ext{multi-night footprint: yes}
ightarrow
	ext{same-species individual footprint similarity: yes}
ightarrow
	ext{persistence after individual turnover: weaker but yes in reference regimes}.
]

## Public-data limitation

The deposited capture file does not reproduce two of the 32 published grid-season species rosters:

- grid 3 winter;
- grid 7 winter.

The paper must not claim a full 32-unit reproduction.

The temporal-scale decomposition therefore uses a prospectively frozen **30-unit public-data universe**. Within this universe the ALL representation recovers 8 segregated and 0 aggregated units, matching the published number of segregated units but not the published denominator.

This discrepancy belongs in Methods, Data Availability and Limitations, not in a footnote.

## Mechanism boundary

The data do not distinguish among:

- microhabitat selection;
- burrow/refuge placement;
- resource distributions;
- longer-term competitive sorting;
- territorial/social structure;
- repeated foraging routes;
- other persistent grid-scale environmental constraints.

The trap-level vegetation and soil variables used in the original resource-selection analysis are not contained in the deposited Figshare record.

Therefore avoid “habitat causes the footprint” unless those original environmental data are obtained.

## Figure architecture

### Figure 1 — Hierarchy of competing spatial mechanisms

One conceptual + empirical panel:

- movement step
- point centre
- multi-night footprint
- seasonal community matrix

Show exactly which observations are retained at each scale.

### Figure 2 — Two simple mechanisms fail

Panel A: distance-matched within-night direction test, showing observed effect within/null or negative.

Panel B: seasonal point-anchor label-shuffle result.

Keep this figure compact; these are falsification results, not the headline.

### Figure 3 — The signal appears at the multi-night footprint scale

For the eight fixed reference units:

- ALL
- NIGHT-FIRST
- ANCHOR

Show SES paired by grid-season.

Headline: 7/8 retained by NIGHT-FIRST, 0/8 by ANCHOR.

### Figure 4 — Individual footprints carry species identity

Conspecific vs heterospecific footprint similarity after exact footprint-size control.

Include global T, 20/22 direction count and physical-grid robustness.

### Figure 5 — Spatial persistence outlives individuals, but is attenuated

For the eight reference units, pair:

- original early→late persistence Z
- post-turnover persistence Z

Show bridge-individual removal count and the decrease from global T = 4.091 to 1.037.

Add a small inset for the broader 18-unit / six-grid audit, clearly labelled exploratory and non-generalizing because grid sign-flip p = 0.125.

## Abstract skeleton

**Background:** Spatial niche partitioning is usually inferred from aggregated locations, leaving unresolved whether community segregation is generated by moment-to-moment avoidance, stable individual placement, or repeated space use over longer periods.

**Approach:** Using repeated nightly live-trap detections from a six-species granivorous rodent guild, we decomposed a previously documented spatial-segregation pattern across nested temporal and organizational scales while preserving predeclared null models.

**Results:** Observed within-night movement directions did not preserve greater segregation than distance-matched random directions, and one seasonal point per individual contained no detectable segregation signal. In contrast, retaining only one location per individual-night preserved 7/8 reference segregation signals, whereas one-point seasonal anchors preserved 0/8. Conspecific individuals had more similar multi-night footprints than heterospecific individuals after exact control for footprint size (T = 2.315, p = 0.00010). Species-specific trap use persisted from early to late season (T = 4.091, p = 0.00020) and remained detectable after all individuals shared between halves were removed (T = 1.037, p = 0.00160), although broader physical-grid generalization was not supported.

**Conclusion:** Spatial partitioning was organized at the scale of recurring multi-night space-use domains rather than individual movement steps or point-like centres. Individual site fidelity amplified these domains, while a weaker species-associated spatial template persisted beyond individual identity in the strongly segregated regimes.

## Journal assessment

### Journal of Animal Ecology

Best current fit.

The paper is now a direct animal/community ecology question about how individual space use scales into community spatial structure. Recent JAE work on multi-species rodent spatial interactions confirms topical fit.

### Movement Ecology

Strong backup if reviewers see the contribution primarily as temporal decomposition of space use.

### Oikos

Also plausible if framed around niche partitioning and spatial community assembly.

### Ecology Letters

Not recommended on present evidence.

To become credible there, the strongest additions would be either:

1. an independent community showing the same scale hierarchy; or
2. recovery of the original trap-level habitat data showing what generates the persistent species template.

Neither should be substituted with further post hoc metrics from the same capture file.

## Stop rule

The current public capture dataset is exhausted for the main ecological question.

Do **not** open:

- species-pair searches;
- alternative overlap metrics;
- alternative anchor definitions;
- alternative turnover thresholds;
- hand-built habitat proxies;
- lower-tail interpretations of failed one-sided tests;
- or new simulation mechanisms designed after these outcomes.

Next work should be manuscript construction, external validation, or acquisition of the original environmental covariates.
