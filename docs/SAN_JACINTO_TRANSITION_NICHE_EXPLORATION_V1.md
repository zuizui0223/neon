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


---

# Stage 3 outcome — published 32-unit reproduction stopped by source mismatch

The public Figshare capture file was independently audited after the 32-unit reproduction gate failed.

The audit found:

- all focal date strings parse successfully;
- deer mouse (PEMA) is present in all 32 grid-seasons, consistent with the paper;
- 30 grid-seasons contain at least 3 focal species;
- **grid 3 winter** contains only PEMA and SKR in the public capture file;
- **grid 7 winter** contains only PEMA and SKR in the public capture file.

This conflicts with the published Methods statement that all 32 spatial matrices contained 3–6 species. The first correct public-data reconstruction on the 30 supported units recovered **8 segregated and 0 aggregated** grid-seasons, matching the published headline count of segregated units but not the stated denominator.

The frozen Stage-3 exact reproduction gate therefore remains failed. Reduced temporal representations are not interpreted under Stage 3.

---

# Stage 4 — public-data-supported temporal scale decomposition

**Status:** adaptive route frozen after the Stage-3 source audit and before NIGHT-FIRST or ANCHOR SIM9 outcomes are opened.

## Why this route is separate

Stage 4 does not redefine the failed 32-unit reproduction. Its inferential universe is explicitly the subset of grid-seasons for which the deposited public capture data support the published matrix requirement of at least 3 focal species.

This subset was determined from species-support counts only, without inspecting any NIGHT-FIRST or ANCHOR C-score or SIM9 result.

## Fixed eligible universe

Include the **30 grid-seasons** with at least 3 focal species in the ALL-capture public-data matrix.

Exclude only:

- grid 3 winter;
- grid 7 winter.

No other unit may be removed.

## ALL reference gate

Using the corrected public-data ALL representation and EcoSimR SIM9 exactly as in Stage 3:

- all 30 eligible units must be analyzable;
- exactly **8** must be above their 97.5th percentile null bound;
- **0** must be below the 2.5th percentile.

This reference result has already been observed during Stage-3 debugging and is therefore a **reconstruction/sanity condition, not a new hypothesis test**.

The eight ALL-segregated grid-seasons define the fixed reference set (S_{ALL,30}).

## Unopened primary comparison

Only after the ALL reference gate passes, run the same EcoSimR SIM9 null on:

1. **NIGHT-FIRST** — earliest valid trap per individual per calendar night;
2. **ANCHOR** — one Stage-2 seasonal medoid of NIGHT-FIRST traps per individual.

These reduced-representation SIM9 outcomes have not been opened in any prior successful route.

Use 5,000 randomizations, burn-in 500, and deterministic seed family beginning at **2026100504**.

## Frozen temporal-scale classification

For each reduced representation, retention is the fraction of the eight ALL-reference segregated units that remain above that representation's own SIM9 97.5th percentile.

Classification:

- **point-anchor sufficient**: ANCHOR retains at least 6/8;
- **between-night footprint**: NIGHT-FIRST retains at least 6/8 but ANCHOR retains fewer than 6/8;
- **within-night records materially contribute**: NIGHT-FIRST retains fewer than 6/8.

No alternative threshold or unit subset will be tried.

## Fixed secondary summaries

Report descriptively:

- total number of segregated / aggregated / null units under each representation;
- exact identities of retained and lost ALL-reference units;
- mean and median SES under each representation;
- Pearson SES correlations ALL vs NIGHT-FIRST and ALL vs ANCHOR;
- row totals and occupied trap counts by representation.

No species-pair decomposition is opened.

## Ecological interpretation

- **Point-anchor sufficient** would mean that one point-like seasonal location per individual carries most of the community segregation.
- **Between-night footprint** would mean that recurring use of multiple locations across nights carries the segregation, while a single point-like individual anchor does not.
- **Within-night records materially contribute** would mean that later positions within nights are required to reproduce most of the published segregation signal.

The last outcome would not distinguish natural movement from capture/release response; it would instead show that the published ecological pattern is partly tied to within-night observation scale.


---

# Stage 4 result — between-night footprint

Stage 4 completed on the separately frozen 30-grid-season public-data universe.

The ALL-capture reference gate passed exactly:

- 30/30 analyzable;
- 8 segregated;
- 0 aggregated;
- 22 null.

The fixed eight ALL-reference segregated units were:

