# MEE v0.4 — core Results text v1

Date: 2026-10-03

Status: manuscript-ready scientific core based only on already-opened empirical outputs and the frozen consequence simulation. Pending PEMA and CHECK-Bk workflows are deliberately excluded from the core claims.

## Within-night locational ambiguity was frequent and usually visible at the endpoints

Across PEMA and PEER, 592 of 1,520 valid individual-nights were observed at least twice within a night (38.9%). Among those repeat-observed nights, 450 (76.0%) contained captures at more than one trap. Thus cross-trap locational ambiguity was directly observed on at least 29.6% of all valid individual-nights.

The simpler FIRST-to-LAST endpoint identified 426 of the 450 cross-trap-conflict nights. It therefore missed 24 nights in which an individual left the first trap and later returned to it, corresponding to 5.3% of all directly observed cross-trap conflicts. The endpoint diagnostic is consequently conservative but captured 94.7% of the full-history conflicts exposed by repeated checking in these data.

The pattern was similar in the two held-out species. PEMA had cross-trap conflict on 77.1% of repeat-observed nights, whereas PEER had conflict on 71.0%.

## Observed transition energy was large relative to common small-mammal SCR scales

Using zero displacement for same-trap repeat nights, the pooled mean squared FIRST-to-LAST displacement across all 592 repeat-observed nights was 206.46 m^2. The corresponding per-axis transition scale among repeat-observed nights was 10.16 m.

After weighting by the observed repeat-observation fraction, the directly observed all-night transition scale was

T_obs = sqrt[(592/1520) E(delta^2 | repeat) / 2] = 6.34 m.

Species-specific values were 6.49 m for PEMA and 5.70 m for PEER.

This calibration was spatially and individually distributed. Leaving out each species-by-grid block in turn while holding the pooled repeat-observation fraction fixed gave T_obs values of 5.98–6.48 m. The largest grid-specific individual cluster contributed 7.6% of observed squared-displacement energy; the five largest clusters contributed 17.7%.

## Stationary SCR did not show a systematic FIRST/LAST bias

The downstream simulation first generated a stationary SCR process and then represented the same check-level histories as CHECK, NIGHT-FIRST or NIGHT-LAST data.

At the central generating sigma of 12.5 m, median relative sigma bias was:
- CHECK: +0.2%;
- FIRST: +3.2%;
- LAST: +0.7%.

Across the frozen sigma grid, stationary FIRST and LAST estimates remained centered close to the generating value. Individual finite samples could differ substantially because nightly aggregation discards detections, but there was no directional FIRST-versus-LAST effect under a single stationary spatial state.

This negative control is important: the downstream effect is not an automatic consequence of reducing the number of occasions.

## Observation-conditioned state mixing changed which sigma was estimated

The empirical-transition simulation then added the already-opened San Jacinto within-night transition process to the stationary SCR generator.

Under the POST mechanism, the FIRST location represented the canonical state and LAST represented the displaced state. At generating sigma = 12.5 m:
- FIRST median relative bias was -1.7%;
- LAST median relative bias was +15.1%;
- the paired median LAST/FIRST sigma ratio was 1.154.

Under the PRE mirror, the biological labels were reversed: LAST was canonical and FIRST displaced. At the same generating sigma:
- LAST median relative bias was +0.03%;
- FIRST median relative bias was +16.6%;
- the paired median FIRST/LAST sigma ratio was 1.169.

The direction therefore reversed when the timing mechanism was reversed. FIRST is not intrinsically preferable to LAST, nor vice versa. Rather, the representative-location rule determines which observation-conditioned spatial state contributes to the fitted spatial scale.

At generating sigma = 6.25 m, the median displaced/canonical ratio was approximately 1.31–1.35; at 25 m it was approximately 1.12 after excluding two numerically invalid fits according to the independent positive-SE criterion.

## A dimensionless state-mixing ratio predicts when the ambiguity can matter

For an isotropic within-occasion transition with all-night per-axis scale T and baseline spatial scale sigma, the continuous dense-detector second-moment benchmark is

sigma_eff / sigma ~= sqrt[1 + (T/sigma)^2].

Define

A_sigma = T / sigma_ref.

A 10% scale change corresponds to A_sigma >= 0.458.

Using T_obs = 6.34 m, that boundary occurs at a reference sigma of approximately 13.84 m.

This is not an estimate of the real San Jacinto sigma. It is a prospective diagnostic: the same within-occasion ambiguity is expected to be more consequential for analyses whose independent/reference spatial scale is small relative to the observed transition scale.

## Numerical QA did not create the central result

A numerical audit found two pathological fits in the PRE / sigma=25 m / FIRST cell with sigma estimates above 300 km but reported sigma SE exactly zero. The original success rule had incorrectly retained these fits because the point estimates and confidence limits were finite.

The success rule was repaired to require a finite positive sigma SE and finite ordered confidence limits, without imposing any effect-size or sigma-magnitude cutoff.

No central sigma=12.5 m fit failed this rule, so the main 15–17% representative-state result is unchanged.

## Interpretation

The results separate two processes that should not be conflated.

1. **Temporal thinning / information loss:** if all checks sample one stationary SCR state, selecting FIRST or LAST mainly reduces information and does not create a systematic new sigma.
2. **Observation-state mixing:** if capture, handling, release or another protocol event changes the short-term spatial/detection state within the nominal occasion, selecting one record can select which state the fitted sigma represents.

The method is therefore best framed as a diagnostic of **estimand stability under locational ambiguity**, not as a claim that temporal aggregation is universally biased.

## Literature-positioning sentence for Results/Discussion transition

Current `secr` documentation already recognizes that combining trap occasions can produce "locational ambiguity" and resolves multi-catch conflicts by selecting FIRST, LAST or a random location. Continuous-time SCR methods can avoid coarse occasioning when exact event times are known, and recent work explicitly allows capture/release processes and history-dependent capture intensity. The remaining practical gap is deciding when the location-selection ambiguity in interval-censored repeated-check data is large enough to matter for a downstream spatial estimand.
