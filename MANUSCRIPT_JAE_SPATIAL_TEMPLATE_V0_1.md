# Spatial niche partitioning recurs across disjoint individual sets in a rodent guild

**Target:** Journal of Animal Ecology — Research Article  
**Version:** v0.1 biological-first draft  
**Status:** ecology manuscript scaffold built from frozen Stage 1–9 results; separate from the MEE temporal-aliasing manuscript

## Abstract

1. Spatial niche partitioning can arise from short-term movement away from competitors, persistent placement of the same individuals, or repeated reconstruction of species-specific space use by different sets of individuals. We asked at what temporal and organizational scale a known rodent-community segregation pattern is encoded, and whether it persists above individual identity.

2. We reanalysed year-round capture–mark–recapture data from a six-species granivorous rodent guild in southern California. Sequential tests, frozen before their focal outcomes were opened, evaluated distance-matched within-night movement direction, one seasonal point per individual, repeated multi-night footprints, and species × trap recurrence after removing individuals shared between time windows.

3. Within-night movement direction did not preserve more segregation than feasible directions of identical length (1,968 repeat nights; standardized excess = -0.197, p = 0.800). In the publicly supported spatial matrices, one NIGHT-FIRST location per individual-night retained 7 of 8 segregation signals, whereas one seasonal anchor per individual retained 0 of 8. Conspecific multi-night footprints were more similar than equally broad heterospecific footprints (T = 2.315, p < 0.0001), and species × trap associations recurred between early and late seasonal halves (8/8 reference units positive; T = 4.091, p = 0.0002).

4. Recurrence remained after removing every individual shared between seasonal halves (7/8 reference units positive; T = 1.037, p = 0.0016). Across adjacent seasons, after removing all individuals shared between seasons, disjoint sets of individuals reassembled species × trap associations in 9 of 10 frozen transitions across six grids (T = 1.775, p < 0.0001; five of six grid means positive; exact grid-level sign-flip p = 0.0469).

5. Fine-scale spatial partitioning was therefore carried by recurrent species-specific multi-night footprints rather than by each movement step or a single point-like individual centre. Individual fidelity amplified the pattern, but different conspecifics rebuilt the same species-associated relationship with place. Spatially stable communities can retain structure even when the individuals expressing it change.

## Keywords

community ecology; individual identity; movement ecology; niche partitioning; rodents; site fidelity; space use; spatial niche

# 1. Introduction

A map of species occurrences is a snapshot of both ecological structure and the individuals that happened to generate it. When species repeatedly occupy different parts of the same landscape, the pattern is commonly interpreted as spatial niche partitioning. Such partitioning can reduce encounter rates or resource overlap among competitors and has long been central to coexistence theory. Yet a persistent spatial pattern does not identify the biological level at which that persistence resides.

This ambiguity is especially important for mobile animals. A stable community map could be generated in at least three qualitatively different ways. First, animals could continually make short-term movement decisions that maintain separation from heterospecifics. Second, the same individuals could remain faithful to different sites or activity centres, so that individual persistence automatically creates apparent species persistence. Third, species could repeatedly occupy similar parts of the landscape even as individual membership changes. In the third case, the community pattern is not carried by particular animals. It is reconstructed by different individuals of the same species.

Movement ecology and community ecology provide strong reasons to distinguish these alternatives. Individual movement decisions generate space-use distributions, and those distributions can scale to population and community patterns (Schlägel et al. 2020). Small-scale, station-keeping movement has therefore been proposed as an underdeveloped route through which movement can affect coexistence (Péron 2024). At the same time, studies of individual spatial specialization show that conspecifics need not use space similarly. Behavioural type, habitat preference and individual experience can all produce substantial among-individual heterogeneity in home ranges, movement and interaction neighbourhoods, including in small mammals (Schirmer et al. 2019, 2020; Stiegler et al. 2026). Population-level spatial stability can consequently coexist with changing individual spatial specialization across seasons (Li et al. 2023).

Most of this literature asks how individual variation contributes to population space use. A different question is whether a species-level spatial pattern survives turnover of the individuals themselves. This distinction is analogous to a broader problem in ecology: higher-order structures can persist even while their constituent members change. Animal social-network studies, for example, have emphasized that stable social structure under demographic turnover requires explanation because persistence of the network need not imply persistence of the same individuals (Shizuka & Johnson 2020). In spatial ecology, however, persistence is still often quantified as individual site fidelity or population return rate, making it difficult to separate a recurrent species–place relationship from repeated observations of site-faithful individuals.

