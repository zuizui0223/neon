# Portal: test individual-turnover and species-specific station use, not generic niche separation

15 November 2026. ONE NEON ecological macroecology manuscript PR #23. Separate Portal field observations are a retrospective independent ecological system; the 2019 niche and 2022 microhabitat publications are PRIOR ART, not novel results.

## Biological question and prior art
Portal has previously documented species spatial niche segregation, resource selection, competitive release and species-composition-driven habitat patch shifts, including a 22-year Chaetodipus penicillatus patch study: https://pmc.ncbi.nlm.nih.gov/articles/PMC6899716/ and a six-species spatial segregation study https://doi.org/10.1007/s00442-021-05104-5. Testing "competition affects realized niche" is not novel.

The useful NEW observable comparison is whether species-associated capture-station use recurs across one year after the observed individual IDs in the two censuses are made completely disjoint. Does species-level station capture-space organization remain stable conditional on species abundance, experimental kangaroo-rat competitor exclusion, and fine-scale plants? Is the old NEON signal more likely a persistent station/habitat opportunity or a repeated trap-observation process? These remain questions, NOT known favorable biological results.

## Frozen original source and eligibility (BEFORE any station-repeat ecological outcome)
Public PortalData repo at immutable commit afd75933249ae60f3a5e9dab00b354f219e5e045. Six exact original Git blob SHAs pinned in analysis/portal_external_id_niche_source_v1.py:
Rodent captures; effort/trap quality; species codebook; plot/year treatment; plant 16-quadrat sampling census; surveyed site UTM rodent-station geometry.

Years fixed 1996–2019, same plot and same calendar month exactly one year apart. Require one original sampled positive-period qcflag=1 census with effort 48–49 traps each year, unchanged original control or Dipodomys-exclosure treatment, and original identified target granivorous rodent species. Exclude negative/out-of-protocol periods and missing/suspect 7x7 station values.

After removing ALL individual IDs observed in both compared years, require at least five unique remaining recorded individual IDs and three distinct valid original stakes per species in each year. IDs denote recorded animals, not all living animals or demographic replacement; imperfect capture still matters. Do not select a taxon by observed stationary recurrence.

SOURCE only GO: >=30 valid plot×species×adjacent-year pairs and >=4 distinct plots per treatment. One Portal field landscape, not 24 independent geographic ecosystems. Do NOT revise the thresholds after looking at response. Source output contains anonymous aggregate eligibility, rodent capture headers, PIT source flag distributions, plant census support and control/exclosure plot counts only; no station Z, p value, niche breadth, original individual identity, coordinates or known ecological direction.

If GO: freeze an actual original null comparison BEFORE opening spatial recurrence: individual-ID-disjoint species×stake recurrence across annual same-month pairs, while conditioning counts, source effort, shared trap opportunity and stable species-blind location preferences. Compare experimental control and exclosure as a test of context dependence; they are not randomized anew every year and treatment differences may be confounded with historical conditions. Validate added spatial predictive information in source-heldout plot-year blocks. Fine-scale quadrat vegetation permits an additional habitat context layer but is not exact 49-stake vegetation for every census.

NEON's historical original Z=+0.795 is a separate observation; Structural global mammal 529-species map-derived result is a different label and graph, not observed movement. They must never be pooled with Portal's spatial-response values. Do not reopen old NEON or Structural outcomes or adjust historical failed gates.

Public original data: https://github.com/weecology/PortalData/tree/main/Rodents
Methods: https://github.com/weecology/PortalData/blob/main/SiteandMethods/Methods.md
