# San Jacinto spatial-template novelty audit v1

**Status:** literature-bounded positioning after frozen Stage 9  
**Branch:** `ecology/san-jacinto-transition-niche-v1`  
**Head at audit:** `8c5ac78f486ddc1d512fd24605913ba568ad7634`

## Bottom line

The ecology branch now supports a standalone biological paper, but its novelty is **not** that animals have spatial niches, that movement affects coexistence, that site fidelity exists, or that aggregate spatial patterns can persist through time.

The strongest defensible novelty is:

> **A multispecies spatial-partitioning pattern recurs across disjoint sets of observed individuals: the same species × place association remains after all marked individuals shared between time windows are removed, even though short-term movement direction does not maintain the pattern and one point-like individual centre is insufficient to recover it.**

This is an empirical **identity-turnover decomposition of spatial niche partitioning**.

The result links three levels that are usually studied separately:

1. short-term movement decisions;
2. individual multi-night space-use footprints;
3. community-level species × place structure.

The key evidence is that information is weak or absent at level 1, strong at level 2, and persists at level 3 even after identity turnover.

## Terminology boundary

The Stage 7 and Stage 9 designs create **disjoint observed identity sets** by removing every marked individual seen in both compared windows. They do not demonstrate literal demographic replacement, mortality, recruitment or complete population turnover, because individuals not captured in one window may still have been present. The preferred terms are therefore **identity-independent recurrence**, **disjoint individual sets**, and **reassembly after shared-identity exclusion**. “Replacement individuals” should be avoided unless explicitly defined as this analytical contrast.

## What is already established

### 1. Spatial niche partitioning in mobile animals is not new

The parent San Jacinto study already demonstrated temporal overlap, spatial segregation and species-specific resource selection in the six-species granivorous rodent guild.

- Chock, Shier & Grether 2022. *Oecologia* 198:553–565. doi:10.1007/s00442-021-05104-5.

The present paper cannot claim discovery of spatial niche partitioning in this community.

### 2. Movement can scale up to community assembly and coexistence

Movement ecology already explicitly asks how individual movement processes scale to community-level patterns, including niche partitioning and coexistence.

- Schlägel et al. 2020. *Biological Reviews* 95:1073–1096. doi:10.1111/brv.12600.
- Péron 2024. *Ecological Modelling* 487:110549. doi:10.1016/j.ecolmodel.2023.110549.

Therefore “movement matters for coexistence” is too generic to be novel.

### 3. Individual spatial niche specialization is established, including in rodents

Rodent telemetry and capture–recapture work has shown that individuals within species occupy differentiated spatial niches and that behavioural phenotype can structure within- and between-species spatial interactions.

- Schirmer et al. 2019. *Oecologia* 189:647–660. doi:10.1007/s00442-019-04365-5.
- Schirmer et al. 2020. *Proceedings B* 287:20192211. doi:10.1098/rspb.2019.2211.
- Stiegler et al. 2026. *Journal of Animal Ecology*. doi:10.1111/1365-2656.70320.

Thus conspecific footprint similarity by itself is not a sufficient novelty claim.

### 4. Population spatial niches can remain stable while individual specialization changes

Seasonal work in bats has explicitly shown a stable population spatial-niche breadth despite changes in individual spatial specialization.

- Li et al. 2023. *Movement Ecology* 11, doi:10.1186/s40462-023-00394-1.

Therefore “population-level spatial stability despite individual dynamics” is also not new in the broad sense.

### 5. Persistence of higher-order structure despite membership turnover is known outside spatial niche partitioning

Animal social-network theory treats persistence of group/network structure under demographic turnover as a major problem. Recent empirical work on sparrow social communities reports persistent communities despite dynamic membership and eventual complete member turnover.

- Shizuka & Johnson 2020. *Behavioral Ecology* 31:1–11, “How demographic processes shape animal social networks”.
- Madsen et al. 2025 preprint, doi:10.1101/2025.07.25.666472, “Dynamic membership drives long-term persistence of sparrow winter social communities”.

Likewise, collective or population-level site fidelity has been studied in several animal systems, and colony distributions can be recurrent even when individual-level processes are more dynamic.

Consequently the manuscript should not claim that persistence above individual identity is unprecedented as a general systems phenomenon.

## Parent-study resource-selection boundary

