# NEON capture-space persistence: source-free identifiability test — 28 October 2026

**Completed: a mathematical counterexample, NOT a new NEON biological effect.** This is part of the ONE unified NEON mammal spatial macroecology draft (PR #23). Do not alter original endpoint gates or use these synthetic results to support submission.

## Keep the verified ecology intact

The original corrected >=3-genus capture-station recurrence: 58 seasonal contrasts / 14 physical sites, 11/14 sites positive, equal-site Z=+0.795. Post-result exploratory exactly-two-genus recurrence: 150 informative seasonal contrasts / 30 physical sites, 25/30 sites positive, Z=+0.615. A 17-site nonoverlap sensitivity had 15/17 positive and Z=+0.760. All come from historical NEON RELEASE-2026, not a never-inspected future release.

The all-six-night *recorded* station restriction retains a positive association, but the strict trapStatus 4/5/6 source gate STOPPED with just 18/158 comparisons. Recorded re-encounter differs between Microtus and Peromyscus by -23.5 percentage points across seven matched sites but is NOT genus detection p. Source-only firstnight fate audit found 615 records including 391 raw post-2017 "processed" values: they are not blank and do not individually certify live release. Confirmed-explicit-release source support remained 1/7 sites, STOP.

## Exact observation-only counterexample

Consider m stations each recording exactly one of two genera in BOTH seasons. Hold the recorded genus-1 station count a constant in each season (and thus fixed genus station totals and station genus richness). A season's size-a selected set S has probability proportional to exp(beta * |S intersect H|), with H a fixed set of stations with higher genus-1 **observation** affinity. The two seasons are INDEPENDENT samples given the same observation affinity. No returning animals, stable territories, or true-use memory is introduced.

This is a legal singleton-column special case of the existing exact two-row uniform fixed-margin null (analysis/neon_exact_two_row_fixedmargin_v1.py). The uniform null corresponds to beta=0. The finite weighted subset law is Fisher's noncentral hypergeometric law; the calculations use exact finite sums, not MCMC.

If p_i is each station's marginal chance of the genus-1 singleton record, then, for independent seasons with the same p_i:

    E[O] - E_uniform[O] = 2 * sum_i (p_i - a/m)^2 >= 0.

This is STRICTLY positive whenever stationary recorded-genus affinities differ among stations. Thus a positive conditional capture-position Z is possible with independently assembled seasons, even when there is no persistent true-use spatial state. Stable ecological habitat preferences and stable capture propensities can create identical observed genus-by-station distributions under this design. The counterexample proves non-identifiability from the binary capture matrix alone, not which mechanism occurred in NEON.

## Reproducible synthetic calculation

Illustration: 100 singleton stations, 50 genus-1 labels per season, half the stations relatively favorable for recording genus 1. No historical source rows used.

| Relative recording odds high/low exp(beta) | Observed genus-1 probability high/low | Expected Z under uniform fixed margins |
|---:|---:|---:|
| 1.00 | .500 / .500 | +0.000 |
| 1.65 | .563 / .437 | +0.157 |
| 2.72 | .624 / .376 | +0.609 |
| 4.48 | .681 / .319 | +1.304 |

This resemblance to an empirical aggregate NEON Z is coincidental/illustrative and MUST NOT be construed as a calibrated NEON detection-bias estimate. The real NEON singleton counts, seasonal margins and site dependence are different.

Recompute with:

    python -m analysis.neon_capture_template_identifiability_v1
    python -m unittest discover -s tests -p test_neon_capture_template_identifiability_v1.py -v

Unit tests include exact direct weighted subset enumeration and cross-check of null moments against the repository's pre-existing two-row fixed-margin implementation.

## Ecological implication and next genuine discriminator

The observed result is **conditional seasonal recurrence of genus-associated capture locations among different detected animal tags**. It is not yet proven persistence of detection-corrected mammal space-use niches. The next mechanism test needs a *source-dated independent observation channel* at the same genus x station x bout grain (e.g. independent detection sampling) and/or independently measured station microhabitat. TrapStatus=4/5 is itself a capture-related outcome; the fate label "processed" is not an independently confirmed live release. Neither should be silently promoted to independent detection truth.

Freeze the sampling grain, independent physical-site/season holdout, habitat/detection covariates and scoring **before** opening any future never-inspected capture responses. Compare held-out latent-use predictions with versus without habitat predictors after genus-by-station detection is separately identified. If no independent detection/use outcome can be aligned to the station, do not fit an unidentifiable "habitat versus catchability" mechanism from these two-genera binary capture matrices. Keep the single draft in SUBMISSION HOLD and do not relax any failed 18/158, 79/80, 5/8 or 12/58 empirical gate.

No effect values or source identities in the earlier ecology receipts have been reopened or changed by this synthetic test.

### Related source receipts
- results/neon_exact_two_genus_ecological_receipt_20261025.json
- results/neon_macro_six_night_trapStatus456_SOURCE_STOP_20261026.json
- results/neon_genus_firstnight_reencounter_outcome_20261026.json
- results/neon_firstnight_original_fate_source_20261028.json
- results/neon_fate_2017plus_unmapped_processed_source_receipt_20261028.json
