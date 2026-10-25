# Seasonal mammal spatial signatures recur beyond the identities of detected animals
## Corrected ecology-first manuscript v0.3 — 25 October 2026

**Status: RESEARCH DRAFT / SUBMISSION HOLD.** This version is the prospective *writing* replacement for v0.2, **not** a new preregistration, data release, biological analysis, or independent replication. The biological endpoint is unchanged. The correction issued on 20 October supersedes all previously quoted accepted-only-swap null statistics. Do not submit without independent analysis and mechanism/detectability review.

**Proposed working title:** *Taxon-associated spatial signatures recur across seasons among different captured small mammals at geographically independent sites*

**Article type:** Ecology research article. **Submission:** none. **Principal dataset:** versioned NEON RELEASE-2026, product DP1.10072.001. **Secondary dataset:** San Jacinto Figshare (Chock et al.), analysed at a distinct taxonomic rank and spatial design.

## Abstract

Community spatial structure may persist even as the identities of observed animals change. We tested whether the same small-mammal genera reappeared at the same fixed trap stations across adjacent seasons after removing animals bearing tags recorded in both seasons. We used checksum-verified National Ecological Observatory Network (NEON) RELEASE-2026 box-trap source files and a source-defined set of 58 season comparisons from 30 plots at 14 physical sites. For each comparison, a genus-by-trap recurrence score was assessed against a conditional fixed-margin null that preserves genus occupancy totals and trap-level genus richness; we averaged standardized contrasts within physical site before estimating the equally weighted across-site mean. An audit of the original null sampler found that counting only *accepted* swaps failed to target a uniform fixed-margin distribution. We corrected the sampler to use lazy, symmetric proposals including holds and failed swaps, verified its finite-state stationary target, and reran the unchanged original cohort with two convergent chains per comparison. The corrected mean site-standardized recurrence was **+0.7947**, with positive means at **11 of 14** sites. In a source-defined sensitivity excluding both sites with shared seasonal source keys, the mean was **+0.8432** across 46 comparisons at 12 sites, of which 10 were positive. Both patterns lay in the positive tails of post-result site-weighted conditional-null simulations; a strongly within-site rank-coupled sensitivity gave one-sided simulated probabilities **0.00125** and **0.00210**, respectively. These probabilities are conditional on the chosen null and coupling, not worst-case bounds for all forms of dependence. A previously obtained San Jacinto analysis showed analogous *species*-associated recurrence among nonshared tagged individuals, but its original chain and dependence calibration have not been independently revalidated here and its effect and p-value are not pooled with NEON. Our primary finding is that repeated taxon-associated capture-location structure need not rely solely on the persistence of the *same detected animals*. Persistent microhabitat, genus-dependent detection and behavioural interaction remain competing mechanisms, not established causes.

**Keywords:** community reassembly; individual identity; small mammals; spatial niche; seasonal recurrence; null models; habitat filtering; capture detection.

## Significance and ecological question

A stable animal community can mean several different things: repeated capture of the same individuals, persistent use of the same places by a lineage, or persistence of the same cross-species organization. These levels are not equivalent. Our principal question is:

> **Do different captured members of a mammal lineage repeatedly occupy the same observed trap positions across seasons, beyond genus prevalence and generally attractive trap stations?**

The nontrivial contrast is **continuity of locations associated with a taxon despite nonoverlapping sets of observed marked animals**, not discovery of rodent segregation itself. Goldingay and Price (1997) already observed temporally stable kangaroo-rat habitat use, and Chock et al. (2022) established nonrandom rodent spatial associations with microhabitat. Our distinctive contribution is a source-frozen animal-disjoint seasonal recurrence comparison across 14 geographically separate NEON sites. We interpret recurrence as a **capture-space pattern**, not proof of home-range fidelity, territory succession or demographic turnover.

## Introduction

