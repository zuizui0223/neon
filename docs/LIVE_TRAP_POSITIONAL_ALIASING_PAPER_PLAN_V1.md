# Live-trap positional aliasing — paper plan v1

Date: 2026-09-29

## Working title

**Repeated within-night live-trap captures reveal positional aliasing in nightly small-mammal locations**

Alternative:

**When is a nightly location a location? Within-night recaptures expose temporal aliasing in live-trap spatial data**

## One-sentence contribution

Repeated-check live trapping can yield multiple valid positions for the same individual within one night; deterministic geometry bounds show how this unresolved within-night span can propagate into movement and population spatial statistics, and a prospectively held-out two-species validation shows that one-trap-spacing-or-greater first-to-last shifts are common among repeat-capture individual-nights.

## What is genuinely new

Not new:
- live trapping can affect capture probability;
- small mammals have within-night activity cycles;
- animals can be recaptured within or across nights;
- trap checking frequency matters;
- triangle inequality itself.

New contribution:
1. formulate the **nightly representative-location problem** explicitly as an observation-process problem;
2. define the observed within-night positional span `delta_t = d(F_t,L_t)`;
3. show deterministic bounds that convert delta_t into maximum sensitivity of downstream movement and mean-pairwise-distance estimates;
4. quantify the magnitude of delta_t in a discovery cohort;
5. prospectively validate material positional aliasing in two held-out Cricetidae species, with spatial replication across trapping grids.

## Confirmatory empirical result

PEMA — *Peromyscus maniculatus*:
- n=485 repeat-capture individual-nights;
- 72.6% shifted >=6.25 m;
- 95% Wilson CI 68.4–76.4%;
- 7/7 eligible grids passed the frozen >25% replication rule;
- median first-to-last distance 8.84 m;
- q90 25.0 m.

PEER — *Peromyscus eremicus*:
- n=107 repeat-capture individual-nights;
- 69.2% shifted >=6.25 m;
- 95% Wilson CI 59.9–77.1%;
- 3/3 eligible grids passed;
- median first-to-last distance 6.25 m;
- q90 19.76 m.

Frozen decision: `authorize_live_trap_positional_aliasing_result`.

## Discovery versus validation

The previously inspected heteromyid cohort is discovery/explanatory only. It motivated the observation-process question and showed that choosing first versus last nightly locations can alter a repeated-night movement estimate.

The confirmatory result is PEMA + PEER only. Their first-to-last outcomes were unopened when the positional-aliasing effect lock was frozen.

## General geometric bounds

For first and last locations F_t and L_t:

`delta_t = d(F_t,L_t)`.

For inter-night movement between nights t and u:

`|d(F_t,F_u) - d(L_t,L_u)| <= delta_t + delta_u`.

For population mean pairwise distance across n paired first/last locations:

`|MPD(F)-MPD(L)| <= 2 mean(delta_i)`.

For standardized packing with common n and null SD sigma_n:

`|z_F-z_L| <= 2 mean(delta_i)/sigma_n`.

These are sensitivity bounds, not estimates of bias and not claims that either first or last location is biologically correct.

## Critical denominator language

The primary proportion is conditioned on **repeat-capture individual-nights**. It must never be described as the proportion of all animal-nights that move one trap spacing.

A separate post-result denominator audit should report:
- all valid individual-nights per held-out species;
- fraction with >=2 captures in that night;
- fraction of all individual-nights for which a >=6.25 m first-to-last shift was directly observed.

This audit is descriptive and cannot change the frozen primary result.

## Protocol-conditioned interpretation

The empirical endpoint is not pure natural movement. It is **protocol-conditioned positional instability** after capture, handling, release and subsequent recapture. That is exactly why it matters as an observation-process diagnostic.

Allowed interpretation:
> For repeatedly captured individuals under this multi-check live-trapping protocol, a single nightly position frequently discards one or more trap spacings of observed within-night positional variation.

Do not say:
- individuals naturally move 6.25+ m on 70% of all nights;
- the first capture is more accurate than the last;
- live trapping universally biases home-range estimates;
- this dataset estimates unrestricted nocturnal paths.

## Relation to existing methods literature

Existing interval-trapping work has tested nocturnal activity timing, trap availability, recapture latency and disturbance from trap checks. Multiple-capture studies have used joint captures to infer social association. The manuscript should frame its gap more narrowly: **the representativeness of a single nightly spatial location when the same marked individual is observed at multiple trap locations within the night**.

## Figure plan

### Figure 1 — Observation-process geometry
- one individual, same night: first F_t and last L_t, span delta_t;
- two nights: first-first and last-last movement;
- visual statement of the deterministic bound;
- population panel showing first/last MPD representations.

### Figure 2 — Prospective held-out validation
- PEMA and PEER one-spacing shift proportions with 95% Wilson intervals;
- horizontal frozen 0.25 materiality line;
- grid-specific raw proportions as small points;
- visually distinguish species-level confirmatory estimates from grid replication.

### Figure 3 — Positional-span magnitude
- ECDF or raincloud-style distributions of first-to-last distance for PEMA/PEER;
- vertical lines at 6.25, 12.5 and 18.75 m;
- report medians and q90.

### Figure 4 — Why downstream metrics can care
- discovery cohort only, clearly labeled exploratory;
- first-vs-last change in repeated-night movement estimate;
- empirical sensitivity shown beside deterministic upper-bound logic;
- packing shown as an example that can be more stable than movement.

## Main text structure

1. Introduction — spatial analyses silently choose a within-night representative state.
2. Observation-process bounds — simple geometry, explicitly not sold as new mathematics.
3. Discovery cohort — motivates magnitude question.
4. Prospective holdout design — PEMA/PEER pre-outcome lock.
5. Held-out result — strong cross-species and cross-grid replication.
6. Consequence — what delta can and cannot imply for downstream statistics.
7. Discussion — protocol dependence, repeat-capture conditioning, design recommendations.

## Practical recommendation to emerge

For studies that check and reset traps repeatedly within a night and use spatial endpoints:
- retain the capture timestamp and trap location for every recapture;
- quantify within-night positional spans before collapsing to one location/night;
- report the representative-location rule;
- if spans are non-negligible relative to trap spacing or the ecological scale of interest, carry representative-location sensitivity into downstream analyses.

## Current paper status

Empirical confirmatory gate: **passed**.
General bounds: proved and computationally verified.
External geographic replication: not yet available.
Manuscript readiness: promising methods/ecology paper, but denominator audit and focused literature audit should be completed before choosing target journal.
