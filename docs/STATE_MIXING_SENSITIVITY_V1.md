# State-mixing sensitivity for a spatial scale parameter

Status: methodological derivation for the live-trap aliasing manuscript.

## Observation-process quantity

For valid ecological occasions (t=1,ldots,N), let (Delta_t) be the observed first-to-last displacement vector when an occasion is repeat-observed. Singly observed occasions do not reveal a first-to-last displacement.

Define the directly observed transition-energy scale

[
s_{mathrm{mix,obs}}
=
sqrt{
rac{1}{2N}
sum_{tin R}
|Delta_t|^2
}.
]

The denominator is all valid occasions, not only repeat-observed occasions. Thus the quantity measures the directly exposed contribution of within-occasion state change on the scale of one spatial axis.

It does **not** set unobserved transitions on singly observed occasions biologically to zero. Their contribution is simply not directly exposed by the protocol.

## Dimensionless diagnostic

For an externally chosen reference half-normal spatial scale (sigma_{mathrm{ref}}>0),

[
A_sigma
=
rac{s_{mathrm{mix,obs}}}{sigma_{mathrm{ref}}}.
]

This makes the diagnostic portable across trap spacing and animal movement scale.

## Second-moment benchmark

Suppose a baseline spatial state has isotropic covariance (sigma^2 I), and an additional approximately zero-mean isotropic transition contributes per-axis variance (v_H).

Then the mixed spatial second moment has scale

[
sigma_{mathrm{eff}}^2
approx
sigma^2 + v_H.
]

Writing (A_sigma=sqrt{v_H}/sigma),

[
rac{sigma_{mathrm{eff}}}{sigma}
approx
sqrt{1+A_sigma^2}.
]

Therefore the benchmark relative change is

[
sqrt{1+A_sigma^2}-1.
]

A 10% scale change corresponds to

[
A_sigma
=
sqrt{1.1^2-1}
approx 0.458.
]

This is a sensitivity relation, not an estimator correction.

## Random-transition form

If an extra transition (H) occurs with probability (q), has negligible mean relative to its RMS size, and is approximately isotropic, then

[
v_H
approx
rac{q,E|H|^2}{2},
]

so

[
rac{sigma_{mathrm{eff}}}{sigma}
approx
sqrt{
1+
rac{q,E|H|^2}{2sigma^2}
}.
]

For non-negligible transition mean or strong anisotropy, the full transition covariance should be retained instead of interpreting the scalar relation as exact.

## Interpretation

The diagnostic asks whether the directly observed within-occasion state-change energy is small or large relative to a planned or plausible spatial scale parameter.

It does not determine:
- which observed state is biologically correct;
- the latent transition distribution on singly observed occasions;
- whether capture/handling caused the state change;
- the exact bias of a finite-detector SCR estimator.

Those questions require an explicit observation model or simulation. The SCR consequence benchmark in this project is therefore used to test when the second-moment sensitivity signal translates into finite-grid estimator instability.
