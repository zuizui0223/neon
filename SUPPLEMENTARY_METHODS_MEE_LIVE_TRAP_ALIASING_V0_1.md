# Supplementary Methods — temporal positional aliasing v0.1

Date: 2026-09-30

## S1. Deterministic sensitivity bounds

### S1.1 Inter-occasion movement

Let (F_t) and (L_t) be two valid within-occasion positions for an individual in occasion (t), and define (delta_t=d(F_t,L_t)). For occasions (t) and (u),

[
d(F_t,F_u)
le d(F_t,L_t)+d(L_t,L_u)+d(L_u,F_u)
=delta_t+d(L_t,L_u)+delta_u.
]

Therefore

[
d(F_t,F_u)-d(L_t,L_u)ledelta_t+delta_u.
]

Exchanging FIRST and LAST gives the reverse inequality, so

[
|d(F_t,F_u)-d(L_t,L_u)|ledelta_t+delta_u.
]

The bound is sharp in a metric space. On a line, choose (F_t=0), (L_t=1), (L_u=9), (F_u=10). The FIRST-based distance is 10, the LAST-based distance is 8, and (delta_t+delta_u=2).

### S1.2 Population mean pairwise distance

For (n) individuals represented by paired FIRST and LAST positions,

[
MPD(F)=rac{2}{n(n-1)}sum_{i<j}d(F_i,F_j)
]

and (MPD(L)) analogously. For every pair,

[
|d(F_i,F_j)-d(L_i,L_j)|le delta_i+delta_j.
]

Summing over unordered pairs, each (delta_i) appears (n-1) times. Hence

[
|MPD(F)-MPD(L)|
le
rac{2}{n(n-1)}(n-1)sum_idelta_i
=
2overline{delta}.
]

For a standardized MPD score (z=(MPD-mu_n)/sigma_n), when FIRST and LAST use the same (n) and the same null moments,

[
|z_F-z_L|
=
rac{|MPD(F)-MPD(L)|}{sigma_n}
le
rac{2overline{delta}}{sigma_n}.
]

The implementation is verified by equality cases and random Euclidean tests.

## S2. Generic diagnostic algorithm

Input observations require:
- individual identifier;
- ecological occasion identifier;
- sortable within-occasion time;
- spatial coordinates;
- a material spatial scale (s>0).

For each individual-occasion:
1. discard rows lacking required structural fields;
2. order valid rows by time with source-row order as deterministic tie-breaker;
3. if only one valid observation remains, retain the occasion in the all-occasion denominator but mark the within-occasion span as unresolved;
4. if at least two observations remain, retain first and last locations and calculate (delta=d(F,L));
5. classify a material shift when (deltage s).

Across repeat-observed occasions, calculate:
- material-shift count and fraction;
- two-sided 95% Wilson interval;
- median, 75th and 90th percentile, and maximum span;
- span divided by (s).

Across all valid occasions, calculate the fraction with a **directly observed** material shift. This is a lower bound because unresolved single-observation occasions cannot contribute to the numerator.

## S3. Simulation benchmark

### S3.1 Parameter grid

The benchmark crosses:
- (N in {100,500});
- displacement component SD / material scale (in {0.25,0.5,1,2});
- baseline repeat-observation probability (qin{0.25,0.5,0.75});
- repeat-observation dependence (etain{-1,0,+1}).

This yields 72 parameter cells. Each cell uses 400 replicates.

### S3.2 Latent span

For each occasion, independent Gaussian (x) and (y) displacement components generate a latent Euclidean span (delta). The material scale is one simulation unit, so the latent material-shift indicator is (I(deltage1)).

### S3.3 Repeat-observation mechanism

For normalized span (r=delta/s),

[
p_{mathrm{repeat}}
=
operatorname{logit}^{-1}
left[
operatorname{logit}(q)+eta(r-1)
ight].
]

Thus:
- (eta=0): non-informative repeat observation;
- (eta>0): span-enriched repeat observation;
- (eta<0): span-depleted repeat observation.

### S3.4 Frozen benchmark diagnostics

For each replicate:
- latent all-occasion material-shift fraction;
- repeat-conditioned material-shift fraction;
- conditional bias;
- Wilson 95% interval and latent-fraction coverage;
- directly observed material shifts / all occasions;
- lower-bound violation indicator.

