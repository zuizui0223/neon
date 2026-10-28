# NEON linked distributed plant-baseplot observations: evidence-gated source audit

Research lane: one NEON mammal macroecology paper, PR #23. This is SOURCE ONLY, no biological effect fit.

Official NEON sampling design places mammal grids at a typical offset of 150 +/- 50 m from a Distributed base plant plot, with shared plotID when they are intentionally associated. Thus a shared plotID may provide independent landscape context but CANNOT be interpreted as ground cover measured at the individual mammal trap. The 2026 NEON release plant presence and percent cover data product DP1.10058.001 supplies multi-scale distributed base plot surveys, including 1 m2 subplots with plant and ground cover. Vegetation structure DP1.10098.001 supplies woody and shrub surveys sampled less frequently. The old successful all-100 mammal station AOP CHM source cannot measure ground vegetation below approximately 2 m. The mechanism between persistent genus-by-trap catchability versus true habitat use is unresolved.

Freeze exact original RELEASE-2026 small mammal 58 comparisons, 30 plots, 14 sites and six source dates per pair. Query the original 2015-04 through 2025-12 DP1.10058.001 basic files only for those sites. Predeclare a budget of 700 1m2 source CSVs / 450MB; exceeding it is a STOP. Require provider MD5 and size checks. Use only exact same-site plotID, original plant endDate, eventID and numeric-cover presence metadata. No magnitude or taxon-specific plant association is calculated. No coordinate interpolation or any same-trap cover is inferred.

For each original mammal season A and B, source-qualify an associated base-plot event within 90 and 365 days of at least one of the season's three nights. Distinguish: any plant survey metadata; verified numerical percentCover; and TWO DISTINCT plant survey events so that a single plant observation cannot count as both mammal seasons. For a descriptive neighborhood source GO require at least 20 of 58 original comparisons, eight independent physical mammal sites and 12 original plot IDs each with TWO distinct numerical-cover observations within 365 days of respective original capture seasons. These thresholds are source feasibility only, not a biological association. 2026 plant sampling was suspended at NEON, but the original mammal source analysis uses historical dates.

A plant plot located 150m from an original mammal grid is not microhabitat for any of the 100 traps. Even perfect source-year overlap cannot identify genus-specific detection, animal presence, shrub exposure at traps or causal environmental mediation. All old positive capture-space recurrence Z and negative density/operability/temperature guards remain unchanged. This is part of ONE integrated manuscript, DRAFT/SUBMISSION HOLD.

Official references:
https://www.neonscience.org/data-samples/data-collection/observational-sampling/site-level-sampling-design
https://data.neonscience.org/data-products/DP1.10058.001/RELEASE-2026
https://data.neonscience.org/data-api/endpoints/data-query/