- grid 1 summer;
- grid 4 fall, winter, spring and summer;
- grid 6 fall, winter and summer.

Under the same EcoSimR SIM9 fixed-fixed null:

- **NIGHT-FIRST retained 7/8 = 87.5%** of those units;
- only grid 1 summer was lost;
- no new NIGHT-FIRST unit became significant;
- **ANCHOR retained 0/8**;
- no ANCHOR unit became significant.

The prospectively frozen classification is therefore:

`between_night_footprint`.

Across all 30 supported units:

- ALL vs NIGHT-FIRST SES correlation = **0.9474**;
- ALL vs ANCHOR SES correlation = **0.1088**;
- mean SES = 2.073 (ALL), 1.413 (NIGHT-FIRST), -0.103 (ANCHOR).

A fully separate implementation reproduced the same eight ALL units, the same seven NIGHT-FIRST retained units, zero ANCHOR retained units, the same retention fractions, the same classification and the same reported SES summaries/correlations.

## Stage-4 ecological conclusion

The relevant ecological scale is neither the within-night movement step nor a one-point individual seasonal centre.

> **The spatial segregation signal is carried by recurring multi-location use across nights.**

Later same-night recaptures are largely unnecessary for reproducing the published public-data segregation pattern: retaining only the first location of each individual-night preserves seven of eight reference signals.

By contrast, collapsing each individual's multi-night footprint to one seasonal point removes all eight reference signals.

This supports a scale-localization statement rather than a causal mechanism claim:

> **Community spatial partitioning can reside in the distributed footprint of repeated space use, even when it is not encoded in short-term movement direction or in a single spatial centre.**

The result does not identify whether those recurring footprints are generated by microhabitat selection, burrow placement, resources, territoriality, longer-term competition, repeated foraging routes or another persistent spatial process.

No species-pair decomposition, alternative retention threshold, alternative anchor definition or habitat surrogate is opened after this result.

See `docs/SAN_JACINTO_TEMPORAL_SCALE_ECOLOGY_INTERPRETATION_V1.md` for the full biological interpretation and claim boundary.


---

# Stage 5A — frozen temporal persistence test

**Status:** support audit complete; primary outcome unopened at this freeze.

## Why Stage 5 is needed

Stage 4 showed that the public-data spatial-segregation signal survives when later same-night recaptures are removed, but disappears when each individual is collapsed to one seasonal point.

That result localizes information to the multi-night representation, but it leaves an important alternative explanation:

> NIGHT-FIRST may succeed simply because it contains more spatial observations than a one-point representation.

Stage 5A therefore asks whether the species-specific NIGHT-FIRST spatial map is **temporally persistent** within a season.

A positive result is required before describing the Stage-4 footprint as a persistent ecological structure rather than merely a deeper sample.

## Support-only audit

Before any trap overlap or persistence statistic was opened, the 30-unit public-data universe was split by unique calendar nights within each grid-season:

- sort unique dates chronologically;
- for an even number of dates, assign the first half to EARLY and second half to LATE;
- for an odd number, discard the single middle date and assign equal numbers of dates to EARLY and LATE.

All 30 units had at least four unique sampling nights.

For the fixed eight Stage-4 ALL-segregated reference units:

- **8/8** have at least three focal species present in both halves;
- **8/8** have at least three common focal species with at least two NIGHT-FIRST records in each half.

No persistence outcome was inspected in this support audit.

## Primary universe

Primary inference is restricted to the eight Stage-4 reference units fixed before Stage 5:

- grid 1 summer;
- grid 4 fall, winter, spring and summer;
- grid 6 fall, winter and summer.

Within each unit, retain focal species that:

1. occur in both EARLY and LATE; and
2. contribute at least two NIGHT-FIRST records in each half.

At least three such species are required. The support audit established that all eight reference units satisfy this rule.

## Spatial persistence statistic

For each unit construct binary species × trap matrices:

- (E): EARLY NIGHT-FIRST trap use;
- (L): LATE NIGHT-FIRST trap use.

Restrict columns to traps used by at least one retained species in LATE. EARLY use at traps that are absent from the entire LATE community cannot contribute to repeated use and is therefore irrelevant to the matched overlap statistic.

Define the observed matched species-trap persistence as

[
P_{obs}=\sum_s\sum_j E_{sj}L_{sj},
]

the total number of species × trap incidences that recur in both halves for the **same species**.

## Fixed-fixed late-season null

EARLY matrix (E) remains fixed.