Frozen benchmark summary:
- non-informative mean absolute bias: 0.000626;
- non-informative mean Wilson coverage: 0.9529;
- span-enriched mean bias: +0.05080;
- span-depleted mean bias: -0.07993;
- lower-bound violations: 0.

## S4. Empirical source and prospective holdout

### S4.1 Source

The empirical source is the public Figshare dataset associated with Chock, Shier & Grether (2022), DOI 10.6084/m9.figshare.18295520.v1.

The capture file checksum frozen for the analysis is:

`ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301`.

The trapping design uses fixed 7×7 grids with 6.25-m spacing.

### S4.2 Discovery versus confirmatory taxa

A separate exploratory heteromyid analysis motivated the positional-aliasing question but does not contribute to the confirmatory result.

The confirmatory taxa were selected from an effect-blind support scan:
- PEMA — *Peromyscus maniculatus*;
- PEER — *P. eremicus*.

Before first-to-last outcomes were inspected, the frozen support counts were:
- PEMA: 485 repeat-capture individual-nights across 8 grids and 12 bouts;
- PEER: 107 repeat-capture individual-nights across 3 grids and 10 bouts.

### S4.3 Frozen materiality rule

The material scale was one adjacent-trap spacing, 6.25 m.

A species passed only when:
1. material-shift fraction (>0.25);
2. lower 95% Wilson bound (>0.25);
3. at least two grids with at least 20 repeat-capture nights each independently had shift fraction (>0.25).

Both species were required to pass.

## S5. Held-out confirmatory result

PEMA:
- 485 repeat-capture nights;
- 352 one-spacing-or-greater shifts;
- fraction 0.7258;
- 95% Wilson interval 0.6844–0.7636;
- median span 8.84 m;
- 90th percentile 25.0 m;
- 7/7 eligible grids passed.

PEER:
- 107 repeat-capture nights;
- 74 one-spacing-or-greater shifts;
- fraction 0.6916;
- 95% Wilson interval 0.5987–0.7712;
- median span 6.25 m;
- 90th percentile 19.76 m;
- 3/3 eligible grids passed.

Frozen decision:

`authorize_live_trap_positional_aliasing_result`.

## S6. All-occasion denominator audit

PEMA:
- 1,219 all valid individual-nights;
- 485 repeat-observed nights (39.8%);
- 352 directly observed material-shift nights;
- all-night directly observed lower bound: 28.9%.

PEER:
- 301 valid individual-nights;
- 107 repeat-observed nights (35.5%);
- 74 directly observed material-shift nights;
- all-night directly observed lower bound: 24.6%.

These lower bounds make no claim about unresolved single-capture nights.

## S7. Prospectively gated downstream MCP test

A downstream minimum convex polygon analysis was specified before MCP effects were inspected.

Individual eligibility required:
- at least 10 capture nights;
- at least 5 unique FIRST flags;
- at least 5 unique LAST flags;
- non-collinear FIRST geometry;
- non-collinear LAST geometry.

Programme support thresholds required:
- at least 20 eligible PEMA individuals;
- at least 15 eligible PEER individuals.

Effect-blind support counts were:
- PEMA: 17;
- PEER: 6.

The frozen decision was:

`stop_downstream_home_range_not_estimable`.

Two effect workflows were triggered prematurely while the support run was still queued. Both stopped inside the analysis code at the frozen support gate before MCP area effects were calculated or persisted.

## S8. Reproducibility files

Core generic method:
- `analysis/temporal_aliasing_diagnostic_v1.py`
- `analysis/temporal_aliasing_bounds_v1.py`
- `analysis/simulate_temporal_aliasing_diagnostic_v1.py`

Generic tests:
- `tests/test_temporal_aliasing_diagnostic.py`
- `tests/test_temporal_aliasing_bounds.py`
- `tests/test_temporal_aliasing_simulation.py`
- `tests/test_temporal_aliasing_example.py`

Empirical validation:
- `analysis/san_jacinto_positional_aliasing_v1.py`
- `tests/test_san_jacinto_positional_aliasing.py`
- `results/san_jacinto_positional_aliasing_result_v1.json`

Review-package workflows verify these files independently of unrelated NEON project analyses.
