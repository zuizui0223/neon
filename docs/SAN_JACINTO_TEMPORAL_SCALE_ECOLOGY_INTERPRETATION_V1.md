# San Jacinto temporal-scale ecology interpretation v1

**Status:** Stage 4 primary classification complete  
**Branch:** `ecology/san-jacinto-transition-niche-v1`  
**Primary result:** `results/san_jacinto_public_data_scale_decomposition_v1.json`  
**Frozen design:** `docs/SAN_JACINTO_TRANSITION_NICHE_EXPLORATION_V1.md`

## One-sentence result

> **The published spatial segregation signal is carried by repeated multi-night space-use footprints, not by directional avoidance within nights and not by one point-like seasonal location per individual.**

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

> **A community pattern can reside in the spatial footprint of repeated behavior even when it is absent from both moment-to-moment directional decisions and point summaries of individuals.**

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
- it gives a falsifiable temporal-scale mechanism statement;
- it is not yet a causal coexistence mechanism because habitat and competition are not separated;
- it is strongest as a reanalysis showing that a known spatial partitioning pattern is encoded in repeated multi-night use rather than within-night direction or point centres.

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