A six-species granivorous rodent guild in southern California provides an unusual opportunity to make this separation. Previous work in the system showed strong temporal overlap but significant fine-scale spatial segregation in a subset of grid-seasons, together with species-specific associations with vegetation and soil variables (Chock, Shier & Grether 2022). Experimental work in the same broader system also found a body-size dominance hierarchy and avoidance by smaller pocket mice of larger heterospecifics (Chock, Shier & Grether 2018). These findings establish both a community pattern and plausible behavioural mechanisms, but they do not reveal the temporal level at which the field pattern is maintained.

The capture protocol retained unusually fine within-night information: traps on 7 × 7 grids at 6.25-m spacing were checked three times per night and captured animals were released at the point of capture. Individual animals therefore sometimes appeared at multiple trap locations in the same night. Rather than treating those repeated locations only as an observation problem, we use them to separate candidate biological carriers of spatial niche partitioning.

We asked one overarching question:

> **Does spatial niche partitioning recur when the same marked individuals are excluded from successive time windows?**

We approached this by sequentially removing possible carriers of the spatial pattern. We first tested whether observed within-night movement directions preferentially maintained community segregation after controlling exactly for movement distance. They did not. We then asked whether one point-like seasonal location per individual was sufficient to preserve the published spatial pattern. It was not. We next tested whether the relevant structure instead resided in repeated multi-location footprints across nights, whether those footprints were shared among conspecific individuals, and whether their species-specific spatial organization persisted through time. Finally, we removed all marked individuals shared between time windows and asked whether non-overlapping conspecific sets reconstructed the same species × trap associations within and across seasons.

Our central prediction was that if spatial partitioning is only an accumulation of individual site fidelity, removing all shared individuals should eliminate species-specific spatial recurrence. Conversely, recurrence among disjoint sets of individuals would indicate a higher-order species–place relationship: a spatial template that persists above individual identity. We use “template” descriptively for a repeatable species × location association; it does not imply cognitive memory, social transmission or a particular causal substrate.

# 2. Materials and Methods

## 2.1 Study system and public data

We used the publicly archived capture–mark–recapture data associated with Chock, Shier & Grether (2022), Figshare DOI 10.6084/m9.figshare.18295520.v1. The focal assemblage consists of six granivorous rodent taxa:

- *Chaetodipus fallax* (CHFA);
- *Dipodomys simulans* (DKR);
- *Dipodomys stephensi* (SKR);
- *Perognathus longimembris brevinasus* (LAPM);
- *Peromyscus maniculatus* (PEMA);
- *Peromyscus eremicus* (PEER).

Animals were live-trapped on eight 7 × 7 grids with 6.25 m spacing between adjacent traps. Traps were checked three times per night and animals were released at their capture location. Seasons followed the original study: fall = August–October, winter = November–January, spring = February–April and summer = May–July.

The public capture file was checksum-verified before each analysis. Analyses requiring temporal ordering used records with valid species, grid, individual identity, date, trap flag and check time. Community presence–absence analyses required only fields necessary for the corresponding species × trap matrix.

### Public-data boundary

The deposited capture file contains only two focal species in grid 3 winter and grid 7 winter, whereas the published Methods report 3–6 species in every one of the 32 grid × season matrices. We therefore did not invent missing records or an unpublished inclusion rule.

For analyses that reconstruct the original fixed-fixed spatial co-occurrence result, we prospectively defined a public-data-supported universe of 30 grid-seasons containing at least three focal species and excluded only grid 3 winter and grid 7 winter. In those 30 units the all-capture reconstruction recovered exactly eight significantly segregated matrices and no significantly aggregated matrices, matching the published headline count of eight segregated grid-seasons.

Other analyses used their own outcome-blind support rules described below.

## 2.2 Sequential scale-localization design

The analyses were intentionally sequential. Each new biological question was frozen before opening its focal outcome, and failed tests were retained as failures rather than replaced by alternative metrics, thresholds or species-pair searches.

The hierarchy was:

