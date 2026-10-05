# Species-specific spatial footprints reassemble niche partitioning across individual turnover in a rodent guild

**Target:** Journal of Animal Ecology  
**Version:** v0.1 ecological manuscript draft  
**Status:** main public-data analyses frozen through Stage 9  
**Authors:** [to be finalized]

## Abstract

1. Spatial niche partitioning is usually inferred from locations accumulated across days or seasons, but the same community pattern could arise from very different processes. Competitors might avoid one another during individual movements, species might occupy different stable individual centres, or segregation might instead be encoded in distributed patterns of repeated space use that persist above individual identity. Distinguishing these possibilities is necessary to connect movement behaviour to community structure.

2. We decomposed a previously documented spatial-segregation pattern in a six-species granivorous rodent guild in southern California across nested temporal and organizational scales. Using repeated live-trap detections, we tested whether segregation was carried by within-night movement direction, one point-like seasonal location per individual, recurring multi-night individual footprints, within-season species × trap recurrence, or a species-level spatial template persisting after complete individual turnover. Null models were fixed before each newly opened outcome and preserved the spatial margins relevant to the hypothesis being tested.

3. Observed within-night movement directions did not preserve greater community segregation than distance-matched feasible directions (standardized effect (T=-0.197), (p=0.800)), and one seasonal point per individual showed no species-associated segregation ((T=-0.012), (p=0.532)). In contrast, retaining only the earliest capture of each individual on each night preserved 7 of 8 fixed community-segregation signals, whereas one-point seasonal anchors preserved none. Conspecific individuals had more similar multi-night footprints than heterospecific individuals after exact control for footprint size ((T=2.315), (p=0.00010)). Species-specific trap use persisted from early to late season ((T=4.091), (p=0.00020)) and remained detectable after removing every individual shared between seasonal halves ((T=1.037), (p=0.00160)).

4. The strongest test changed both season and individual identity. Across ten prospectively fixed adjacent-season comparisons, after removing all individuals observed in both seasons and requiring at least two season-exclusive individuals per species in each season, species-specific trap recurrence was positive in 9/10 comparisons (global (Z=1.775), (p=0.00010)). Five of six physical-grid means were positive, passing a predeclared exact sign-flip criterion ((p=0.046875)). Thus fine-scale niche partitioning was expressed as a recurrent species-level spatial template built from multi-night footprints. Individual site fidelity amplified the pattern, but different individuals rebuilt the species-associated spatial structure across time.

**Keywords:** community assembly; individual turnover; movement ecology; niche partitioning; rodents; site fidelity; space use; species sorting

---

# Introduction

Spatial niche partitioning is a central route by which ecologically similar species can coexist. Yet the spatial patterns used to diagnose partitioning are usually accumulated over sampling periods much longer than the behavioural events that generate them. A checkerboard pattern across traps, habitat patches or territories can therefore conceal fundamentally different biological organizations. The same static pattern could arise because individuals continually avoid competitors during movement, because species place stable individual activity centres in different parts of the landscape, or because individuals repeatedly use distributed sets of locations whose aggregate geometry differs among species.

This distinction matters because movement ecology and community ecology operate at different organizational scales. Movement-mediated community theory emphasizes that individual decisions can scale into population distributions and community assembly, but the mapping between behavioural decisions and emergent community patterns is not one-to-one (Schlägel et al. 2020). Home-range formation, habitat selection, memory, social interactions and repeated resource use can all transform short-term movement into longer-term spatial structure. Consequently, observing spatial segregation does not by itself identify the temporal scale at which that segregation is organized.

Work on individual spatial niches sharpens the problem. Rodents can show consistent among-individual differences in movement, home-range size, microhabitat use and spatial interactions (Schirmer et al. 2019, 2020), and recent multi-species work shows that behavioural type and niche width can structure spatial encounters within natural rodent communities (Stiegler et al. 2026). More broadly, previous use and habitat can make comparable contributions to animal space use (Verzuh et al. 2025). These studies demonstrate that spatial structure can emerge from persistent individual differences and repeated use. They do not, however, tell us whether a community-level niche-partitioning pattern is stored primarily in the identities and site fidelity of particular individuals or whether a species-associated spatial structure is repeatedly rebuilt when individuals change.

