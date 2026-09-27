# Local spatial cohesion in small mammals is redundant across species but context-dependent across sites

## Abstract

Ecological aggregation can generate new properties through complementarity, but an aggregate property can also be redundant when component species already satisfy it independently. We tested this distinction for a stringent local spatial-cohesion property in small-mammal metacommunities: under each prespecified trap-neighbourhood criterion, every positive trap had to have another positive neighbour. In 16 response-naive National Ecological Observatory Network sites, pooling species never increased cohesion beyond the best individual species; median gain was zero, no site showed a positive gain, and the preregistered null-adjusted sign test gave p = 1.0. Yet the carrier species were highly replaceable among sites: 48 site × carrier records involved 32 species and median pairwise carrier-set Jaccard similarity was zero. Those carriers spanned granivores, herbivores, omnivores and predators, showing that redundancy in this spatial response property did not imply redundancy in ecosystem-effect roles. We then froze an independent prospective mechanism test on all 11 remaining structurally eligible sites. After conditioning on each species' observed number of positive traps, observed spatial allocation did not produce carriers more often than random site-wide placement (median site excess = -0.080, 4/11 positive sites, one-sided exact p = 0.887). A second null preserving positive counts within each mammal grid reproduced observed carrier status almost exactly, leaving a median within-grid component of zero. Among species occurring at multiple fresh sites, 10/15 switched between carrier and non-carrier states. Local spatial cohesion is therefore a context-dependent occurrence state rather than a conserved species syndrome: ecologically different species can converge on it, but whether a species carries it depends primarily on how its occurrences are allocated among site-scale spatial strata.

## 1. Introduction

Metacommunity ecology links local community composition to regional processes such as dispersal, environmental filtering and species sorting (Thompson et al. 2020). A recurring ecological idea is that heterogeneous components can compensate for one another when aggregated. Insurance effects provide a familiar example: asynchronous responses among populations or species can stabilize regional abundance or ecosystem functioning (Loreau et al. 2003; Lamy et al. 2019; Hammond et al. 2020).

That complementarity logic does not imply that every aggregate ecological property must become stronger when species are pooled. Some properties can instead be redundant. Here we use redundancy only in a property-specific sense: multiple species may each independently satisfy the same declared occurrence-geometry criterion. This is narrower than general functional equivalence, an interpretation for which redundancy terminology requires particular caution (Laliberté et al. 2010; Eisenhauer et al. 2023).

Our criterion is best described as **local spatial cohesion**. Under a declared trap-neighbourhood adjacency rule, a species or pooled community is cohesive when every positive trap has at least one other positive trap connected to it. The criterion therefore detects the absence of isolated positive occurrences. It does not require a species to occupy the whole site or establish whole-landscape connectivity.

We first ask whether turnover among species creates this local spatial property through complementarity. Can pooling species satisfy spatial configurations unavailable to every individual species, or is the aggregate property already carried independently by one or more components?

This is not a direct test of spatial-insurance theory, whose classical predictions concern stability of aggregate abundance or function. Rather, it tests whether the broader complementarity logic motivating insurance effects transfers to a different aggregate property: local spatial cohesion of observed occurrences.

A second question follows once redundant carriers are identified. Is carrier status a species syndrome — associated with broad niche breadth, mobility, trophic position or abundance — or is it a context-dependent state that changes with the local species × site occurrence pattern? This distinction parallels the broader separation between traits governing responses to environmental filters and traits governing ecosystem effects (Lavorel and Garnier 2002). Species may share a spatial response state while differing strongly in diet, trophic role and ecosystem effects.

Our original primary contrast was deliberately stringent:

**emergent cohesion gain = pooled-community cohesion fraction - maximum individual-species cohesion fraction.**

A positive value requires the pooled community to satisfy at least one prespecified spatial criterion unavailable to every individual species. After that endpoint was closed, we used a post hoc carrier audit to describe taxonomic and trophic turnover, then designed a separate response-blind 11-site prospective validation to distinguish three mechanisms: total prevalence, allocation among mammal grids, and fine arrangement within grids.

## 2. Methods

