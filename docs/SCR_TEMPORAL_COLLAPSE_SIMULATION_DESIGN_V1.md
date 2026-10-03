# SCR temporal-collapse simulation design v1

Date: 2026-10-03

Status: prospective simulation extension after the empirical SCR sigma gate stopped.

## Why this simulation exists

The empirical FIRST-vs-LAST SCR sigma programme stopped before any sigma effect was opened because the frozen two-species support gate failed: PEMA had 19 eligible sessions whereas PEER had 2, so only PEMA qualified.

That stop remains binding. This simulation does not reopen, relax, or reinterpret the empirical gate.

The new target is the missing downstream question:

> When a repeated-check live-trapping protocol is represented as one SCR occasion per night, how much can the spatial scale parameter sigma differ from the estimate obtained when each trap check is retained as its own occasion?

## Key rebuttal incorporated into the design

A natural objection is: "Why not make each trap check an SCR occasion?"

Therefore the simulation compares three representations of the same generated detections:

1. CHECK — every trap check is its own SCR occasion;
2. FIRST — one occasion per night, retaining the first detection within that night;
3. LAST — one occasion per night, retaining the last detection within that night.

CHECK is the information-preserving reference representation. FIRST and LAST are one-location-per-night reductions.

## Phase 1: aggregation only

Phase 1 deliberately includes no post-handling behavioural displacement. This isolates temporal aggregation itself. The San Jacinto protocol used three checks per night, released animals at the point of capture during each check, and trapped for three consecutive nights per monthly bout. The 1--4 check axis therefore treats three checks/night as the empirical centre and adjacent values as a generality sensitivity.

Data are generated with the R package `secr` on a 7 x 7 multi-catch detector grid with 6.25 m spacing, matching the San Jacinto geometry.

Frozen pilot settings:
- nights = 3;
- checks per night = 1, 2, 3, 4;
- true sigma = 12.5 m;
- centre detection probability = 0.15 per check;
- population density = 30 animals/ha;
- population buffer = 100 m;
- fit mask buffer = 75 m;
- conditional likelihood (`CL = TRUE`);
- detector = `multi`;
- matched generating and fitted detection function;
- detection functions = HN and HHN.

For HHN, lambda0 is chosen so that g(0)=0.15:
`lambda0 = -log(1 - 0.15)`.

## Why HN and HHN are both required

For a probability half-normal detector,

`g(d) = g0 exp(-d^2/(2 sigma^2))`.

Across C independent checks, the probability of at least one detection at a detector is

`1 - (1 - g(d))^C`,

which is generally not another probability half-normal curve.

For a hazard half-normal detector,

`lambda(d) = lambda0 exp(-d^2/(2 sigma^2))`,

and

`g(d) = 1 - exp(-lambda(d))`.

Across C independent checks, cumulative hazard becomes `C lambda(d)`, so the marginal at-least-one-detection probability remains hazard half-normal with the same sigma and a scaled intercept.

This closure argument is exact for detector-level detection probability. It does not by itself prove that retaining only one detector location per night is harmless for multi-catch capture histories. The simulation tests the full capture-history consequence.

## Primary outputs

For every replicate and representation:
- fitted sigma;
- relative sigma error versus generating sigma;
- fit success/failure.

For FIRST and LAST:
- relative sigma difference versus CHECK;
- FIRST-vs-LAST sigma difference.

For the generated CHECK history:
- number of repeat-detected individual-nights;
- fraction of repeat-detected nights whose first-to-last detector distance is >= one trap spacing;
- median first-to-last distance among changed repeat-detected nights.

The latter two quantities allow direct calibration against the held-out San Jacinto pattern without fitting any empirical SCR effect.

Observed calibration band used only for interpretation:
- repeat-night material-shift fraction roughly 0.69-0.73;
- changed-night median first-to-last distance roughly 12.5-14 m.

## Pilot decision

The pilot is a code-and-mechanism check, not the final Monte Carlo analysis.

Advance to the final simulation grid if:
1. CHECK sigma recovery is acceptably centred under both matched detection functions;
2. the one-check condition gives no systematic FIRST/LAST/CHECK separation;
3. increasing checks per night produces interpretable changes without widespread fit failure.

No empirical sigma estimate is opened at any stage.
