# San Jacinto held-out cross-scale effect-analysis lock v1

Date: 2026-09-29

Status: frozen after effect-blind estimability passed, before any sex-specific packing score or movement distance is calculated.

## Frozen eligible species and matched grids

- CHFA — Chaetodipus fallax: grids 2, 6
- DKR — Dipodomys simulans: grids 1, 2
- LAPM — Perognathus longimembris brevinasus: grids 3, 5, 6
- SKR — Dipodomys stephensi: grids 3, 4, 5

Primary analyses use only these matched grids for both endpoints.

## Shared nightly state

Use the frozen preprocessing from estimability v1: resolved sex within identity-bout and the earliest parsed nocturnal capture location per individual per source date.

All distances use the canonical 7 x 7 grid geometry with 6.25 m spacing.

## Packing outcome

For each primary species × grid × date session, compute mean pairwise Euclidean distance separately for male and female nightly states.

Because traps were checked and reset multiple times per night, different individuals may legitimately have the same nightly flag. The null therefore samples individual flag locations IID with replacement from the 49 fixed flags.

For N individuals and distance kernel h:

`mu = E[h(X1,X2)]` under two independent uniform draws from the 49 flags.

`Var(U_N) = [C(N,2) Var(h) + 6 C(N,3) Cov(h12,h13)] / C(N,2)^2`

with exact finite-grid moments calculated from the 49 x 49 distance matrix. This null mean is independent of N.

`Packing_z = (observed_MPD - mu) / sd_N`

`Delta_packing = Packing_z_male - Packing_z_female`

Positive Delta_packing means males are more spatially dispersed than females after conditioning on each sex's captured N and the common grid geometry.

## Movement outcome

Within each primary species × grid × bout event:

1. sort each movement-eligible individual's nightly states by date;
2. for each successive observed date pair compute Euclidean displacement divided by elapsed calendar days;
3. transform each daily rate as `log1p(meters_per_day)`;
4. individual movement = median of those transformed successive rates;
5. event male movement = arithmetic mean of eligible male individual values;
6. event female movement = arithmetic mean of eligible female individual values;
7. `Delta_movement = male_mean - female_mean`.

Zero displacement is retained.

## Hierarchical weighting

For each species and matched grid:
- packing grid effect = arithmetic mean Delta_packing across primary nights;
- movement grid effect = arithmetic mean Delta_movement across primary bouts.

For each species:
- species effect = equal-weight mean of matched-grid effects;
- species SE = sample SD of matched-grid effects / sqrt(number of matched grids).

For each endpoint family mean:
- every species receives equal weight;
- within-species grid uncertainty is propagated;
- between-species variance uses method of moments:
  `tau2 = max(sample_variance(species_effects) - mean(species_SE^2), 0)`;
- `Var(family_mean) = tau2/S + sum(species_SE^2)/S^2`;
- confidence intervals use Student-t with df = S-1.

This explicitly prevents the prior error where similar species point estimates produced an artificially narrow family interval despite uncertain species estimates.

## Confirmatory directional gates

Movement-positive gate passes only if:
- family Delta_movement > 0;
- lower bound of the two-sided 95% family CI > 0;
- at least 3 of 4 species movement effects > 0.

Packing-positive gate uses the same three conditions for Delta_packing.

## Packing equivalence gate

A small packing difference is prospectively defined as `|Delta_packing| < 0.5` standardized null SD.

Packing equivalence to zero passes only if:
- the two-sided 90% family CI lies entirely within [-0.5, +0.5];
- at least 3 of 4 species point effects lie within [-0.5, +0.5].

## Frozen cross-scale decision

1. If movement-positive passes AND packing-positive passes:
   `authorize_crossscale_propagation_manuscript`.

2. Else if movement-positive passes AND packing-positive fails AND packing-equivalence passes:
   `authorize_crossscale_decoupling_manuscript`.

3. Otherwise:
   `stop_no_confirmatory_crossscale_result`.

Packing or movement results from N>=2/sex sessions/events cannot reverse this primary decision.

## Secondary diagnostics

Reported but non-rescuing:
- N>=2/sex version of both endpoints using the same rules;
- last nightly capture instead of first nightly capture;
- leave-one-species-out family estimates;
- leave-one-matched-grid-out species estimates;
- descriptive Spearman association between matched-grid packing and movement effects.

## Claim boundaries

Allowed propagation claim, if authorized:
`male-biased individual movement is accompanied by male-biased nightly population spatial packing across held-out heteromyid taxa.`

Allowed decoupling claim, if authorized:
`male-biased individual movement is detectable while nightly population spatial packing remains equivalent to a small sex difference under an abundance- and geometry-conditioned null.`

Not allowed:
- natal or breeding dispersal;
- home-range size;
- reproductive causation;
- universal Heteromyidae claim beyond the four held-out taxa.

At this lock:
- packing effects computed: false
- movement distances computed: false
- ecological effect models fit: 0