### 2.1 Fresh confirmatory sites

We used the NSF National Ecological Observatory Network small-mammal box-trapping product DP1.10072.001, RELEASE-2026 (NEON 2026). We excluded 16 NEON sites used in the preceding methodological programme and three tutorial sites whose biological summaries had been viewed during study design. From RELEASE-2026 small-mammal sites, we scanned site codes in ascending order and froze the first 16 meeting response-blind geometry and structural-adequacy requirements:

JORN, KONA, LAJA, LENO, MLBS, MOAB, NIWO, NOGP, OAES, ONAQ, ORNL, OSBS, RMNP, SERC, SJER and SOAP.

No biological response was opened during site selection.

### 2.2 Trap nodes and adjacency criteria

Individual geolocatable mammal traps were spatial nodes. Coordinates containing X were excluded prospectively because NEON's official implementation treats those trap locations as spatially uncertain.

For each site, Haversine distances among retained traps were used to construct an adequacy-complete distance ladder. Exact duplicate adjacency operators were removed, leaving three or four distinct one-step adjacency criteria. All 16 sites passed the frozen structural gate.

These criteria are prespecified spatial scales, not estimated dispersal kernels.

### 2.3 Target guild and incidence

The target set comprised species-rank SMALL_MAMMAL taxa with NEON `taxonProtocolCategory = target`. Two species whose public response summaries had been exposed during earlier design work were excluded prospectively.

For each site, a species-by-trap incidence matrix recorded whether each eligible species was ever captured at each frozen non-X trap in RELEASE-2026.

### 2.4 Continuity fraction

An adjacency criterion was satisfied when every positive trap had at least one other positive trap connected under that criterion.

The pooled-community continuity fraction was the proportion of site criteria satisfied by the union of eligible target-species positive traps. Species continuity fractions were computed independently. Species with fewer than two retained positive traps had continuity fraction zero.

### 2.5 Complementarity, redundancy and weakest-link outcomes

At each site:

**emergent continuity gain = community continuity fraction - best-species continuity fraction.**

- gain > 0: complementarity
- gain = 0: redundancy at the strongest species level
- gain < 0: weakest-link effect under the all-positive definition

A strict emergent criterion was satisfied by the pooled guild but by no eligible individual species.

Cross-species-only local support counted positive trap-by-criterion targets with at least one positive neighbour but no neighbouring trap sharing a species with the target.

Dominance coverage was the maximum proportion of guild-positive traps occupied by any single species.

### 2.6 Assemblage-row null and confirmatory rule

Within each site, 999 null communities were generated by permuting complete observed species-incidence row vectors among fixed guild-positive trap coordinates. This preserved the guild-positive trap set, every species' positive-trap count, the multiset of local richness values, and within-trap co-occurrence vectors, while changing only their spatial assignment.

The null-adjusted site effect was observed emergent continuity gain minus the median permuted gain. The frozen aggregate test counted sites with null-adjusted effect > 0 and used a one-sided exact sign test against probability 0.5. The endpoint is consumed and closed.

### 2.7 Post hoc carrier niche and trait audit

After the original 16-site endpoint was closed, we classified all 32 species that had been individually sufficient carriers into four coarse primary trophic groups: granivore, herbivore, omnivore and predator. The classification was used only to ask whether the same local spatial property was restricted to one ecosystem-effect guild. It did not alter any confirmatory endpoint.

We also matched carrier species to the COMBINE mammal trait database using exact scientific names. Reported values were preferred and imputed values were used only when the reported value was missing. We examined adult mass, dispersal distance, habitat breadth, diet breadth, home-range size, population density and trophic level as exploratory correlates of carrier recurrence across the original sites.

### 2.8 Independent prospective mechanism panel

We then froze a new mechanism programme before opening any additional biological response. All sites used in the original methodological programme, the 16 Paper A sites, and three design-contaminated tutorial sites were excluded. The remaining RELEASE-2026 small-mammal sites were screened using geometry alone. All 11 remaining candidates passed the frozen structural gate and were retained: SRER, STEI, STER, TALL, TEAK, TOOL, TREE, UKFS, WOOD, WREF and YELL. No site was added, replaced or removed after response access.

