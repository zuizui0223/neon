# One NEON macroecology programme: spatial reassembly × spatial accommodation
**Decision date: 2026-10-25 — unified scientific mainline, superseding the two-paper strategy as an active research plan.**

**Status:** integrated hypothesis and source-only future-analysis design. **No new ecological effect and no independent validation have been opened by this document.** The 2026-10-19 / 20 primary seasonal finding was already observed before this plan. The historical A/B manuscripts, preregistration records and failure decisions remain immutable provenance, not two new parallel targets. The currently corrected ecology draft (v0.3) is a verified baseline, not the final macroecology paper.

## A single, nontrivial ecological question

> **When the observed animals and local abundance change, under what environmental and taxonomic conditions is the spatial organization of a small-mammal assemblage reconstructed rather than erased?**

The conceptual claim to be tested is a *decoupling*: community-level taxon-to-place recurrence may be more persistent than the identities of sampled animals or the distribution of short-term space use *within* and *among* animals. Temporal recurrence and density-related spatial accommodation are **different, nested ecological responses**; they do not become the same effect merely by being presented in one paper.

**Working title:** *Spatial persistence and population reorganization across continental small-mammal assemblages*.

**Distinctive contribution being pursued:** quantify whether **the same taxon-associated spatial signature survives population reorganization**, and predict *where across landscapes and biomes* that separation is strongest. Prior literature already covers temporal stability, rodent segregation, home-range changes with density and NEON-wide population synchrony: never claim any of those as first discoveries.

## Current evidence, frozen and correctly qualified

1. **Validated positive observation:** original RELEASE-2026, **58** season-pair contrasts nested in **30** plots and **14** physical sites. Corrected lazy symmetric fixed-margin null yields site-equal mean recurrence Z **+0.7946637727454396**, **11/14** positive site means; source-defined season-reuse exclusion leaves **46** contrasts in **12** sites, corrected mean **+0.8431617303483938**, **10/12** positive site means. Conditional rank-coupled stress p **0.0012499375** and **0.0020998950**, respectively, are **post-result model-based sensitivity p-values, not guaranteed joint dependence bounds**. An observed-tag-disjoint comparison does not prove deaths, migration or true demographic turnover.
2. **Different response, inconclusive generality:** density-accommodation W/B development on **1,326** taxon-event sessions across **40** NEON sites and **eight** genera. Genus-balanced beta_W **-4.3948258967** and beta_B **+4.9769395758** m²/MNKA, but the **6/8 positive-genus precommitted rule FAILED (only 5/8)**. These are same-release *development* associations, not a confirmed population law; the subsequent independent *Peromyscus* positive-point-sign test did not replicate cleanly. Exploratory spatial response modes are heterogeneous; no post hoc sorting may rescue the original threshold.
3. **External consistency, not a pooled effect:** San Jacinto species-level seasonal recurrence under nonshared observed tags (10 contrasts in six local grids, 9 positive), analysed with EcoSimR SIM9. Unlike the NEON defective accepted-only jump chain, this code invokes `sim9_single`; nevertheless its finite-chain and season-dependence validation has **not** been rerun following the NEON sampler correction. The six grids are from one study area. Its historical site-signflip p=0.046875 is *not* a continental second replicate for a common estimand.
4. **Independent environmental material exists, mechanism not shown:** original 30 plots have 150 official A1/A10/E5/J1/J10 source anchor pixels in verified AOP CHM. **14/30** plots have nonzero five-point canopy height range. Missing historical source-dated locations, unquantified per-station uncertainty and historical image/capture-year mismatch **STOP** habitat causation. The full 3,000-location GraphQL–REST audit failed at a five-name schema preflight; do not spin this into habitat selection evidence.

There is **no validated same-site crosswalk** at present showing how many seasonal recurrence pairs overlap the 1,326 exact W/B development sessions. The large 40-site versus 14-site geographic footprints are not already linked per site, genus, plot or date. A merged paper cannot silently take numerical estimates from different cohorts as a measured correlation.

## One hierarchical biological framework, rather than two papers

### Spatial persistence: cross-season lineage-associated station recurrence

`R_{spt} = [overlap(A_{spt}, B_{spt}) - E_{FF}(overlap)] / SD_{FF}(overlap)`, where `s` is physical site, `p` a plot and `t` an adjacent-season pair. `FF` is the **corrected** fixed-fixed null preserving season B taxon station totals and trap taxon richness. The observed A/B matrices exclude tags seen in both seasons. Multiple `t` values within a site are not geographic replication. NEON uses **genera** here, not DNA-validated species.

### Spatial accommodation: density-associated allocation within vs among animals

`W_{g,spe}`: repeat-location **within-individual** short-term variance, `B_{g,spe}`: debiased dispersion of observed **individual centres** at event `e`; `D=B-W`. The historical predictor is genus-MNKA, subject to field identification and detection limitations. Contrasts `beta_D = beta_B - beta_W` describe **association** with abundance, not experimentally identified competition, movement trajectories or home range. The former all-genera generality FAIL is preserved.

### Environmental setting and macroecological gradient