The difference between those alternatives can be framed as a question of where ecological information resides. If community segregation is encoded at the scale of movement decisions, then observed short-term directions should preferentially maintain separation. If it is encoded in point-like individual placement, one representative seasonal centre per individual should retain the signal. If it is encoded in repeated space use, the signal should require the distributed set of locations used across nights. Finally, if that distributed structure belongs only to persistent individuals, it should disappear when the individuals shared across time periods are removed. Persistence after complete turnover would instead imply a species-by-place relationship above the identity of the individuals expressing it.

The granivorous rodent assemblage of the San Jacinto Wildlife Area provides an unusually useful system for this decomposition. Chock, Shier & Grether (2022) studied six sympatric species with extensive dietary overlap: San Diego pocket mice *Chaetodipus fallax*, Dulzura kangaroo rats *Dipodomys simulans*, Los Angeles pocket mice *Perognathus longimembris brevinasus*, Stephens' kangaroo rats *Dipodomys stephensi*, deer mice *Peromyscus maniculatus* and cactus mice *P. eremicus*. The assemblage showed substantial temporal overlap but non-random spatial segregation, together with species-specific resource associations. Independent behavioural experiments in this system also documented a body-size dominance hierarchy and heterospecific avoidance (Chock, Shier & Grether 2018). These observations make continual short-term avoidance an intuitively plausible mechanism, while the repeated live-trap checks provide information below the seasonal scale at which the community pattern was originally summarized.

Here we ask one question: **at what temporal and organizational scale is spatial niche partitioning encoded in this mobile mammal community, and does that spatial structure survive replacement of the individuals that express it?** We test a sequence of increasingly coarse-to-persistent hypotheses. First, we ask whether within-night movement directions preferentially preserve spatial segregation when movement length and origin are held fixed. Second, we test whether one point-like seasonal location per individual is sufficient. Third, we return to the fixed-fixed null model used for the published community analysis and determine whether the segregation signal survives removal of later within-night captures but disappears when multi-night use is collapsed to one point. We then test whether individual multi-night footprints are assortative by species, whether the species × trap pattern recurs within seasons, whether recurrence survives complete individual turnover, and finally whether different individuals reassemble the same species-associated spatial structure across adjacent seasons.

The sequential design is deliberately asymmetric. Failed hypotheses are stopped rather than replaced by searches over alternative endpoints. This allows the final ecological interpretation to rest not only on a positive pattern, but on a hierarchy of rejected and supported mechanisms. We predicted that if spatial niche partitioning is organized as a recurrent species-level spatial template, the community signal would be weak at the scale of individual movement steps and point centres, strong in multi-night footprints, and detectable after removal of the individuals shared across time.

---

# Materials and methods

## Study system and source data

We reanalysed the publicly deposited capture data associated with Chock, Shier & Grether (2022), collected in the San Jacinto Wildlife Area, Riverside County, California, USA, from August 2015 through July 2016. The study sampled eight live-trapping grids. Each grid contained 49 traps in a (7	imes7) arrangement with 6.25-m spacing. Traps were checked repeatedly within nights, and captured animals were individually identified, allowing multiple spatial records for the same individual within a night and repeated records across nights and seasons.

We considered the six focal granivorous species from the original community analysis: *Chaetodipus fallax* (CHFA), *Dipodomys simulans* (DKR), *Perognathus longimembris brevinasus* (LAPM), *Peromyscus eremicus* (PEER), *P. maniculatus* (PEMA) and *Dipodomys stephensi* (SKR). We used the original seasonal definitions: fall, August–October; winter, November–January; spring, February–April; and summer, May–July.

The capture file was obtained from Figshare (doi:10.6084/m9.figshare.18295520.v1), and the analysis pipeline verified the frozen SHA-256 checksum before every data-dependent workflow. The deposited record contains the capture table and a metadata workbook but does not contain the trap-level vegetation and soil variables used in the original resource-selection models.

### Public-data denominator discrepancy

