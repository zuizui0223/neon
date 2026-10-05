# San Jacinto species-template ecology paper architecture v2

**Branch:** `ecology/san-jacinto-transition-niche-v1`  
**Status:** main public-data analysis closed after Stage 9  
**Primary journal fit:** *Journal of Animal Ecology*  
**Secondary fit:** *Ecology* / *Oikos* / *Movement Ecology*  
**Reach option:** *Ecology Letters* only with independent-system replication or direct mechanism closure

## Working title

**Species-specific spatial footprints reassemble niche partitioning across disjoint individual sets in a rodent guild**

Short alternative:

**Community spatial segregation is rebuilt by species-specific multi-night footprints**

## One question

> **At what temporal and organizational scale is spatial niche partitioning encoded, and does that spatial structure survive replacement of the individuals that express it?**

The paper is biological. Temporal aggregation and observation-process issues are supporting design considerations, not the subject.

## Central answer

**Terminology boundary.** Here, identity turnover means analytical exclusion of all marked individuals shared between compared windows. The remaining observed identity sets are disjoint; this does not establish literal demographic replacement, mortality or recruitment in the underlying population.

The San Jacinto segregation pattern is not detectable as a rule acting at every within-night movement step and is lost when each individual is reduced to one seasonal point. It is retained by recurring multi-location use across nights, is shared preferentially among conspecific individuals, persists through a season, survives complete replacement of individuals within strongly segregated regimes, and is reassembled across adjacent seasons by disjoint sets of individuals.

The strongest current statement is:

> **Fine-scale niche partitioning is expressed as a recurrent species-level spatial template built from multi-night space-use footprints. Individual site fidelity amplifies that template, but the template can be reassembled by different individuals across time.**

Do not call the template cognitive “memory”.

---

## Competing biological hypotheses and sequential tests

### H1 — segregation is maintained move by move

If competitors continually maintain spatial partitioning by short-term directional avoidance, then for an observed movement of fixed origin and fixed length, the realized direction should preserve more community segregation than feasible alternative directions.

**Result: rejected.**

- 18 informative grid-seasons
- 1,968 repeat-capture nights
- 71.9% of moves had more than one feasible direction
- global standardized C-score excess: **T = -0.197**
- one-sided Monte Carlo **p = 0.800**

Thus the community checkerboard is not continually reconstructed by the direction of each observed within-night move.

### H2 — segregation resides in point-like seasonal centres

If species differ mainly in where individuals place stable point centres, one seasonal point per individual should retain species-associated spatial segregation.

**Result: rejected under the frozen anchor-label null.**

- 1,334 seasonal anchors
- 30 informative public-data grid-seasons
- **T = -0.012**
- **p = 0.532**

This does not prove that home-range centres do not exist. It shows that one point per individual is not the representation carrying the detected community segregation.

### H3 — segregation resides in recurring multi-night footprints

Using the same fixed-fixed SIM9 null family as the published co-occurrence analysis, reduce the data sequentially:

- ALL captures
- one NIGHT-FIRST location per individual-night
- one seasonal ANCHOR per individual

The exact 32-unit publication reconstruction is formally stopped because the deposited file contains only two focal species in grid 3 winter and grid 7 winter, whereas the paper states 3–6 species per matrix. A separately frozen public-data universe contains the 30 supported grid-seasons.

**Result: supported.**

Public-data ALL reference:
- **8 segregated**
- **0 aggregated**
- 22 null

NIGHT-FIRST:
- retains **7/8 = 87.5%** of the fixed ALL segregation signals
- creates no new significant unit
- ALL vs NIGHT-FIRST SES **r = 0.947**

ANCHOR:
- retains **0/8**
- creates no new significant unit
- ALL vs ANCHOR SES **r = 0.109**

Frozen classification: **between-night footprint**.

### H4 — individual footprints themselves carry species identity

For individuals observed on at least two nights, define the footprint as the set of distinct NIGHT-FIRST traps. Compare conspecific and heterospecific Jaccard similarity while permuting species labels only within exact footprint-size strata.

