# Exactly-two-genus NEON expansion — source-frozen exploratory ecological comparison
**Locked 25 October 2026 after original 3+ genus spatial recurrence was known; BEFORE opening any new exactly-two-genera genus × trap overlap or its randomization outcome.**

## Ecological question, relationship to the unified macro paper

**Question:** Is the seasonally recurring association between mammal *genera* and exact 10×10 trap stations detectable in seasonal comparisons from *less genus-rich* sampled assemblages, where exactly **two** genera satisfy the same nonshared-tag and station-support rules?

The pre-existing original dataset contains **216** season comparisons that pass the >=2 shared-genera *diagnostic* rule, of which **58** passed the original >=3 rule and have already been analysed for recurrence. The new **exactly-two** group therefore consists of **158 distinct eligible pairs** by subtraction. This is a new **post-result, historically overlapping RELEASE-2026 exploratory cohort**, **NOT** new independent biological validation, and never a replacement for the original strict 14-site corrected primary.

**Working hypothesis H+ (qualitative, post-result):** taxonomy-associated trap-use patterns recur across adjacent seasons among different observed tags in exactly-two-genus pairs, beyond season-B fixed genus and trap margins. **H0:** no excess of original same-genus same-station recurrence conditional on these fixed margins. A zero/negative or null result is fully reportable.

## Immutable source and exact two-genus selection

- Original **DP1.10072.001 RELEASE-2026, 2015-04..2026-09**, source checksum verified; 3,547 manifest entries, 1,773 original plot files and 1,707 trap files, source plots 21,363 and trap rows 1,505,827.
- Exact pre-existing 3-night completed standard 10×10 sessions, >=90 distinct valid stations on EACH of 3 nights, earliest source-approved bout per site×plot×season, consecutive meteorological seasons ONLY.
- Same tagged animals in both adjacent seasons removed from BOTH matrices; >=2 season-exclusive marked animals and >=2 occupied trap stations in each season for each qualifying genus. Genus conflict and ambiguous same-night tag-station events excluded identically to the original. 
- **New subcohort = exactly two qualifying genera, no third**. Never mine all 216 with the original 58 combined as if independent. No changes to seasonal window, effort, taxonomic interpretation, trap geometry or animal exclusion. Source-only support must reproduce **158 exactly-two, 58 original 3+, 216 total 2+**, with identical original 58 historical source cohort and all original primary source receipt invariants.
- Record actual number of physical sites and NEON domains, plots, year counts, and season-key reuse *before any new spatial overlap value*. Do not publish specific site/plot names, animal tag IDs or actual trap positions.

## Phase 1 — source-only feasibility (no ecological effects)

Independent source-only metadata and label join should report how many **of the 158** exact-two seasonal comparisons occur in at least **12 physical sites**, **8 ecological domains**, and at least **80** original seasonal units, all *prior* to opening the new recurrence endpoint. If any prerequisite fails, STOP effects and keep the support-only diagnostic. The numeric thresholds are **post-result safeguards**, not the frozen threshold that originally passed with >=3 genera.

Also report seasonal source keys reused among comparisons and the number of *entire physical sites* that must be excluded to remove all source-season reuse in a source-defined sensitivity group. If exclusion removes too many sites (<8), report no clean-site-site inference.

## Phase 2 — conditional fixed-margin observational recurrence (only if phase 1 passes)

The primary statistic is `O_u = sum_{g,t} A[g,t]B[g,t]` with only 2 genus rows `g`, at the **same observed station t**. Use a **corrected lazy symmetric proposal-clock Markov chain** (do not reuse old accepted-only jump chain) on season B, fixing each genus's station occupancy and each trap's genus richness, with season A held fixed. Failed proposals and explicit holding probability count as steps. The 2-row binary matrix finite-state kernel must be verified for row/column margin preservation, symmetric transitions and a uniform stationary target. It need not have the same mixing time as 3+-row matrices.

Two independently seeded chains per unit; 10,000 proposal burn-in each, 100 proposal steps per retained draw, 2,000 retained overlap draws per chain. Use the **same** simulation quality thresholds as corrected 3+ primary: `SD(null)>0`, split-Rhat <1.05, each chain's batch means ESS >=200. Units failing these guards remain in denominators and are reported, never dropped for sign. The strict, **pre-effect** sensitivity decision will only treat the exploratory outcome as analysable if >=40 informative units, >=8 physical sites, and >=75% of the 158 original units pass chain quality. Otherwise STOP with observed source/chain inadequacy (no seasonal ecological claim).

- For supported data, compute Z for each informative pair, then equal-weight within each independent physical NEON site. Report number of positive site means, grand site Z and distribution (including negatives); no genus, habitat or region fishing.
- Draw 20,000 conditional **direct site grand nulls** from the saved per-unit corrected null margins: independent-unit product scenario and within-site comonotone rank coupling, both with site-equal weights. This is a transparency/sensitivity analysis, **not** a mathematically universal bound for the true joint ecological process and not a second independent replication. Original site sign-flip conditional p may be reported as descriptive only, not principal ecological inference.
- Source-reuse sensitivity removes **all pairs from every physical site with a reused site×plot×season key**, based solely on source keys before signs, and recomputes the same conditional null if >=8 sites and >=40 informative original source pairs remain. Otherwise report STOP. Do not select individual favourable pairs.
- Do not compare `Z` magnitudes between 2-row and 3+-row analyses as the same taxonomic richness estimand or pool their p-values. Any cross-cohort direction concordance is **exploratory consistency**, not a common meta-analytic effect.

## Phase 3 — macro domain coverage (descriptive first)

Report candidate/qualified **site/domain coverage** for exactly-two group against all 803 effort-supported source seasonal candidates and the original 58 three-genera subset. All selection ratios are *support*, not ecological recurrence probabilities. Comparing ecological macro gradients or causes needs a separately frozen model and independent new site/season data, including measured genus-dependent detection/capture probabilities.

**Interpretation ceiling:** conditional genus-associated *capture-space* recurrence in an alternate low-richness observational subset of the SAME historical release, if tests pass. No proven demographic replacement, home-range behaviour, competition, canopy filtering, island-like biogeography, or universal continental rule; no reversal of failed original 5/8 density-response criterion. Keep one unified macroecology manuscript, not paper A/B or a new third independent publication.

## Source code and reproducibility priority

Original baseline source inclusion: `analysis/audit_neon_crossseason_genus_support_v1.py` (new optional private exact-two extraction, unchanged original default), source-only runner `analysis/run_neon_two_genus_source_v1.py`; current corrected null inspiration: `analysis/neon_proposal_clock_v2.py`. Distinct new 2-row sampler and effect runner will be added **only after** the source-only gate is verified. Check the returned counts and stop decisions from the real source before any effect opening.