The published Methods describe 32 grid-season spatial matrices with three to six species per matrix. In the deposited capture file, grid 3 winter and grid 7 winter contain only two focal species. All focal date strings were parseable, and *P. maniculatus* was present in all 32 grid-seasons as reported, so the discrepancy could not be attributed to date parsing or wholesale omission of those periods.

We therefore did not claim an exact 32-unit reproduction. A preregistered reproduction gate formally stopped. For temporal scale decomposition, we separately froze the 30 grid-seasons in the public file containing at least three focal species. In those 30 units, the ALL-capture reconstruction recovered eight segregated and zero aggregated units under the same fixed-fixed null family as the published analysis. The two-unit discrepancy is retained as a limitation rather than silently reclassified.

## Common spatial representation

Trap identities were mapped to the (7	imes7) grid. For analyses requiring temporal order, records were grouped by species, grid, individual and calendar date and ordered by recorded trap-check time.

We use **NIGHT-FIRST** to denote the earliest valid trap location for an individual on a calendar night. This representation excludes every later same-night recapture while retaining repeated spatial use across different nights.

The **multi-night footprint** of an individual within a grid-season was the set of distinct NIGHT-FIRST traps used by that individual. The footprint was defined only for individuals observed on at least two nights when analyses explicitly required multi-night individuals.

A **seasonal anchor** was a single observed NIGHT-FIRST trap chosen as the medoid of an individual's seasonal nightly-FIRST locations: the observed trap minimizing summed squared grid distance to all nightly-FIRST locations. Ties were broken by the highest observed nightly-FIRST frequency and then lexicographically. The anchor intentionally compressed a distributed footprint to one point.

## Sequential testing framework

Each new biological outcome was preceded by a frozen design or an outcome-blind support audit. Later positive results did not reclassify failed earlier tests. The full audit trail, frozen designs, code and result JSONs are version controlled in the repository.

### Stage 1: does within-night movement direction maintain segregation?

For each eligible repeat-capture night, the observed FIRST trap and exact squared FIRST-to-LAST grid displacement were fixed. We enumerated all destinations on the same (7	imes7) grid with that exact displacement from FIRST and randomized only the feasible direction. Zero-length movements were unchanged.

Community segregation was summarized with the mean pairwise checkerboard C-score. For species (A) and (B),

[
C_{AB}=(r_A-S)(r_B-S),
]

where (r_A) and (r_B) are the numbers of occupied trap locations and (S) is the number of shared traps.

Singleton individual-nights were retained as fixed background. A species was eligible within a grid-season if it contributed at least five repeat-capture individual-nights, and a grid-season required at least three eligible species. We generated 10,000 joint direction randomizations. Unit effects were standardized relative to their distance-matched null distributions and averaged equally across grid-seasons.

The preregistered alternative was one-sided: observed directions should yield greater segregation than distance-matched feasible alternatives.

### Stage 2: is one point-like seasonal location sufficient?

Each individual was reduced to its seasonal anchor. Within each grid-season, species labels were permuted among fixed anchor locations while preserving the observed number of individuals assigned to each species. The primary statistic was again mean pairwise C-score.

This test asked whether species identity was associated with point-like seasonal placement. It used a different null from the published community analysis and was not treated as a reproduction test.

### Stage 4: temporal scale decomposition under the published fixed-fixed null

For the separately frozen 30-unit public-data universe, we constructed three species × trap presence/absence matrices per grid-season:

1. **ALL:** every valid capture location;
2. **NIGHT-FIRST:** only the earliest capture of each individual-night;
3. **ANCHOR:** one seasonal anchor per individual.

For each representation we used EcoSimR's SIM9 curveball algorithm with C-score, 5,000 null replicates and 500 burn-in iterations. SIM9 preserves species trap-occupancy totals and trap species-richness totals.

The eight segregated ALL units formed a fixed reference set. We prospectively classified temporal scale as:
- point-anchor sufficient if ANCHOR retained at least 6/8;
- between-night footprint if NIGHT-FIRST retained at least 6/8 but ANCHOR retained fewer than 6/8;
- within-night records materially contribute if NIGHT-FIRST retained fewer than 6/8.

