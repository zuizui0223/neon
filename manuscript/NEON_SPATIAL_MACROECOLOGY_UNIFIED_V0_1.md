# Spatial persistence and population reorganization across small-mammal assemblages
## Unified macroecological manuscript v0.1 — 25 October 2026

**Working manuscript — NOT SUBMITTED.** This is ONE ecological paper concept integrating previously separated seasonal recurrence and abundance-related spatial-allocation evidence. It is a reorganization of **already inspected** NEON RELEASE-2026 results, not a new prospective confirmation or a pooled meta-analysis of incompatible endpoints. The new cross-population coupling question remains an explicit **untested hypothesis**. The paper is not ready for journal submission.

**Scientific focus:** Under what landscape and population conditions do recognizable taxon-associated spatial configurations persist despite changing observed individuals and local density? The geographic unit is the **physical NEON site**; seasonal comparisons and trap rows are nested observations, not independent sites.

## Abstract — provisional, appropriately bounded

Animal community spatial structure may appear persistent even when individual identities and population density change. We propose a macroecological framework distinguishing (i) recurrence of taxon-associated capture locations among different observed animals across seasons and (ii) how population density is associated with variance in short-term spatial use within individuals versus across their observed centres. We assembled existing checksum-verified National Ecological Observatory Network (NEON) small-mammal box-trap analyses across standard 10×10 trap grids and the 2015–2026 RELEASE-2026 window. In 58 adjacent-season comparisons nested in 30 plots at 14 independent physical sites, the same genus reappeared at the same named trap positions more often than expected under a genus-and-trap-fixed occupancy null, after individuals bearing tags shared between seasons were removed. Correcting a nonuniform accepted-only-swap null yielded a mean physical-site standardized recurrence of **+0.7947**, positive at **11/14** sites. Excluding two physical sites with reused seasonal source keys left 46 comparisons across 12 sites, mean **+0.8432**, positive at **10/12**. These positive conditional patterns survived two post-result simulation scenarios, but their p-values do not bound all temporal dependence or distinguish true space use from genus-specific catchability. An earlier, broader abundance–space-use analysis included **1,326** sessions at **40** sites and eight genera. Although the genus-balanced contrast suggested opposite associations of density with within-individual and among-centre spatial variance, its predeclared taxonomic generality criterion **failed (5/8 positive genera versus six required)**, with exploratory between-genus differences in apparent modes of spatial accommodation. The corrected positive recurrence pattern and heterogeneous density response are therefore **complementary observations, not yet a verified correlation or causal trade-off in matched populations**. We outline a testable continental framework for determining whether the persistence of taxon-associated spatial signatures is buffered by habitat constancy, despite context-dependent individual/population spatial reorganization. An original-source exact event crosswalk and independent habitat/detection validation are mandatory before that synthesis can become a supported mechanism or novel macroecological law.

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

The abundance-related spatial-response development dataset sampled **1,326** taxon-event records across **40** physical sites and eight genera, under its different frozen support rules. No exact site × plot × event crosswalk had been completed when the two analyses were first compared. Their 14-site and 40-site footprints cannot be assumed to coincide at the same population or season, nor can their effects be combined into a single p-value.

The independent San Jacinto source comprised six local 7×7 grids within one study area, with a species-rank result in nine of ten positive original season comparisons after removing bridge-tagged animals. It motivated the NEON genus-rank recurrence endpoint. Its sampling and chain calibration remain separate, and its historical p=0.046875 is NOT part of the current corrected continental NEON null result.

The NEON archive uses tagged small-mammal protocols, not telemetry or full home-range delineation. Observed tag disjointness is distinct from direct mortality/birth/migration estimates. Taxonomic labels for NEON's *Peromyscus* species are not DNA validated by the linked historical morphology-based BOLD metadata.

## 3. Methods: two responses, one hierarchy

### 3.1 Community-scale taxon–station recurrence

