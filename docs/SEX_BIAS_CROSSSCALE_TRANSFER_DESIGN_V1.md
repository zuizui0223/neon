# Sex-bias cross-scale transfer in NEON small mammals — design v1

Date: 2026-09-29

Status: frozen before any included species sex-specific packing or movement effect is calculated.

## Biological question

> Across species-site populations, does the direction and magnitude of sex bias in repeated-night individual movement predict the sex bias in one-night captured population spatial packing?

This is a cross-scale transmission question, not a universal male-greater-than-female hypothesis.

## Independence

The branch starts from `main`.

Species with previously inspected sex-specific outcomes are excluded before estimability:
- Chaetodipus baileyi
- Chaetodipus penicillatus
- Dipodomys merriami
- Dipodomys ordii

Two known problematic Peromyscus complexes are also excluded prospectively:
- Peromyscus maniculatus
- Peromyscus leucopus

No sex-specific packing or movement outcome for any included species is inspected during estimability.

## Data source

NSF NEON small-mammal box trapping DP1.10072.001, RELEASE-2026.

Endpoints:
1. diversity-grid one-night population configuration;
2. pathogen-grid repeated-night individual movement.

## Session/event inclusion

Primary sex-count threshold for both endpoints:

**N_male >= 3 and N_female >= 3**

This threshold is fixed before effect extraction and is not selected by significance.

### Packing candidate

Species x site x diversity-grid plot x event, requiring:
- one valid diversity plot-night;
- complete/acceptable grid;
- active traps resolving to finite NEON registry coordinates;
- target species-rank unambiguous identification;
- valid tagID;
- deterministic first record per individual;
- all retained individual trap nodes valid and unique;
- >=3 males and >=3 females.

### Movement candidate

Species x site x pathogen-grid plot x event, requiring:
- at least two valid pathogen-grid nights;
- target species-rank unambiguous identification;
- valid tagID;
- consistent known sex per individual;
- at least two distinct nights at finite registry-backed trap nodes;
- >=3 recapture-eligible males and >=3 recapture-eligible females.

## Species-site stratum gate

A species-site stratum is cross-scale estimable only if it has:
- >=5 eligible packing sessions;
- >=5 eligible movement events.

## Programme advance gate

Effect analysis is authorized only if the effect-blind scan yields:
- >=10 cross-scale estimable species-site strata;
- >=5 species;
- >=4 sites;
- >=3 species represented by cross-scale strata at >=2 sites each.

If the gate fails:
`stop_crossscale_transfer_not_estimable`

If the gate passes:
`authorize_crossscale_transfer_effect_lock`

A second effect-analysis lock must then be committed before any sex-specific distance or Packing_z is calculated.

## Planned inferential target if estimable

The eventual primary quantity is the cross-scale association between site-level sex bias in movement and site-level sex bias in packing.

The sign of either endpoint is not required to be positive. A positive transfer slope would mean that populations with more male-biased movement also tend to show more male-biased one-night spatial packing.

No slope, correlation, effect sign, confidence interval, or p-value is calculated at this stage.

## Effect status at lock

- packing sex effects inspected: false
- movement sex effects inspected: false
- cross-scale slope fitted: false
- ecological effect models fit: 0
