# Spatial persistence and population reorganization across small-mammal assemblages
## Unified macroecological manuscript v0.3 — 25 October 2026

**Working manuscript — NOT SUBMITTED.** This is ONE ecological paper concept integrating previously separated seasonal recurrence and abundance-related spatial-allocation evidence. It is a reorganization of **already inspected** NEON RELEASE-2026 results, not a new prospective confirmation or a pooled meta-analysis of incompatible endpoints. The new cross-population coupling question remains an explicit **untested hypothesis**. The paper is not ready for journal submission.

**Scientific focus:** Under what landscape and population conditions do recognizable taxon-associated spatial configurations persist despite changing observed individuals and local density? The geographic unit is the **physical NEON site**; seasonal comparisons and trap rows are nested observations, not independent sites.

## Abstract — provisional, appropriately bounded

Animal community spatial organization could persist across seasons even when the same marked animals are not detected again. We tested **genus-associated recurrence at exactly the same fixed trap stations**, conditional on seasonal genus station totals and station genus richness, after removing every shared observed animal tag from both compared seasons. Using checksum-verified NEON RELEASE-2026 small-mammal box-trapping observations, the original stringent ≥3-genus analysis comprised **58 adjacent-season comparisons at 14 physical sites**. A corrected uniform fixed-margin sampler produced an equal-site mean standardized recurrence **Z=+0.795**, positive at **11/14** sites. Removing entire source-defined season-reuse sites retained 46 comparisons at 12 sites, **Z=+0.843**. A *newly locked, post-result exploratory* analysis of a disjoint **exactly-two eligible-genera** seasonal group reconstructed **158** further seasonal pairs at **30 sites across 15 ecological domains**. Its two-row null was calculated **exactly**, by multivariate hypergeometric enumeration of all uniform fixed-margin trap matrices, rather than approximated by MCMC. **150/158** units had nondegenerate exact null variance, and the equal-site mean recurrence was **+0.615**, with **25/30** site means positive. A site-weighted 20,000-draw rank-comonotone within-site dependence sensitivity yielded conditional p=**0.000150**; excluding all source-season-reuse sites left **48 comparisons/17 physical sites**, Z=**+0.698**, with sensitivity p=**0.001250**. These analyses share the historically inspected source release, partly overlap in geographic sites, and involve distinct two-row versus ≥3-row estimands: their Z or p-values are **not pooled as independent confirmations**, and the dependence stress is not a universal site-joint null. Together, the two disjoint seasonal-comparison cohorts extend observable taxon-to-location recurrence across a source union of **31 physical sites and 15 domains**; this does not prove all 15 domains independently show recurrence. A distinct historical density–space-use development study across 1,326 sessions/40 sites suggested heterogeneous within/among-animal responses but **failed** its original 6/8 genus generality rule (5/8 positive). An exact same-population crosswalk recovered only 12 of the 58 stringent seasonal comparisons with repeat-supported W/B opportunities, precluding an adequate joint population mechanism test. The consolidated ecology evidence therefore supports conditional **spatial taxon signature recurrence among different *detected tags*** while leaving persistent microhabitat, lineage-specific capture propensity, true demographic turnover, and ecological interactions unresolved. Independent prospective environmental and detection-corrected sampling remains necessary for a continental mechanism.

**Keywords:** metacommunity assembly; ecological spatial persistence; population turnover; individual variation; density dependence; mammal macroecology; habitat filtering; catchability; spatial resilience.

## 1. Ecological question: persistence across levels

A community can undergo two different changes: *which animals are detected at a station* and *how those animals distribute observed space use within and among individuals*. Spatial niche partitioning, seasonal stability and density-associated home-range changes are already well known. The question here is not simply whether a given species has a preferred habitat or whether crowding compresses a home range; it is whether recognizable taxon-associated spatial organization endures despite reconfiguration of the constituent sampled population.

We distinguish three nested observational levels:
1. **Observed marked-individual level:** repeated locations of a tag, short-term movement and W (variance of observed positions *within* individuals).
2. **Local population level:** spatial arrangement of observed individual centres (B), relative abundance or genus MNKA, and shifts in their allocation.
3. **Community and landscape level:** season-to-season recurrence of genus-associated station use, independently weighted across physical sites and ultimately compared along environmental gradients.

