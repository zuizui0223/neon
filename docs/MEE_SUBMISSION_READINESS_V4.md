# MEE submission-readiness checklist — live-trap aliasing v6

Date: 2026-10-06

## Scientific core

- [x] Central question is estimand stability: when does temporal representation change a downstream spatial quantity?
- [x] Positional aliasing is explicitly a warning condition, not a bias estimate.
- [x] Prospectively held-out positional non-uniqueness validation passed in PEMA and PEER.
- [x] Spatial replication passed in 7/7 PEMA and 3/3 PEER eligible grids.
- [x] Repeat-conditioned estimates are separated from all-night observed lower bounds.
- [x] Prospectively frozen MCP analysis remains stopped at its support gate.
- [x] Prospectively planned two-species empirical SCR sigma programme remains stopped because PEER failed its support gate.
- [x] The PEMA-only SCR comparison is explicitly post-stop exploratory.

## Representation-stability results

- [x] PEMA FIRST sigma = 8.8515 m; LAST sigma = 8.5625 m; LAST/FIRST = 0.9673 (-3.27%).
- [x] Matched 19-session stationary-SCR displacement reference addresses the main state-shift alternative: 218/525 nights were repeat-observed, empirical per-axis RMS = 9.1231 m, and the primary stationary 95% interval = 9.0979–10.4448 m.
- [x] Empirical changed-trap fraction = 0.6972, below the primary independent-check stationary 95% interval = 0.8761–0.9468, supporting short-term positional persistence/serial dependence rather than excess displacement.
- [x] Post-result second-moment decomposition is receipted: same-trap fraction = 30.3% versus primary-null median 8.3% (95% 5.3–12.4%); changed-night RMS = 15.45 m versus primary-null median 14.30 m (95% 13.39–15.40 m). Same-trap excess occurs in 6/6 supported cells and changed-night RMS exceeds the 97.5th percentile in 5/6.
- [x] The empirical PEMA result is contrasted with an independent-additive second-moment prediction of approximately +24.0%, showing that raw span magnitude is not a sigma correction.
- [x] Stationary SCR controls show FIRST/LAST equivalence: median ratios 1.007, 0.966 and 1.025.
- [x] Mirrored ordered-state simulations reverse the FIRST/LAST direction while preserving displacement magnitudes.
- [x] POST median LAST/FIRST ratios = 1.347, 1.154, 1.124.
- [x] PRE median LAST/FIRST ratios = 0.766, 0.856, 0.894.
- [x] CHECK-level stress-test results are not used as a clean estimate of state-mixing bias because the primary stress generator also changes encounter dependence.

## Time-reversal theory and audit

- [x] Time-reversal symmetry is stated as a transparent process-level sufficient condition for FIRST/LAST stability, weaker than full temporal exchangeability but not logically necessary.
- [x] Full exchangeability is treated as a sufficient special case; reversible serial dependence is allowed.
- [x] Span-only statistics are invariant to reversal while directed FIRST/LAST contrasts are antisymmetric.
- [x] Post-result grid-stratified, individual-cluster sign-flip audit is labelled exploratory and non-rescuing.
- [x] PEMA: reversal p=0.193; mean directed vector magnitude 0.071 m versus RMS 17.08 m.
- [x] PEER: reversal p=0.735; mean directed vector magnitude 1.68 m versus RMS 16.26 m.
- [x] No claim is made that failure to reject proves reversal symmetry.

## Sequential robustness and calibration boundary

- [x] Sequential generator creates every physical check directly through secr and changes only the within-night state centre.
- [x] Initial 24-replicate zero-shift run narrowly failed the <10% implementation gate (10.22%).
- [x] Independently seeded zero-shift-only replication used 96 replicates per sigma and the unchanged gate.
- [x] Independent null replication passed: maximum absolute median bias 5.55%; LAST/FIRST ratios 0.9968, 1.0031 and 0.9992.
- [x] Already-opened non-zero cells are not retroactively promoted after the original failed-gate run.
- [x] Observation-only v3 calibration searched 204 cells and independently validated the 12 closest candidates.
- [x] Zero of 12 candidates matched all four San Jacinto observation-process targets.
- [x] Frozen calibration decision remains `stop_v3_no_observation_process_match`.
- [x] No downstream sigma was fitted in the v3 calibration and no handling mechanism is claimed.

## Aggregation theory and literature boundary

- [x] Current secr FIRST/LAST reduction semantics are documented.
- [x] Direct small-mammal precedent for coarser occasions is retained.
- [x] Continuous-time SECR literature is acknowledged as the broader solution to temporal aggregation and movement dependence.
- [x] Milleret et al. (2018) is used to bound novelty: aggregation effects are already known to depend on observation model.
- [x] Detection-kernel closure is retained as a distinct theoretical issue in the Supplement: probability-HN pooling is not shape-closed under a simple at-least-one Bernoulli representation, whereas hazard-HN exposure is closed.
- [x] No claim is made that secr itself mishandles effort; its usage model operates on the hazard scale.

## Manuscript / figures / reproducibility

- [x] Manuscript v0.6 uses the positional-non-uniqueness → serial-persistence/time-reversal → estimand-stability structure.
- [x] Supplement v0.3 contains the estimator benchmark, time-reversal theorem, closure note, SCR consequence benchmark and post-result symmetry audit.
- [x] Figure 2 is a four-panel stability figure: stationary null, mirrored state-transition failure mode, exploratory PEMA stability plus additive benchmark, and the matched-session stationary displacement check.
- [x] Figure captions v4 match the current figure set.
- [x] Generic and manuscript invariant tests include the additive benchmark and time-reversal audit.
- [x] Review-package builder includes the time-reversal audit, v3 calibration stop, and matched PEMA stationary-displacement diagnostic.
- [ ] Final review-package workflow at the current head must complete successfully after the latest synchronization.
- [ ] Create final versioned archival release / persistent repository identifier.

## Author / submission metadata

- [ ] Final author list and affiliations.
- [ ] Author-contribution statement.
- [ ] Funding statement.
- [ ] Conflict-of-interest statement.
- [x] AI-assisted development disclosure remains in Methods.
- [ ] Final anonymous title-page/manuscript split.

## Current decision

**Scientific status:** the v0.3 weakness has been resolved in a stronger form than a simple “aggregation biases sigma” result. The paper now shows that frequent within-occasion positional non-uniqueness can coexist with downstream stability, uses time-reversal symmetry as an interpretable sufficient condition for directional stability, and demonstrates by mirrored simulation how an arrow of time can break that stability. The matched-session stationary reference further shows that the empirical PEMA displacement magnitude itself does not require an ordered post-capture state shift, while the much lower changed-trap fraction reveals short-term persistence that the independent-check null misses. The v3 calibration stop prevents over-interpreting a simple handling-response mechanism.

**Pre-submission status:** **HOLD until the current-head review package/CI is green and the remaining author/archive metadata are completed.** No further same-data biological-effect search is justified.

**Analysis policy:** do not open a new downstream endpoint or relax a failed gate. Preserve the MCP and two-species SCR stops. Treat the PEMA fit, reversal audit and sequential diagnostics according to their explicit exploratory/robustness labels.
