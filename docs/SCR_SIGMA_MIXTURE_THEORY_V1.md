# Observation-state mixture and effective SCR spatial scale — theory note v1

Date: 2026-10-01

Status: analytic companion to the already locked downstream simulation. This note does not change simulation cells or decision thresholds.

## Why the downstream issue is deeper than information loss

If every within-night check samples the same stationary SCR kernel, selecting FIRST or LAST should not create a new spatial scale in expectation. It mainly discards detections and therefore information.

A different situation arises when the observation protocol changes the animal's spatial state within the nominal occasion. Live trapping makes this possibility explicit: later records occur after capture, handling and release.

Then a single nominal night can contain observations from more than one spatial kernel. Collapsing the night does not merely remove records; the representative-location rule can determine **which spatial state contributes to the fitted SCR scale parameter**.

## Continuous dense-detector benchmark

Consider a long-term activity centre at the origin.

Under a half-normal spatial kernel in the continuous dense-detector limit, write a pre-response detection location as

Z0 ~ N_2(0, sigma^2 I).

After the first capture, suppose a temporary state displacement H is added before subsequent detections.

For the locked simulation, H has fixed length h and a direction uniform on [0, 2*pi). Therefore

E[H] = 0

and

Cov(H) = (h^2 / 2) I.

A post-response location is

Z1 = H + Z0.

If H is independent of the baseline kernel,

Cov(Z1) = (sigma^2 + h^2/2) I.

Thus a single Gaussian/halfnormal scale fitted to post-response positions has the second-moment benchmark

sigma_eff ~= sqrt(sigma^2 + h^2/2).

If the displacement occurs with probability p and otherwise H = 0, the mixture covariance is

Cov(Zmix) = (sigma^2 + p h^2/2) I,

giving

sigma_eff ~= sqrt(sigma^2 + p h^2/2).

Equivalently,

sigma_eff / sigma ~= sqrt(1 + (p/2) (h/sigma)^2).

This makes h/sigma the natural dimensionless control parameter.

## Ten-percent benchmark

For a 10% scale inflation,

sqrt(1 + (p/2) (h/sigma)^2) >= 1.10.

Therefore

h/sigma >= sqrt( 2(1.10^2 - 1) / p ).

At the locked stress-test response probability p = 0.70,

h/sigma >= 0.775 approximately.

This is an analytic benchmark, not a claim that the fitted discrete-trap SCR estimator must cross 10% at exactly that value.

## Random-length empirical transition kernel

The exact-protocol consequence benchmark uses the already-opened San Jacinto
first-to-last displacement-vector distribution rather than a fixed shift
length. Let a transition occur with overall probability q and let R be its
random length. If transition direction is approximately isotropic and has
mean zero, then

Cov(H) = E[R^2] / 2 * I

conditional on a transition, and the mixture benchmark becomes

sigma_eff / sigma ~= sqrt(1 + q E[R^2] / (2 sigma^2)).

For the pooled held-out San Jacinto calibration,

q = P(repeat capture | captured night) *
    P(material position change | repeat-capture night)
  = (592 / 1520) * (426 / 592)
  = 426 / 1520
  ~= 0.2803.

Thus the empirically anchored benchmark is governed by

sqrt(q E[R^2]) / sigma,

the RMS observation-state displacement scaled by the baseline SCR spatial
scale. The exact simulation reports E[R^2] from the frozen empirical vector
kernel and compares the corresponding continuous-limit prediction with fitted
discrete-grid SCR estimates.

This is the more general criterion: a large raw positional span need not imply
a large sigma consequence if the baseline sigma is much larger; the same
observation-process displacement can be consequential when sigma is small.

## Expected ordering of representations

Under the locked simulation mechanism:

- FIRST is selected before the state shift is applied, so its continuous-limit target remains approximately the baseline sigma.
- LAST preferentially samples the post-response state on repeat-capture nights, so its target can move toward sigma_eff.
- CHECK retains both pre- and post-response records and therefore estimates a mixture scale intermediate between the baseline and post-response targets, with the exact weight determined by the number and timing of subsequent detections.

This implies that CHECK is not automatically a biological gold standard once the observation process changes state. It is the data-preserving representation, but its sigma can estimate a mixed spatial process.

## What the full simulation adds

The closed-form benchmark ignores several features that can matter in the real analysis:

- a finite 7 x 7 detector grid;
- 6.25 m detector spacing;
- edge effects and a finite activity-centre mask;
- multi-catch detection probability rather than direct sampling from a continuous Gaussian location density;
- conditioning on capture and recapture;
- the fact that the state shift is triggered only after an actual capture;
- nightly collapse to FIRST or LAST;
- finite-sample SCR maximum-likelihood estimation.

The locked secr simulation therefore tests whether the second-moment prediction survives these realistic observation-process features.

## Interpretive consequence

The downstream contribution should not be phrased as a universal claim that temporal aggregation biases SCR sigma.

The sharper claim, if supported by the full simulation, is:

> Coarse occasions can mix distinct observation-conditioned spatial states. When within-occasion state displacement is non-negligible relative to the baseline SCR scale, the representative-location rule changes the spatial scale being estimated; under a stationary kernel, that effect should largely disappear.

This converts the diagnostic from a generic warning about discarded locations into a testable criterion for **estimand stability across temporal aggregation rules**.