Individual identity, taxon identity and patch identity provide three potential sources of community spatial continuity. If the same animals repeatedly use the same stations, a temporally stable community pattern could result from individual fidelity alone. If different observed animals of the same genus recur at the same stations, this simple explanation becomes insufficient at the level of observed identities. Persistent habitat attributes, genotype-linked preferences, historical settlement, behavioural interactions and detection heterogeneity could each generate a similar signature.

Ordinary contemporaneous species separation cannot discriminate these cases. We therefore compared observed genus-by-station occupancy across consecutive meteorological seasons after removing every tag present in both seasons from *both* matrices. A constrained randomization controlled for the overall frequency of each genus across stations and for the number of genera detected at each station in season B. Repeated pairs within sites were not treated as independent geographic sites.

The San Jacinto programme motivated this prediction: its earlier species-level frozen test found 9/10 positive seasonal contrasts and 5/6 positive grid means within one California study area. Because that evidence was known before designing the NEON test, the NEON source/outcome lock was independent in **data and outcome opening**, not a claim of pre-evidence theory discovery. The two study programmes differ in taxonomic and sampling resolution, so any agreement is qualitative.

## Methods

### Source universe and identity-disjoint comparisons

We retained the original NEON DP1.10072.001 RELEASE-2026 box-trap source population, with its checksum-pinned inventory, source taxonomy and canonical 10 × 10 grid coordinates. Eligible three-night sessions had verified source trap-night effort, and one earliest completed bout was selected per site × plot × meteorological season-year according to the pre-outcome support contract (19 October 2026). Only **adjacent** seasons were compared; missing intervening seasons were never bridged. All source spatial effects were opened *after* the locked eligibility count of at least 20 season comparisons spanning at least eight physical sites passed.

For every comparison, individuals carrying the same consistent tag at that site/plot in both seasons were removed from both seasonal matrices. Each qualifying genus needed at least two season-exclusive marked individuals and two occupied stations in each season; comparisons required at least three shared qualifying genera. Conflict, unknown taxonomic status and tag reuse follow the frozen source rules. This yields **58 comparisons, 30 plots and 14 physical sites**. The genus rather than species rank was chosen to avoid claiming certainty from ambiguous field species identifications. The exclusion is **tag-set nonoverlap**, not measured mortality, dispersal, birth, full demographic replacement or genetic identity.

### Ecological statistic and corrected randomization

For fixed season-A matrix `A` and season-B matrix `B`, with rows representing genera and columns the original named trap stations, define observed recurrence

`O = sum_{g,t} A[g,t] B[g,t]`.

Randomized season B retains each genus's number of occupied stations and each station's number of occupied genera. Season A, spatial station labels and the eligibility set remain fixed. For each comparison we evaluate the standardized departure

`Z = (O - mean(O_null)) / sd(O_null)`.

The 20 October audit established that the original **accepted-swap-only** chain was not generally uniform on the fixed-margin matrix state space. Its original mean Z and p-values are historical values, not current fixed-margin inferences. The corrected implementation uses a symmetric proposal/hold kernel whose rejected/unswappable steps remain part of the chain. Two seeded chains per each of the 58 fixed comparisons used 10,000 burn-in proposals, 100 proposals between the 2,000 retained draws per chain, and finite-state/chain-mixing diagnostics. All 58 comparisons passed the frozen correction quality checks (maximum split-Rhat **1.001347** and minimum batch-means ESS **1023.947**). These are chain diagnostics, not independent ecological replications.

We first average unit Z within each physical NEON site, then give the 14 physical sites equal weight. A source-only dependence sensitivity excludes *all* observations from the two physical sites with re-used site × plot × season source keys, leaving **12 sites and 46 comparisons**. This restriction was defined by original source topology, not outcome sign or habitat.

