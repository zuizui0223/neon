# Unseen-species high-information heteromyid movement validation — design v1

Date: 2026-09-29

Status: frozen before any movement magnitude is inspected in the validation species.

## Provenance of the hypothesis

The preceding heteromyid sex-packing programme was stopped under its frozen confirmatory rules. Its pre-specified NEON recapture sensitivity at >=5 recaptured males and >=5 recaptured females per event showed a positive and unusually consistent male-minus-female movement contrast in three discovery species:

- Chaetodipus penicillatus
- Dipodomys merriami
- Dipodomys ordii

That result is explicitly hypothesis-generating and cannot rescue the stopped programme.

## New confirmatory question

> In heteromyid species whose movement outcomes were not inspected in the discovery programme, do high-information pathogen-grid events (>=5 recapture-eligible males and >=5 recapture-eligible females) show a positive male-minus-female repeated-night movement contrast?

## Validation taxonomic scope

All NEON target Heteromyidae in the genera Chaetodipus, Dipodomys, Perognathus, and Microdipodops, excluding the three discovery species above.

Species-rank ambiguous records are excluded.

## Effect-blind estimability stage

Before any movement distance is calculated, count recapture-eligible individuals only.

An individual is recapture-eligible within a pathogen-grid event when:
- tagID is present;
- sex is consistently male or consistently female across its event records;
- at least two distinct trapping nights have valid trap coordinates;
- species identification passes the frozen taxonomic rules.

Primary event eligibility:
- >=5 recapture-eligible males;
- >=5 recapture-eligible females.

Sensitivity inventory only:
- >=3 per sex.

No displacement distance, median, sign, coefficient, CI, or p-value is inspected in this stage.

## Advance gate

The movement-effect analysis is authorized only if:
1. at least 3 outcome-uninspected heteromyid species each have >=5 primary events;
2. the qualifying primary events collectively span at least 3 NEON sites.

If the gate fails, this validation stops and no movement outcome is opened.

## Frozen effect estimator if the gate passes

For each recapture-eligible individual:
1. retain one valid location per night under deterministic date/night/uid ordering;
2. calculate successive-night Euclidean displacements;
3. summarize the individual by its median successive-night displacement;
4. transform with log1p.

Within each primary event:

`Delta_movement = median(male individual log1p median displacement) - median(female individual log1p median displacement)`

For each qualifying species:
- average event contrasts within site;
- average site means with equal site weight.

Validation family effect:
- equal-weight mean over qualifying species;
- two-sided 95% Student-t CI over species effects.

Confirmatory positive support requires:
- family effect > 0;
- family 95% CI lower bound > 0;
- at least ceiling(2/3 of qualifying species) have positive species effects.

## Sensitivity

N>=3 per sex is reported only as a sensitivity and cannot rescue a failed N>=5 primary result.

## Claim boundary

Allowed if confirmatory gate passes:
- male-biased repeated-night movement generalizes to outcome-uninspected heteromyid species under high-information trapping events.

Not allowed:
- universal heteromyid sex dimorphism;
- dispersal;
- home-range size;
- mating movement or reproductive causation;
- using the result to reverse the stopped packing programme.

At this lock:
- validation-species movement magnitudes inspected: false
- movement effect models fit: 0
