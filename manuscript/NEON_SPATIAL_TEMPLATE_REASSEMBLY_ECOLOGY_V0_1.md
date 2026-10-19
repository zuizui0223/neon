# Spatial niche signatures reappear across seasons after turnover in observed small-mammal individuals: independent evidence from San Jacinto and NEON

**Working ecology manuscript v0.1 — 19 October 2026**  
**Status: RESEARCH DRAFT, not submitted.** Source-dependent mechanism, cross-rank equivalence, detectability and code-review issues require resolution before a journal submission decision.  
**Proposed article type:** full ecological research article. Author list not yet designated.  
**Primary positive NEON analysis:** preregistered in `docs/NEON_CROSS_SEASON_GENUS_SPATIAL_TEMPLATE_DESIGN_20261019.md` **after** the previously opened San Jacinto result, and **before** NEON recurrence outcomes.  
**Do not pool San Jacinto and NEON p-values or call their species/genus endpoints identical.**

## Abstract

A community can recover a characteristic spatial organization even when the animals observed at its constituent locations change. Spatial niche partitioning has been documented in small-mammal assemblages, yet distinguishing persistence of individual animals from recurrent use of habitat positions by different individuals is less often tested across independent sites. We asked whether seasonally separated small-mammal cohorts show greater within-lineage recurrence at the same fixed trap locations than expected after retaining the richness of each trap position and the number of positions occupied by each lineage. We first reanalysed a year-round, six-grid southern California rodent dataset at species resolution using adjacent seasons with repeated animals removed from both seasonal samples. The earlier frozen analysis found positive species-level recurrence in 9 of 10 grid–season comparisons, with 5 of 6 physical grids showing positive means (exact grid sign-flip p=0.046875). We then tested an independent, preregistered, genus-resolution prediction in the National Ecological Observatory Network's (NEON) versioned RELEASE-2026 box-trap archives. We selected completed three-night 10×10 grid sessions without inspecting spatial outcomes, restricted comparisons to consecutive meteorological seasons, removed tags observed in both seasons, and retained 58 comparisons across 30 plots in 14 physical sites. All 58 source-fixed genus×trap matrices were informative under a fixed-fixed season-B randomization preserving genus occupied-station counts and trap-level genus richness. Site-level mean standardized recurrence was +0.801; 11 of 14 physical sites had positive mean recurrence and the exact, one-sided physical-site sign-flip p-value was 0.001160 (16,384 sign patterns). Thus the identity of observed trapped individuals was not necessary for **genus-associated trap-location recurrence** across adjacent seasons. The two datasets differ in taxonomic resolution, trapping frame and season structure, precluding a pooled estimate or a claim of species-level universality. Persistent microhabitat, genus-specific detectability and interactions remain competing, untested explanations. This cross-programme evidence supports a repeatable ecological **pattern** while leaving its causal mechanism unresolved.

**Keywords:** individual turnover; site use; habitat filtering; niche partitioning; seasonal recurrence; small mammals; ecological community reassembly; NEON.

## Ecological significance for a broad audience

Animals move, die, emigrate and re-enter observational samples. Does that mean the *places* occupied by particular lineages continually lose their ecological identity? Our results indicate that, at fixed trapping positions, **different tagged small mammals tend to reconstruct genus-associated spatial patterns across seasons more than expected by chance given each season's observed genus and trap occupancy**. This is neither an estimate of population home-range stability nor direct evidence that competition drives the reconstruction. It is an empirical question about the **persistence of spatial niche structure despite observed individual replacement**, not about better estimating detection or movement from live traps.

## Introduction

Stable spatial segregation does not require static individuals. Species and genera can repeatedly encounter the same kinds of local habitat, select similar patches, or respond to persistent social and microenvironmental filters. Therefore community spatial organization could remain statistically recognizable even if the trapped individuals change from one season to the next. Conversely, individual fidelity could create apparent spatial stability without requiring any persistent ecological sorting of newly observed animals. Distinguishing these possibilities calls for explicit tracking of individual identities and for null models that respect uneven local trapping occupancy.

