# Species-specific versus congeneric crowding: next-generation ecological test

**Defined:** 2026-10-18. **Scientific category:** hypothesis and effect-blind predictor-feasibility audit generated AFTER examining NEON RELEASE-2026 W/B effects and the 2025–2026 provisional held-out outcomes. NOT a prospective validation of the original eight-genus result. Those results remain fixed as documented; do not re-label the positive or negative historical effects confirmatory.

## One ecological question

**When more individuals of a small-mammal *species* are present, does their short-term within-individual trap-coordinate variance change differently from the dispersion of observed animal centres, and are those associations distinguishable from changes in abundance of *other species in the same genus*?**

The original study modeled W, debiased B and Δ=B−W against **genus-level** minimum number known alive (MNKA). A focal *Peromyscus* species's genus MNKA may include individuals of another species. The original coefficient therefore cannot isolate effects of conspecific crowding, or establish ecological causation. Moving to species-resolved predictors would address a genuine biological distinction, **not rescue** the prior failed 5/8 versus 6/8 generality rule.

## Fix the taxonomic interpretation before seeing new effects

The existing RELEASE-2026 target list contains 31 target species concepts and four species-group concepts (e.g., PEMA/PELE group). Each historical marked animal has a site × plot × tag identity and a set of target taxon IDs across captured events. For predictor-only feasibility use:

- **Resolved-species animal:** history assigned to exactly *one* target species taxon ID (taxon rank species, not a species-group label) across all eligible captures.
- **Unresolved genus animal:** history containing a species-group assignment OR multiple taxon labels *within* a genus; do not count it as a resolved animal of any species.
- **Cross-genus taxonomic conflict:** exclude from the genus MNKA predictor, exactly as the original frozen index did; report its count.
- **Known alive:** within the same exact-three-night standard site × plot event sequence, an animal is counted at every event from its first to last target capture, following the original genus-MNKA rule. Do not insert an animal outside this interval.

For focal resolved species s within genus g, at event e:
  * F(s,e) = MNKA of histories unambiguously assigned to s
  * C(s,e) = MNKA of histories unambiguously assigned to other species in g
  * U(g,e) = MNKA of unresolved, same-genus histories
  * N(g,e) = F(s,e) + C(s,e) + U(g,e), **exact identity** on the frozen event universe.

**F, C and U are availability/known-alive indices, not densities**, and even clearly labelled individuals can have detection error. Focal species-group response rows are not candidates for the species-specific primary inference; they remain in the historical original cohort.

## Outcome-blind RELEASE-2026 feasibility audit

Before touching any new W/B outcome:
- Reconstruct original checksum/version-tied complete three-night NEON events, 1536 target response sessions, 47360 target marked histories, 103 cross-genus excluded histories and 176 genus-MNKA varying series as invariant checks. **Never modify** the original W/B or fixed model scripts.
- For each *resolved focal species* × plot × event, calculate only N, F, C, U and reported identity counts; **do not compute spatial distances, W, B, Δ or test correlations with them**.
- Report by genus (and at sufficiently aggregated scale) series with >=3 events, >1 distinct focal F and other-congener C values, number of sites and predictor-only co-occurrence.
- Critically, diagnose residual predictor variation **after the unchanged series, site × calendar month, and year fixed effects**. A two-predictor design must have full rank; testing species-specific versus congeneric slopes when predictor variation is absorbed by the nuisance effects is prohibited.
- Do not choose a favorable genus from already-known W/B signs. *Peromyscus* is the predeclared feasibility priority **because its taxonomy explicitly includes multiple target species and cryptic pairs**; the other genera are fully reported as structural context. A "GO" only means **potential identifiability**, not that future data have enough statistical power or correct biological identities.
- **Pre-exposure predictor-only feasibility descriptor** (not a scientific success test): a genus can be called *candidate structurally identifiable* only with >=60 sessions for strictly resolved focal species, >=6 NEON sites, >=8 distinct focal taxon × site × plot series with at least three sessions, >=5 series showing both focal F and congener C variation, full conditional rank two after frozen fixed effects, and condition number <=30 for the two residualized predictors (no further threshold tuning after this audit). All these are **sample/predictor-only** gates: even a pass does not permit a W/B fit, prove power, or retrospectively choose a positive genus. Record both pass and fail for every genus, with *Peromyscus* discussed first regardless of outcome.
- Do not make the observed abundance range, site count or regression coefficient from RELEASE-2026 an independent confirmation. Historical data are already response-consumed.

## Prospective future-study hypotheses (only new, unconsumed trapping events)

Primary ecological estimand: within-species slope contrast for *true resolved-species* abundance F when allowing a separate congeneric abundance index C in the same model, using comparable-season repeat observations of the same species × site × plot.

Competing predictions, to be tested on **new events not contained in either RELEASE-2026 or any previously opened 2025–2026 provisional stream**:

1. **Conspecific competition/individual compression:** higher F is associated with W decreasing, potentially with B maintaining or increasing. A positive Δ_F alone is not proof of competition or territorial exclusion.
2. **Congeneric interaction/redistribution:** the relationship between C and W/B differs from the one for F (two-sided contrast Δ_C − Δ_F), if both index series have independent within-population adjusted variation. Differences may arise from ecological sorting or species turnover, not necessarily direct interference.
3. **No identifiable or no ecological association:** capture selection, habitat/seasonal composition or weak within-population variation accounts for the observed covariance. This must be treated as a substantive possible outcome, not rescued with an ad hoc threshold or genus subset.

Future release primary screening is based on *effect-blind predictor-support* criteria (full rank, fixed taxonomy rule, enough distinct site-level seasonal repeats, and trap completeness). Any formal minimum site/series number and expected detectable effect must be separately locked before opening future W/B outcomes. Use year- and site-cluster uncertainty, explicit detection sensitivity, and report W and B component slopes in addition to Δ. Distinguish observed trap coordinate variance from true home ranges.

## Rationale and availability

NEON's publicly documented protocol uses **100 traps spaced 10 m** on standard 10 × 10 grids; complete three-night pathogen-grid bouts are scheduled multiple times per year with seasonality and lunar timing. Researchers identify species, sex, age and reproductive condition, and taxonomic identification history is tracked. Sampling and identification uncertainty must be confronted, not ignored. See:
- https://www.neonscience.org/data-collection/small-mammals
- https://www.neonscience.org/resources/learning-hub/tutorials/mammal-data-intro
- https://data.neonscience.org/data-api/endpoints/releases/
- https://www.neonscience.org/data-samples/data-notifications

A static data release is citable and versioned; since 2026-06-30 NEON downloads require a user login/API token. No exact next release date or future sample size is promised. New releases may correct 18 affected *geoNEON* trap-point coordinate maps: this does **not** alter nominal `trapCoordinate` labels or the existing purely nominal W/B lattice and should not be misrepresented as correcting those original W/B coefficients. It matters if later adding map-derived habitat/topography covariates.

## Explicit boundaries

- No changes to the original 8-genera denominator or already-opened results.
- No post-hoc new species or sex/habitat moderator model fitted on historical W/B in this audit.
- No inference that a difference in W/B indicates territoriality, individual avoidance, resource competition, predation or disease transmission.
- Do not claim independent future validation if observations or tagged histories are reused across releases.
- MOSA's 153-month predictor-only support does not solve biological identity issues or permit opening its sealed W/B effects.
- The ecological manuscript `manuscript/NEON_MAMMAL_DENSITY_SPACE_ECOLOGY_V0_2.md` remains Draft/HOLD.
