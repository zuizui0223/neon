# Community spatial continuity is species-redundant within sites but carried by different taxa across small-mammal metacommunities

## One-sentence claim

Across 16 fresh NEON small-mammal sites, pooling target species never increased spatial continuity beyond the best individual species, yet the identity of individually sufficient species turned over strongly among sites: continuity was locally redundant but taxonomically replaceable across the network of sites.

## Abstract

Ecological aggregation can generate new properties through complementarity, or it can be redundant when component species already carry the aggregate property independently. We tested whether species turnover creates spatial continuity in small-mammal metacommunities that is absent from every individual species. Before biological-response access, we froze 16 fresh NSF NEON sites, geolocatable trap nodes, prespecified trap-neighbourhood adjacency criteria, target taxa, and a community-minus-best-species contrast. Pooling species never increased continuity beyond the best individual species: median gain was zero, no site showed a positive gain, and the preregistered null-adjusted sign test gave p = 1.0. At every site, at least one individual species satisfied every adjacency criterion, and no strict emergent criterion occurred. Cross-species-only local support was rare. Yet this within-site redundancy was not carried by one recurrent taxon. A post hoc frozen-summary audit found 48 site × carrier records distributed across 32 species; 20 species were carriers at only one site, no species at more than three sites, and only 18 of 120 site pairs shared any carrier species (median pairwise Jaccard = 0). Richer sites contained more individually sufficient species while dominance declined, but the fraction of eligible species that were sufficient did not increase. At ORNL, pooling reduced continuity from 1.0 for the best species to 0.25 for the community under the all-positive definition. Spatial continuity was therefore organized as **within-site redundancy with among-site turnover in carrier identity**, rather than as turnover-generated complementarity.

## 1. Introduction

Metacommunity ecology links local community composition to regional processes such as dispersal, environmental filtering and species sorting. A recurring ecological idea is that heterogeneous components can compensate for one another when aggregated. Insurance effects provide a familiar example: asynchronous responses among populations or species can stabilize regional abundance or ecosystem functioning.

That complementarity logic does not imply that every aggregate ecological property must become stronger when species are pooled. Some properties can instead be redundant. A regional community may appear spatially continuous because one or more individual species are already continuous across the same landscape. In that case, taxonomic aggregation inherits an existing property rather than creating an emergent one.

We ask whether this distinction applies to observed spatial occupancy. If local assemblages turn over across space, can the union of species occurrences satisfy spatial configurations that no individual species can satisfy alone? Or is community-level continuity mostly explained by species whose own occurrence patterns already span the relevant trap network?

This is not a direct test of spatial-insurance theory, whose classical predictions concern stability of aggregate abundance or function. Rather, it tests whether the broader complementarity logic motivating insurance effects transfers to a different aggregate property: spatial continuity of observed occurrences.

Our primary contrast was deliberately stringent:

**emergent continuity gain = pooled-community continuity fraction - maximum individual-species continuity fraction.**

A positive value requires the pooled community to satisfy at least one prespecified spatial criterion unavailable to every individual species. We further quantified strict emergence, cross-species-only local support and dominance coverage, and used a preregistered assemblage-row permutation to test whether any gain depended on the spatial assignment of local assemblages.

## 2. Methods

### 2.1 Fresh confirmatory sites

We excluded 16 NEON sites used in the preceding methodological programme and three tutorial sites whose biological summaries had been viewed during study design. From RELEASE-2026 small-mammal sites, we scanned site codes in ascending order and froze the first 16 meeting response-blind geometry and structural-adequacy requirements:

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

## 4. Discussion

The expected complementarity pattern did not occur. Across 16 fresh NEON small-mammal sites, taxonomic turnover never created spatial continuity beyond what was already available in at least one component species.

The alternative organization was redundancy. Every site contained at least one species whose occurrence pattern satisfied all prespecified adjacency criteria, and no pooled community satisfied a criterion that every individual species failed.

This clarifies an important distinction among aggregate ecological properties. Complementarity can stabilize aggregate abundance or function when components compensate for one another. Spatial continuity under an all-positive occurrence rule need not behave the same way. A taxonomically heterogeneous community can remain spatially redundant because one or more constituent species already span the relevant spatial structure.