Before response access we also froze the COMBINE trait table for the complete 132-species eligible NEON target pool. Exact IUCN-2020 binomial matching yielded standardized traits for 119 species; unmatched names were left unmatched rather than rescued after observing the response.

### 2.9 Count-conditioned and grid-conditioned mechanism nulls

For each eligible species at each fresh site, the primary mechanism null conditioned on its observed number of positive trap nodes, k. We placed k positives uniformly without replacement among the site's guild-positive trap nodes and calculated the probability that the randomized pattern satisfied every frozen adjacency criterion. The species-level carrier excess was:

**observed carrier indicator - count-conditioned expected carrier probability.**

We used 999 randomizations per species unless the complete combinatorial space was smaller, in which case it was enumerated exactly. The primary site effect was the mean species carrier excess. The frozen aggregate test used a one-sided exact sign test across sites, with at least six scored sites required. Support for positive spatial organization beyond prevalence required both a positive median site effect and p < 0.05.

A predeclared secondary null additionally preserved each species' observed number of positive traps separately within every mammal grid. This produced the exact additive decomposition:

**site-wide carrier excess = between-grid allocation component + within-grid organization component.**

Here, the between-grid component is the difference between grid-conditioned and site-wide expected carrier probabilities, while the within-grid component is the observed carrier indicator minus the grid-conditioned expectation. Grid identity is a sampling stratum and potential habitat proxy, not a measured habitat variable.

Finally, the pre-frozen COMBINE traits were related descriptively to species carrier excess using within-site Spearman correlations. These trait analyses were secondary and could not alter the primary mechanism decision.


## 3. Results

### 3.1 Pooling never created additional continuity

All 16 fixed sites completed the once-only programme. Median emergent continuity gain was 0. No site had a positive gain. The null-adjusted positive-site count was 0/16 and the preregistered one-sided sign-test p-value was 1.0.

Fifteen pooled communities satisfied every prespecified adjacency criterion. Yet at all 16 sites, at least one individual target species also satisfied every criterion.

### 3.2 No strict emergence occurred

The strict emergent fraction was zero at every site. There was no site-by-criterion case in which the pooled guild remained spatially continuous while every eligible individual species failed.

### 3.3 Cross-species-only local support was rare

Across sites, cross-species-only local support had median 0.00269, mean 0.0103 and maximum 0.0661. Species replacement occasionally supplied local neighbour support, but these events never accumulated into a criterion satisfied only by the pooled community.

### 3.4 Continuity was redundant across species

The number of species tied for best continuity had a median of two and ranged from one to eight. Dominance coverage had median 0.835 and range 0.501–0.982; 10/16 sites had at least one species occupying 80% or more of guild-positive traps.

Different sites were carried by different species. Across all sites there were 48 site × carrier records distributed among 32 distinct species. Twenty of those 32 species were carriers at only one site, eight at two sites, and four at three sites; no species was a carrier at more than three of the 16 sites.

Among the 120 possible site pairs, only 18 shared any carrier species. Pairwise carrier-set Jaccard similarity had median 0, mean 0.0316 and maximum 0.5.

The pattern is therefore not only within-site redundancy. It is **within-site redundancy combined with strong among-site turnover in the taxonomic identity of the species carrying continuity**.

### 3.5 Richer sites deepened redundancy without increasing the sufficient-species fraction

A post hoc frozen-summary decomposition showed that the number of individually sufficient species increased with observed target-species richness (Spearman rho = 0.668). Dominance coverage declined with richness (rho = -0.594), whereas cross-species-only rescue did not increase (rho = -0.390).

However, the fraction of eligible species that were individually sufficient had a median of 0.477 and showed little rank association with richness (rho = -0.159). Thus richer sites contained more alternative continuity carriers largely because they contained more eligible species, not because a progressively larger fraction of species became spatially sufficient.

These analyses are exploratory and cannot alter the confirmatory decision.

### 3.6 ORNL showed a weakest-link effect

