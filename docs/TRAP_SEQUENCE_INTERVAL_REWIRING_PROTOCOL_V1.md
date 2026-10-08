# Trap-sequence interval-rewiring uncertainty audit v1

Date: 2026-10-08

**Status:** Post-result exploratory audit. The original pooled ordering, early/middle vs middle/late differences and KR→LAPM contrast were already inspected before this protocol was written. This cannot be treated as a prospective confirmation.

## Claim at risk
The existing synthesis calls the six-species detector-local sequence network temporally reconfiguring because only 9/15 dyad signs agree between EARLY→MIDDLE and MIDDLE→LATE. The change could arise from sampling uncertainty, especially for sparse heterospecific transitions.

## Frozen audit before running
- Read the checksum-frozen San Jacinto CSV; retain grid-dates with all three time-bin labels observed, and reconstruct all 49 traps per check as EMPTY/focal species.
- Exclude ambiguous or nonfocal trap-check records, matching the fixed-effect comparison population.
- Use the same trap × grid × trapping-bout × check-pair date-shuffle reference as the original transition-network route; use only strata with at least two dates.
- For each 30 directional heterospecific species transitions and each of two adjacent check pairs, aggregate observed and conditional random-pair expected counts.
- For each unordered dyad A/B and interval, define smoothed log directional asymmetry as log[(O_AB+0.5)/(E_AB+0.5)] − log[(O_BA+0.5)/(E_BA+0.5)].
- Resample the 96 grid×bout blocks with replacement 5,000 times, seed 20261008, maintaining both intervals within each block. Report the percentile CI for the change in log directional asymmetry between the two intervals.
- Report the descriptive number of dyad signs conserved and its bootstrap distribution, and multiplicity-aware exploratory BH q across all 15 interval differences.
- Specifically compare KR→LAPM observed/expected early→middle vs middle→late; report the paired bootstrap CI for the difference in smoothed log O/E.
- Repeat with only original trapping bouts containing exactly three recorded capture dates.

**Interpretation gates:** A shift in the optimum rank or 9/15 conserved signs alone is not evidence of true ecological network reorganization. If few or no dyads show an interval contrast with interval-excluding-zero CI after multiplicity adjustment, remove 'reconfiguration' from the strong ecological conclusion; call it a descriptive difference between sparse interval estimates. Even strong interval dependence does not identify natural competition, scent, or release effects.

## Critical design limitation
A recorded EARLY/MIDDLE/LATE label in a grid-night guarantees some captures in that bin, but not that every detector was definitely operational. EMPTY is a protocol-based reconstruction. The original full schedule is not available for all grid-dates; this audit is conditional on the complete-bin subset and does not establish untreated animal behaviour.