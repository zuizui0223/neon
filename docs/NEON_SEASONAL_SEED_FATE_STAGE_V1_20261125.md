# Seasonal seed-fate stage shifts — 25 November 2026
Status: exploratory published-aggregate reanalysis; independent seed-fate manuscript direction, not a new NEON capture-space effect. No submission or merge. Parent aff15c4c49a8e25a6bbd27b5037e1708949e4d34; original spatial manuscript and source STOPs unchanged.

## Research question and prior art
Does the seasonal direction of seed removal misrepresent the direction of seed predation because the allocation of recorded handled seeds to removal versus in-situ consumption changes? Do opposing stage responses offset one another across resource contexts?
Lichti, Steele & Swihart (2017), doi:10.1111/brv.12240 already decomposed seed fate into six subprocesses; Zwolak et al. (2024), doi:10.1111/1365-2745.14356 already modelled stage-specific effects of mouse abundance and within-season date. Novelty must be earned through comparable within-study seasonal contrasts and independent resource-context prediction, not the product identity or seasonality itself.

## Fixed descriptive estimands
For offered seeds N, H=(N-IS)/N (recorded removed or eaten at station, NOT all animal encounters); R=(PR+IR+HR+MR)/N (all recorded removals); M=R/H (recorded removal among handled); K=HR/N (recorded buried seeds); Q=K/R (recorded buried among removed). P=(PS+PR)/N. H, R, K, P are fractions of release cohort. Missing after removal MR is not assigned to a fate. K=H*M*Q, R=H*M. At equal follow-up the symmetric two-factor split of a product ab is (a1-a0)*(b1+b0)/2 + (b1-b0)*(a1+a0)/2; descriptive arithmetic, not causal attribution. Do not use H for Lu because in-situ fate counts are unavailable here. No epsilon for zeros; no ratios when denominators are zero.

## Li et al. 2021, independent northeastern China source
DOI 10.3897/zookeys.1025.60972; published Results "Seed fate", Fig. 4, https://pmc.ncbi.nlm.nih.gov/articles/PMC7997858/; matched to existing data/neon_li2021_seasonal_published_fates_20261124.json. Four species, spring 15 stations/1200 nominal seeds, autumn 9/720, same scheduled 60-day investigations; published rounded percentages, do not infer integer counts or station-level uncertainty. Published six categories sum to one in each season.

| Recorded fraction (%) | Spring | Autumn |
|---|---:|---:|
| H | 85.80 | 74.86 |
| R | 44.28 | 66.39 |
| M | 51.60839 | 88.68555 |
| K | 11.07 | 19.58 |
| Q | 25.00000 | 29.49239 |
| P | 55.11 | 16.39 |
| MR | 18.17 | 33.61 |

R autumn-spring +22.11 pp; H contribution -7.67408 pp, M contribution +29.78408 pp. K autumn-spring +8.51 pp; R contribution +6.02413 pp, Q contribution +2.48587 pp. Opposed H and M signs are identified for observed aggregate fates, not within-animal switching, causal seasonal effects, or equivalence of stations/species composition.
Worst-case unidentified final fates: spring P 55.11–73.28%, autumn P 16.39–50.00%, spring minus autumn +5.11 to +56.89 pp. Printed rounding cannot reverse this. K autumn-spring -9.66 to +42.12 pp; Q difference -36.54193 to +55.11749 pp, not identified. These are missing-fate bounds at reported endpoint, not confidence intervals or ever-cached transitions. Lower confirmed P and higher R in autumn are robust to assigning the missing removed seeds to predation.

## Lu & Zhang 2004, Donglingshan
DOI 10.1016/j.actao.2004.08.002, data/neon_lu2004_published_seasonal_release_counts_20261124.json. 1200 per season, 16 days. R spring 334/1200, summer 62/1200, autumn 978/1200. K 88/1200,15/1200,209/1200. Q 26.34731%,24.19355%,21.37014%. Summer to autumn K +16.16667 pp = R +17.39014 pp plus Q -1.22348 pp. Spring to summer reversed sign; spring minus summer +6.08333 pp = R +5.72796 pp plus Q +0.35537 pp. Table 4 has four mismatches; use only printed release, removal and hoarding totals, not a fabricated complete partition. P not comparable. Pooled Q change is not universal across two habitats: autumn vs summer low 85/503 vs 8/27, high 124/475 vs 7/35. Broad K autumn-summer lower bound +12.25 pp under recorded removal upper ceiling, but Q direction and true ever-caching are unresolved.

## Geographic extension, literature only (not pooled)
Haugaasen et al. 2010, Brazil nut, https://www.cambridge.org/core/journals/journal-of-tropical-ecology/article/abs/seed-dispersal-of-the-brazil-nut-tree-bertholletia-excelsa-by-scatterhoarding-rodents-in-a-central-amazonian-forest/38B37BBE2AA578977A32B62F58969DA2: dry season faster removal and longer distances, wet season higher recorded burial and longer primary cache duration. Original authors' result; no independent recomputation because denominator discrepancy and follow-up semantics remain unresolved.
Yadok et al. 2018, Nigerian montane forest conference proceedings pp.255–260, https://nscbconf2018.wordpress.com/wp-content/uploads/2018/05/42_70-nscb-2018.pdf: 12 interior plots, artificial seeds, 2016; wet removal faster (original p=.03), all removed by day five, seed fate comparison p=.19 and distances 7.37/7.34 m. Table 1 gives model probabilities, not observed counts; contains "remained" despite reported complete removal. Do not infer matching horizon or count denominators. No equivalence claim or quantitative pooling. Original PDF pp.257–258 visually inspected. Artificial seeds cannot demonstrate recruitment.
Lai et al. 2025 doi:10.1111/1749-4877.12912: higher summer predation, lower cache, longer displacement; abstract only, source fate and followup still require verification. Prior source register retained.
External source candidates for further resource-state analysis: Cao et al. 2018 doi:10.5061/dryad.4vh37hn (interannual pilferage; not seasonal), Guo et al. 2026 doi:10.5061/dryad.g79cnp64s (artificial seeds, composition treatment, November only, not a seasonal contrast); published results already stage-specific. No raw data acquired, no new independent estimate.

## Next analysis gate
Study unit is matched site × seed taxon/experimental treatment × season pair with same time horizon and denominator definition; block station/plot and source landscape, no pseudo-replication of pooled seeds. Record distinct endpoints H,R,K,P, missing fates and optionally linked cache recovery/germination. Compare stage log-risk ratios or product contributions within matched contrasts, test joint sign discordance and its robustness to missing fate assignments, not differences in significance. Do not label a higher/lower resource phase using the observed fate itself. Resource and rodent density must be independently measured; seasons within same year or repeat matched phase across years. Do not code non-significant as zero. No universal climate claim without new geographically independent matched cohorts. No formal meta-analysis yet. NEON seedfall–pregnancy gate remains STOP and is not evidence of mechanism. Distinguish movement from successful dispersal and recruitment; net mutualism requires an unhandled/control establishment counterfactual.
