# MEE pre-submission enquiry — HOLD draft v6

Date: 2026-10-06

**Status: HOLD — do not send yet.**

This draft is updated to manuscript v0.6. The scientific reason for the original hold—absence of a demonstrated downstream consequence—has been resolved in a more informative form. The manuscript now distinguishes frequent positional non-uniqueness from downstream estimand instability and identifies temporal asymmetry as the condition that can make a representative-location rule directional.

The enquiry should remain unsent until the current-head dedicated live-trap-aliasing review-package workflow is green, author metadata are complete, and the archival release is prepared.

**Proposed article type:** Research Article  
**Working title:** *Diagnosing when temporal aggregation changes spatial scale inference in repeated-location ecological data*

## Draft enquiry text

Dear Editors,

We would like to ask whether our manuscript, **“Diagnosing when temporal aggregation changes spatial scale inference in repeated-location ecological data,”** would be suitable as a Research Article in *Methods in Ecology and Evolution*.

Ecological observations are often collected more frequently than the occasions used for analysis. When several valid locations of the same marked individual are collapsed to one spatial state, the common response is to ask how large the within-occasion movement was. We address a different question: **when does that coarsening actually change the downstream estimand?**

We introduce a two-stage framework. A scale-aware diagnostic first quantifies within-occasion positional non-uniqueness relative to a prechosen material spatial scale. A representation-stability test then evaluates the intended downstream estimator under defensible temporal reductions. We show that time-reversal symmetry provides a process-level stability boundary: reversal leaves span-only diagnostics unchanged but exchanges FIRST and LAST, so large positional spans alone cannot identify either the existence or direction of a FIRST-versus-LAST effect.

We test the framework using public repeated-check live-trapping data and SCR simulation. In prospectively held-out validation, shifts of at least one 6.25-m trap spacing occurred on 72.6% of 485 repeat-capture nights for *Peromyscus maniculatus* and 69.2% of 107 nights for *P. eremicus*. Yet a clearly labelled post-stop exploratory SCR analysis of 19 estimable PEMA sessions gave a small point contrast: sigma was 8.85 m under FIRST and 8.56 m under LAST (-3.3%). Because the paired fit covariance was not retained, we do not present this as an equivalence result; a delta-method sensitivity shows that uncertainty in the ratio depends materially on the unknown FIRST/LAST estimate correlation. In those same sessions, first-to-last displacement RMS was compatible with a fixed-centre stationary-SCR reference, although the transition distribution was not: same-trap repeats were 30.3% versus a stationary-null median of 8.3%, while RMS distance conditional on changing traps was 15.45 versus 14.30 m in the primary reference. The same-trap excess was robust across all nine sensitivity cells, whereas support for the longer changed-night tail varied across cells. Thus a similar marginal spatial scale was assembled from a different within-occasion process.

Controlled simulations identify the failure mode. FIRST and LAST remained equivalent under a stationary time-reversal-symmetric generator. Introducing an ordered state transition produced median LAST/FIRST sigma ratios of 1.35, 1.15 and 1.12 across three spatial scales; reversing the transition order produced 0.77, 0.86 and 0.89. The span distribution is unchanged by reversal, but the downstream direction changes.

The field protocol released animals at the capture detector after each check, providing a plausible source of short-term trap-centred persistence, but our independent calibration did not identify this as the empirical mechanism. Movement-driven dependence in SCR is already recognized, and we do not claim otherwise. Our contribution is to separate three properties that are often conflated—positional non-uniqueness, serial dependence and directional temporal asymmetry—and to connect them explicitly to estimand stability. We also retain negative results: planned empirical downstream routes that lacked support remain stopped, and a simple handling-centred mechanism failed independent calibration, so we make no causal handling claim.

The empirical downstream sigma comparison is limited to PEMA in one repeated-check trapping programme, whereas the positional-aliasing screen was prospectively replicated in both species. The diagnostic is intended for repeated-location data beyond live trapping, including camera detections, telemetry, acoustic localization and repeated resightings. Would this combination of a general diagnostic, a time-reversal stability result, prospective validation and direct downstream simulation be within scope for an MEE Research Article?

Thank you for your consideration.

## Conditions for lifting HOLD

All of the following should be true before sending:

- current-head anonymous review-package build passes;
- manuscript v0.6, Supplement v0.3 and Figure Captions v4 remain synchronized;
- final author list and affiliations are supplied outside the double-anonymous manuscript;
- author-contribution, funding and conflict-of-interest statements are complete;
- versioned archival release / persistent repository identifier is prepared;
- no text implies that handling caused the empirical transition, that failure to reject proves time-reversal symmetry, or that FIRST/LAST/CHECK has a universally correct ordering.

No additional same-data biological-effect search is required to lift this hold.