The hypothesis of **persistence at the community level despite plasticity below it** is biologically interesting because stable ecological organization need not imply the same stationary animals or one universally conserved density response. However, mere juxtaposition of two separate analyses does not demonstrate this cross-level decoupling; matched cohorts and an explicit contrast are required.

### Alternative explanatory processes

- **Persistent habitat/resource template:** repeated genus capture locations can reflect recurring vegetation, shelter, soil/moisture, food or predator exposure.
- **Lineage-dependent capture/detection template:** traps and behaviours can give repeated genus labels even without stable true-use niches. This is not controlled merely by holding trap *overall genus richness* constant.
- **Biotic interactions and crowding:** animal interactions can alter the distribution of individuals within a lineage and where lineages are recorded. The historical fixed-N/U conspecific/congeneric comparison has zero conservative same-season matched substitution pairs, and therefore cannot currently identify the proposed competition mechanism.
- **Source and temporal dependence:** repeated season keys, sampling windows, uneven target taxa and field identification qualifiers can all influence apparent spatial structure.

## 2. Source-backed population and macroecological selection

NEON standardized three-night pathogen-grid bouts provide original tagged-animal histories and nightly trap effort. The original 2026 source census had **1,838** selected complete bouts meeting the effort rule; among them were **803** adjacent-season pair candidates. **216** pairs supported a predeclared *diagnostic* two-genus eligibility rule, and only **58** qualified under the frozen ≥3 shared-genera/two nonshared marked animals/two stations per genus rule at **14 independent sites**. Therefore the spatial-recurrence result cannot be described as 44 or 46 site-level positive ecological estimates, and unqualified sites are not negative-recurrence sites.

The abundance-related spatial-response development dataset sampled **1,326** taxon-event records across **40** physical sites and eight genera, under its different frozen support rules. A subsequent checksum-verified **structural** event crosswalk has now been completed for the originally selected 58 seasonal pairs (not a recomputation of the historical 1,326 W/B event memberships). It yielded just **12 pairs, 8 sites and one genus replicated across ≥2 sites** for same-genus repeat-supported observational opportunities. The original 14-site and 40-site response families still cannot be treated as matched ecological effects or combined into a single p-value.

The independent San Jacinto source comprised six local 7×7 grids within one study area, with a species-rank result in nine of ten positive original season comparisons after removing bridge-tagged animals. It motivated the NEON genus-rank recurrence endpoint. Its sampling and chain calibration remain separate, and its historical p=0.046875 is NOT part of the current corrected continental NEON null result.

The NEON archive uses tagged small-mammal protocols, not telemetry or full home-range delineation. Observed tag disjointness is distinct from direct mortality/birth/migration estimates. Taxonomic labels for NEON's *Peromyscus* species are not DNA validated by the linked historical morphology-based BOLD metadata.

## 3. Methods: two responses, one hierarchy

### 3.1 Community-scale taxon–station recurrence

Use the **already frozen** 58 comparisons across 14 sites. For each pair, season A and B genus×station binary matrices are built after tags present in both seasons have been excluded from BOTH matrices. Overlap is `O = sum_{g,t} A[g,t]B[g,t]`. A corrected fixed-margin Markov sampler randomizes season B while preserving each genus's occupied station total and the number of genera at each station. Contrast `R_u = (O_u-E_0 O_u)/SD_0 O_u` is averaged within each physical site and then with equal site weights. The full 14-site group and prespecified-by-source 12-site exclusion sensitivity are distinct views of the **same ecological outcome**, not independent datasets.

The 2026-10-20 null correction replaced an invalid accepted-only-jump-chain clock with a symmetric proposal-clock that retains failed swaps and holding probabilities; two chains of 2,000 retained draws each were run for every unit. Finite-state target and mixing diagnostics passed. Post-result independent-unit and comonotone rank-coupled scenarios probe, but cannot fully identify, intra-site temporal dependence.


### 3.1b Post-result ecological broadening to exactly two eligible genera

The original pre-effect ≥3-genera support design had already documented **216** adjacent-season comparisons containing ≥2 supported genera, but the original effect study opened only the **58** with ≥3. The **158** exactly-two comparisons are disjoint at the site×plot×season-pair key level from the old 58 and were frozen as an *exploratory historical same-release extension* before their new spatial effect was opened. All original source, genus-level field taxonomy, nightly trap-effort, ≥2 season-exclusive individuals and ≥2 occupied stations per genus in both seasons, and exact shared-tag removal from both matrices remain identical to the old design. Source-only geographical support passed prospectively under the *new* 12-site, 8-domain, 80-pair feasibility threshold: **158 pairs, 30 sites, 15 domains**.