The low cross-species-only support reinforces this interpretation. Turnover occurred locally, but local replacement did not generate new site-level continuity.

At the same time, the identity of the species carrying continuity changed strongly among sites. This creates a two-scale pattern that a simple “turnover versus no turnover” framing misses. **Within sites**, continuity was often redundant because multiple species could satisfy the full spatial criterion independently. **Among sites**, those sufficient species were taxonomically replaceable: most site pairs shared no carrier species at all. Taxonomic turnover therefore characterized *who carried* the aggregate spatial property, not *whether pooling was required to create it*.

This distinction separates two forms of biodiversity organization. Complementarity asks whether different species must be combined to obtain the property. Redundancy asks whether several species can each provide it independently. The NEON sites were dominated by the latter, even though the identity of redundant providers changed across the broader set of sites.

ORNL establishes a third logical outcome: depending on the measured property, aggregation can be complementary, redundant, or weakest-link. The ecological lesson is not that diversity reduces connectivity; it is that aggregation changes the set of observations a continuity criterion must accommodate.

### 4.1 Exploratory richness and carrier-turnover pattern

A post hoc audit found that richer sites contained more individually fully continuous species (Spearman rho = 0.668, p = 0.0047), while richness was negatively associated with dominance coverage (rho = -0.594, p = 0.015). Richness was not positively associated with cross-species-only rescue (rho = -0.390, p = 0.135).

The new carrier analysis sharpens that result. The median fraction of eligible species that were individually sufficient was 0.477, and this fraction showed little association with richness (rho = -0.159). Richer sites therefore deepened redundancy primarily in absolute number, while becoming less dominated by a single widespread species.

Across sites, carrier identity was highly labile: 32 species supplied 48 site-level carrier records, only 15% of site pairs shared any carrier species, and the median pairwise Jaccard similarity was zero. This suggests a form of **taxonomic replaceability of the continuity role across sites**. It should not be interpreted as temporal insurance, causal stabilization, or a conserved functional trait because the analysis is post hoc and sites span different regional species pools.

### 4.2 Limits

The analysis evaluates observed trap occurrences, not latent occupancy or movement. The adjacency criteria are spatial evaluation scales, not estimated dispersal kernels. The result does not identify habitat filtering, mass effects, colonization history or demographic mechanisms. The all-positive definition is intentionally stringent and is not the only meaningful definition of metacommunity connectivity.

## 5. Claim boundary

Supported:
- pooled-community continuity never exceeded best-species continuity at any fresh site;
- no strict emergent criterion occurred;
- cross-species-only local support was rare;
- at every site, at least one individual species satisfied every criterion;
- ORNL showed a weakest-link reduction under the declared all-positive definition;
- exploratorily, richer sites contained more individually fully continuous species;
- exploratorily, continuity-carrier identity turned over strongly among sites: 32 species supplied 48 site-level carrier records, and only 18/120 site pairs shared any carrier species;
- exploratorily, the median fraction of eligible species that were individually sufficient was 0.477 and did not increase with richness.

Not supported:
- spatial-insurance theory is falsified;
- species turnover is unimportant to metacommunity dynamics generally;
- high richness causes redundancy;
- the result estimates dispersal mechanisms;
- biodiversity pooling is biologically harmful;
- the result automatically generalizes beyond NEON small mammals;
- carrier turnover causes stability or insurance;
- continuity-carrier identity is a conserved functional trait.


## 6. Figure plan

1. **Complementarity, redundancy and weakest-link outcomes** — conceptual three-case diagram.
2. **Fresh-site paired continuity fractions** — pooled community versus best species for all 16 sites.
3. **Two-scale redundancy structure** — left: redundancy depth versus richness; right: carrier-frequency distribution and pairwise carrier-set overlap, emphasizing within-site redundancy but among-site taxonomic turnover.
4. **ORNL weakest-link example** — extra peripheral positives reduce pooled continuity while an individual species remains fully continuous.
