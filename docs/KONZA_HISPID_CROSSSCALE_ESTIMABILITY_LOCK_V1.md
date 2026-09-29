# Konza hispid pocket mouse cross-scale validation — estimability lock v1

Date: 2026-09-29

Status: frozen after source-schema audit and before species-by-sex support counts.

## Target taxon

Prospective target: species code `Ch` in the Konza metadata/codebook, matched **case-insensitively** in CSM012 (`ch` in the pinned raw file), corresponding to *Chaetodipus hispidus*.

This species had no sex-specific packing or movement effect inspected in the completed Portal/NEON programme. Held-out NEON work inspected only its estimability, not its effects.

## Sampling unit

A trapping period is:
`Recyear × Season × Watershed × Line`.

Primary protocol nights are `TrapDay ∈ {1,2,3,4}` only, matching the metadata description of four consecutive trapping nights. Rows outside those four trap days are excluded from the primary estimand.

Independent spatial unit:
`Watershed × Line` (trapline).

Watershed is also retained as a higher-level replication check.

## Trap geometry

Each trapline contains 20 stations at 15 m spacing. The protocol places **two Sherman traps per station**.

Therefore the finite trapping frame is 40 trap slots:
- station coordinates: 0, 15, ..., 285 m;
- each station coordinate occurs twice in the slot population.

Two captured target individuals at the same station in the same night are valid. More than two capture rows at one station/night across all species is incompatible with the stated protocol and makes that trapline-night non-estimable.

Any later packing null must operate on the 40-slot finite population, not on 20 unique station coordinates.

## Packing estimability

One packing observation is `period × TrapDay` for *C. hispidus*.

Requirements:
- trap day 1–4;
- station 1–20;
- sex resolves to M or F;
- total capture-row occupancy at every station that night is <=2;
- at least 5 male and at least 5 female *C. hispidus* captures.

Primary packing threshold: **N_male >= 5 and N_female >= 5**.

N>=3/sex is diagnostic only and cannot authorize effects.

## Individual identity for movement

Movement is reconstructed only within a single trapping period, never across seasons or years.

Strong mark tokens:
- `R:<normalized REarTag>` if the value contains at least one digit;
- `L:<normalized LEarTag>` if the value contains at least one digit;
- `T:<normalized ToeClip>` if the value contains at least one digit.

`HairClip` is not used as a primary identity token because the observed coding includes short positional codes that need not be globally unique.

Rows are linked into one individual when they share a strong token, using connected components within species × trapping period. Components fail closed when:
- no strong token exists;
- recorded sex conflicts within the component;
- the component contains more than one station on the same TrapDay.

This rule is deliberately conservative: unresolved tag loss can split an individual and reduce estimability, but may not create movement.

## Movement estimability

A recapture-eligible individual must:
- belong to the target species;
- have consistent known sex;
- have valid stations on at least 2 distinct primary TrapDays;
- pass the identity ambiguity rules above.

A trapping period is primary movement-eligible when it has:
**>=5 recapture-eligible males and >=5 recapture-eligible females**.

No distance is calculated during estimability.

## Cross-scale advance gate

Let a trapline be packing-supported if it contains >=1 primary packing night.
Let a trapline be movement-supported if it contains >=1 primary movement period.

Only traplines in the intersection of these two sets count toward the cross-scale gate.

Effect analysis is authorized only if all are true:
- >=20 primary packing nights within overlapping traplines;
- >=6 primary movement periods within overlapping traplines;
- >=6 overlapping traplines;
- >=3 watersheds represented among overlapping traplines.

Pass: `authorize_konza_crossscale_effect_lock`.

Fail: `stop_konza_crossscale_not_estimable`.

## Current effect boundary

At this lock:
- *C. hispidus* packing effects inspected: false;
- *C. hispidus* movement distances inspected: false;
- ecological effect models fit: 0.

If the gate passes, a second effect-analysis lock is required before any Packing_z or movement distance is calculated.
