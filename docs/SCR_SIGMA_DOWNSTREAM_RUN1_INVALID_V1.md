# SCR sigma downstream run-1 invalidation note

Date: 2026-10-01

Status: **implementation-invalid; not a scientific result**

The first persisted output of `analysis/simulate_scr_sigma_downstream_v1.R`
(commit `5327e07da41c0c4db896cfdc9b6a49dba4f51a11`) reported zero
successful CHECK/FIRST/LAST fits across all 144 simulated datasets.

This was not evidence that the SCR models were unestimable and is not a null
downstream result.

## Root cause

`secr::make.grid()` uses alphanumeric detector row names by default
(`A1`, `A2`, ...). The simulator encoded detections as numeric detector
indices `1..49`. `make.capthist(..., fmt="trapID")` matches the fourth
capture column to detector row names, so the simulated detector identifiers
did not match the `traps` object.

The bug occurred before any sigma estimate was produced.

## Repair

The detector grid is now constructed with numeric row-dominant IDs and no
leading zero padding:

`ID = "numy", leadingzero = FALSE`

This preserves the frozen detector geometry, data-generating process,
parameter grid, seeds, estimands, and thresholds. It changes only the
identifier representation needed to connect simulated detections to the
`secr` capture-history object.

The same identifier repair was applied to the exact-protocol consequence
benchmark and the PEMA post-stop exploratory script because they used the same
numeric detector-index convention.

## Fail-closed change

The downstream-simulation workflow now requires at least one successful fit
for each of CHECK, FIRST, and LAST. A file with the expected row count but
zero successful model fits can no longer pass CI as a valid result.

## Claim boundary

Until a repaired run completes:

- downstream sigma effect: **not yet estimated**;
- stationary-SCR negative control: **not yet evaluated**;
- empirical PEMA sigma: **not yet opened successfully**;
- the frozen two-species empirical gate remains stopped.

The run-1 JSON/CSV are retained only for provenance.
