# Wyoming pocket-mouse cross-scale estimability design lock v1

Date: 2026-09-29

Status: frozen before any species-specific sample-support count is opened.

## Focal held-out species

Primary focal species: *Perognathus fasciatus*.

*Dipodomys ordii* is prospectively excluded because its sex-specific outcomes were already inspected in the completed NEON/Portal programme.

## Primary information threshold

`N_male >= 5` and `N_female >= 5` is the primary inclusion rule for both endpoints.

This is an information threshold, not a biological threshold. The analysis will not claim that a sex effect begins at N=5 and will not compare N>=3 versus N>=5 significance as a threshold mechanism.

## Endpoint 1: one-night packing estimability

Within site × trapping session × night, retain one capture location per uniquely marked individual under a deterministic rule.

A primary packing session requires:
- >=5 retained males and >=5 retained females;
- valid spatial grid/trap locations;
- no duplicate retained location within the same sex-specific one-night configuration unless the field protocol allows more than one simultaneously active trap at that grid point and the geometry model explicitly represents them.

Packing advance requirement:
- >=10 primary sessions;
- >=2 independent sites.

## Endpoint 2: repeated-night movement estimability

Within site × trapping session, an individual is movement-eligible when:
- identity is unique and stable;
- sex is known and internally consistent;
- at least 2 distinct trapping nights have valid spatial capture locations.

A primary movement event requires >=5 movement-eligible males and >=5 movement-eligible females.

Movement advance requirement:
- >=5 primary events;
- >=2 independent sites.

## Cross-scale site match

The same species must satisfy both endpoints in at least 2 overlapping sites.

Within those overlapping sites there must be:
- >=10 packing primary sessions; and
- >=5 movement primary events.

If this fails: `stop_wyoming_pocketmouse_not_estimable`.

If it passes: `authorize_wyoming_pocketmouse_effect_lock`, after which a second lock must be committed before any packing or movement effect is calculated.

## Current effect status

- focal-species support counts inspected: false
- sex-specific effects inspected: false
- movement distances inspected: false
- packing effects inspected: false
- ecological effect models fit: 0