**Result: supported.**

- 928 multi-night individuals before unit filtering
- 22/22 eligible units informative
- 20/22 raw conspecific-minus-heterospecific contrasts positive
- mean conspecific Jaccard = **0.05760**
- mean heterospecific Jaccard = **0.03446**
- standardized assortativity **T = 2.315**
- **p = 0.00010**
- unit assortativity vs NIGHT-FIRST community SES **r = 0.694**

Thus the community result is not only a matrix property: equally broad conspecific footprints occupy more similar spatial domains.

### H5 — the multi-night footprint is temporally persistent

Split each of the eight fixed segregation-reference grid-seasons into EARLY and LATE halves and test matched species × trap reuse against a LATE fixed-fixed null.

**Result: supported.**

- informative: **8/8**
- positive: **8/8**
- **T = 4.091**
- **p = 0.00020**

The multi-night representation does not work merely because it contains more locations: species identity at traps recurs through the season beyond occupancy margins.

### H6 — persistence is more than site fidelity of the same individuals

Remove every species × individual identity observed in both seasonal halves from both halves, then repeat the matched species × trap recurrence test.

**Result: supported in the fixed segregated reference regimes.**

- 188 bridge individuals removed
- informative: **8/8**
- positive: **7/8**
- **T = 1.037**
- **p = 0.00160**

The marked attenuation from Stage 5 (4.091 -> 1.037) is biologically useful: individual site fidelity is an amplifier, but not the whole source of spatial recurrence.

A post-result broader audit yielded 13/18 positive grid-seasons and global p = 0.00080, but the six-grid sign-flip test failed (**p = 0.125**). Therefore do not claim that this within-season turnover result generalizes uniformly across the whole assemblage.

### H7 — the species template is reassembled across seasons by different individuals

For adjacent seasons within a grid, remove from both seasons every individual appearing in both. Before opening spatial outcomes, require each eligible species to retain at least two season-exclusive individuals in each season and each unit to retain at least three species.

This froze **10 adjacent-season units across 6 physical grids**.

Use matched species × trap recurrence; hold season A fixed and randomize season B under the same fixed-fixed curveball logic.

**Result: supported.**

- informative units: **10/10**
- positive units: **9/10**
- global mean standardized recurrence: **Z = 1.775**
- joint Monte Carlo **p = 0.00010**

Independent-grid robustness:
- positive grid means: **5/6**
- grid means: 1 = 1.572, 2 = 2.868, 4 = 3.500, 5 = -0.464, 6 = 2.245, 7 = 0.393
- exact six-grid sign-flip **p = 0.046875**

Frozen decision:

`support_cross_season_species_template_reassembly`.

This is the strongest ecological result in the branch.

---

## Biological hierarchy

The evidence locates community spatial information at an intermediate scale:

[
	ext{movement step}
;<;
mathbf{multi	ext{-}night spatial footprint}
;<;
	ext{seasonal community pattern}.
]

The middle scale has two components:

[
	ext{species-level spatial template}
;+;
	ext{individual site-fidelity amplification}.
]

A single point summary destroys the relevant spatial topology, while moment-to-moment movement direction is too fine a scale to explain it.

The cross-season result adds a second hierarchy:

[
	ext{individual identity}
;<;
mathbf{species	ext{-}level spatial template}
;<;
	ext{community segregation}.
]

The template can be expressed by different individuals in adjacent seasons.

---

## General principle and novelty boundary

Do **not** sell any of the following as new:

- animals show site fidelity;
- movement affects coexistence;
- spatial niche partitioning occurs in rodents;
- individuals differ in their spatial niches;
- habitat and memory can both structure animal space use;
- population-level spatial fidelity or repeated community assembly exists.

Those ideas are established.

The distinctive contribution is the **within-system scale-falsification sequence** applied to one already-documented community pattern:

> **The same community segregation signal is absent from short-term movement direction, lost under point compression, recovered by multi-night footprints, shared among conspecific individuals, persistent through time, and reassembled after replacement of the individuals that carried it.**