Chock et al. (2022) already established species-specific selection on vegetation and soil axes. Their resource-selection analysis used all captures including recaptures, included individual ID and grid as random effects, and was restricted to **May–July 2016**. Therefore the present paper must not claim that species-specific habitat use, or similarity of place use among conspecifics, is newly discovered.

The new question is at a different level: whether the independently documented **community-level species × trap segregation pattern** can be localized to a temporal representation and whether species × place recurrence remains after every marked identity shared between compared windows is excluded. The adjacent-season analysis also extends beyond the summer-only resource-selection window.

Persistent habitat filtering is consequently a strong candidate explanation for the identity-independent recurrence, not a novelty claim. Because the trap-level vegetation and soil values are not deposited with the public capture file, that mechanism cannot be closed here.

Population-level site fidelity is likewise established and can be estimated directly from capture–recapture data (Tschopp et al. 2018, *PeerJ* 6:e4782, doi:10.7717/peerj.4782). The distinctive contrast here is species × place recurrence among disjoint observed identity sets, not population return to a location.

## What appears distinctive in the present study

The literature search did not identify a close prior animal-community study that performs the full combination below:

1. starts from an independently documented **multispecies spatial niche-partitioning pattern**;
2. tests and rejects a **short-term directional-movement maintenance** explanation;
3. shows that a **one-point individual seasonal summary** is insufficient;
4. localizes the signal to **multi-night individual spatial footprints**;
5. shows **conspecific footprint assortativity** after exact control for footprint breadth;
6. tests recurrence across time while preserving later-period species occupancy and local species richness;
7. removes **all individuals shared between time windows** before measuring spatial recurrence;
8. repeats the identity-removal logic across **adjacent seasons**, showing reassembly by disjoint individual sets;
9. retains a physical-grid-level replication criterion rather than treating seasons as independent replicates.

That combination is the main novelty.

The safest wording is therefore not “first demonstration of spatial-template persistence”, which would be difficult to establish exhaustively. It is:

> **We explicitly separate persistence of spatial niche structure from persistence of the individuals that generated it.**

and, for the result:

> **Species-specific fine-scale spatial structure can be reassembled across disjoint observed individual sets between seasons.**

## Evidence hierarchy

### Stage 1 — short-term directional avoidance is not the carrier

- 18 informative grid-seasons;
- 1,968 repeat nights;
- 71.9% of repeat nights had more than one feasible direction under the exact-distance null;
- global standardized C-score excess = **-0.1966**;
- one-sided Monte Carlo **p = 0.8000**.

Observed within-night movement direction did not preferentially maintain community segregation.

### Stage 4 — the signal resides in multi-night footprints

On the separately frozen 30-unit public-data universe:

- ALL-capture fixed-fixed result: **8 segregated, 0 aggregated**;
- NIGHT-FIRST retained **7/8 = 87.5%** of those segregated units;
- one-point ANCHOR retained **0/8**;
- ALL vs NIGHT-FIRST SES correlation = **0.9474**;
- ALL vs ANCHOR SES correlation = **0.1088**.

Frozen classification: **between-night footprint**.

### Stage 5A — species × trap structure is temporally persistent

Across the eight fixed segregation-reference units:

- **8/8** informative;
- **8/8** positive;
- global mean standardized persistence = **4.0909**;
- one-sided Monte Carlo **p = 0.00019996**.

This rules out the simple explanation that NIGHT-FIRST succeeds only because it has more spatial observations.

### Stage 5B — individual footprints are species-assortative

- 928 multi-night individuals;
- 22 informative grid-seasons;
- global standardized conspecific footprint assortativity = **2.3149**;
- one-sided Monte Carlo **p = 0.00009999**;
- 20/22 units positive.

The label null preserves each individual footprint exactly and permutes species only within exact footprint-size strata.

### Stage 7 — within-season recurrence survives complete identity turnover

After removing **188** individuals appearing in both EARLY and LATE from both halves:

- 8/8 reference units informative;
- 7/8 positive;
- global standardized turnover persistence = **1.0374**;
- one-sided Monte Carlo **p = 0.00160**.

The attenuation from Stage 5A (4.09 -> 1.04) is itself biologically useful: individual fidelity amplifies the spatial pattern, but does not fully create it.

### Stage 9 — cross-season reassembly across disjoint observed individual sets

For adjacent seasons, every individual appearing in both seasons was removed from both matrices before spatial recurrence was measured.

