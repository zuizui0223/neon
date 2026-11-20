# Resource × competitor context × capture experience: a disjoint measurement plan for NEON and Portal
Date: 2026-11-20; **ONE existing mammal ecology Draft PR #23; SUBMISSION HOLD**.

## Scientific decision

Do not rank three processes as if all were measured in the same way.

- **Resources:** independent Portal plant quadrats measure *plant abundance/counts* (0.25 m² in up to 16 quadrats per plot; visual cover only from 2015), NOT seed production, diet, edible biomass or per-trap food quantity. Use plant abundance as a *plot-level vegetation/possible-resource proxy*, not a validated food-energy measure. No direct quantitative food-biomass estimand is available.
- **Biotic interactions:** the original fixed Portal plot treatment `control` vs `exclosure` experimentally restricts kangaroo-rat access. This is a *competitor access manipulation* but original long-term treatment histories, ant treatment and period/plot identity can confound a simple between-plot contrast. Prior competitor effects, delayed recovery and microhabitat patches were published (e.g. 2019 Portal recovery; 2022 resource partition and community compensation). Do not claim ordinary competition effects as novel.
- **Learning:** individual rodent ID histories allow *prior recorded capture*, not learning or spatial memory: animals of differing age, home range, survival, individual catchability and handling state are unbalanced. Without a randomized novel reward/maze/cue reversal or independent localization, past-recorded-capture is an *observation-history covariate* only. Do NOT model it as evidence for cognitive learning or fit a favorable memory coefficient.

The biological question is whether **resource abundance change and competitor access predict changes in observed rodent community composition in a later time period** when the original historical NEON/Portal capture-space results are frozen. This is plot-scale community organization, not 49-station within-plot microhabitat selection.

## Temporal holdout cohort locked BEFORE 2020+ animal spatial/composition responses

Source: `weecology/PortalData` immutable Git commit `afd75933249ae60f3a5e9dab00b354f219e5e045`. Keep original six files and Git SHA validation from `analysis/portal_external_id_niche_source_v1.py` unchanged, and ADD only:

- `Plants/Portal_plant_quadrats.csv`: Git blob SHA `82b296aceb964f64864e979a34a0c7bc455a87f8`, original columns `year,season,plot,quadrat,species,abundance,cover,cf,notes`; cap source bytes 100,000,000.
- `Plants/Portal_plant_census_dates.csv`: Git blob SHA `2ab18f4f9e603da3e8c0b472d24c8a4d5caa8ef8`; original columns `year,season,censusdone,start_month,start_day,end_month,end_day`; cap 30,000 bytes.

**Current host independently checked SOURCE-ONLY:** 2020–2025 had 860 QC 48–49 effort plot sessions in control/exclosure, 453 unique plot×same-month adjacent-year session pairs whose two original plot treatment labels agree. Requiring on BOTH sides at least 12 of the 16 originally censused 0.25 m² plant quadrats and a completed original plant census ending BEFORE the capture day and within 90 days yielded 203 plot-time pairs / 18 plots (113 control, 90 exclosure). These values do not include animal identity, species abundance, plant abundance, seed mass, plot-varying effects, or any outcome.

Time-heldout period is **2020–2025**, disjoint from the previously evaluated Portal 1996–2019 rodent source study. Source cutoff at fixed Git commit, not living main. Keep ALL eligible years and both plant seasons, no post-result month/site/species rescue.

Capture gate: original standardized positive period, one 48–49 trap QC survey per original plot×month×year; exact unaltered rodent treatment between paired years; only authoritative identified target granivorous rodents (frozen species codebook); distinct valid ID and canonical 7x7 stake; remove same-event IDs with conflicting stake, across-species code or invalid tag, and shared between-year IDs within each species before *individual-disjoint station-persistence* eligibility. Require >=5 nonshared tags and >=3 distinct original stakes per species in EACH year. This matches old structural eligibility without reopening old effects.

