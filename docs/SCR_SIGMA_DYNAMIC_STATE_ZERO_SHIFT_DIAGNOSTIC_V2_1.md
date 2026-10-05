# Dynamic-state SCR zero-shift diagnostic replication v2.1

Date: 2026-10-05

Status: post-failure diagnostic replication of the pre-specified v2 negative-control gate. Non-zero shift cells remain frozen and are not used to tune this design.

## Trigger

The first v2 run completed all simulations but failed its pre-specified negative-control gate because the maximum absolute median relative sigma bias across the nine zero-shift method × sigma cells was 0.1022, just above the frozen 0.10 limit. The offending cell was LAST at generating sigma = 12.5 m (23/24 successful fits; median relative bias +10.22%). The paired median LAST/FIRST ratio in that cell was 1.0509.

## Purpose

Determine whether the 10.22% null-cell result is a stable property of the sequential generator/analysis or Monte Carlo variation from 24 replicates.

This diagnostic contains **only zero-shift data**. It cannot inspect or tune any non-zero state-shift effect.

## Generator

Use the same stationary sequential generator as v2 with shift multiplier exactly zero:

- 7×7 multi-catch trap grid;
- spacing 6.25 m;
- 3 nights × 3 independently generated checks;
- one fixed activity centre per animal throughout each night and across checks;
- HN detection, g0 = 0.15;
- density = 60 animals ha^-1;
- 100 m buffer;
- true sigma = 6.25, 12.5, 25 m.

The same records are encoded as CHECK, FIRST and LAST and fitted with conditional-likelihood HN SCR, g0 ~ b, sigma ~ 1.

## Replication

- independent seed: 20261005;
- 96 replicates per true-sigma cell;
- no non-zero shift cells.

The increased replication is chosen only to reduce Monte Carlo uncertainty in the null gate after the 24-replicate run landed 0.22 percentage points beyond the frozen threshold.

## Frozen decision

The original v2 negative-control criterion is retained unchanged:

- pass if maximum absolute median relative sigma bias across CHECK/FIRST/LAST × the three true sigma values is < 0.10;
- fail otherwise.

Also report paired median LAST/FIRST ratios as a descriptive equivalence diagnostic.

If this independent null-only replication fails the same 10% gate, v2 non-zero cells remain uninterpretable and the dynamic-state robustness lane is stopped. If it passes, the original run-1 failure remains documented, but the larger null replication may be used to classify the 10.22% result as unstable Monte Carlo noise rather than a reproducible null bias.

No empirical real-data sigma is opened.
