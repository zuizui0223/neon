# Fresh mechanism result: carrier status is a context-dependent spatial state

## Current location

The once-only fresh mechanism response completed on the 11 response-naive sites
SRER, STEI, STER, TALL, TEAK, TOOL, TREE, UKFS, WOOD, WREF and YELL.

All 11 sites were scored; no site was replaced or stopped.

The response result is frozen at fingerprint:

`869f33ce56df5a6a6f69f1dc783f10ddb459616992bb1a6f26f813e14446df07`.

## 1. Prospective primary result: no excess carrier production beyond prevalence

The primary null conditioned on each species' observed number of positive trap nodes.

Observed spatial organization did **not** produce more carriers than count-conditioned random placement:

- median site carrier excess = **-0.0804**;
- positive site effects = **4/11**;
- one-sided exact sign-test p = **0.8867**;
- the frozen decision is **no support for spatial organization beyond prevalence at the declared resolution**.

Across the 68 eligible species × site records there were 29 observed carriers, whereas the site-wide count-conditioned expectation summed to 33.85 carriers.

This is not evidence that spatial organization is absent. It says that the *observed* spatial allocation does not systematically turn a fixed number of positive traps into the declared carrier state more often than random site-wide placement.

## 2. Predeclared grid decomposition: nearly all departure occurs between grids

The secondary predeclared null preserved each species' observed positive-node count **within each mammal grid**.

The additive identity is:

`site-wide carrier excess = between-grid allocation component + within-grid organization component`.

Results:

- median between-grid component = **-0.0804**;
- median within-grid component = **0**;
- sites with positive mean within-grid component = **0/11**;
- one-sided sign-test p for positive within-grid effects = **1.0**.

At the species × site level, the grid-conditioned expected carrier probability equalled the observed binary carrier state exactly in **66/68** records. The remaining two departures were extremely small Monte-Carlo differences.

Thus the declared carrier state is almost completely determined once the **number of positive traps allocated to each grid** is known.

This does **not** establish habitat filtering. NEON grid identity is a spatial stratum and potential habitat proxy, not an environmental measurement.

## 3. The metric is local spatial cohesion, not landscape-wide connectivity

The formal criterion is:

> every positive trap has at least one other positive trap admitted by every declared adjacency criterion.

A species does not need to occupy or connect the whole site. A compact occurrence cluster inside one grid can satisfy the criterion, while a widely distributed species can fail if it has one or more isolated peripheral positives.

The fresh examples make this explicit.

### Strong positive between-grid allocation

- **Perognathus flavescens, SRER**: 6 positive traps, 1 grid; observed carrier = 1; site-wide random expectation = 0.032; grid-conditioned expectation = 1.
- **Perognathus flavus, STER**: 6 positive traps, 1 grid; observed carrier = 1; site-wide expectation = 0.044; grid-conditioned expectation = 1.
- **Microtus montanus, TEAK**: 18 positive traps, 1 grid; observed carrier = 1; site-wide expectation = 0.190; grid-conditioned expectation = 1.

Here, concentration into particular grids strongly increases the carrier probability relative to site-wide random placement.

### Strong negative between-grid allocation

- **Peromyscus eremicus, SRER**: 136 positive traps across 7 grids; observed carrier = 0 although the site-wide count-conditioned expectation = 1.
- **Napaeozapus insignis, STEI**: 201 positives across 6 grids; observed carrier = 0, site-wide expectation = 1.
- **Myodes gapperi, WREF**: 135 positives across 8 grids; observed carrier = 0, site-wide expectation = 0.994.

Thus high prevalence is not sufficient. How positives are allocated among grids can either create or destroy the no-isolated-occurrence property.

## 4. Post-response diagnostic: concentration within occupied grids is the strongest simple descriptor

These diagnostics are exploratory and cannot alter the frozen primary result.

Across 68 eligible records:

| descriptor | carriers | non-carriers |
| --- | ---: | ---: |
| median positive traps | 157 | 21 |
| median occupied grids | 6 | 4 |
| median positive traps / occupied grid | 26.17 | 5.00 |

Pooled descriptive Spearman associations with carrier status were:

- positive-node count: rho = **0.396**;
- occupied-grid count: rho = **0.133**;
- positive nodes per occupied grid: rho = **0.520**.

More importantly, the median **within-site** Spearman association was:

- positive-node count: rho = **0.579**;
- occupied-grid count: rho = **0.324**;
- positive nodes per occupied grid: rho = **0.707**.

The positive-nodes-per-grid association was positive in 9 of 11 sites.

The current mechanistic candidate is therefore not simply "a common species becomes a carrier". It is closer to:

> **a species becomes locally cohesive when its positive occurrences are sufficiently dense within the spatial strata that it occupies.**

That is a hypothesis generated after the fresh response and must remain labelled exploratory unless validated on another untouched panel.

## 5. Carrier is not a species trait

Fifteen species occurred as eligible species at two or more fresh sites. **Ten of those 15 switched between carrier and non-carrier states among sites.**

Examples:

- **Myodes gapperi** — carrier at STEI, TREE and YELL; non-carrier at WREF.
- **Microtus montanus** — carrier at TEAK; non-carrier at YELL.
- **Perognathus flavus** — non-carrier at SRER; carrier at STER.
- **Zapus hudsonius** — carrier at STEI; non-carrier at TREE and WOOD.
- **Sigmodon hispidus** — non-carrier at TALL; carrier at UKFS.

This prospective fresh panel therefore directly supports a context-dependent interpretation:

> **continuity-carrier status is a local spatial state produced by the species × site occurrence pattern, not a conserved property of the species.**

This is consistent with the earlier 16-site observation that carrier identity turns over strongly among sites.

## 6. Standardized species traits do not explain the residual

After positive-node count was conditioned out, the pre-frozen COMBINE traits showed no consistent positive association with carrier excess.

Median within-site rho:

- adult mass: **+0.100**;
- dispersal distance: **+0.100**;
- habitat breadth: **-0.316**;
- diet breadth: **-0.103**;
- home range: **-0.063**;
- population density: **-0.300**;
- trophic level: **+0.099**.

The earlier carrier-only diagnostic had suggested species-level density as the largest positive candidate (rho about +0.321). It **did not replicate prospectively**: the fresh within-site median was -0.300.

Therefore the current evidence argues against a simple universal carrier syndrome based on body size, dispersal, niche breadth, home range, density or trophic level.

## 7. Integration with trophic and ecosystem roles

The original 32 carriers span granivores, herbivores, omnivores and predators. In 12 of 13 original multi-carrier sites, independent carriers belonged to multiple primary trophic groups; MOAB and OAES contained all four groups.

The fresh mechanism result now changes the interpretation.

The shared property is not a shared ecosystem-effect role. Instead:

1. different trophic roles can reach the same **local spatial-cohesion state**;
2. the same species can leave that state when the local spatial allocation changes;
3. the state is determined predominantly at the between-grid allocation scale under the present metric;
4. within-grid fine arrangement contributes almost nothing detectable to the declared carrier criterion.

This is best described as **effect-role divergence with context-dependent spatial-response convergence**.

## 8. Consequence for Paper A terminology

The current manuscript phrase "span the relevant trap network" is broader than the actual metric and should be removed.

Preferred terminology:

- **local spatial cohesion**;
- **no-isolated-occurrence criterion**;
- **locally cohesive carrier**.

"Spatial continuity" can remain only if it is repeatedly defined as this precise local-neighbour property and explicitly distinguished from whole-landscape connectivity.

The strongest combined ecological statement is:

> Small-mammal species with very different ecological roles can independently attain the same local spatial-cohesion state, but that state is not a stable species attribute: it changes among sites and is determined primarily by grid-scale allocation of occurrences rather than by trophic identity, broad niche breadth, dispersal, or fine within-grid arrangement.

## Claim boundary

The fresh result supports a statement about the declared occurrence geometry. It does not show that:

- grid identity equals habitat;
- habitat filtering is the causal mechanism;
- local cohesion guarantees dispersal connectivity;
- carriers are functionally interchangeable;
- within-grid microhabitat processes are biologically absent.

A direct habitat-mechanism study would require independently measured vegetation, soil, moisture, topography or other environmental covariates at grid/trap scale.