The null for **exactly two genus rows** has an explicit uniform finite distribution. Among season-B stations, columns of genus richness 0 or 2 are fixed; suppose `m` stations have richness exactly 1, with `a` occupied by genus1. All `C(m,a)` equally weighted assignments preserve B genus occupancy and station richness. Holding season A fixed, assign every singleton station weight `A1(t)−A2(t)∈{−1,0,1}` and enumerate the exact distribution of selected weights using the multivariate hypergeometric counts `C(n+,x) C(n−,y) C(n0,a−x−y)/C(m,a)`. This yields the exact overlap mean and variance for each seasonal pair, and Z is standardized by that **exact conditional fixed-margin null**. Brute-force synthetic full-state comparisons and row-label symmetry tests passed before source outcomes. It does not use the historically defective accepted-only-swap chain.

Before calculating any new observed spatial overlap, we checked all exact-null marginal variances. The fixed source eligibility gate required ≥75% informative among all 158 units, ≥40 informative pairs, and ≥8 independent sites. Exactly **150/158** units at **30 sites** passed (8 zero-variance units were retained in denominators but not assigned Z). We then averaged informative pair Z values within each site and sites equally; no genus, year or environmental subgroup was selected by sign. We sampled **20,000** site-equal joint statistics independently from the exact per-pair null marginals, and separately under a strong within-site shared-rank (comonotone) coupling. These are conditional null *scenarios*, not the empirical joint capture mechanism or worst-case bounds over all possible site dependencies. A source-defined **whole-physical-site** exclusion removed every site with any reused site×plot×season key, leaving **17 sites/48 informative pairs**. The exact-two site effects are **not pooled** with earlier 3+-genus site effects or San Jacinto.

### 3.2 Population-scale density accommodation

Use the historical RESPONSE definition, not new fitting after observing the 14-site recurrence result. `W` is within-animal observed positional variance over exact three-night sessions; `B` is the debiased among-animal observed centre dispersion. The historical genus-MNKA predictor and `Delta_beta = beta_B - beta_W` compare associations across levels; fixed temporal and location controls follow the frozen joint model. These are observational proxies, not causal density manipulations, true activity centres or complete animal ranges.

The frozen genus-balanced model had a positive difference but only 5/8 positive genus-specific estimates against the mandatory 6/8 threshold. We report **all eight**, retain negative genera and mark post hoc ecological modes exploratory. No propensity to crowding is established by the mean coefficient alone.

### 3.3 New macroecological linkage, explicitly not yet an outcome

From the same original source and original 58 pairs, link exact three-night source event dates to the structurally eligible marked-animal repeat bouts for the original response taxa; count matched physical sites, plots, seasonal transitions and genera. The result is **support-only**; it cannot by itself replicate the exact historical 1,326 W/B *modeled* sessions, because MNKA variation, response-series eligibility and finalized geometry remain additional requirements.

**Observed source outcome:** only **12 of the 58** frozen pair units had the same original recurrence genus with the target-taxon repeat support required for a within-animal metric in BOTH original three-night seasons, across eight sites and ten plots. Six genera appeared in these potential pairs, but only one was repeated across at least two sites. Therefore the newly declared joint *feasibility* requirement FAILS. No W/B variances or abundance/reoccurrence effect relationships were computed during this audit. A prospective matched effect or a new independent release will require:
- at least eight independent physical sites, 20 exact matched seasonal pairs and three genera replicated over ≥2 sites merely to pass newly specified *feasibility*;
- a genuinely fresh post-2026 response cohort or other independent standardized marked-individual system for confirmatory coupling claims;
- originally sourced time-appropriate covariates and separate observation/detection accounting.

If these gates fail, the ecological question remains unified, but the outcomes are presented as **partly non-overlapping observational scales** rather than falsely fitting a cross-response covariance.

### 3.4 Environmental gradients

The post-result source pilot measured all 150 approved five-anchor CHM points in the original 30 plots. Fourteen plots had nonzero five-anchor CHM range and sixteen were zero at all five measured pixels. This documents source raster heterogeneity, not a mammal habitat preference. E5 alone can miss canopy above another anchor. For a *trap-level* association, the full historic 3,000 station coordinates and their uncertainty, and flight-year match for the original 2015–2026 capture dates, must pass independent source checks. The 2026-10-22 GraphQL–REST equivalence preflight STOP prevents treating all 100 named trap points as verified, and 1-m pixels do not imply 1-m absolute source accuracy.

