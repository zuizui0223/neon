# Powdermill cross-scale estimability design lock v1

Date: 2026-09-29

Status: frozen before any Powdermill sex-specific sample-support count or ecological effect is inspected.

## Source precondition

This design is authorized to run only if the DataONE source audit verifies the documented individual-capture structure:
`animal_id, is_new, species_code, period, time, date, quadrat, sex, ...`.

## Taxonomic panel fixed before counts

Restrict the analysis to documented Rodentia codes:
- CG — *Clethrionomys/Myodes gapperi*
- GV — *Glaucomys volans*
- MM — *Marmota monax*
- NI — *Napaeozapus insignis*
- NM — *Neotoma magister*
- PL — *Peromyscus leucopus*
- PM — *Peromyscus maniculatus*
- TS — *Tamias striatus*

Non-rodents, mustelids, opossums and shrews are excluded before counts are viewed.

## Primary information threshold

Primary within-period sex threshold: **N_male >= 3 and N_female >= 3**.

This is a minimum estimability rule, not a biological abundance threshold. N>=5/sex will be counted as a pre-specified high-information diagnostic but cannot replace the primary rule after outcomes are opened.

## Packing-side estimability

Unit: species × trapping period × capture date.

A night is packing-eligible when:
- sex is known and resolves consistently for the retained animal record;
- animal_id is present;
- quadrat/station is structurally valid;
- no station has more captured individuals than the documented two trap slots available at that station;
- >=3 retained males and >=3 retained females are present.

A period has packing support when it contains >=2 packing-eligible nights for that species.

No Packing_z or pairwise-distance response is calculated during this gate.

## Movement-side estimability

Unit: species × trapping period.

An individual is movement-eligible when:
- animal_id is present;
- sex is consistent within the period;
- it has captures on >=2 distinct dates/nights;
- every retained capture has a structurally valid quadrat/station.

A period has movement support when >=3 movement-eligible males and >=3 movement-eligible females are present.

No movement distance is calculated during this gate; repeated locations with zero displacement are not excluded.

## Paired cross-scale period

A species-period is paired-eligible only when the same species and period has both:
- packing support (>=2 eligible nights), and
- movement support.

This makes the later cross-scale comparison temporally matched rather than comparing different portions of the time series.

## Species and programme advance gates

A rodent species qualifies only if it has:
- >=10 paired-eligible primary periods;
- paired periods spanning >=3 calendar years.

The programme advances to an effect-analysis lock only if **>=3 fixed-panel rodent species** qualify.

Pass decision: `authorize_powdermill_crossscale_effect_lock`.

Fail decision: `stop_powdermill_crossscale_not_estimable`.

## Structural geometry gate

The known field protocol is a 10 x 10 station grid at 10-m spacing with two trap slots at each station.

Before effects are opened, the estimability audit must additionally verify that observed `quadrat` coding is compatible with exactly 100 station identities. The later effect lock must document the station-number-to-grid-coordinate mapping; it may not infer an arbitrary mapping after seeing effects.

The exact finite-slot null already implemented on this branch is the only permitted packing-null family: active trap support consists of 200 trap slots, with each station coordinate represented twice.

## Future effect question (not yet authorized)

If the gate passes, the next lock will test cross-scale coupling rather than a universal male-positive sign:

> Across temporally matched periods, do sex differences in individual movement covary positively with sex differences in one-night population packing?

The exact estimator, uncertainty model and manuscript rule must be frozen in a separate commit after estimability but before any movement distance or Packing_z is calculated.

## Current effect status

- species-specific support counts inspected: false
- sex-specific support counts inspected: false
- movement distances computed: false
- packing effects computed: false
- ecological effect models fit: 0