Randomize the LATE matrix with EcoSimR's SIM9 curveball step while preserving exactly:

- every retained species' LATE trap-occupancy total (row sums);
- every LATE trap's species-richness total (column sums).

Use:

- burn-in = **500** curveball steps;
- null replicates = **5,000**;
- deterministic seed family beginning at **2026100505**, unique by reference unit.

For each randomized LATE matrix (L_b), calculate

[
P_b=\sum_s\sum_j E_{sj}L_{b,sj}.
]

For unit (u),

[
Z_u=(P_{obs,u}-\mu_{u})/\sigma_u,
]

where (mu_u) and (sigma_u) are the null mean and SD. Units with zero null SD are reported but excluded from standardized aggregation.

## Global primary test

Define

[
T_{obs}=\operatorname{mean}_u Z_u.
]

For each synchronized null replicate (b),

[
T_b=\operatorname{mean}_u (P_{b,u}-\mu_u)/\sigma_u.
]

The one-sided Monte Carlo p-value is

[
p=(1+\#\{T_b\ge T_{obs}\})/(5000+1).
]

Stage 5A supports **persistent species-specific multi-night footprints** only if all three pre-declared conditions hold:

1. at least **6 of 8** reference units have non-zero null SD;
2. at least **6 of 8** reference units have (Z_u>0);
3. (T_{obs}>0) and one-sided Monte Carlo (p<0.05).

Otherwise the persistence claim stops.

## Secondary generality analysis

The same frozen statistic may be reported descriptively for the broader public-data units having at least three common species with at least two NIGHT-FIRST records per species in each half. The support audit identified **22** such units.

This broader set is not allowed to rescue the eight-reference-unit primary test.

Report descriptively:

- number of positive-(Z) units;
- mean and median (Z);
- reference vs non-reference distributions;
- early/late row totals and late column totals.

No species-pair decomposition is opened.

## Interpretation boundary

A positive Stage-5A primary result would support:

> **In the grid-seasons where community segregation is strongest, species-specific trap-use footprints recur from the early to the late half of the season beyond what is expected from species occupancy and trap richness alone.**

Combined with Stage 1 and Stage 4, that would justify the stronger biological statement that spatial segregation is associated with **persistent species-specific multi-night space-use footprints**, rather than continual within-night directional avoidance.

It would still not identify whether persistence is caused by microhabitat selection, burrow placement, resources, territoriality or competition.


---

# Stage 5A result — seasonal persistence supported

The frozen temporal-persistence primary test passed all pre-declared criteria:

- informative Stage-4 reference units: **8/8**;
- reference units with positive standardized persistence: **8/8**;
- global mean standardized persistence: **T = 4.0908870811**;
- one-sided Monte Carlo **p = 0.000199960008**.

Decision:

`support_persistent_species_specific_multi_night_footprints`.

Across the broader 22-unit support set, reported descriptively only, **20/22** units had positive (Z), with mean (Z=2.6610) and median (Z=2.6365).

Thus the Stage-4 NIGHT-FIRST result is not merely a deeper spatial sample. In every fixed segregated reference unit, the same species reused the same trap locations from the early to late half of the season more strongly than expected after preserving LATE species trap-occupancy totals and LATE trap species richness.

This establishes persistence at the **community species × trap** level. It does not by itself show that different conspecific individuals share similar footprints; Stage 5B tests that separate individual-level bridge.


---

# Stage 5B — individual multi-night footprint assortativity

**Status:** frozen after the Stage-4 between-night-footprint classification and before any Stage-5 overlap outcome is calculated.

## Biological question

Stage 4 localized the published community segregation signal to recurring multi-location use across nights: NIGHT-FIRST retained 7/8 reference segregation signals, whereas a single seasonal point per individual retained 0/8.

Stage 5B asks whether that matrix-level result is visible at the individual ecological level:

> **Do individuals of the same species repeatedly use more similar multi-night spatial footprints than individuals of different species?**

A positive result would identify species-specific recurring-use domains as the individual-level structure underlying the between-night footprint.

## Individual footprint

Use the same deposited capture file, focal six species and season definitions as Stage 4.

For each species × grid × season × individual:

1. retain the earliest valid trap on each calendar night;
2. require observations on at least **2 distinct nights**;
3. define the individual's multi-night footprint as the **set of distinct NIGHT-FIRST trap flags**.

No later same-night capture enters the footprint.

## Unit eligibility

Start from the fixed Stage-4 public-data universe of 30 grid-seasons.

Within a grid-season, a species is eligible only if at least **3 individuals** have multi-night footprints. A grid-season enters Stage 5B if at least **3 focal species** are eligible.

These support rules are fixed without inspecting footprint overlap.

The route requires at least **8 informative grid-seasons** with non-zero permutation-null variance; otherwise it stops for support.

## Primary individual-level statistic

For every pair of eligible individuals in a unit, calculate footprint Jaccard similarity

[
J_{ij}=|F_i\cap F_j|/|F_i\cup F_j|.
]

For unit (u), define

[
D_u=\overline{J}_{\mathrm{conspecific}}-\overline{J}_{\mathrm{heterospecific}}.
]

Pair weighting is used within a unit; the later global statistic weights grid-seasons equally.

## Footprint-size-stratified label null

The null keeps every individual footprint exactly fixed in space.

Within each grid-season, species labels are permuted **only among individuals with the same number of distinct traps in their footprint**. Thus the permutation preserves:

- every observed footprint geometry;
- every individual's footprint size;
- the number of individuals assigned to each species within each exact footprint-size stratum;
- the grid, season and sampling footprint.

It destroys only the association between species identity and **where same-sized individual footprints occur**.

Use **10,000** joint permutations with seed **2026100505**.

For each informative unit, let (mu_u,sigma_u) be the null mean and SD of (D_u), and define

[
Z_u=(D_u^{obs}-mu_u)/sigma_u.
]

The global statistic is

[
T_{footprint}=\operatorname{mean}_u Z_u.
]

For joint permutation replicate (b), compute the same global mean standardized statistic (T_b). The one-sided Monte Carlo p-value is

[
(1+#\{T_b\ge T_{footprint}\})/(B+1).
]

## Frozen decision

Support for species-specific recurring-use domains requires:

- at least **8** informative grid-seasons;
- (T_{footprint}>0); and
- one-sided Monte Carlo (p<0.05).

Otherwise Stage 5B stops. No alternative overlap metric, footprint-size binning, minimum-night rule or species-pair decomposition will be opened after seeing the result.

## Fixed secondary summaries

Report descriptively:

- number of eligible and informative grid-seasons;
- number of multi-night individuals overall and by species;
- exact footprint-size distribution;
- observed conspecific and heterospecific mean Jaccard by unit;
- (D_u), null mean, null SD and (Z_u) by unit;
- fraction of units with positive (D_u);
- correlation between unit (Z_u) and Stage-4 NIGHT-FIRST SIM9 SES.

## Interpretation boundary

A positive result would support:

> **Species identity is associated with the spatial placement of repeated multi-night footprints even after controlling exactly for footprint size.**

Combined with Stage 1 and Stage 4, that would support an ecological hierarchy in which community segregation is encoded in persistent species-specific space-use domains rather than in the direction of each within-night move or in a single point centre.

It would not identify whether those domains are produced by habitat, burrows, resource distributions, territoriality or competition.


---

---

# Stage 5B result — individual species-specific footprints supported

The independently frozen individual-level test also passed.

Support:

- **928** individuals were observed on at least two nights before unit filtering;
- all six focal species contributed multi-night individuals;
- **22** grid-seasons met the pre-declared species/individual support rule;
- **22/22** had non-zero permutation-null variance.

Primary result:

- global mean standardized footprint assortativity: **T = 2.3148618332**;
- one-sided Monte Carlo **p = 0.000099990001**;
- decision: `support_species_specific_multinight_footprints`.

The null permuted species labels only among individuals having the **exact same number of distinct traps** in their footprint. Therefore this result is not explained by one species merely having larger or more intensively sampled footprints.

Across the 22 eligible units:

- **20/22** had a positive raw conspecific-minus-heterospecific Jaccard difference;
- mean conspecific footprint Jaccard = **0.05760**;
- mean heterospecific footprint Jaccard = **0.03446**;
- mean raw difference = **0.02313**;
- unit-level footprint-assortativity (Z) correlated with Stage-4 NIGHT-FIRST SIM9 SES at **r = 0.6943**.

The individual-level result therefore supplies the missing bridge beneath the community matrix:

> **Different individuals of the same species repeatedly use more similar multi-night spatial footprints than equally broad footprints assigned across species.**

Together, Stages 5A and 5B show that the between-night signal is both temporally persistent at the species × trap level and organized among individuals by species identity.

The current ecological conclusion is:

> **Spatial niche partitioning in this rodent guild is encoded in persistent, species-specific multi-night space-use footprints, while neither within-night movement direction nor a single seasonal point per individual carries the community segregation signal.**

Mechanism remains unresolved: habitat selection, burrow/refuge placement, resource distributions, territoriality and longer-term competitive sorting remain viable causes. No species-pair decomposition or alternative overlap metric is opened.



---

# Stage 7 — persistence across complete individual turnover

**Status:** support audit completed; primary test frozen before any post-turnover trap-overlap outcome is opened.

## Biological question

Stage 5 showed that the same species reuse the same trap locations from the early to late half of a season, and the individual-footprint test showed that conspecific individuals use more similar multi-night footprints than heterospecific individuals. Those results leave one biologically important ambiguity:

> **Is the seasonal spatial memory carried only by the same site-faithful individuals, or does a species-specific spatial template persist when the individuals themselves turn over?**

Stage 7 removes every individual observed in both seasonal halves before measuring persistence.

## Fixed universe and temporal split

Use only the eight fixed Stage-4 segregated reference grid-seasons:

- 1|summer
- 4|fall, 4|winter, 4|spring, 4|summer
- 6|fall, 6|winter, 6|summer

Use NIGHT-FIRST records only and exactly the same chronological EARLY/LATE split as the frozen Stage-5 temporal-persistence analysis. If a grid-season has an odd number of unique sampling nights, discard the single middle night.

## Complete individual-turnover rule

Within each reference grid-season, define a bridge individual as a species × individual ID observed at least once in both EARLY and LATE.

Remove every bridge individual from **both halves**, including all of its NIGHT-FIRST records.

The remaining EARLY and LATE data therefore contain disjoint individual identities by construction.

## Species eligibility after turnover

A focal species enters a grid-season if, after bridge removal, it retains:

- at least **1 distinct EARLY-only individual**, and
- at least **1 distinct LATE-only individual**.

The support-only audit was opened before any post-turnover spatial-overlap outcome. All 8/8 reference units retain at least three such species.

No stricter individual-count threshold will be tried after outcomes are opened.

## Primary statistic and fixed-fixed null

For each reference unit, build EARLY and LATE species × trap presence/absence matrices from the disjoint-individual NIGHT-FIRST records of the eligible species.

Use the same matched species × trap persistence statistic as Stage 5:

[
P_u = sum_{s,j} I(E_{sj}=1 land L_{sj}=1).
]

Hold EARLY fixed. Randomize the LATE matrix using the EcoSimR curveball / SIM9 fixed-fixed algorithm, preserving:

- each species' LATE number of occupied traps;
- each trap's LATE species richness.

Use **10,000** null replicates after **500** burn-in swaps, with deterministic seed family beginning at **2026100507**.

For informative unit (u),

[
Z_u=(P_u-mu_u)/sigma_u.
]

The global statistic is the equally weighted mean across informative reference units,

[
T_{turnover}=operatorname{mean}(Z_u).
]

Use joint replicate index across units to obtain the global null and a one-sided Monte Carlo upper-tail p-value with plus-one correction.

## Frozen decision

Support for a species-level spatial template beyond individual site fidelity requires all of:

- at least **6 of 8** reference units with non-zero null SD;
- at least **6 of 8** reference units with (Z_u>0);
- (T_{turnover}>0);
- global one-sided Monte Carlo (p<0.05).

Otherwise Stage 7 stops and the conservative conclusion is that the observed seasonal persistence cannot be separated from persistence of the same individuals.

## Fixed secondary summaries

Report descriptively:

- bridge individuals removed by unit and species;
- EARLY-only and LATE-only individual counts by species;
- observed and null matched species × trap overlap;
- (Z_u) and unit p-values;
- ratio of post-turnover (Z_u) to the original Stage-5 persistence (Z_u) where both are finite.

No species-pair decomposition, alternative turnover definition, relaxed species threshold, alternative overlap metric or habitat surrogate will be opened after seeing the result.

## Interpretation boundary

A positive Stage-7 result supports:

> **Species-specific spatial use recurs across seasonal halves even when no individual contributes observations to both halves.**

That would locate spatial memory above individual identity, consistent with a persistent species/community-level spatial template.

It would not identify whether the template is caused by habitat, burrow/refuge distributions, resources, territoriality, social processes, competition or another persistent grid-scale constraint.
