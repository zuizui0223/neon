# Seasonal seed–rodent functional roles: staged seed fate and spatial continuity

24 November 2026 — hypothesis/design, not a new ecological result. Existing NEON same-station genus recurrence is a conditional capture-space pattern; corrected nonidentical-station canopy affinity is unsupported. One paper DRAFT / SUBMISSION HOLD.

## Source inventory completed

Both originally selected Figshare v1 ZIPs passed complete provider MD5/size checks: Dri 15029247 (file 36110309, 2,277,102 bytes) and Brehm & Mortelliti 14488626 (file 27847659, 692,526 bytes). Original run 45312323517, archived stdout receipt [inventory](../results/neon_direct_resource_groundcover_source_inventory_20261124.json). Dri archive includes seed-trap measurements and coordinates, capture-history, use/availability and home-range inputs, author kriging and survival/selection code. Brehm archive includes microhabitat, trap distances, occupation and personality records. Member names do not establish valid patch-level chronological joins.

## Main ecological direction

Role persistence need not equal location persistence. A mammal taxon occupying a recurring patch may contribute differently to plant recruitment over the seed cohort's lifetime: encounter/removal, primary caching, subsequent retrieval/pilferage/recaching, survival to germination. Test whether the taxon ranking of contributions changes between these stages and whether cohort survival depends on the temporal overlap of seed availability and animal activity, beyond static body/seed traits and contemporaneous seed:rodent ratios. Distinguish within-species behavior shifts from species/individual turnover. For true net facilitation need a valid unhandled/exclusion counterfactual and germination or establishment outcome; primary caching alone is not beneficial dispersal.

Prior art: Li et al. 2021 (10.3897/zookeys.1025.60972) found faster spring consumption and more autumn dispersal. Vander Wall 2010 (10.1098/rstb.2009.0205) and the 2021 theoretical mast/caching study (PMC8520775) already distinguish autumn storage from winter/spring retrieval, seed pulses and consumer density. Lichti et al. (10.1111/brv.12240) already propose stage-specific mechanisms. Sachser et al. 2025 (10.1098/rsbl.2024.0586) followed 639 beech seeds; among located dispersed seeds none germinated. Thus neither seasonality itself nor a general predator/disperser dual-role claim is novel. Test a specific cross-season transition in the taxonomic contribution to seed fate or the predictability of cumulative surviving seed cohorts given phase alignment; novelty remains provisional.

## First source-only step

Dri et al. 2022 (10.1111/oik.09551): inspect checksummed original archive CSV schema, counts, literal years, original README/R input references, not model outputs or biological values. Published summer trapping preceded upcoming autumn seed availability; any actual-resource test must link a PREVIOUS realized seed crop to later capture observations. Annual seed-trap data cannot identify seed transport or fate, and 36 years at one forest are not 36 sites.

Gu et al. 2025 (10.1002/ece3.72409): already checksummed original workbook has 738 rows and 735 distinct seed codes, first/second dispersal dates, no actor PIT in the seed table, and uncertain release/final-fate dates. Audit only date parsing, month coverage, chronological validity and interval categories; keep duplicated codes and count archive rows. A dated first dispersal is NOT a release date, and dated secondary movement is NOT proof of a change in rodent identity. No seasonal fate coefficient before eligibility and cohort denominators frozen. If the source has no actual contrasting seasons, release dates or stage-specific actors, do not calculate a seasonal hazard, infer turnover or treat blank dates as zero events.

The Austrian four-cohort aggregate data and Panamanian timed seed trajectories previously audited are relevant external comparators, but lack stage-specific actor linkage; no pooling of distinct estimands. Brehm ground cover is a separate structural inventory, not a substitute if the temporal seed-fate source is inadequate. Future cross-system synthesis should use distinct seed-cohort outcomes and equal study/site weights; no universal mutualism claim from incomplete fate.

One new source workflow only; no refitting of NEON, no effect-driven subgroup selection.
