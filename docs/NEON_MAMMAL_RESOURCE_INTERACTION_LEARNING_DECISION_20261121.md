# NEON mammal ecology: mechanism admission decision (21 November 2026)

**One main goal:** Identify the ecological conditions for recurrence of *true* mammal spatial use across changing individuals or population contexts. Do **NOT** replace this with a stream of post-result weather coefficients or a separate method-only paper. Existing integrated NEON PR #23 remains Draft, main unmerged, **SUBMISSION HOLD**.

## Mechanism verdict from actual evidence, not preferences

| Candidate | Actual measurement and positive/negative evidence | Identification decision |
|---|---|---|
| **Resource quantity / plant biomass** | Source-matched Portal 2020–25 plot-level *plant individuals per surveyed 0.25m² quadrat* (NOT seeds or edible biomass) and captured-rodent community composition: full frozen control slope −0.11064, exclosure×resource slope +0.12954; **both signs reverse after dropping 2022**. Verified 2022→23 later **July–September NDVI fell −0.10156**, but **43/65** follow-up rodent captures occurred earlier in **April–June**. The independently sourced original **February–March leading NDVI slightly rose +0.002967**, not a preceding same-season greenness crash. | **No transferable resource or biomass mechanism demonstrated.** A simple pre-spring site-greenness decline is not supported by this index. True seed supply, biomass/quality, patch accessibility and plot-specific resources remain unmeasured. |
| **Competition / biotic interaction** | Portal's historical kangaroo-rat exclosure is a meaningful experimental context, but its captured-community difference is a *slope association* in a site-confounded historical plot design. It is not time-robust (2022 removal sign reversal), and Portal's original 1996–2019 species-stake reference-conditioned experiment gave near-zero R1 recurrence excess with nonresolved exclusion contrast. | **No causal competition/competitive buffering generality.** Competition may operate but it is not uniquely identified by these observational endpoints. |
| **Individual learning / site memory** | NEON's recorded recapture history, Finland same-animal captured-centroid displacement and positive dyad continuity vs whole-ID shuffle. The stricter own-location stationarity null gave rho observed-minus-expected **−0.2426** in Python, confirming the prior positive dyad contrast was not dyadic persistence over individual site preferences. A trap reencounter is not a rewarded navigation or learning task. | **Unmeasured.** No direct learning/experience-mediated habitat relocation, path tracking or randomized cue reversal; do not infer cognition or social bonds. |
| **Alternative observation process** | NEON 14 physical sites positive genus×exact-trap conditional Z+0.795; separate 30-site exploratory exactly-two Z+0.615. Independent Portal 436 individual-ID-disjoint same-stake comparisons lack a reference-conditioned species-specific excess. Cameras/contact data lack exact matching detector opportunity. | **Still open**: repeated trap geometry/capture propensities are not independently separated from real mammal space use or resource-habitat niches. |

## Ecological principle remains a prediction, NOT a result

**Conditional spatial organization hypothesis:** repeated use of species- or genus-associated resource patches despite changing observed tagged animals is more likely where resource/habitat configurations remain stable; altered competitive access or learned experience may shift the realized use of those patches. It is falsified by no predictive capture-independent habitat association after controlling effort/detectability or by lack of consistency across genuinely independent sites and periods.

This is distinct from declaring "mammals maintain a spatial niche" from a fixed-margin live-trap permutation. Existing results cannot rank the three biological causes.

## Strict stop/advance gate

**STOP this Portal 2020–25 source for post-result mechanism fishing.** Do not open more NDVI month windows, alternative cloud filters/sensors, subsets of rodent taxa, plant functional groups, or weather-based refits to recover a positive slope after the year-omission failure. Original Portal 114-pair model, 69 source-only disjoint pairs, NDVI findings and chronology are frozen with all signed estimates.

**ADVANCE only when independently measured new source provides all of:**

1. **At same spatial grain**: per plot/trap or unbiased resource-patch measurements of **rodent-consumable seed or plant-food energy/biomass** at times preceding mammal observations (not 1km NDVI or off-grid plant totals alone).
2. **Independent observation of animal use**: original activity camera/PIT/RFID/telemetry *and its measurement effort* at the matching station/time; separate actual-use counts from capture probabilities, trap-state, animal availability and individual capture history.
3. **Explicit biotic interaction and time support**: original competitor access/abundance (prefer manipulations or pre-specified natural contrasts), repeated before/after resource changes, enough independent sites and temporal transitions to test held-out year/area prediction.
4. **Cognitive tests separate from spatial structure**: only add learning if a tracked individual experiences a documented changed reward/cue/route and its subsequent choice is measured independently of capture, ideally by counterbalanced interventions.

Then lock one effect *before opening* the new mammal response: out-of-site temporal predictive gain in capture-independent species/individual resource-patch use when adding resources, then competitor term, then learned-history term only if measured. A positive predictive improvement under effort-controlled independent observation could support the conditional ecological mechanism; no gain means non-support. Never pool incomparable raw NEON Z, Portal collision probability, Finland dyad rho or Structural IUCN island-map log loss as one meta-effect.

**Submission decision:** Preserve conditional positive NEON capture-station result, observational negatives and year-fragile Portal result in the one manuscript; abstract/main conclusion cannot assert resources, biomass, competition or learning as established drivers. Keep **SUBMISSION HOLD**.

## Evidence source

- `docs/NEON_PORTAL_RESOURCE_INTERACTION_ECOLOGY_RESULT_20261120.md`
- `results/neon_portal_resource_competitor_year_stability_20261120.json`
- `results/neon_portal_ndvi_capture_chronology_20261121.json`
- `results/neon_portal_2022_independent_monsoon_NDVI_and_rain_QC_20261121.json`
- `docs/NEON_PORTAL_PRECAPTURE_FEBMAR_NDVI_RESULT_20261121.md`
- `results/neon_portal_precapture_febmar_ndvi_context_20261121.json`
- `results/neon_vole_stationarity_python_action_verified_20261119.json`
- Exact-source original [Feb–Mar NDVI workflow 44853409600](https://github.com/zuizui0223/neon/actions/runs/44853409600).