At ORNL, the pooled community satisfied 0.25 of adjacency criteria while the best individual species satisfied all criteria, giving an emergent gain of -0.75.

This does not imply that biodiversity or species pooling is biologically harmful. It demonstrates a property of the all-positive continuity definition: adding spatially restricted positive occurrences makes the aggregate criterion stricter because every added occurrence must also have peer support.

### 3.7 Carriers spanned contrasting trophic and ecosystem-effect roles

The 32 carrier species were distributed among four coarse primary trophic groups: 13 granivores, 10 herbivores, seven omnivores and two predators. Thirteen of the original 16 sites contained at least two independent carriers; 12 of those 13 sites contained carriers from more than one trophic group. At MOAB and OAES, granivorous, herbivorous, omnivorous and predatory species all independently satisfied the same local spatial-cohesion criterion.

Thus property-specific spatial redundancy was usually cross-trophic rather than redundancy among species with the same ecosystem-effect role.

The carrier-only COMBINE diagnostic provided little evidence for a universal carrier syndrome. Correlations between carrier recurrence and adult mass, dispersal, habitat breadth, diet breadth and home range were all small. Species-level density was the largest positive exploratory candidate, but this signal was not treated as a local abundance mechanism because COMBINE density is not site-specific NEON density.

### 3.8 Fresh validation did not support positive spatial organization beyond prevalence

All 11 fresh sites were estimable and none stopped after biological-response access. Across sites, the median mean carrier excess relative to the site-wide count-conditioned null was **-0.0804**. Four of 11 sites had positive effects and the frozen one-sided exact sign test gave **p = 0.8867**. The preregistered positive spatial-organization hypothesis was therefore not supported.

Across 68 eligible species × site records, 29 were observed carriers, whereas the summed site-wide count-conditioned expectation was 33.85. Observed occurrence geometry thus did not systematically convert a fixed number of positive traps into the carrier state more often than random site-wide placement.

### 3.9 Grid allocation almost completely determined the carrier state

The predeclared grid-conditioned decomposition localized nearly all departure from the site-wide null to allocation among mammal grids. The median between-grid allocation component was **-0.0804**, whereas the median within-grid organization component was **0**. No site had a positive mean within-grid component and the one-sided sign test for positive within-grid effects gave **p = 1.0**.

At species × site resolution, the grid-conditioned expected carrier probability equalled the observed binary carrier state exactly in 66 of 68 records; the other two departures were extremely small Monte Carlo differences. Thus, under the declared criterion, knowing how many positive traps a species had in each grid was nearly sufficient to determine whether it was a carrier.

Carrier status was also strongly context-dependent. Fifteen species occurred as eligible species at two or more fresh sites and **10 of those 15 switched between carrier and non-carrier states**. For example, *Myodes gapperi* was a carrier at STEI, TREE and YELL but not WREF; *Microtus montanus* was a carrier at TEAK but not YELL; and *Perognathus flavus* was non-carrier at SRER but carrier at STER.

Post-response diagnostics suggested that concentration within occupied grids, rather than simple range breadth across grids, was the strongest simple descriptor of carrier status. The median within-site Spearman association between carrier status and positive traps per occupied grid was 0.707, compared with 0.579 for total positive-trap count and 0.324 for occupied-grid count. This diagnostic is exploratory and does not alter the prospective mechanism decision.

The prospectively frozen standardized traits did not provide a consistent residual explanation after positive-node count was conditioned out. Median within-site Spearman correlations with carrier excess were +0.100 for adult mass, +0.100 for dispersal distance, -0.316 for habitat breadth, -0.103 for diet breadth, -0.063 for home range, -0.300 for species-level population density and +0.099 for trophic level.


## 4. Discussion

The study resolves two different questions that are easily conflated. First, species pooling did not create a new local spatial-cohesion property. Across the original 16 fresh sites, every pooled outcome could already be matched by at least one individual species. Second, the species carrying that property were neither taxonomically fixed nor ecologically equivalent. Carrier identity turned over strongly among sites, carriers spanned contrasting trophic roles, and most repeatedly observed species in an independent fresh panel switched between carrier and non-carrier states.

