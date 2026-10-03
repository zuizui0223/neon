# SCR sigma consequence benchmark — numerical validity correction v1

Date: 2026-10-03

Status: implementation-validity correction after inspecting the Monte Carlo output. Biological generator, empirical calibration, seeds, parameter cells, models, and the pre-specified 10% descriptive threshold are unchanged.

## Problem found

The original result classified a fit as successful when sigma and its confidence limits were finite.

That criterion was too weak.

Across 1,080 fitted models, exactly two rows had:
- very large sigma estimates (333,424 m and 438,134 m);
- reported sigma SE exactly 0;
- correspondingly implausible confidence intervals only about 0.01 m wide.

Both occurred in the empirical-transition PRE / true sigma = 25 m / FIRST cell.

These two rows dominated the arithmetic mean for that cell while leaving the median essentially unchanged. They are numerical/Hessian failures, not interpretable ecological effects.

## Repair

A fitted model is now counted as successful only when:
- sigma is finite and > 0;
- sigma SE is finite and > 0;
- the lower and upper confidence limits are finite and ordered.

The optimizer convergence code is also written to the replicate file for audit, but it is not by itself used to delete a fit because secr documents that some nlm warning codes can still represent usable maxima.

The frozen simulation is rerun with the same:
- source checksum;
- random seeds;
- 40 replicates per cell;
- trap geometry;
- density repair;
- g0;
- sigma grid;
- empirical transition kernel;
- POST/PRE mirror mechanisms;
- analysis models.

## Why this is not result-driven exclusion

The correction does not impose a sigma magnitude cutoff or remove estimates because they are extreme.

The rejected rows fail an estimator-validity requirement independent of effect direction or magnitude: a fitted positive continuous parameter cannot be treated as a reliable finite-uncertainty estimate when the reported Hessian-based SE is exactly zero at a near-unbounded solution.

Current secr documentation similarly cautions that failures of the information matrix indicate major model-fitting problems and that affected parameter estimates should not be trusted.

## Interim corrected values from the existing replicate file

Applying only the positive-SE/ordered-CI rule to the existing saved replicate rows gives, for the affected PRE / sigma = 25 m / FIRST cell:
- valid fits: 38 / 40;
- median sigma: 27.73 m;
- mean sigma: 28.76 m;
- median relative bias: +10.9%;
- mean relative bias: +15.0%.

Thus the scientific pattern is not created by the two pathological fits.

For the empirically central sigma = 12.5 m cells, no rows fail this numerical rule, so the previously reported median results are unchanged.

## Claim boundary

This correction repairs numerical classification only. It does not resolve the separate modelling question of whether CHECK, FIRST or LAST is biologically preferable under a state-changing observation process.
