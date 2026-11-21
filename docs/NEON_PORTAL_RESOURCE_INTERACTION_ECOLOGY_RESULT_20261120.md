# NEON: resources, competitors and learning — new Portal biological result and limitation (20 November 2026)

**Current scientific verdict:** one **exploratory**, pre-effect-fixed 2020–2025 Portal temporal-holdout test supports an unusual **association between plant-abundance volatility and captured rodent community stability whose slope differs by kangaroo-rat access**. The pattern is robust to excluding any single **plot**, BUT a fixed-model leave-one-**year**-out diagnostic reverses both coefficient signs when 2022 is omitted. It is thus **NOT a generally stable multiyear ecological law**, not proof of competitive buffering, resource-based niche memory or learning. One unified NEON ecology paper remains DRAFT/SUBMISSION HOLD; do not merge on an ecological mechanism claim.

## What was actually executed, in chronological order

1. **Source-only precommit**: original `weecology/PortalData` Git commit `afd75933249ae60f3a5e9dab00b354f219e5e045`, all 8 Git blob hashes verified. Source census 2020–2025: 860 standard 48–49-trap QC plot sessions, 453 adjacent-year same-month eligible plot pairs, 203 plot pairs with TWO preceding-90-day original plant field censuses including >=12/16 sampled 0.25m² quadrats. Original 203 source pair treatment: control 113, exclosure 90.
2. **Before plant-count or mammal-composition outcome** the original capture-ID crosswalk returned **69** individual-ID-disjoint eligible *species×plot×adjacent-year* pairs at **17** original physical plots (control 37, exclosure 32), three species and three source start years. This passed all precommitted source GO gates. Verified [GitHub Action #44760271257](https://github.com/zuizui0223/neon/actions/runs/44760271257), artifact 14640627486. This is SOURCE support, not ecology.
3. **Frozen biological endpoint** then used **plot-level relative captured-species composition change** (total-variation distance, [0,1]), with >=5 tagged granivorous rodents in each census and a *different* precommitted 203 plot-pair candidate universe. 89 source pairs lacked >=5 target animals on either side; **114** source pairs remained across **18** physical plots (control 70 pairs, 10 plots; kangaroo-rat exclosure 44 pairs, 8 plots). These 114 are NOT 114 independent geographic sites, nor the previous 69 different-ID species-specific station pairs.
4. **Environment**: per-plot original counted vegetation individuals per censused 0.25m² quadrat, from preceding <=90-day quadrat surveys, not plant biomass, edible seed yield or trap-level food. Predictor was absolute log1p count change between the two preceding surveys. Fixed model was `D_comp ~ plot FE + calendar-month FE + start-year FE + resource_change + resource_change × exclosure`. A time-invariant exclosure main effect is not separately identifiable with plot FE, hence not claimed. Treatment-stratified 2,000 whole-plot bootstrap replicates ALL fit. Verified [GitHub Action #44761367686](https://github.com/zuizui0223/neon/actions/runs/44761367686), artifact 14639934117.

## Fixed full-data results

| Parameter | Point coefficient | Descriptive 95% whole-plot CI | Meaning |
|---|---:|---:|---|
| Plant count change → captured rodent composition distance in controls | **−0.11064** | **[−0.19304,−0.07531]** | Original prediction of positive plant→rodent turnover association failed in controls; observed association reversed |
| Same slope in exclosures | +0.01890 | [−0.04953,+0.09968] | Unresolved, not an absence of resource response |
| Slope difference exclosure − control | **+0.12954** | **[+0.05581,+0.24130]** | Captured community/resource-change relationship differs with original competitor-access treatment, but not proven competition causation |
| Unadjusted plot-equal exclosure − control D_comp | −0.07032 | [−0.15610,+0.00659] | Between-plot descriptive non-support; no causal treatment main effect |

Mean observed captured composition difference D_comp =0.34427; mean absolute change in log1p plot vegetation count=1.2420. Positive interactions are not equivalent to a plant-resource buffering mechanism. The experiment was a historical treatment program, with other treatment/history differences, and the plotted plant abundance proxy does not establish mammal energy resources. All observations are capture-based; detection and true habitat occupancy are unidentified. Prior Portal experiments already documented competitor removal, community compensation/recovery, and habitat patch reorganizations.

## Critical post-result *same model* falsification

[GitHub Action #44762065220](https://github.com/zuizui0223/neon/actions/runs/44762065220) re-downloaded and checksum-verified all 8 original source files and recovered exact original beta control −0.11064, interaction +0.12954. It did NOT change filters, plant measure, model terms, taxon roster or precommitted bootstrap.

| Sensitivity | Control slope | Exclosure−control slope difference |
|---|---:|---:|
| All 114 | −0.11064 | +0.12954 |
| Omit 2021 start-year (93 source pairs) | −0.13258 | +0.13983 |
| **Omit 2022 start-year (49 source pairs)** | **+0.16391** | **−0.66466** |
| Omit 2023 start-year (86 source pairs) | −0.08403 | +0.12299 |

Leave one original plot out: all 18 full-rank models retained a negative control-resource slope (range −0.16055 to −0.10283) and a positive treatment interaction (range +0.10995 to +0.17972). Thus the apparent signal does NOT depend on one plot, but DOES depend on including the 2022 source start-year. The original sample has only **three start years** and 114 plot×month×year records; those records collapse to **46 plot×start-year resource groups**, with 50 repeated uses of the same plot-year vegetation-change value. A whole-*plot* bootstrap does not fully describe shared year-specific environmental pulses across plots; its narrow intervals are not evidence of temporal generality.

The unselected source-only 203 original plant-matched pairs used the same recorded plant survey **season in both years** (132 winter→winter, 71 summer→summer), with mean plant-survey-to-capture lags ~49 and 44 days on first and second year. Thus a winter/summer *label mismatch* does not explain source inclusion, but timing and actual plant phenology can still confound abundance values.

**New ecological question, not a result yet:** whether observed community responses to resource pulses depend on historical competitor context and the state/phase of the rodent assemblage (e.g. transition vs established community). 2022-specific conditions would require independent environmental evidence and prospective predictions; do not mine drought, species, season or plant subgroups from this already-opened small cohort to rescue the coefficient.

## Mechanism ranking is NOT possible

- **Resources:** measured change in count of all recorded plants, not true seed food or biomass. Association has an unexpected negative direction in original controls but fails a strong temporal sensitivity criterion.
- **Biotic interactions:** original exclusion vs control provides a possible manipulated context; the noncausal resource×treatment interaction is model-sensitive to time. It does not establish competition, buffering or a cause.
- **Learning:** tags capture encounter *experience* but no randomized reward/cue relocation, task response or independent movement/detection record. It was deliberately **not fitted**. Calling a model of recapture an inference about animal learning would be incorrect.

**No stable cross-system ecological principle has yet been demonstrated.** The defensible programmatic conjecture is that individual-, resource-, and interaction-driven spatial structure can be decoupled, but its mechanistic conditions require verified independent field behavior, local resource and detector data beyond this single landscape.

## Reproducibility and decisions

- Pre-effect resource+competitor+experience measurement boundaries: `docs/NEON_RESOURCE_COMPETITION_LEARNING_DISCRIMINATION_20261120.md`.
- Pre-effect final plot-composition analysis: `docs/NEON_PORTAL_RESOURCE_COMPETITOR_OUTCOME_FROZEN_20261120.md`.
- Source code/receipts: `analysis/audit_portal_resources_competition_learning_source_v1.py`, `results/neon_portal_plant_change_competitor_ecology_20261120.json`.
- Post-result diagnostic: `analysis/diagnose_portal_resource_competitor_stability_v1.py`, `results/neon_portal_resource_competitor_year_stability_20261120.json`.
- Immutable original prior evidence: NEON 14 physical sites conditional genus×trap Z+0.795; exploratory two-genus 30-site Z+0.615; Portal 1996–2019 436 pair station source-conditioned near-zero excess; Finland 10-site own-location-stationarity rho residual −0.243; original NEON density 5/8 genera generality FAIL. None has been changed.

**Editorial state:** continue one NEON ecological manuscript only. Place the Portal resource result in an explicit exploratory/negative temporal-generality appendix or development note; **do not add a new causal mechanism claim to the abstract or mark the draft ready for submission.** No second A/B or method paper created.
