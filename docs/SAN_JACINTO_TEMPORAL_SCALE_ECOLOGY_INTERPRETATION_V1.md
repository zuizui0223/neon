# San Jacinto temporal-scale ecology interpretation v1

**Status:** Stage 5A/5B ecological localization complete  
**Branch:** `ecology/san-jacinto-transition-niche-v1`  
**Primary results:** `results/san_jacinto_public_data_scale_decomposition_v1.json`; `results/san_jacinto_stage5_temporal_persistence_v1.json`; `results/san_jacinto_individual_footprint_assortativity_v1.json`  
**Frozen design:** `docs/SAN_JACINTO_TRANSITION_NICHE_EXPLORATION_V1.md`

## One-sentence result

> **The published spatial segregation signal is carried by persistent species-specific multi-night space-use footprints, not by directional avoidance within nights and not by one point-like seasonal location per individual.**

This is a temporal-scale localization result.

## Evidence chain

The analysis deliberately asked three different ecological questions in sequence and stopped failed routes rather than searching for a positive metric.

### 1. Within-night direction did not maintain segregation

Stage 1 held each repeat-capture night's FIRST location and exact FIRST-to-LAST movement length fixed, randomized only feasible movement direction, and asked whether observed directions preserved greater community C-score than random directions.

Support was ample (1,968 randomized repeat nights; 18 informative grid-seasons), but the global effect was negative:

- standardized excess: **-0.1966**
- one-sided Monte Carlo **p = 0.8000**
- decision: `stop_no_directional_maintenance_support`

Thus there is no community-level evidence that each short-term move is directionally chosen to maintain the seasonal checkerboard pattern.

### 2. A single seasonal point per individual did not encode segregation

Stage 2 reduced each individual to one seasonal medoid of its nightly-FIRST trap locations and tested species-specific placement with a fixed-location species-label permutation.

- 1,334 individual anchors
- 30 informative grid-seasons
- global statistic: **-0.0120**
- one-sided Monte Carlo **p = 0.5315**
- decision: `stop_no_species_specific_seasonal_anchoring_support`

This particular point-anchor hypothesis was not supported.

Because Stage 2 uses a different null hypothesis from the published fixed-fixed co-occurrence analysis, it is not a replication test of the original C-score result.

### 3. The original fixed-fixed signal survives removal of later within-night captures

Stage 4 returned to the **same EcoSimR SIM9 fixed-fixed C-score null** used in the published study and changed only the temporal representation.

The exact 32-unit publication reconstruction remains formally stopped because the deposited Figshare file contains only two focal species in grid 3 winter and grid 7 winter, contrary to the published statement that each of 32 matrices contained 3–6 species.

The separately frozen public-data universe therefore contains the 30 grid-seasons supported by the deposited data.

On those 30 units, the ALL-capture reconstruction exactly recovered the published headline count:

- **8 segregated**
- **0 aggregated**
- **22 null**

The eight fixed reference units were:

- grid 1 summer
- grid 4 fall
- grid 4 winter
- grid 4 spring
- grid 4 summer
- grid 6 fall
- grid 6 winter
- grid 6 summer

When every individual-night was reduced to its **earliest capture only**, seven of those eight remained significantly segregated under their own representation-specific SIM9 null:

- retained: grid 4 fall/winter/spring/summer and grid 6 fall/winter/summer
- lost: grid 1 summer
- retention: **7/8 = 87.5%**

No new NIGHT-FIRST units became significant.

When every individual was reduced further to a **single seasonal anchor**, none of the eight remained significantly segregated:

- retention: **0/8**
- no new ANCHOR unit became significant

The prospectively frozen Stage-4 classification is therefore:

> **BETWEEN-NIGHT FOOTPRINT**

## Quantitative coherence

The full pattern across all 30 supported grid-seasons was highly preserved by NIGHT-FIRST but not by ANCHOR:

