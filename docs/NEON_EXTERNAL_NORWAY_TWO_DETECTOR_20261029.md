# External two-detector longitudinal small-mammal presence — locked exploratory validation

29 Oct 2026. ONE integrated NEON ecological macro programme PR #23. No new A/B or standalone methods paper and no change to original NEON 14-site Z.

## Empirical external design

A published 2025 Norway study (Lindsø et al., Ecology and Evolution, DOI 10.1002/ece3.71590) deployed tunnel cameras year-round at 12 independent forest sites in 2018–2020 and sampled four ordinary capture-trap stations within 20 m during spring/fall (different gear at sites: snap and cage). All published source metadata is external to original NEON RELEASE-2026 and its source failure to find simultaneous cameras at the 58 source sites. Data were already analyzed for diel niche and camera/trap count correlations by the original authors; our descriptive two-method presence and apparent temporal persistence audit is retrospective/exploratory and should not be presented as a new confirmatory experimental result.

Source pinned in advance: latest original 2025 Zenodo v5 DOI 10.5281/zenodo.15312178, file count_cam_vs_trap_traptype.csv, MD5 56f71c980503a4e6043b4d3d424fd53c (English species labels).

## Fixed validation and analysis choices

1. Require original published source MD5, complete seven named fields, exactly 12 sites x five campaigns x four named taxa = 240 original cells. Campaigns: fall 2018, fall/spring 2019, fall/spring 2020. Four species bank vole (Myodes), wood mouse (Apodemus), common shrew and pygmy shrew (Sorex). Each site×campaign must have one true source count for all four species; do not replace absent sampling with zero.
2. For each site×campaign×species, compare the CAMERA INDEX computed from the **30 days PRIOR to onset of ordinary trapping** with capture records from the subsequent **three consecutive trapping days**. These are not simultaneous measurements. Reduce each separately to recorded >0/0 indicators. Report paired both-positive, camera-only, capture-only, both-zero cells. Report by taxon; original raw event count cannot be compared as a rate because continuous cameras and 3-night ordinary trapping have different exposures.
3. Define the only three transitions before calculating outcomes: 2018 fall→2019 fall, 2019 fall→2020 fall, 2019 spring→2020 spring. At identical site/species, compute camera and capture positive in BOTH campaigns as *detection-history continuity*, not confirmed individual or community persistence. Include symmetric cases camera-repeat/capture-not and capture-repeat/camera-not.
4. A particularly interpretable observational discrepancy is capture-positive in the earlier year and zero in the next, with camera-positive in BOTH years. This is a discordance between NONCOINCIDENT observation windows. It shows that zero captures do not establish the taxon's absence in the preceding 30-day camera period. It cannot disprove true biological loss during the intervening weeks or demonstrate a difference caused by detector hardware alone. Also report converse apparent camera loss with capture-positive both years. It does not prove that capture probability is smaller or that two instruments have independent errors.
5. Stratify by sites whose ordinary trap type is unchanged versus switched (cage/snap). Do not call the captive count a non-lethal live trap when snap traps were used. Report site-equal effect of difference in both-year-positive fractions over 12 independent sites with a fixed 10,000-resample site-cluster bootstrap, descriptive only without a confirmatory P. Site-campaign richness difference is detection richness, not true assemblage richness.
6. This is a different geography, different site/station layout, and only four species; no extrapolation to NEON original exact trap Z or stable habitat niches. Original source 14-site and 30-site capture-space recurrence, failed 10m patch, density, tower, operability, release and joint W/B controls remain unchanged. A genuinely prospective genus-by-trap spatial use/detection study is still needed for causal inference.

### Reproducibility
- analysis/neon_external_norway_two_detector_v1.py
- tests/test_neon_external_norway_two_detector_v1.py
- .github/workflows/neon-external-norway-two-detector.yml
- build/neon_norway_external_two_detector_20261029.json as aggregate-only Action artifact

Sources: https://zenodo.org/records/15312178
https://pmc.ncbi.nlm.nih.gov/articles/PMC12162949/
