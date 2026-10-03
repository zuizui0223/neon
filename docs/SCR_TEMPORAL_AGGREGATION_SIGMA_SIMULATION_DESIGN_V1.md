# SCR temporal aggregation: closure theorem and downstream sigma simulation v1

Date: 2026-10-03

Status: frozen before simulation outcomes are inspected.

## Why this replaces the weak benchmark

The existing v0.3 simulation checks binomial-proportion properties of the positional-aliasing diagnostic. Those properties are useful QC but do not answer the paper's missing question: when does collapsing repeated within-night observations alter a downstream SCR spatial-scale estimate?

This programme targets that question directly.

The empirical SCR comparison remains stopped exactly as recorded:
- PEMA passed the pre-specified session-support gate;
- PEER did not;
- no first/last empirical sigma estimate was opened.

The present programme does not reopen that gate. It uses a generative SCR experiment.

## Key theoretical prediction: closure under temporal aggregation

Let one within-night check have radial distance d from an activity centre and half-normal kernel

h(d; sigma) = exp[-d^2/(2 sigma^2)].

### Probability half-normal (HN)

For one check,

p(d) = g0 h(d; sigma).

For K conditionally independent checks collapsed to a binary "detected at least once" night,

p_K(d) = 1 - [1 - g0 h(d; sigma)]^K.

For K > 1 and 0 < g0 < 1 this is not, in general, another HN curve. Therefore temporal aggregation changes not only the intercept but also the shape. A static HN model fitted to the collapsed data can absorb this shape change into sigma.

Because f(p)=1-(1-p)^K is concave with f(0)=0,

f(alpha p0) / f(p0) >= alpha

for 0 <= alpha <= 1. Thus the aggregated HN curve falls more slowly with distance than the one-check HN curve. The directional prediction, before any simulation is opened, is upward pressure on fitted sigma as K and/or g0 increase.

### Hazard half-normal (HHN)

For one check,

lambda(d) = lambda0 h(d; sigma),
p(d) = 1 - exp[-lambda(d)].

For K conditionally independent checks,

p_K(d)
= 1 - exp[-K lambda0 h(d; sigma)].

This is exactly HHN with

lambda0_K = K lambda0
sigma_K = sigma.

Thus HHN is closed under aggregation of repeated independent exposure, whereas probability HN is not.

This is a model-class statement, not a claim that HHN automatically solves post-capture behavioural displacement.

## Primary simulation question

How much does estimated sigma change when repeated checks are represented as:

1. CHECK — each check retained as its own SCR occasion;
2. FIRST — checks collapsed to one nightly occasion, retaining the first detection;
3. LAST — checks collapsed to one nightly occasion, retaining the last detection?

The target is bias relative to the generating sigma, not merely FIRST-vs-LAST disagreement.

## Simulation engine

R package: secr >= 5.4.

Detector array:
- 7 x 7 multi-catch detector grid;
- spacing = 6.25 m;
- 100 m habitat-mask buffer.

Base sampling schedule:
- 5 nights;
- K = 4 checks per night for the end-to-end SCR experiment;
- 20 check-level occasions.

Generating sigma:
- 12.5 m (two trap spacings).

One-check centre detection probability is matched across HN and HHN:
- HN g0 = 0.15;
- HHN lambda0 = -log(1 - 0.15).

Theoretical closure curves additionally vary K in {1,2,4,8} and one-check centre detection in {0.05,0.15,0.30,0.50}.

## Post-capture displacement perturbation

The simulation separates temporal aggregation from handling-associated positional change.

After a first detection has occurred within an individual-night, later recorded detector locations can be spatially perturbed while detection occurrence itself is held fixed.

Primary perturbation levels:
- NONE: move probability = 0;
- SAN_JACINTO: move probability = 0.70, radial displacement median = 13.0 m.

The calibrated level is intentionally approximate and anchored to the already-open empirical result:
- about 69-73% of repeat-capture nights changed trap position;
- changed-night first-to-last displacement was approximately 12.5-14 m.

The perturbation is an observation-process sensitivity device. It is not asserted to reconstruct undisturbed animal movement or a mechanistic post-release trajectory.

## Frozen estimands

For each fitted dataset:

sigma_relative_error = (sigma_hat - sigma_true) / sigma_true.

For each scenario and representation, report:
- median sigma_hat;
- median sigma_relative_error;
- mean sigma_relative_error;
- RMSE on sigma;
- 10th and 90th percentiles of sigma_hat;
- fit-success fraction.

Primary contrasts:
- HN vs HHN under NONE perturbation;
- CHECK vs FIRST vs LAST;
- change in these contrasts under SAN_JACINTO perturbation.

## Frozen predictions

P1. With K=1 and no perturbation, all representations are equivalent up to Monte Carlo and optimizer variation.

P2. With K>1 and no perturbation, HN nightly aggregation will tend to inflate sigma relative to CHECK because the probability-HN family is not closed under repeated-check aggregation.

P3. With K>1 and no perturbation, HHN will show substantially less aggregation-induced sigma bias than HN because cumulative hazard is additive and the HHN family is closed under repeated independent exposure.

P4. Under SAN_JACINTO perturbation, LAST and CHECK may move away from FIRST because post-first recorded locations have been altered. This contrast is descriptive sensitivity to handling-associated positional change, not evidence of natural movement.

P5. If FIRST is relatively stable while LAST/CHECK shift under perturbation, the paper should not claim that "finer occasions solve the problem". Instead it should state that retaining finer observations preserves information but can also expose a second process that a static SCR model may absorb into sigma.

## Decision rule for manuscript use

Replace the current Figure 2 proportion benchmark only if the end-to-end simulation satisfies both:
- fit-success >= 0.80 in every primary representation/scenario cell; and
- the predicted HN-vs-HHN aggregation contrast is directionally reproduced.

No minimum effect size is required for inclusion.

If the contrast is weak, null, or unstable, report that result and retain the closure theorem as a model-diagnostic boundary rather than manufacturing a stronger empirical claim.

## Claim boundary

Supported by this programme:
- temporal aggregation can interact with SCR detection-function parameterisation;
- hazard-based and probability-based half-normal detection functions differ in whether repeated independent exposure is closed under aggregation;
- post-capture positional changes can create additional sigma sensitivity that is distinct from aggregation alone.

Not supported:
- FIRST or LAST is biologically correct;
- all live-trapping SCR studies are biased;
- observed first-to-last displacements are undisturbed movement;
- check-level occasions automatically remove handling effects;
- the San Jacinto empirical sigma effect for PEER, which remains unopened.
