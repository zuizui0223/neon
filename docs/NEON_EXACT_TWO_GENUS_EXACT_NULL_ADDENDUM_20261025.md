# Pre-effect statistical correction to exact-two-genus exploratory contract
**Dated and committed 25 October 2026, BEFORE opening any exactly-two-genus `A × B` overlap, Z or biological outcome.** This addendum replaces ONLY the sampler implementation and associated sampler-quality paragraph of `docs/NEON_EXACT_TWO_GENUS_MACRO_EXPANSION_20261025.md`; it does not change the source eligibility group, spatial statistic, direction, site/domain thresholds, effort, taxa or treatment of the prior 58 comparisons.

## Why an exact null exists specifically with TWO genera

Let the original season-B genus rows be `B1, B2`. Under fixed genus-row and trap-column sums:
- a trap with both genera detected (`column sum=2`) has forced assignments;
- a trap with no genus (`column sum=0`) has forced assignments;
- a trap with exactly one genus (`column sum=1`) can be assigned to exactly one of the two genera.

Let `m` be the number of columns with single genus, `a` the observed season-B count of those columns assigned genus1, and `d` the number of double-occupied columns. The uniform fixed-margin null consists of **exactly `choose(m,a)` equally weighted matrices**, determined by choosing `a` of the `m` singleton columns for genus1. This is a direct enumeration of the **same uniform fixed-margin target** as the corrected lazy proposal-clock Markov chain, but requires no MCMC. The target probability is not the old invalid accepted-only jump chain.

Fix season A. For each season-B singleton station `t`, define weight `w_t=A1_t−A2_t ∈{-1,0,+1}`. The overlap is `O=D+sum_{t singleton}A2_t+sum_{t chosen B1}w_t` with `D=sum_{t both B}(A1_t+A2_t)`. Let numbers of singleton columns with weights `+1,-1,0` be `n+,n-,n0`. For chosen counts `x` positive, `y` negative and `z=a−x−y` zero, the **exact null probability** is:
`P(x,y,z)=[C(n+,x) C(n-,y) C(n0,z)]/C(m,a)`.
This yields the complete exact finite null PMF for `O` without approximating the marginal null or selecting a favourable effect.

## Revised Phase 2 (all phase 1 gate conditions unchanged)

- **First** confirm source-only 158 exact-two pairs, 58 original three-plus pairs and the frozen 216 two-plus denominator, with >=12 physical sites and >=8 domains; if the source gate fails, no effect is opened.
- **For each exact-two pair**, retain both original seasonally nonshared tag sets, same genus × A1–J10 occupancy. Calculate the observed `O` and its fully **enumerated exact fixed-margin null**, with all structural B margins unchanged. Unit `Z=(O−E_0 O)/SD_0 O` only if exact null variance is nonzero. An uninformative unit remains in denominators.
- **Pre-effect outcome feasibility**: at least **40** of 158 units informative, at least **8** independent physical sites with any informative unit, and >=**75% of all 158** source units with positive exact-null variance. If not, STOP biological inference as not estimable.
- **Geographic endpoint**: equally weight mean `Z` within physical sites, then equally weight sites. Report ALL signs, including negatives. Positive mean and conditional meta-null p<0.05 under both independent draws from the **exact** per-unit PMFs and a **within-site comonotone rank-coupled** stress may be described as an exploratory positive conditional recurrence result (never a new independent confirmatory replication). If either mode fails, report it. No subgroup selection or threshold changes.
- **Conditional meta inference**: 20,000 independent-unit and 20,000 within-site rank-coupled site-weighted draws. Draw from exact PMFs; Monte Carlo uncertainty arises **only** in this site-combination calibration, not individual two-row null enumeration. Rank coupling is a stress, not a valid upper bound on all ecological dependence.
- **Source-reused season sensitivity**: remove entire physical sites containing ANY repeated site×plot×season keys, regardless of observed site effect, and repeat only if at least 8 remaining independent sites and >=40 informative original source seasonal pairs. Otherwise report not estimable. Never remove selectively favourable/negative pairs.
- **Unit test prior to source outcome:** verify 2-row exact distribution against brute-force enumeration of every admissible small fixed-margin matrix (row sums and trap richness retained), including forced double-positive B stations, impossible swaps, zero variance, tail probabilities, and identity under row relabelling. Never run the original biased accepted-clock sampler.
- Existing 3+-genus corrected sampler, its +0.795 original effect, old failed 5/8 density generality and all provenance remain unchanged. **No p-value pooling across taxonomic richness groups or with San Jacinto**.

## Rationale and integrity

This exact method was chosen solely from the algebra of two fixed rows, **before any new exploratory spatial result was opened**. It improves finite-null statistical validity and speed, not the original ecological hypotheses. The original phase 2 instruction to run 2 × 2000 corrected MCMC draws with Rhat/ESS is superseded here because the exact per-unit null needs no mixing or convergence diagnostic. Its originally stated 75% variance-support, >=40 units and >=8 sites feasibility gates remain unchanged. If source coverage is insufficient, none of this authorizes new biological analysis.