Covariates must have **independently documented measurement times and grain**:
- Site/season climate (temperature, precipitation or vapor pressure deficit, one prespecified variability axis), matched to dates with original NEON source dates, not present-day climate inferred for previous bouts.
- Within-plot vegetation structural heterogeneity (if and only if source-dated, uncertainty-aware trap locations and acquisition date checks pass). CHM = tall canopy proxy only; a zero pixel does not prove low shrubs/grass absent. Vegetation structure/cover field plots are **not** automatically co-located with rodent traps.
- Observational exposure: actual operating trap-nights, trap changes, capture propensity proxies and source field identification qualifiers; these are **detection/effort controls**, never evidence of true occupancy by themselves.
- Population state: within-genus MNKA, observed marked-tag turnover fraction in the full source *before* bridge-tag exclusion, and relative conspecific/congeneric counts only where identity is adequately verified. F/C composition has **0** conservative exact same-season fixed-N/U matches, so do not claim competition.

### A falsifiable set of explanations, not cherry-picked climate regressions

- **H1: persistent spatial template / context buffering.** High local habitat constancy predicts cross-season `R>0` even where sampled identities and population abundance change; rank order in `R` should be stable across nonoverlapping bouts/years. Evidence required: source-dated habitat or independent verification of repeated station attributes and a held-out population or release.
- **H2: flexible density accommodation.** The spatial level of abundance response varies across lineages/environments, rather than sharing the original failed positive `beta_D` rule. Tested using a pre-specified interaction/partial pooling in new genuinely unobserved data, with `W` and `B` separately and identity/effort sensitivity. Taxon random slopes require multiple independent sites per genus.
- **H3: differential persistence despite reorganization.** In **matched site×plot×time populations with both endpoints**, `R` may stay positive while `W` and `B` respond heterogeneously to local abundance. The **joint cross-response association is unmeasured** until structural crosswalk and independently held-out outcomes pass.
- **H0: observation-process template.** Repeated genus-specific capture propensity and stable station conditions reproduce `R` without true-use recurrence. This competes directly with H1/H3 and must be explicitly modelled or measured with an independent detection channel.

These hypotheses are not all independent or guaranteed to be simultaneously estimable. H3 is not accepted by juxtaposing two source-level tables.

## Macro research design: scale, replication and non-overfitting

**Data universe:** NEON original DP1.10072.001 RELEASE-2026 (2015-04..2026-09) for *descriptive/development* work; external Figshare San Jacinto separate. For genuinely new ecological confirmation, predeclare a **new post-2026 independent release/cohort or geographically independent standardized marked-individual trapping system**, with checksum-proven no reused original observations. Do not mine the consumed release for supposedly fresh p-values.

**Population universe, not just significant stations:** first reconstruct every standard complete three-night pathogen grid and trap-night effort; report all sampling sites, dates, taxon richness, absent/low-richness site exclusion, and prevalence of 1/2/3+ shared-genera adjacent-season pairs. The existing source-only census shows 1,838 effort-valid bouts, 803 adjacent-season candidate pairs, 216 eligible diagnostic two-genus pairs and 58 original ≥3-genus primary pairs; **the diagnostic 216 are NOT newly confirmed spatial effects**. Map sample eligibility independently of observed `R` to avoid the 14-site selection masquerading as all-NEON spatial macroecology.

**Grain and nesting:** individual captures → event (three nights) → genus×plot×season → seasonal transitions → physical sites → domains/biomes. For new environmental-scale analyses, avoid pretending 58 nested transitions are 58 independent ecosystems. Use leave-one-*physical-site*-out or held-out biome prediction, and preserve site-block/site×year dependence, missingness and true calendar-year alignment. All historical site-level analyses are explicitly *post-result exploratory*. Do not rely on 100 trap-night binary cells as pseudo-replicates.

**Crosswalk required before any joint model:** derive exact source event keys for both the **locked** 58 recurrence pairs and the **frozen structural** W/B opportunity sessions from the *same* checksum-pinned source. Count source-overlap at physical-site, plot, event, and genus levels; count at least one W/B structurally supported genus in each of BOTH adjacent seasons. No outcome regression, W/B geometry or recurrence recomputation in this audit. If fewer than **8 independent sites**, **20 matched pairs**, and **3 multi-site genera** support a joint contrast, label a direct same-population mediation/coupling test **NOT ESTIMABLE**; retain the single macroecological question with two differently sampled response families, but never fit a spurious matched model. These are newly chosen post-result feasibility thresholds, **not preregistered inference thresholds for the original NEON finding**.

**Macro environmental-effect gate (new cohorts):** require documented covariate coverage in at least 20 *independent* sites across 3 declared ecological domains (and at least 100 nonoverlapping seasonal pair units) before interpreting *two* fixed macro environmental gradients with site/genus partially pooled effects. If below threshold, report observational descriptive maps and no environment-driven general mechanism. Confirmatory validation requires genuinely independent spatiotemporal observations and a locked model before effects are opened.

**Model family (conditional on above gates):** a multilevel response model for genus-trap recurrence `R` with a physical-site intercept, spatial/temporal covariate effects and effort/detectability sensitivities; separately, a partially pooled bivariate model for `W,B` with group-level genus and independent-site effects. A joint population covariance term may be fitted **only to exactly linked matching units with sufficient independent support**. Prefer held-out predictive improvement against a station-detection-only baseline rather than reporting a large in-sample p-value. Conditioning on taxonomic eligibility must be acknowledged as a selected observed-population estimand.

## Three core manuscript figures (do not reuse obsolete V6 geometry)