- ALL vs NIGHT-FIRST SES correlation: **r = 0.9474**
- ALL vs ANCHOR SES correlation: **r = 0.1088**

Mean SES likewise declined across the temporal reductions:

- ALL: **2.073**
- NIGHT-FIRST: **1.413**
- ANCHOR: **-0.103**

The important evidence is not the decline in mean SES by itself, because each representation has different fixed row/column margins. The primary evidence is the pre-declared retention classification under the same fixed-fixed null family.


## Stage-4 unresolved alternative: sampling depth versus temporal persistence

Stage 4 localizes the published signal to a representation that retains multiple NIGHT-FIRST locations across nights and shows that one point per individual is insufficient. By itself, however, this does **not** prove that the repeated-use footprint is temporally persistent. A reviewer could reasonably argue that NIGHT-FIRST succeeds simply because it contains more spatial observations / occupied traps than a one-point representation.

The next ecological test therefore does not search for another segregation metric. It asks whether the species-specific spatial map itself recurs through time: do the same species reuse the same trap locations in the early and late halves of a season more than expected under a fixed-fixed late-season null?

A positive answer would upgrade “multi-night representation carries the signal” to “species-specific multi-night footprints persist through the season.” A null answer would force the weaker, sampling-depth interpretation.


## Stage 5 result — the multi-night footprint is temporally persistent

The frozen persistence test passed all pre-declared criteria.

Primary inference used only the eight Stage-4 reference grid-seasons. EARLY and LATE halves contained equal numbers of calendar sampling nights (discarding one middle night when needed), and the LATE species × trap matrix was randomized with the same fixed-fixed curveball logic while preserving each species' LATE trap occupancy and each trap's LATE species richness.

Results:

- informative reference units: **8/8**;
- positive standardized persistence: **8/8**;
- global mean standardized persistence: **T = 4.0909**;
- one-sided Monte Carlo **p = 0.00019996**.

The observed same-species EARLY→LATE trap overlap exceeded the fixed-fixed expectation in every reference grid-season.

The broader 22-unit support set was descriptive only, but showed the same direction in **20/22** units:

- mean (Z = 2.661);
- median (Z = 2.637);
- reference mean (Z = 4.091);
- non-reference mean (Z = 1.844).

The frozen Stage-5 decision is:

`support_persistent_species_specific_multi_night_footprints`.

This closes the main sampling-depth objection to the Stage-4 interpretation. NIGHT-FIRST does not merely accumulate more spatial points: in the segregated grid-seasons, the **identity of the species using a given trap is reproducible from the early to the late half of the season beyond expectations from species occupancy and trap richness alone**.

The strongest current ecological synthesis is therefore:

> **Community spatial segregation is encoded in persistent species-specific multi-night space-use footprints, not in continual within-night directional avoidance and not in one point-like seasonal location per individual.**

The word “persistent” refers to community-level species × trap reuse across seasonal halves. It does not imply that every individual has a stable telemetry-defined home range.


## Stage 5B — the community signal is also visible among individuals

A separate, independently frozen analysis asked whether the recurring footprint is merely a matrix-level property or whether **different individuals of the same species actually use more similar multi-night footprints than individuals of different species**.

For every individual observed on at least two nights, the footprint was the set of distinct NIGHT-FIRST traps used during a grid-season. The test compared pairwise Jaccard similarity among conspecific versus heterospecific individuals.

Crucially, the null shuffled species labels **only among individuals with exactly the same number of distinct traps in their footprints**. This controls the obvious alternative that the pattern merely reflects species differences in footprint breadth or sampling depth.

Results:

- multi-night individuals before unit filtering: **928**;
- eligible/informative grid-seasons: **22/22**;
- global standardized assortativity: **T = 2.3149**;
- one-sided Monte Carlo **p = 0.00009999**;
- positive raw conspecific-minus-heterospecific difference: **20/22** units;
- mean conspecific Jaccard: **0.05760**;
- mean heterospecific Jaccard: **0.03446**;
- unit-level assortativity (Z) vs Stage-4 NIGHT-FIRST community SES: **r = 0.6943**.

