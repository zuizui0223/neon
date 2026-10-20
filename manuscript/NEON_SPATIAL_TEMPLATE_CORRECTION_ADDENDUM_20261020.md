# Corrected statistical results for seasonal genus-associated trap recurrence

**20 October 2026 — current statistical addendum to `NEON_SPATIAL_TEMPLATE_REASSEMBLY_ECOLOGY_V0_1.md` and `V0_2.md`.**

This addendum supersedes those drafts' characterization of the original accepted-swap sampler as a calibrated uniform fixed-margin null. The earlier files and numerical receipts remain historical records; they are not additional independent evidence alongside the corrected analysis. The main ecological question and original observational cohort are unchanged. No manuscript has been submitted.

## Current ecological conclusion

The positive conditional observation pattern survives the sampler correction: genus-associated nominal trap positions recur across adjacent seasons among nonshared observed tagged-animal sets more strongly than under the specified fixed-margin randomization. For all 14 original sites (58 comparisons), corrected mean site Z is **+0.794664**, with 11 positive site means. Removing both source-defined sites that reuse seasonal observations leaves 12 sites and 46 comparisons, with corrected mean Z **+0.843162** and 10 positive site means. Both cohorts remain in the positive tail under independent-unit and within-site comonotone conditional-null calibrations.

This is a correction of an already-inspected dataset, not new biological replication or new preregistration. It supports a pattern of captured genus-associated spatial recurrence, not a causal competition mechanism, genetically validated species-specific niches, full home ranges or verified demographic replacement.

## Error, cause, correction and verification

The original implementation proposed a pair of matrix rows, attempted a margin-preserving swap, and retried unsuccessful proposals until a swap succeeded. It measured burn-in and sample spacing in **accepted swaps**. Although the one-attempt proposal kernel is symmetric, its accepted-only jump chain does not generally have a uniform stationary distribution over fixed-margin binary matrices: state probability is proportional to the probability of leaving that state.

An exact synthetic counterexample with row totals (2,2,2), column totals (1,1,2,2) and 15 admissible matrices demonstrates the error. Uniform sampling assigns mass 1/15 to each state; the accepted-only chain assigns 1/21 to three states and 1/14 to the other twelve. For one observed arrangement, the probability of overlap at least six is 1/15 under the uniform distribution but 1/21 under the accepted-only chain. These values are an exact mathematical demonstration, **not estimates of NEON bias**. In that example, both null means are 10/3, so mean matching does not validate tail probabilities.

We corrected the clock rather than the ecological design. Each step now consists of one lazy row-pair proposal; failed proposals and intentional holds are retained. A one-half hold probability ensures aperiodicity. A successful row-pair swap preserves the sizes of both exclusive column sets, giving equal forward and reverse proposal probabilities. Thus the kernel is symmetric and has the uniform fixed-margin target. Exact finite-state transition and stationarity tests, empirical frequency tests, preserved-margin tests, two-chain checks and output-privacy tests all passed (seven tests).

The tests establish the kernel's intended stationary target, not exact independent draws after a finite simulation. Consequently, the corrected analysis also checked two chains for every real-data comparison, with no failed unit dropped to create significance.

## Corrected methods to replace the old sampling paragraph

The unchanged source reconstruction reproduced all 58 eligible comparisons at the original 14 sites, genus labels, nominal station margins and shared-tag exclusions. The two-site sensitivity was determined by source site/plot/season reuse, not by observed effect signs. We checked 3,547 source-manifest files against the existing source workflow, reconstructing 21,363 plot rows and 1,505,827 trap rows.

For each of the 58 fixed-margin seasonal comparisons, two independent seeded proposal-clock chains retained 2,000 overlap draws each after 10,000 burn-in proposals, with 100 proposals between retained draws. All failed proposals and lazy holds count. The first chain seed was 2026102001 plus the source-sorted unit index, and the second used offset 1000003. The pre-written correction required nonzero overlap variance, split-Rhat below 1.05, and batch-means effective sample size at least 200 in both chains. All 58 comparisons passed; maximum split-Rhat was 1.001347 and the minimum chain effective sample size was 1023.947. No unit was removed for chain quality.