At a broader **site-level macro** grain, independently measured seasonal climate products may be considered without inventing 100 exact station points, provided temporal matching, source completeness and effort/detection adjustments are frozen before any new confirmatory outcome. Current 14-site effects were already inspected; correlations with those sites' climate would be exploratory only, not fresh evidence. Predeclared macro environmental-effect support is ≥20 independent sites, ≥3 ecological domains and ≥100 non-overlapping eligible season pairs.

## 4. Existing results with their inferential boundaries

### 4.1 Positive community recurrence in original NEON

| Corrected conditional analysis | Original 14 sites | Source-disjoint 12 sites |
|---|---:|---:|
| Seasonal comparisons | 58 | 46 |
| Positive site means | 11 | 10 |
| Equally weighted mean site Z | **+0.794664** | **+0.843162** |
| Product-null p (+1, 100,000 draws; simulation-floor) | 0.000010 | 0.000010 |
| Rank-coupled p (+1, 20,000 draws; not all-joint bound) | 0.001250 | 0.002100 |

This supports conditional repeatability of **genus-associated *observed capture* locations** beyond fixed genus and station margins, despite no shared *detected tag IDs* in the pair. It does not verify true demographic replacement, segregation into exclusive territories or an ecological explanation.


### 4.1b Exploratory spatial recurrence across less genus-rich assemblages

The new, already-inspected RELEASE-2026 *exactly-two-genus* subset contained **158** source-valid seasonal comparisons, with **150** informative under the mathematically exact conditional fixed-margin null. They were distributed across **30 geographically distinct physical sites** (15 ecological domains in the original source metadata). **99/150** unit Z values were positive; after aggregating at the physical-site level, **25/30** site means were positive, and the site-equal grand mean was **+0.614711**. The site mean sign distribution includes **five negative means**, which are retained in the figure and inference.

| Exact-two-genus exploratory conditional analysis | Original 30 sites | Source-defined nonreused 17 sites |
|---|---:|---:|
| Informative seasonal comparisons | **150** | **48** |
| Equal-site mean Z | **+0.614711** | **+0.698352** |
| Product-null Monte Carlo exceedances / 20,000 | 0 | 1 |
| Product-null plus-one p (simulation resolution) | 0.000050 | 0.000100 |
| Within-site rank-coupled exceedances / 20,000 | 2 | 24 |
| Within-site rank-coupled plus-one p | **0.000150** | **0.001250** |

The new two-row marginal null is **exact**, whereas Monte Carlo uncertainty and unverified dependence remain at the site-combination level. These tests are **post-result exploratory**, not independent biological validation of the earlier positive 3+-genus result; the 30-site subset shares the same historical NEON source release, with **13 physical sites occurring in both source subsets** (31 unique sites across either subset). In particular, the geographic union is not 44 independent sites, and standardized values from two versus three-plus taxon rows must not be pooled as a common meta-analytic estimand.

The observed pattern suggests that **taxon-associated seasonal capture-site signatures can recur even in less genus-rich sampled assemblages**, subject to comparable trap configuration and animal identity criteria. Neither local microhabitat preference nor genus-specific detection probability has been separated; an exact hypergeometric station allocation null does *not* remove fixed genus×station catchability effects. The new source-backed visual is [Figure 2B](figures/neon_exact_two_genus_site_means_20261025.svg).

### 4.2 Spatial accommodation is heterogeneous, not a general rule

Genus-balanced historical slopes were `beta_W = -4.395`, `beta_B = +4.977`, `Delta = +9.372` m²/MNKA, but the original **five of eight positive-genus** result failed the required six. Every one of the eight genus estimates must be displayed. Additional post-result exploratory diagnostics suggested different multi-site geometric modes:
- Apparent within-animal compression with relative centre dispersion/maintenance: *Chaetodipus*, *Myodes*, *Peromyscus*.
- Apparent population-footprint compression: *Dipodomys*, *Sigmodon*.
- Unresolved or inconsistent modes: *Microtus*, *Napaeozapus*, *Onychomys*.