Small-mammal spatial niche partitioning is established, not a discovery invented here. Thinsp and Price (1997) observed temporally stable and habitat-associated spatial segregation between *Dipodomys stephensi* and *D. agilis* over two years; the stability depended partly on sympatric species abundance. Chock et al. (2022) reported nonrandom spatial segregation, temporal overlap and microhabitat associations among six granivorous rodent species in the San Jacinto Wildlife Area. Their published analysis investigated contemporaneous spatial partitioning using fixed-fixed trap-occupancy randomization; it did **not** establish that species-specific trap use reassembled after removing animals captured in both seasons. Previous work on other mammals has documented turnover of recognizable individuals and spatial use, and community persistence has long been central in ecological theory. Hence our claim cannot be the first example of temporally stable rodent niches or high mammal turnover.

The narrower question is whether, for two adjacent seasons, taxon-associated capture locations repeat when the **observed animal identities overlap neither across seasons nor within the focal unit**, and whether this recurrence exceeds what one would expect merely because a taxon occupies many trap positions or a few traps are generally popular.

Two independent programmes provide complementary evidence. The San Jacinto dataset records multiple checks within nights and supports species-level analysis across one local set of grids. NEON standardizes the box-trapping grid geometry at geographically separated sites but captures coarser, three-night event histories with substantial field species-label uncertainty. We therefore frozen the NEON primary test at **genus level**, did not reinterpret prior density-regression outcomes, and required enough independent *sites* to discriminate a geographically repeated ecological pattern from repeated seasonal events inside one place.

We predicted **positive genus-associated cross-season trap recurrence** beyond a season-B fixed-fixed null, even after excluding all tags observed in both seasons. The independent NEON endpoint and support limits were written into repository history before its spatial recurrence responses were opened, but after the positive San Jacinto result was known.

## Methods

### Independent San Jacinto source and prior result

The published year-round rodent trapping archive (`10.6084/m9.figshare.18295520.v1`) covered eight 7×7 grids with 6.25 m trap spacing from August 2015 to July 2016. Chock et al. (2022) analysed six sympatric species and surveyed trapping stations multiple times per night. A subsequent frozen, source-checksummed ecological analysis in the NEON research repository compared eligible adjacent-season pairs, with each tagged animal observed across both seasons removed from both. The primary response was exact **species × trap station** recurrence, standardized against a null fixing season-A labels and season-B species occupancies and trap richness (fixed-fixed). A site-independent check treated the six *physical grids* as the independent sign-flip units rather than 10 seasonal comparisons. The previously opened San Jacinto result was the inspiration for, not a previously independent confirmatory test of, the NEON study below.

### NEON archival study universe

We used the unchanged NEON RELEASE-2026 archive, product DP1.10072.001 (box trapping), spanning April 2015 to September 2026. Source manifests, 1,773 `mam_perplotnight` and 1,707 `mam_pertrapnight` source files were checked against original reported file size and MD5. Exactly completed, protocol-compliant three-night sessions were considered from canonical 10×10 plots, while known nonstandard site SRER was excluded from the primary. Each nightly trap configuration needed >=90 distinct valid station codes. We selected one earliest valid bout for each site×plot×meteorological season-year combination, before opening recurrence outcomes. Only adjacent meteorological seasons were linked, not arbitrarily distant observed bouts.

One event comprised exactly three distinct original night IDs and complete NEON plot metadata; start and end dates had to lie within a four-day window and entirely in one season. The genus taxonomy came from the official NEON target-taxon lookup. This genus-level endpoint retains taxonomically ambiguous Peromyscus species and species-group records as Peromyscus, without treating field identification as a genetically verified species. Captures had to carry a consistent `site×plot×tagID` identity; histories with genus conflicts or impossible same-night multi-station records were dropped. We did not infer true individual uniqueness beyond published tags.

A pair of seasons was eligible if at least three shared target genera each supplied >=2 **season-exclusive individuals** and >=2 distinct occupied stations in each season. For every pair we removed individuals whose tags were seen in both seasons, from **both seasons**, before building the genus×trap matrices. The minimum replication rule required at least 20 qualifying seasonal comparisons across eight independent physical sites. We froze this structural rule and completed a predictor/effort-only source audit before computing any actual genus×trap recurrence effects.