### Stage 5B: are individual footprints assortative by species?

Within the 30-unit universe, an individual was included if observed on at least two nights. A species required at least three multi-night individuals in a grid-season, and a unit required at least three eligible species.

For individuals (i) and (j), footprint similarity was Jaccard overlap,

[
J_{ij}=rac{|F_icap F_j|}{|F_icup F_j|}.
]

For each unit, we calculated the difference between mean conspecific and heterospecific Jaccard similarity.

The null kept every footprint fixed in space and permuted species labels only among individuals with **exactly the same number of distinct traps**. This controlled exactly for footprint breadth and a major component of sampling depth. We used 10,000 joint permutations and equally weighted standardized unit effects.

### Stage 5A: does species-specific trap use persist within seasons?

We tested temporal persistence only in the eight fixed ALL-capture segregation-reference grid-seasons. Unique sampling nights were divided chronologically into equal EARLY and LATE halves; when the number of nights was odd, the single middle night was discarded.

Using NIGHT-FIRST data, we constructed EARLY and LATE species × trap matrices. The persistence statistic was matched species × trap recurrence,

[
P_u=sum_{s,j}I(E_{sj}=1 land L_{sj}=1).
]

EARLY was fixed and LATE was randomized with a fixed-fixed curveball null preserving each species' LATE number of occupied traps and each trap's LATE species richness. We used 10,000 null replicates after 500 burn-in swaps.

### Stage 7: persistence after complete within-season individual turnover

Stage 5 could be generated partly by repeatedly observing the same site-faithful individuals. Before opening Stage-7 spatial outcomes, we identified every species × individual ID observed at least once in both EARLY and LATE. Every such bridge individual was removed from **both** halves.

A species was retained if at least one EARLY-only and one LATE-only individual remained. All eight reference grid-seasons retained at least three eligible species. We then repeated the matched species × trap recurrence test with the same fixed-fixed LATE null.

The frozen decision required at least six informative units, at least six positive standardized effects, positive global mean effect and global one-sided (p<0.05).

A separate post-result broader audit applied the same turnover rule to a wider 22-unit support set. Its physical-grid robustness criterion was specified before those broader outcomes were opened.

### Stage 9: cross-season reassembly after complete individual turnover

The strongest test asked whether the spatial template reappeared after both individuals and season changed.

Within each grid we considered adjacent seasonal transitions: fall→winter, winter→spring and spring→summer. For every candidate grid × season-pair, we removed from **both seasons** every species × individual ID observed in both.

An outcome-blind support audit was then used to set a stricter eligibility rule. A species had to retain at least two season-A-exclusive and two season-B-exclusive individuals. A unit required at least three eligible focal species. This froze ten adjacent-season comparisons spanning six physical grids before any cross-season trap-overlap statistic was calculated.

For each fixed unit we built season-A and season-B species × trap matrices from NIGHT-FIRST records of the disjoint individual sets and calculated the same matched species × trap recurrence statistic. Season A was fixed; season B was randomized under a fixed-fixed curveball null preserving species occupancies and trap richness. We used 10,000 null replicates after 500 burn-in swaps.

The unit-level criterion required at least 8/10 informative units, at least 7/10 positive standardized effects, positive global mean standardized recurrence and joint Monte Carlo (p<0.05).

Because multiple adjacent-season comparisons occurred within some grids, a second criterion treated physical grid as the replication level. We averaged standardized effects across eligible seasonal transitions within each grid and exhaustively enumerated all (2^6=64) sign flips of the six grid means. Cross-season reassembly was supported only if at least 5/6 grid means were positive and the exact one-sided sign-flip (p<0.05).

## Statistical interpretation

All tests were directional only where a positive ecological prediction was frozen before the relevant outcome was opened. Failed one-sided tests were not reinterpreted through lower tails. Species-pair decompositions, alternative anchors, alternative overlap measures and weaker turnover thresholds were not opened after the main outcomes.

The public capture dataset was considered exhausted for the main ecological claim after Stage 9.

---

# Results

## Short-term movement did not directionally maintain the community pattern

