# Temporal aggregation and SCR detection-function closure v1

Date: 2026-10-03

## Result

Suppose an animal at distance d from a detector experiences C independent trap-check opportunities within one ecological night.

For the probability half-normal (HN),

`g(d) = g0 exp[-d^2/(2 sigma^2)]`.

If the C checks are collapsed to whether the animal was detected at least once at that detector, then

`g_C(d) = 1 - [1 - g0 exp(-d^2/(2 sigma^2))]^C`.

Except for C=1 or the rare-detection limit, `g_C(d)` is not itself a probability half-normal. Therefore a one-night-per-occasion HN fit need not preserve the check-scale sigma even when the underlying activity centre is perfectly static and there is no handling displacement.

For the hazard half-normal (HHN),

`lambda(d) = lambda0 exp[-d^2/(2 sigma^2)]`

and

`g(d)=1-exp[-lambda(d)]`.

Independent check hazards add, giving

`lambda_C(d) = C lambda0 exp[-d^2/(2 sigma^2)]`

and therefore

`g_C(d)=1-exp[-C lambda0 exp(-d^2/(2 sigma^2))]`.

Thus detector-level temporal aggregation is exactly closed under HHN: the intercept changes from lambda0 to C lambda0 while sigma is unchanged.

## Numerical shape implication for the pilot geometry

For true sigma = 12.5 m and per-check centre detection probability g(0)=0.15, least-squares approximation of the aggregated HN curve by another HN over distances 0--4 sigma gives approximately:

- 2 checks/night: sigma +2.2%;
- 3 checks/night: sigma +4.3%;
- 4 checks/night: sigma +6.4%.

The distortion increases strongly with per-check centre detection probability. With g(0)=0.30:

- 2 checks/night: sigma +4.6%;
- 3 checks/night: sigma +9.1%;
- 4 checks/night: sigma +13.4%.

These values are analytic curve-shape diagnostics, not SECR estimates. The full `multi` detector likelihood also encodes which detector supplied the retained nightly detection. The CI simulation in `scr_temporal_collapse_simulation_v1.R` tests whether the same direction survives complete capture-history generation and fitting.

## Consequence for the paper

The methodological question is sharper than "does first versus last matter?"

The general issue is:

> Is the detector model used downstream closed under the temporal aggregation imposed during capture-history construction, and if it is not, how much does the aggregation alter spatial-scale inference?

FIRST versus LAST remains relevant because one-location-per-night `multi` histories must choose a detector when multiple checks captured the same individual at different detectors. But even agreement between FIRST and LAST would not establish that nightly collapse is harmless; both can differ from the check-level representation.

## Handling boundary

This derivation assumes a static activity centre and no handling-induced change in location or detection.

Handling is therefore a separate perturbation axis, not part of the aggregation theorem. The planned phase-2 simulation will add post-capture spatial perturbation only after the no-handling benchmark is validated.

## Claim boundary

The exact closure statement is at the detector-level detection-function scale. It does not claim exact closure of a one-location-per-night multi-catch capture history, because multiple detector identities observed across checks are discarded by that reduction.