- **290** bridge individuals removed across candidate season pairs;
- frozen eligible units: **10** across **6 physical grids**;
- 10/10 informative;
- 9/10 positive;
- global mean standardized recurrence = **1.7747**;
- one-sided joint Monte Carlo **p = 0.00009999**;
- physical-grid means positive in **5/6** grids;
- exact six-grid sign-flip **p = 0.046875**.

This is the strongest result because neither short-term behavioural continuity nor persistence of the same marked individuals can explain the recurrence.

## General principle

The broad principle is best stated as:

> **Ecological spatial structure can persist above individual identity.**

For this system, the more specific version is:

> **A spatial niche can be a species-level recurrent relationship with place rather than a fixed property of particular individuals.**

The important distinction is between two superficially similar forms of stability:

- **identity-carried stability:** the same individuals repeatedly use the same places;
- **template-reassembled stability:** non-overlapping sets of observed individuals of the same species reconstruct a similar species × place pattern.

The data support both layers, but Stage 7 and Stage 9 show that the second remains after removing the first.

This can be described as **turnover-resilient spatial niche structure** or **identity-independent spatial reassembly**. “Collective memory” should be avoided because the causal mechanism could be habitat filtering and need not involve information transfer or cognition.

## Why the result is surprising

A static species × trap checkerboard can easily be interpreted as the accumulated consequence of site-faithful individuals.

That explanation predicts that removing all individuals shared between time windows should largely destroy species-specific spatial recurrence.

It does not.

At the same time, the opposite simple explanation—continual directional avoidance by moving animals—is also unsupported.

The resulting pattern is therefore counterintuitive:

> **The community-level map is more persistent than either the identity of the animals occupying it or their moment-to-moment movement direction.**

That is the conceptual hook.

## Cross-scale coherence

The individual-footprint and community-segregation effects covary across the 22 matched grid-seasons (descriptive (r=0.694)). After averaging within physical grids, the association is much stronger ((r=0.923)); an exact permutation audit gives (p=0.000992).

Within-grid seasonal covariance is weak ((r=0.271, p=0.207)).

This pattern suggests that a **persistent grid-scale context** is more plausible than a rapidly changing season-specific mechanism. Candidate substrates include habitat structure, refuge/burrow distribution, resource geography, competitor assemblage and other local spatial constraints.

This is mechanistic guidance, not causal identification.

## Scope limits

### Stage 8 limits broad generalization

The complete-turnover effect was positive in 13/18 broader supported grid-seasons and had a significant unit-level global test, but the six-grid robustness test failed:

- 5/6 grid means positive;
- exact sign-flip **p = 0.125**.

Therefore do **not** claim that complete-turnover recurrence is established throughout the whole guild or all grids.

The strongest inference is for the frozen strongly segregated regimes plus the independently frozen adjacent-season Stage-9 test.

### Public-source discrepancy

The public Figshare file contains only two focal species in grid 3 winter and grid 7 winter, whereas the published Methods state 3–6 species in all 32 matrices.

Accordingly:

- exact 32-unit reproduction remains source-limited;
- the scale-decomposition analysis uses a separately frozen 30-unit public-data universe;
- no missing species or unpublished inclusion rule is invented.

### Capture-based footprint

NIGHT-FIRST removes later same-night recaptures, but it is still capture–recapture data rather than continuous telemetry. The object should be called a **capture-based multi-night spatial footprint**, not a complete natural movement path or exact home range.

### Mechanism remains open

The data do not identify why different conspecifics rebuild the same spatial pattern. Plausible alternatives include:

- persistent microhabitat selection;
- burrow/refuge distributions;
- resource geography;
- territorial/social constraints;
- longer-term competitive sorting;
- species-specific physiological constraints.

The original study's resource-selection results make persistent habitat structure particularly plausible, but the deposited Figshare record lacks the trap-level vegetation and soil data needed to test that mechanism directly.

## Novelty and impact assessment

### Novelty: **high, but combination-level rather than theorem-level**

The individual ingredients are established. The novel contribution is the **identity-turnover decomposition of an observed multispecies spatial niche pattern**.

A defensible novelty sentence is:

> **Previous work has described individual spatial specialization and population-level spatial stability; here we ask whether a community spatial niche pattern survives replacement of the individuals that generated it, and show that it does.**

### Importance: **high**

The result changes how static niche-partitioning maps should be interpreted.

A spatially stable community pattern need not mean:

