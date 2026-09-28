# Heteromyid sex-packing programme — recapture interpretation gate v1

Date: 2026-09-29

Status: frozen after the Phase-3 packing result but before any
sex-specific recapture displacement magnitude is inspected.

## Fixed Phase-3 fact

The packing analysis decision is:

**no_replicated_positive_support**

Portal is centered near zero and the positive NEON family mean is driven
by Dipodomys ordii rather than replicated across the three shared species.

This decision cannot change.

## Why recapture still matters

Sex-specific recapture displacement was pre-specified independently before
the Phase-3 packing outcome was opened.

It tests a different biological level:
- repeated-night individual movement versus
- same-session population spatial configuration.

A positive movement result combined with a null packing result would
support a decoupling interpretation. A weak or null movement result would
not.

## Manuscript authorization rule

The programme may advance to a **decoupling manuscript** only if all of
the following are true:

1. the frozen recapture estimability gate authorizes movement-effect
   extraction;
2. at least two frozen shared species remain in the movement validation;
3. the validation family effect
   (male minus female log1p successive-night displacement) is > 0;
4. the lower two-sided 95% Student-t CI bound for that family effect is > 0;
5. at least two frozen eligible species have positive species effects.

If all five pass:

decision = authorize_movement_packing_decoupling_manuscript

Allowed central claim:

> Sex-biased individual movement can be detectable without producing a
> replicated sex difference in abundance- and trap-geometry-conditioned
> population spatial packing.

If the movement family effect is positive but its 95% CI includes zero:

decision = stop_no_confirmatory_movement_dimorphism

If the movement family effect is <= 0:

decision = stop_no_directional_movement_dimorphism

If the recapture estimability gate fails:

decision = stop_recapture_validation_not_estimable

## Boundaries

No threshold, taxon set, site set, displacement summary, or confidence
rule may be changed after movement magnitudes are opened.

A species-specific positive movement effect cannot substitute for a failed
family gate.

The decoupling result, if authorized, does not imply:
- sex-biased dispersal;
- home-range size;
- mating movement;
- reproductive causation.

At this lock:
- sex-specific recapture displacement magnitudes inspected: false
- movement effect models fit: 0