The resulting general proposition is narrower and stronger than “scale matters”:

> **Community spatial structure can be encoded in a distributed species-level pattern of repeated space use that is neither reducible to instantaneous movement rules nor to fixed individual centres, and that can be rebuilt by non-overlapping sets of observed individuals.**

This is an empirical localization of where ecological information resides.

---

## Relation to nearest literature

The Introduction and Discussion should explicitly bound the claim against:

- **Chock, Shier & Grether (2018)** — direct interspecific dominance and heterospecific avoidance in this system.
- **Chock, Shier & Grether (2022)** — original temporal overlap, spatial segregation and species-specific resource-selection result.
- **Schirmer et al. (2019)** — personality-dependent movement, microhabitat use and individual spatial niche specialization in rodents.
- **Schirmer et al. (2020)** — individual spatial niches affect within- and between-species spatial interactions.
- **Schlägel et al. (2020)** — movement-mediated community assembly and coexistence across scales.
- **Stiegler et al. (2026)** — behavioural type and niche width structure spatial interactions in a multi-species rodent community.
- **Verzuh et al. (2025)** — habitat and previous use can be comparable drivers of animal space use.

These studies make individual spatial specialization, movement-mediated coexistence and spatial fidelity insufficient novelty claims. None substitutes for the present sequential localization and complete-individual-turnover reassembly test.

---

## Why the result is surprising

The same system already has experimental evidence of a dominance hierarchy and heterospecific avoidance. That makes a step-level avoidance mechanism an obvious expectation.

It fails.

A second intuitive explanation is stable species-specific individual centres.

That also fails under the frozen point-anchor test.

Yet the known community segregation almost completely survives when later within-night captures are removed and only repeated NIGHT-FIRST locations across nights remain.

Most importantly, after the individuals common to two time periods are removed, species-specific trap use still recurs. Across adjacent seasons, the signal survives with entirely disjoint individual identities and passes a six-grid exact sign-flip criterion.

The surprising statement is therefore not “rodents return to places.” It is:

> **The spatial pattern belongs partly to the species-by-place relationship, not only to the trajectories or centres of the particular individuals observed at a given time.**

---

## Mechanism boundary

The public capture data identify the scale and persistence of the pattern, not its causal substrate.

Still viable:

- measured microhabitat structure;
- resource distribution;
- burrow/refuge placement;
- long-term competitive sorting;
- territorial or social constraints;
- repeated foraging-route geometry;
- other persistent grid-scale environmental structure.

The original paper measured trap-level vegetation and soil properties, but those raw variables are not deposited with the public capture dataset.

Therefore:

> **species-level spatial template** is supported;

> **habitat filtering causes the template** is not yet supported by the available public files.

Do not substitute hand-built habitat proxies.

---

## Public-data discrepancy

The deposited public file supports only two focal species in grid 3 winter and grid 7 winter, in tension with the published statement that all 32 spatial matrices contained 3–6 species.

Therefore:

- never claim exact 32-unit reproduction;
- retain the failed Stage-3 gate in Methods/Supplement;
- use the separately frozen 30-unit public-data universe for the temporal-scale decomposition;
- state that the 30-unit reconstruction nevertheless recovers eight segregated and zero aggregated units.

This transparency is a strength, not something to hide.

---

## Figure architecture

### Figure 1 — Where can community segregation reside?

Conceptual hierarchy plus data reduction:

ALL -> NIGHT-FIRST -> multi-night footprint -> one-point anchor.

Overlay the competing hypotheses:
- movement direction
- point centre
- distributed multi-night footprint
- supra-individual species template

### Figure 2 — Two intuitive mechanisms fail

A. Distance-matched movement-direction null: **T = -0.197, p = 0.800**.  
B. Seasonal one-point anchor: **T = -0.012, p = 0.532**.

The point is falsification, not absence of all movement/centre biology.

### Figure 3 — Community segregation localizes to the between-night footprint

Paired SIM9 SES for the eight fixed reference units under:
- ALL
- NIGHT-FIRST
- ANCHOR

