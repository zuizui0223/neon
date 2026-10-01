# SCR sigma downstream run-1 invalidation note

Date: 2026-10-01

Status: **implementation-invalid; not a scientific result**

The first persisted output of `analysis/simulate_scr_sigma_downstream_v1.R`
(commit `5327e07da41c0c4db896cfdc9b6a49dba4f51a11`) reported zero
successful CHECK/FIRST/LAST fits across all 144 simulated datasets.

This was not evidence that the SCR models were unestimable and is not a null
downstream result.

## Failure localization

The failure occurred during capture-history construction, before any sigma
estimate was produced. The first run did not persist the underlying
`make.capthist` exception text, so its precise cause cannot be reconstructed
from that result file alone.

The leading hypothesis is a detector-identifier mismatch. There is a
version-specific documentation/implementation discrepancy in current
`secr`: the `make.capthist` help page describes the fourth
`fmt="trapID"` field as a numeric detector index, whereas the current
`make.capthist.R` implementation matches that field against
`rownames(traps)`. Current `make.grid` defaults to `ID="alphay"`, yielding
alphanumeric labels such as `A1`, while the simulation emitted numeric
detector indices `1..49`.

The repair therefore makes the trap row names explicitly numeric
(`ID="numy", leadingzero=FALSE`) so both documented-index and implemented-ID
interpretations coincide. A diagnostic rerun also persists the
CHECK/FIRST/LAST exception messages; these provide the direct confirmation of
the failure mode before the repaired output is interpreted scientifically.

## Repair status

- detector identifiers have been normalized to numeric row-dominant labels;
- this does not alter detector geometry, seeds, data-generating parameters,
  estimands, or thresholds;
- direct confirmation is pending from the diagnostic rerun that records the
  original `make.capthist` exception text;
- no sigma estimate from run 1 exists.

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
