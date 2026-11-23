# San Jacinto intra-night positional aliasing — held-out effect lock v1

Date: 2026-09-29

Status: frozen before any PEMA/PEER first-vs-last positional outcome is calculated.

## Discovery and holdout separation

The discovery sample was the four heteromyid species analyzed in the completed San Jacinto cross-scale programme. In that discovery sample, first and last nightly capture positions often differed.

The confirmatory sample here is restricted to two Cricetidae whose first-vs-last outcomes were not inspected:

- PEMA — Peromyscus maniculatus
- PEER — Peromyscus eremicus

REME is excluded prospectively because the effect-blind support scan found no repeat-capture individual-nights.

Species were selected for this confirmatory programme only from effect-blind support counts.

## Unit and preprocessing

Unit: repeat-capture individual-night = grid × species × unique_ID × date with >=2 valid capture records.

Use:
- fixed 7×7 A1-G7 geometry, 6.25 m spacing;
- valid unique_ID only;
- valid canonical flag only;
- valid source date;
- valid nocturnal time using the frozen 19-30 h ordering;
- first location = earliest nocturnal capture;
- last location = latest nocturnal capture;
- source-row order breaks exact time ties.

No sex variable is used.

## Primary endpoint

`changed = 1` if first and last capture flags differ; otherwise 0.

For each held-out species:
- estimate changed fraction across all repeat-capture individual-nights;
- compute a two-sided 95% Wilson interval.

## Confirmatory aliasing threshold

A species shows practically important intra-night positional aliasing only if:

1. changed fraction > 0.25;
2. lower 95% Wilson confidence bound > 0.25;
3. among changed nights, the median Euclidean first-to-last distance is >= 6.25 m (one trap spacing);
4. the species has at least 100 repeat-capture individual-nights spanning >=2 grids and >=6 trapping bouts, as already established effect-blind.

The programme passes only if **both PEMA and PEER** satisfy all four conditions.

Pass decision: `confirm_intranight_positional_aliasing_across_cricetids`.

Fail decision: `stop_intranight_aliasing_not_replicated`.

## Secondary endpoints

Reported but non-rescuing:
- mean and median first-to-last distance over all repeat-capture nights;
- 90th percentile and maximum distance;
- median elapsed first-to-last time;
- changed fraction by grid and trapping bout;
- fraction moving >=1, >=2, and >=3 trap spacings;
- individual-level repeatability: for individuals with >=3 repeat-capture nights, proportion of changed nights;
- leave-one-grid-out changed fractions.

## Generality boundary

If confirmed, the allowed claim is narrow:

`In two held-out Cricetidae sampled on the same live-trapping grids, a practically important fraction of repeat-capture individual-nights change trap location within a night, so a single nightly location can alias intra-night space use.`

Not allowed:
- all small mammals;
- home-range inference;
- sex-specific movement;
- causal claims about foraging or territoriality;
- using this result to redefine the completed cross-scale programme.

At this lock:
- PEMA first-vs-last outcomes inspected: false
- PEER first-vs-last outcomes inspected: false
- distance values inspected: false
- changed/not-changed values inspected: false
- ecological/model fits: 0
