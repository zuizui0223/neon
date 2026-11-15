# Independent vole seasonal capture-centroid shift: pre-outcome freeze (2026-11-15)

Existing NEON PR #23 only. This is a retrospective external 2021 bank-vole field system with already published behavioural outcomes; it cannot be called novel confirmation or a methods paper.

## Prior art and exact source
Mistrick et al. 2024 JAE DOI 10.1111/1365-2656.14067 already demonstrated food supplementation shrinks capture-derived seasonal space use, deworming expands it in autumn, and observed spatial overlap is broadly similar despite density changes. This is established mammal ecology, not our discovery.
Source GitHub jmistrick/vole-spatial-manuscript immutable commit 47dc1e9b1f83ec2faaf7ba232e02e00f9e4cffb4; capture CSV original Git blob 343de8c3846eea21d3f0648358e159bd61bb87a2; codebook site_trts.csv blob b4059f818650ce844472a80f6caf38eee65bfffe. Published Zenodo DOI 10.5281/zenodo.10603001.

## Effect-blind original source census
Without inspecting capture x/y spatial outcome, counted 2,012 June-October 2021 capture rows at 12 distinct Finland forest sites, 742 site×tag individuals, 905 summer and 1,107 autumn records. 120 individuals captured in both seasons, and exactly 51 individuals with >=2 capture rows EACH summer and autumn. Four factorial groups each have 3 original physical sites: fed/control 16 individuals; fed/deworm 12; unfed/control 15; unfed/deworm 8. Original site×tag is the individual key and group assignments are frozen prior to spatial outcome. Do not select source individuals by centroid displacement.

## Prespecified seasonal location response
For all 51 source-eligible individuals, calculate seasonal arithmetic mean of original source trap coordinates (x,y, local grid units). Primary observed outcome d_i is Euclidean distance between summer and fall CENTROIDS OF OBSERVED CAPTURES. It is NOT trajectory length, telemetry or true niche use. Require finite x/y, unique stable coordinates per site×trap name across all original source records, exact original source census/counts and 12 site factorial balance or STOP before outcome.

Fixed sampling baseline per individual: pool that same individual's original captured x/y records; randomly reassign all records into seasonal partitions with EXACT observed summer and fall sample counts, 2000 independent reproducible within-individual permutations, no re-selection of tags or stations. Define D_i = observed centroid shift minus mean permutation shift. Permutation represents a fixed captured-location distribution with finite counts, not a hypothesis about unobserved true movement or season-specific detector effort.

Primary plot/site-equal D: average within site, then average the 12 ORIGINAL site means equally. Report individual observed distances, null expectation and D summaries ONLY as aggregate; no animal tags/positions exported. Fixed stratified 5000 whole-site bootstrap by separately resampling the 3 sites WITHIN each factorial treatment cell, preserving their original individuals, yielding a descriptive percentile 95% CI. No p-values or post-hoc positive threshold.

Two fixed mechanistic contrasts at site mean level, both included regardless of direction:
- food: fed minus unfed, predicted negative in excess centroid displacement;
- helminth removal: deworm minus control, predicted positive.
Also report four factorial cell means and the number of individuals whose observed d_i exceeds the 97.5% point of the personal permutation distance distribution (descriptive secondary). Never switch metrics to rescue a non-support outcome. Interaction is not promoted to a third hypothesis. CIs and effects are descriptive/retrospective and not randomized movement treatment estimates, especially with 3 sites per group.

## Source gate and scientific boundaries
Eligible only if exact original 2012 rows / 742 individuals / 120 both seasons / 51 with >=2 each / 12 sites / 3 per factorial cell reproduce and coords pass original site×trap identity. If any failure, source STOP before publishing an ecological effect. No re-opening old NEON, Portal or Structural responses; no new preferred species/site/year. Original authors already investigated season, space use, treatment and density. A new centroid D would be a *different observational question*, not evidence that food or deworming is independently causing latent niche movement.

NEON (14 physical sites, corrected Z +0.795) remains a conditional genus×capture-station pattern; Portal reference-conditioned exact-stake recurrence after disjoint IDs was non-support; Structural 529 ultrarare island mapped labels are not observed colonization. These distinct endpoints cannot be pooled. Keep one unified NEON manuscript draft / submission HOLD.

Original research: https://doi.org/10.1111/1365-2656.14067
Original code: https://github.com/jmistrick/vole-spatial-manuscript


## Post-STOP response-blind source codebook correction (2026-11-15)

The first actual run stopped BEFORE computing any original seasonal x/y effect at the source cardinality check. Source-only inspection of the exact pinned 2024 Git files confirmed **13 original treatment-codebook site rows, of which exactly 12 are represented in the 2,012 recorded 2021 captures**. The thirteenth lookup site has no original 2021 captures; its treatment was never used in individual selection. The initial code incorrectly asserted 12 treatment rows. The correction accepts 13 metadata rows while still requiring 12 actually sampled sites, 742 unique captured animals, 120 observed in both seasons, 51 with >=2 records in both seasons, and three actual replicated sampled sites per each of four factorial groups. It does not change the frozen source sample, seasonal centroid definition, within-animal permutation, contrasts, statistical thresholds or old ecological results. Any further source mismatch STOPs.
