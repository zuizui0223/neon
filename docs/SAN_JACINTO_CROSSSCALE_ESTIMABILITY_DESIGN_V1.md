# San Jacinto held-out cross-scale estimability design v1

Date: 2026-09-29

Status: frozen before any species-by-sex support counts or ecological effect are computed.

## Focal held-out heteromyids

- LAPM — Perognathus longimembris brevinasus
- CHFA — Chaetodipus fallax
- DKR — Dipodomys simulans
- SKR — Dipodomys stephensi

None of these species had sex-specific packing or recapture-movement outcomes inspected in the completed Portal/NEON programme.

## Source and fixed geometry

Figshare 18295520 v1, file `year round trap data.csv`, SHA256 `ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301`.

Each grid uses the published fixed 7 x 7 geometry A1-G7 with 6.25 m spacing. Absence of a capture at a flag does not remove that flag from the active geometry.

## Trapping bouts

Trapping bouts are reconstructed from the union of capture dates over all grids, without reference to species or sex.

Sort distinct dates globally. Start a new bout when the gap from the previous distinct capture date is > 7 days. The source is expected to yield approximately monthly bouts over August 2015-July 2016.

If this deterministic rule produces fewer than 10 or more than 14 bouts, stop before species/sex support counts.

## Nocturnal time ordering

The `time` field is interpreted as a 12-hour nocturnal clock:
- hours 7-11 -> add 12 (evening);
- hour 12 -> 24 (midnight);
- hours 0-6 -> add 24 (post-midnight);
- minutes are retained as fractions of an hour.

Rows with unparseable time are excluded from nightly first-location construction.

## Individual identity and sex

Identity key: `grid × species × unique_ID`.

Rows lacking `unique_ID` are excluded.

Within each `grid × species × unique_ID × bout`, normalize sex to M/F and require exactly one non-missing sex state. If none or if both M and F occur, that individual-bout is excluded from both endpoints.

Sex is propagated only within the same trapping bout. It is not borrowed from another month.

## Nightly state

For each eligible individual on each capture date, retain exactly one location: the row with the earliest parsed nocturnal time. Ties are broken by original source row order.

The resulting flag is the individual's nightly state used by both cross-scale endpoints.

## Packing estimability endpoint

Unit: species × grid × capture date.

A primary packing session requires at least:
- 3 resolved male nightly states;
- 3 resolved female nightly states.

N>=2/sex is retained only as an estimability diagnostic and cannot authorize effects.

A species passes the packing side when it has >=10 primary sessions across >=2 grids.

## Movement estimability endpoint

Unit: species × grid × trapping bout.

An individual is movement-eligible in a bout when it has nightly states on >=2 distinct dates in that bout.

A primary movement event requires at least:
- 3 movement-eligible males;
- 3 movement-eligible females.

N>=2/sex is diagnostic only.

A species passes the movement side when it has >=5 primary events across >=2 grids.

## Cross-scale matched-grid gate

For a species to qualify:
- packing gate passes;
- movement gate passes;
- >=2 grids occur in both the packing-eligible and movement-eligible sets;
- within those overlapping grids there are >=10 packing sessions and >=5 movement events.

The programme advances to an effect-analysis lock only if >=2 held-out species qualify and those species span >=2 heteromyid genera.

Pass decision: `authorize_san_jacinto_crossscale_effect_lock`.

Fail decision: `stop_san_jacinto_crossscale_not_estimable`.

## Effect boundary

At this lock:
- species-by-sex support counts inspected: false
- packing effects computed: false
- movement distances computed: false
- ecological effect models fit: 0

No threshold, identity rule, bout rule or cross-scale gate may be altered after the support counts are opened.
