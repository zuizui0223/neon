# Held-out heteromyid cross-scale validation — design v1

Date: 2026-09-29

Status: frozen before any held-out species sex-specific packing or movement outcome is calculated.

## Motivation

The completed heteromyid sex-packing programme ended with no confirmatory cross-scale result. Its primary N>=3/sex recapture family effect was positive but uncertain, while the pre-specified N>=5/sex sensitivity was positive in all three movement-inspected species with a family interval above zero.

That sensitivity cannot rescue the completed programme. It motivates one independent validation only.

## Independence rule

This branch starts from `main`, not from the completed sex-packing branch.

The following species are excluded before estimability is inspected because at least one sex-specific packing or movement outcome was already inspected in the completed programme:

- Chaetodipus baileyi
- Chaetodipus penicillatus
- Dipodomys merriami
- Dipodomys ordii

No outcome from these species may enter the held-out analysis.

## Question

> In heteromyid species whose sex-specific outcomes were not inspected in the completed programme, is male-biased repeated-night movement detectable in high-information events, and if so does that direction propagate to one-night population spatial packing?

## Data source

NSF NEON small-mammal box trapping DP1.10072.001, RELEASE-2026.

Two independent observation levels are screened:

1. diversity grids: one-night captured population configuration;
2. pathogen grids: repeated-night individual movement estimability.

## Primary sample threshold

The new programme prospectively uses **N_male >= 5 and N_female >= 5** as the primary threshold for both endpoints.

This threshold is not a sensitivity here. It is the primary threshold fixed before any held-out effect is computed.

It is treated as a **high-information inclusion rule**, not as a biological abundance threshold. The study will not claim that a sex difference begins at N=5, and it will not compare N>=3 versus N>=5 significance as evidence for a threshold mechanism.

N>=3/sex counts may be reported only as an estimability diagnostic and cannot authorize effects.

## Effect-blind estimability definitions

### Diversity-grid packing

A candidate session is species x site x diversity-grid plot x event.

Requirements:
- exactly one valid diversity plot-night for the event;
- complete grid under the existing NEON completion rule;
- acceptable samplingImpractical value;
- active-trap support passes the existing completeness rule;
- target species-rank identification with no identificationQualifier;
- valid tagID;
- deterministic first record per individual;
- all retained trap coordinates valid and unique within the session;
- >=5 retained males and >=5 retained females.

### Pathogen-grid movement

A candidate event is species x site x pathogen-grid plot x event.

An individual is recapture-eligible when:
- target species-rank identification with no identificationQualifier;
- valid tagID;
- sex is consistently male or consistently female across retained records;
- at least two distinct trapping nights have valid trap coordinates.

A primary paired event requires >=5 recapture-eligible males and >=5 recapture-eligible females.

No distance is calculated during estimability.

## Cross-scale advance gate

A held-out species qualifies only if it has both:

Packing side:
- >=10 primary N>=5/sex diversity sessions;
- >=2 independent NEON sites.

Movement side:
- >=5 primary N>=5/sex pathogen events;
- >=2 independent NEON sites.

The programme advances to any held-out effect extraction only if **at least two species** meet both sides.

If fewer than two species qualify, decision = `stop_heldout_crossscale_not_estimable`.

If at least two qualify, decision = `authorize_heldout_crossscale_effect_lock`.

## Effect boundary

At this design stage:
- held-out packing effects inspected: false
- held-out movement distances inspected: false
- ecological effect models fit: 0

Even if the estimability gate passes, a second analysis lock must be committed before effects are calculated.

## Why this is not a rescue analysis

The current programme is a new confirmatory sample of species. Species with inspected outcomes are excluded entirely, the N>=5 threshold is primary rather than selected after seeing held-out values, and the advance gate depends only on sample support.