1. **Observed macro coverage:** whole NEON site/plot/bout support funnel and biome sampling; all site counts including sites with no qualified seasonal comparisons. This is an inclusion figure, not a significance map.
2. **Spatial recurrence:** corrected 14 site effects, separately showing original source-disjoint 12-site sensitivity; `manuscript/figures/neon_crossseason_genus_site_means_corrected_v0_3.svg` is available. Historical accepted-swap Figure 2 is obsolete.
3. **Spatial accommodation heterogeneity:** all eight frozen genera, original beta_D (+/-), 1,326 sessions across 40 sites, and the **5/8 FAIL guard** visibly marked. Display post-result inferred modes as exploratory, and never put density beta_D estimates on the same numerical Z-axis as recurrence. A future matched-coupling panel exists only after the crosswalk passes.

## Explicit claim-status ledger

| Item | Current interpretation |
|---|---|
| Season-to-season genus×station recurrence among nonshared observed tags | **Supported conditionally** in original 14-site data and corrected 12-site sensitivity |
| Universal density-induced within-individual packing | **FAILED** its prespecified eight-genus guard |
| Multiple apparent spatial allocation modes | **Exploratory descriptive** development result, not replicated mechanism |
| Matched relation between persistence and accommodation | **NOT YET TESTED**; source crosswalk pending |
| Habitat persistence / competition / true turnover causes recurrence | **NOT ESTABLISHED** |
| San Jacinto full corrected independent validation | **PENDING** chain/dependence review |
| General broad-biome ecological macro principle | **PENDING** independent supported gradients and genuinely new validation |

## Execution sequence

1. **Now:** programmatically collate the corrected 14/12-site data, frozen 40-site W/B result, eight genus modes, the exact source eligibility funnel and historical environmental source receipts into **one immutable machine-checkable macro evidence ledger**. The ledger must flag failed/null results, avoid pooling incompatible outcomes and carry source paths.
2. **Now:** code and run a single-download **source-only** same-population crosswalk for the locked 58 pairs versus frozen W/B structural support; record aggregate site, pair and genus eligibility, no identifiers and no new effect.
3. **After structural audit:** if minimum support passes, write a future matched-cohort outcome contract, not a post hoc “new discovery” on already consumed 2026 observations; otherwise model the two scales separately within one ecological synthesis.
4. **Later:** site/season environmental and detection source-audit and independent replication beyond the current NEON cohort. Do not block the macro framing on the unresolved 3,000-location GraphQL preflight; station-specific canopy effects remain explicitly unavailable in the meantime.

**Historical strategy superseded as a planning decision (not deleted):** `docs/NEON_ECOLOGY_TWO_PAPER_DECISION_20261019.md`. Existing failed/null/hold decisions and individual effect locks cannot be overwritten by editorial unification.

---

## 25 October 2026 source-only crosswalk outcome — direct combined response STOP

