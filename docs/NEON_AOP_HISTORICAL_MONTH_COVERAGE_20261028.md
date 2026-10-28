# NEON source-only historical AOP CHM flight month availability

28 October 2026, ONE unified mammal macroecology paper (PR #23), DRAFT/SUBMISSION HOLD.

Rationale: Previous five-anchor AOP CHM environmental-source pilot used the latest published month per site from 2015–2025, yielding 2022–2024 acquisitions while the original 58 mammal seasonal comparisons include capture dates in 2015–2024. Full 3000-station canonical historical positions are now source verified. To avoid substituting a late image for historical trapping environment, independently inventory ALL originally advertised official RELEASE-2026 DP3.30015.001 flight months between 2013 and 2025. This is an acquisition metadata inventory; no raster image is selected for ecological response based on its height value.

Pre-specified metadata-only selection rule: for each original capture day find the closest acquisition calendar month from the fixed site visit list, minimizing absolute month distance; in an exact tie prefer the earlier visit, never choose using mammal taxon identity, capture outcome, Z, climate or canopy value. This is only a feasibility projection, not actual dated ground habitat. Report original 348 repeated six-night day attempts/339 unique plot-day keys, counts <=3/12/24 months, earlier/later month, full 58-pair support and numbers of published site acquisition visits. Do not export sites, plots, capture dates, station locations, tile URLs, per-site years or observed biological outcomes.

Months alone do not verify spatial CHM tile coverage, exact flight dates, shrub/grass cover or genus detection probability. If there is good month support, the next work is independently source/CRC verified visit-specific raster coverage and uncertainty audit, without refitting the already opened mammal space effects. If temporal coverage is poor, retain the ecological mechanism as unidentified, not a negative mammal ecological effect. Maintain original empirical recurrence and all failed controls unchanged.

Implementation:
- analysis/run_neon_aop_historical_flight_month_v1.py
- tests/test_neon_aop_historical_flight_month_v1.py
- GitHub Action neon-aop-historical-month-availability.yml
- artifact build/neon_aop_historical_flight_month_coverage_v1.json
