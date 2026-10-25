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