Stage 1 had substantial support: 1,968 repeat-capture individual-nights across 18 eligible grid-seasons were randomized, and 1,415 (71.9%) had more than one feasible movement direction at the observed displacement length.

Observed LAST positions did not preserve greater community segregation than distance-matched feasible directions. The global mean standardized C-score excess was

[
T=-0.1966,
]

with one-sided Monte Carlo (p=0.8000).

Thus the data did not support a mechanism in which each observed within-night movement is preferentially directed so as to maintain the seasonal community checkerboard.

## One seasonal point per individual did not carry the segregation signal

The seasonal-anchor test included 1,334 individual anchors across 30 informative grid-seasons. The global standardized anchor C-score excess was

[
T=-0.0120,
]

with (p=0.5315).

Species identity was therefore not detectably associated with one point-like seasonal anchor under the frozen label-permutation null.

## The community signal localized to repeated use across nights

In the frozen 30-unit public-data reconstruction, the ALL-capture representation contained eight segregated, zero aggregated and 22 null grid-seasons.

The eight fixed segregated units were:
- grid 1 summer;
- grid 4 fall, winter, spring and summer;
- grid 6 fall, winter and summer.

NIGHT-FIRST retained seven of these eight segregation signals (87.5%) and created no new significant unit. The single lost reference unit was grid 1 summer. By contrast, ANCHOR retained none of the eight and created no new significant unit.

Across all 30 supported grid-seasons, SIM9 standardized effect sizes were strongly correlated between ALL and NIGHT-FIRST ((r=0.9474)) but almost uncorrelated between ALL and ANCHOR ((r=0.1088)).

The prospectively frozen scale classification was therefore **between-night footprint**.

## Different individuals of the same species shared similar multi-night footprints

There were 928 individuals observed on at least two nights before Stage-5B unit filtering, spanning all six focal species. Twenty-two grid-seasons met the frozen support rule, and all 22 had non-zero permutation-null variance.

Raw conspecific-minus-heterospecific footprint similarity was positive in 20/22 units. Mean conspecific Jaccard similarity was 0.05760, compared with 0.03446 among heterospecifics.

After species labels were permuted only among footprints with exactly equal numbers of distinct traps, the global standardized assortativity was

[
T=2.3149,
]

with (p=0.00009999).

Unit-level footprint assortativity also covaried with NIGHT-FIRST community segregation strength ((r=0.6943)).

Thus species-specific recurring-use domains were visible among individuals even after exact control for footprint breadth.

## Species-specific trap use persisted through the season

All eight fixed segregation-reference grid-seasons had non-zero temporal-persistence null variance, and all eight showed positive standardized EARLY→LATE matched species × trap recurrence.

The global standardized persistence statistic was

[
T=4.0909,
]

with one-sided Monte Carlo (p=0.00019996).

This ruled out the simple interpretation that the NIGHT-FIRST representation retained community segregation only because it contained more spatial observations than a one-point representation. In the segregated regimes, the identity of the species using particular traps was reproducible from the early to the late half of the season beyond fixed occupancy margins.

## Individual site fidelity amplified, but did not fully create, spatial persistence

Before Stage 7, 188 bridge individuals occurring in both EARLY and LATE were removed from both halves across the eight reference units.

All eight units remained informative. Seven of eight had positive standardized post-turnover recurrence. The global effect remained positive,

[
T=1.0374,
]

with (p=0.00159984).

The post-turnover effect was substantially smaller than the Stage-5 recurrence with persistent individuals retained ((T=4.0909)). Individual site fidelity therefore contributed strongly to temporal persistence, but recurrence was not eliminated when the shared individuals were removed.

A broader post-result audit was directionally consistent at the grid-season level (13/18 positive; mean standardized effect 0.752; joint (p=0.00080)) but did not pass its frozen physical-grid criterion: 5/6 grid means were positive, with exact sign-flip (p=0.125). We therefore do not generalize the Stage-7 strength uniformly across the full assemblage.

## Different individuals reassembled the species spatial template across seasons