Use the **already frozen** 58 comparisons across 14 sites. For each pair, season A and B genus×station binary matrices are built after tags present in both seasons have been excluded from BOTH matrices. Overlap is `O = sum_{g,t} A[g,t]B[g,t]`. A corrected fixed-margin Markov sampler randomizes season B while preserving each genus's occupied station total and the number of genera at each station. Contrast `R_u = (O_u-E_0 O_u)/SD_0 O_u` is averaged within each physical site and then with equal site weights. The full 14-site group and prespecified-by-source 12-site exclusion sensitivity are distinct views of the **same ecological outcome**, not independent datasets.

The 2026-10-20 null correction replaced an invalid accepted-only-jump-chain clock with a symmetric proposal-clock that retains failed swaps and holding probabilities; two chains of 2,000 retained draws each were run for every unit. Finite-state target and mixing diagnostics passed. Post-result independent-unit and comonotone rank-coupled scenarios probe, but cannot fully identify, intra-site temporal dependence.

### 3.2 Population-scale density accommodation

Use the historical RESPONSE definition, not new fitting after observing the 14-site recurrence result. `W` is within-animal observed positional variance over exact three-night sessions; `B` is the debiased among-animal observed centre dispersion. The historical genus-MNKA predictor and `Delta_beta = beta_B - beta_W` compare associations across levels; fixed temporal and location controls follow the frozen joint model. These are observational proxies, not causal density manipulations, true activity centres or complete animal ranges.

The frozen genus-balanced model had a positive difference but only 5/8 positive genus-specific estimates against the mandatory 6/8 threshold. We report **all eight**, retain negative genera and mark post hoc ecological modes exploratory. No propensity to crowding is established by the mean coefficient alone.

### 3.3 New macroecological linkage, explicitly not yet an outcome

From the same original source and original 58 pairs, link exact three-night source event dates to the structurally eligible marked-animal repeat bouts for the original response taxa; count matched physical sites, plots, seasonal transitions and genera. The result is **support-only**; it cannot by itself replicate the exact historical 1,326 W/B *modeled* sessions, because MNKA variation, response-series eligibility and finalized geometry remain additional requirements.

A prospective matched effect or a new independent release will require:
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

### 4.2 Spatial accommodation is heterogeneous, not a general rule

Genus-balanced historical slopes were `beta_W = -4.395`, `beta_B = +4.977`, `Delta = +9.372` m²/MNKA, but the original **five of eight positive-genus** result failed the required six. Every one of the eight genus estimates must be displayed. Additional post-result exploratory diagnostics suggested different multi-site geometric modes:
- Apparent within-animal compression with relative centre dispersion/maintenance: *Chaetodipus*, *Myodes*, *Peromyscus*.
- Apparent population-footprint compression: *Dipodomys*, *Sigmodon*.
- Unresolved or inconsistent modes: *Microtus*, *Napaeozapus*, *Onychomys*.

These patterns are **post-result descriptions**, not validated behaviour types or evidence that traits, taxonomy or competitive status caused the modes. One-site genera have no independent cross-site replication; *Peromyscus* is particularly heavily sampled and later positive-sign confirmation was imprecise/nonreplicated.

### 4.3 The macro coupling remains an open ecological test

Both observational scales exist in the same broad continental monitoring programme. However, **the current receipts do not show that the 14 sites with positive taxon recurrence are the exact site×plot×event populations used for density-mode estimation**. Any claim that site-level recurrence predicts higher or lower individual-density accommodation would therefore be invented. The source-only crosswalk is the immediate next empirical result, followed by independent habitat and detection evidence if structurally estimable.

## 5. Discussion and proposed generality

The pattern established today is **organizational recurrence beyond repeated observation of the same individuals**. The historical density component does not establish a complementary conserved law: it instead warns that density-associated within-vs-among individual geometry varies among lineages and has observational limitations. This contrast motivates a stronger and genuinely macroecological next question: *Is high-level spatial organization buffered against lower-level population rearrangement, and do environmental heterogeneity and temporal constancy predict the limits of this buffering?*