This is an important strengthening of the Stage-4/5A interpretation. The recurring spatial footprint is not only temporally persistent at the aggregated species × trap level; it is **assortative among different individuals of the same species**, even after exact control for footprint size.

Accordingly, the stronger but still defensible synthesis is:

> **Species-specific community segregation emerges from persistent, overlapping domains of repeated space use shared among conspecific individuals, rather than from continual directional avoidance or one static centre per individual.**

This remains an association, not a causal identification of habitat selection or competition.

## Biological interpretation

The result rejects two simple pictures of spatial niche partitioning.

### Not continual step-by-step avoidance

The community is not spatially partitioned simply because every observed within-night movement points away from heterospecific space. Stage 1 found no such directional maintenance.

### Not one static centre per individual

The community pattern is also not recoverable by replacing each individual with one point-like seasonal location. ANCHOR retained 0/8 reference segregation signals.

### Instead: repeated use of a distributed spatial footprint

The segregation signal appears when individuals are allowed to contribute **multiple locations across different nights**, even after every later recapture within each night is removed.

The relevant spatial object is therefore neither an instantaneous movement vector nor a single centre. It is the **set of places repeatedly used across nights**.

A concise ecological statement is:

> **Species partition space through the topology of repeated space use, not through constant directional avoidance or static point centres.**

Here “topology” is used descriptively for which trap locations enter the repeated-use footprint; it does not imply a formal topological model.

A still safer phrasing for a manuscript is:

> **Community-level spatial segregation was preserved by recurring multi-location use across nights, but disappeared when individuals were reduced to one seasonal location.**

## General principle

Hierarchical habitat selection, movement-mediated coexistence, home-range formation and scale-dependent species interactions are established ideas. The new contribution should therefore not be framed as “scale matters” or “movement matters”.

The more distinctive principle suggested by this analysis is:

> **A community pattern can be encoded in persistent, species-specific spatial footprints shared across repeated behavior and across individuals, even when it is absent from moment-to-moment directional decisions and point summaries.**

This identifies a middle organizational scale:

[
	ext{movement step} ;<; mathbf{repeated multi	ext{-}night footprint} ;<; 	ext{seasonal community pattern}.
]

The bolded middle scale is what the present decomposition localizes.

## Why this is surprising

A common mechanistic shortcut is to explain a spatially segregated community in one of two ways:

1. individuals actively avoid competitors during movement; or
2. species occupy different stable centres / preferred locations.

The San Jacinto results support neither simple reduction.

Animals can move substantially within nights without those directions preserving the community checkerboard, and a single seasonal individual location loses the signal entirely. Yet one FIRST location per individual per night is enough to preserve seven of the eight reference segregated grid-seasons.

The ecological organization is therefore distributed across repeated nights.

## Relation to previous work

The result does not overturn the original San Jacinto conclusions. It localizes one component of their spatial pattern in time.

Relevant prior boundaries include:

- Chock, Shier & Grether (2018), *Animal Behaviour* 137:197–204, doi:10.1016/j.anbehav.2018.01.015 — direct evidence for body-size dominance and heterospecific avoidance in this system.
- Chock, Shier & Grether (2022), *Oecologia* 198:553–565, doi:10.1007/s00442-021-05104-5 — temporal overlap, spatial segregation and species-specific resource selection in the six-species guild.
- Schlägel et al. (2020), *Biological Reviews*, doi:10.1111/brv.12600 — movement as a link between individuals and community assembly/coexistence across scales.
- Péron (2024), *Ecological Modelling* 487:110549, doi:10.1016/j.ecolmodel.2023.110549 — small-scale station-keeping movement and coexistence.