1. within-night movement direction;
2. one point-like seasonal individual location;
3. repeated multi-night individual footprint;
4. within-season species × trap recurrence;
5. recurrence after excluding all individuals shared between seasonal halves;
6. recurrence across seasons after excluding all individuals shared between adjacent seasons.

The individual footprint was based exclusively on NIGHT-FIRST records—the earliest valid trap location for each individual on each calendar night—to prevent later same-night recapture positions from carrying the main ecological result.

## 2.3 Does within-night movement direction maintain spatial segregation?

For focal species, valid records were grouped by grid × individual × calendar date and ordered by check time. Nights with at least two valid captures contributed a FIRST and LAST location.

A species was eligible within a grid-season if it contributed at least five repeat-capture individual-nights; all singleton nights from eligible species were retained as fixed background. A grid-season required at least three eligible species.

For each repeat night, we fixed the FIRST trap and the exact observed squared grid displacement to the LAST trap. We enumerated all traps on the same 7 × 7 grid lying at that exact displacement from the FIRST trap and randomly selected among those feasible destinations. Thus the null preserved movement magnitude, origin and grid-edge geometry while randomizing direction.

For each observed and randomized community we calculated mean pairwise Stone–Roberts C-score from species × trap presence–absence. We used 10,000 joint randomizations. The frozen global statistic was the mean grid-season standardized excess of the observed LAST C-score over its direction-randomized null. The one-sided test asked whether observed movement directions maintained more segregation than feasible directions of exactly the same length.

## 2.4 Which temporal representation carries the published segregation pattern?

We compared three representations under the same EcoSimR SIM9 fixed-fixed C-score null.

**ALL** used every valid capture location.

**NIGHT-FIRST** retained only the earliest valid trap for each individual on each calendar night.

**ANCHOR** reduced each individual within a grid-season to one point. The anchor was the observed NIGHT-FIRST trap minimizing summed squared grid distance to that individual's other NIGHT-FIRST traps, with ties broken first by observed frequency and then lexicographically.

For the 30 public-data-supported grid-seasons, ALL was required to reconstruct exactly eight segregated and zero aggregated units before reduced representations were interpreted.

For each representation and unit, the species × trap matrix was randomized using EcoSimR SIM9, preserving species trap-occupancy totals and trap species-richness totals. We used 5,000 null replicates after 500 burn-in swaps. A unit was classified as segregated when its observed C-score exceeded the 97.5th percentile of its representation-specific null.

Before opening NIGHT-FIRST or ANCHOR results, we froze a retention rule relative to the eight ALL-segregated reference units. Retaining at least six of eight signals with ANCHOR would classify point anchors as sufficient; retaining at least six with NIGHT-FIRST but fewer than six with ANCHOR would classify the relevant level as the between-night footprint; fewer than six NIGHT-FIRST signals would indicate that later within-night records materially contributed.

## 2.5 Are individual multi-night footprints species-specific?

For each individual observed on at least two distinct nights within a grid-season, we defined the multi-night footprint as the set of distinct NIGHT-FIRST traps used.

Within an eligible unit, we calculated Jaccard similarity between every pair of individual footprints and defined

\[
D_u = \overline{J}_{\mathrm{conspecific}} -
      \overline{J}_{\mathrm{heterospecific}} .
\]

A species required at least three multi-night individuals and a grid-season required at least three eligible focal species.

The null kept every individual footprint exactly fixed in space and permuted species labels only among individuals with the same number of distinct traps in their footprint. This controls exactly for footprint breadth while destroying the association between species identity and footprint location. We used 10,000 joint permutations and standardized each unit against its null. The global statistic was the equally weighted mean standardized assortativity across informative grid-seasons.

No alternative footprint-size binning, minimum-night threshold, overlap metric or species-pair decomposition was opened after the result.

## 2.6 Does species-specific trap use persist within a season?

To distinguish persistent structure from simple sampling depth, we split each grid-season chronologically into equal EARLY and LATE halves of unique sampling nights, discarding the single middle date when necessary.

Primary inference used the eight fixed ALL-segregated reference grid-seasons. A focal species had to occur in both halves and contribute at least two NIGHT-FIRST records in each.

For each unit we constructed binary EARLY and LATE species × trap matrices and measured matched recurrence

\[
P_{obs} = \sum_s \sum_j E_{sj} L_{sj},
\]

