# MEE pre-submission enquiry — HOLD draft v5

Date: 2026-10-05

**Status: HOLD — do not send yet.**

This draft is updated to manuscript v0.5. The scientific reason for the original hold—absence of a demonstrated downstream consequence—has been resolved in a more informative form. The manuscript now distinguishes frequent positional non-uniqueness from downstream estimand instability and identifies temporal asymmetry as the condition that can make a representative-location rule directional.

The enquiry should remain unsent until the current-head manuscript/review-package CI is green, author metadata are complete, and the archival release is prepared.

**Proposed article type:** Research Article  
**Working title:** *Diagnosing when temporal aggregation changes spatial scale inference in repeated-location ecological data*

## Draft enquiry text

Dear Editors,

We would like to ask whether a manuscript on **temporal positional aliasing and downstream representation stability** would be suitable for *Methods in Ecology and Evolution*.

Ecological observations are often collected more frequently than the temporal occasion used in downstream spatial analysis. When the same marked individual is observed at several detector locations within one nominal occasion, reducing those records to one position creates a spatial-state choice. The practical question, however, is not merely whether those locations differ: **when does the temporal representation change the spatial quantity the analyst intends to estimate?**

We make three linked contributions.

First, we introduce a lightweight scale-aware screen for within-occasion positional non-uniqueness. It quantifies first-to-last span relative to a prechosen material spatial scale, keeps repeat-conditioned estimates separate from conservative all-occasion lower bounds, and provides deterministic FIRST-versus-LAST sensitivity bounds for selected spatial summaries. We also formalize an identification limit: if the within-occasion observation law is symmetric under time reversal, FIRST and LAST are distributionally equivalent even when their realized locations differ. Full temporal exchangeability is sufficient but not necessary; span magnitude alone cannot identify the sign of a downstream FIRST/LAST effect.

Second, we validate positional non-uniqueness prospectively in two held-out Cricetidae species from a public repeated-check live-trapping programme. Shifts of at least one 6.25-m trap spacing occurred on 72.6% of 485 repeat-capture nights for *Peromyscus maniculatus* and 69.2% of 107 nights for *P. eremicus*, with every eligible validation grid exceeding the pre-specified threshold. Yet a clearly labelled post-stop exploratory SCR analysis of 19 estimable PEMA sessions was stable: sigma was 8.85 m under FIRST and 8.56 m under LAST (LAST/FIRST = 0.967; -3.3%). A post-result cluster sign-flip audit likewise found no clear grid-stratified first-to-last directional asymmetry (PEMA p = 0.193; PEER p = 0.735).

Third, we identify the failure mode with controlled SCR simulation. Under a stationary time-reversal-symmetric generator, FIRST and LAST remained equivalent. We then imposed the same within-night displacement magnitudes as an ordered state transition. With the baseline state first and transitioned state last, median LAST/FIRST sigma ratios were 1.35, 1.15 and 1.12 across three generating spatial scales; reversing the order produced 0.77, 0.86 and 0.89. The span distribution is unchanged by this reversal, but the downstream direction changes. Thus the consequential ingredient is an arrow of time in the observation/state process, not positional variation alone.

The empirical example also shows why raw span should not be treated as a bias correction. If the observed PEMA first-to-last vectors were naively interpreted as independent additive displacements, their transition energy would predict about +24% sigma inflation; the observed FIRST/LAST change was instead -3.3%.

We retain several negative results explicitly. A prospectively planned MCP analysis and two-species empirical SCR sigma programme stopped at support gates. A separate 204-cell observation-only calibration of a simple release-centred transient-state mechanism produced zero independently validated cells matching all four San Jacinto observation-process targets, so we do not attribute the empirical pattern to handling or promote that generator as an empirically matched mechanism.

The proposed workflow is therefore not “never aggregate.” It is: screen for material positional non-uniqueness, assess whether the observation process contains a temporal arrow, test the intended downstream estimand under defensible representations, and move to finer-time or state-aware modelling only when that estimand is unstable.

Would this combination of a general diagnostic, a time-reversal stability result, prospectively held-out empirical validation and direct downstream SCR consequence benchmark be within scope for an MEE Research Article?

Thank you for your consideration.

## Conditions for lifting HOLD

All of the following should be true before sending:

- current-head frozen-paper checks pass;
- current-head anonymous review-package build passes;
- manuscript v0.5, Supplement v0.3 and Figure Captions v4 remain synchronized;
- final author list and affiliations are supplied outside the double-anonymous manuscript;
- author-contribution, funding and conflict-of-interest statements are complete;
- versioned archival release / persistent repository identifier is prepared;
- no text implies that handling caused the empirical transition, that failure to reject proves time-reversal symmetry, or that FIRST/LAST/CHECK has a universally correct ordering.

No additional same-data biological-effect search is required to lift this hold.
