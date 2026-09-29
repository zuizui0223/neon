# San Jacinto temporal-aliasing holdout — estimability design v1

Date: 2026-09-29

Status: frozen before any held-out first-vs-last positional difference is calculated.

## Discovery that motivated this independent validation

In the completed four-heteromyid San Jacinto programme, first and last nightly capture locations differed on 50.7% of analyzed individual-nights, and the family repeated-night movement estimate changed from +0.1128 using first nightly capture to -0.0091 using last nightly capture. Those observations are discovery evidence only.

## Held-out taxa

The same public capture file contains three non-heteromyid species whose first-vs-last temporal-aliasing outcomes were not computed in the completed programme:

- PEMA — Peromyscus maniculatus
- PEER — Peromyscus eremicus
- REME — Reithrodontomys megalotis

These three Cricetidae form the only confirmatory sample for this programme.

## Source

Figshare article 18295520 v1, `year round trap data.csv`, SHA256 `ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301`.

Fixed trap geometry: 7 x 7 flags A1-G7, 6.25 m spacing.

## Frozen preprocessing

Use the same deterministic structural rules established before the heteromyid effects:

- two-digit years map to 2000-2099;
- global trapping bouts are blocks of distinct capture dates separated by gaps <= 7 days;
- nocturnal time order maps 7-11 PM to 19-23, 12 to 24, and 0-6 to 24-30;
- identity key = grid × species × unique_ID;
- rows lacking unique_ID, valid canonical flag, valid date, or valid nocturnal time are excluded.

Sex is irrelevant to this programme and is not used.

## Effect-blind support quantities

A repeat-capture individual-night is a grid × species × unique_ID × date with >=2 valid raw capture records.

A movement-eligible individual-bout is a grid × species × unique_ID × bout with valid nightly states on >=2 distinct dates.

A movement support event is species × grid × bout with >=10 movement-eligible individuals.

## Species estimability gate

A held-out species qualifies only if all are true:

- >=100 repeat-capture individual-nights;
- repeat-capture nights occur in >=2 grids;
- repeat-capture nights span >=6 trapping bouts;
- >=5 movement support events;
- movement support events occur in >=2 grids.

The programme advances to an effect lock only if >=2 of 3 held-out species qualify.

Pass decision: `authorize_temporal_aliasing_effect_lock`.

Fail decision: `stop_temporal_aliasing_holdout_not_estimable`.

## Effect boundary

At this stage:
- first-vs-last distance values inspected: false
- first-vs-last changed/not-changed outcomes inspected: false
- first-vs-last movement sensitivity inspected: false
- packing stability inspected: false
- ecological/model fits: 0

No support threshold may change after held-out support counts are opened.