The Stage-9 support audit removed all individuals shared between adjacent seasons before spatial outcomes were opened. The stricter frozen rule—at least two season-exclusive individuals per species in both seasons and at least three eligible species—yielded ten adjacent-season comparisons across six physical grids.

All ten comparisons had non-zero null variance, and nine showed positive standardized matched species × trap recurrence.

The global mean standardized cross-season recurrence was

[
Z=1.7747,
]

with joint Monte Carlo (p=0.00009999).

The six physical-grid mean effects were:
- grid 1: 1.572;
- grid 2: 2.868;
- grid 4: 3.500;
- grid 5: -0.464;
- grid 6: 2.245;
- grid 7: 0.393.

Five of six were positive. Exhaustive sign flipping of the six grid means gave an exact one-sided

[
p=0.046875.
]

The preregistered unit-level and independent-grid criteria both passed.

Therefore the species-associated spatial pattern did not require the same marked individuals to bridge adjacent seasons. Different sets of individuals reassembled the same species × trap structure.

---

# Discussion

## Community spatial information resides at the multi-night footprint scale

The central result is a localization rather than a simple detection of spatial segregation. The San Jacinto rodent community was already known to partition space. What was unresolved was the scale at which that pattern was biologically organized.

Two intuitive reductions failed. The pattern was not preferentially maintained by the directions of observed within-night movements when movement length and origin were held constant, and it was not recoverable from one point-like seasonal location per individual. Yet it survived almost intact after every later within-night recapture was removed, provided repeated locations across nights were retained.

This identifies an intermediate organizational scale: the **multi-night spatial footprint**. A movement vector is too local, and a single centre is too compressed. The relevant object is the distributed set of places an individual repeatedly uses through time.

That conclusion connects movement ecology and community ecology more specifically than the generic statement that movement affects coexistence. Movement-mediated community theory emphasizes pathways from individual movement to community assembly (Schlägel et al. 2020), while individual-level studies show that behavioural differences generate different spatial niches and interaction environments (Schirmer et al. 2019, 2020; Stiegler et al. 2026). Our results add a scale diagnosis for an independently documented community pattern: the spatial information detected at the community level is retained by repeated-use footprints but is absent from both the short-term directional rule and the point summary that might otherwise be assumed to generate it.

## The species template is not merely a property of persistent individuals

Multi-night footprints could still have been an elaborate restatement of site fidelity. If the same marked individuals repeatedly returned to the same traps, aggregation across those individuals would automatically create temporal persistence.

The turnover tests show that this explanation is incomplete.

Removing all individuals shared between the early and late halves of a season weakened species × trap recurrence sharply, demonstrating that individual fidelity is important. But recurrence remained above the fixed-fixed expectation. The correct interpretation is therefore layered: a species-associated spatial structure is present, and repeated use by the same individuals strengthens it.

Stage 9 provides the stronger separation. Across adjacent seasons, we removed every individual observed in both seasons, required at least two exclusive individuals per species in each season, and still recovered species-specific trap recurrence in 9/10 comparisons. The result also survived a conservative replication check in which six physical grids, rather than ten grid-season transitions, were the units of sign randomization.

The spatial pattern therefore cannot be carried only by particular marked individuals. It is repeatedly expressed by different members of the same species.

This does not imply a literal “species memory”. Population-level spatial fidelity and repeated assembly can arise without any shared cognitive representation. The safer inference is that there is a persistent **species-by-place template**: for whatever underlying reasons, different individuals of a species tend to rebuild spatial use in the same parts of a grid more often than fixed occupancy margins predict.

## Why step-level avoidance was a plausible but insufficient explanation

The null movement-direction result is biologically informative because the San Jacinto system contains direct evidence for interspecific dominance and avoidance. Larger heteromyids dominate smaller species in staged interactions, making continual heterospecific avoidance an obvious candidate for the field segregation pattern.

We did not find the predicted community-level signature. Given the same observed displacement length and starting point, the realized within-night direction did not preserve more segregation than feasible alternatives.

