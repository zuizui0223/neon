# San Jacinto positional temporal-aliasing validation — effect lock v1

Date: 2026-09-29

Status: frozen before any held-out first-to-last nightly displacement or changed/not-changed outcome is calculated.

## Why these two species

A broader, effect-blind Cricetidae support scan was frozen first and then stopped because only one species met the movement-support portion of that earlier programme.

That scan nevertheless established, without opening first-vs-last outcomes, that two species have strong positional-repeat support:

- PEMA — Peromyscus maniculatus: 485 repeat-capture individual-nights across 8 grids and 12 bouts.
- PEER — Peromyscus eremicus: 107 repeat-capture individual-nights across 3 grids and 10 bouts.

REME had no repeat-capture support and is excluded.

PEMA and PEER are selected **only from effect-blind support counts**. Neither species' first-vs-last distance or changed/not-changed outcome has been inspected.

## Source and geometry

Figshare article 18295520 v1, `year round trap data.csv`, SHA256 `ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301`.

Trap flags form a fixed 7 x 7 A1-G7 grid with 6.25 m spacing.

## Frozen preprocessing

Use only valid rows for PEMA and PEER with:
- non-empty unique_ID;
- canonical A1-G7 flag;
- valid capture date;
- valid nocturnal time under the frozen 12-hour-night ordering rule.

A repeat-capture individual-night is `grid × species × unique_ID × date` with >=2 valid capture rows.

For each such individual-night:
- first location = canonical flag from the earliest nocturnal capture;
- last location = canonical flag from the latest nocturnal capture;
- ties are broken by original source row order.

## Primary positional-aliasing outcome

`d_first_last` = Euclidean distance in meters between first and last nightly trap flags.

`one_spacing_shift` = 1 if `d_first_last >= 6.25 m`, otherwise 0.

6.25 m is fixed before outcomes because it is exactly one adjacent-trap spacing and therefore has direct protocol meaning.

## Species-level confirmatory rule

For each species separately:

- estimate `p_shift`, the proportion of repeat-capture individual-nights with `one_spacing_shift = 1`;
- calculate a two-sided 95% Wilson interval for the binomial proportion;
- species passes if the **lower 95% Wilson bound exceeds 0.25**.

The 0.25 threshold is an operational materiality criterion: at least one quarter of repeatedly observed individual-nights shifting by one full trap spacing is treated as non-negligible positional aliasing.

## Spatial replication rule

For each species, among grids with >=20 repeat-capture individual-nights:
- compute the raw one-spacing-shift fraction;
- require at least 2 such grids to have shift fraction > 0.25.

## Programme decision

`authorize_live_trap_positional_aliasing_result` only if **both PEMA and PEER** pass:
- the species-level Wilson lower-bound rule; and
- the spatial replication rule.

Otherwise:
`stop_positional_aliasing_not_replicated`.

## Secondary descriptive quantities

Reported but non-rescuing:
- median, 75th, 90th percentile, and maximum `d_first_last`;
- fraction with any flag change;
- first-to-last elapsed time distribution;
- grid-specific shift fractions;
- trapping-bout-specific shift fractions;
- discovery-cohort comparison to the previously inspected heteromyids, clearly labeled exploratory.

## Claim boundary

If authorized, the strongest allowed claim is:

> In two independently held-out Cricetidae species sampled with repeated nightly trap checks, collapsing repeated within-night captures to one nightly position would discard a materially frequent one-trap-spacing-or-greater positional change.

Not allowed:
- movement-rate or home-range claims;
- sex-specific claims;
- universal small-mammal claims;
- causal claims about why animals changed trap locations.

At this lock:
- held-out first-last distances inspected: false
- held-out changed/not-changed outcomes inspected: false
- held-out grid-level shift fractions inspected: false
- ecological/model fits: 0
