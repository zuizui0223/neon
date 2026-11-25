# 25 November 2026 — close Poland session source; distinguish resource fraction and loss density

## Closure

[Run 45426233617](https://github.com/zuizui0223/neon/actions/runs/45426233617) returned STOP_CALENDAR_SESSION_SOURCE, not a density effect. Unique day-first dates (180 distinct year/date strings), but four day codes with multiple dates and four dates with multiple codes. Reconstructed only 83 calendar sessions, 81 with three-day spans and two with 7/21-day spans. Only 13/18 site-years have five sessions; eight groups exceed 80 release rows and two have nonconstant abundance. No author-summary crosswalk attempted. All original unit tests and global CI 45426233755 passed. [Log receipt](../results/neon_poland_calendar_session_v2_source_stop_20261125.json). Close both mouse-specific and all-rodent reconstruction without further regrouping. Do not treat STOP as an ecological null.

## Independent annual resource-state example, quantitative but descriptive

Huang et al. 2021, Journal of Ecology, DOI 10.1111/1365-2745.13722, sections 2.2, 2.4, 3.1, 3.2. Jinyunshan; 86 seed traps, 30,466 recorded mature seeds over 2013–2018. Highest vs lowest seed production: 315.3 vs 25.8 mature seeds/m². Original article reports estimated losses as a proportion of mature seed production (not individually tracked seeds). High vs low production: pre-dispersal vertebrate loss 8.04 vs 13.88%; post-dispersal rodent loss 46.15 vs 61.12%. Both fractions decline. Under the same published area normalization, multiplication of reported mean density and loss fractions implies:
- Vertebrate loss density high 25.35 vs low 3.58 seeds/m²; ratio 7.08.
- Rodent loss density high 145.51 vs low 15.77 seeds/m²; ratio 9.23 (rounding-only 9.21–9.25). Fraction difference -14.97 pp. Crop density ratio 12.22; threshold for increasing implied rodent loss density = 1.32. These are products of aggregate summaries under original denominator conventions, not direct counts, measured flux or intake biomass. Adjacent different seed rain, soil bank and seedling quadrats, no rodent abundance or individual transition tracking. Do not assign causal resource effects or independent samples; rounding ranges are not sampling CIs. The paper already demonstrates a trade-off between reduced predation fraction, seed mass/germination, and later establishment; no claim of novel theory.

Useful distinction for NEON: resource abundance can lower per-seed predation risk while increasing implied consumer resource throughput. A general animal population response requires actual measured food availability and consumption or abundance, time alignment and out-of-sample test. This case does not establish a connection to NEON exact-trap recurrence.

## Two new sources, no post-hoc repairs

Huang annual Dryad file 758390 (613 bytes on repository landing page, DOI 10.5061/dryad.4qrfj6q9m): original metadata, checksum if provided, six annual rows and their literal semantics. Browser download returned 403; official API attempted only, no access circumvention. 
Lichti et al. 2014 Ecology, DOI 10.1890/13-1657.1, publisher-linked Figshare collection 3306858. North American Castanea dentata and Quercus alba/rubra pairwise tagged-seed treatments; prior paper reports neighbor dormancy differences and survival. Inventory actual deposited files, distinguish supplements from raw cohorts. No effect if not present. The question is whether initial mixed-resource effects persist through later outcomes across geographically distinct forests, not another test of a known mixed-species main effect. No direct season claim. 

[Updated study register](../data/neon_seasonal_seed_fate_study_register_20261124.json). DRAFT / SUBMISSION HOLD. No formal pooled effect, no new density fit.