This does not mean that animals never avoid heterospecifics. Avoidance may occur at spatial or temporal scales not represented by consecutive trap captures, may be conditional on direct encounters, or may influence settlement and longer-term space use rather than every short movement. The result instead rejects the stronger bridge: the published seasonal checkerboard is not continuously maintained by a detectable direction bias in each observed within-night transition.

The distinction between interaction behaviour and community pattern is important. A competitive mechanism can affect where animals establish or repeatedly use space without leaving a simple displacement-by-displacement signature.

## A persistent environmental or community substrate is now the leading mechanistic class

What can cause different individuals to reconstruct the same species-associated spatial footprint after turnover?

The public capture data cannot answer that question directly, but the result constrains plausible mechanisms. The substrate must be more persistent than the identities of the individual rodents and sufficiently fine grained to recur at trap scale.

Microhabitat heterogeneity is an obvious candidate. The original study found species-specific associations with vegetation and soil variables, and those environmental features can persist across the time span of the present analysis. Burrows and refuges, resource distributions and stable landscape structure are related possibilities. Longer-term competitive sorting could also cause species to occupy particular parts of a grid without requiring every short-term movement to be directionally avoidant. Territorial or social constraints could contribute as well.

The key limitation is that the trap-level environmental measurements used by Chock et al. (2022) are not present in the deposited public dataset. We therefore cannot partition the Stage-9 recurrence into habitat, resource, refuge, social or competitive components without additional data.

Recent work comparing habitat and prior use shows why such a direct comparison would matter: environmental conditions and memory can have comparable explanatory power for animal space use, with their relative importance varying among species (Verzuh et al. 2025). Our turnover design weakens a purely individual-memory explanation because the individuals themselves change, but it does not distinguish stable habitat from other persistent species-level constraints.

## Implications for niche partitioning and community assembly

A common static view of niche partitioning describes species as occupying different parts of environmental or resource space. A common dynamic view asks how movement decisions generate those distributions. The present results indicate that an important intermediate object can be missed by both views.

The community pattern here is not well represented by a stable point per individual, yet it is also not written into every observed movement direction. It resides in a distributed, recurrent footprint that emerges over multiple nights and can be reconstructed by different individuals.

This suggests a more general principle:

> Persistent community spatial structure need not be stored in particular individuals or enforced at every movement step; it can be repeatedly reconstructed through species-specific patterns of distributed space use.

The principle is deliberately narrower than “scale matters”. It makes a falsifiable claim about where a community pattern survives when spatial information is progressively removed.

This view also changes how turnover is interpreted. Individual turnover usually emphasizes replacement, loss of identity or changing composition. Here turnover becomes a diagnostic tool: if the same species × place association is rebuilt after the individuals change, the organization lies above individual identity. In that sense, species turnover within a local population can reveal whether a community spatial pattern is a transient sum of individual behaviours or a recurrent property of the species–environment–community relationship.

## Conservation relevance

Four of the six focal species are heteromyids of conservation concern in southern California, and the original study emphasized the difficulty of conserving interacting species at the community level. Our reanalysis reinforces that perspective but changes what should be measured.

If species-specific spatial organization is expressed through distributed multi-night footprints, a single capture point, centroid or coarse occurrence polygon can miss the structure relevant to coexistence. Preserving enough area for each species may likewise be insufficient if fine-grained spatial heterogeneity generates recurrent species-specific domains.

This is a hypothesis about conservation mechanism, not a direct management prescription. Without the original trap-level environmental covariates we cannot identify which habitat features create the recurrent domains. But the scale decomposition indicates what future habitat work should explain: not simply where one animal is centred, but why different individuals of a species repeatedly reconstruct similar multi-location footprints through time.

## Limits and scope

Several limitations are central.

First, these are live-trap capture locations, not continuous telemetry trajectories. NIGHT-FIRST removes later within-night captures and therefore avoids relying on same-night post-capture displacement for the positive footprint results, but capture processes may still affect detection across nights.

Second, the exact 32-grid-season published spatial analysis could not be reconstructed from the deposited data because two winter grid-seasons contain only two focal species. We did not repair the discrepancy by inventing records or changing the denominator. The 30-unit temporal-scale analysis was separately frozen after the source audit.

