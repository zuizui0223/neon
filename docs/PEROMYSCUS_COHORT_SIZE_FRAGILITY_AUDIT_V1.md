# Post-result cohort-size sensitivity: Peromyscus local geometry

**Date:** 2026-10-10. **Status: IMPORTANT FRAGILITY — ECOLOGICAL INTERPRETATION HOLD.**

This is a transparent post-result audit of the original NEON RELEASE-2026 development sample, not independent evidence. It is deliberately not a revision of any original preregistered hypothesis or the original failed 6/8 genus guard.

## Why this is important

The number of repeatedly captured animals `m` is positively correlated with MNKA. The raw mean squared nearest-neighbor distance mechanically changes when m animals are placed in the same finite lattice. Even the previous two m-conditioned geometric reference distributions need not ensure *regression residuals* independent of m.

The relationship `m ~ MNKA` in the frozen development model was previously +0.3266 repeat-supported individuals per one MNKA for Peromyscus. Therefore a fitted `NN2 ~ MNKA` relationship could be driven by selection of more animals into the coordinate-bearing cohort.

## Reproduction from the immutable source

Read the exact 1,326-session artifact from GitHub Actions run 37793401501; use 956 Peromyscus sessions from 33 sites, 111 series. No new NEON data are read. The prior fixed-effect slopes are reproduced to floating-point precision before this sensitivity is interpreted.

All fits use exactly the prior taxon×plot (series), site×month and year fixed effects, equal weights, a site-cluster uncertainty estimator. *After the original result was observed*, add (i) cohort size `m`, (ii) `m` plus overall centroid footprint `B_observed`; do not swap the estimand or report these as prospectively frozen confirmatory tests.

### Preliminary local reproduction — verified with a separate statsmodels OLS design

| Response / MNKA slope | Original FE | +m FE | +m+B_observed FE |
|---|---:|---:|---:|
| raw NN squared distance | -12.929 | +3.362 | +2.325 |
| NN excess vs x/y shuffle | +2.557 | +1.591 | +1.741 |
| NN excess vs other-event series pool | +4.172 | +4.306 | +3.126 |

With `m` included, site-cluster normal-approx 95% confidence intervals for the MNKA coefficient include zero for *both* excess responses. For instance, local independent statsmodels reproduction yielded 95% intervals of approximately [-1.63,+4.81] for the x/y excess and [-1.13,+9.74] for the series-reference excess. These are conditional descriptive sensitivity intervals; the same dataset selected the Peromyscus candidate.

The original negative raw NN slope is **reversed** in the +m fit. The data consequently do **not** currently identify a robust density-specific local-spacing effect apart from the number of sampled repeat-supported individuals.

## Inference boundary

`m` is a capture-selected post-exposure quantity and may reflect a biological component of crowding *as well as* trap detection. Conditioning on m is therefore not a causal correction or proof that the original relationship was an artefact. Equally, retaining the original unadjusted positive excess slopes cannot establish density-dependent spatial regularization.

**Stop statements:**
- Do not claim territorial spacing, spatial repulsion, resource partitioning or anti-crowding adaptation from these capture records.
- Do not claim the dual-null sign result independently eliminates m-dependence.
- Do not promote a single Peromyscus genus effect as a cross-mammal principle.
- Do not convert the prior 5/8 original generality failure into success.
- Do not select PELE alone to rescue the weakened genus result.

**What survives:** a descriptive association between genus MNKA, cohort sampling intensity and multiple capture-centroid geometry measures, with a plausible biological alternative worth independent study, but without evidence distinguishing animal behavior from observation selection.

## Future check (separate addendum; original future contract not overwritten)

Preserve the 2026-10-08 future Peromyscus geometry contract as a historical preregistration record. Add an explicitly dated *before-future-data but after-discovery* requirement: also report `m`-controlled slopes, prospective within-site sampling controls and the detection process. A future result that only passes the original unadjusted criteria but not a prespecified m-sensitive robustness requirement should be reported as an observational geometry finding rather than a robust ecological density effect.
