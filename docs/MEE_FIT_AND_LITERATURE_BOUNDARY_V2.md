# MEE fit and focused literature boundary — v2

Date: 2026-09-30

## Recommended article type

**Methods in Ecology and Evolution — Research Article**

The current MEE author guidance states that Research Articles should describe new methods in ecology and evolution, that new computational methods normally should be evaluated with simulations or benchmark datasets, and that broad applicability across taxa or systems should be demonstrated.

This project now satisfies the structural requirements better as a Research Article than as an Application paper:
- the contribution is a diagnostic/methodological approach rather than a software package alone;
- generic code is provided;
- a simulation benchmark is frozen;
- deterministic sensitivity bounds are supplied;
- an empirical held-out validation is prospectively locked and spatially replicated;
- failure modes are explicitly demonstrated.

MEE also encourages pre-submission enquiries. A concise enquiry should be sent before full submission once figures and v0.5 prose are ready.

## Existing methods that define the boundary

### Detector semantics in SCR/SECR

Efford & Boulanger (2019, Methods in Ecology and Evolution, DOI 10.1111/2041-210X.13239) explicitly distinguish traps, which detain an animal and therefore generate at most one detector location per animal per occasion, from proximity detectors that can record an animal at multiple detectors within one occasion.

Efford, Dawson & Borchers (2009, Ecology, DOI 10.1890/08-1735.1) similarly emphasize that the observation model must match detector type and that spatial detections may be collapsed or retained differently depending on detector process.

Efford (2013, Methods in Ecology and Evolution, DOI 10.1111/2041-210X.12049) shows that variation in detector effort and occasion definition matters for spatial capture–recapture likelihoods.

**Implication for this paper:** a repeated-check live-trapping protocol in which animals are released and may be caught again at another trap within the same night does not fit neutrally into a one-location-per-night representation. Either the night is split into finer occasions or multiple within-night locations must be reduced by an explicit rule.

### Interval trapping and within-night capture timing

Drickamer & Springer (1998, Behavioural Processes, DOI 10.1016/S0376-6357(98)00012-6) used 2-hour live-trap checks to study nocturnal activity timing in house mice.

This establishes that within-night trapping intervals and recapture timing are methodologically meaningful. It does **not** directly answer the present representative-location question: how much spatial information is discarded when multiple valid locations for the same marked individual within one ecological occasion are collapsed to one location.

## Specific gap retained after literature audit

The manuscript should not claim:
- that rodents moving within a night is novel;
- that repeated capture is novel;
- that trap checking influences activity is novel;
- that triangle inequality is novel;
- that detector/occasion definitions are new.

The narrower gap is:

> **There is no routine, scale-aware diagnostic for the representativeness of a single spatial state assigned to an occasion when the same marked individual is observed at multiple locations within that occasion, together with transparent bounds linking the observed within-occasion positional span to downstream spatial statistics.**

The contribution is therefore an **observation-process diagnostic and sensitivity framework**, not a new movement model.

## Empirical source and ethics

The validation dataset was deposited in Figshare by Chock, Shier & Grether and is associated with:

Chock RY, Shier DM, Grether GF. 2022. Niche partitioning in an assemblage of granivorous rodents, and the challenge of community-level conservation. Oecologia 198:553–565. DOI 10.1007/s00442-021-05104-5.

The published article states that applicable institutional guidelines for animal care and use were followed and links the public Figshare dataset (10.6084/m9.figshare.18295520.v1).

The present study performs secondary analysis only and conducts no new animal handling. The Methods/Ethics statement should cite the original animal-use statement and make the secondary-analysis status explicit.

## Empirical claim boundary

The confirmatory empirical result concerns **repeat-capture individual-nights** in two held-out Cricetidae species:
- PEMA: 72.6% >= one trap spacing;
- PEER: 69.2% >= one trap spacing.

These proportions must not be described as all-night movement probabilities.

The denominator audit provides the safer all-night statement:
- PEMA: material positional change directly observed on at least 28.9% of 1,219 valid individual-nights;
- PEER: at least 24.6% of 301 valid individual-nights.

These are observational lower bounds because single-capture nights cannot reveal first-to-last change.

## Simulation boundary

The simulation benchmark demonstrates:
- under non-informative repeat observation, repeat-conditioned estimates are essentially unbiased and Wilson coverage is near nominal;
- span-dependent repeat observation produces directional bias;
- the all-night directly observed fraction remains a lower bound in every simulated replicate.

Therefore the method diagnoses temporal positional aliasing but does not claim to identify an unobserved all-occasion aliasing rate unless the repeat-observation mechanism is modelled or plausibly non-informative.

## Downstream-analysis boundary

A prospectively frozen MCP home-range sensitivity test was attempted only after an effect-blind support gate.

The support gate failed:
- PEMA: 17 eligible individuals versus 20 required;
- PEER: 6 versus 15 required.

No MCP areas or area ratios were authorized. This is non-estimability, not a negative downstream effect.

The manuscript should not imply direct empirical proof that home-range estimates change. The deterministic bounds and generic diagnostic provide the methodological link; downstream estimator-specific effects remain a future application.

## MEE-specific framing

The paper should lead with the method:

1. define temporal positional aliasing;
2. provide the generic diagnostic;
3. derive practical deterministic sensitivity bounds;
4. evaluate the diagnostic by simulation;
5. provide a prospectively held-out empirical validation;
6. discuss observation-process limitations and reporting recommendations.

San Jacinto is the **validation case**, not the paper's central identity.

## Current recommendation

Proceed toward a MEE pre-submission enquiry after:
- finalizing Figures 1–4;
- replacing manuscript citation placeholders;
- verifying the generic example workflow;
- exporting the paper branch to a standalone review repository/archive;
- adding a title page and ethics/data/code statements.

Do not add another post-hoc ecological effect analysis merely to make the paper look larger.
