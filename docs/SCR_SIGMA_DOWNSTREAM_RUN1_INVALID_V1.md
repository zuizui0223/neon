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

An initial hypothesis was a mismatch between numeric simulated detector
indices and the default alphanumeric detector labels from `make.grid`.
Current `secr` documentation shows that this hypothesis is not sufficient:
for `fmt="trapID"`, the fourth capture column is the **numeric detector
index (row number)**, not the detector row name. The numeric-ID change made
during debugging is therefore only a harmless normalization and must not be
reported as the established root cause.

A diagnostic rerun now persists the CHECK/FIRST/LAST exception messages so the
failure can be localized from direct evidence before any further scientific
interpretation.

## Repair status

- detector identifiers have been normalized to numeric row-dominant labels;
- this does not alter detector geometry, seeds, data-generating parameters,
  estimands, or thresholds;
- the exact implementation failure remains **under diagnosis** until the
  diagnostic rerun exposes the `make.capthist` exception text;
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