- the same individuals stay in the same places; or
- individuals continually enforce the pattern through directional avoidance.

Instead it can reflect a repeatable species–environment/community mapping that recruits new individuals into similar spatial roles.

This distinction matters for:

- coexistence inference;
- habitat restoration;
- reintroduction/translocation;
- predicting community resilience after demographic turnover.

For conservation, protecting only currently occupied individual sites is not necessarily equivalent to protecting the environmental template that repeatedly regenerates species-specific space use.

### Generality: **conceptually high, empirically moderate**

The principle can apply broadly to mobile communities, but the current empirical test is one rodent guild and a small number of independent grids.

Stage 9's grid-level pass is encouraging, but a second system would materially strengthen generality.

### Causal closure: **moderate-to-low**

The study localizes the level at which structure lives but does not identify the physical/biotic mechanism that rebuilds it.

This is the largest remaining scientific limitation.

## Journal positioning

### Journal of Animal Ecology — strong fit

The paper directly links individual movement/space use to species interactions and community structure, with marked individuals and explicit turnover tests. The 2026 JAE rodent-community paper on behavioural type and spatial interactions confirms active interest in this interface.

Current evidence is strong enough to justify a serious JAE submission if written as an ecology paper rather than a methodological decomposition.

### Ecology — strong fit

The general ecological message—community spatial structure persists beyond individual identity—is broad, and the sequential falsification of simpler scales gives the paper a strong process-to-pattern structure.

### Oikos — very strong / safer fit

Good fit for niche partitioning and coexistence framing, but likely undersells the strongest current result if the manuscript is polished well.

### Ecology Letters — plausible stretch, not yet the default

The conceptual hook is EL-like: higher-order ecological structure can survive turnover of its constituent individuals.

What currently holds it below a confident EL recommendation:

1. one study system;
2. public-source discrepancy in 2/32 original grid-seasons;
3. capture-based rather than continuous trajectories;
4. causal substrate of reassembly unresolved;
5. Stage 8 broader grid-level generalization did not pass.

A second independent community or direct habitat-mechanism closure could upgrade this substantially.

### Nature Ecology & Evolution / Nature — not supported by present evidence

The principle is interesting, but one reanalysis of one guild without causal closure or cross-system replication is not enough for those venues.

## Recommended manuscript question

Do **not** make the question “what temporal scale matters?”

Use one biological question:

> **Does spatial niche partitioning recur when the same marked individuals are excluded from successive time windows?**

The answer is:

> **Yes. Individual fidelity amplifies the pattern, but non-overlapping conspecific sets reassemble species-specific spatial use within and across seasons.**

The short-term movement and point-anchor results become falsified alternative mechanisms, not the topic of the paper.

## Candidate title

**Spatial niche partitioning recurs across disjoint individual sets in a rodent guild**

Alternatives:

- **Species-level spatial niches persist beyond individual identity**
- **Disjoint individual sets rebuild spatial niche partitioning across seasons**
- **A community spatial template persists beyond the individuals that occupy it**

The first is the safest combination of biological specificity and conceptual reach.

## Recommended four-figure story

### Figure 1 — The puzzle

Show the known community-level spatial segregation together with the new observation that individuals change trap locations within nights.

Question: what carries a stable spatial niche pattern in a mobile guild?

### Figure 2 — Locate the information scale

Contrast:

- within-night direction: unsupported;
- one-point seasonal anchor: insufficient;
- multi-night NIGHT-FIRST footprint: retains 7/8 segregation signals.

This is a compact falsification figure, not a methods figure.

### Figure 3 — Footprints are species-specific and persistent

Combine:

- conspecific vs heterospecific individual-footprint similarity;
- EARLY vs LATE species × trap recurrence;
- reference/non-reference context.

This establishes the spatial template before identity removal.

### Figure 4 — Replace the animals

Main climax:

- within-season removal of all bridge individuals: 7/8 positive, (p=0.0016);
- cross-season disjoint individuals: 9/10 positive, (p<10^{-4});
- six grid means and exact sign-flip (p=0.046875).

The visual message should be “same spatial template, different animals.”

## Stopping rule

No further post-result search over:

- species pairs;
- alternative overlap metrics;
- weaker individual thresholds;
- non-adjacent seasons;
- alternative anchor definitions;
- or additional movement-distance summaries

is justified with the current public data.

The next scientifically valuable addition is **independent evidence**, not another endpoint from the same dataset.