### Cross-season null hypothesis and response

For each qualifying season pair u, the observed statistic counted exact same-genus/same-trap cells shared between season A and season B, `O_u = sum(A[g,t] * B[g,t])`. Each fixed season-A genus×station matrix was compared with 2,000 season-B fixed-fixed randomizations. A constrained 2×2 swap preserved every genus's number of occupied trap positions in season B and every trap's season-B genus richness. The same originally observed trap sites, edges, effort-verified sessions, identity exclusions and taxonomic classes were retained. The null therefore accounts for generic station hotspots and genus prevalence but does not guarantee control of genus-specific habitat or detection differences.

The algorithm used 1,000 accepted burn-in swaps, 40 accepted constrained swaps between stored draws, seed 2026101901, and a fixed swap-proposal cap. Null chains were considered informative only when the sampled overlap variance was nonzero and lag-one effective sample size approximations exceeded 200. We standardised each observed recurrence relative to its own fixed-fixed null to produce Z_u.

### Geographic primary inference

Multiple seasons in one NEON site were not treated as independent geographic replicates. We computed a site mean of the Z_u values from each site and tested the grand mean of *physical-site means* against zero. The precommitted one-sided alternative was positive. For <=18 informative physical sites, we enumerated all sign flips exactly (rather than drawing 2,000 site permutations). Ecological support required >=8 informative sites, a positive mean site Z, and exact one-sided p<0.05. The primary test did not select only positive genera, habitats, regions or seasonal pairs. Separate null-model and site-significance criteria were frozen before NEON recurrence outcomes were calculated.

### Scope exclusions

This model was deliberately *not* the earlier density-associated within-animal W versus among-individual centroid B hypothesis. It does not use abundance-conditioned F/C/U regression, any of its 948 species-labelled *Peromyscus* candidate sessions, or the external MOSA animal-identity archive as an effect source. Results from the earlier failed multigenus density hypothesis remain failed.

## Results

### San Jacinto: recurrence among different observed individuals

The existing frozen San Jacinto source test retained 10 informative consecutive seasonal comparisons over six physical 7×7 grids. Species-level standardized recurrence exceeded its fixed-fixed season-B null in 9 of the 10 comparisons, and five grids had positive mean Z. The mean unit Z was 1.775; the exact physical-grid sign-flip test yielded a one-sided p=0.046875. These results were *known* when the independent NEON test was planned. This dataset did not include a geographically independent 14-site network, and species-level San Jacinto Z magnitudes should not be numerically pooled with NEON's genus-level Z.

### NEON: source eligibility and individual-overlap exclusions

The outcome-blind historical source audit initially identified 2,757 canonical, completed three-night candidate sessions, from which one bout per eligible site×plot×season-year was selected. The source-supported study included 58 consecutive-season pair units across **30 plots at 14 physical NEON sites**, spanning ten distinct combinations of adjacent calendar seasons. The original frozen genus-richness distribution was 47 units with three eligible genera, nine with four, and two with five. A total of 3,607 shared-tag occurrences were excluded across the source-level adjacent-season candidate-pair audit; because the same animals and dates can occur in multiple candidate pairs, this is **not a count of 3,607 unique animals removed from the 58 final units**.

The original eligibility requirements of at least 20 pairs and at least eight sites passed *before* any ecological recurrence statistic was calculated.

### NEON: positive genus-associated spatial recurrence

All **58 of 58** eligible pair units supported nondegenerate fixed-fixed null randomizations and passed the fixed mixing diagnostic. The standardized recurrence Z values were positive in **42 of 58** seasonal units. After aggregation to physical sites, **11 of 14** site means were positive. The mean site Z was **+0.800742**, with median **+0.529616**. The exact one-sided physical-site sign-flip test, enumerating 16,384 sign combinations, gave **p=0.001159668**. Thus all three frozen primary gates were met: adequate independent geographic support, a positive mean standardized recurrence, and p<0.05 under the specified site-blocked sign-flip test.

