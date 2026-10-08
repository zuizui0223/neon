# Portal spatial effect execution supplement — frozen before spatial response access

Derived from docs/PORTAL_SPATIAL_RECOLONIZATION_HYPOTHESIS_LOCK_V1.md.

- Keep frozen cohorts, support gate, valid dates, species DM/DO/DS, plot unit and sample size 10 captures exactly.
- Resample 10 capture locations without replacement within each supported plot × six-month window, 500 draws per plot-window, seed 20261008. Compute mean pairwise Euclidean distance on a 6.25 m-spaced 7×7 lattice.
- Aggregate repeated windows **within plot**, then plot means **within cohort**.
- Explicit pre-result comparison: "early" post-switch windows 0–1 (April 2015–March 2016) versus "later" windows 2–5 (April 2016–March 2018). If a plot lacks support in either period, exclude it from the early/later paired contrast; do not relax support.
- Primary directional prediction: KR-return minus rodent-return MPD initially negative; difference-in-differences (later minus early treatment contrast) positive as spatial occupancy broadens.
- 5,000 cluster bootstrap draws at independent plot level and exact one-sided label permutations between supported KR-return and rodent-return plots. With at most three treatment plots per group, a significant result may not be achievable; disclose this.
- Long-term control plots are a descriptive reference, not interchangeable randomized treatment units.
- Distinguish null/unsupported outcomes from sampling failure. Do not call this a San Jacinto check-level replication, a proof of interspecific competition, or a measurement of individual home ranges.