The fresh mechanism validation changes how the original result should be interpreted. The property measured here is not whole-landscape connectivity. It is a stringent **no-isolated-occurrence** condition: every positive trap must have peer support under every declared adjacency criterion. A species concentrated in one spatially coherent patch can therefore satisfy the criterion, whereas a widespread species can fail if it contains isolated peripheral occurrences. We consequently interpret the original “continuity” measure as **local spatial cohesion**.

This clarification also explains why broad species traits performed poorly. Carrier status was not consistently associated with dispersal distance, habitat breadth, home range, trophic level or population density after prevalence was conditioned out. More importantly, the same species frequently changed carrier state among sites. Carrier status is therefore better understood as a **species × site spatial state** than as a conserved species attribute.

The trophic audit makes the complementary point. Granivores, herbivores, omnivores and predators could independently occupy the same spatial-response state. At MOAB and OAES, all four groups were represented among individually sufficient carriers. In the language of response–effect frameworks, this is closer to convergence in a spatial response property despite divergence in ecosystem-effect roles than to classical functional redundancy (Lavorel and Garnier 2002). A seed predator, herbivore and predator can all be locally cohesive without being functionally interchangeable.

The prospective nulls further locate the relevant spatial scale. Once the number of positives assigned to each mammal grid was preserved, carrier status was reproduced almost perfectly. Fine placement within grids contributed essentially no detectable carrier signal under the present metric. Yet the between-grid component did not act in one direction. Some species became much more likely to be carriers because their positives were concentrated into particular grids, whereas others became less likely because their observed allocation created unsupported occurrences across grids. The aggregate median between-grid effect was negative.

This means that the fresh result should not be summarized simply as “habitat filtering creates continuity.” Grid identity is not a habitat measurement, and the primary test found no systematic positive excess over prevalence. A more defensible interpretation is that **grid-scale allocation determines which local cohesion state is realized**, while that allocation can either create or destroy the carrier property. Independent vegetation, moisture, soil, topographic or other environmental data are needed to determine whether habitat filtering is the mechanism behind those grid allocations.

The post-response concentration diagnostic points to a concrete next hypothesis. Within sites, positive traps per occupied grid showed a stronger association with carrier state than total positive traps or number of occupied grids. This suggests that local occupancy density within used spatial strata may be more relevant to no-isolated-occurrence geometry than broad site-wide prevalence. Because this contrast was identified after opening the fresh response, it remains hypothesis-generating.

Together, the original and fresh panels support a two-level ecological picture. **Across species**, very different ecological roles can converge on the same local spatial-cohesion state. **Across sites**, both the identity of the carrier and whether a given species is a carrier can change. The stable object is therefore not a universal carrier taxon or trait syndrome, but the repeated emergence of the same local spatial property from different species × environment configurations.

The ORNL weakest-link result remains useful in this framework. Pooling can add isolated occurrences and thereby lower an all-positive cohesion score even when one component species is fully cohesive. This is a property of the endpoint, not evidence that biodiversity is harmful.

### 4.1 Limits

The analysis evaluates observed trap captures, not latent occupancy, abundance or movement. Detection probability is not modeled. The adjacency criteria are spatial evaluation scales, not estimated dispersal kernels. Mammal-grid identity is a sampling stratum rather than a measured habitat variable. The post-response positive-traps-per-grid diagnostic is exploratory. Finally, local spatial cohesion should not be equated with dispersal connectivity, demographic coupling, ecosystem functioning or temporal insurance.

## 5. References

Eisenhauer, N., Hines, J., Maestre, F. T. and Rillig, M. C. 2023. Reconsidering functional redundancy in biodiversity research. *npj Biodiversity* 2:9. https://doi.org/10.1038/s44185-023-00015-5.

Hammond, M., Loreau, M., de Mazancourt, C. and Gonzalez, A. 2020. Disentangling local, metapopulation, and cross-community sources of stabilization and asynchrony in metacommunities. *Ecosphere* 11:e03078. https://doi.org/10.1002/ecs2.3078.