The site mean estimates varied substantially (range −0.2204 to +2.7170); three sites showed slightly negative means, and the positive effect should not be described as universal across sites or genera. The lowest recorded fixed-fixed lag-one effective draw count was approximately 1,294 (above the 200 minimum). Two different randomization samples do not create different ecological sites; this quality diagnostic concerns Monte Carlo stability only.

### Contrasts with previously failed density hypotheses

The original NEON development analysis suggested a positive pooled between-minus-within spatial variance response to genus-level known-alive abundance, but its frozen six-of-eight-genus generality requirement **failed** (only five positive genera). Its subsequent provisional *Peromyscus* time-heldout positive-sign prediction was not replicated and was too imprecise to prove reversal; the five-genus follow-up was not estimable. A separate congeneric-versus-conspecific fixed-total source assessment found zero literal same-season equal-N/U comparisons under conservative taxonomic uncertainty, despite predictor rank-two mathematical feasibility. The current lineage-specific recurrence result tests **a different ecological question** and does not rehabilitate those original density hypotheses.

## Discussion

### Spatial structure can recur even when sampled individuals do not

Across the two independent sources, the observed seasonal distribution of trapping locations carries recognizable taxonomic structure after the individuals encountered in adjacent seasons have been forced to be disjoint in the analysis. In NEON, 14 geographically independent sites and an explicit preservation of season-B genus and trap occupancy yielded positive average genus-specific recurrence. At the observational scale of fixed live traps, the data show that changes in which individuals were trapped do **not necessarily erase** the spatial signature of a mammal lineage.

The word *turnover* here means **nonoverlapping observed tagged-animal sets in the compared season samples**. Excluding repeated tag IDs does not directly measure mortality, birth, immigration, emigration, unobserved persistence, or the fraction of truly distinct unmarked animals. We cannot infer that every individual biologically died or was replaced. A more accurate formulation is that the spatial pattern persists **across different captured/tagged individuals**, not that demographic population replacement was fully established.

### Why this is a genuine ecological pattern, but not a demonstrated mechanism

The fixed-fixed null controls important banal explanations: if one genus occupies many positions, or if some traps have a high overall number of captured genera, those properties are preserved in randomized season B. A positive observed advantage therefore represents **consistent genus-associated trap-position placement across seasonal observations, beyond these margins**.

But the residual pattern may still emerge from a persistent microhabitat template, differential detection or trapping affinity, historical colonization/recruitment, behavioural decisions, biotic interactions, or stable trap-specific conditions. No local vegetation/soil or lineage-specific detection estimates were jointly included here. Accordingly, *habitat filtering* is a credible possible explanation and *competition* is neither demonstrated nor ruled out. No data here show individual territorial interactions, inter-animal avoidance or causal succession into vacated territories.

### Novelty relative to previous rodent and temporal-niche studies

Prior studies clearly predate ours in documenting spatial niche partitioning and temporal stability. Thinsp and Price (1997) reported seasonally stable segregation and associations with habitat between two *Dipodomys* species. Chock et al. (2022) quantified fixed-fixed co-occurrence patterns and habitat associations among six sympatric rodents in the very source community used for our San Jacinto reanalysis. The distinct contribution of the present programme is **the explicitly individual-disjoint adjacent-season recurrence endpoint** and its **independent replication at genus level across 14 spatially separate standardized NEON sites, with site-block inference and a trap-richness-preserving null**. This is a broader observation of repeatable taxon-associated spatial sorting—not the first appearance of stable rodent distributions, fixed-fixed null models or ecological site fidelity.

### What remains uncertain and what would constitute a mechanism test

Different data products and taxonomic units are a substantive limitation, not merely a footnote. The San Jacinto null used species on 7×7 traps checked multiple times per night; NEON used genera on 10×10 traps, with three-night bouts and substantial cryptic-species uncertainty. Pooling the two p-values or standardized Zs would create a misleading common effect. Resolving species identity where possible in new NEON data, externally calibrating capture propensity, and linking explicit local habitat conditions to trap positions would distinguish persistent abiotic filters from an active interaction mechanism. Such explanatory moderators must be prospectively specified as a different analysis, not selected after discovering the positive source result.