Plant gate: original `Portal_plant_censuses.csv` must identify >=12 actually surveyed quadrats/plot×season with area exactly 0.25 m²; census-date end month/day must parse with no time imputation, end date <= capture date and within 90 days, both years must use distinct source surveys; `Portal_plant_quadrats.csv` has a known numeric abundance field for at least one species observation in each selected plot×season (zero plants at a censused quadrat can be an actual zero, not a missing value). No summing actual plant abundances in the source gate.

**PRE-OUTCOME SOURCE GO** only if >=30 eligible 2020–2025 different-ID species×plot×adjacent-year pairs, >=8 distinct plot clusters and >=4 original plots per `control/exclosure`, at least 3 source start years, >=2 species codes, and >=90% of the 203 (or reproducibly recalculated) plot-month pairing source records readable as original CSV without ambiguity. These source rules are frozen *before* opening new species/plant abundance or species station overlap values. If STOP: record exact failed support, do not lower thresholds.

## Fixed ecological outcome IF original source gate GO (no results yet)

Use independent plot-level relative capture composition for each of two adjacent-year same-month QC censuses (all identified target granivorous rodents with valid original tags, one captured individual per genus/species in each census; no after-the-fact target species group selection). Primary fixed ecological response is **total-variation distance** between all target-species capture-composition proportions:

`D_comp = 1/2 × Σ_taxon |p_A_taxon − p_B_taxon|`.

This is **observed capture-composition change**, not latent community occupancy, biomass or true survival; tag exclusion is for separate identity-disjoint station-support audit, not a requirement that all animals die or immigrate.

At plot×year plant surveys compute **plot mean counted individuals per censused 0.25 m² quadrat** across all surveyed quadrats (zero at surveyed quadrat with no plant rows; missing never coded zero). This is a proxy for plant abundance, not seed/edible biomass; `resource_change = | log1p(plant_count_B_per_quadrat) − log1p(plant_count_A_per_quadrat) |`, exact source survey before each trapping date, within 90 days.

Two fixed biological predictions tested as an explicitly exploratory held-out-time *within-one-landscape* model:
1. **Resource change:** higher `resource_change` predicts larger capture-composition turnover (`D_comp` coefficient positive), evaluated holding plot and calendar-month context fixed where estimable.
2. **Competitor access:** fixed `exclosure` versus `control` difference and a `resource_change × treatment` interaction test whether resource-response differs with kangaroo-rat access. The INTERACTION direction is *not* preselected because there is no validated mechanism assigning it a sign; report full uncertainty in both directions, not an after-the-fact positive subgroup.

Use original plot as cluster and original year as a temporal unit; treatments are not independently randomized every year. Do not treat the 203 source pairs, plants within 16 quadrats, animal tags or observed traps as geographically independent. A transparent leakage-free plot-disjoint split is necessary for out-of-plot predictive performance; single-landscape generality is **never** proven by temporal holdout alone. Plant abundance itself is an environmental covariate not a manipulation. Separate detection/behavioral observations still required to call the contrast a mechanistic explanation.

**No learning effect coefficient.** Prior-capture count is allowable only as an observation-process descriptive boundary if a distinct later protocol is frozen; do not add it now to explain results. No post-hoc replacing `D_comp` with station exact-overlap, no seed/plant cover alternative search, no treatment/site subgroup rescue, no re-opening historical 14-site NEON Z or Portal 436-pair R1.

## Record-keeping

New `analysis/audit_portal_resources_competition_learning_source_v1.py` checks the new-source temporal and ID support **without computing abundance totals, composition turnover, station persistence or treatment effects**. New source-only CI and unit tests must pass before any novel outcome is unsealed. Original past results and failure gates unchanged. Manuscript remains DRAFT / SUBMISSION HOLD regardless of source GO.

Bibliographic boundary: Ernest et al. Portal living study and 2019/2022 published ecological comparisons; original coordinates show permanent quadrats interlaced among 49 rodent stakes and one known duplicated source-stake ID in plot 1 (never silently repair geometries or claim all 49 precise station coordinates validated). Source support does not imply plant quadrat exact-trap food accessibility.
