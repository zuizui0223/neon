# San Jacinto transition-niche ecology exploration v2

**Status:** Stage 0 complete; Stage 1 v3 frozen before transition direction / distance outcomes are opened  
**Parent MEE commit:** `265b338521da52d8379f851ca6383dde96e7812c`  
**Ecology branch:** `ecology/san-jacinto-transition-niche-v1`

## Biological question

The published San Jacinto study found temporal overlap but spatial segregation among six granivorous rodent species, together with species-specific microhabitat associations. The new question is:

> **How can spatial niche partitioning persist when individuals move among multiple trap locations within the same night?**

The hypothesis is not that rodents move little. It is that **movement direction is structured**, so substantial movement can occur without erasing spatial segregation.

This branch does not alter, rescue or reclassify any frozen claim in the MEE temporal-aliasing programme.

## Stage 0 — completed without opening transition outcomes

The Figshare record contains two files: `year round trap data.csv` and `Metadata.xlsx`. The capture CSV contains the six focal community species and no trap-level vegetation or soil columns. No separate environmental file is deposited in this Figshare record.

The six focal species codes and available consecutive within-night transition counts are:

- CHFA: 963
- DKR: 658
- LAPM: 384
- PEER: 132
- PEMA: 664
- SKR: 1474

Incidental codes `P` and `REME` are not members of the focal six-species analysis and are excluded from Stage 1.

Stage 0 did **not** calculate transition distances, transition directions, habitat changes, transition kernels or movement effects on spatial segregation.

## Stage 1 — frozen movement-direction test

### Ecological estimand

Stage 1 asks whether the **direction** of observed within-night movement preserves spatial segregation more strongly than expected if animals made moves of exactly the same length in random feasible directions.

This directly separates movement magnitude from movement direction.

### Observation unit

For each focal species, valid records are grouped by grid × individual × calendar date and ordered by recorded check time. Nights with at least two valid records contribute one FIRST trap and one LAST trap.

The study seasons follow the published definitions:

- Fall: August–October
- Winter: November–January
- Spring: February–April
- Summer: May–July

The analysis unit is grid × season.

### Unit eligibility

Within each grid × season, a species is included only if it contributes at least **5 repeat-capture individual-nights**; all valid singleton nights from that same eligible species are then retained as fixed background in its C-score occupancy. A grid-season is eligible if at least **3 focal species** meet the repeat-night requirement.

No eligibility rule uses observed movement distance, direction or the resulting segregation statistic.

### Spatial segregation statistic

For each eligible grid-season, construct a species × trap presence/absence matrix from **all valid captured individual-nights** of the eligible species, so that the estimand remains aligned with the published grid-season spatial-partitioning analysis.

- A singly captured individual-night contributes its one observed trap and is identical in FIRST, LAST and every randomization.
- A repeat-capture individual-night contributes its FIRST trap in the FIRST representation, its LAST trap in the observed LAST representation, and a randomized distance-matched destination in each null replicate.
- Nights with more than two captures are still represented by their earliest and latest valid traps; intermediate checks are not opened as an alternative endpoint in Stage 1.

Thus the null changes only the direction assigned to observed repeat-night displacement while leaving the full background of singly observed animal-nights fixed.

For species pair A,B, use the published checkerboard C-score

[
C_{AB}=(r_A-S)(r_B-S),
]

where (r_A) and (r_B) are numbers of occupied trap locations and (S) is the number shared. The community statistic is the mean pairwise C-score across the eligible species in that grid-season.

Compute this statistic for both FIRST and observed LAST endpoints.

### Distance-matched directional null

For every individual-night:

1. keep species, grid-season and FIRST trap fixed;
2. calculate the observed FIRST-to-LAST squared grid displacement (d^2=Delta x^2+Delta y^2);
3. enumerate **all traps on the same 7 × 7 grid** lying at that exact (d^2) from the FIRST trap;
4. choose one candidate destination uniformly at random.

Thus every randomized move has the same origin and exact movement length as observed, while only its feasible direction is randomized. Grid-edge geometry is automatically preserved. Zero-length movements are retained but have one possible destination and therefore contribute no directional randomization.

Use **10,000** joint randomizations with seed **2026100501**.

### Primary statistic and decision

For each eligible grid-season (u), let (C_u^{obs}) be the observed LAST community C-score and let (mu_u,sigma_u) be the mean and SD of its distance-matched null distribution. Units with (sigma_u=0) are reported but excluded from standardized aggregation.

Define

[
Z_u=(C_u^{obs}-mu_u)/sigma_u
]

and the global statistic

[
T_{obs}=operatorname{mean}_u Z_u.
]

For each randomization (b), calculate

[
T_b=operatorname{mean}_u (C_{ub}-mu_u)/sigma_u.
]

