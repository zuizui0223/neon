# MEE pre-submission enquiry — HOLD draft v5

Date: 2026-10-05

**Status: HOLD — do not send yet.**

The scientific reason for the original v0.3 hold has been resolved, but the enquiry remains unsent until the current-head anonymous review package is green and final author/archive metadata are complete.

**Proposed article type:** Research Article  
**Working title:** *Diagnosing when temporal aggregation changes spatial scale inference in repeated-location ecological data*

## Draft enquiry text

Dear Editors,

We would like to ask whether a manuscript on **when temporal aggregation changes a downstream spatial estimand** would be suitable for *Methods in Ecology and Evolution*.

Repeated ecological observations are often collected more frequently than the occasion used in analysis. If one marked individual occupies several detector locations within an occasion, those records may be reduced to a single state. The obvious diagnostic is how far the alternative observed positions differ. Our central result is that this is only the first of two distinct questions: **positional non-uniqueness can be large while the downstream estimator remains stable**.

We develop a two-stage framework.

First, a scale-aware screen quantifies first-to-last positional span relative to a prechosen material spatial scale, separates repeat-observation-conditioned frequencies from conservative all-occasion lower bounds, and provides deterministic sensitivity bounds for selected spatial summaries.

Second, the intended downstream estimator is tested for **representation stability**. We show that the minimal directional-stability condition is time-reversal symmetry of the within-occasion observation process. Full temporal exchangeability is sufficient but not necessary: a serially dependent but reversible process can still make FIRST and LAST distributionally equivalent. Span-only summaries are invariant under time reversal, whereas any directed FIRST-versus-LAST contrast changes sign. Thus displacement magnitude alone cannot identify the direction—or even the existence—of downstream representation bias.

We validate the positional-non-uniqueness screen prospectively in two held-out Cricetidae from a public repeated-check live-trapping programme. First-to-last shifts of at least one 6.25-m trap spacing occurred on 72.6% of 485 repeat-capture nights for *Peromyscus maniculatus* and 69.2% of 107 nights for *P. eremicus*, with every eligible validation grid passing the pre-specified replication criterion.

Crucially, an explicitly post-stop exploratory SCR analysis of the 19 estimable *P. maniculatus* sessions showed a stable pooled spatial scale: sigma was 8.85 m under FIRST and 8.56 m under LAST (LAST/FIRST = 0.967; -3.3%). Treating the observed material first-to-last shifts as an independent additive transition kernel would instead predict approximately +24% inflation, demonstrating why raw span magnitude is not a correction for sigma.

A post-result, non-rescuing temporal-direction audit was concordant with this stable case. In PEMA, the mean directed first-to-last vector was only 0.071 m against a 17.08-m RMS changed-night displacement; a grid-stratified individual-cluster sign-flip audit gave p=0.193. We treat this only as consistency evidence, not proof of time-reversal symmetry.

Generative SCR simulations then establish the failure mode. Under stationary time-reversal-symmetric controls, CHECK, FIRST and LAST recovered the same generating spatial scale. When an ordered within-night state transition was imposed, FIRST and LAST diverged; reversing the state order reversed the direction of the sigma contrast while leaving the displacement magnitudes unchanged. The result identifies the missing ingredient: an **arrow of time** in the observation/state process.

We also retain negative results that bound the interpretation. Prospectively planned MCP and two-species empirical SCR analyses stopped at effect-blind support gates. A separate observation-only calibration searched 204 simple release-centred transient-state parameter cells and independently validated the 12 closest candidates; none reproduced all four empirical San Jacinto observation-process targets. We therefore do not infer that handling caused the observed shifts or claim that the state-transition stress test is a quantitatively matched San Jacinto mechanism.

The contribution is consequently narrower than a claim that temporal aggregation is new or generally biased. It is a practical framework that separates:
1. positional non-uniqueness,
2. temporal asymmetry,
3. downstream estimand instability.

The generic diagnostic is released as lightweight open-source code. We see its role as an early decision tool: stable representations can justify a coarse analysis, whereas directional instability motivates finer-time or state-aware modelling.

Would this combination of an exact representation-stability result, prospectively held-out empirical validation, model-specific downstream testing and explicit failure-mode simulation be within scope for an MEE Research Article?

Thank you for your consideration.

## Conditions for lifting HOLD

Before sending:
- [ ] current-head manuscript v0.5 and Supplement v0.3 pass repository invariant tests;
- [ ] current-head anonymous review package v4 builds successfully with the time-reversal audit and current figures;
- [x] Figure 2 contains the stationary null, mirrored ordered-state failure mode and exploratory PEMA stability/additive benchmark;
- [x] current `secr` detector/occasion/reduction and effort semantics are bounded correctly in the prose;
- [x] literature positioning acknowledges continuous-time SECR and prior aggregation work;
- [x] no text claims that handling caused the empirical pattern or that failure to reject proves time-reversal symmetry;
- [ ] final author/affiliation/contribution/funding/conflict metadata are supplied outside the double-anonymous manuscript;
- [ ] final versioned archival release / persistent identifier is created.

No additional same-data biological-effect search is required or justified to lift this hold.