the number of trap incidences occupied by the same species in both halves.

EARLY remained fixed. LATE was randomized using fixed-fixed curveball swaps preserving every species' LATE trap-occupancy total and every trap's LATE species richness. We used 5,000 null replicates after 500 burn-in swaps.

The frozen persistence claim required at least six informative reference units, at least six positive standardized effects, and a positive global mean standardized recurrence with one-sided Monte Carlo p < 0.05.

## 2.7 Does recurrence survive exclusion of all individuals shared between seasonal halves?

The previous test could be driven by the same site-faithful animals being present in both temporal halves. Before measuring recurrence, we therefore identified every species × individual identity occurring in both EARLY and LATE and removed that individual from **both** halves.

The resulting EARLY-only and LATE-only matrices contained mutually exclusive individual sets by construction. Species-support rules were fixed before any post-removal spatial overlap outcome was opened.

We then applied the same matched species × trap recurrence statistic and fixed-fixed LATE randomization. The primary universe remained the eight fixed segregation-reference units. The frozen decision required at least six informative units, at least six positive effects and a positive global statistic with p < 0.05.

## 2.8 Does a species-level spatial template reassemble across seasons?

We next imposed a stronger turnover test across adjacent seasons within the same physical grid:

- fall → winter;
- winter → spring;
- spring → summer.

For each grid × season pair, every species × individual identity observed in both seasons was removed from **both** matrices before spatial recurrence was calculated.

After this removal, a species had to retain at least two distinct individuals in each season. A unit required at least three such species. A support-only audit performed before opening recurrence outcomes froze 10 eligible grid × adjacent-season units spanning six physical grids. Across all candidate season pairs, 290 bridge individuals were removed before support evaluation.

The recurrence statistic again counted matched species × trap incidences between season A and season B. Season A remained fixed; season B was randomized with a fixed-fixed curveball null preserving species occupancy and trap richness. We used 10,000 null replicates after 500 burn-in swaps.

The unit-level claim required at least 8 of 10 informative units, at least 7 of 10 positive effects, a positive mean standardized recurrence and p < 0.05.

Because multiple season pairs could arise from one physical grid, we additionally averaged standardized effects within grid and enumerated all \(2^6=64\) sign flips of the six grid means. The cross-season claim required at least five positive grid means and an exact one-sided sign-flip p < 0.05.

### Identity-turnover terminology

Here, **identity turnover** is an analytical contrast: all marked individuals observed in both compared time windows are removed from both before recurrence is measured. The remaining matrices therefore contain disjoint sets of observed identities. This does **not** establish literal demographic replacement, mortality, recruitment or complete turnover of the underlying population, because an animal not captured in one window may still have been present.

## 2.9 Scope and non-independence

The analyses are a structured reanalysis of one field system, not six independent species experiments. We therefore use physical-grid robustness where possible and distinguish prospectively frozen primary tests from post-result descriptive generality analyses.

A broader within-season turnover audit extended the same identity-removal rule beyond the eight reference units. Although its unit-level signal was positive, its six-grid sign-flip test did not pass. We treat that as a scope limit rather than evidence for generality across all grids.

# 3. Results

## 3.1 Short-term movement was common but did not directionally maintain segregation

Within-night relocation was common in the two species used in the original positional-variation validation, and the six-species Stage-1 dataset provided 1,968 repeat-capture individual-nights across 18 eligible grid-seasons. Of these repeat nights, 1,415 (71.9%) had more than one feasible direction at the observed movement length.

Despite this directional freedom, observed movement directions did not yield higher community segregation than exact-distance randomized directions. The global standardized C-score excess was

\[
T=-0.1966,
\]

with one-sided Monte Carlo \(p=0.8000\).

Thus the first candidate carrier of community structure—move-by-move directional maintenance—was rejected.

## 3.2 The spatial signal was preserved by multi-night footprints, not point anchors

In the 30 grid-seasons supported by the public file, the ALL representation reconstructed eight segregated units and zero aggregated units.

The eight fixed reference units were grid 1 summer; all four seasons of grid 4; and fall, winter and summer of grid 6.

Removing every later same-night capture and retaining only NIGHT-FIRST locations preserved seven of those eight significant segregation signals (87.5%). Only grid 1 summer was lost, and no new NIGHT-FIRST unit became significant.

