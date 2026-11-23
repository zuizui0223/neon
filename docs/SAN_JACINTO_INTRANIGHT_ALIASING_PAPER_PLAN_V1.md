# Intra-night positional aliasing — paper plan v1

## Working title

**A night is not a point: repeated-check live trapping reveals intra-night positional aliasing in small mammals**

Alternatives:
- Repeated live-trap recaptures expose positional aliasing within nominal nightly occasions
- One-location-per-night reductions discard spatial information in repeated-check live trapping

## One-sentence result

In two prospectively held-out Cricetidae, roughly seven in ten repeat-capture individual-nights changed trap position within a night, with median changed-night displacement of 12.5–14.0 m, demonstrating that a one-location-per-night reduction can substantially alias observed space use.

## Why it matters

Capture-recapture analyses routinely define temporal occasions and may reduce repeated detections to one state per occasion. Continuous-time theory already shows that aggregation can discard information. What is usually missing is a direct empirical diagnostic of how spatially consequential that reduction is in a repeated-check live-trapping protocol.

## Discovery / confirmation structure

Discovery:
- four heteromyid species in a separate completed analysis exposed strong first-versus-last nightly-position sensitivity.

Confirmation:
- PEMA and PEER were selected using effect-blind support only;
- frozen primary thresholds were committed before first-versus-last outcomes were opened;
- both held-out species passed all pre-specified conditions.

## Confirmatory numbers

PEMA — Peromyscus maniculatus:
- 352 / 485 repeat-capture nights changed flag = 72.6%;
- 95% Wilson CI 68.4–76.4%;
- median changed-night distance 14.0 m;
- 45.2% of all repeat-capture nights moved >=12.5 m;
- 23.3% moved >=18.75 m;
- 8 grids, 12 bouts.

PEER — Peromyscus eremicus:
- 74 / 107 = 69.2%;
- 95% Wilson CI 59.9–77.1%;
- median changed-night distance 12.5 m;
- 38.3% moved >=12.5 m;
- 20.6% moved >=18.75 m;
- 3 grids, 10 bouts.

## Primary inference

The target is the **observation process**, not natural undisturbed movement.

Animals were captured, handled and released. A changed trap location is direct evidence that the observed position within the protocol is time-dependent, but not an unbiased sample of the animal's natural path.

## Recommended manuscript structure

### Introduction
1. Ecological inference often discretizes continuous animal movement into sampling occasions.
2. Continuous-time capture-recapture theory shows that temporal aggregation can discard information.
3. In repeated-check live trapping, the spatial cost of selecting one nightly position is rarely measured directly.
4. We use a discovery/held-out validation design to ask whether positional aliasing is practically large and cross-species repeatable.

### Methods
- public San Jacinto live-trapping data;
- fixed 7×7 grids, 6.25 m spacing;
- deterministic nocturnal time ordering;
- repeat-capture individual-night definition;
- prospective held-out species gate;
- first-versus-last changed flag and Euclidean displacement;
- Wilson interval and pre-specified 25% / 6.25 m confirmation thresholds;
- leave-one-grid-out and cluster-robust audits.

### Results
- support and prospective gate;
- held-out changed fractions;
- displacement scale in trap spacings;
- grid/bout/individual robustness;
- cross-platform byte-identical reproduction.

### Discussion
1. one night can contain multiple spatial states;
2. arbitrary representative-location rules can change movement-derived quantities;
3. retain within-night sequences when available;
4. at minimum, report a temporal-aliasing diagnostic before reducing repeated detections;
5. generality is limited to this protocol until externally replicated.

## Figure plan

Figure 1 — Confirmatory changed fraction:
- PEMA and PEER point estimates with 95% Wilson CI;
- horizontal 25% pre-specified threshold;
- annotate n and number of grids/bouts.

Figure 2 — Spatial magnitude:
- empirical CDF of first-to-last distance over all repeat-capture nights;
- vertical references at 6.25, 12.5 and 18.75 m;
- zero-distance mass remains visible.

Figure 3 — Spatial robustness:
- changed fraction by grid for each species;
- overall species estimates overlaid;
- demonstrates result is not one-grid driven.

Supplement:
- bout-level fractions;
- individual equal-weight fractions;
- leave-one-grid-out;
- discovery heteromyid sample clearly labelled exploratory.

## Candidate journals

Primary fit:
- Methods in Ecology and Evolution — strongest if framed as a general diagnostic with transparent software and cluster-robust validation.

Other plausible fits:
- Ecological Methods / Ecological Informatics style outlets;
- Journal of Mammalogy if framed more strongly around live-trapping observation biology.

## Do not add

- sex effects;
- home-range claims;
- extra species chosen after seeing outcome;
- threshold optimization;
- claims that all live-trapping protocols have the same magnitude.

## Remaining must-do items before manuscript-ready

- freeze cluster-robust individual/grid/bout sensitivity;
- generate deterministic figures;
- archive exact public-source checksum and workflow artifacts;
- write concise Methods and Results from the frozen receipts;
- optionally add an external protocol replication later, but do not hold the present result hostage to finding one.
