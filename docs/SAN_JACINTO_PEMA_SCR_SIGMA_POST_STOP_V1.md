# PEMA SCR sigma FIRST-versus-LAST post-stop exploration v1

Date: 2026-10-01

Status: post-stop exploratory analysis.

The confirmatory downstream SCR programme required both PEMA and PEER to pass an effect-blind session-support gate. PEER failed that gate, so the confirmatory programme stopped before sigma was opened. This analysis does not alter that decision.

Its sole purpose is to provide an empirical companion to the generative SCR simulation using the one species that independently satisfied the frozen support rule: PEMA (*Peromyscus maniculatus*), with 19 eligible sessions across five grids.

## Data reduction

For every eligible species x grid x bout session and each individual x date:

- FIRST retains the earliest valid nocturnal capture.
- LAST retains the latest valid nocturnal capture.
- source-row order breaks exact time ties.

The two reductions use the same frozen session set and the same observed individual-nights; only the selected detector may differ.

## Models

Primary exploratory model:

- detector: multi
- detection function: half-normal
- likelihood: conditional
- g0 ~ b + grid + bout
- sigma ~ 1
- 100 m trap-buffer mask

The execution is now intentionally limited to this prospectively designated primary model. Earlier workflow attempts were cancelled before any sigma output was written, so no FIRST/LAST effect was inspected before dropping the two non-rescuing sensitivity fits for computational tractability.

The reported comparison is sigma_LAST / sigma_FIRST and its relative change. The previously written 10% threshold is used descriptively only.

## Interpretation boundary

A material PEMA difference can support the claim that the aggregation rule is capable of changing a fitted spatial scale in this data set. It cannot replace the failed two-species confirmatory gate, establish a universal direction of bias, or determine whether FIRST or LAST is biologically preferable.