The one-sided Monte Carlo p-value is ((1+#{T_bge T_{obs}})/(B+1)).

The route is considered supported only if:

- at least **4** grid-seasons have non-zero null variance;
- (T_{obs}>0); and
- the one-sided Monte Carlo (p<0.05).

Otherwise the ecological route stops at Stage 1. A null result will not trigger a search over alternative movement metrics.

### Design correction made before outcome opening

Stage 1 v2 initially defined C-score only on repeat-capture nights. Before any transition distance, direction, null C-score or observed movement effect was computed, this was corrected to retain singleton nights as fixed background. The correction aligns the new endpoint with the published grid-season species × trap spatial-partitioning estimand and prevents the ecological claim from being restricted to the repeat-observed subset. The randomization still acts only on repeat-night movement directions.

### Secondary quantities fixed in advance

Report, without additional confirmatory claims:

- number of eligible grid-seasons;
- number and fraction of individual-night moves with more than one feasible direction;
- FIRST C-score, observed LAST C-score and null mean by grid-season;
- observed LAST minus FIRST C-score;
- null-expected LAST minus FIRST C-score;
- grid-season (Z_u) values.

Species-pair decomposition is **not opened in Stage 1**. It requires a separate freeze if the primary test passes.

## Interpretation boundary

A positive Stage-1 result would support:

> **For moves of the same length from the same starting locations, observed movement directions preserve more interspecific spatial segregation than feasible random directions.**

It would not show that competition itself causes the direction choice, that handling has no influence, or that capture-to-recapture segments are complete natural trajectories. Habitat filtering, species interactions and capture response remain candidate mechanisms.

The ecological principle being tested is therefore:

> **Spatial partitioning in a mobile guild can be maintained by where movements are directed, not by suppression of movement magnitude.**


---

# Stage 2 — adaptive but prospectively frozen scale-localization test

**Status:** opened only after the frozen Stage-1 movement-direction test stopped. No Stage-2 anchor outcome has been calculated at the time of this freeze.

## Why Stage 2 is a distinct question

Stage 1 rejected the hypothesis that within-night movement **direction**, conditional on exact movement length and origin, continually maintains community-level spatial segregation.

Stage 2 therefore asks a different ecological question:

> **Is species segregation already encoded in where individuals are seasonally anchored in space, before later within-night movements are considered?**

This is a scale-localization test, not a rescue of Stage 1.

## Individual spatial-anchor proxy

Within each grid × season, for every focal individual:

1. group valid captures by calendar night;
2. retain only the **earliest valid trap of each night**, thereby excluding all later within-night recapture positions used in Stage 1;
3. among the retained nightly-FIRST traps, choose the observed trap that minimizes the sum of squared 7 × 7 grid distances to all retained nightly-FIRST traps;
4. break medoid ties by greatest observed frequency among nightly-FIRST traps and then lexicographically.

Every individual therefore contributes exactly one seasonal anchor proxy. Individuals captured on only one night contribute that one trap; no minimum recapture count is imposed because the null conditions on the complete observed set of individual anchor proxies.

## Grid-season inclusion

Use the same published seasons (fall Aug–Oct, winter Nov–Jan, spring Feb–Apr, summer May–Jul).

Within each grid-season, include every focal species represented by at least one individual anchor proxy. A unit is eligible if at least **3 focal species** are represented.

This rule is fixed without inspecting anchor C-scores or species spatial locations.

## Primary statistic

For each eligible grid-season, build a species × trap presence/absence matrix from the one-anchor-per-individual representation and calculate the same mean pairwise checkerboard C-score used in Stage 1 and the published community analysis.

## Species-label null

Within each grid-season:

- keep the exact multiset of individual anchor locations fixed;
- keep the exact number of individuals assigned to each species fixed;
- randomly permute species labels among individual anchors.

This null destroys species-specific anchor placement while preserving spatial sampling footprint, grid geometry, number of observed individuals, and the observed clustering of anchor locations irrespective of species.

Use **10,000** permutations with seed **2026100502**.

For unit (u), let (C_u^{obs}) be the observed anchor C-score and let (mu_u,sigma_u) be its permutation-null mean and SD. Define

[
Z_u=(C_u^{obs}-mu_u)/sigma_u.
]

Units with (sigma_u=0) are reported but excluded from standardized aggregation.

The global statistic is

[
T_{anchor}=operatorname{mean}_u Z_u.
]

For permutation (b), compute the corresponding global mean standardized statistic (T_b). The one-sided Monte Carlo p-value is

[
(1+#{T_bge T_{anchor}})/(B+1).
]

## Frozen decision

Stage 2 supports species-specific spatial anchoring only if:

- at least **8** grid-seasons have non-zero null variance;
- (T_{anchor}>0); and
- one-sided Monte Carlo (p<0.05).

Otherwise the scale-localization route stops.

## Fixed secondary summaries

Report without separate confirmatory claims:

- number of eligible and informative grid-seasons;
- number of individual anchor proxies overall and by species;
- observed anchor C-score, null mean and (Z_u) by grid-season;
- the same grid-season C-score computed from all capture locations as descriptive context;
- correlation across eligible grid-seasons between anchor-only and all-capture C-scores.

No species-pair decomposition, alternative anchor definitions, habitat surrogates, or threshold search will be opened after seeing the Stage-2 result.

## Interpretation boundary

If positive, Stage 2 would support:

> **Species identity is non-randomly associated with the seasonal spatial locations around which individuals are observed, even after later within-night recaptures are removed.**

Together with a null Stage 1, that pattern would be consistent with spatial niche partitioning arising primarily at a slower individual-placement / space-use-anchor scale rather than being re-created by directional avoidance at each within-night move.

It would **not** identify whether anchor placement is caused by habitat selection, burrow placement, territoriality, past or current competition, or capture-related processes.


---

# Stage 2 result — stopped

The frozen seasonal-anchor test had ample support:

- 1,334 individual anchor proxies;
- 928 individuals observed on at least two nights;
- 30 eligible grid-seasons;
- 30/30 units with non-zero permutation-null variance.

The global anchor statistic was

[
T_{anchor}=-0.0120,
]

with one-sided Monte Carlo (p=0.5315).

Decision:

`stop_no_species_specific_seasonal_anchoring_support`.

This rejects the specific label-shuffle hypothesis that species identity is associated with one point-like seasonal anchor more strongly than expected after conditioning on the observed anchor-location cloud and species individual counts. It does not overturn the published fixed-fixed SIM9 result because the two null hypotheses differ.

---

# Stage 3 — frozen published-null scale decomposition

**Status:** frozen after Stage 2 stopped and before any Stage-3 SIM9 result is calculated.

## Rationale

The published spatial-partitioning result used EcoSimR SIM9, not the individual-label permutation used in Stage 2. SIM9 preserves both species trap-occupancy totals and trap species-richness totals.

Stage 3 therefore first attempts a direct reproduction of the published null analysis, then changes only the temporal representation while keeping the same SIM9 null model.

## Representations

For every one of the published 8 grids × 4 seasons:

1. **ALL** — species × trap presence/absence using every valid capture record, including recaptures. This is the published representation.
2. **NIGHT-FIRST** — species × trap presence/absence using only the earliest valid capture of each individual on each calendar night. Later within-night recaptures are excluded, but repeated use across nights and individuals is retained.
3. **ANCHOR** — species × trap presence/absence using one seasonal spatial-anchor proxy per individual, defined exactly as in frozen Stage 2 from NIGHT-FIRST locations.

The focal six species are CHFA, DKR, LAPM, PEER, PEMA and SKR. In each representation, include every focal species present in that grid-season. Empty trap columns are removed before EcoSimR because the package requires non-empty columns.

## Null model

For each representation × grid-season matrix:

- EcoSimR `cooc_null_model`;
- algorithm = `"sim9"`;
- metric = `"c_score"`;
- 5,000 null replicates, matching the published study;
- burn-in = 500;
- deterministic seed family beginning at **2026100503**, with a unique fixed seed by representation and grid-season.

SIM9 is the fixed–fixed curveball implementation documented by EcoSimR and preserves row and column totals.

For each matrix report observed C-score, null mean, null SD, SES, lower and upper two-tailed 95% null quantiles, and whether the observed value is above, within, or below that interval.

## Reproduction gate

The **ALL** representation is opened first.

The scale-decomposition route is authorized only if ALL reproduces the published headline result:

- all **32** grid-seasons analyzable;
- **8** grid-seasons above the two-tailed 95% null interval (segregated);
- **0** below it (aggregated).

If this exact gate fails, Stage 3 stops and NIGHT-FIRST / ANCHOR results are not interpreted as a reproduction of the published partitioning signal.

## Scale classification if reproduction passes

Let (S_{ALL}) be the set of the 8 reproduced segregated grid-seasons.

For NIGHT-FIRST and ANCHOR, define retention as the fraction of (S_{ALL}) that remains above its own representation-specific SIM9 97.5th percentile.

The ecological scale is classified prospectively as:

- **point-anchor sufficient**: ANCHOR retains at least 75% of (S_{ALL});
- **between-night footprint**: NIGHT-FIRST retains at least 75% of (S_{ALL}) but ANCHOR retains less than 75%;
- **within-night records materially contribute**: NIGHT-FIRST retains less than 75% of (S_{ALL}).

The 75% rule corresponds to retaining at least 6 of the 8 published segregated grid-seasons.

This is a mutually exclusive classification; no alternative threshold will be tried.

## Secondary fixed summaries

Report:

- mean and median SES for each representation across all 32 grid-seasons;
- Pearson correlation of SES between ALL and NIGHT-FIRST and between ALL and ANCHOR;
- counts of newly significant units outside (S_{ALL}), descriptively only;
- per-unit changes in row totals and occupied trap columns across representations.

No species-pair decomposition is opened in Stage 3.

## Interpretation boundary

A NIGHT-FIRST result that retains the published segregation while ANCHOR does not would support a specific temporal-scale statement:

> **Community spatial partitioning is carried by recurring multi-night space-use footprints rather than by a single point-like individual anchor or by later within-night recapture directions.**

A failure of NIGHT-FIRST retention would instead show that later within-night capture locations materially contribute to the published co-occurrence pattern, without identifying whether that contribution is natural movement or handling-related observation process.
