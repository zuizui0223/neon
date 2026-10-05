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
