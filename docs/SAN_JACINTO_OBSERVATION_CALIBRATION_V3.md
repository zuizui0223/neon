# San Jacinto observation-process calibration for SCR downstream simulation — v3

Date: 2026-10-03

Status: frozen before v3 calibration outcomes are opened.

## Purpose

V1 showed that temporal representation can materially alter fitted SCR sigma. V2 preserved that result under observation-process-based selection, but its best cells reproduced repeat-capture and shift frequencies better than the empirical changed-night distance distribution.

V3 therefore performs **calibration only**. No SCR sigma model is fitted anywhere in this stage.

A downstream v3 sigma experiment is authorized only if at least one parameter cell passes all pre-specified observation-process tolerances on an independent validation seed set.

## Empirical targets

The targets were opened before this design from the two held-out Cricetidae:

### PEMA
- repeat-capture fraction among all captured individual-nights: 0.398;
- >=1-spacing shift fraction among repeat-capture nights: 0.7258;
- median all-repeat first-to-last distance: 8.84 m;
- median changed-night first-to-last distance: 14.0 m.

### PEER
- repeat-capture fraction: 0.355;
- >=1-spacing shift fraction: 0.6916;
- median all-repeat first-to-last distance: 6.25 m;
- median changed-night first-to-last distance: 12.5 m.

The v3 acceptance gate is defined from these observed ranges and a modest frequency tolerance; no downstream sigma estimate enters the gate.

## Protocol model

- 7 x 7 multi-catch live-trap array;
- 6.25 m trap spacing;
- three checks per night;
- three consecutive nights;
- baseline detection generated with `secr::sim.capthist`, detectfn = HN;
- baseline activity centre fixed within the closed bout and restored at the start of every night.

### Release-centred transient state

The field protocol released animals at the detector where they were captured.

After each simulated capture:

- with probability `p_response`, the animal enters a transient post-release spatial state;
- its transient centre is the **capture/release detector coordinate plus an isotropic Gaussian displacement**;
- the displacement component SD is `handling_rms / sqrt(2)`, so the radial RMS displacement equals `handling_rms`;
- the transient centre applies to subsequent checks until another capture updates the state or the night ends;
- with probability `1-p_response`, the animal is returned to its baseline activity centre for subsequent checks.

This is a sensitivity model, not a claim that real animals literally acquire a new activity centre after handling.

## Candidate grid

- baseline sigma: 3.125, 4.0, 5.0, 6.25 m;
- g0: 0.12, 0.16, 0.20;
- no-response control: handling RMS = 0, p_response = 0;
- response RMS: 6.25, 12.5, 18.75, 25.0 m;
- p_response: 0.10, 0.25, 0.50, 0.75.

Total candidate cells: 204.

Population density is set to 60 animals/ha to reduce Monte Carlo noise in observation-process summaries. Density is not a calibration target.

## Stage A1 — search

Each of the 204 cells is simulated for 12 independent replicates.

No SCR model is fitted.

For each cell, pooled across replicates, calculate:

- repeat-capture fraction = total repeat-capture individual-nights / total captured individual-nights;
- shift fraction = total >=1-spacing shifts / total repeat-capture individual-nights;
- pooled median all-repeat first-to-last distance;
- pooled median changed-night first-to-last distance.

A ranking score is used **only** to choose cells for independent validation:

[
S =
((q_{repeat}-0.3765)/0.05)^2 +
((q_{shift}-0.70868)/0.05)^2 +
((m_{all}-7.5444)/2.5888)^2 +
((m_{changed}-13.25)/1.5)^2.
]

The 12 lowest-score cells advance to Stage A2.

## Stage A2 — independent calibration validation

The 12 A1 cells are re-simulated with a disjoint seed range for 50 replicates per cell.

Again, no SCR model is fitted.

A cell passes only if **all four** validation conditions hold:

1. repeat-capture fraction in [0.3265, 0.4265];
2. >=1-spacing shift fraction in [0.65868, 0.75868];
3. pooled all-repeat median first-to-last distance in [6.25, 8.84] m;
4. pooled changed-night median first-to-last distance in [12.5, 14.0] m.

These bounds cannot be relaxed after validation outputs are opened.

## Decision rule

- If zero cells pass: `stop_v3_no_observation_process_match`.
- If one or more cells pass: `authorize_v3_downstream_freeze`.

If more than three cells pass, retain the three passing cells with the lowest validation ranking score for a later downstream experiment. Selection remains based only on observation-process summaries.

## Downstream boundary

This workflow must report:

- `scr_models_fit = 0`;
- `empirical_sigma_opened = false`;
- `v1_v2_sigma_results_not_used_for_v3_cell_selection = true`.

No CHECK/FIRST/LAST sigma is generated in v3 calibration.

A separate design must be committed after this calibration result and before any downstream v3 sigma simulation is run.
