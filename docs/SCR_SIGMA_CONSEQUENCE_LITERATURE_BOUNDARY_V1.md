# Literature boundary — within-occasion state mixing and SCR sigma v1

Date: 2026-10-01

## What is already known

### Behavioural responses are already part of SCR/SECR

The `secr` detection model already distinguishes several post-detection responses in encounter probability:

- `b`: global learned response after first detection;
- `B`: global transient response to the previous occasion;
- `bk`: detector-specific learned response;
- `Bk`: detector-specific transient response.

Therefore this paper must not claim that post-capture behavioural dependence is new.

Published SCR analyses and simulation work have shown that trap-specific responses can affect sigma and density when the response is omitted or misspecified. Schmidt et al. (2022, Ecological Applications) is an especially relevant boundary case.

### Explicit detection-history movement dependence is also not new

van Helsdingen & Jones-Todd (2026, Journal of Agricultural, Biological and Environmental Statistics) developed a continuous-time SCR model with Hawkes-inspired detection rates. Their detection rate combines a fixed home-range component with a component centred on the individual's previous detection, allowing temporal and spatial clustering after detection.

Thus the general idea that detections can change the distribution of later detections, and that standard stationary SCR may then target the wrong process, cannot be presented as novel here.

### Fine trap checks can legitimately be occasions

SCR datasets exist in which individual trap checks, rather than whole days, are the sampling occasions. Small-mammal/open-population examples also preserve AM/PM or other secondary checks. Therefore the manuscript must directly address the objection:

> Why not simply define each check as an SCR occasion?

This is an alternative analysis, not a straw man.

## The narrower gap addressed here

The present contribution is the combination of four elements:

1. **Physical live-trap repeated checks within a nominal ecological occasion.**
   The same marked individual can be captured, handled, released and later captured at another detector before the analyst's conventional nightly occasion ends.

2. **An empirical diagnostic before downstream modelling.**
   The raw data reveal how often alternative within-night detector states differ by a material spatial scale. Single-observation nights are kept unresolved rather than silently coded as no change.

3. **Direct aggregation-rule consequence analysis.**
   The same observation process is encoded as CHECK, NIGHT-FIRST and NIGHT-LAST capture histories, and sigma is compared to its known generating value in simulation.

4. **Empirical calibration with observed transition vectors.**
   The consequence benchmark does not invent an arbitrary movement distribution: repeat frequency, changed-location frequency, and the non-zero first-to-last vector kernel are taken from the already-opened held-out PEMA + PEER data.

The specific methodological question is therefore not:

> Can SCR contain behavioural dependence?

It can.

Nor is it:

> Can a more complex continuous-time SCR model represent movement after detection?

It can.

The question is:

> Before committing to a finer or more complex model, can repeated-check data diagnose whether a conventional occasion collapse is spatially consequential, and can the actual observed within-occasion transition scale be translated into the size and direction of downstream sigma instability?

## Why CHECK is not automatically the reference truth

If each check samples a stationary SCR kernel, CHECK should be the information-preserving encoding and NIGHT-FIRST/LAST should mainly lose precision.

If observation changes state, however, CHECK can contain detections from both the baseline and post-observation states. A standard stationary CHECK model can then estimate a mixture spatial scale rather than the baseline long-term sigma.

This is why the primary benchmark evaluates all encodings against a known generating sigma and includes mirrored POST/PRE transitions. It does not declare CHECK, FIRST, or LAST intrinsically correct.

## Relation to behavioural-response models

The targeted pilot additionally compares naive CHECK with CHECK-`Bk`.

This matters because a conventional behavioural term modifies encounter probability. It may repair a local trap-attraction process, but it is not guaranteed to repair a transition in spatial state whose later locations are displaced to other detectors.

If CHECK-`Bk` recovers sigma in the calibrated local-response pilot while naive CHECK does not, that demonstrates a model-based remedy for that specific response mechanism.

If an empirical-vector transition still shifts sigma under standard behavioural terms, the interpretation is instead that the nominal occasion contains multiple spatial states and requires a richer movement/detection model.

## Claim boundary for the paper

Do not claim:
- discovery of trap response;
- discovery that behavioural misspecification can bias SCR;
- first time-dependent SCR model;
- first model linking detections through movement;
- that San Jacinto first-to-last displacement is caused by handling.

Potentially support, if the frozen benchmark succeeds:
- repeated-check live-trap data can expose material within-occasion state variation before SCR fitting;
- nightly reduction is benign under a stationary negative control but becomes consequential under empirically calibrated within-occasion state transitions;
- simply splitting checks into occasions need not recover baseline sigma if the observation protocol changes the spatial state;
- the dimensionless size of within-occasion transition relative to baseline sigma is a natural diagnostic of estimand stability.

## Key references

- Borchers DL, Distiller G, Foster RJ, Harmsen BJ, Milazzo L. 2014. Continuous-time spatially explicit capture-recapture models, with an application to a jaguar camera-trap survey. Methods in Ecology and Evolution 5:656-665.
- Schmidt JH et al. 2022. Precision and bias of spatial capture-recapture estimates: a multi-site, multi-year Utah black bear case study. Ecological Applications 32:e2618.
- van Helsdingen ABM, Jones-Todd CM. 2026. A Spatial Capture-Recapture Model with Hawkes-Inspired Detection Rates to account for Animal Movement. Journal of Agricultural, Biological and Environmental Statistics.
- Efford MG. current `secr` documentation: behavioural predictors `b`, `B`, `bk`, `Bk`; `make.capthist`; `sim.capthist`.