Annotate:
- NIGHT-FIRST 7/8
- ANCHOR 0/8
- ALL vs NIGHT-FIRST r = 0.947

### Figure 4 — Different conspecifics share the same spatial domain

Individual-footprint Jaccard:
- conspecific
- heterospecific

Show unit-level standardized effects and exact footprint-size-stratified null.

### Figure 5 — Persistence weakens but survives removal of all shared individuals

For the eight reference units:
- Stage-5 EARLY/LATE persistence Z
- Stage-7 post-turnover Z

Annotate 188 shared individuals removed and the attenuation 4.091 -> 1.037.

### Figure 6 — Different individuals rebuild the species template across seasons

Ten fixed adjacent-season units grouped by six physical grids.

Show unit Z, grid means, and:
- 9/10 positive
- global p = 0.00010
- 5/6 grid means positive
- exact grid sign-flip p = 0.046875

This is the biological climax.

If six figures are too many, merge Figures 5 and 6 into a two-panel “persistence beyond individual identity” figure.

---

## Abstract skeleton

**Background.** Spatial niche partitioning is commonly inferred from accumulated locations, but the community pattern could arise from short-term avoidance, stable placement of individuals, or repeated use of distributed spatial domains.

**Approach.** We decomposed a previously documented spatial-segregation pattern in a six-species granivorous rodent guild across nested temporal and organizational scales, using predeclared null models and explicit tests with all shared marked individuals removed between time windows.

**Results.** Within-night movement direction did not preserve more segregation than distance-matched alternative directions, and reducing each individual to one seasonal point produced no detectable species-associated segregation. In contrast, one location per individual-night retained 7/8 reference community-segregation signals. Conspecific multi-night footprints were more similar than equally broad heterospecific footprints (T = 2.315, p = 0.00010), and species-specific trap use persisted from early to late season (T = 4.091, p = 0.00020). Persistence remained after removing all individuals shared between seasonal halves (T = 1.037, p = 0.00160). Across adjacent seasons, after removing all individuals shared between seasons and requiring at least two exclusive individuals per species in each season, species-specific trap recurrence remained positive in 9/10 tests (global Z = 1.775, p = 0.00010) and in 5/6 physical grids (exact sign-flip p = 0.046875).

**Conclusion.** Fine-scale niche partitioning was encoded in recurrent species-specific multi-night footprints rather than in individual movement steps or point-like centres. Individual fidelity amplified the pattern, but different individuals rebuilt the same species-associated spatial template across time.

---

## Journal assessment after Stage 9

### Journal of Animal Ecology — strongest current target

The paper now directly links individual space use to a multi-species community pattern and separates individual fidelity from a species-level template using complete-turnover tests. This is tightly aligned with current JAE work on rodent space use, individual niches and spatial interactions.

### Ecology — plausible high target

The cross-season reassembly result broadens the manuscript beyond movement ecology into community organization and species sorting at fine spatial scales. The single-system reanalysis and unresolved causal substrate remain the main limitations.

### Oikos — strong alternative

Good fit if framed as niche partitioning, species sorting and recurrent spatial structure.

### Movement Ecology — safe alternative

Strong fit for the temporal/organizational scale decomposition, but the paper should not be reduced to a movement-methods story.

### Ecology Letters — reach, not default

Stage 9 makes the conceptual argument substantially stronger, but one community plus missing direct habitat/mechanism covariates still leaves a generality gap. An independent community or recovery of the original trap-level environmental data would materially change this assessment.

---

## Stop rule

The public San Jacinto capture dataset is now **exhausted for the main ecological claim**.

Do not open Stage 10 from the same file to search for:

- favourable species pairs;
- alternative overlap statistics;
- alternative anchors;
- alternative turnover definitions;
- non-adjacent seasons;
- weaker support thresholds;
- lower-tail reinterpretations;
- or synthetic habitat proxies.

Next work is:

1. manuscript construction;
2. figure construction;
3. external validation in an independent system; or
4. recovery of the original trap-level environmental covariates.

The scientific core should now be treated as frozen.
