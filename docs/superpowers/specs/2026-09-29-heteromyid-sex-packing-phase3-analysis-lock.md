# Heteromyid sex-specific spatial packing — Phase 3 analysis lock v1

Date: 2026-09-29

Status: frozen after the exact-v2 mechanical gate and trap-support
estimability gate, but before any observed sex-specific Packing_z or
Delta_sex_packing effect is extracted.

## 1. Preconditions now satisfied

The exact finite-population mechanical audit passed without changing the
frozen |rho| <= 0.2 warning threshold.

The post-support estimability gate also passed:

Portal primary support-valid N>=3/sex sessions:
- count-only: 1,431
- support-valid: 1,308
- qualifying species: Chaetodipus baileyi, Chaetodipus penicillatus,
  Dipodomys merriami, Dipodomys ordii

NEON primary support-valid N>=3/sex sessions:
- count-only: 110
- support-valid: 110
- qualifying species: Chaetodipus penicillatus, Dipodomys merriami,
  Dipodomys ordii

Frozen same-species cross-source set:
- Chaetodipus penicillatus
- Dipodomys merriami
- Dipodomys ordii

At this lock:
- observed sex-specific Packing_z effects inspected: false
- Delta_sex_packing effects inspected: false
- ecological sex model fits: 0

## 2. Outcome extraction

For every support-valid candidate session:

1. Retain the deterministic first record for each individual under the
   frozen source-specific ordering rule.
2. Require every retained trap location to be valid and the retained
   male+female+unknown location union to contain no duplicates.
3. Use the exact active-trap geometry for that session.
4. Calculate exact-v2 Packing_z separately for males and females,
   conditioning on exact N_male or N_female.
5. Define:

   Delta_sex_packing = Packing_z_male - Packing_z_female

Positive Delta means that males are more spatially dispersed relative to
their sex-specific exact trap-geometry null than females.

The primary threshold remains N_male >= 3 and N_female >= 3.

## 3. Primary estimator

The v1 design named a generic random-effects model before the realized
replication structure was known. The support-only gate now shows that the
NEON qualifying species have only 2, 2, and 3 independent sites.
Before outcomes are opened, the implementation is therefore frozen as a
design-based hierarchical estimator rather than estimating poorly
identified Gaussian random-effect variances.

For each source:

### 3.1 Spatial-unit means

Portal independent spatial unit:
- plot

NEON independent spatial unit:
- site

For species s in spatial unit u:

unit_mean(s,u) = arithmetic mean Delta across all primary eligible sessions
for that species and unit.

Every session has equal weight within its unit.

### 3.2 Species means

species_effect(s) = arithmetic mean of unit_mean(s,u) across the frozen
independent units represented by species s.

Thus long-running plots or sites do not receive more weight merely because
they contain more eligible sessions.

Species-specific uncertainty:
- sample SD of spatial-unit means;
- standard error = SD/sqrt(G_s);
- two-sided 95% Student-t interval with df = G_s - 1.

No normal-theory z interval is substituted when G_s is small.

### 3.3 Source-level family mean

source_family_effect = arithmetic mean of species_effect(s) over the
frozen qualifying species in that source.

Every qualifying species receives equal weight.

Source-level uncertainty:
- sample SD of frozen species effects;
- standard error = SD/sqrt(S);
- two-sided 95% Student-t interval with df = S - 1.

This interval deliberately treats species, not sessions, as the final
replication layer for the across-species claim.

## 4. Primary replicated-support rule

The directional hypothesis remains Delta_sex_packing > 0.

The label replicated_positive_support may be used only if all of the
following are true:

1. Portal source_family_effect > 0;
2. NEON source_family_effect > 0;
3. the lower 95% Student-t CI bound for the Portal source-family effect is > 0;
4. the lower 95% Student-t CI bound for the NEON source-family effect is > 0;
5. at least 2 of the 3 frozen shared species have species_effect > 0 in
   both sources.

If any condition fails, the primary decision is
no_replicated_positive_support.

No sensitivity analysis can reverse that primary decision.

## 5. Primary claim boundary

Even if the support rule passes, the allowed claim is:

"Across the frozen included heteromyid species in two independent
long-term trapping systems, males show higher abundance- and
trap-geometry-conditioned population spatial packing than females."

Not allowed:
- a universal claim about all Heteromyidae;
- individual home-range size;
- sex-biased dispersal;
- territory size;
- mating movement;
- causal attribution to reproduction.

## 6. Frozen sensitivities

The following are reported but cannot rescue a failed primary result:

1. N_male >= 2 and N_female >= 2;
2. N_male >= 5 and N_female >= 5;
3. Portal sessions with pit_reliable_fraction = 1;
4. sessions with known_sex_fraction >= 0.8;
5. leave-one-species-out source-family means;
6. leave-one-spatial-unit-out species means.

All sensitivities use the same exact-v2 Packing_z and the same
unit-then-species weighting logic.

## 7. Season

The primary estimand is the marginal sex difference over the actual
trapping-season distribution because male and female responses are paired
within the same session; calendar season is therefore shared by the two
sexes and is not a confounder of the within-session contrast.

The generic v1 "season" term is not used to redefine the primary
estimand after the realized site counts are known.

A harmonic month analysis may be reported as a secondary effect-modifier
analysis only:
- sin(2*pi*month/12)
- cos(2*pi*month/12)

It cannot redefine or rescue the primary effect.

## 8. Independent movement validation

The frozen NEON pathogen-grid recapture validation remains separate.

It asks whether male-female recapture displacement is directionally
concordant with the primary population-packing result after species and
site context are accounted for.

Movement validation cannot redefine Delta_sex_packing or rescue the
primary decision.

## 9. Reproducibility boundary

The effect-extraction workflow must:
- verify the exact-v2 mechanical receipt passes;
- verify the post-support gate decision is authorize_effect_extraction;
- use the frozen Portal commit and NEON RELEASE-2026;
- save source-specific session-level outcome tables as workflow artifacts;
- commit only compact result summaries/receipts, not raw downloaded data;
- record ecological_model_fits only after this lock exists.

No species, threshold, sign, or estimator may be changed after the
observed Delta values are generated.