By contrast, reducing each individual to one seasonal point retained none of the eight reference signals.

The prospectively frozen classification was therefore **between-night footprint**.

Across all 30 supported grid-seasons, the standardized co-occurrence pattern was strongly conserved between ALL and NIGHT-FIRST (Pearson \(r=0.9474\)) but not between ALL and ANCHOR (\(r=0.1088\)). Mean SIM9 standardized effect size declined from 2.073 for ALL to 1.413 for NIGHT-FIRST and -0.103 for ANCHOR.

## 3.3 Different conspecifics used more similar multi-night footprints

The individual-footprint analysis contained 928 individuals observed on at least two nights and 22 informative grid-seasons.

After exact control for the number of traps in each individual's footprint, conspecific individuals occupied more similar multi-night footprints than heterospecific individuals. The global standardized footprint-assortativity statistic was

\[
T=2.3149,
\]

with one-sided Monte Carlo \(p=0.00009999\).

Raw conspecific-minus-heterospecific similarity was positive in 20 of 22 units.

Unit-level footprint assortativity covaried with community NIGHT-FIRST segregation (descriptive \(r=0.6943\)), indicating that the individual and community patterns were linked rather than independent summaries of the same data.

## 3.4 Species-specific spatial footprints recurred through the season

The eight fixed segregation-reference units all had sufficient support for an independent EARLY–LATE recurrence test.

All eight showed positive standardized recurrence of the same species at the same traps. The global mean standardized recurrence was

\[
T=4.0909,
\]

with one-sided Monte Carlo \(p=0.00019996\).

In a broader descriptive set, 20 of 22 eligible grid-seasons had positive standardized recurrence (mean \(Z=2.661\), median \(Z=2.637\)).

Thus the multi-night result was not explained simply by NIGHT-FIRST containing more spatial observations than a point representation. The species × trap map itself was reproducible through time.

## 3.5 Individual fidelity amplified but did not create spatial persistence

Across the eight reference units, 188 individuals appeared in both EARLY and LATE and were therefore removed from both halves before the shared-identity-exclusion test.

Even with no marked individual shared between the two matrices, seven of eight units retained positive standardized species × trap recurrence. The global mean standardized effect was

\[
T=1.0374,
\]

with one-sided Monte Carlo \(p=0.00160\).

The effect was substantially weaker than the corresponding recurrence before identity removal (4.091), showing that individual site fidelity was an important amplifier of spatial persistence. However, the positive post-exclusion result demonstrated that fidelity of the same individuals was not sufficient to explain the species-level spatial pattern.

## 3.6 Disjoint individual sets reassembled species-specific space use across seasons

The most stringent test compared adjacent seasons after deleting every marked individual shared by the two seasons.

The support-only audit froze 10 eligible season transitions across six physical grids. All 10 had non-zero null variance and nine had positive standardized recurrence.

The global mean standardized cross-season recurrence was

\[
T=1.7747,
\]

with one-sided joint Monte Carlo \(p=0.00009999\).

The corresponding physical-grid means were 1.572, 2.868, 3.500, -0.464, 2.245 and 0.393 for grids 1, 2, 4, 5, 6 and 7, respectively. Five of six grid means were positive. The exact one-sided sign-flip test over the six independent grid means gave

\[
p=0.046875.
\]

The frozen decision therefore supported **cross-season species-template reassembly**.

Because every individual shared between paired seasons had been removed from both seasons, this recurrence cannot be attributed to the same marked animals returning to the same traps.

## 3.7 Scope limit: broader turnover generalization was suggestive but not established

A separately frozen post-result generalization audit applied the within-season shared-identity-exclusion test to 18 supported grid-seasons across six physical grids.

Thirteen of 18 units were positive, with global mean standardized recurrence 0.752 and joint Monte Carlo \(p=0.00080\). However, although five of six grid means were positive, the exact six-grid sign-flip test was \(p=0.125\), failing the predeclared grid-level robustness criterion.

We therefore do not generalize the within-season shared-identity-exclusion effect to the entire assemblage. The primary identity-independent recurrence inference remains strongest for the fixed segregated regimes and the independent adjacent-season test.

# 4. Discussion

## 4.1 A community map can outlive the individuals that made it

The central result is simple: the fine-scale spatial organization of this rodent guild persisted after the identities of the animals generating it were removed.

