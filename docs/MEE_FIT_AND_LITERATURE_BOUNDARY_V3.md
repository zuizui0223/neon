# MEE fit and focused literature boundary — v4

Date: 2026-10-06

Status: current literature/implementation boundary for manuscript v0.6.

## What the current `secr` interface actually permits

Current `secr` documentation distinguishes exclusive trap detectors such as `multi` from non-exclusive proximity/count detectors. When old occasions are pooled and a `multi` capture history contains conflicting detector locations for the same animal, `reduce.capthist` explicitly resolves that locational ambiguity with

`select = c("last", "first", "random")`.

Usage data are pooled as well: detector usage is summed across the contributing occasions. Numeric `usage` is interpreted as effort and enters the detection process as a known linear coefficient on the hazard scale (Efford et al. 2013).

This matters for two reasons.

1. FIRST and LAST are not artificial manipulations invented for this manuscript; they are explicit conflict-resolution options in the current package interface.
2. The paper should not imply that `secr` loses repeated detector effort merely because occasions are pooled. Correctly retained usage carries that effort forward. The unresolved issue is which detector state represents an animal when several locations conflict, and whether the latent spatial state itself changes within the pooled occasion.

Sources rechecked 2026-10-05:
- current CRAN/R documentation for `secr::reduce.capthist`;
- current `secr::usage` documentation;
- current `secr.fit` documentation and vignettes.

## The reviewer objection: why not use each trap check as an occasion?

That is a valid representation and the manuscript acknowledges it directly.

The San Jacinto protocol checked traps three times within each night and released animals at the point of capture. The same raw record can therefore be represented as:

- **CHECK** — retain each physical check as an SCR occasion;
- **FIRST** — pool checks to one night and retain the first detector when a `multi` conflict occurs;
- **LAST** — pool checks to one night and retain the last detector.

The manuscript's question is not whether the data *must* be collapsed. It is:

> **When do defensible temporal representations of the same repeated-location record remain estimand-equivalent, and when do they cease to be so?**

When the latent state is effectively stable and the check-level observation law is symmetric under time reversal, FIRST and LAST are distributionally equivalent. Retaining every check is then the natural way to preserve information.

If the within-occasion state or observation process acquires an arrow of time, retaining all checks avoids record loss but does not make a static-state SCR model automatically correct. This is a state-model issue rather than a simple bookkeeping issue.

## Existing small-mammal precedent

Romairone et al. (2018) analysed live-trapped common voles with trapping days as SCR capture occasions even though traps were checked twice per day and animals were released where captured. This establishes direct precedent for an ecological occasion coarser than the physical check interval.

The precedent does not show that coarse occasions are universally optimal; it shows that the manuscript is addressing a real analytical decision rather than a contrived data transformation.

## Closest prior aggregation work

### Borchers et al. (2014)

Continuous-time SECR addresses loss and subjectivity created by discretizing exact detection times into occasions. This is the broader temporal-aggregation literature and must remain explicit.

### Milleret et al. (2018)

Milleret et al. showed that **spatial** aggregation of SCR detections can affect precision and bias detection-function parameters, with consequences that depend on the observation model. The present manuscript must therefore avoid claims such as “aggregation can bias SCR” or “observation model matters under aggregation” as novel.

The narrower contribution here is different:

- observed **within-occasion positional multiplicity** is screened directly;
- positional non-uniqueness is separated from **downstream estimand instability**;
- time-reversal symmetry is used as an interpretable process-level sufficient condition for FIRST/LAST stability, weaker than full exchangeability;
- mirrored ordered-state simulations show how an arrow of time breaks that condition;
- an empirical PEMA comparison shows that large positional aliasing can coexist with sigma stability.

## Repeated exposure and detector effort

For independent repeated exposures at one fixed detector, the binary at-least-one probability

\[
p_K(d)=1-\{1-p(d)\}^K
\]

is generally not obtained merely by changing the intercept of a one-check probability-scale half-normal curve. Hazard-scale exposure is algebraically additive.

This is a useful observation-model caution, but it is **not** evidence that current `secr` mishandles pooled effort. `secr` represents numeric usage as effort on the hazard scale, and `reduce.capthist` sums usage across pooled occasions. Accordingly, the manuscript treats effort preservation and location/state representation as separate issues.

## Process-level sufficient condition: time-reversal symmetry

Full temporal exchangeability is also sufficient but stronger than reversal symmetry. Reversal symmetry is not logically necessary for equal FIRST/LAST marginals.

Let one occasion contain ordered detector outcomes (Y=(Y_1,ldots,Y_K)), and let (R(Y)) denote reversal. A transparent directional sufficient condition is

\[
Y\overset d=R(Y)
\]

conditional on the latent state and observation design relevant to the downstream model.

Reversal exchanges FIRST and LAST, so under this condition

\[
F(Y)\overset d=L(Y).
\]

Serial dependence is not excluded: a reversible stationary process can satisfy the same condition without independent checks.

This reframes the stable case as absence of a detectable arrow of time, not absence of movement.

## Empirical stable side

The prospectively held-out observation-process result is strong:

- PEMA: 72.6% of 485 repeat nights shifted at least one trap spacing;
- PEER: 69.2% of 107 repeat nights did so;
- all eligible validation grids passed.

Yet the post-stop exploratory PEMA SCR comparison was stable:

- FIRST sigma = 8.8515 m;
- LAST sigma = 8.5625 m;
- LAST/FIRST = 0.9673;
- relative change = -3.27%.

A matched 19-session stationary-SCR displacement reference gives the same conclusion from the opposite direction: empirical per-axis RMS displacement was 9.1231 m versus a primary stationary 95% interval of 9.0979–10.4448 m, so an ordered post-capture state shift is not required to explain displacement magnitude. The empirical changed-trap fraction was instead 0.6972, below the independent-check stationary interval of 0.8761–0.9468, showing excess same-trap recurrence relative to that null. A post-result algebraic decomposition sharpens the pattern: same-trap repeats comprise 30.3% of observed repeat nights versus a primary-null median of 8.3% (95% 5.3–12.4%), while the RMS distance conditional on changing traps is 15.45 m versus a primary-null median of 14.30 m (95% 13.39–15.40 m). The first contrast exceeds the 97.5th percentile in all six supported sensitivity cells and the second in five of six. This is evidence about transition-distribution shape, not an identified handling mechanism.\n\nA naive independent-additive interpretation of the observed PEMA transition energy would predict approximately +24.0% inflation instead. The contrast is central: positional-span magnitude is not a direct sigma correction.

The post-result reversal audit is concordant with the stable interpretation:

- PEMA cluster sign-flip p = 0.193; mean directed vector = 0.071 m versus RMS 17.08 m;
- PEER p = 0.735; mean directed vector = 1.68 m versus RMS 16.26 m.

These are exploratory consistency diagnostics, not proof of reversibility.

## Simulated failure mode

The primary consequence benchmark contains a stationary control and mirrored ordered-state transition.

Stationary median LAST/FIRST ratios:
- 1.007;
- 0.966;
- 1.025.

POST ordered-transition ratios:
- 1.347;
- 1.154;
- 1.124.

Mirrored PRE ratios:
- 0.766;
- 0.856;
- 0.894.

PRE and POST preserve the same displacement magnitudes but reverse temporal ordering and the sign/direction of the FIRST/LAST effect. This is the cleanest evidence that a span-only diagnostic cannot identify a directed downstream consequence.

## Sequential robustness and its boundary

A sequential generator in which every physical check was generated directly through `secr` was used as a robustness lane.

Its initial 24-replicate null run narrowly failed the pre-specified <10% implementation gate (10.22%). A separately frozen, independently seeded zero-shift-only replication with 96 replicates per sigma passed the unchanged gate: maximum absolute median bias was 5.55%, and median LAST/FIRST ratios were 0.9968, 1.0031 and 0.9992.

The non-zero cells had already been opened before this larger null diagnostic, so they are not retroactively promoted as confirmatory evidence. Their role remains descriptive mechanism checking.

## Mechanistic calibration stop

A stricter observation-only v3 calibration searched 204 simple release-centred transient-state parameter cells and independently validated the 12 closest candidates against four San Jacinto targets:

- repeat-capture fraction;
- material-shift fraction among repeat nights;
- median all-repeat first-to-last distance;
- median changed-night distance.

Zero of 12 validation candidates passed all four criteria. No downstream sigma model was fitted in this calibration.

Binding interpretation:

> The paper may use ordered state change as a controlled failure mode, but it must not call that simple generator an empirically matched handling mechanism for San Jacinto.

## Handling/release boundary

Every later capture within a San Jacinto night occurs after at least one capture/handling/release event, so handling is a plausible contributor. It is not identifiable from these data as the cause.

The empirical first-to-last vector must not be described as:
- an undisturbed movement trajectory;
- home-range displacement;
- natural path length;
- proof of handling-induced movement.

Natural movement, trap attraction/avoidance, heterogeneous activity and stochastic recapture can all contribute.

## Continuous-time and dynamic models define the upper boundary

Continuous-time SECR and explicit movement/state models remain more complete solutions when exact event timing, serial dependence or observation-conditioned state change is central.

The manuscript must not claim:
- temporal aggregation is newly recognized;
- the proposed diagnostic replaces continuous-time/state-aware models;
- static SCR is universally invalid for repeated-check trapping;
- finer occasions are always sufficient or always insufficient;
- FIRST or LAST is universally preferable.

The proposed workflow occupies an earlier decision point:

1. screen whether within-occasion positional non-uniqueness is material;
2. ask whether the observation/state process is plausibly time-reversal symmetric;
3. test the intended downstream estimator under defensible temporal representations;
4. escalate to finer-time or state-aware modelling when the estimand is unstable.

## Defensible novelty wording

Avoid:

> Aggregation can bias SCR.

Prefer:

> **The manuscript separates positional non-uniqueness from estimand instability and uses time-reversal symmetry as a tractable diagnostic boundary between stable FIRST/LAST representation and ordered-state failure modes. It provides a scale-aware screen, a direct downstream stability test, and an empirical example in which substantial within-occasion positional variation coexists with a stable SCR spatial scale.**

The deterministic bounds are practical sensitivity translations rather than new mathematics.

## Current MEE position

The weakness that made v0.3 too thin has been resolved without needing a positive empirical bias result. The stronger contribution is that the paper explains **why a large raw aliasing signal may or may not matter downstream**, and identifies the extra temporal structure required for directional instability.

Pre-submission remains on HOLD only until the current-head review package/CI is green and author/archive metadata are complete. No additional same-data biological-effect search is justified.
