# Key methodological statements — live-trap aliasing v2

Date: 2026-10-05

## 30-second editor summary

Ecological observations are often collected more frequently than the temporal occasion used in downstream spatial analysis. When one marked individual occupies several detector locations within a nominal occasion, collapsing the record to one position creates **positional non-uniqueness**. We show that this is not itself a bias estimate. The key second question is whether the downstream estimand is stable to defensible temporal representations.

The manuscript combines a scale-aware positional-aliasing screen with a representation-stability analysis. A transparent process-level sufficient condition is time-reversal symmetry: if the within-occasion observation law is unchanged when check order is reversed, FIRST and LAST are distributionally equivalent even when their realized locations differ. Full temporal exchangeability is sufficient but not necessary.

## Central claim

> Frequent within-occasion positional non-uniqueness can coexist with a stable downstream spatial parameter. Directional FIRST-versus-LAST divergence requires additional temporal asymmetry—an arrow of time in the observation or state process—rather than large positional span alone.

## Strongest empirical claims

> In two prospectively held-out Cricetidae species, first-to-last shifts of at least one 6.25-m trap spacing occurred on 72.6% of 485 repeat-capture nights for *Peromyscus maniculatus* and 69.2% of 107 nights for *P. eremicus*, with every eligible validation grid exceeding the pre-specified materiality threshold.

> Yet in a clearly labelled post-stop exploratory SCR analysis of 19 estimable PEMA sessions, FIRST sigma was 8.8515 m and LAST sigma was 8.5625 m (LAST/FIRST = 0.9673; -3.27%). Thus strong positional aliasing did not automatically imply material sigma instability.

## Reversal-symmetry evidence

> A post-result, non-rescuing grid-stratified individual-cluster sign-flip audit found no clear directional first-to-last asymmetry (PEMA p = 0.193; PEER p = 0.735). PEMA's mean directed vector was only 0.071 m compared with a 17.08-m RMS changed-night displacement.

This is consistency evidence only; it does not prove exact reversibility or independence.

## Why raw span is not a sigma correction

For PEMA, treating the directly observed material vectors as independent zero-mean additive displacements would predict approximately +24.0% sigma inflation from the continuous second-moment benchmark. The observed FIRST/LAST change was instead -3.3%.

> The magnitude of observed within-occasion span cannot be converted directly into downstream sigma bias without an assumption about temporal ordering and state dynamics.

## Simulation claim

Under a stationary, time-reversal-symmetric SCR generator, FIRST and LAST remained equivalent at the cell-median level. When the same displacement magnitudes were imposed as an ordered state transition, FIRST/LAST sigma diverged; reversing PRE versus POST ordering reversed the direction of the effect.

> The mirrored simulation identifies temporal asymmetry, not displacement magnitude alone, as the ingredient that makes the representative-state rule directional.

## Observation-model boundary

Pooling repeated occasions can also alter the effective detection process if detector effort is discarded. In current `secr`, detector `usage` is interpreted as effort on the hazard scale and `reduce.capthist` sums usage across pooled occasions, so the manuscript does **not** claim that `secr` intrinsically mishandles repeated exposure. The unresolved problem is conflicting detector location and/or within-occasion state change.

## Mechanism boundary

A separate observation-only calibration searched 204 release-centred transient-state parameter cells and independently validated the 12 closest candidates. Zero of 12 matched all four San Jacinto targets simultaneously.

> The paper therefore does not claim that handling or a simple release-centred state shift generated the empirical pattern.

## Safest all-night claim

> Even when all valid individual-nights are used as the denominator and single-capture nights are left unresolved, material first-to-last shifts were directly observed on at least 28.9% of PEMA nights and 24.6% of PEER nights.

## What this paper does not claim

- It does not reconstruct an unrestricted movement path.
- It does not identify FIRST or LAST as the biologically correct location.
- It does not estimate empirical two-species SCR sigma bias.
- It does not rescue the stopped MCP or two-species SCR analyses.
- It does not claim handling caused the observed transition.
- It does not claim failure to reject the reversal audit proves time-reversal symmetry.
- It does not claim temporal aggregation is a newly discovered problem.
- It does not claim every repeated-check dataset requires a dynamic model.
- It does not generalize the San Jacinto effect magnitude to all live-trapping protocols or taxa.