The post-result conditional-null calibrations simulate 100,000 grand-site statistics under independent unit-null draws, and 20,000 under within-site comonotone rank coupling of the same fixed-margin nulls. The latter is a deliberate strong positive-dependence stress, **not** the known full site-level capture null or a guaranteed upper p-value bound. Both calibrations reuse the observed dataset and cannot be described as independent preregistered evidence. Descriptive sign-flip probabilities require additional sign-symmetry assumptions and are not primary ecological inference.

### Distinct San Jacinto comparison

The prior California Figshare dataset measured focal species rather than NEON genera and used six 7 × 7 physical grids within one study area. Its original test compared adjacent seasons with repeat-tagged individuals removed and an EcoSimR fixed-fixed `sim9_single` null. That R function retains possible no-change transitions, unlike the defective **NEON** accepted-only chain; however this code-level distinction does **not** constitute an independent mixing, chain, seasonal-dependence or biological source audit of the San Jacinto result. We report it as a separate prior consistency observation and do not combine its Z magnitudes or p-values with NEON. The California grid-level p = 0.046875 is historical and vulnerable to limited six-grid support and dependence assumptions.

### Environmental feasibility, not a mechanism test

After the positive original NEON endpoint was opened, we investigated whether source-labelled mammal stations could be linked to independent NEON AOP canopy height data (CHM, DP3.30015.001). The unchanged 14-site/30-plot cohort yielded 150 official five-anchor locations (four corners and E5), all with valid provider-verified raster pixels in the selected published imagery. **14/30** plots showed a nonzero range across their five pixels; **16/30** were zero at all five points. These are **five sampled CHM values**, not complete 100-station environmental distributions and not observations of genus-specific habitat use. A zero canopy pixel does not imply no shrub/grass habitat.

An original-day historical location check validated **1,740/1,740 five-anchor day comparisons**. A subsequent 3,000-station, 34,800 station×capture-day source audit remains **STOP** at the prerequisite REST–GraphQL historical record equivalence gate (latest attempt 22 October 2026). Published non-E5 positional uncertainties remain incomplete and selected 2022–24 aerial imagery is not event-year matched to the 2015–24 capture-day subset or the wider NEON source universe. We therefore do **not** regress genus recurrence on CHM, nor infer competition, habitat filtering or calibrated detection effects from these anchor data.

## Results

### Corrected recurrence in geographically repeated NEON sites

The original source population and its genus/station margins remained identical through the sampler correction. The revised mean equally weighted physical-site Z was **+0.794663773** in **58 seasonal comparisons nested in 14 sites**, with **11/14** positive means. The 12-site source-disjoint sensitivity retained **46 comparisons**, **10/12** positive site means and corrected mean Z **+0.843161730**. The corresponding earlier accepted-swap-clock Z values (+0.800742 and +0.849774) are historical, not equal-weight additional findings.

| Corrected fixed-margin analysis | Full source cohort | No re-used seasonal source keys |
|:--|--:|--:|
| Independent physical sites | 14 | 12 |
| Consecutive-season comparisons | 58 | 46 |
| Positive site means | 11 | 10 |
| Mean physical-site Z | +0.794664 | +0.843162 |
| Independent-unit null exceedances / 100,000 | 0 | 0 |
| Independent-unit conditional Monte Carlo +1 p | 0.000010 | 0.000010 |
| Within-site rank-coupled exceedances / 20,000 | 24 | 41 |
| Rank-coupled conditional Monte Carlo +1 p | **0.001250** | **0.002100** |

Both 100,000-draw probabilities are **simulation resolution floors**, not exact tail probabilities. The comonotone-coupled p-values apply only to the stated dependency stress. They are not multiple independent tests or proof that all conceivable site-joint null models have been rejected.

### Source-based habitat contrast remains unresolved

At 30 original plots, the five independently named CHM station points yielded within-plot nonzero five-anchor height ranges at **14 plots**, including **three** for which E5 alone was zero. Thus one monumented central point cannot universally represent the available mapped canopy variation across a plot. However, 16 plots had zero CHM at all five sampled anchors and no comparable year-aligned ground-cover observations. **No statistical association between genus recurrence and CHM was calculated**, and no habitat effect is established by the anchor heterogeneity.

