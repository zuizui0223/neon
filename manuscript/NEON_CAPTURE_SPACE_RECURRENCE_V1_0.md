# Seasonal recurrence of genus-associated capture locations among nonshared small-mammal tags

**Focused working draft V1.0 | 25 November 2026 | DRAFT / SUBMISSION HOLD**

This reorganizes the existing evidence, not the underlying tests, of [V0.9](NEON_SPATIAL_MACROECOLOGY_UNIFIED_V0_9.md). It is not a submission-ready or independently replicated manuscript. [Source-linked evidence ledger](../results/neon_core_ecological_evidence_20261125.json).

## Abstract

Community composition and the identities of observed animals can change on different timescales. We asked whether genus-associated capture locations recur across consecutive seasons even when marked animals observed in both seasons are excluded. Using NEON RELEASE-2026 small-mammal trapping, the original stringent set comprised 58 adjacent-season comparisons with at least three eligible genera at 14 physical sites. A corrected fixed-margin sampler yielded site-equal standardized recurrence Z=0.795 (11/14 positive sites); removal of whole sites with reused source seasons retained 46 comparisons at 12 sites (Z=0.843). In an exploratory same-release extension to exactly two eligible genera, 150 informative comparisons from 158 pairs at 30 sites showed Z=0.615 (25/30 positive); 71 comparisons in 17 geographically nonoverlapping sites were also positive (Z=0.760; 15/17). Matching positions recorded on all six nights retained the result. Evidence beyond exact stations at 10-m neighbors did not survive the source-reuse sensitivity; observed count-rank reversals failed the prespecified subgroup criterion. Re-encounter heterogeneity and incomplete verification of trap operation constrain interpretation. Thus genus-associated nominal capture locations recur conditionally among nonshared observed tag sets. This does not establish actual demographic replacement, spatial niche invariance, density-independent habitat use or causal coexistence.

## Introduction

Individual space use, taxon distributions and community spatial organization are distinct ecological levels. The persistence of a taxon within a whole plot does not establish that particular positions used by that taxon recur among different animals. Conversely, recurrent capture positions do not necessarily indicate habitat choice. Persistent microhabitat, detector response and unobserved survivors may all contribute.

