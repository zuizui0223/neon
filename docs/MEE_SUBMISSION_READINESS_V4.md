# MEE submission-readiness checklist — live-trap aliasing v4

Date: 2026-10-03

## Scientific core

- [x] Methodological question is central: when does temporal aggregation alter a downstream spatial estimand?
- [x] Temporal positional aliasing is defined as an observation-process property, not a reconstructed movement path.
- [x] Generic scale-aware diagnostic and deterministic FIRST/LAST sensitivity bounds are retained.
- [x] Prospectively held-out positional-aliasing validation passed in PEMA and PEER.
- [x] Spatial replication passed in 7/7 PEMA and 3/3 PEER eligible grids.
- [x] Repeat-conditioned denominator limitation and all-night observed lower bounds are explicit.
- [x] Original diagnostic-estimator simulation is retained as a supplementary property check rather than the main result.
- [x] Prospectively frozen MCP effect analysis remains stopped.
- [x] Two-species empirical SCR sigma programme remains stopped because PEER failed its support gate.
- [x] No home-range effect or empirical two-species sigma effect is claimed.

## Downstream SCR consequence benchmark

- [x] Empirical transition kernel reproduces frozen held-out counts: 1,520 valid nights, 592 repeat-observed, 426 material transitions.
- [x] Pooled empirical transition probability = 0.2803.
- [x] Pooled changed-night median displacement = 12.5 m; RMS = 16.94 m.
- [x] Continuous second-moment benchmark derived and documented.
- [x] 10% analytic scale-sensitivity boundary is approximately sigma = 13.84 m.
- [x] Simulation uses the San Jacinto 7×7 grid, 6.25-m spacing and three checks per night.
- [x] Stationary negative controls included.
- [x] Mirrored PRE/POST transition orientations prevent an intrinsic advantage for FIRST.
- [x] CHECK, FIRST and LAST representations are compared against known generating sigma.
- [x] 40 replicates per cell completed.
- [x] Stationary maximum absolute median sigma bias <4%.
- [x] Stationary paired LAST/FIRST ratios remain near one.
- [x] Empirical-transition POST median LAST/FIRST ratios = 1.347, 1.154, 1.124.
- [x] Mirrored PRE ratios = 0.766, 0.856, 0.894.
- [x] CHECK is interpreted as retaining detections but potentially estimating a state mixture; it is not labelled intrinsically biased.
- [x] No statement attributes the empirical transition specifically to handling.

## Manuscript / supplement

- [x] Manuscript v0.4 drafted with the downstream SCR consequence as Results 3.1.
- [x] Supplement v0.3 retains the 72-cell estimator benchmark and adds the SCR consequence design/results.
- [x] Figure 2 caption now describes the SCR downstream result.
- [x] Figure captions v3 drafted.
- [x] v0.4 invariant test added.
- [x] Main-text discussion explicitly answers the “use each trap check as an occasion” objection.
- [x] MCP and empirical SCR stopping decisions remain visible.
- [x] Handling is treated as one possible source of state change, not an inferred cause.
- [x] Current `secr` detector/occasion/reduction semantics rechecked against CRAN documentation; final prose consistency remains.

## Figures

- [x] Figure 1 observation-process geometry retained.
- [x] Figure 2 replaced by stationary-control + empirical-transition SCR consequence panels.
- [x] Figure 3 held-out validation retained.
- [x] Figure 4 denominator/span context retained.
- [x] Figure workflow regenerated PNG/PDF successfully.
- [x] Human visual check of final Figure 2 typography, axes, 10% reference band and PRE/POST direction.

## Reproducibility package

- [x] Primary SCR consequence R script copied onto the paper branch.
- [x] Frozen consequence JSON and replicate CSV copied onto the paper branch.
- [x] Design, empirical-scale benchmark and mixture-theory notes included.
- [x] Anonymous review-package builder upgraded to v3.
- [x] Review package v3 build passes its tests.
- [x] Repository-wide frozen-paper checks pass at the current v0.4 state.
- [ ] Create final versioned archival release / persistent repository identifier.

## Author / submission metadata

- [ ] Final author list and affiliations.
- [ ] Author-contribution statement.
- [ ] Funding statement.
- [ ] Conflict-of-interest statement.
- [x] AI-assisted development disclosure remains in Methods.
- [ ] Final anonymous title-page/manuscript split.

## Current decision

**Scientific status:** the specific weakness identified in v0.3—absence of a demonstrated downstream consequence—has been addressed by the empirically anchored SCR benchmark with stationary negative controls and mirrored state ordering.

**Pre-submission status:** **HOLD. Do not send the enquiry yet.** The scientific/literature and Figure 2 checks are now complete; the remaining blockers are final prose consistency, author metadata and archival-release details.

**Analysis policy:** do not open new same-data biological-effect searches. The failed MCP and two-species empirical SCR gates remain binding. A PEMA-only post-stop fit, if retained at all, must remain explicitly exploratory and cannot alter the primary inference.
