# Temporal aggregation bounds for repeated-location trapping data

Version: v1
Date: 2026-09-29

## Setup

For one individual on night t, let:
- F_t = a representative location chosen as the first observed position;
- L_t = a representative location chosen as the last observed position;
- delta_t = d(F_t, L_t), the within-night positional span.

The metric d may be ordinary Euclidean distance or any metric satisfying the triangle inequality.

## Theorem 1 — movement representative-location sensitivity

For two nights t and u:

`| d(F_t,F_u) - d(L_t,L_u) | <= delta_t + delta_u`.

### Proof

By the triangle inequality:

`d(F_t,F_u) <= d(F_t,L_t) + d(L_t,L_u) + d(L_u,F_u)`

so

`d(F_t,F_u) - d(L_t,L_u) <= delta_t + delta_u`.

Swap F and L to obtain the reverse inequality. Taking the absolute value gives the result.

### Interpretation

The sum of within-night first-to-last positional spans is a deterministic upper bound on how much an inter-night movement estimate can change solely because a different within-night representative position was chosen.

## Theorem 2 — population mean-pairwise-distance sensitivity

For n individuals observed under paired first and last nightly representations, define:

`MPD(F) = 2/[n(n-1)] * sum_{i<j} d(F_i,F_j)`

and similarly MPD(L). Let delta_i = d(F_i,L_i). Then:

`|MPD(F) - MPD(L)| <= 2 * mean(delta_i)`.

### Proof

For each pair i<j:

`|d(F_i,F_j)-d(L_i,L_j)| <= delta_i + delta_j`.

Summing over all unordered pairs, each delta_i appears exactly n-1 times. Multiplying by 2/[n(n-1)] yields:

`2/n * sum_i delta_i = 2 * mean(delta_i)`.

## Corollary — standardized packing sensitivity

If a packing score uses the same n individuals and fixed null moments:

`z = (MPD - mu_n) / sigma_n`,

then first versus last representations satisfy:

`|z_F - z_L| <= 2 * mean(delta_i) / sigma_n`.

The null mean cancels exactly.

## Sharpness

The movement bound is sharp. On a one-dimensional line, choose F_t=0, F_u=10, L_t=1, L_u=9. Then the movement difference is 2 and delta_t+delta_u=2.

The MPD bound is also sharp for n=2, where MPD is just the pairwise distance.

## Ecological implication

These are not stochastic assumptions and do not require a movement model. They are observation-process bounds.

They separate two questions:

1. how much an animal actually shifts among repeated within-night observations;
2. how much that unresolved shift can alter an ecological statistic after the data are collapsed to one nightly location.

This provides a protocol diagnostic before interpreting movement or spatial-configuration differences.

## Claim boundary

The inequalities do not imply that first or last capture is biologically superior, that all repeated-check live trapping is biased, or that the upper bound is usually attained. Their value is to provide a scale-aware maximum sensitivity implied by the observed within-night positional uncertainty.