Another potential concern is local geographic clustering or unmeasured environmental similarity among NEON sites. Although the test treats NEON physical sites rather than seasonal events as geographic units, 14 sites are not 14 independent experimental manipulations. An independently reviewed spatial/environmental replication design would strengthen claims of generality. The open ecological result itself should be reproduced from published source artifacts by independent code review before submitting a high-impact manuscript.

## Conclusion

Seasonal changes in the observed identities of trapped mammals do not erase their genus-associated trap-location patterns. In independent NEON sites, **observed genus × trap recurrence among different tagged animals exceeded a fixed-fixed seasonal null**, with positive site means in 11 of 14 sites and a preregistered exact site-blocked p=0.001160. Together with the independently opened species-level San Jacinto result, the data support the *pattern* that local spatial niche signatures can be re-established by different captured animals. They do not identify the causal filtering or competition processes generating that consistency.

## Figures planned with grounded sources

**Figure 1:** conceptual contrast between persistence of a single animal's trap location and recurrence of the same lineage's trap location with different tagged animals. Requires labelled schematic of simulated examples only; must not look like real observed tag trajectories.

**Figure 2:** 14 sorted NEON independent physical-site mean standardized Z values (from source receipt, anonymized geographic labels), indicating the zero-null axis, 11 positive and 3 negative site means; note physical site, not 58 unit independence. Same panel may show site mean +0.801 and exact p=0.001160. This can be generated from the existing machine-readable receipt without downloading any animal-level coordinates.

**Figure 3:** independent source triangulation: San Jacinto species-level six physical grids, 10 seasonal pairs, exact p=0.046875, and NEON genus-level 14 physical sites, 58 pairs, p=0.001160. Different units and null contrasts: do not overlay standardized effect distributions as though directly equivalent or combine p-values.

## Key source-based references

- Thinsp, R. L. G. & Price, M. V. (1997). Influence of season and a sympatric congener on habitat use by Stephens' kangaroo rat. *Conservation Biology* 11, 708–717. https://doi.org/10.1046/j.1523-1739.1997.95480.x
- Chock, R. Y. et al. (2022). Niche partitioning in an assemblage of granivorous rodents, and the challenge of community-level conservation. *Oecologia* 198, 553–565. https://doi.org/10.1007/s00442-021-05104-5
- San Jacinto original open data: https://doi.org/10.6084/m9.figshare.18295520.v1
- NEON original release product: https://data.neonscience.org/data-products/DP1.10072.001
- NEON small mammal box trapping: https://www.neonscience.org/data-collection/small-mammals

## Immutable analytical source trail

1. `results/san_jacinto_cross_season_turnover_v1.json` on the dedicated `ecology/san-jacinto-transition-niche-v1` branch: independent source analysis from Figshare.
2. `docs/NEON_CROSS_SEASON_GENUS_SPATIAL_TEMPLATE_DESIGN_20261019.md`: frozen hypothesis, support thresholds, randomization and site-level inference **before NEON outcome**.
3. `results/neon_crossseason_genus_template_support_receipt_20261019.json`: successful **58 pairs, 14 sites** outcome-blind source eligibility.
4. `results/neon_crossseason_genus_template_ecology_receipt_20261019.json`: all 58 null results and exact 14-site p-value from GitHub Actions 39208798076.
5. `analysis/neon_crossseason_template_null_v1.py`, `analysis/run_neon_crossseason_genus_template_ecology_v1.py` and `tests/test_neon_crossseason_template_null_v1.py`: frozen code and synthetic source-free validation.

**Explicit submission hold:** publication readiness requires numerical source-to-figure verification, independent null-implementation review, site-influence disclosure and transparent habitat/detection limitations. No post-result change to the NEON endpoint is permitted. The previous density/W/B manuscript is a separate **negative generality / imprecise replication** programme, not part of this positive article's validation.
