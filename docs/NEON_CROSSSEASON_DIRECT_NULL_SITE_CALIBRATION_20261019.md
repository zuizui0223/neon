# Post-result calibration of the 14-site NEON lineage spatial recurrence
## Direct fixed-fixed null propagation, independent of sign symmetry

**Locked 19 October 2026 AFTER the positive primary result (14 sites; 58 source pairs; grand mean site Z=+0.800742; one-sided sign-flip p=0.001159668) was opened, and BEFORE calculating any direct all-site fixed-fixed null calibration.** This is a targeted statistical-validity challenge, not an independent replication, a new preregistration of the old ecological claim, an opportunity to select the preferable p-value, or a new biological outcome.

### Why this matters

The original physical-site sign-flip test enumerates 2^14 sign assignments exactly, **conditional on the already estimated 14 site Zs**. Its nominal exactness for the ecological null additionally requires a sign-invariance/symmetry assumption for the site statistics. Even when within-pair fixed-fixed randomization is valid, a finite binary genus×trap matrix may induce a skewed null distribution. Therefore an exact sign-flip permutation count is **not automatically an exact null-calibrated p-value for genus recurrence**.

The mechanistic inference remains restricted: a positive result cannot by itself distinguish genotype-informed taxon-specific habitat, movement, social competition, trap identity/detection, or environmental stationarity.

### Fixed post-result validation design

Use the **same checksum-verified RELEASE-2026 files, same original 58 outcome-blind selected seasonal pairs across the same 14 sites, same disjoint observed tag set, same original fixed-fixed B-null and its already frozen seed, draw count and burn-in**. Do NOT change the main source filtering, A/B occupancy, genus taxonomy, null randomization or original archived p and Z.

**Independent array collection:** Extend the original pure `fixed_fixed_null_for_unit` function only by an optional ephemeral `private_draws_out` collector of the same existing 2,000 *null overlap counts*. This option must not change an accepted swap, random generator, null mean/SD/Z, primary source keys or external output. Unit null arrays and site codes remain in RAM only, are NEVER committed as animal-level data. Each rerun's 58 original unit Z statistics (in frozen site/plot/season order) must agree with the already archived `unlabelled_unit_diagnostics` to within 1e-9, and all 14 sorted site means and the original site signflip p must match exactly. Otherwise STOP.

**Direct conditional null**: For each meta-null replicate b=1..20,000, sample **one overlap** from each of the 58 already-fixed 2,000-draw fixed-fixed null arrays, using a new **independent, deterministic random seed 2026101929**; standardize with that unit's original null mean and SD; average Z within original physical sites, then take equal-weight mean of 14 site means. The Monte Carlo one-sided tail probability is `(1 + sum(T_null >= T_observed))/(20001)`. Because the same physical site can contribute multiple units, also report a **maximally positively rank-coupled within-site** scenario: draw one uniform quantile per site/replicate, and use that same quantile for every unit's SORTED empirical null overlap distribution at that site. This comonotone marginal coupling deliberately magnifies within-site dependence, though it is **not** a validated realistic joint ecological null. It is an exploratory bounding-style stress test, not a mathematical upper bound for all possible dependence structures.

**No source-dependent retuning**: 20,000 draws, seed, original 58 units/14 sites, equal physical site weights, observed grand Z, exact matched code, one-sided direction, two coupling schemes and output precision are fixed here. No threshold, genus subset, date window, latitude, trap-station rank, habitat covariate or year interaction may be adjusted after viewing this direct-null result.

**Interpretation labels (do not rewrite primary p)**:
- Both direct conditional null and comonotonic stress p <0.05: record `SOURCE_NULL_CALIBRATION_SUPPORTS_ORIGINAL_DIRECTION_POST_RESULT`, emphasizing additional validation on **same** data, not independent confirmation.
- At least one p >=0.05: record `SOURCE_NULL_CALIBRATION_LIMITS_ORIGINAL_CLAIM`; retain the original precommitted result as a descriptive point pattern, but downgrade inferential certainty and manuscript claims, and identify which assumption failed.
- No source/chain agreement, fewer than 58 informative units or any other failure: `STOP_REPRODUCIBILITY_OR_MCMC`, no calibrated conclusion.

**Additional transparent checks**:
- Compare Monte Carlo p to original sign-flip p, not pool or average them.
- Calculate empirical lower-tail/upper-tail quantiles and null SD of the grand site statistic under both couplings; NEVER export site names or individual-season A/B trap positions.
- Reproduce the exact one-sided sign-flip p from the archived original 14 site means as a separate algebraic check; do not call it assumption-free.
- An analytic or enumerated synthetic toy 2×2 fixed-margin example must confirm original sampler conserves row and column sums; a deterministic sampler collector test must assert original null Z is unchanged with the collector enabled.

### Limits even if both tests pass

The validity of the conditional 58-unit null model still assumes that B season assignments follow the sampled fixed-fixed space under the ecological null; this is not an experimental randomized assignment. Cross-season pairs inside one physical site may share a season, or may share traps with persistent taxon-specific detectability; comonotonic and independent coupling provide two sensitivity assumptions, not a full generative model. A new genuinely independent environmental/detection cohort and ideally microhabitat/trap-operation covariates remain needed for mechanism.

San Jacinto's species-level six-grid prior, the unrelated original 8-genus W/B density *failed* test, the Peromyscus fixed-total 0 conservative matched pairs and MOSA W/B source seal are unchanged.
