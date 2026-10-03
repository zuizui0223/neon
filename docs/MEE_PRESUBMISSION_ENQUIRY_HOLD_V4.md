# MEE pre-submission enquiry — HOLD draft v4

Date: 2026-10-03

**Status: HOLD — do not send yet.**

The v3 enquiry is retained as historical provenance but is superseded. It was drafted before the paper had a direct downstream-parameter consequence. Manuscript v0.4 now contains that missing result, so the scientific reason for the earlier hold has been substantially addressed. This enquiry should nevertheless remain unsent until the v0.4 manuscript, Figure 2, Supplement v0.3 and anonymous review package have completed a final consistency and literature-boundary review.

**Proposed article type:** Research Article  
**Working title:** *Diagnosing when temporal aggregation changes spatial scale inference in repeated-location ecological data*

## Draft enquiry text

Dear Editors,

We would like to ask whether a manuscript on **temporal positional aliasing**—within-occasion spatial variation hidden when repeated observations of a marked individual are reduced to one detector state—would be suitable for *Methods in Ecology and Evolution*.

The paper addresses a practical decision made before many spatial analyses: when observations are collected more frequently than the ecological occasion used downstream, does collapsing them merely discard information, or can it change the spatial parameter being estimated?

We make three linked contributions.

First, we provide a scale-aware diagnostic of first-to-last within-occasion positional span relative to a prechosen material spatial scale, together with a conservative all-occasion directly observed lower bound and deterministic FIRST-versus-LAST sensitivity bounds for selected spatial summaries.

Second, we validate the phenomenon prospectively in two held-out Cricetidae species from a public repeated-check live-trapping programme. First-to-last shifts of at least one 6.25-m trap spacing occurred on 72.6% of 485 repeat-capture nights for *Peromyscus maniculatus* and 69.2% of 107 nights for *P. eremicus*. The pre-specified spatial-replication criterion was met in every eligible validation grid. Across all valid individual-nights, directly observed material shifts provided conservative lower bounds of 28.9% and 24.6%, respectively.

Third, we test the missing downstream consequence with a generative spatial capture-recapture benchmark using the same 7×7 trap geometry, observed repeat frequency and observed detector-to-detector transition vectors. Under a stationary negative control, CHECK-, FIRST- and LAST-based representations recovered the same generating spatial scale: the largest absolute median relative sigma bias was below 4%, and paired FIRST/LAST ratios were near one. After injecting the empirical within-night transition kernel, the representative-state rule became consequential. With the baseline state first and the transitioned state last, median LAST/FIRST sigma ratios were 1.35, 1.15 and 1.12 for generating sigma values of 6.25, 12.5 and 25 m. Mirroring the state order reversed the direction (0.77, 0.86 and 0.89).

This mirrored design is important to the interpretation. We do not claim that FIRST or LAST is the biologically correct state, or that handling caused the empirical transitions. Instead, the result shows that when one nominal occasion mixes observation-conditioned spatial states, defensible temporal representations can target different effective spatial scales. Treating every physical trap check as a separate occasion preserves observations but does not by itself remove this state-mixture problem under a static-centre SCR model.

A prospectively planned empirical MCP analysis and a two-species empirical SCR sigma analysis both stopped at effect-blind support gates, and we retain those stops. The manuscript therefore combines a held-out empirical observation-process result with a controlled downstream consequence simulation rather than presenting an under-supported post hoc empirical effect.

The generic diagnostic is released as lightweight open-source code and is intended as a pre-analysis screen for deciding whether temporal aggregation is negligible, whether representative-state sensitivity should be reported, or whether a finer-time/state-aware model is warranted.

Would this combination of a general diagnostic, prospectively held-out empirical validation and direct downstream SCR consequence benchmark be within scope for an MEE Research Article?

Thank you for your consideration.

## Conditions for lifting HOLD

All of the following should be true before sending:
- manuscript v0.4 and Supplement v0.3 pass invariant tests;
- regenerated Figure 2 is visually checked against the frozen SCR consequence JSON; **completed 2026-10-03**
- anonymous review package v3 builds successfully and contains the v0.4/v0.3 files;
- literature wording around `secr` detector/occasion semantics is rechecked against current CRAN documentation; **completed 2026-10-03**
- no text implies that handling caused the empirical transition or that CHECK/FIRST/LAST has a universally correct ordering;
- final author/affiliation metadata are supplied outside the double-anonymous manuscript package.

No additional biological effect search is required to lift this hold. The remaining hold items are final prose consistency, author/affiliation statements and archival-release metadata.