This persistence was not inferred from a single static comparison. It emerged after sequentially removing plausible carriers of the pattern. Within-night movement direction did not maintain segregation. One point-like seasonal location per individual did not reproduce it. Repeated multi-night footprints did. Those footprints were more similar among conspecific individuals, recurred through the season, and remained species-specific after all individuals shared between temporal windows were deleted. Across adjacent seasons, different individuals reconstructed the same species × trap associations.

These results distinguish **identity-carried stability** from **template-reassembled stability**. Identity-carried stability arises when persistent individuals repeatedly use the same places. Template-reassembled stability arises when non-overlapping sets of observed individuals of the same species occupy similar spatial domains. Both occurred here. Removing shared individuals weakened the recurrence signal substantially, showing that individual fidelity matters. But it did not erase the pattern.

The community map was therefore more persistent than its membership.

## 4.2 Spatial niches need not be reducible to movement steps or centres

The scale decomposition also changes how the spatial niche itself should be pictured.

A simple movement-based explanation predicts that community segregation should be visible in the direction of individual steps. We found no support for that prediction after controlling exactly for origin and movement length.

A simple home-centre explanation predicts that one representative seasonal location per individual should preserve the segregation. It did not.

The signal instead required a distributed, multi-location footprint accumulated over repeated nights. This middle scale is ecologically intuitive but often omitted when movement studies jump directly from fine-scale trajectories to home-range summaries. In the present system, the repeated-use domain—not the momentary direction and not a single centre—was the spatial object most closely aligned with the community pattern.

This result complements rather than contradicts movement-mediated coexistence theory. Schlägel et al. (2020) emphasized the need to connect individual movement processes to community-level outcomes, while Péron (2024) showed theoretically that species-specific station-keeping space use can support coexistence without classical functional trade-offs. Our contribution is empirical scale localization in a natural multispecies guild: not every measurable component of movement carries the community signal equally.

## 4.3 Individual spatial specialization and species-level templates are different questions

Individual spatial specialization is well established. Conspecific animals can differ markedly in movement, home-range extent, microhabitat selection and interaction neighbourhoods (Schirmer et al. 2019, 2020; Stiegler et al. 2026). Those findings might seem to predict that a species-level spatial map should dissolve as individual membership changes.

Instead, conspecific individuals in the present study had more similar multi-night footprints than equivalently broad heterospecific footprints, and species × place recurrence persisted after turnover.

This does not imply that conspecifics are interchangeable. The attenuation after bridge-individual removal shows the opposite: persistent individuals contribute substantial additional structure. A better interpretation is hierarchical. Individual animals have their own spatial histories within a broader species-associated domain. Species-level structure is therefore neither merely the average of identical individuals nor merely the persistence of particular individuals.

The distinction resembles a general problem recognized in animal social systems, where network or group structure can persist despite demographic turnover (Shizuka & Johnson 2020). Recent work on sparrow social communities similarly shows that higher-order organization can remain recognizable as membership changes. The analogy is conceptual rather than mechanistic: the rodent result concerns species–place associations, not social connections. But both systems illustrate that stability of ecological organization need not require stability of the entities carrying it at any one time.

## 4.4 What rebuilds the spatial template?

The present analyses localize the structure but do not identify its causal substrate.

A strong clue is that the footprint–community association is much stronger among physical grids than among seasons within a grid. Across seven grids with matched analyses, mean individual-footprint assortativity and mean community segregation were strongly correlated (descriptive \(r=0.923\)), whereas the within-grid seasonal correlation was much weaker (\(r=0.271\)). This points toward persistent local context rather than a rapidly changing seasonal process.

Habitat structure is an obvious candidate, but it is not a new result of this study. Chock et al. (2022) already showed species-specific selection on vegetation and soil axes, using all captures and recaptures in individual-level resource-selection models with individual ID and grid as random effects. That analysis was restricted to May–July 2016. It therefore establishes a strong prior expectation that different individuals of a species can respond similarly to a persistent habitat mosaic. What it did not test was whether the **community-level species × trap segregation signal** is localized to a particular temporal representation, whether it recurs after all shared marked identities are removed, or whether such recurrence extends across adjacent seasons beyond the summer resource-selection window. Those are the distinctions tested here. Stable refuge or burrow distributions, spatial resource structure, territorial constraints and long-term competitive sorting remain alternative substrates.

