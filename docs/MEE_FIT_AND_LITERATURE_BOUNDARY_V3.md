# MEE fit and focused literature boundary — v3

Date: 2026-10-03

Status: current literature/implementation boundary for manuscript v0.4.

## What the current `secr` interface actually permits

The current `secr` documentation distinguishes multi-catch traps (`multi`) from non-exclusive proximity/count detectors. True traps create competing capture risks because capture at one trap precludes simultaneous capture at another until the animal is released. Capture histories are organized by animal, sampling occasion and detector.

For an output detector of type `multi`, `reduce.capthist` explicitly recognizes a locational ambiguity when old occasions are pooled and the same animal was detected at more than one detector in the resulting occasion. The current documented conflict rule is

`select = c("last", "first", "random")`.

Detector usage is summed across the contributing occasions when occasions are pooled.

This is important for the manuscript because FIRST and LAST are not artificial data manipulations invented for this paper. They are explicit conflict-resolution options in the current package interface when multiple old occasions are reduced to one `multi`-trap occasion.

Sources checked 2026-10-03:
- current CRAN `secr::reduce.capthist` documentation;
- `secr` 5.4 overview / current CRAN vignette;
- current `secr` package documentation index.

## The obvious reviewer objection: why not make each trap check an occasion?

That is a valid representation and must be acknowledged directly.

In the San Jacinto protocol, traps were checked three times within each night and animals were released at the point of capture during each check. Thus the raw protocol naturally permits a CHECK representation with three SCR occasions per night. The original study reports eight 7×7 grids, 6.25-m spacing, three nightly checks and release at the point of capture.

The manuscript therefore no longer argues that nightly collapse is the only possible SCR encoding. It compares:

- **CHECK** — retain the physical trap checks as occasions;
- **FIRST** — pool the three checks to one night and retain the first detector when pooling creates a `multi`-detector conflict;
- **LAST** — the analogous last-detector resolution.

The methodological question is consequently not “must these data be collapsed?” It is:

> **When do plausible temporal representations of the same raw repeated-check record estimate the same spatial scale, and when do they cease to be estimand-equivalent?**

## Existing small-mammal precedent still matters

Romairone et al. (2018) used live-trapped common voles in an SCR study in which traps were checked twice per day, while the model used eight capture occasions per trapping session corresponding to trapping days. Animals were released where captured.

This establishes that a coarser ecological occasion than the physical trap-check interval has precedent in small-mammal SCR. It does not prove that nightly/daily pooling is always optimal, and it does not determine how repeated within-occasion detector conflicts should be resolved.

That is exactly why the manuscript now tests temporal representation rather than presenting nightly pooling as a uniquely standard solution.

Reference:
Romairone J, Jiménez J, Luque-Larena JJ, Mougeot F. 2018. Spatial capture-recapture design and modelling for the study of small mammals. *PLoS ONE* 13:e0198766. DOI 10.1371/journal.pone.0198766.

## Why finer occasions solve only one of two problems

The v0.4 benchmark separates two issues.

### 1. Information loss

If all physical checks sample the same stationary SCR state, pooling checks to FIRST or LAST discards observations but should not systematically create two different sigma estimands.

The stationary negative controls support this: CHECK, FIRST and LAST all remain near the generating sigma and FIRST/LAST ratios remain near one.

### 2. State-mixture mismatch

If the within-night observation process changes which spatial state is sampled, CHECK retains the observations but a static-centre SCR model is then fitted to more than one spatial state.

In the empirical-transition simulations, CHECK therefore does not consistently recover the baseline generating sigma even though no detections are discarded. FIRST and LAST also differ because they preferentially select different states. Mirroring whether the transitioned state is PRE or POST reverses the FIRST/LAST direction.

Thus:

> **Finer occasions are a remedy for record loss, not automatically for within-occasion state change under a static-state model.**

This is the direct response to the strongest foreseeable SCR reviewer objection.

## Handling/release is a limitation and a reason for the state-based framing

The San Jacinto protocol released animals at the point of capture during each trap check. Therefore every capture after the first within a night occurs after at least one capture/handling/release event.

The empirical FIRST-to-LAST vector must not be described as:
- an undisturbed movement trajectory;
- home-range displacement;
- free-ranging path length;
- evidence that handling caused movement.

Handling is one possible contributor. Natural within-night movement, trap attraction/avoidance and stochastic recapture at another nearby detector may also contribute.

For that reason, the v0.4 simulation uses the empirical vectors as an **observation-process transition kernel**. PRE and POST orientations are mirrored. The result asks what happens if an observation protocol samples alternative states at the empirically observed spatial scale; it does not assign a biological cause to those states.

## Continuous-time and behavioural models define the upper boundary

Continuous-time SECR and models with explicit behavioural/state structure remain more complete solutions when exact event timing or observation-induced state changes are central to inference.

The manuscript must not claim:
- temporal aggregation is newly recognized;
- finer temporal modelling is unnecessary;
- static SCR is universally invalid for repeated-check trapping;
- the proposed diagnostic substitutes for a process model.

The proposed diagnostic occupies an earlier and lighter decision point:

1. determine whether repeat observations expose materially different spatial states;
2. scale that transition relative to the downstream spatial parameter;
3. test whether defensible temporal encodings are estimand-stable;
4. escalate to finer-time or state-aware modelling if they are not.

## Empirical and simulated claim boundary

Empirically supported:
- PEMA and PEER often had different observed detector states within a night among repeat-observed nights;
- directly observed material shifts occur on at least 28.9% and 24.6% of all valid individual-nights;
- these are observation-process facts, not latent movement probabilities.

Simulation-supported:
- stationary CHECK/FIRST/LAST encodings are approximately sigma-equivalent under the tested design;
- empirical-scale state mixing can make FIRST, LAST and CHECK target materially different spatial scales under a static-centre SCR model;
- reversing state order reverses FIRST/LAST direction.

Not supported:
- an empirical two-species SCR sigma effect;
- an empirical home-range effect;
- handling as the cause of the empirical transition;
- a universal best temporal representation.

## Novelty wording for v0.4

Avoid the broad claim that no prior work has addressed temporal aggregation. The defensible contribution is more specific:

> **The paper provides a lightweight, scale-aware diagnostic for observed within-occasion positional multiplicity and connects it to an explicit downstream estimand-stability test. The key methodological distinction is between information lost by aggregation and spatial-state mixtures that make plausible temporal representations non-equivalent.**

The deterministic bounds are practical translations, not novel mathematics. The downstream SCR result is the main methodological consequence, while the 72-cell Wilson/bias benchmark remains supplementary.

## Current MEE position

The scientific issue that made v0.3 too thin has been addressed: the paper now shows a direct downstream parameter consequence under known truth, with a stationary negative control and mirrored state ordering.

The pre-submission enquiry should remain on HOLD only for final consistency, author metadata and archival packaging. No further same-data biological-effect search is required.
