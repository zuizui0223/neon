# San Jacinto SCR sigma calibrated simulation v2 — interpretation

Date: 2026-10-03

Status: completed; informative but not yet manuscript-final.

## Calibration result

The v2 calibration selected three cells using observation-process summaries only; no downstream sigma estimate entered cell selection.

The empirical targets were:

- repeat-capture fraction = 0.3765;
- >=1-spacing shift fraction among repeat nights = 0.70868;
- median changed-night first-to-last distance = 13.25 m.

Selected cells:

1. sigma 4 m, g0 0.20, handling RMS 12.5 m, response probability 0.50:
   repeat 0.327, shift 0.725, changed-night median 8.84 m.
2. sigma 5 m, g0 0.16, handling RMS 25 m, response probability 0.25:
   repeat 0.359, shift 0.762, changed-night median 8.84 m.
3. sigma 4 m, g0 0.16, handling RMS 12.5 m, response probability 0.25:
   repeat 0.300, shift 0.718, changed-night median 7.54 m.

Thus repeat-capture and shift frequencies were reasonably close, but the changed-night distance distribution remained too short relative to the empirical 12.5–14 m species medians. V2 is therefore not a sufficiently tight San Jacinto calibration.

## Downstream result

Twenty new replicates were generated for each selected cell. All three representations had 85% fit success in every selected cell.

### Selected cell 1

Median relative sigma error:
- CHECK +19.1%;
- FIRST +3.8%;
- LAST +9.9%.

Median representation contrasts:
- FIRST/CHECK -12.3%;
- LAST/CHECK -2.7%;
- LAST/FIRST +9.3%.

The 10% materiality threshold was exceeded by 47.1% of fitted replicates for LAST versus FIRST.

### Selected cell 2

Median relative sigma error:
- CHECK +16.1%;
- FIRST -1.8%;
- LAST +32.1%.

Median representation contrasts:
- FIRST/CHECK -13.3%;
- LAST/CHECK +9.6%;
- LAST/FIRST +20.7%.

The 10% threshold was exceeded by:
- 70.6% of fitted replicates for FIRST versus CHECK;
- 52.9% for LAST versus CHECK;
- 64.7% for LAST versus FIRST.

### Selected cell 3

Median relative sigma error:
- CHECK +5.4%;
- FIRST -4.2%;
- LAST +6.2%.

Median representation contrasts:
- FIRST/CHECK -2.8%;
- LAST/CHECK +4.2%;
- LAST/FIRST +7.4%.

The 10% threshold was exceeded by 41.2% of fitted replicates for LAST versus FIRST.

## What v2 supports

1. Downstream sigma sensitivity survives observation-process-based cell selection; it is not confined to the broad v1 grid.
2. The sensitivity is conditional rather than universal. One selected cell had a clear median LAST/FIRST effect (>20%), whereas two had median effects below 10%.
3. Treating each trap check as an occasion is not automatically an unbiased solution. CHECK median sigma error was +16–19% in the two best calibration cells, consistent with transient post-capture states being absorbed into the static SCR spatial scale.
4. FIRST tended to be less inflated than LAST in the strongest selected cell, as predicted if later captures are more exposed to the post-release state.

## Why v2 should not yet replace Figure 2

The calibration score traded off three summaries and allowed cells with too-short changed-night displacement to rank highly. In addition, only 12 calibration replicates per cell made selection vulnerable to Monte Carlo noise; Stage-B observation summaries drifted from Stage-A values.

The next calibration should therefore use a hard pre-effect acceptance gate rather than a weighted score, and should validate calibration on a second independent seed set before any sigma model is fitted.

## Next methodological refinement

A more faithful post-release transition should be centered on the **capture/release detector**, not on the baseline activity centre. This matches the field protocol: the animal is physically released where it was caught, after which a transient displacement can occur.

The next stage is calibration only. It will search and independently validate parameter cells against four empirical observation summaries, with no SCR sigma fitting. Downstream fits will be authorized only if at least one cell passes all fixed calibration tolerances.
