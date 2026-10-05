# San Jacinto species-level spatial-template interpretation v2

**Status:** ecological synthesis frozen after Stage 9  
**Branch:** `ecology/san-jacinto-transition-niche-v1`  
**Primary architecture:** `docs/SAN_JACINTO_ECOLOGY_PAPER_ARCHITECTURE_V2.md`

## One-sentence finding

> **A known rodent-community segregation pattern is carried by recurrent species-specific multi-night spatial footprints and can be rebuilt by different individuals across seasons.**

This is not a claim that animals do not move, that individual site fidelity is unimportant, or that habitat has been causally identified.

## What was localized

The analyses successively removed different kinds of spatial information.

### Within-night direction: not the carrier

Holding every repeat-capture origin and exact movement length fixed, observed directions did not preserve more segregation than feasible alternative directions.

- 18 informative grid-seasons
- 1,968 repeat nights
- T = -0.197
- p = 0.800

The seasonal community pattern is therefore not explained by a simple rule in which every short-term move maintains the checkerboard.

### One seasonal point per individual: not the carrier

Reducing every individual to one seasonal medoid of NIGHT-FIRST captures also failed to reveal species-associated placement.

- 1,334 anchors
- 30 informative grid-seasons
- T = -0.012
- p = 0.532

The relevant spatial object is not recoverable as one point per individual.

### Multi-night footprint: the carrier

On the frozen 30-unit public-data universe, the same fixed-fixed SIM9 null used for the published co-occurrence analysis recovered 8 segregated and 0 aggregated ALL-capture units.

When later within-night captures were removed:

- NIGHT-FIRST retained 7/8 reference signals;
- ANCHOR retained 0/8;
- ALL vs NIGHT-FIRST SES r = 0.947;
- ALL vs ANCHOR SES r = 0.109.

Thus the community signal is retained by the distributed set of locations used across nights.

## Why this is not just sampling depth

Two independent tests show that the repeated-use footprint has biological structure.

First, same-species individuals have more similar multi-night footprints than different-species individuals even after species labels are shuffled only among footprints with exactly the same number of traps:

- 928 multi-night individuals
- 22 informative grid-seasons
- 20/22 raw contrasts positive
- T = 2.315
- p = 0.00010.

Second, species identity at traps recurs from early to late season beyond a fixed-fixed occupancy null:

- 8/8 reference units positive
- T = 4.091
- p = 0.00020.

The footprint is therefore not merely a larger sample of positions.

## Individual fidelity is an amplifier, not the whole explanation

Removing every individual observed in both seasonal halves attenuated the recurrence strongly but did not erase it.

- 188 bridge individuals removed
- 8/8 units informative
- 7/8 positive
- T = 1.037
- p = 0.00160.

The reduction from T = 4.091 to 1.037 matters biologically.

A pure “species template” story would ignore the large contribution of individual fidelity. A pure “site-faithful individuals” story would fail to explain the residual signal after complete turnover.

The supported model is layered:

[
	ext{species-level spatial template}
+
	ext{individual fidelity amplification}.
]

## Cross-season reassembly is the strongest result

Stage 9 changed both the individuals and the season.

For each adjacent-season comparison, every marked individual observed in both seasons was removed from both matrices before any spatial recurrence statistic was calculated. The stricter frozen support rule required at least two season-exclusive individuals per species in each season and at least three eligible species.

This yielded 10 fixed comparisons across six physical grids.

Results:

- 10/10 informative
- 9/10 positive
- global Z = 1.775
- one-sided joint Monte Carlo p = 0.00010
- 5/6 physical-grid means positive
- exact six-grid sign-flip p = 0.046875.

Therefore:

> **Species-associated trap use reappears in the next season even when no individual is allowed to carry that recurrence across the seasonal boundary.**

The exact grid-level p-value is discrete and close to 0.05 because only six independent grids contribute. Report that limitation directly.

## Ecological interpretation

The most useful conceptual model is not “stable home ranges despite movement”.

It is:

> **Community spatial organization is encoded in a distributed relationship between species identity and repeatedly used places.**

That relationship is expressed by individuals, but it is not reducible to the identities of those individuals.

This distinguishes three levels:

1. **movement step** — highly dynamic and not directionally maintaining the community pattern;
2. **individual multi-night footprint** — the scale at which species identity becomes spatially organized;
3. **species-level spatial template** — the recurrence of those domains across individuals and across seasons.

The community checkerboard is an emergent summary of level 3.

## What may generate the template

The public capture data cannot discriminate among:

- microhabitat filtering;
- recurring resource patches;
- burrow or refuge distributions;
- longer-term competitive sorting;
- territorial or social constraints;
- repeated foraging-route geometry;
- combinations of the above.

The original study measured trap-level vegetation and soil variables and found species-specific resource selection, making persistent habitat structure a plausible candidate. Those raw trap-level covariates are not present in the deposited Figshare record, so they cannot be used to close mechanism here.

Avoid claiming that competition or habitat “causes” the Stage-9 recurrence.

## Novelty boundary

Several nearby ideas are already established:

- individual spatial niches and personality-dependent space use in rodents;
- movement-mediated community assembly;
- home-range/site fidelity;
- habitat and memory as joint drivers of space use;
- population-level recurring spatial patterns.

The distinctive contribution is not any one of those concepts.

It is the empirical sequence showing where a known community pattern survives and where it disappears:

[
	ext{step direction: no}
ightarrow
	ext{point anchor: no}
ightarrow
	ext{multi-night footprint: yes}
ightarrow
	ext{conspecific footprint similarity: yes}
ightarrow
	ext{within-season persistence: yes}
ightarrow
	ext{complete-turnover persistence: yes}
ightarrow
	ext{cross-season reassembly: yes}.
]

That sequence turns a static observation of niche partitioning into a statement about its organizational scale.

## General principle

A defensible general proposition is:

> **Persistent community spatial structure need not be stored in particular individuals or enforced by each movement decision; it can be repeatedly reconstructed from species-specific patterns of distributed space use.**

The word “stored” is metaphorical in prose. In the manuscript, “encoded” or “expressed” is safer than “memory” unless the cognitive mechanism is measured.

## Scope

Stage 8 is still a real limit. Broad within-season turnover recurrence across 18 grid-seasons passed at the unit level but failed the predeclared six-grid sign-flip criterion (p = 0.125). The current evidence therefore does not justify saying that every part of the assemblage expresses the same strength of supra-individual template.

Stage 9 passes a different, prospectively frozen adjacent-season question across six grids. It supports cross-season reassembly in that strict support set; it does not erase the Stage-8 heterogeneity.

## Publication position

The result is now strongest as an animal/community ecology paper rather than an observation-process or statistical-method paper.

Best current target: **Journal of Animal Ecology**.

The conceptual reach toward **Ecology** is credible because the result links individual space use, temporal turnover and community niche structure. **Ecology Letters** remains a reach because the causal substrate and independent-system generality are still unresolved.

## Stop

No additional endpoint should be opened from the public San Jacinto capture file for the main claim.

The next scientific gains must come from:

- independent replication, or
- the original environmental covariates.

Everything else is manuscript and figure work.