Those literatures make a generic “movement-based coexistence” claim insufficiently novel. The present result is narrower: a **within-system temporal decomposition of an already documented community pattern**.

## What the result does not identify

The between-night footprint could arise from several mechanisms that the public data cannot distinguish:

- microhabitat selection;
- burrow / refuge placement;
- resource distributions;
- longer-term competitor avoidance;
- territorial or social structure;
- repeated foraging routes;
- historical sorting of individuals;
- or other persistent spatial constraints.

The publicly deposited Figshare record does not contain the trap-level vegetation/soil measurements used in the original resource-selection models, so a direct habitat-mechanism closure is not possible from the current public files.

## Observation-process boundary

NIGHT-FIRST was chosen specifically because it removes all later within-night capture locations from the representation. This sharply reduces dependence of the retained footprint on same-night post-capture movement.

It does not make the data telemetry trajectories and does not prove absence of capture effects across nights. The correct referent is **capture-based multi-night spatial footprint**, not a complete natural home range.

## Public-data discrepancy

The exact 32-grid-season reproduction must remain labelled as failed.

The deposited capture file supports only two focal species in:

- grid 3 winter;
- grid 7 winter.

The published Methods state 3–6 species per matrix. The public-data support audit found no date-parsing explanation and confirmed PEMA is present in all 32 units.

Stage 4 therefore uses a separately frozen 30-unit public-data universe. The 8/30 ALL result is a reconstruction sanity condition, not a claim that the published denominator was 30.

## Current impact assessment

This result is materially stronger biologically than the temporal-aliasing methods story alone because it says **where the community-level ecological information resides**.

On the current evidence:

- it is more than a generic observation-process result;
- it gives a falsifiable temporal-scale localization and two independent persistence/assortativity tests;
- the individual-footprint result controls exactly for footprint size, substantially weakening a simple sampling-depth explanation;
- it is not yet a causal coexistence mechanism because habitat and competition are not separated;
- it is strongest as a reanalysis showing that a known spatial partitioning pattern is encoded in persistent species-specific multi-night use shared among conspecific individuals rather than within-night direction or point centres.

A high-impact ecology claim would require an independent system or the missing trap-level habitat data to show *why* the multi-night footprints differ among species.

## Claim boundary

Do not claim that:

- competition causes the between-night footprint;
- heterospecific avoidance is absent;
- habitat filtering is proven;
- the NIGHT-FIRST footprint is a full home range;
- Stage 3 reproduced all 32 published matrices;
- the two excluded public-data units are biologically absent from the original unpublished analysis;
- ANCHOR “proves no home-range centres exist”;
- or species-pair post hoc searches identify the driver.

No species-pair decomposition is opened by this result.


---

## Stage 7–8 update: spatial memory survives individual turnover, but broad-grid generalization remains unresolved

A final turnover analysis asked whether the EARLY→LATE species × trap persistence could be explained entirely by the **same individuals** remaining site-faithful through the season.

Before opening spatial overlap, a support-only audit removed every species × individual identity observed in both seasonal halves. Across the eight fixed Stage-4 reference grid-seasons, **188 bridge individuals** were removed. All eight units still retained at least three focal species represented by at least one EARLY-only and one LATE-only individual.

The frozen Stage-7 test then rebuilt the EARLY and LATE species × trap matrices from **mutually disjoint individual sets** and applied the same fixed-fixed LATE null used for temporal persistence.

Results:

- informative reference units: **8/8**;
- positive standardized turnover persistence: **7/8**;
- global mean standardized persistence: **T = 1.0374**;
- one-sided Monte Carlo **p = 0.00160**;
- decision: `support_species_level_spatial_template_beyond_individual_identity`.

The effect was substantially weaker than the original Stage-5 persistence signal (**T = 4.0909**), and individual-unit standardized effects were generally attenuated after bridge removal. The defensible biological interpretation is therefore **layered**, not all-or-none:

> **individual site fidelity strongly amplifies seasonal spatial persistence, but it does not fully create it; a weaker species-associated spatial template remains when the individuals themselves turn over.**

This is the strongest evidence in the current public data that the spatial pattern is not merely an artefact of repeatedly recapturing the same site-faithful animals.

### Broader generalization audit

Because the eight segregation-reference units come from only three physical grids, Stage 8 prospectively extended the identical turnover rule to the previously established 22-unit temporal-persistence universe.

The outcome-blind support audit found 18 eligible grid-seasons spanning six physical grids.

At the grid-season level the broader pattern remained positive:

- informative units: **18/18**;
- positive standardized effects: **13/18**;
- global mean **Z = 0.7522**;
- joint Monte Carlo **p = 0.00080**.

However, the predeclared physical-grid robustness criterion did **not** pass:

- positive grid means: **5/6**;
- grid means: 0.771 (grid 1), 0.611 (grid 2), 1.208 (grid 4), 0.379 (grid 5), 1.158 (grid 6), −1.206 (grid 7);
- exact six-grid sign-flip **p = 0.125**.

The frozen Stage-8 decision is therefore:

`broader_turnover_generalization_not_supported`.

The correct claim is not that a species-level template has been demonstrated generally across the whole assemblage. It is:

> **Within the strongly segregated spatial regimes, species-specific space use persists beyond individual identity; the broader public-data set is suggestive in the same direction but lacks sufficient independent grid-level support for generalization.**

### Revised ecological synthesis

Taken together, the evidence now separates four spatial organizations:

1. **within-night movement direction** — does not maintain the checkerboard pattern;
2. **one point-like seasonal individual centre** — does not retain the pattern;
3. **multi-night individual footprint** — strongly species-assortative and linked to community segregation;
4. **species × trap template across individual turnover** — weaker but still detectable in the fixed segregated reference regimes.

The most defensible current model is therefore:

> **Spatial niche partitioning is a layered spatial regime: persistent environmental or community context generates species-associated recurring-use domains, while individual site fidelity amplifies those domains through repeated use.**

The public data cannot identify what generates the species-associated template. Habitat heterogeneity is an especially plausible candidate because the original study documented species-specific resource selection, but the deposited Figshare record lacks the trap-level vegetation and soil variables required for a direct mechanistic test.

### Literature boundary after the turnover result

Individual spatial memory, site fidelity and emergent space-use patterns are well established, and individual-level memory can itself generate spatial segregation in theoretical and empirical movement systems. Recent work also shows that habitat and memory can have comparable explanatory power for animal space use. The present contribution should therefore **not** be framed as discovering spatial memory.

The narrower contribution is the empirical decomposition:

> **a known community segregation pattern is weak at the movement-step scale, lost under one-point individual summaries, strong in recurring individual footprints, and partly retained after complete individual turnover.**

That turnover contrast distinguishes individual spatial memory from a persistent species-associated spatial template in a way that the generic movement-to-home-range literature does not by itself provide.

Relevant additional boundaries include:

- Aarts et al. (2021), *The American Naturalist* 198, doi:10.1086/715014 — individual-level memory can generate spatial segregation among neighboring central-place foragers.
- Potts & Börger (2023), *Journal of Animal Ecology* — formal scaling from movement decisions to emergent space-use distributions.
- Verzuh et al. (2025), *Ecology Letters*, doi:10.1111/ele.70233 — direct comparison of habitat and memory as drivers of animal space use.

### Final claim boundary for the ecology branch

Do not claim that:

- the residual turnover signal is cognitive or social “memory” of the species;
- habitat filtering has been causally identified;
- competition creates the species-level template;
- individual fidelity is unimportant;
- the turnover result generalizes across all physical grids;
- grid 7 falsifies the mechanism in general;
- or Stage 8 rescues or upgrades the Stage-7 primary inference.

No further alternative movement metric, turnover definition, species-pair decomposition or threshold search is justified with the present public data.
