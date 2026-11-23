# Simulation benchmark correction — v2

Date: 2026-09-30

## Why v1 is superseded

The v1 benchmark evaluated Wilson coverage against the realized latent
all-occasion fraction within each finite simulated dataset. That quantity is
itself a random empirical proportion. Wilson intervals for the
repeat-observed subset are instead naturally evaluated against the generating
material-shift probability.

The v1 Wilson implementation also relied on floating-point cancellation at
the binomial boundaries. For k=0, the nominal lower bound can become a tiny
positive number rather than exact zero; for k=n, the upper bound can be a tiny
amount below one. This especially distorted rare-event coverage cells.

## v2 target definitions

For dx,dy iid Normal(0,sigma^2), the span is Rayleigh(sigma), so the
generating material-shift probability at scale s is known analytically:

P(span >= s) = exp[-s^2/(2 sigma^2)].

v2 therefore evaluates:
- conditional estimator bias against this analytic generating probability;
- Wilson coverage against this analytic generating probability;
- the directly observed all-occasion fraction as a deterministic lower bound
  on the finite realized all-occasion material-shift fraction.

The last property remains a set-inclusion statement within each simulated
dataset and is not reinterpreted as a confidence bound on the generating
probability.

## Empirical effect

This correction does not alter:
- the prospectively frozen PEMA/PEER held-out result;
- denominator audit values;
- deterministic geometry bounds;
- downstream MCP non-estimability.

Only the simulation performance characterization and corresponding manuscript
language are superseded.