### Independent-system interpretation

The pre-existing San Jacinto species-level positive recurrence result arose from a distinct California trapping programme, while the corrected continental NEON finding concerns genus-level occupancy. They jointly motivate the prediction that taxon-associated observed spatial structure can be reconstructed despite observed identity change. They **do not** constitute 20 independent physical NEON-like sites or prove one common species-level mechanism. San Jacinto remains secondary until its null/dependence checks are reviewed.

## Discussion

### The positive ecological claim is about spatial reassembly, not movement measurement

The empirical finding is stronger than simple contemporaneous segregation: after removing shared observed tags, **the correspondence between taxon identity and named locations persists across seasons beyond fixed genus and station-occupancy margins**. This shows that observing exactly the same marked individuals in both seasons is **not necessary** to see a repeated taxonomic spatial signature. It does **not** show that the real population completely turned over, that those positions form exclusive territories, or that the environment causally determines them.

### Three rival biological explanations and falsifiable implications

**H1 — stable local resource/habitat template:** Different individuals of a lineage select similar covered/sheltered/resource locations, generating repeated taxon–station associations. A properly historical, independently mapped station-level habitat layer would predict habitat-specific recurrence beyond generic station occupancy. Temporal changes in measured habitat should precede or co-vary with spatial rearrangement. Current CHM five-point coverage is not sufficient for this inference.

**H2 — persistent lineage-specific catchability:** Species/genera differ in capture probability at stations with stable placement, trap features, bait access, or behavioural responses. This could recreate the entire observed signal without corresponding true-use differences. The discriminating prediction is that lineage recurrence substantially attenuates when measured trap operating effort, independent detection estimates and non-trap location observations are modelled; fixed-fixed station genus richness alone does not control genus-specific detection.

**H3 — biotic interactions/dynamic sorting:** Genus identity at stations may recur because residents, conspecifics or competitors alter occupancy of neighbours. This predicts changes in spatial taxon relationships associated with independently measured competitor state **after** habitat and detection adjustment. The historical fixed-total F/C substitution design lacks conservative directly matched states and **cannot** currently identify this cause.

These are alternatives, not a post hoc ranking. A persistent template may also be a combination of stable habitat, phenotypic tendencies, historic community state and observation processes. The positive pattern alone does not adjudicate them.

### What is novel, and what is not

Spatially segregated rodent assemblages and stable habitat association are established in previous literature. We therefore avoid first-ever claims about rodent partitioning, seasonality, fixed-fixed randomization, or community resilience. The contribution is a **sequential design that excludes shared detected individual identities and then tests geographic repetition of the remaining lineage-associated trap-location pattern**. It is a bounded ecological observation about how spatial organization can reappear in sampled communities.

### Limits, corrections and robustness interpretation

The conditional fixed-margin null captures genus-level prevalence and shared station activity but cannot neutralize stable genus-dependent detection, unmeasured habitat or source reconstruction errors. The main NEON test has a correctly targeted finite-state stationary randomization after correction, but within-site dependence is handled only via a model-based stress calibration, not exact biological generative modeling. The source-disjoint two-site deletion reduces season-key reuse, not all temporal autocorrelation or the ecological nonindependence of stations.

An unobserved animal can survive from season to season without being caught twice. A reused, corrupted or ambiguous field tag also limits a demographic reading. The results are at genus resolution in NEON; environmental station coordinates are neither time-historically validated for all 3,000 names nor known precise to 1 m because the rasters are 1 m. We avoid inferring competition, territory, stable true home range, true individual replacement or genotype-defined species sorting.

The former multi-genus abundance–within/among-individual space-use hypothesis **failed** its frozen 6-of-8-positive-genus generality threshold (5 positive); *Peromyscus* subsequent support did not confirm the sign; conservative same-total F/C directly matched pairs were absent; external MOSA W/B effects remain sealed. None are converted into a successful result by the seasonal recurrence finding.