The question is whether genus labels recur at particular nominal capture positions after conditioning on observed genus station totals and station genus richness, and after excluding every shared observed tag from both seasons. A broader spatial patch hypothesis additionally predicts recurrence at adjacent positions beyond exact matches. A separate rank-reversal hypothesis asks whether recurrence is demonstrable even when relative observed captured numbers switch. Neither extension follows automatically from the main effect. Seasonal dominance changes, density-associated space use and spatial niche partitioning are established ecological topics, not our novelty. A targeted literature comparison confirms that station-scale spatial segregation (Chock et al. 2022, doi:10.1007/s00442-021-05104-5), continental NEON individual space-use analysis (O'Fallon et al. 2025, doi:10.1007/s00442-025-05731-2), and seasonal community changes along forest disturbance gradients (Pruvot et al. 2024, doi:10.1016/j.oneear.2023.11.003) are already established. The narrower contribution concerns cross-season station-label recurrence among nonshared observed tags conditional on sampling margins. This targeted review does not establish priority or a causal mechanism. [Literature boundary and independent source](../docs/NEON_CAPTURE_SPACE_LITERATURE_AND_INDEPENDENT_SOURCE_20261125.md).

## Methods

NEON DP1.10072.001 RELEASE-2026, April 2015–September 2026. Original reconstruction used 3,547 manifest entries and 3,480 selected checksum-verified files, 21,363 plot-night records and 1,505,827 trap-night rows. Original completed three-night event gate, nominal 10×10 grid and >=90 canonical recorded station positions per night; first selected event per meteorological season under the frozen rule. Exclude ambiguous same-night multi-coordinate events and conflicting genus histories. For adjacent seasons on a grid, remove all shared observed tags from both sets; eligible genera require at least two exclusive tags and two stations per season. This does not prove actual population replacement. The original >=3-genus cohort and exploratory exact-two source extension are disjoint seasonal comparisons but geographically overlap. Their union is 31 physical sites and 15 domains, not 31 independent replications.

Let A and B be binary genus-by-station occupancy matrices from the exclusive observed tag sets. Compare their same-genus same-position overlap against the conditional null holding A and B's genus-row and station-richness-column margins fixed (A fixed in its entirety). Standardize by conditional mean and SD. Three-plus rows use the corrected lazy symmetric proposal clock, counting failed proposals and holds (two chains per unit, 2,000 retained draws each, 10,000 burn proposals, 100 proposals between retained draws). Earlier accepted-only sampling did not have the required uniform stationary weights. Two rows use exact enumeration of allocations of singleton columns. Zero-variance comparisons remain counted in support but do not yield Z.

Equal-site averaging, and conditional product and rank-comonotone within-site marginal null simulations. The latter is a dependence stress, not a universal bound. Exclude whole sites containing reused source seasons in the specified sensitivity; remaining ecological dependence is not ruled out. All post-original-result subgroup analyses are exploratory.

For 10-m rook neighbors, also condition on observed exact same-genus overlap. For capture-count ranks, require non-tied orders of the two original genera to agree before and after removing shared tags in both seasons. Strict reversal requires opposite orders in the two seasons; all ties/disagreements are separately retained in the roster. Predeclared reversal criteria: >=20 informative pairs/8 sites, and >=12/6 in whole-site reuse exclusion; positive site mean Z, >=75% positive sites and rank-coupled conditional p<.05 in both. Retained rank is context, no direct difference test.

Restrict separately to positions recorded on all six nights and audit explicit 4/5/6 trapStatus operability. Within-bout Microtus/Peromyscus first-night re-encounter is a distinct observed outcome, not detection or survival probability. No pooling of independent mechanisms or unrelated datasets.

## Results

### Exact nominal stations recur conditionally

| Subset / distinct endpoint | Pairs | Sites | Mean Z | Positive sites | Conditional rank-coupled p | Disposition |
|---|---:|---:|---:|---:|---:|---|
| >=3 genera | 58 | 14 | 0.795 | 11/14 | 0.00125 | CONDITIONAL_POSITIVE |
| >=3 genera, whole reused-season sites removed | 46 | 12 | 0.843 | 10/12 | 0.00210 | CONDITIONAL_POSITIVE |
| exactly two eligible genera | 150 | 30 | 0.615 | 25/30 | 0.00015 | EXPLORATORY_POSITIVE |
| two genera, whole reused-season sites removed | 48 | 17 | 0.698 | — | 0.00125 | EXPLORATORY_POSITIVE |
| sites outside original 14 | 71 | 17 | 0.760 | 15/17 | 0.00060 | EXPLORATORY_GEOGRAPHIC_SENSITIVITY |
| new sites, whole reused-season sites removed | 16 | 9 | — | — | — | STOP_INSUFFICIENT_SUPPORT |
| positions recorded all six nights | 150 | 30 | 0.611 | 25/30 | 0.00010 | EXPLORATORY_POSITIVE |
| common recorded positions, reused-season sites removed | 48 | 17 | 0.692 | — | 0.00110 | EXPLORATORY_POSITIVE |
| original two-genus source | 153 | 30 | 0.310 | 22/30 | 0.03915 | EXPLORATORY_FULL_SAMPLE_POSITIVE |
| whole reused-season sites removed | 50 | 17 | 0.183 | — | 0.22054 | NONSUPPORT_STRICT_SENSITIVITY |
| strict observed count rank retained | 81 | 28 | 0.552 | 22/28 | 0.00095 | EXPLORATORY_POSITIVE_SUBGROUP_CONTEXT |
| strict observed count rank reversed | 27 | 16 | 0.351 | 11/16 | 0.07500 | NONSUPPORT_FROZEN_CRITERION |
| rank reversal, reused-season sites removed | 6 | 4 | — | — | — | STOP_INSUFFICIENT_SUPPORT |

Dashes denote unrecorded or unestimated values, not zero. No pooled p-value or independent ecological replication. The neighbor estimand differs from exact-station recurrence.

### Observation opportunity, scale and relative captured numbers

Matching the 93–100 positions recorded on all six nights (median 100) retained the same 150 informative pairs and near-identical Z=0.611. However, median all-six-night explicitly operable positions were only 60. Only 18 of 158 pairs at eight sites met the 90-operable-position and genus-support gate, so no fully operability-verified effect was opened. At seven matched sites, 97/179 first-night Microtus and 330/435 Peromyscus tag histories reappeared on nights 2–3 (pooled 54.2% versus 75.9%). Site-equal difference −23.5 percentage points, descriptive site bootstrap interval −45.7 to −2.4 points. The causal source of that difference and any link to recurrence are unidentified.

The conditional neighboring-station effect was not robust to whole-site reuse exclusion (Z=0.183, p=.221). In the count-rank audit, 84 source pairs retained ranks, 27 reversed, and 47 had ties/disagreement. Reversal subgroup Z=0.351, 11/16 positive, rank-coupled p=.075; six pairs/four sites after reuse exclusion, below threshold. Both full-sample directional gates fail. Retained ranks showed Z=.552, 22/28 positive. Excess exact station matches per B genus-by-station cell was +2.30 points in reversal and +1.95 points in retained rank. Differences in standardized effects and significance labels cannot establish a difference in biological effects. No direct subgroup difference or equivalence test was performed.

### Candidate mechanisms remain unresolved

The historical density generality rule failed (five of eight genera, six required; 1,326 sessions/40 sites). Joint recurrence–density opportunity was only 12/58 pairs. Nonidentical-station canopy-affinity test: 20 comparisons/eight sites, Z=.481 and descriptive signflip p=.207, nonsupport. Temperature and seedfall–pregnancy linkages stopped for source support. Direct reproductive contrasts had three eligible comparisons at two sites, no replicated species-pair transfer. These are distinct nonsupport and estimability boundaries, not proof that these processes are irrelevant.

A separate Portal analysis (436 species/plot-year pairs, 20 plots within one landscape) found plot-equal excess exact-stake collision of −0.000064 against the species-blind observed station reference, descriptive bootstrap interval −0.001547 to +0.001401. Its timing, grain and null differ; neither independent confirmation nor a direct refutation of NEON. The other external seed-fate and vole investigations are archived context, not direct tests of the NEON mechanism.

## Discussion

The supported pattern concerns the organization of recorded taxon labels, not merely their marginal abundance: genus-associated capture locations recur beyond the fixed-margin expectation when shared observed tags are removed. It appears across the observed geographical source union. The strongest evidence is restricted to exact nominal stations. Neither the failure of adjacent-station extension nor the rank-reversal nonsupport proves an ecological discontinuity or a causal change in spatial organization.

Persistent fine-scale habitat features could lead different animals of a taxon to similar positions. Persistent genus-specific capture propensity, access to bait, surviving undetected individuals and unresolved tag history may instead explain capture signatures. Both classes of processes could operate. Recorded station presence is not operation, and repeated captures are not an independent measurement of latent space use. Removing shared recorded tags cannot demonstrate demographic turnover. Thus the pattern is a substantive empirical capture-space result but cannot identify resource competition, niche invariance or coexistence.

A decisive next test must use a separately frozen independent cohort with independently measured station-level observation opportunity and contemporaneous habitat or resource data, ideally with synchronized independent animal observations at the same spatial positions. It must distinguish transfer of a latent-use prediction from transfer of detector-specific capture association. Further same-release subgroup analysis cannot replace that validation. This is a research requirement, not a result or a promise that suitable data are available.

## Figure and supplement plan

Four figures: source and paired-season design; primary corrected and exact-two site-level distributions including negative sites; scale and rank boundaries in distinct panels; trap operability and re-encounter limits. Existing source-backed [exact-two distribution](figures/neon_exact_two_genus_site_means_20261025.svg), [operability](figures/neon_6night_trapStatus456_operability_source_20261026.svg), and [re-encounter](figures/neon_firstnight_microtus_peromyscus_reencounter_20261026.svg) may be reused. No new figure claimed here. The full V0.9 archive and source-ledger preserve failed, stopped and positive endpoints; no selective deletion.

## Reproducibility

NEON source https://data.neonscience.org/data-products/DP1.10072.001. [Evidence ledger](../results/neon_core_ecological_evidence_20261125.json) points to the original numerical receipts. [Latest rank analysis](https://github.com/zuizui0223/neon/actions/runs/45536108603) and [closure](../docs/NEON_OBSERVED_RANK_REVERSAL_RECURRENCE_RESULT_20261125.md). Older corrections and prior-art record remain in V0.9. No new data fit, submission, merge or communication. Literature synthesis and independent validation remain outstanding; DRAFT / SUBMISSION HOLD.