Competition also remains plausible but cannot be inferred directly from the present tests. Experimental work in this system showed size-structured interspecific dominance and heterospecific avoidance (Chock et al. 2018). Yet our within-night direction test found no evidence that observed short-term moves continually enforce the field checkerboard. Competition could instead operate at slower decisions such as settlement, refuge selection or repeated foraging-domain placement.

The relevant mechanism may therefore act before or above the movement step.

## 4.5 A general principle: ecological spatial structure can persist above identity

The broadest inference supported by these data is:

> **Ecological spatial structure can persist above individual identity.**

This principle is not equivalent to population-level site fidelity, which can itself be estimated from capture–recapture data at the population level (Tschopp et al. 2018). Site fidelity asks whether individuals or a population repeatedly use a location. Here the critical operation was different: every marked individual observed in both compared windows was excluded from both, and we then asked whether the association between **species identity and fine-scale location** still recurred among disjoint observed identity sets.

Likewise, this is not “collective memory” in a cognitive sense. The template may be regenerated independently by different animals responding to the same habitat and competitive landscape.

A spatial niche can therefore be viewed not only as an area occupied by a population, but as a repeatable mapping

\[
\text{species identity} \longrightarrow \text{relative use of places},
\]

which may persist even as the individuals instantiating that mapping change.

That distinction should matter wherever ecologists infer mechanism from repeated distribution maps. Observed stability can be produced by fidelity of persistent individuals, by recurring recruitment into similar spatial roles, or by both. Those alternatives imply different responses to demographic disturbance.

## 4.6 Implications for conservation and reintroduction

The original San Jacinto work emphasized the conservation challenge of maintaining a community in which smaller subordinate rodents coexist with larger competitors. The shared-identity-exclusion result sharpens that problem.

If species-specific spatial organization were carried only by the same resident individuals, then loss of those individuals would be expected to erase much of the pattern. Instead, different individuals can reconstruct the spatial template. This suggests that the underlying landscape features or interaction regime that repeatedly generates spatial roles may be as important as the currently occupying animals.

For restoration and reintroduction, “occupied location” and “regenerating spatial niche” are therefore not necessarily the same thing. Protecting the environmental conditions that repeatedly generate appropriate recurring-use domains may therefore matter as much as protecting the locations occupied by the currently observed individuals.

This remains a hypothesis about management mechanism, not a demonstrated intervention effect.

## 4.7 Limitations

First, this is one rodent guild. The cross-season test included six physical grids and passed a conservative grid-level sign-flip criterion, but broader generalization would require another system or substantially more independent spatial replication.

Second, the data are capture–recapture observations rather than continuous movement tracks. NIGHT-FIRST reduces dependence on later within-night post-capture relocation, but the inferred footprints are capture-based spatial footprints rather than complete natural trajectories.

Third, the publicly deposited dataset cannot reproduce the published 32-matrix species-richness statement exactly: two winter grid-seasons contain only two focal species. We therefore isolated a prospectively frozen 30-unit public-data-supported universe for the scale-decomposition analysis and did not impute missing species.

Fourth, the trap-level vegetation and soil data used in the original resource-selection analysis are not included in the public Figshare record. We consequently cannot close the most plausible habitat-template mechanism directly.

Finally, Stage 8 showed that turnover recurrence should not be generalized indiscriminately across every grid-season. The strongest identity-independent signal occurs in the spatial regimes where community segregation is itself strongest, with an independent cross-season test providing broader but still finite replication.

# 5. Conclusions

Spatial niche partitioning in this mobile rodent guild was not maintained by continual within-night directional avoidance and could not be compressed to one seasonal point per animal. It resided in recurrent, species-specific multi-night footprints.

Individual fidelity strengthened those footprints, but did not create them completely. When all individuals shared between time windows were removed, non-overlapping sets of conspecifics still reassembled the same fine-scale species × place associations within seasons and across adjacent seasons.

The result changes the unit of stability. A stable community pattern need not depend on repeatedly observing the same individuals. Spatial niche structure can be a higher-order species–place relationship that recurs across disjoint observed identity sets.

# Acknowledgements

[To be completed. Do not infer authorship, funding or acknowledgements from the public source paper.]

# Conflict of interest