Corrected standardized overlap scores were averaged first within physical site and then equally across sites. We used 100,000 draws under a conditional product of unit null distributions and 20,000 draws under a within-site comonotone rank coupling of the same null marginals. These avoid relying on sign symmetry of the site statistics. Comonotone coupling is a strong dependence sensitivity, **not** a demonstrated joint ecological process or an upper bound over every possible dependence structure. The 12-site cohort has no reused seasonal keys, but may still have within-site environmental or detection dependence.

The corrected sign-flip p-values (0.00103760 for 14 sites and 0.00122070 for 12 sites) are retained only as descriptive historical-style comparisons, not the principal uniform-null calibration or assumption-free exact ecological probabilities.

## Corrected results

| Quantity | All original sites | Source-season-reuse sites excluded |
|---|---:|---:|
| Physical sites | 14 | 12 |
| Seasonal comparisons | 58 | 46 |
| Positive site means | 11 | 10 |
| Corrected mean site Z | +0.794663773 | +0.843161730 |
| Earlier accepted-clock mean Z (historical) | +0.800742017 | +0.849774204 |
| Independent conditional-null exceedances | 0 / 100,000 | 0 / 100,000 |
| Independent-null +1 probability | 1 / 100,001 | 1 / 100,001 |
| Within-site comonotone exceedances | 24 / 20,000 | 41 / 20,000 |
| Comonotone +1 probability | 0.001249938 | 0.002099895 |

The independent-null value of approximately 0.000010 is a simulation resolution floor, not a known exact tail probability or a zero probability. The respective central 95% simulated ranges for the site-level statistic are [-0.325907, +0.330389] and [-0.369557, +0.376176], compared with observed means +0.794664 and +0.843162. These are **null reference intervals**, not confidence intervals for the observed ecological effect.

Across the 58 comparisons, the mean absolute change in standardized Z was 0.029074 and the maximum was 0.150160. These differences combine the corrected sampler clock with finite Monte Carlo variation from the new chains and should not be labelled a pure estimate of bias. The underlying observed occupancy patterns and their margins did not change.

## Inferential and publication status

The corrected results show that the positive conditional NEON pattern is not eliminated by either the known accepted-clock error or the removal of the two source-season-reuse sites. They do not validate earlier biased-sampler p-values retroactively. Those values, including the earlier direct-null and site-influence checks, are preserved only to disclose how the analysis changed.

Persistent genus-dependent capture probability and local habitat structure have not been separated. Removing shared observed tags does not prove true demographic replacement, and inference remains at genus rather than verified species resolution. The San Jacinto species-level analysis was not rerun here, so its null implementation and uncertainty require separate review before describing it as a corrected independent confirmation. Do not pool its p-value with NEON.

The earlier density W/B generality failure (5 positive genera versus six required), imprecise provisional Peromyscus nonreplication, lack of conservative fixed-total F/C matched pairs, and sealed MOSA W/B outcomes are unchanged. No habitat or density response was fitted during this correction.

## Reproducibility and verification status

- Corrected source workflow: Actions **39370044411**, job **118455621391**, success, at commit `4f7d7288dde3d5e627bdaa08263e61a1a2b3af76`.
- Full machine-generated result: artifact **12241137829**, `neon-uniform-null-correction-v2`, containing `neon_uniform_null_correction_v2.json` with all 58 unit diagnostics.
- Artifact ZIP SHA-256: `92961984ebedc33abfd410ae9d587cf6eb2cbe69c1ec252d1c05c455938c56cb`. The downloaded bytes and aggregate means, positive counts, p-value arithmetic and chain summaries were independently checked locally.
- Current aggregate receipt: `results/neon_uniform_null_correction_receipt_20261020.json`.
- Error proof: `results/neon_sampler_finite_state_audit_20261020.json`; corrective plan: `docs/NEON_NULL_PROPOSAL_CLOCK_CORRECTION_20261020.md`.
- Corrected code and tests: `analysis/neon_proposal_clock_v2.py`, `analysis/run_neon_uniform_null_correction_v2.py`, `tests/test_neon_proposal_clock_v2.py`.

The dedicated correction workflow passed. The repository-wide CI at the same run head did **not** pass: 429 tests, one error and three skips, caused by the already-missing `analysis.audit_neon_lineage_environmental_source_coverage_v1` module. The seven new sampler tests passed there as well. This unrelated unfinished module was not filled with a placeholder or silently skipped. Full integration remains outstanding; do not describe the entire repository as green.

**Status: corrected conditional ecological pattern supported; research draft, not submitted.**
