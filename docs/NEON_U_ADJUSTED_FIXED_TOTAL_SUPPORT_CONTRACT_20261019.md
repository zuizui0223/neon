# NEON conspecific–congeneric fixed-total contrast: historical U-adjusted predictor-only support

**Frozen 2026-10-19, before computing real NEON N/F/U conditional predictor geometry.** This is an extension of the already-approved ecological question in `docs/NEON_FIXED_TOTAL_COMPOSITION_TEST_20261019.md`, NOT a new ecological hypothesis selected after looking at new W/B associations. Do not change the original historical eight-genus denominator or any prior hypothesis status.

## Biological question

At the same genus-level known-alive abundance N, with the same count of animals whose species is uncertain U, are focal conspecific F and same-genus heterospecific C distinguishable in observed NEON source data? If yes, future new-capture-event data can ask whether replacing one congener by one conspecific is associated differently with the **within-individual W** and **among-centroid B** observed spatial variance. The original frozen primary target remains Θ=[β(F,B)−β(F,W)]−[β(C,B)−β(C,W)] with a two-sided interpretation.

## Source and date boundary

- Use exactly the original `RELEASE-2026` target response *structural* universe of 1,536 taxon×plot×event sessions, its target individual/site/plot taxonomic histories, and the previously documented qualifier-sensitive interpretation of species groups, history-level taxon switches, and explicit nonblank `identificationQualifier` values.
- No download of additional response data beyond the already-running **predictor-only** NEON source reconstruction. The 2025–2026 provisional and past W/B observations remain **consumed**, not a new holdout.
- Preserve each original 1,536 response session, the 47,360 tagged histories, 104,322 target captures and 176 varying genus MNKA series. Use only species-ranked response taxa; series must contain >=3 original structural events. All genera are retained in a completeness readout; *Peromyscus* is the already frozen priority, never selected from a newly positive response coefficient.
- Baseline (field single-species histories) and history-level conservative qualifier sensitivity are **both** reported, not selected by the better predictor rank.

## Predictor-only model geometry and exact algebra

For every supported focal-species response row reconstruct F (focal species), C (other species of same genus) and U (unresolved genus) from event-level known-alive history intervals, with exact N=F+C+U. Do not redistribute U into any chosen species.

Use **the exact original nuisance effects Z**: intercept + focal taxon×site×plot series, site×calendar-month, and calendar year. On the same qualified rows, compute:

1. rank of [F,C] after Z (must reproduce the prior F/C-only rank);
2. rank/condition of [F,C] after [Z,U]; rank of [F,C,U] after Z;
3. whether `β_F−β_C` is identifiable even if all three underlying slopes are not separately identifiable (projection of contrast onto row space);
4. squared residual predictor information for F after [Z,N,U], equivalent to holding the **total and unknown fraction** fixed; do not treat this as precision or a biological effect estimate;
5. descriptive concentration of this conditional information among **physical NEON sites** (number of contributing sites, top-one/top-three share, Kish-equivalent number of sites), WITHOUT filtering favorable sites.

## Fixed source-only eligibility rule and interpretation

A genus is a **candidate source-predictor comparison, NOT an ecological GO** only if it was already above all frozen F/C-only thresholds (>=60 sessions in >=3-event series, >=6 sites, >=8 series, >=5 series jointly varying F/C, conditional rank two and condition number <=30 **in the original F/C-only screen**) AND:

- rank [F,C] | [Z,U] == 2;
- condition number for [F,C] | [Z,U] is finite and <=30;
- fixed-total contrast `β_F−β_C` estimable and squared F | [Z,N,U] residual information > numerical tolerance.

Report both historical field-label and qualifier-conservative outcomes and all physical-site information concentration. **No additional effective-site threshold is invented here**: a concentration-equivalent-site number is descriptive, not a substitute for site-cluster inference or for the existing >=6 actual-sites rule. Low independent-site concentration can still warrant prospective design HOLD despite nominal rank.

No U-adjusted check can classify stable field species labels as genetically correct. The earlier source-level matches to NEON BOLD have `identificationMethod=morphology`, and the provider `identificationHistory` language indicates molecular revision rationales without demonstrating per-individual verified DNA assignments. A rank or source-support PASS is only design feasibility, not enough to release future W/B outcomes.

## Mandatory stop and privacy guards

- A source cohort mismatch (original 1,536 target sessions, tagged histories, target capture rows, 176 varying series, original baseline and qualifier F/C support summaries) raises STOP.
- No real tag IDs, sample IDs, event IDs, real-valued coordinates, per-individual records or newly joined W/B are exported. Only group counts and predictor residual moments.
- No re-estimation of the already-consumed W/B or Δ responses. Prior cross-genus preregistered 6/8 gate **FAILED at 5/8**; provisional Peromyscus positive sign **NOT REPLICATED/IMPRECISE**; future five-genus mode **NOT ESTIMABLE**; MOSA spatial ecological effects **SEALED**.
- In case of a negative rank result, report **STOP** instead of weakening taxonomic constraints or fit selection. If source-only support is positive, the next study still needs an **unseen independent future capture-event cohort**, explicit taxonomic validation and capture-detection assessment before any ecological density–space inference.
