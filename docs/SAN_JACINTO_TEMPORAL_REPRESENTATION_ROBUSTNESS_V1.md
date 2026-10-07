# Temporal representation robustness v1

Date: 2026-10-07

## Why this test is needed

FIRST-only strongly shifts every species toward the EARLY check by construction. It is therefore not sufficient to interpret stronger RA3 aggregation under FIRST-only as biological synchrony.

This post-result robustness compares four deterministic representations and an ensemble:

1. ALL capture events;
2. FIRST capture per identifiable individual-night;
3. LAST capture per identifiable individual-night;
4. INDIVIDUAL-NIGHT NORMALIZED: each identifiable animal-night contributes total weight 1, split equally among the unique check bins in which it was captured;
5. RANDOM: one capture chosen per identifiable individual-night, repeated across 100 seeded representations.

Unknown-identity rows are retained as separate capture events rather than guessed to be repeat observations.

## Readout

For deterministic lanes, use exact RA3 enumeration with community Czekanowski overlap for each of 32 grid-seasons.

For RANDOM, use 999 RA3 permutations per grid-season for each of 100 representations and report the distribution of the number of aggregated / segregated / null grid-seasons.

## Interpretation

- FIRST high but LAST low: likely edge-censoring artifact.
- FIRST and LAST both high, but RANDOM/NORMALIZED low: order censoring creates apparent synchrony.
- FIRST/LAST/RANDOM/NORMALIZED all retain aggregation and no segregation: coarse relative activity overlap is robust to repeat-capture representation even though absolute activity profiles are not.
