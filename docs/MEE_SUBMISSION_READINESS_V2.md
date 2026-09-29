# MEE submission-readiness checklist — live-trap aliasing v2

Date: 2026-09-30

## Scientific core

- [x] Methodological approach, not biological case study, is central.
- [x] Temporal positional aliasing is defined as an observation-process diagnostic, not as a movement model.
- [x] Deterministic movement/MPD sensitivity bounds implemented and verified.
- [x] Generic diagnostic accepts arbitrary individual / occasion / time / coordinate columns.
- [x] Material spatial scale is user-defined and chosen before interpretation.
- [x] Prospectively held-out empirical validation passed in two Cricetidae species.
- [x] Spatial replication criterion passed in 7/7 PEMA and 3/3 PEER eligible grids.
- [x] Repeat-conditioned denominator limitation is explicit.
- [x] All-individual-night observational lower bounds are reported.
- [x] Informative repeat-observation failure mode is demonstrated by simulation.
- [x] Prospectively frozen downstream MCP analysis was stopped when support gate failed.
- [x] No home-range effect is claimed.
- [x] No sex-specific or universal small-mammal claim is made.

## Simulation / benchmark

- [x] 72-cell simulation grid frozen.
- [x] 400 replicates per cell.
- [x] Non-informative repeat observation shows near-zero bias.
- [x] Mean Wilson coverage is near nominal under non-informative repeat observation.
- [x] Span-enriched repeat observation produces positive bias.
- [x] Span-depleted repeat observation produces negative bias.
- [x] All-night directly observed fraction had zero lower-bound violations.
- [x] Simulation benchmark workflow completed successfully.

## Empirical validation

- [x] Source file checksum frozen.
- [x] Effect lock frozen before held-out PEMA/PEER outcomes were opened.
- [x] Primary material scale fixed at one 6.25-m trap spacing.
- [x] Frozen 25% materiality threshold used.
- [x] Wilson lower-bound rule used.
- [x] Grid-level spatial replication rule used.
- [x] Workflow provenance and artifact digest frozen.
- [x] Discovery heteromyids excluded from confirmatory inference.

## Generic usability

- [x] Generic command-line diagnostic implemented.
- [x] Generic synthetic CSV example checked in.
- [x] Expected generic output checked in.
- [x] Generic example has passed its dedicated workflow.
- [x] Standard unit test verifies checked-in example.
- [x] Usage documentation included.
- [x] Minimal dependency file included.
- [x] MIT open-source license included.

## Literature and novelty

- [x] SCR/SECR detector-semantics literature audited.
- [x] Interval-trapping timing literature audited.
- [x] Continuous-time SECR literature audited.
- [x] Temporal aggregation / thinning positioned as existing methods, not novelty.
- [x] Triangle inequality explicitly not claimed as mathematical novelty.
- [x] Novelty narrowed to a lightweight scale-aware pre-analysis diagnostic plus downstream sensitivity bounds.
- [x] Empirical magnitude distinguished from general applicability.

## Manuscript

- [x] v0.2 manuscript drafted.
- [x] Approximate manuscript length ~4,900 words before final author statements.
- [x] Numbered 1–4 abstract drafted.
- [x] Simulation appears before empirical validation.
- [x] Results and Discussion include denominator-selection boundary.
- [x] Continuous-time alternatives discussed.
- [x] Downstream MCP non-estimability transparently reported.
- [x] Figure 1–4 callouts and captions drafted.
- [x] Data availability section drafted.
- [x] Ethics statement drafted.
- [x] References verified for core cited methods.
- [ ] Final author list / affiliations.
- [ ] Author-contribution statement.
- [ ] Funding statement.
- [ ] Conflict-of-interest statement.
- [ ] Final AI-tool disclosure if required by current journal policy.

## Figures

- [x] Figure 1 observation-process geometry rendered.
- [x] Figure 2 simulation benchmark rendered.
- [x] Figure 3 prospective held-out validation rendered.
- [x] Figure 4 denominator and span magnitude rendered.
- [x] PNG and PDF versions committed.
- [x] Figure-rendering workflow completed successfully.
- [x] Figure captions drafted.
- [ ] Final editorial polish after co-author review.

## MEE fit / submission

- [x] Research Article chosen as intended article type.
- [x] Method centrality aligns with current MEE scope.
- [x] Computational method evaluated with simulation.
- [x] Generic applicability is explicit.
- [x] Pre-submission enquiry drafted.
- [x] Manuscript is comfortably below the journal word-count ceiling.
- [ ] Send pre-submission enquiry.
- [ ] Incorporate editor response.
- [ ] Create final anonymous title-page/manuscript pair.

## Reproducibility package

- [x] Clean paper branch separated from failed exploratory programmes.
- [x] Review-package manifest defined.
- [x] Review-package builder implemented.
- [x] Raw third-party data excluded from package; public DOI/source retained.
- [ ] Review-package builder rerun successfully after the corrected simulation-module docstring.
- [ ] Create versioned archival release / persistent repository identifier.
- [ ] Insert final repository/archive identifier into Data Availability statement.

## Current decision

**Scientific status:** proceed toward MEE pre-submission enquiry.

**Do not add more post-hoc biological effect analyses.**

The remaining work is packaging, author metadata, editorial polishing, and editor feedback—not searching for a larger biological effect.
