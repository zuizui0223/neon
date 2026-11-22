# Finland bank vole dyad spatial fidelity: individual-stationarity falsification (post-result frozen contract)

Date: 2026-11-15. Existing unified ecological manuscript PR #23; DRAFT / SUBMISSION HOLD.
This protocol was written **after** opening the same-cohort dyad-rank result (+0.469 over random autumn identity assignment) and seasonal capture-centroid displacement (+0.616 source-grid units). Its purpose is a strict **retrospective falsification/sensitivity analysis**, not independent preregistered biological confirmation.

## Distinct biological question

Does summer-to-autumn persistence of the **rank ordering of pair distances** exceed what arises automatically if each tagged vole is independently faithful to its *own* characteristic captured stations? The existing all-autumn-identity permutation destroys both individual fidelity and pair structure and cannot separate them. Published social-network methods require spatially conditioned controls before interpreting apparent partner continuity (Fisher et al. 2017, DOI 10.1111/1365-2656.12630; Farine & Carter 2022, DOI 10.1111/2041-210X.13741).

This is NOT a test of animal direct contact, reproductive partners, territory, kinship, infection transmission, true occupancy or survival. Captured trap-centroid ranks are the sole observable endpoint.

## Frozen source and identical cohort

Reuse exactly the original Mistrick et al. (2024) public source
`jmistrick/vole-spatial-manuscript` commit `47dc1e9b1f83ec2faaf7ba232e02e00f9e4cffb4`, capture CSV Git blob `343de8c3846eea21d3f0648358e159bd61bb87a2` and treatments blob `b4059f818650ce844472a80f6caf38eee65bfffe`.
Retain the 2,012 raw captures / 742 site-tag keys / 120 observed both seasons / **51** animals caught >=2 times in each season / 12 observed sites / 563 original site-trap position identities and 13 treatment codebook rows (one unsampled). **Never add individuals, sites, taxa, time periods or alternative trappability strata.**

Primary analysis retains the **exact same 10 physically independent sites, 47 animals and 102 within-site unordered animal pairs** from `analysis/run_neon_bank_vole_dyad_geometry_v1.py`, requiring >=3 animals and >=3 distinct summer and fall pair distances per site, >=8 sites/60 dyads and >=2 sites from each original factorial food×helminth group. Abort if source counts, hashes, geometry, eligibility or factorial support mismatch. Do not open a new cohort to rescue a result.

## One additional frozen null: within-animal pooled-stationarity

For each eligible tagged animal, pool ALL of that animal's original summer and autumn captured (x,y) coordinates (including repeats), with the original captured count `n_s` and `n_f` retained. For each of **2,000** fixed-seed replicate worlds:
1. Independently shuffle that animal's pooled capture coordinate records; assign its first `n_s` positions to hypothetical summer and the remaining `n_f` to hypothetical autumn, preserving the original station preferences and observation counts of THAT animal.
2. Recalculate each animal's two centroids, same-identity unordered pair distances and site-level tie-aware summer-to-autumn Spearman rho. Ranks use midranks with distance ties defined at 1e-10 as in the original dyad code.
3. All animal label identities, sites, trap-coordinate source values, pooled individual location frequencies and capture counts are kept. DO NOT permute identities between different voles or different sites.
4. If a randomized site's summer or autumn pair-distance vector has zero rank variance, record a nonestimable permutation. Require >=1,900/2,000 estimable simulations per site; otherwise STOP all result reporting. Do NOT fill with zero, optimize random seed or change the original cohort.

Fixed RNG seed **2026111567**. Recompute the **observed** site Spearman on unchanged original seasonal centroids, then report for each site only in private: observed rho; expected rho under *individual fixed pooled station preference*; and residual `rho_observed - mean(rho_stationarity_null)`.

Primary aggregate: unweighted mean of the site residuals; **5,000** whole-site bootstrap draws stratified within the four original food×helminth source cells (2/3/3/2 site counts, without changing source membership), percentile 95% descriptive interval; number of positive and negative residual sites. Do not treat the 102 dyads or capture records as independent units. Report both observed and null site-equal means, uncertainty, null-degeneracy counts, exact source support and limitations. No confirmatory p-value, no demographic or treatment subgroup analysis.

## Interpretation decided before this sensitivity is run

- If the site-equal residual is near zero, negative or has a descriptive 95% interval including zero, **individual positional preferences are sufficient as a plausible observational explanation** for the originally positive ID-shuffle contrast. This is NOT proof no dyad behavior exists.
- If residual is positive with a descriptive interval entirely above zero and consistent site signs, it would be **an exploratory excess of captured pair-distance rank persistence beyond this stationary-individual capture null only**; it still does not identify social ties, dynamic individual movement, environmental resources, trap-specific capture probability or fitness.
- The individual-stationarity null assumes exchangeable captured trap positions across seasons *within animal*, and does not preserve season-specific vegetation, available trap positions, trapping schedule or behavior. Thus it may fail biologically even with a valid source; failure to exceed it is not a causal attribution to site fidelity.

Original NEON 14-site Z+0.795, Portal 436 reference-conditioned non-support, Finland 51-animal centroid shift, Finland original 10-site +0.469 against identity-shuffle, future NEON density 5/8 generality FAIL and Structural map-based island results are all **historical frozen endpoints** and remain unchanged. No cross-system pooling or journal-submission promotion based on this retrospective analysis.

## Planned reproducible implementation

`analysis/run_neon_bank_vole_individual_stationarity_null_v1.py` reads checksum-pinned original bytes, imports original centroid and tie-handling helpers, verifies the original cohort, simulates the null and writes only aggregate anonymous summary into `build/neon_bank_vole_individual_stationarity_20261115.json`. NO tag/site identifiers or raw coordinates are exported. A separate validated result receipt may be added only after the runner or local source-reconstruction is checked.

Prior primary receipt: `results/neon_bank_vole_dyad_geometry_receipt_20261115.json`.
