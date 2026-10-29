# Peromyscus holdout: identifying density variation is unevenly distributed

**2026-10-12. Post-result design diagnostic, not an ecological mechanism claim or a replacement for the frozen tests.**

## What was newly checked

The three original archived inputs matched their recorded SHA256 digests. Independent SVD projection (also checked with pivoted QR) reproduced the frozen development coefficient +15.930057, provisional holdout coefficient -7.072965, and holdout effective-rank site-CR1 standard error 20.346861. No new ecological predictor, favourable subset or alternative response model was fitted.

| Property | Development | Provisional holdout |
|---|---:|---:|
| Sessions | 956 | 127 |
| Sites in the unchanged cohort | 33 | 19 |
| Sites with numerically zero residual MNKA variation | 0 | 6 |
| Residual MNKA sum of squares | 43,091.44 | 2,589.68 |
| Share in the three highest-information sites | 20.67% | 54.86% |
| Share in the five highest-information sites | 32.05% | 72.85% |
| Concentration-equivalent site count | 21.97 | 7.69 |

The six holdout sites are BART, BLAN, CLBJ, NIWO, ORNL and STEI (19 sessions). Within these eligible observations, every site-by-calendar-month category occurs once. The frozen site-month effects consequently absorb all local MNKA variation. Those observations cannot separately identify the density coefficient under this model. **This is not evidence of a missing biological density response. All six sites and all 127 observations remain in the original analysis.**

The largest shares of remaining predictor variation are MLBS (20.45%), NOGP (17.77%) and KONA (16.64%). Site ranking uses residualized MNKA only, never W/B values or the direction of site-specific effects.

## What the concentration index means

Let residualized MNKA be x_tilde = (I - P_Z)x using the unchanged series, site-month and year design. Each site's share is p_g = sum(x_tilde_i squared within site g) / sum(x_tilde_i squared overall). The concentration-equivalent count is 1 / sum(p_g squared).

The value 7.69 describes uneven allocation of the coefficient's identifying predictor variation. It is **not** an independent-animal sample size, a new cluster count, or a replacement degrees of freedom. Existing confidence intervals are not changed by this diagnostic. General cautions on fixed effects and clustered uncertainty are discussed by Cameron and Miller (2015), DOI 10.3368/jhr.50.2.317.

The earlier 6.0% comparison concerns residual predictor sum of squares, not total statistical information. Outcome residual noise and within-site dependence also matter: the ratio of inverse empirical CR1 variances is 2.68%, which is a different, outcome-dependent precision measure. Neither number supplies a sample-size guarantee.

## Biological interpretation and next evidence

The unresolved question is whether abundance changes are associated with different changes in within-individual capture-coordinate variance and among-centroid variance. The new observations do not confirm the old positive-direction prediction, but also do not precisely exclude its magnitude.

A useful future comparison should repeatedly observe the **same taxon/site/plot in comparable calendar months**, with MNKA varying across repeats, and spread that identifying variation across sites. More unmatched seasons can increase record counts while leaving seasonal and density differences inseparable under the fixed model. This is a sampling-design implication, not a new ecological discovery or permission to drop seasonal adjustment.

The original development 6/8 generality failure, full five-genus future inestimability and failed Peromyscus positive-direction rule remain unchanged. There is still no demonstrated temporal regime switch, territoriality or active repulsion. Provisional input revisions and cross-release marked-individual overlap remain limitations.

## Evidence and reproduction

The machine-readable record is `results/peromyscus_holdout_partial_leverage_audit_v1.json`.

A self-contained reproduction bundle delivered with this audit contains the three exact source archives, the full per-site output, `analysis/audit_peromyscus_holdout_partial_leverage_v1.py`, seven unit tests and execution logs. Its script SHA256 is `6deb9f4352bde8834334dcf3f2873dde2bf5be8e0f833209372cdd413bdd8d4f`. The script and tests are bundle paths, not newly installed modules in this branch.

The seven local tests passed: zero identifying variation from singleton site-months, outcome-independent rankings, row-order invariance, redundant fixed effects, constant MNKA rejection, nonfinite value rejection and source-hash mismatch rejection. No new remote GitHub Actions success is asserted.
