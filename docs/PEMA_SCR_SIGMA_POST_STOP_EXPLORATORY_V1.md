# PEMA-only SCR sigma sensitivity after the programme stop — exploratory v1

Date: 2026-10-03

Status: post-stop exploratory analysis explicitly authorized after the prospectively frozen two-species programme stopped.

## Binding prior decision

The original confirmatory downstream programme remains:

`stop_scr_sigma_sensitivity_not_estimable`

because the frozen rule required both PEMA and PEER to pass the session-support gate. PEMA passed with 19 eligible sessions across 5 grids; PEER had only 2 eligible sessions and failed.

Nothing in this analysis changes that decision.

## Purpose

Use the species that independently passed the original effect-blind support gate to ask a narrower descriptive question:

> Among the 19 already-frozen PEMA sessions, how much does pooled SCR sigma differ when a nightly multi-catch history retains the FIRST versus LAST capture location?

This is supporting empirical evidence for the simulation, not a replacement confirmatory test.

## Data and sessions

Source: Figshare article 18295520 v1, file 33058799, frozen SHA256
`ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301`.

Eligible PEMA sessions are read verbatim from
`validation/san_jacinto_scr_sigma_v1/eligible_sessions_v1.csv`.

No session is added or removed after FIRST/LAST effects are opened.

## Nightly reductions

Within each eligible session, individual, and date:
- FIRST = earliest valid nocturnal capture;
- LAST = latest valid nocturnal capture;
- source row order resolves exact time ties.

FIRST and LAST have identical sessions, individuals, occupied dates, and trap arrays; only the retained detector may differ.

## Model

R package `secr`, detector type `multi`, half-normal detection function, conditional likelihood.

Primary exploratory model:
- `g0 ~ b + grid + bout`
- `sigma ~ 1`

The session covariates grid and bout are the original San Jacinto identifiers.

Mask: 100 m trap buffer, 5 m mask spacing, identical between FIRST and LAST.

Sensitivity model:
- `g0 ~ grid + bout`
- `sigma ~ 1`

## Outputs

For FIRST and LAST:
- pooled sigma estimate and 95% interval;
- log likelihood / AIC;
- fit status.

Derived descriptive contrasts:
- `sigma_ratio = sigma_LAST / sigma_FIRST`;
- `relative_change = sigma_LAST / sigma_FIRST - 1`.

The previously frozen 10% materiality threshold is shown only as context. It is **not** used to retroactively pass or fail the stopped two-species programme.

## Claim boundary

Allowed wording:
- "In a post-stop exploratory fit of the independently eligible PEMA sessions, FIRST and LAST nightly reductions produced [X] difference in sigma."

Not allowed:
- "The preregistered SCR sigma test passed";
- "both species show sigma sensitivity";
- any use of the PEMA-only result to alter PEER eligibility or the original stop.