Third, the Stage-8 broader turnover audit did not pass its independent-grid robustness criterion. Thus the strength of post-turnover recurrence is heterogeneous among grids. Stage 9 passed its own prospectively frozen six-grid criterion, but that exact sign-flip p-value was 0.046875, the smallest conventional significance level attainable by only three upper-tail sign configurations out of 64 beyond the observed threshold. The grid-level evidence should therefore be described as supportive but limited by six independent grids.

Fourth, the analyses localize the spatial structure but do not identify its causal substrate. Habitat, refuges, resources, social organization and longer-term competition remain unresolved.

Finally, this is one rodent assemblage. The scale hierarchy may not generalize to systems in which species segregation is driven by direct territorial repulsion, rapidly moving resources or seasonal migrations. Independent application of the same decomposition is needed before treating recurrent species-level footprints as a general rule of spatial coexistence.

## Conclusion

A static map of niche partitioning can hide where the underlying ecological organization resides. In this six-species rodent guild, the known community segregation pattern was not preferentially maintained by short-term movement directions and disappeared when individuals were compressed to one seasonal point. It was instead retained by distributed multi-night footprints, shared preferentially among conspecific individuals, persistent through seasons, and detectable after complete replacement of the individuals that expressed it.

The strongest result was cross-season reassembly: disjoint sets of individuals reconstructed species-specific trap use in 9/10 adjacent-season comparisons across six grids.

Spatial niche partitioning in this system is therefore best understood as a recurrent species-level spatial template expressed through multi-night space use. Individual fidelity amplifies that pattern, but the spatial organization can outlive the individuals that carry it.

---

# Data availability

The source capture data are publicly available from Figshare, doi:10.6084/m9.figshare.18295520.v1. The repository pipeline verifies the source-file SHA-256 checksum before analysis.

The original trap-level vegetation and soil variables used for resource-selection analyses are not included in that deposited record and were not reconstructed from surrogate data.

A versioned analysis repository and archival persistent identifier will be provided before publication.

# Code availability

All sequential designs, outcome-blind support audits, analysis scripts, frozen result artifacts and tests are maintained in the project repository. A review package and archival release will be prepared for submission.

# Ethics and original field permissions

This study is a secondary analysis of previously published data. Field ethics, trapping permits and animal-care approvals should be cited from Chock, Shier & Grether (2022) in the final submitted version rather than restated from memory here.

# References — working core

Chock, R. Y., Shier, D. M. & Grether, G. F. (2018). Body size, not phylogenetic relationship or residency, drives interspecific dominance in a little pocket mouse community. *Animal Behaviour*, 137, 197–204. doi:10.1016/j.anbehav.2018.01.015.

Chock, R. Y., Shier, D. M. & Grether, G. F. (2022). Niche partitioning in an assemblage of granivorous rodents, and the challenge of community-level conservation. *Oecologia*, 198, 553–565. doi:10.1007/s00442-021-05104-5.

Schirmer, A., Herde, A., Eccard, J. A. & Dammhahn, M. (2019). Individuals in space: personality-dependent space use, movement and microhabitat use facilitate individual spatial niche specialization. *Oecologia*, 189, 647–660. doi:10.1007/s00442-019-04365-5.

Schirmer, A., Hoffmann, J., Eccard, J. A. & Dammhahn, M. (2020). My niche: individual spatial niche specialization affects within- and between-species interactions. *Proceedings of the Royal Society B*, 287, 20192211. doi:10.1098/rspb.2019.2211.

Schlägel, U. E. et al. (2020). Movement-mediated community assembly and coexistence. *Biological Reviews*, 95, 1073–1096. doi:10.1111/brv.12600.

Stiegler, J., Schirmer, A., Eccard, J. A., Jeltsch, F. & Dammhahn, M. (2026). Boldness and niche width structure spatial interactions in a natural rodent community. *Journal of Animal Ecology*. doi:10.1111/1365-2656.70320.

Verzuh, T. L. et al. (2025). Beyond habitat: Memory versus environment in shaping animal space use. *Ecology Letters*, 28, e70233. doi:10.1111/ele.70233.