Laliberté, E., Wells, J. A., DeClerck, F., Metcalfe, D. J., Catterall, C. P., Queiroz, C., Aubin, I., Bonser, S. P., Ding, Y., Fraterrigo, J. M., McNamara, S., Morgan, J. W., Sánchez Merlos, D., Vesk, P. A. and Mayfield, M. M. 2010. Land-use intensification reduces functional redundancy and response diversity in plant communities. *Ecology Letters* 13:76–86. https://doi.org/10.1111/j.1461-0248.2009.01403.x.

Lavorel, S. and Garnier, E. 2002. Predicting changes in community composition and ecosystem functioning from plant traits: revisiting the Holy Grail. *Functional Ecology* 16:545–556. https://doi.org/10.1046/j.1365-2435.2002.00664.x.

Lamy, T., Wang, S., Renard, D., Lafferty, K. D., Reed, D. C. and Miller, R. J. 2019. Species insurance trumps spatial insurance in stabilizing biomass of a marine macroalgal metacommunity. *Ecology* 100:e02719. https://doi.org/10.1002/ecy.2719.

Loreau, M., Mouquet, N. and Gonzalez, A. 2003. Biodiversity as spatial insurance in heterogeneous landscapes. *Proceedings of the National Academy of Sciences USA* 100:12765–12770. https://doi.org/10.1073/pnas.2235465100.

NEON. 2026. Small mammal box trapping (DP1.10072.001), RELEASE-2026. https://doi.org/10.48443/A83H-TB34.

Thompson, P. L., Guzman, L. M., De Meester, L., Horváth, Z., Ptáčník, R., Vanschoenwinkel, B., Viana, D. S. and Chase, J. M. 2020. A process-based metacommunity framework linking local and regional scale community ecology. *Ecology Letters* 23:1314–1329. https://doi.org/10.1111/ele.13568.


## 6. Figure captions

**Figure 1. Complementarity, redundancy and weakest-link outcomes for an aggregate spatial-continuity property.** Complementarity occurs when the pooled community satisfies spatial criteria unavailable to every individual species; redundancy occurs when one or more species independently match the pooled community; a weakest-link outcome occurs when additional spatially restricted positive occurrences make the pooled all-positive criterion harder to satisfy.

**Figure 2. Pooled-community versus best-species continuity fractions across 16 fresh small-mammal sites.** Filled symbols represent the pooled target-species community and open symbols the best individual species. Pooling increased continuity at no site. Fifteen sites were tied at 1.0 versus 1.0; at ORNL the pooled community satisfied 0.25 of prespecified adjacency criteria while the best individual species satisfied all criteria.

**Figure 3. Two-scale organization of spatial continuity.** Richer sites contain more individually sufficient species, but continuity-carrier identity turns over strongly among sites. Across the programme, 48 site × carrier records were distributed among 32 species; 20 carrier species occurred at one site only and only 18 of 120 site pairs shared any carrier species. These carrier-turnover summaries are post hoc exploratory.

**Figure 4. Weakest-link aggregation at ORNL.** The best individual species can remain fully cohesive while pooling adds spatially restricted positive occurrences that must also satisfy the all-positive criterion, reducing the pooled cohesion fraction. This endpoint property does not imply that biodiversity is biologically harmful.

**Figure 5. Prospective mechanism validation on 11 independent fresh sites.** Site-level mean carrier excess under the site-wide count-conditioned null is decomposed additively into a between-grid allocation component and a within-grid organization component. Within-grid components were zero or nearly zero at all sites, whereas between-grid allocation accounted for essentially all deviation from the site-wide null. The primary one-sided sign test did not support positive spatial organization beyond prevalence (median site excess = -0.0804, 4/11 positive sites, p = 0.8867).

## 7. Artificial intelligence use

Generative artificial intelligence (OpenAI ChatGPT) was used during manuscript development for language editing, organizational assistance and drafting portions of analysis and repository code. The author reviewed and verified the analysis logic, executable code, numerical results, literature citations and scientific interpretations, and takes responsibility for the submitted work. Generative AI was not used to create or alter the primary biological response data.