## Conclusion

The corrected, source-fixed NEON evidence supports an ecological *pattern*: **genus-associated nominal trap positions recur across adjacent seasons among different observed marked small mammals**. The spatial signature remains positive after fixing the invalid accepted-only-swap null and removing both sites with season-reuse dependence. This identifies a reproducible level of observed community spatial structure above the persistence of particular **detected** animals, while leaving the relative roles of persistent microhabitat, taxon-specific detection and biotic sorting unresolved.

## Figure and submission gates

- **Figure 1:** clearly labelled schematic distinguishing repeated capture of the same tag from recurrence among nonshared observed tags; illustrative, not a simulated biological mechanism presented as data.
- **Figure 2 (corrected and source-backed):** [Corrected NEON site-recurrence figure](figures/neon_crossseason_genus_site_means_corrected_v0_3.svg) plots all 14 sorted original physical-site means and the 12 source-disjoint means from the SHA-256-verified correction artifact. Each panel is separately ranked, so vertical ranks are not matched site identities. The older `neon_crossseason_genus_site_means_v1.svg` was based on the obsolete accepted-only sampler and **must not** be used for current inference. No biological identifiers are exported.
- **Figure 3:** show full 14-site and source-disjoint 12-site corrected results, with 100,000 product-null and 20,000 rank-coupled **null reference distributions** clearly labelled as nonindependent post-result sensitivity analyses. Do not show null reference ranges as confidence intervals.
- **Secondary San Jacinto figure:** present distinct species-level California results separately, subject to a new independent sampling and dependence audit. Do not merge its p-value with NEON.

**Submission remains HOLD** until independent review of corrected null mixing/site dependence, observation-identity linkage, public-source reproducibility, and an explicit decision whether habitat/detection must be established for the selected journal. This draft alone does not lift the hold.

## Reproducibility and priority sources

1. Original source and preregistration: `docs/NEON_CROSS_SEASON_GENUS_SPATIAL_TEMPLATE_DESIGN_20261019.md`; original historical results retained for provenance only.
2. **Current numerical record:** `results/neon_uniform_null_correction_receipt_20261020.json`; `analysis/neon_proposal_clock_v2.py`; `analysis/run_neon_uniform_null_correction_v2.py`; verified Actions [39370044411](https://github.com/zuizui0223/neon/actions/runs/39370044411).
3. **Current correction explanation:** `manuscript/NEON_SPATIAL_TEMPLATE_CORRECTION_ADDENDUM_20261020.md`.
4. Post-result habitat **source-only** measurements: `docs/NEON_HABITAT_LINKAGE_CURRENT_STATE_20261020.md`, `results/neon_five_anchor_chm_source_receipt_20261020.json`, `results/neon_dated_five_anchor_feasibility_receipt_20261021.json`.
5. Full historical locations pending: `docs/NEON_3000_DATED_STATION_GRAPHQL_SOURCE_GATE_20261021.md`, Actions [39721738876](https://github.com/zuizui0223/neon/actions/runs/39721738876) — STOP at 5-name REST/GraphQL preflight, not evidence of a biological lack of habitat.
6. California source: `results/san_jacinto_crossseason_ecological_comparator_receipt_20261019.json` (separate branch `ecology/san-jacinto-transition-niche-v1`, historical; not independently corrected with NEON 20 October workflow).
7. Goldingay, R. L. & Price, M. V. (1997), *Conservation Biology* 11:708–717, doi:10.1046/j.1523-1739.1997.95480.x.
8. Chock, R. Y. et al. (2022), *Oecologia* 198:553–565, doi:10.1007/s00442-021-05104-5.
9. NEON source DP1.10072.001: https://data.neonscience.org/data-products/DP1.10072.001. San Jacinto data: https://doi.org/10.6084/m9.figshare.18295520.v1.