These patterns are **post-result descriptions**, not validated behaviour types or evidence that traits, taxonomy or competitive status caused the modes. One-site genera have no independent cross-site replication; *Peromyscus* is particularly heavily sampled and later positive-sign confirmation was imprecise/nonreplicated.

### 4.3 The macro coupling remains an open ecological test

Both observational scales exist in the same broad continental monitoring programme. An original-source structural overlap audit **has now tested** whether the fixed 58 transition pairs have the exact same event, genus and repeated-individual support needed for a future matched W/B response: **12/58 pairs; 8 sites; 6 distinct genera but only one replicated across multiple sites**. Precommitted structural thresholds were 20 pairs, 8 sites and 3 multisite genera; hence **direct joint modeling STOP**. This cannot be interpreted as the exact historical 1,326-session effect crosswalk, a biological null association, or evidence for an ecological trade-off. **The single manuscript now emphasizes geographic selection and environmental heterogeneity across distinct response grains, with new independent cohorts required for cross-level confirmation.**


### 4.4 First full-domain macro selection census (new source-only result, NOT an ecological effect)

The **complete original NEON RELEASE-2026 source** was re-audited on 25 October 2026 without opening new genus×trap recurrence scores, density W/B outcomes, or habitat effects. The original **1,838** effort-valid three-night bouts spanned **45** physical sites. **803** adjacent-season candidate pairs spanned **42** physical sites and **18** ecological domains. Only **58/803 = 7.22%** passed the frozen stringent ≥3-genera, ≥2 nonshared marked individuals and ≥2 stations per genus rules, spanning **14/42** candidate sites and **10/18** candidate domains. The positive 14-site original effect is therefore estimated on a highly selected subset, not all NEON mammal populations.

| Historical source stratum | Candidate season pairs | Strict qualifying pairs | Source eligibility |
|---|---:|---:|---:|
| All 18 candidate domains | 803 | 58 | **7.22%** |
| CORE | 373 | 27 | 7.24% |
| GRADIENT | 430 | 31 | 7.21% |
| Latitude 35–45° N | 481 | 46 | 9.56% |
| Latitude 45–55° N | 145 | 5 | 3.45% |
| Latitude ≥55° N | 8 | 0 | 0% (no supported estimand) |
| Original seasonal starts in 2015 | 71 | 13 | 18.31% |
| Original seasonal starts in 2018 | 141 | 2 | 1.42% |
| Original seasonal starts in 2024 | 89 | 12 | 13.48% |

A complementary descriptive concentration audit gives a **Shannon effective ecological-domain count** of **15.08** in the 803 candidate-pair distribution versus **7.56** in the strict 58-pair distribution — almost **half the effective geographic-domain representation** (ratio 0.501). These are nested seasonal observations, not independent ecosystems or effect samples. The metric does **not** establish any ecological domain's mammal spatial persistence. Source: `analysis/neon_macro_eligibility_concentration_v1.py` and `results/neon_macro_eligibility_concentration_20261025.json`.

Original domain differences are substantial (D06 **13/96**, D10 **12/60**, D11 **9/35**, D15 **9/17**), but D15's nine eligible comparisons arise within only **one physical site**, whereas D06's 13 arise within **three sites**. None of these estimates identifies ecological *recurrence*, climate causation or within-species competition in those domains. The nearly identical CORE and GRADIENT average selection fractions cannot rule out finer site, genus-richness, year or detector selection.

A broader diagnostic two-genus source-support pool (**216** transitions) exists, but is not a newly confirmed ecological result. The site-level spatial-recurrence result remains the corrected 58-pair/14-site finding without post hoc extension. The newly recorded macro finding is the **observational selection bottleneck**: many domains and years do not have an estimable animal-disjoint, multi-genus seasonal effect under the unchanged protocol. Geographic noneligibility must not be treated as zero ecological persistence.

