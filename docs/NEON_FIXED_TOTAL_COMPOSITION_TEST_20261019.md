# Same crowding, different neighbours: a fixed-total reading of the NEON hypothesis

**Date:** 19 October 2026. **State:** algebra and synthetic verification only; no new ecological response estimated.

## Biological hypothesis

At the same local **genus-level known-alive abundance**, focal small mammals can show different within-individual positional spread and among-individual centroid dispersion depending on how many neighbours are conspecific versus congeneric heterospecific.

The empirical comparison is not simply a larger population versus a smaller one. For illustration, compare the same focal species in otherwise comparable sessions with F=10, C=20 versus F=20, C=10, keeping unresolved abundance U constant. These are **hypothetical count configurations**, not observed NEON contrasts. They hold F+C+U constant while changing its composition. This is an observational contrast, not an instruction to replace or manipulate animals.

F, C and U are known-alive indices, not independently measured true densities. “Total” here means the target genus, **not all mammals** or all ecological competitors. W and B remain three-night capture-position statistics rather than complete home ranges, territory sizes or true activity centres.

## Preserve the previously defined primary estimand

The prior hypothesis spine defines

    Theta = (beta_FB - beta_FW) - (beta_CB - beta_CW).

That two-sided primary estimand is retained. The following is an exact re-expression of the same **additive linear model**, not a different fitted model or a retrospective replacement for an unsuccessful test.

For either outcome Y = W or B, with the same rows, weights, and nuisance fixed effects Z:

    Y = Z alpha + beta_F F + beta_C C + beta_U U + error
    N = F + C + U

Substitution C=N-F-U gives

    Y = Z alpha + beta_C N + (beta_F-beta_C) F
                    + (beta_U-beta_C) U + error.

Define theta_W = beta_FW-beta_CW and theta_B = beta_FB-beta_CB. Holding N, U and Z fixed, a one-unit higher F necessarily corresponds to a one-unit lower C. The fitted difference in Y is theta_Y. Hence the existing primary **Theta = theta_B-theta_W** is a difference between two **fixed-total composition associations**.

Use either columns F,C,U or columns N,F,U. Do not include N,F,C,U simultaneously: their exact dependence makes the full coefficient vector non-identifiable. Nonlinear/interacting models need their own local finite-difference definitions; the identity above does not automatically license changing to them.

## Important limit of a single cross-scale difference

A nonzero Theta establishes a statistical contrast between the two spatial components only if its uncertainty and the original prospective rules support that conclusion. It does not identify competition or territoriality as a cause.

Conversely, **Theta=0 does not imply that neighbour identity has no association with spatial use**. Both component contrasts can be the same nonzero value. For example, theta_W=theta_B=-3 gives Theta=0 even though both observed spatial components decrease by 3 per unit of the fixed-total composition contrast.

Illustrative parameter settings, not empirical mammal estimates:

| Synthetic setting | theta_W | theta_B | Theta | theta_W+theta_B |
|---|---:|---:|---:|---:|
| No composition association | 0 | 0 | 0 | 0 |
| Within-individual component only | -3 | 0 | +3 | -3 |
| Equal decreases in both components | -3 | -3 | 0 | -6 |
| Opposing component associations | -3 | +3 | +6 | 0 |

Keep the distinction between the narrow primary null **Theta=0** and the broader joint null **theta_W=theta_B=0**. Report theta_W and theta_B with joint uncertainty as already motivated by the hypothesis spine. A secondary joint diagnostic must not be used to relabel failure of the primary Theta test as success. A nonsignificant result is not evidence of equivalence without a separately justified equivalence margin and adequate precision. The component sum is a descriptive sum of the two metrics; it is not proof of a conserved spatial footprint or occupied area.

## U must enter the actual design check

The inspected repository function `_fwl_predictors` in `analysis/conspecific_congeneric_predictor_support_v1.py` tests F and C after series, site-by-month and year effects. **It does not condition on U.** The recorded Peromyscus rank-two result cannot therefore establish rank/support for the proposed U-adjusted model.

The new pure helper reports, without accessing any W/B outcomes:

