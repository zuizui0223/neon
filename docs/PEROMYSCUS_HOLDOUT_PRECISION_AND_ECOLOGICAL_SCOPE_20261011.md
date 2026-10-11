# NEON Peromyscus: nonreplication versus exclusion (2026-10-11)

**Status:** post-result statistical calibration of the *unchanged* prospective NEON ecology test. This document does **not** revise the prespecified success condition, infer a new mechanism, or establish a temporal regime shift.

## Two decisions that must not be conflated

1. **Prespecified directional replication (binary sign rule): FAILED.** Development RELEASE-2026 Peromyscus had beta_delta = +15.930 m²/MNKA, whereas genuinely new, disjoint 2025–2026 provisional events returned beta_delta = −7.073. The proposed five-genus replication remains not estimable because the full fixed roster lacks sufficient future sessions. The frozen development generality threshold >=6/8 was not met (5/8).
2. **Evidence that the true old positive effect is contradicted by the new data: INSUFFICIENT.** The observed future site-cluster confidence interval is wide and contains the development effect. The old-minus-new phase difference confidence intervals also contain zero.

A failed positive sign replication is a real result, but it does not logically imply a statistically significant negative spatial response or a mechanism reversal.

## Why the new experiment is weakly discriminating

Use the exact frozen model: taxon×plot, site×calendar month and year fixed effects, equal session weight within Peromyscus. Evaluate the total residual sum of squares of genus MNKA after removing those nuisance factors. Results from immutable source event outputs:

| | RELEASE-2026 development | 2025–2026 provisional events |
|---|---:|---:|
| Taxon×plot×event sessions | 956 | 127 |
| NEON sites | 33 | 19 |
| Taxon×plot series | 111 | 32 |
| MNKA range | 5–64 | 5–56 |
| MNKA residual sum of squares | about 43,091.4 | about 2,589.7 |
| MNKA residual sum-of-squares ratio | reference | **about 6.0% of development** |
| Residual degrees of freedom | 690 | 46 |
| Fixed-effect coefficient beta_delta | +15.930 | −7.073 |
| Site-cluster CR1 standard error (effective FE rank) | about 3.33 | about 20.35 |

The marginal MNKA ranges overlap considerably. The issue is **limited *within-taxonomic-series and adjusted* abundance variation**, not lack of overlap in the range of observed counts.

With 19 site clusters, t critical df=18 gives a prospective-period 95% interval approximately **[−49.82,+35.67] m²/MNKA**, including both zero and +15.930.

A *post-outcome conditional* reference calculation, substituting the new standard error and the old selected development point estimate, gives a nominal two-sided 5% detectability around 11.5% and an approximate 80%-detectable coefficient magnitude around 59.9 m²/MNKA. This is **not a pre-experiment power calculation**; it is a quantitative illustration that the new dataset was not precise enough to reliably recover a +15.93 slope. It must not be used to retroactively enlarge alpha, change N inclusion, or exonerate the frozen sign prediction.

## Correct rank-based two-period uncertainty

The joint phase-specific model has extensive redundant dummy columns for site×month, plot and year effects. Some software's default CR1 finite-sample factor counts raw dummy columns, inflating the standard error relative to the actual rank of the fitted model. All point estimates and cohorts are unchanged; use effective **matrix rank** in the finite-sample correction. Preserve old dummy-count estimates for transparency.

| Joint old/new comparison | New minus old beta_delta | Revised site-cluster 95% interval |
|---|---:|---:|
| 956 old versus 127 new sessions | −23.00 | [−53.61,+7.61] |
| Old restricted to 19 shared sites | −24.96 | [−56.35,+6.43] |
| Old/new restricted to shared 31 taxon×plot series | −26.71 | [−61.28,+7.86] |

All intervals continue to cross zero. This **does not rescue the temporal regime-shift claim**.

## Biological implications

- A weak net population footprint change cannot be equated to no spatial organization change, but neither can a change in W/B allocation be called adaptive without an independent observation process.
- The original positive pooled result had **failed cross-genus generality**; the new Peromyscus data had **failed prospective sign replication**, and the new period is imprecise. Both failures remain in the scientific record.
- The two periods represent 2015–2024 versus 2025–2026 NEON events, not a randomized intervention or even separate animal populations: 230 marked animal histories were observed on both sides of the data-release boundary.
- Three-night trap-centroid metrics are not undisturbed home-range centres, and MNKA is retrospectively estimated, not causal animal density.
- No evidence here identifies territoriality, social repulsion, competition, environmental seasonality, resource patchiness or demographic hysteresis as the mechanism behind the apparent sign disagreement.

## Next scientifically warranted experiment

Rather than searching post-hoc environmental or lineage moderators for a favorable explanation, plan sampling capable of resolving the prespecified ~+15.9 m²/MNKA association in the relevant temporal scale, including more independent high-/low-abundance episodes across the same site×plot series and animal-position/detection calibration. The exact additional required sample size is not determined from this crude observed-SE calculation; simply increasing sessions without increasing within-series MNKA variation may have little power.

Keep the ecological manuscript **Draft/HOLD**. The defendable result is a transparent *failure to establish a transportable positive spatial response with the available new events*, not evidence of an opposing universal biological law.

Reproduction: `analysis/audit_peromyscus_holdout_information_v1.py`, `analysis/audit_future_neon_phase_slope_transportability_v1.py`. Results `results/peromyscus_provisional_transportability_receipt_v1.json` and the dedicated October 11 precision receipt.
