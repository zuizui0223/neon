# Within-night trap-sequence rewiring audit — result v1

Date: 2026-10-08  
Status: post-result exploratory; does not replace prior frozen endpoint or establish a causal biological mechanism.

## Decision: no demonstrated temporal rewiring

The previously highlighted change from 14/15 directional consistency in EARLY→MIDDLE to 12/15 in MIDDLE→LATE and only 9/15 sign agreements was descriptive. A new common-support paired uncertainty analysis does **not** support temporal reorganization of the detector-local sequence network.

- 250 grid-nights with captures recorded in EARLY, MIDDLE and LATE; 49 traps per grid.
- 24,408 unambiguous adjacent check-to-check state pairs; 92 invalid/ambiguous/nonfocal pairs excluded.
- 95 grid×trapping-bout blocks; 5,000 paired resamples (seed 20261008).
- On the common-support subset, 10/15 dyads had matching directional signs; bootstrap 95% of matching count was 6–12.
- No dyad had a 95% interval-excluding-zero interval difference (0/15).
- No dyad survived exploratory BH at q < 0.10 (0/15).
- Exact-three-night-bout sensitivity: 11/15 signs matched; 1/15 nominal 95% interval excluded zero, but 0/15 survived BH.

## Focal biological contrast

In the common-support subset, KR→LAPM same-detector observed/expected was 13/20.667 = **0.629** in EARLY→MIDDLE and 14/17.167 = **0.816** in MIDDLE→LATE. The smoothed log-O/E contrast between intervals was **−0.252**, paired bootstrap 95% **−0.778 to +0.245**. This does not establish an interval change.

Exact-three-night-bout sensitivity gives log contrast −0.328, 95% −0.873 to +0.328.

The earlier full-record discovery KR→LAPM O/E 0.719 versus reverse 1.022 is a different pooled reference, not a time-rewiring test.

## Ecological interpretation

The strongest remaining result is a pooled detector-local asymmetric capture sequence with substantial conspecific persistence and partial concordance with experimental body-size dominance. The evidence does not identify:
- change in natural interspecific relationships over hours;
- a static biological dominance hierarchy;
- residual odour versus release, bait, microhabitat, or natural animal interactions;
- a broad neighborhood-scale exclusion zone.

The original spatial niche-segregation classification was unchanged when later within-night recaptures were excluded (8/32 grid-seasons). Temporal aggregation/segregation counts are more representation-sensitive, but no new temporal segregation emerges robustly. Thus one cannot argue that the trapping protocol manufactured the published spatial partitioning or masked a demonstrable temporal partitioning signal.

## Reproducibility

- Code: `analysis/audit_trap_sequence_interval_rewiring_v1.py`
- Frozen analysis design: `docs/TRAP_SEQUENCE_INTERVAL_REWIRING_PROTOCOL_V1.md`
- Original verified public data: Figshare 10.6084/m9.figshare.18295520.v1
- Action run: https://github.com/zuizui0223/neon/actions/runs/37705561797
- Artifact ID: 11519064103 (full 15-dyad result, including exploratory multiple-comparison audit)
- Compact result: `results/trap_sequence_interval_rewiring_summary_v1.json`

The result was opened after the original interval-specific rank changes were seen; nothing here is preregistered or confirmatory.

## Next discriminating evidence

A separate live-trapping dataset with check number, trap identity and species history, or an experimental manipulation of previous occupant/bait/cleaning, is needed to test whether detector-local asymmetric sequence structure reflects a transferable ecological phenomenon rather than this sampling protocol.