1. Rank of F,C after Z.
2. Rank of F,C after Z and U.
3. Rank of F,C,U after Z.
4. Whether the particular contrast beta_F-beta_C is estimable; equivalently whether F retains variation after Z,N,U.

Rank deficiency needs careful interpretation. Two exact synthetic counterexamples were checked:

- If U=F, F and C can initially have rank two, but holding N and U fixes F. The replacement contrast is not identifiable.
- If U=F+C, the three coefficients are not all separately identifiable, yet beta_F-beta_C can be identifiable because composition can vary at fixed total. This **does not waive** the existing full-component/geographic/taxonomic eligibility rules. Contrast-specific estimability is reported as a diagnostic, not an automatic permission to fit outcomes.

Numerical tolerance, nuisance redundancy and row-order invariance are tested. A numerical rank test does not demonstrate adequate uncertainty coverage, independent sites, power, or empirical overlap in a scientifically relevant count range. The actual NEON F,C,U row-level design has **not** been subjected to this new check in this work. Previously published aggregate F/C cross-products and a marginal U fraction are insufficient to reconstruct its conditional geometry.

Treating U as a covariate also does not recover the unobserved species assignments inside U. The result would remain conditional on the adopted identification/measurement model. Direct molecular evidence, provider-supported current taxonomic corrections, and predeclared uncertainty sensitivity remain relevant; no retrospective label allocation is authorized here.

## Paired uncertainty and sampling support

W and B refer to the same session and the same repeat-captured cohort. Their estimation errors must not be treated as independent merely because two regressions were run. In particular:

    Var(Theta) = Var(theta_B) + Var(theta_W)
                 - 2 Cov(theta_B, theta_W).

The algebra helper transforms a supplied joint covariance; it does **not** estimate that covariance, provide a p-value, or authorize a model fit. A future application must use the original common rows/weights/controls and a declared joint covariance procedure respecting site/series dependence. Different response-specific filters would break the intended paired comparison. Failure to detect an effect in one component and detection in the other is not itself a test of their difference.

## What was executed, and what was not

Executed locally: 18 synthetic unit tests; exact coefficient reparameterization; fixed-total one-unit composition differences; paired-covariance transformation; cancellation examples; conditional-rank counterexamples; permutation and redundant-fixed-effect checks. The implementation has no network calls and no ecological regression runner.

Not executed: new NEON outcome retrieval; F/C/U-adjusted real predictor assessment; a real Theta estimate; species reassignment; molecular sequence inference; change to historical inclusion rules; new independent ecological confirmation. No original eight-genus 5/8<6/8 result, provisional holdout, or MOSA seal is modified.

## Source state inspected

- `docs/NEON_CONSPECIFIC_CONGENERIC_CROSS_SCALE_PAPER_SPINE_20261018.md`, blob `7ea5bff0468251c5e994e5d311c4f587286778a7`: existing Theta and component-reporting requirements.
- `analysis/conspecific_congeneric_predictor_support_v1.py`, blob `dd63c967309aae0d438aced84602d18c9d564b65`: current F/C-only residualization.
- `results/conspecific_congeneric_qualifier_sensitivity_receipt_20261018.json`, blob `eba840c8ec5a5623a491bbf28cfffc05b72da7f7`: prior source-only taxonomy sensitivity, not a spatial effect.
- Latest inspected branch head: `cc912a838431457c194e99130ac5918137020f1b`. Its `results/neon_molecular_history_reason_review_receipt_20261018.json` records provider molecular-rationale metadata, explicitly **not independently validated individuals or current species calls**. This work preserves those later commits and does not treat provider-history row counts as DNA-confirmed animal counts.

## Next ecological decision

First apply the declared identity handling and the new **predictor-only** N/F/U support check to the exact intended future cohort. If supported, use genuinely unconsumed observations under the existing primary Theta definition and paired W/B protocol. Keep molecular-source research subordinate to that biological question. Do not select a new habitat, species subset, or nonlinear model from favourable historical W/B results.

**Working ecological statement:** Does neighbour identity change spatial use even when genus-level crowding is comparable, and does that association differ within animals versus among their observed centres?
