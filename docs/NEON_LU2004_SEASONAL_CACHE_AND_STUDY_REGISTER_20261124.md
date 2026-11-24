# Independent seasonal seed-fate evidence: Lu & Zhang 2004

24 November 2026. Li 2021 prior CI 45394455170 passed 929 tests (3 skipped). Yang/Holt remain closed.

Lu & Zhang, Acta Oecologica 26:247–254, DOI 10.1016/j.actao.2004.08.002. Original PDF methods p.249 and Tables 3/4 p.251 visually checked. Donglingshan Beijing, 3,600 wild apricot seeds in 2002, 600 per habitat-season, 16-day observation. Table 4 concerns fates **after removal**. Removed minus sum of listed fate counts differs in four cells: low spring +1, low autumn −9, high summer +1, high autumn +3. Do not guess a correction; Table 3 cache sample counts agree with Table 4 in all six cells.

Conditional on accurate printed removal/hoarding columns and caching requiring removal during the observation window, reported hoards bound the cache fraction below and all removals bound it above. No use of inconsistent fate partition.

| Season | Released | Recorded hoarded | Removed | Broad cache interval (%) |
|---|---:|---:|---:|---:|
| Spring | 1200 | 88 | 334 | 7.33–27.83 |
| Summer | 1200 | 15 | 62 | 1.25–5.17 |
| Autumn | 1200 | 209 | 978 | 17.42–81.50 |

Spring-minus-summer +2.167 to +26.583 pp; autumn-minus-summer +12.25 to +80.25 pp. Both lower bounds positive in each habitat. Autumn-minus-spring −10.417 to +74.167 pp, unresolved. Bounds are not confidence intervals; no claim of robustness to errors in the removal/hoarding columns themselves. Reported three established seedlings originated in spring releases in high shrub, not a complete recruitment comparison. Eaten after removal is not total predation.

Li identifies higher spring total predation under published missing-fate extremes, not higher autumn caching. Lu identifies a summer cache trough with a different observation duration and endpoint. Do not pool. Lai 2025 reports high summer predation and low summer caching vs winter, missing category/duration unverified. Rusch 2014 fynbos links food availability and seasonal diet/cache changes, already prior art. The 2007 mast study shares Donglingshan site group, and Ma 2010 may overlap another report of the same 1,800 seeds. See study register. Next test would distinguish immediate consumption demand from storage demand across sites, using independently measured resource supply, rodent abundance and season phase. Two descriptive calculations are not a meta-analysis. DRAFT / SUBMISSION HOLD. No causal NEON mechanism claim.

Reproduce: python -m analysis.neon_lu2004_seasonal_cache_bounds_v1
