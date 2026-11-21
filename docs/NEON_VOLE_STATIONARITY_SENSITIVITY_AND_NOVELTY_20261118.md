# NEON unified mammal ecology: Finland vole stationarity sensitivity and biological novelty boundary (18 November 2026)

**State:** Existing draft PR #23, one unified ecological paper, **SUBMISSION HOLD**. This is *retrospective sensitivity on already inspected 2021 Finnish vole captures*, NOT a newly preregistered test, independently sampled ecology, or a mammal generality confirmation. Original results are unchanged.

## What was verified and added

The GitHub original biological source remains pinned to `jmistrick/vole-spatial-manuscript` commit `47dc1e9b1f83ec2faaf7ba232e02e00f9e4cffb4` and Git blob `343de8c3846eea21d3f0648358e159bd61bb87a2`. Exactly 2,012 capture rows and 742 source site-tag keys reproduced. The old original repeated-capture source set has 51 qualifying animals at 12 sites; only the original frozen dyad endpoint's 47 animals/10 sites/102 within-site pairs were analyzed. **Sites (n=10), not dyads (n=102), are the independent approximate uncertainty units.**

The previous outcome: site-equal same-tag summer-to-autumn individual-pair distance rank correlation `rho_observed=+0.469986845`. An autumn identity-label permutation yielded near-zero expected rank correlation, but conflated own-site preference and any pair-specific persistence.

Stricter *individual-stationarity* counterfactual: each individual preserves her/his own original pooled capture-site frequency and observed summer/fall capture counts. Draw summer/fall capture positions by independently reallocating that individual's pooled positions; calculate site-level same-pair distance rank rho. Five fresh source-reverified independent pseudorandom streams (2,000 simulations/site/seed, each with 5,000 food×deworm-stratified whole-site bootstrap draws) gave:

| RNG seed | Expected rho under fixed individual capture-location distribution | Observed minus expected rho | Descriptive bootstrap 95% |
|---|---:|---:|---:|
| 2026111567 | +0.71372 | −0.24373 | [−0.49905, −0.00946] |
| 2026111568 | +0.71097 | −0.24098 | [−0.49404, −0.00986] |
| 2026111569 | +0.71212 | −0.24213 | [−0.49435, −0.01074] |
| 2026111570 | +0.71328 | −0.24330 | [−0.50724, −0.00796] |
| 991 | +0.71513 | −0.24514 | [−0.50450, −0.00144] |

All five had negative site-equal residual, 7/10 residual sites negative, no degenerate Monte Carlo replicas, and negative mean residual under every leave-one-original-physical-site-out deletion (across seeds, LOO means ranged from −0.3052 to −0.1303). This demonstrates **computational sensitivity to RNG is small**, but five streams are NOT five biological studies or independent biological confirmations. Bootstrap upper bounds are close to zero, based on only ten selected source sites and a potentially unrealistic stationarity null. Do NOT claim strong population-level inferential certainty.

## Observation-process source check

For the same **10 original physical sites**, without selecting by any effect, compare sets of ORIGINAL site-specific trap station names with *at least one recorded bank-vole capture* in summer vs autumn. Site-equal summer/fall positive-capture-station Jaccard **0.467786** (range **0.2222–0.6226**, median **0.50036**). The within-repeated-individual source-station intersection/union Jaccard averaged **0.192319** at the site level. Across these sites 811 records are summer, 975 fall.

**These are capture-positive station sets, NOT operative-station histories or camera-verified availability.** Original Mistrick et al. field design used the same regular 61-trap 1-ha layout repeatedly; observed captured-station turnover cannot be described as traps becoming unavailable. The fixed individual pooling reference conditions on recorded positions only; it does not preserve month-specific habitat, trap status, animal availability, live-trap attraction or capture detection. Jaccard by itself therefore cannot resolve whether the lower observed rank continuity reflects animal movement or season-specific capture sampling.

## Biological interpretation after strict audit

The initially positive partner-rank correlation has been explained **as a contrast to randomly reassigned animal identities**. It does *not* identify partner-specific geometry beyond stationary individual spatial preferences. Under that stronger null, capture-centroid pair ranks reorganize *more* than the null expects. Distinct negative residuals and individual seasonal capture-centroid shifts are consistent with changing recorded spatial arrangement, not a direct measurement of true motion, dyadic interaction, disease contact or social network rewiring.

**Important PRIOR ART:** The authors of the original field paper already experimentally studied season, density, food supplementation, helminth removal, sex/reproductive status, space use and overlapping individual locations (Mistrick et al. 2024, DOI 10.1111/1365-2656.14067). We cannot claim that rodents change seasonal location, resource-related home range size or mean overlap as a novel discovery. The null-model logic is also established (Farine 2017, DOI 10.1111/2041-210X.12772; Farine & Carter 2022, DOI 10.1111/2041-210X.13741). Earlier reference Fisher et al. (2017), DOI 10.1111/1365-2656.12630, is about stochastic actor-oriented social network dynamics, not the most directly relevant source-conditioned randomization guide.

A limited *new descriptive contrast* is that the original vole capture-derived **identity-pair geometry is LESS persistent than an own-capture-location stationary counterfactual**, notwithstanding positive similarity under cross-individual identity permutation. This result is exploratory, mechanistically unidentified and not a transferable mammal law.

## Consequences for the one manuscript

- Preserve original positive NEON 14-site genus-by-station Z=+0.795 strictly as conditional capture-station recurrence, not confirmed true niche retention; retain the operative-trap source gate failure.
- Preserve original Portal 436 species×plot pair reference-conditioned exact-station non-support; do not pool Portal's collision probability with Finnish rank rho or NEON rank Z.
- Retain both 2021 Finland published prior ecological effects and our exploratory negative stationarity-rank residual; these answers test **different estimands**, not contradictory movement results.
- Preserve original NEON density-space 6/8 genus generality FAIL, prospective direction nonreplication and missing direct-contact denominator.
- **Do not merge for submission or upgrade to general niche mechanism.** The next biological test requires matched, independently observed actual individual space use and capture effort across time, preferably new cross-season data with telemetry/camera observations and habitat resources.

Machine-verifiable aggregate sensitivity: `results/neon_vole_stationarity_multiseed_and_station_source_20261118.json`. First single-seed crosscheck: `results/neon_bank_vole_stationarity_js_crosscheck_20261115.json`. GitHub Python runner and workflow exist on this branch; its new exact source run/artifact is NOT yet independently checked. JS source retrieval verified immutable Git blob SHA, so the aggregate JS Monte Carlo results are source-backed but no Python-vs-JS exact numerical agreement is claimed.

All source identifiers and individual capture coordinates remain in original source only, not in this added aggregate receipt.