[To be completed by the authors.]

# Author contributions

[To be completed by the authors.]

# Data availability

The public capture–mark–recapture data are available from Figshare at DOI 10.6084/m9.figshare.18295520.v1. Analysis code and frozen result objects will be archived in a versioned repository with a persistent identifier before publication. The trap-level vegetation and soil data used in the original resource-selection analysis are not redistributed in the Figshare record used here.

# References — core positioning set

Chock, R. Y., Shier, D. M. & Grether, G. F. (2018). Body size, not phylogenetic relationship or residency, drives interspecific dominance in a little pocket mouse community. *Animal Behaviour*, 137, 197–204. https://doi.org/10.1016/j.anbehav.2018.01.015

Chock, R. Y., Shier, D. M. & Grether, G. F. (2022). Niche partitioning in an assemblage of granivorous rodents, and the challenge of community-level conservation. *Oecologia*, 198, 553–565. https://doi.org/10.1007/s00442-021-05104-5

Li, et al. (2023). Linking changes in individual specialization and population niche of space use across seasons in the great evening bat (*Ia io*). *Movement Ecology*. https://doi.org/10.1186/s40462-023-00394-1

Péron, G. (2024). Movement-based coexistence does not always require a functional trade-off. *Ecological Modelling*, 487, 110549. https://doi.org/10.1016/j.ecolmodel.2023.110549

Tschopp, A., Ferrari, M. A., Crespo, E. A. & Coscarella, M. A. (2018). Development of a site fidelity index based on population capture-recapture data. *PeerJ*, 6, e4782. https://doi.org/10.7717/peerj.4782

Schirmer, A., Herde, A., Eccard, J. A. & Dammhahn, M. (2019). Individuals in space: personality-dependent space use, movement and microhabitat use facilitate individual spatial niche specialization. *Oecologia*, 189, 647–660. https://doi.org/10.1007/s00442-019-04365-5

Schirmer, A., Hoffmann, J., Eccard, J. A. & Dammhahn, M. (2020). My niche: individual spatial niche specialization affects within- and between-species interactions. *Proceedings of the Royal Society B*, 287, 20192211. https://doi.org/10.1098/rspb.2019.2211

Schlägel, U. E., et al. (2020). Movement-mediated community assembly and coexistence. *Biological Reviews*, 95, 1073–1096. https://doi.org/10.1111/brv.12600

Shizuka, D. & Johnson, A. E. (2020). How demographic processes shape animal social networks. *Behavioral Ecology*, 31, 1–11.

Stiegler, et al. (2026). Boldness and niche width structure spatial interactions in a natural rodent community. *Journal of Animal Ecology*. https://doi.org/10.1111/1365-2656.70320

# Figure plan

## Figure 1. The ecological puzzle: a mobile guild with stable spatial partitioning

A. Study design: 7 × 7 trap grid, three checks per night, six focal species.  
B. Previously documented spatial segregation across grid-seasons.  
C. Frequency of within-night relocations illustrating that the animals are not spatially static.

Purpose: motivate the question without making positional aliasing the paper topic.

## Figure 2. Where does the spatial information live?

Three representations of the same observations:

- within-night transition direction;
- NIGHT-FIRST multi-night footprint;
- one seasonal ANCHOR per individual.

Show Stage-1 null result plus Stage-4 retention (ALL 8/8 reference, NIGHT-FIRST 7/8, ANCHOR 0/8) and SES correlations.

Purpose: falsify movement-step and single-centre explanations and localize the signal to the between-night footprint.

## Figure 3. Multi-night footprints are species-specific and recurrent

A. Conspecific vs heterospecific individual-footprint overlap under exact footprint-size control.  
B. EARLY–LATE same-species trap recurrence for the eight reference units.  
C. Optional grid-level relationship between footprint assortativity and community segregation, clearly labelled exploratory/descriptive.

Purpose: connect individual space use to persistent community structure.

## Figure 4. Same spatial structure, different animals

A. Schematic of bridge-individual removal.  
B. Within-season shared-identity-exclusion standardized recurrence by reference unit.  
C. Cross-season standardized recurrence for the 10 frozen adjacent-season units.  
D. Six physical-grid means with exact sign-flip result.

Purpose: deliver the main biological result: species-specific spatial structure recurs across disjoint individual sets.
