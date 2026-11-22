# Fixed-margin null sampler correction — 20 October 2026

## Current decision
The original 14-site/58-pair recurrence and the newly retrieved 12-site/46-pair sensitivity all used the SAME accepted-swap-clock kernel. Their numeric records are retained as historical computations, but their p-values must NOT be represented as calibrated uniform fixed-margin tests until this implementation error is corrected. This is a correctness correction after viewing results, not new preregistration, new biological data, or a change in the ecological question.

## Completed source-overlap exclusion (historical sampler only)
Actions 39220781449, job 117955314320, commit 93791a8b37f2062543d7b23f67f4617182bd3fe6 succeeded on 19 October. Removing both sites with reused site/plot/season keys removed 12 pairs, leaving 12 sites and 46 pairs, no reused keys. Mean site Z=0.8497742041226968, 10/12 positive; sign-flip p=0.00146484375. Independent-unit product null: 0/100000 exceedances (+1 p=1/100001); within-site comonotone stress: 24/20000 exceedances (+1 p=25/20001=0.0012499375031248437). Artifact 12171887814, sha256:9843f625f4a1fc16268ba9cd7ec7a1e85ae170964b50f1904521c8ec71b41b73. These computations do not resolve an error shared by their underlying sampler.

## Root cause and exact counterexample
`analysis/neon_crossseason_template_null_v1.py` draws a row pair, swaps one exclusive occupied column from each row when possible, and RETRIES until a swap succeeds. It measures burn-in/thinning in accepted moves. The one-attempt kernel P is symmetric because the two exclusive-set sizes are preserved by the reverse swap. But discarding self-transitions changes its stationary distribution: the jump chain targets probability proportional to 1-P(x,x), not a uniform distribution when move availability differs among matrices.

Exact enumeration: row totals (2,2,2), column totals (1,1,2,2), 15 admissible matrices. Under uniform fixed margins each matrix has probability 1/15. The accepted-only chain assigns 1/21 to each of three states with an identical-row pair, and 1/14 to the other twelve. For the fully matching arrangement [(0,0,1,1),(0,0,1,1),(1,1,0,0)], the probability of overlap >=6 is 1/15 under uniform sampling but 1/21 under the accepted-only chain. This is a synthetic exact mathematical counterexample, NOT a numerical estimate of the bias in the NEON result. Keeping margins fixed and obtaining low lag-1 autocorrelation do not establish uniformity.

Local regression test against the faithful old accepted-only step failed: maximum state-frequency deviation from 1/15 was 0.0198902, above tolerance 0.004. A proposal-clock implementation passed seven tests, including exact rational transition symmetry, uniform stationarity on all 15 states, empirical frequencies, preserved margins, two-chain diagnostics and no raw identifiers in outputs.

Context: Carstens (2015), Physical Review E 91:042812, DOI 10.1103/PhysRevE.91.042812, explicitly establishes the need to retain certain failed trades for uniform fixed-margin sampling. The proof here concerns this repository's row-pair swap directly, rather than claiming that our swap is the Curveball algorithm.

## Corrective analysis frozen before corrected NEON results
Keep the same source release, 58 pairs, 14 sites, genus labels, trap margins, shared-tag exclusions, source sorting and site equal weighting. Do not alter inclusion thresholds, choose favorable sites, or run environmental moderators.

Replace only the sampler clock: each step makes one row-pair proposal; unsuccessful proposals count. Include probability 1/2 of a hold for aperiodicity. Count ALL proposals, not accepted swaps. This symmetric lazy kernel has uniform fixed-margin stationary distribution. Uniform stationary distribution is not a guarantee of independent draws at finite running time.

Run two chains per unit, 2000 retained draws per chain, 10000 burn-in proposals and 100 proposal steps between draws. Unit seed=2026102001+original sorted unit index; second chain offset=1000003. Require nonzero null SD, split-Rhat<1.05 and batch-means ESS>=200 in BOTH chains. Report all 58 units; if any fails, retain the failure and label the rerun HOLD rather than silently removing units or tuning settings.

Calculate corrected Z and site means, retaining the former sign-flip test only as a historical-style descriptor. Direct conditional unit-independent product null uses 100000 draws; within-site rank-comonotone stress uses 20000 draws. Report both full 14 sites and the pre-existing source-defined 12-site exclusion; no p-value pooling, no claimed bound over every possible joint ecological null. Seeds are specified in the new runner before execution. The same-source dependent observations, genus-specific capture probability and habitat structure remain unresolved.

If corrected results do not support recurrence, withdraw the former supported-pattern claim. If they do, replace the inferential reference with the corrected estimates and disclose the implementation error and same-data reanalysis. All original density W/B failures, F/C matched-pair limitations, and MOSA seals remain unchanged. No journal submission is authorized by this correction.
