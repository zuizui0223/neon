# Novelty stress test — live-trap temporal aliasing v1

Date: 2026-10-07

## Verdict

The paper has **moderate, MEE-level novelty**, not a fundamental discovery of a new ecological law.

The mathematically obvious part is not the contribution: if an ordered process is invariant under time reversal, FIRST and LAST have the same marginal distribution; reversing a sequence preserves first-to-last distance. Nor is it novel that temporal aggregation, movement dependence or trap responses can affect SCR.

## Prior-art boundary

- Borchers et al. (2014): temporal aggregation can discard information and become sensitive to within-occasion variation/correlation.
- Milleret et al. (2018): aggregation can alter precision and bias depending on observation model.
- Stevenson et al. (2022): movement can induce residual spatial correlation beyond the activity centre and bias SCR.
- Recent movement/history-dependent SCR models explicitly model dependence rather than assuming conditionally independent detections.
- Current `secr` already exposes FIRST/LAST/random conflict resolution when occasions are pooled.

## What is genuinely useful and non-trivial here

### 1. A warning signal is not a consequence estimate

Large or frequent within-occasion displacement is commonly tempting to interpret as evidence that temporal coarsening must distort spatial scale. This paper shows why that inference fails.

In PEMA, 72.6% of repeat nights shifted at least one trap spacing. Yet the observed FIRST/LAST sigma point contrast was only -3.3%, and empirical displacement RMS remained inside the matched stationary-SCR reference.

### 2. The naive span-based correction failed in both size and sign

Using the observed transition energy as an independent additive displacement predicts roughly +24% sigma inflation at the observed FIRST sigma. The actual point contrast was -3.3%.

The comparison is not a formal equivalence test, but it is a direct empirical counterexample to treating raw transition magnitude as a sigma correction.

### 3. Similar marginal scale hid a different temporal process

PEMA same-trap repeat probability was 30.3% versus a primary stationary-null median of about 8.3%. Conditional on changing traps, distances were somewhat longer. The marginal RMS could therefore look stationary-compatible while the transition mixture was strongly different.

This is mathematically possible by construction, but empirically it is not obvious before looking at the data.

### 4. Mirrored ordering isolates what span cannot contain

PRE and POST stress simulations retain the same displacement magnitudes and span distribution but reverse the FIRST/LAST sigma effect. This turns the elementary reversal observation into a practical falsification result: no diagnostic based only on unordered span can determine the direction of a representation effect.

## What not to claim

Do not claim:
- dependence in SCR is newly discovered;
- aggregation bias is newly discovered;
- time-reversal symmetry is a deep new theorem;
- PEMA proves FIRST and LAST are equivalent;
- the release protocol caused the same-trap recurrence;
- the downstream empirical result is general beyond this PEMA programme.

## Publication-level assessment

**MEE:** defensible if framed as a practical diagnostic/decision framework with an empirical counterexample to span-based intuition.

**Broader ecology/high-impact:** currently too narrow. The downstream empirical test is one species/programme and the central theoretical identity is elementary.

## One-sentence novelty claim

> Large within-occasion displacement is a warning that temporal representation may matter, but its magnitude cannot tell whether, how much, or in which direction a downstream spatial estimand will change.

That sentence is the manuscript's strongest defensible novelty boundary.
