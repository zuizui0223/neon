# San Jacinto SCR sigma downstream simulation pilot v1

Date: 2026-10-01

Status: targeted exploratory simulation on the existing SCR-sigma branch.

## Why this exists

The empirical FIRST-versus-LAST SCR analysis was stopped before any sigma estimate was opened because the pre-specified two-species support gate failed: PEMA had 19 eligible sessions, whereas PEER had only 2. That stop remains in force.

The current MEE manuscript therefore lacks a direct demonstration of how within-night positional aliasing can affect a downstream spatial parameter. This pilot asks that question by simulation rather than by relaxing the empirical gate.

## Empirical calibration targets

The data-generating process is calibrated only to already-opened San Jacinto observation-process summaries, not to any downstream sigma estimate.

Pooled across the two held-out Cricetidae:

- valid captured individual-nights: 1,520
- repeat-capture individual-nights: 592
- repeat-observation fraction: 0.389
- changed trap among repeat nights: 426 / 592 = 0.720
- overall repeat-night median FIRST-to-LAST span: 8.84 m
- changed-night median FIRST-to-LAST span: 12.5 m

Species-specific changed-night medians are approximately 14 m (PEMA) and 12.5 m (PEER).

A stationary single-scale SCR process could not simultaneously reproduce the observed combination of many same-trap repeat captures and a broad positive displacement tail. The empirical-like pilot therefore includes a transient local recapture response: after a capture, the detector used on the immediately following check receives a multiplicative detection boost. This is deliberately analogous to a local transient behavioural response (Bk) in SECR.

## Simulated protocol

- detector layout: 7 x 7
- detector spacing: 6.25 m
- 3 nights per session
- 3 checks per night
- 4 independent sessions per replicate
- 300 activity centres per session
- true half-normal sigma: 11 m
- baseline g0: 0.04
- empirical-like transient local recapture factor: 10
- control transient local recapture factor: 1

The empirical-like parameter combination was chosen before downstream sigma fits because it reproduces the opened San Jacinto repeat-observation, changed-trap and span summaries reasonably closely.

Between nights, an explicit zero-effort separator occasion resets the immediate previous-check response.

## Four downstream analyses

Each simulated data set is analysed four ways:

1. CHECK-NAIVE: every trap check is an occasion; g0 ~ 1; sigma ~ 1.
2. CHECK-Bk: every trap check is an occasion; g0 ~ Bk; sigma ~ 1.
3. NIGHT-FIRST: one occasion per night, retaining the first capture; g0 ~ 1; sigma ~ 1.
4. NIGHT-LAST: one occasion per night, retaining the last capture; g0 ~ 1; sigma ~ 1.

All fits use the same half-normal detector model, multi-catch detector type, conditional likelihood, trap geometry and 100 m mask buffer.

## Questions

The pilot is designed to distinguish three possibilities rather than force a positive result.

1. Under the no-dependence control, does nightly collapse primarily reduce information while leaving sigma approximately unbiased?
2. Under the empirically calibrated local dependence, does merely redefining every check as an occasion create a different bias unless short-term recapture dependence is represented?
3. Relative to the dependence-aware check-level fit, do NIGHT-FIRST and NIGHT-LAST change sigma by >=10%, and how often?

The 10% threshold is retained from the earlier sigma-sensitivity design as a descriptive materiality threshold.

## Claim boundary

This simulation does not establish that handling causes the San Jacinto displacement pattern, nor that Bk is the unique biological mechanism. The recapture response is a generative device chosen because it reproduces the observed mixture of same-trap repeats and broad changed-trap spans and is representable in the downstream model.

The real-data PEMA and PEER sigma outcomes remain unopened on this branch. Any later PEMA-only fit must be labelled post-stop exploratory and cannot retroactively replace the failed two-species confirmatory gate.