**Observed after the unified *feasibility criteria* above were written; no ecological R, W/B, abundance slopes, habitat scores or competition outcome was reopened.** The checksum/size-verifying workflow [40162524657](https://github.com/zuizui0223/neon/actions/runs/40162524657) rebuilt the exact same original **3,547**-file source manifest, downloaded/verified 3,480 relevant capture files, reproduced the **58** fixed eligible adjacent-season contrasts over **30 plots / 14 physical sites**, and matched their **113** distinct original three-night source events to the frozen target-taxon repeat-capture *structural* criteria. Source receipt: `results/neon_unified_macro_source_crosswalk_receipt_20261025.json`.

| Structural stage | Verified count |
|---|---:|
| Frozen genus-recurrence pairs | **58** |
| Distinct source trapping events within those pairs | **113** |
| Events below the old total capture/trap-night saturation cap | **74** |
| Events containing ≥1 structural repeat-supported target genus | **56** |
| Pairs with ANY repeat-supported target genus in both seasons | **18** |
| Pairs with the SAME genus that is in the original recurrence matrix and has repeat support in both seasons | **12** |
| Physical sites containing such pairs | **8** |
| Original plots containing such pairs | **10** |
| Distinct matched genera | **6**, but **only 1** occurs in matched pairs at ≥2 sites |

**Decision: `STOP_MATCHED_RESPONSES_NOT_STRUCTURALLY_GENERAL`.** The precommitted **8-site minimum passes exactly**, but **12 matched pairs < 20** and **1 multi-site replicated genus < 3**. Thus the already-opened data cannot justify a robust same-population `R`–`W/B` mediator/covariance analysis. This is an explicit *support-limited result*, not evidence that no ecological relationship exists; if the original full 1,326-session model membership and MNKA variation were imposed, support could narrow further.

**Effect fidelity preserved:** the corrected positive 14-/12-site recurrence stays unchanged; the original eight-genus density 5/8 FAIL remains; San Jacinto is not pooled; the structural crosswalk is not a biological joint effect. Historical records and their source identity remain immutable. Do not relax the 20-pair or three multi-site-genera source guard to obtain an estimate from the previously inspected cohort.

### Scientific direction after STOP — macro context before another biological effect

The single-paper goal is retained, but **not** as an estimated density→ecological memory mechanism. Prioritize **geographic and temporal coverage, environmental contextualization and the selection process into the original 58 pairs**, followed by independent new source data for population-reorganization tests. The immediate feasible macro unit is the *physical NEON site* and its nested standardized three-night source observations, including sites failing the ≥3 shared-genus transition rule. A secondary core outcome remains the corrected genus×trap recurrence among the qualified subset.

1. **Macro study universe:** document physical-site/domain/season coverage across *all* effort-valid bouts and **803** adjacent-season candidate pairs, then distinguish the 216 diagnostic two-genus and 58 stringent three-genus subsets. Presence in the 44-site NEON terrestrial protocol is not proof that a source site yields a supported paired effect. Estimate/report inclusion probability and environment/data-availability asymmetry without using observed recurrence signs.
2. **Environmental context:** independently dated site-season climate and ecological-domain covariates may be audited before choosing biological hypotheses, avoiding the failed station-level REST–GraphQL geometry join. High-dimensional spatial niche habitat/interaction claims remain blocked until independent detection and station-specific covariates actually match capture dates.
3. **Test novelty where possible:** whether taxon-associated space-use recurrence *and* the diversity of density spatial responses exhibit **predictable environmental/taxonomic heterogeneity** across new independent field cohorts. Do not interpret heterogeneous old development slopes as an already established climate-by-density interaction.
4. **Negative result remains informative:** under the currently qualified time/individual support, only 12/58 seasonal pairs can even *potentially* support both a recurring genus and within-individual response, providing a concrete design limit on studies that infer cross-scale mechanisms from the same mark-recapture data.

**Publication ceiling now:** a one-manuscript, ecology-first synthesis with a corrected positive recurrence result and historical negative/hypothesis-generating density heterogeneity; any new macro generality must be separately generated and validated.

---

## Novelty audit — named overlapping macroecological studies (25 October 2026)

The merged-paper claim must be **narrower than "a new macroecological abundance–occupancy law"**. Several close published programmes already occupy the broad space:

- **Holian et al. (2026), `Abundance–Occupancy Relationships are Informed by Species Temporal Occupancy`, *Ecology and Evolution*, DOI [10.1002/ece3.73214](https://doi.org/10.1002/ece3.73214)**: used NEON small-mammal observations across geographically distributed sites, **127 species / 40 genera, 2014–2019**, and explicitly evaluated spatial AND temporal occupancy–abundance relationships at both interspecific and intraspecific levels. Therefore *temporal persistence + abundance + continental NEON* is **already published** and must not be claimed as our novel contribution. Their temporal occupancy is a fraction of time species present; our original `R` is specifically **a taxon occupying the same exact trap location across adjacent seasons with shared observed tags excluded**, conditional on taxon and station marginal totals. These are related but non-equivalent estimands, and the publication should be described as a prior theory/context, not as an identical test.
- **Brownfield et al. (2025), `Uncovering multiple influences on space use by deer mice using large ecological networks`, *Oecologia*, DOI [10.1007/s00442-025-05731-2](https://doi.org/10.1007/s00442-025-05731-2)**: tested *Peromyscus* spatial use vs density, habitat and latitude across **36 NEON sites**. Continental density × habitat × latitude in NEON alone is established.
- **Barton et al. (2026), `An Ecological Dipole in North American Mast-Eating Small Mammal Dynamics`, *Ecology and Evolution*, DOI [10.1002/ece3.73413](https://doi.org/10.1002/ece3.73413)**: continental rodent abundance synchrony / anti-synchrony across **23 NEON forested sites**, so broad geographic population variation is not the novelty.
- **Chock et al. (2022), *Oecologia*, DOI [10.1007/s00442-021-05104-5](https://doi.org/10.1007/s00442-021-05104-5)**: rodent trap-level co-occurrence segregation, species-specific habitat filtering and fixed-fixed comparison were already demonstrated in San Jacinto. Old methods cannot be headlined as innovations.

**Refined nontrivial question:** `Is taxon-to-station spatial recurrence among NONSHARED observed marked individuals preserved beyond marginal occupancy, and how do the environmental/biogeographic limits of eligibility, detection and population response determine the scope of its generalization?`

**What would make a genuinely new macro *result***: source-verified inclusion probabilities across all NEON domains, followed by a *new independently observed cohort* showing that **conditional spatial recurrence at individual-disjoint traps** varies predictably across site-level independent environmental differences after allowing taxon-specific capture propensity. The existing 14-site positive result remains strong *conditional* ecological evidence, but is not by itself proof of that macroenvironmental relationship.

**Avoid a false inference from the new source crosswalk STOP:** It does **not** show an inverse ecological relation between within-individual reorganization and community persistence; it shows there is insufficient same-event repeat support for the proposed joint response analysis.

---

## 25 October 2026: positive exactly-two-genus exploratory expansion (new original-release effect)

**The source-feasibility and mathematically exact conditional-null design were committed before the new two-genus genus×trap spatial overlap results were opened.** The original previous >=3-genus positive 14-site result was already known, so this new same-release group is *historical post-result exploration*, NOT independently prospective replication. The immutable original 58 comparisons and failed original density generality remain unchanged.

### Source-defined independence and broader macro coverage

The original **216** pairs meeting the effect-blind >=2 genus diagnostic support divide into:
- **58** original >=3-genus seasonal comparisons: strict old corrected positive conditional result at **14 sites/10 ecological domains**;
- **158** disjoint EXACTLY-two-genera comparisons: **30 sites/15 ecological domains**, including **17 physical sites** and **five ecological domains** absent from the older strict group.

The source union comprises **216 distinct seasonal pair keys at 31 unique physical sites and 15 ecological domains**, *not* 44 sites (13 sites overlap between groups), nor 216 independent physical ecosystems. This broadens estimable geographic source coverage from 14/42 to 31/42 candidate sites, and from 10/18 to 15/18 candidate domains. Strict >=3 source case fractions remain historically **58/803 = 7.22%**; >=2 diagnostic source coverage is **216/803 = 26.90%**. In the source pair-weighted Shannon sense, effective domain coverage rises from 7.56 to 12.64, versus 15.08 of all candidates. **These are sample representativeness, not ecological effect estimates.**

### Exact two-genus ecological result (distinct conditional estimand)

New original-data [Actions 40166644498](https://github.com/zuizui0223/neon/actions/runs/40166644498) opened the two-genus seasonal overlap only after source support GO and a separate exact-null variance feasibility GO. In two rows, the fixed-margin genus×trap null is mathematically a finite multivariate hypergeometric distribution, with no MCMC convergence approximation for each unit; see pre-effect `docs/NEON_EXACT_TWO_GENUS_EXACT_NULL_ADDENDUM_20261025.md` and brute-force state-enumeration tests.

| Statistic | All original EXACT two-genus group | Entire reused-season source sites excluded |
|---|---:|---:|
| Original source seasonal pairs | 158 | 52 |
| Informative nonzero exact-null-variance pairs | **150** (8 zero variance) | **48** |
| Independent physical sites | **30** | **17** |
| Observed positive site means | **25/30** | not separately archived (do not infer) |
| Equal-site mean standardized recurrence Z | **+0.614711** | **+0.698352** |
| Product exact-null 20k Monte Carlo plus-one p | 0.000050 | 0.000100 |
| Rank-comonotone within-site exact-null 20k stress p | **0.000150** | **0.001250** |

The 20k site meta-null draws still carry simulation precision limits, and the comonotone dependence scenario is NOT an all-joint ecological worst-case bound. All **30 original site means** are retained in an anonymous [source-backed figure](../manuscript/figures/neon_exact_two_genus_site_means_20261025.svg) including the five negative sites.

**What this adds biologically:** The same direction of genus-to-exact-trap seasonal recurrence among different observed tags was present in a lower sampled genus-richness group with broader geographic coverage. It is conditional **capture-space structure**, *not* proof that lower richness increases or decreases true ecological persistence, and not a direct test that species are absent/present in particular habitat*. The two-row versus >=3-row matrices have different per-unit null effect scales; never pool their Z or p-values or compare their magnitudes as a genus-richness effect.

**Major remaining alternatives:** stable genus-dependent trap catchability, unmeasured station-specific microhabitat/resource positions, unverified true demographic turnover, within-site season/dependence beyond the reported stress. None are excluded by an exact conditional fixed-margin null. Repeated source sites mean this is NOT an independent second ecosystem/time sample, even though pair keys are disjoint.

**One manuscript, not A/B and not a new third paper:** active source is `manuscript/NEON_SPATIAL_MACROECOLOGY_UNIFIED_V0_3.md`. The original historical density W/B 5/8 vs6 required failure and unsuccessful direct 12/58 cross-scale matching stay as clearly flagged separate-scale observations.

**Next primary science gate:** identify environmental and detection-source variables that are independently measured and temporally aligned at these **30** sites / 15 domains. A single new held-out environmental hypothesis should then be frozen before testing another independent site/season cohort. Reporting exploratory correlations against already inspected site Z can generate hypotheses but cannot establish macro causal mechanisms.

Original machine records:
- `results/neon_exact_two_genus_source_receipt_20261025.json`;
- `results/neon_exact_two_genus_ecological_receipt_20261025.json`;
- `results/neon_macro_two_plus_genus_coverage_20261025.json`;
- conditional-null code `analysis/neon_exact_two_row_fixedmargin_v1.py`, and effect runner `analysis/run_neon_exact_two_genus_ecology_v1.py`.

---

## 25 October 2026 further geographic nonoverlap sensitivity: **positive conditional direction, strict season-reuse STOP**

A new separate **post-result** conditional test retained only the **17 exact-two-genera physical sites not included among the original ≥3-genera 14 NEON physical sites**, by source site-ID set difference *before* opening the subgroup's effect. This provides a narrower ecological geographic statement than treating all 30 exact-two sites as independently replicating the original 14, which they do not (13 physical sites overlap). The new 17 sites span 11 ecological domains, including five absent from the original 14-site source.

- **Source/conditional-null support:** 74 original seasonal comparisons across the 17 entirely new sites, **71** nondegenerate exact two-row uniform fixed-margin null contrasts.
- **Observed result:** **15 of 17 site means positive**, equally weighted site Z=**+0.760059**, source-fixed independent-unit Monte Carlo +1 p=**0.000050** and strong within-site rank-comonotone dependence stress p=**0.000600** (20,000 draws per scenario).
- **Important STOP:** eight new physical sites contained a reused source season key among full original exact-two pairs. Excluding *the entire site* from every such key left just **9 physical sites and 16 informative seasonal comparisons**, below the separately frozen 20-pair requirement. Hence no strict fully source-season-disjoint meta-null for the geographically new subset was opened. The 17-site positive conditional result does not prove arbitrary within-site dependence has been excluded.
- **Inferential scope:** stronger geographic nonoverlap *within a previously inspected release*, not a new independent temporal cohort, not a new preregistered validation, and no demonstration of competition, stable local habitat choice or full biological turnover. The exact two-row marginal null removes MCMC error only, not genus-dependent capture propensity.

Source: `docs/NEON_EXACT_TWO_NEW_SITES_GEOGRAPHIC_SENSITIVITY_20261025.md`, `results/neon_exact_two_new_sites_sensitivity_receipt_20261025.json`, verified [Actions 40167476048](https://github.com/zuizui0223/neon/actions/runs/40167476048).

**Active biological conclusion, unified:** conditional genus-associated capture-station recurrence across *different observed tagged animals* appears at both ≥3-genus and exactly-two-genus comparison strata, and remains positive in source-defined sites not present in the original strict analysis. The density response is heterogeneous with original taxonomic generality FAIL, and exact joint W/B–recurrence effects remain STOP. Future causal macroecology must use independently matched habitat/detection information and genuinely unseen source populations rather than turn these nested historical comparisons into pseudo-replicates.

---

## 25 October 2026 observation-process and climate-source discrimination update

**Positive observation-process robustness, precisely bounded:** Original 158 exactly-two-genus seasonal comparisons at 30 sites/15 domains have **93–100** canonical trap stations (median 100) recorded on all six original nightly station rosters. Every one of the original 158 retained ≥90 common recorded stations and ≥2 original recorded genus locations in both seasons. The source-only [QC audit](../results/neon_macro_six_night_recorded_station_support_20261025.json) passed before a new `A×B` station overlap effect was opened. After restricting both genus matrices to that all-six-night common recorded station set, **150 informative comparisons / 30 sites**, **25 positive physical-site mean Z values**, grand Z **+0.610901** (original unrestricted +0.614711), within-site comonotone rank stress conditional plus-one p **0.000100**. Whole-site reused-season exclusion retained **48 pairs / 17 sites** with Z **+0.691629** (original unrestricted source-disjoint +0.698352), conditional rank stress p **0.001100**. Actual [source-controlled Actions 40180683068](https://github.com/zuizui0223/neon/actions/runs/40180683068) and `results/neon_macro_six_night_common_station_recurrence_receipt_20261025.json`. This weakens **recorded trap-site availability differences** as a sufficient trivial explanation, but station presence is not confirmed trap operability; source `trapStatus` syntax is incompletely interpreted and genus-specific catchability, habitat and within-site dependencies remain unresolved.

**Independent site tower temperature acquisition, honest ecological STOP:** After independently diagnosing and fixing the official NEON instrument file naming `SAAT_30min.YYYY-MM.basic.GENTIME.csv` suffix, **205/205** ORIGINAL RELEASE-2026 `DP1.00002.001` source temperature month files were downloaded and provider checksum/size verified. **143/205** months passed the predeclared half-hour `tempSingleMean` / `finalQF=0` / ≥70% completeness gate; **62** months failed. Only **79** original two-genus seasonal comparison pairs among **27 physical sites / 15 domains** had *both* quality-qualified weather months, short of the frozen **80** pair minimum. The planned one-axis site-level absolute temperature shift vs taxon-station recurrence model was **NOT FITTED**, no temperature beta/p/CI, and this is **NOT** evidence against the thermal displacement ecological hypothesis. Do not lower the threshold to 79 or search other climate axes. Source `results/neon_macro_original_tower_month_thermal_QC_STOP_20261025.json` and [Actions 40181122523](https://github.com/zuizui0223/neon/actions/runs/40181122523). The broken original metadata parser and repair are both recorded in `docs/NEON_ORIGINAL_TOWER_BULK_METADATA_QUERY_CORRECTION_20261025.md`.

**Updated publication position:** one macroecological ecology paper, `manuscript/NEON_SPATIAL_MACROECOLOGY_UNIFIED_V0_4.md`; previous 14-site and new 30-site seasonal observations preserved, 17 original-14 nonoverlap site sensitivity remains post-result and its strict whole-season-reuse sensitivity STOP, original W/B universal 5/8 vs 6 FAIL remains unrescued. Robust observed capture-space genus recurrence is supported; ecological environmental mechanism and taxon-specific detection probability are **not** identified. **SUBMISSION HOLD** until independent true-use/detection/habitat data or a prospectively unobserved NEON release permit source-complete cross-scale/abiotic testing.

---

## 25 October 2026: spatial **scale** of taxon-associated recurrence (new biological boundary)

**A new, single-radius, post-result 10m ecological test was source/design-frozen before inspecting its new outcome.** NEON's official small-mammal trapping lattice has **10m separation between immediate row/column neighboring stations**. After retaining all **158** original exact-two-genus seasonal comparisons and restricting both seasons to the *same stations recorded across all six trap nights*, the new response measured whether a B-season genus occurred at an immediately adjacent (not self) station to an A-season occurrence of the same genus.

**Critical contrast:** the null not only fixed B genus station prevalence and station genus richness, but also the observed original *same-genus, same-trap intersection O*. Consequently any extra positive nearest-neighbor test cannot simply be the original exact-trap overlap re-labeled. Conditional uniform-null moments are analytically exact, and direct iid conditional hypergeometric draws (not old accepted-swap MCMC) supply nested site-null calibrations. Exhaustive small-state tests verified this target. The 10m neighbor outcome was examined only after the source/variance gate passed at **153/158 informative pairs spanning 30 physical sites**, with five non-informative zero-variance units retained in denominators.

| Endpoint for 10m neighborhood conditional on exact same station O | Original full subset | All physical sites with reused season source key omitted |
|---|---:|---:|
| Informative original two-genus seasonal pairs | **153** | **50** |
| Independent physical sites | **30** | **17** |
| Positive physical-site mean Z | **22/30** | not archived separately |
| Site-equal conditional patch Z | **+0.310307** | **+0.182589** |
| Unit-independent conditional-null site +1 p | **0.002400** | **0.152292** |
| Within-site rank-comonotone stress conditional +1 p | **0.039148** | **0.220539** |
| Positive under both declared null scenarios | **YES, historically exploratory** | **NO** |

**Scientific decision: general 10m patch-scale reassembly BEYOND exact trap identity is NOT supported robustly after season-source reused sites are removed.** The full-data p=0.039 under the rank-coupled scenario is a model-dependent, post-result exploratory threshold result; the stricter source-level dependence sensitivity gives p=0.221. This does NOT mean that 10m patch structure was proven absent: fewer observations and distinct location-dependent effects limit power. It is a substantive *scale-boundary result*, not a technical artifact to discard.

**What remains positive:** the original >=3-genera 14-site corrected genus-at-exact-trap recurrence; the exact-two 30-site same-trap recurrence; the 17 original-14 geographically new site positive same-trap sensitivity; and six-night common-recorded station exactly-two 30-site positive conditional recurrence. These are all **capture-space**, not true population turnover or independent replications.

**What is newly constrained:** previous same-trap recurrence must not be summarized as "persistent neighborhood niche patches, territory or ecological spatial memory" without new supporting measurements. Stable genus×trap catchability can explain exact-trap patterns; spatially autocorrelated catchability or stable habitat can generate neighbor patterns, but have not been distinguished by this null. Density-mediated mechanism stays STOP/FAILED and independent climatic tower QC gave only 79 source-complete pairs vs 80 required, STOP no climate regression.

**The 17 physical sites in this whole-source-season reuse exclusion are not necessarily the same 17 physically new sites outside the original >=3 genus geography.** This distinction matters when reporting independent-source robustness.

Evidence: `docs/NEON_10M_PATCH_BEYOND_EXACT_STATION_DESIGN_20261025.md`, `results/neon_macro_10m_patch_conditional_20261025.json`, `analysis/neon_macro_10m_patch_conditional_v1.py`, `manuscript/figures/neon_10m_patch_conditional_exact_station_20261025.svg`; verified [Actions 40186368607](https://github.com/zuizui0223/neon/actions/runs/40186368607). Integrated single ecology paper: `manuscript/NEON_SPATIAL_MACROECOLOGY_UNIFIED_V0_5.md`.

**Further high-impact macroecology testing** should prioritize independent taxon-specific capture-detection information and stationary/nonstationary habitat at confirmed historically dated trapping grid positions. Do not rescue an inconclusive 10m test by opportunistically trying 20m/30m radii on the same inspected release. A spatially informed independent detection instrument or truly unseen source cohort is necessary to claim generality across ecological patch scales.

---

## 26 October 2026: independent detection-mechanism source limitation from official NEON trapStatus

**A new source-only comparison advanced directly toward the paper's core habitat-versus-catchability ambiguity, but the strict observational feasibility gate FAILED before any new ecological effect was opened.** The data are still the exact same 158 season-pair, 30-physical-site, 15-domain historical NEON RELEASE-2026 exact-two-genus observational population.

**NEON official trap-status categorical definition**: codes 4 (>1 capture), 5 (capture), 6 (trap set and empty) are affirmative evidence of a trap recording a functioning encounter or checked empty status. Codes 0/1/2/3 respectively mean no data, not set/captures not processed, disturbed/door closed and empty, and door open with spoor. The prior all-six-night *recorded station roster* metric treated any source row as a station record regardless of whether the source trapStatus described actual trapping opportunity. NEON [2026 mammal data tutorial](https://www.neonscience.org/resources/learning-hub/tutorials/mammal-data-intro) and [small mammal sampling guide](https://data.neonscience.org/api/v0/documents/NEON_smammal_userGuide_vF?inline=true) explain the separate states.

The original source stage, frozen before any new operational-status subset's A×B genus trap overlap, produced:

| Item | Actual original-release source result |
|---|---:|
| Original exactly-two-genus comparisons | 158 |
| Distinct source 3-night trapping events | 293 |
| Canonical trapStatus source rows | 87,916 |
| Source statuses: code1 / 2 / 3 | 1,275 / 3,494 / 4,938 |
| Source statuses: code4 / 5 / 6 | 57 / 13,727 / 64,425 |
| Original 6-night intersection of **recorded stations** | median **100/100**, minimum 93 |
| Intersection of stations coded **4/5/6 on each of all six nights** | median **60/100**, range 1–97 |
| Pairs preserving ≥90 valid source 4/5/6 stations and the same two-genera station support | **18/158**, only **8 physical sites/7 domains** |
| Newly frozen minimum source feasibility | **80 pairs / 18 sites / 10 domains** |
| Decision | **`STOP_OPERABLE_456_SIX_NIGHT_SOURCE_SUPPORT`**; new Z/p **NOT computed** |

**Ecological interpretation:** The current strongly positive genus×named-trap seasonal recurrence (original 30-site Z≈+0.615, common-recorded-station sensitivity Z≈+0.611) is **not** also established on an independently verified all-six-night operational-status cohort. The joint presence of a trap record is a different, weaker exposure criterion than repeated "set/empty" status or capture. This is NOT evidence that animals were absent or that the earlier taxon-to-trap recurrence is false. **Nor** is it a fraction of traps actually nonoperable throughout six nights: statuses 2/3 may result from trapping disturbances after valid exposure, and status 1 conflates traps not set with captures not processed.

**Important selection caveat:** Code4/5 status is itself generated by a captured animal, so making it part of a strict exposure filter conditions on an outcome-related variable. The source gate can diagnose whether a rigorous all-six-night code4/5/6 analysis is estimable; it cannot supply a causal, taxon-specific catchability adjustment. **Do not loosen 90→60, 80→18, or 18 sites→8** simply to rescue the old positive signal. Without a separately observed detection channel, actual trap function histories and microhabitat, the **mechanistic fork between repeated genus-specific trap capture probability and repeated animal habitat use remains unresolved**.

The key new operational progress is an **identified observational-data limitation** and an honest STOP, replacing speculative detection-corrected causal claims. The paper remains ONE `manuscript/NEON_SPATIAL_MACROECOLOGY_UNIFIED_V0_6.md`, with the old W/B failed cross-genus hypothesis and direct matched W/B–R source STOP still explicitly separate evidence families, and the strict 10m-neighbor source-reuse test still unsupported.

**Next science priority:** obtain *independent detection information*, meaning within-season repeat detection independently of animal depletion/trap-status outcome **or** non-trapping cameras/telemetry alongside the same historically valid trap positions, plus independently mapped microhabitat at source-matched stations. Existing NEON `trapStatus` alone cannot identify true genus-level site occupancy or habitat preference separately from capture. The present 2015–2026 release has been repeatedly inspected; any later ecological association analysis is exploratory unless validated on a genuinely unseen release/source.

**Actual source:** `docs/NEON_ALL_SIX_NIGHT_OPERABLE_TRAPSTATUS_GATE_20261026.md`, `results/neon_macro_six_night_trapStatus456_SOURCE_STOP_20261026.json`, [Action 40211504923](https://github.com/zuizui0223/neon/actions/runs/40211504923), [Figure S1](../manuscript/figures/neon_6night_trapStatus456_operability_source_20261026.svg). No new biotic/abiotic genus×trap effect computed.

---

## 28 October 2026: original capture disposition and mechanism identification boundary

NEON's original 2026-release `mam_pertrapnight` contains an observed `fate`/handling status field, initially omitted by our Python trap-row loader. The opt-in original source parser now carries `fate` without changing its original historical default outputs, original 58/158 paired-recurrence selection, old density guard, or seven-site source-selected Microtus/Peromyscus re-encounter result.

**New actual SOURCE-only result:** Across the original seven source-selected physical sites, **615 first-night tagged animal captures** have original raw `fate` records: 179 Microtus, 436 Peromyscus. Initial strict parser found **102 explicitly released**, **12 dead**, **16 escaped**, **94 blank**, and **391 coded entries it could not classify**. After independent source-label inspection **ALL 391** were verified literally `processed`, all from 2017 onward (111 Microtus, 280 Peromyscus). The NEON official 2023 field protocol classifies `Processed` as a capture history/condition, distinct from Dead/Escaped/Not Processed. Therefore the 391 are **not missing `fate` observations**, and the original conservative parser's 21.14% category recognition is **not the raw metadata completeness rate**. Yet `processed` is **not a separate individual-level verified alive-release event**.

Under the source-gated released-only same-genus comparison established on 28 October BEFORE source-fate observations were opened, **only one original physical site** had ≥5 explicit releases in BOTH previously selected genera, whereas ≥6 of original seven sites was required. The stricter released-conditioned downstream response therefore **STOP** and was NOT computed. The previously observed source-matched first-night-to-days2/3 re-encounter difference **−23.5 percentage points** (site-equal Microtus minus Peromyscus, 2000-site-bootstrap interval −45.7 to −2.4 pp) remains a **recorded return rate**, not identifiable intrinsic capture p, causal habitat selection or a mechanism of same-trap seasonal genus recurrence.

**Main ecological inference stays as before:** conditional exact-trap genus-associated capture-space recurrence is supported by the original ≥3 and exploratory 2-genus analyses and survives matching all six recorded nightly station rosters. Neighbor-scale 10m recurrence beyond exact station matching is **not robust** to whole-site season-source reuse exclusion. Independent tower-temperature QC had only 79 paired units vs the precommitted 80, so there is NO tested macrothermal effect. Original density W/B generic 5/8<6 FAIL and same-population coupling STOP unchanged.

**Research boundary/next data needed:** To discriminate true use from observation probability across macro gradients, source the NEON era-specific categorical dictionary and independently verified handling/release records or independent nontrap detection measurements, and a genuinely uninspected population/time cohort. Never retroactively code `processed` as source-confirmed release to rescue the failed explicit-release source gate.

Verified artifacts: `docs/NEON_FATE_RELEASE_REENCOUNTER_DESIGN_20261028.md`, `results/neon_firstnight_original_fate_source_20261028.json`, `results/neon_fate_2017plus_unmapped_processed_source_receipt_20261028.json`, `manuscript/NEON_SPATIAL_MACROECOLOGY_UNIFIED_V0_8.md`. [Source firstnight fate action](https://github.com/zuizui0223/neon/actions/runs/40535085090) and [raw-label-only original source action](https://github.com/zuizui0223/neon/actions/runs/40538157364). [2023 official NEON protocol](https://data.neonscience.org/documents/10179/1883155/NEON.DOC.000481vO/bde7eb23-ba45-8afb-05fa-9ca5667c3482).