The key prediction is cross-level, not a generic rediscovery of rodent niche segregation. A valuable **negative** future result would be that apparently persistent taxon signatures disappear when genus-specific detection is measured independently; another would be that few source populations support both nested responses, making direct coupling empirically unidentifiable in the current NEON data. Neither should be hidden by exploratory subgroup selection.

Prior literature establishes separate axes of habitat association (Goldingay & Price 1997; Chock et al. 2022), density and space-use variation (e.g. O'Fallon et al., *Oecologia*, 2025), and continental population synchrony (Barton et al., *Ecology and Evolution*, 2026). Continental coverage of NEON by itself is not novelty. What could be novel is **a genuinely matched ecological test of the stability of taxon-to-place structure versus the plasticity of individual/population space use, with site-level environmental and detection boundaries**.

## 6. Figures in one paper

**Figure 1 — Macro population & missingness.** Plot all standardized NEON source bouts, the 803 candidate transition denominator, the 216 diagnostic two-genus supports, and the 58 original three-genus eligible comparisons. Site/domain coverage must include unqualified sites (not classify them as negative outcomes).

**Figure 2 — Corrected community spatial persistence.** Use only [corrected Figure 2](figures/neon_crossseason_genus_site_means_corrected_v0_3.svg) derived from verified corrected null output, 14 vs 12 physical-site sensitivity. Do not re-use the obsolete accepted-swap figure.

**Figure 3 — Density-associated geometric response diversity.** Plot the eight original genus `Delta_beta` estimates with sample-size/site counts and a prominently labelled frozen **FAIL 5/8 < 6/8**; modes exploratory. There is no shared Z / beta axis or pooled significance.

**Future Figure 4 — Direct matched macro analysis.** Not authorized until source crosswalk, independent covariates and independently validated outcomes are available. Omit it rather than invent an association.

## 7. Conclusion

**Established:** Genus-associated capture locations can recur across adjacent seasons without requiring observation of the same tagged individuals in both seasons, under a corrected, constrained fixed-margin null and geographically blocked analysis. **Not established:** universal density accommodation, a link between recurrence and population-level W/B responses, a climatic/macroscale mechanism, competition, or habitat-driven recurrence. These become a unified, falsifiable macroecological research programme rather than two separately advertised successful papers.

## Source and reproducibility links

- Main unified contract: `docs/NEON_UNIFIED_MACROECOLOGY_20261025.md`.
- Unified factual result ledger: `results/neon_unified_macro_evidence_20261025.json`, builder `analysis/build_neon_unified_macro_evidence_v1.py`.
- Positive corrected NEON evidence: `results/neon_uniform_null_correction_receipt_20261020.json`; `manuscript/NEON_SPATIAL_TEMPLATE_CORRECTION_ADDENDUM_20261020.md`.
- Historical density **failed** generality: `results/multiscale_density_development_result_v1.json`, `results/multiscale_density_heterogeneity_result_v1.json`.
- Complete source support denominator: `results/neon_crossseason_genus_template_support_receipt_20261019.json`.
- CHM feasibility only: `results/neon_five_anchor_chm_source_receipt_20261020.json`.
- San Jacinto historical different-rank result: `results/san_jacinto_crossseason_ecological_comparator_receipt_20261019.json`.
- New source-only joint audit: `analysis/audit_neon_unified_macro_source_crosswalk_v1.py`; `.github/workflows/neon-unified-macro-source-crosswalk-v1.yml`.
- Source NEON DP1.10072.001: https://data.neonscience.org/data-products/DP1.10072.001
- Chock et al. 2022 *Oecologia*: https://doi.org/10.1007/s00442-021-05104-5
- Goldingay & Price 1997 *Conservation Biology*: https://doi.org/10.1046/j.1523-1739.1997.95480.x
- Barton et al. 2026, *Ecology and Evolution*: https://doi.org/10.1002/ece3.73413

**Decision:** one ecology/macroecology manuscript route replaces the planning split described in `docs/NEON_ECOLOGY_TWO_PAPER_DECISION_20261019.md`. Historical frozen tests, decisions, results and drafts are preserved for provenance and cannot be rewritten by this paper strategy.