Original direct data: `results/neon_macro_biogeographic_selection_receipt_20261025.json`; reproducible [Actions 40163416566](https://github.com/zuizui0223/neon/actions/runs/40163416566). [Figure 1](figures/neon_unified_macro_domain_selection_v0_1.svg) plots the 18 candidate domains with full denominator and eligible subset. New predictive environmental inference requires a genuinely uninspected cohort, source-matched seasonal climate/biome variables and taxon-specific detection sensitivity.

## 5. Discussion and proposed generality

The pattern established today is **organizational recurrence beyond repeated observation of the same individuals**.


**New empirically tested macro generality (bounded).** The original 14-site taxon signature recurrence is not an isolated consequence of requiring three or more sampled genera: the structurally separate two-genus seasonal comparisons yielded concordant positive average site effects at 30 physical sites and covered five additional ecological domains relative to the original ≥3 genus cohort. The underlying observational population and station identities are not verified as independent across the *two* analyses; therefore this is **greater geographic coverage and stronger within-release exploratory consistency, not independent prospective replication**. The two-row exact null also eliminates a specific computational uncertainty at that taxonomic richness; it cannot eliminate systematic genus-dependent trap propensity or persistent habitat fields.

 The historical density component does not establish a complementary conserved law: it instead warns that density-associated within-vs-among individual geometry varies among lineages and has observational limitations. This contrast motivates a stronger and genuinely macroecological next question: *Is high-level spatial organization buffered against lower-level population rearrangement, and do environmental heterogeneity and temporal constancy predict the limits of this buffering?*


**Novelty boundary against recent NEON macroecology.** Holian et al. (2026, *Ecology and Evolution*, DOI [10.1002/ece3.73214](https://doi.org/10.1002/ece3.73214)) already examined continental NEON small-mammal **spatial and temporal occupancy–abundance relationships**, including 127 species/40 genera. Brownfield et al. (2025, *Oecologia*, DOI [10.1007/s00442-025-05731-2](https://doi.org/10.1007/s00442-025-05731-2)) analysed density, latitude and habitat effects on deer mouse space use across 36 NEON sites, and Barton et al. (2026, *Ecology and Evolution*, DOI [10.1002/ece3.73413](https://doi.org/10.1002/ece3.73413)) documented North American rodent population synchrony. Our unique current observable is specifically **the same genus recurring at the same trap station between adjacent seasons after excluding all shared observed tag identities, beyond fixed genus/station margins**. This differs from simply recording occupancy through time. Its predictive climate/biome generality remains untested, especially in light of the source eligibility bottleneck.

The key prediction is cross-level, not a generic rediscovery of rodent niche segregation. A valuable **negative** future result would be that apparently persistent taxon signatures disappear when genus-specific detection is measured independently; another would be that few source populations support both nested responses, making direct coupling empirically unidentifiable in the current NEON data. Neither should be hidden by exploratory subgroup selection.

Prior literature establishes separate axes of habitat association (Goldingay & Price 1997; Chock et al. 2022), density and space-use variation (e.g. O'Fallon et al., *Oecologia*, 2025), and continental population synchrony (Barton et al., *Ecology and Evolution*, 2026). Continental coverage of NEON by itself is not novelty. What could be novel is **a genuinely matched ecological test of the stability of taxon-to-place structure versus the plasticity of individual/population space use, with site-level environmental and detection boundaries**.

## 6. Figures in one paper

**Figure 1 — Macro domain support.** [Expanded 18-domain candidate / two-genus / ≥3-genus source figure](figures/neon_macro_two_plus_genus_domain_support_20261025.svg) separates all **803** candidate transitions into the **158 exactly-two**, **58 original ≥3**, and **587** unsupported-by-≥2 seasonal comparison categories. Source eligibility across either qualifying subset spans **216** transitions, **31/42** candidate physical sites and **15/18** candidate ecological domains. The 158 were only subsequently analysed as a post-result exploratory spatial result; geographic ineligibility is not zero ecological recurrence.

**Figure 2 — Community spatial recurrence at two source richness thresholds (separate panels, never pooled).** [Panel A: corrected ≥3-genus 14-/12-site analysis](figures/neon_crossseason_genus_site_means_corrected_v0_3.svg) and [Panel B: exact-two-genus 30-site exploratory analysis](figures/neon_exact_two_genus_site_means_20261025.svg). Both panels include all site signs; different row-richness estimands and overlapping geographic sites preclude pooling site Z or p-values. Whole-site source-reuse sensitivity is separately shown/reported for each cohort. Do not re-use the obsolete accepted-swap plot.

**Figure 3 — Density-associated geometric response diversity.** [All-eight-genus source-backed figure](figures/neon_unified_macro_density_heterogeneity_v0_1.svg) displays each frozen genus `Delta_beta` point estimate, all negative results, site/session replication, and the prominently labelled **FAIL 5/8 < 6/8**. Six multi-site genera have a shared x-axis; two one-site genera are separately listed as exact values to avoid false graphic scale interpretation. No confidence intervals or pooled recurrence/density p-value.

**Future Figure 4 — Direct matched macro analysis.** Not authorized until source crosswalk, independent covariates and independently validated outcomes are available. Omit it rather than invent an association.

## 7. Conclusion

**Established under specified conditional observational nulls:** Genus-associated capture locations can recur across adjacent seasons without requiring observation of the same tagged individuals in both seasons. The original corrected 3+-genus 14-site pattern is complemented by a **new exact-two-genus, post-result exploratory 30-site pattern** that supports the same direction in less genus-rich observed communities without pooling the two effects. **Separately observed:** density response heterogeneity with a failed original generality criterion. **New structural finding:** only 12/58 original seasonal comparisons had same-genus repeat-supported opportunities for direct cross-scale source linking; direct joint ecological inference did not meet its newly fixed sample-support rule. **Not established:** universal density accommodation, a causal or predictive cross-level linkage, a climatic/macroscale mechanism, competition, or habitat-driven recurrence. We proceed as **one** falsifiable macroecological programme, not two successfully validated papers.

## Source and reproducibility links

- **Exactly-two source and exploratory outcome:** `docs/NEON_EXACT_TWO_GENUS_MACRO_EXPANSION_20261025.md`, pre-effect exact-null addendum `docs/NEON_EXACT_TWO_GENUS_EXACT_NULL_ADDENDUM_20261025.md`, `results/neon_exact_two_genus_source_receipt_20261025.json`, `results/neon_exact_two_genus_ecological_receipt_20261025.json`; independently executed [Actions 40166644498](https://github.com/zuizui0223/neon/actions/runs/40166644498). Exact conditional two-row marginal implementation: `analysis/neon_exact_two_row_fixedmargin_v1.py` (full brute-force synthetic distribution QA).
- **Expanded domain support, source-only:** `results/neon_macro_two_plus_genus_coverage_20261025.json` and `manuscript/figures/neon_macro_two_plus_genus_domain_support_20261025.svg`.

- Main unified contract: `docs/NEON_UNIFIED_MACROECOLOGY_20261025.md`.
- Unified factual result ledger: `results/neon_unified_macro_evidence_20261025.json`, builder `analysis/build_neon_unified_macro_evidence_v1.py`.
- Positive corrected NEON evidence: `results/neon_uniform_null_correction_receipt_20261020.json`; `manuscript/NEON_SPATIAL_TEMPLATE_CORRECTION_ADDENDUM_20261020.md`.
- Historical density **failed** generality: `results/multiscale_density_development_result_v1.json`, `results/multiscale_density_heterogeneity_result_v1.json`.
- Complete source support denominator: `results/neon_crossseason_genus_template_support_receipt_20261019.json`.
- Source-only biogeography and eligibility: `results/neon_macro_biogeographic_selection_receipt_20261025.json`, `analysis/neon_macro_site_selection_v1.py`, [Actions 40163416566](https://github.com/zuizui0223/neon/actions/runs/40163416566).
- CHM feasibility only: `results/neon_five_anchor_chm_source_receipt_20261020.json`.
- San Jacinto historical different-rank result: `results/san_jacinto_crossseason_ecological_comparator_receipt_20261019.json`.
- **Completed source-only joint audit:** `results/neon_unified_macro_source_crosswalk_receipt_20261025.json`; `analysis/audit_neon_unified_macro_source_crosswalk_v1.py`; workflow [40162524657](https://github.com/zuizui0223/neon/actions/runs/40162524657). **12/58 same-genus structural matches, eight sites, direct joint STOP.**
- Source NEON DP1.10072.001: https://data.neonscience.org/data-products/DP1.10072.001
- Chock et al. 2022 *Oecologia*: https://doi.org/10.1007/s00442-021-05104-5
- Goldingay & Price 1997 *Conservation Biology*: https://doi.org/10.1046/j.1523-1739.1997.95480.x
- Barton et al. 2026, *Ecology and Evolution*: https://doi.org/10.1002/ece3.73413

**Decision:** one ecology/macroecology manuscript route replaces the planning split described in `docs/NEON_ECOLOGY_TWO_PAPER_DECISION_20261019.md`. Historical frozen tests, decisions, results and drafts are preserved for provenance and cannot be rewritten by this paper strategy.
