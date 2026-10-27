# NEON capture-fate availability and released-animal re-encounter feasibility
**Date: 2026-10-28. PRE-FATE-SOURCE-VALUES and PRE-FATE-STRATIFIED DAY2/3 OUTCOME design.**
**One integrated macroecology paper; no separate paper/methods line.**

## Ecological question and identified confound

The historically source-selected Microtus–Peromyscus difference in recorded night-2/3 re-encounters across seven NEON physical sites was -0.2351 (site-equal), after capturing marked animals on night 1. This was explicitly NOT calibrated capture probability. A key missing mechanism is that a first-night tagged capture may be dead, retained, lost or otherwise not safely released; non-return in that case cannot be attributed to station choice or capture response.

**Important new authoritative source:** The official NEON DP1.10072.001 RELEASE-2026 `mam_pertrapnight` contains a `fate` variable, with revised categories for 2017+ captured observations (NEON product data issue log, 2026). The existing NEON analysis loader discarded it; “not carried through by the loader” MUST NOT be summarized as “the raw source has no fate.”

**Concrete ecological test:** Does the historical difference in *observed* first-night-to-later-night re-encounter propensity persist when the first-night tagged animals are restricted to a source-confirmed released-alive category? This is a noncausal observation-process sensitivity, NOT an identifiable animal×trap detection probability, availability-independent survival, complete demographic turnover, or habitat-choice test.

## Source stage, NO later-night re-encounter outcomes opened

- **Original immutable source:** checksum+byte-verified NEON RELEASE-2026 DP1.10072.001, 2015-04…2026-09, 3,547 manifest entries / 1,773 `mam_perplotnight` source files / 1,707 `mam_pertrapnight` source files, original two-genus 158 adjacent-season comparisons across 30 physical sites, 293 unique original 3-night bouts.
- **Original predetermined source-selected contrast remains:** `Microtus` minus `Peromyscus` in the SAME seven original source-matched sites; 2026-10-26 design and source receipts are immutable; DO NOT pick new taxa/sites by fate or future re-encounter outcomes. Their original source first-night individual identities and genus conflicts are preserved.
- Add a strictly **opt-in** `fate`/fate-column-presence read to the loader; calling it without the new opt-in MUST output byte-for-byte equivalent original records, preserving original 158/58 counts and all published analyses. Never carry source site/plot/tag/trap/day identifiers in any public result.
- For each original source-eligible first-night marked animal of the fixed genera/sites, read ONLY the original **first-night** `mam_pertrapnight` `fate`. Do NOT read whether that animal was re-caught in nights 2/3 at this stage. Summarize: exact missing-column vs blank fate vs controlled category; first-night fate group counts, numbers of original sites having five or more known released animals of EACH original genus, and source-year category missingness. Do not print raw free-text `fate` (only controlled safe categories/indicators).
- Interpret codes only against the official original RELEASE-2026 `categoricalCodes_10072` (if source-accessible) or a source-confirmed, unambiguous restricted vocabulary: `released`/explicitly released alive vs `dead`/mortality, `escaped`/lost, `other` and `missing/ambiguous`. **Do not invent equivalences.** Retain ambiguity as non-eligible; a numeric or unfamiliar category requires source dictionary lookup and separate pre-effect addendum.
- A site/bout with genuinely missing fate is *missing observational eligibility*, never treated as 0 re-encounters or a released animal.

## One fixed source support gate (chosen BEFORE fate data and new outcomes)

To estimate the original fixed-genus, released-at-night-1 observational difference, require at least:
1. **Six of the seven ORIGINAL preselected physical sites**, each with ≥5 original night-one **confirmed released** tagged animals of BOTH frozen genera;
2. ≥**90 Microtus** confirmed released tagged first-night records AND ≥**220 Peromyscus** in those same source-qualifying original sites;
3. >=**80%** of the original fixed-genus first-night cohort must have an unambiguous controlled source fate (released or a documented nonrelease disposition), counting blanks and unknown as missing, *before* any later-night matching.
4. Original capture-status 4/5, authoritative target genus, original trap source coordinate, tag and original season-event membership, global genus/tag-conflict and duplicate-handling remain exactly as historically committed.

These thresholds are NEW post-result feasibility constraints and do not retroactively affect the original seven-site re-encounter difference. If any fail, report the source-only fate coverage and **STOP new biological outcome** without choosing other genera/sites or changing thresholds. If unavailable fate dictionary categories or no fate column, STOP.

## If AND ONLY IF the fate source gate passes

On the approved original site/genus cohort, compute night2-or-night3 recorded re-encounter fraction for first-night documented released individuals using the SAME original night-specific capture-status and ambiguous tag-history rules. Do NOT count known dead/unreleased/escaped tagged captures in the denominator; do NOT infer that a released individual remained alive or spatially available until night 3.

Site-level genus fractions -> **site-equal difference** Microtus minus Peromyscus on precisely source-eligible original sites; include all signs. Preserve whole-site bootstrap 2,000 draws seed `2026102801`; 95% percentile CI (2.5%,97.5%) and leave-one-original-site-out sign count. Report missing/fate disposition rates by genus before any inference.

A result with CI including 0 is **not support for a robust released-conditioned genus difference** and CANNOT be rescued by replacing source thresholds or a narrower taxon subgroup. A result excluding 0 is a *same-release sensitivity of observed return rate conditional on source-classified release*, NOT true p, capture experience, preference, habitat or a cause of cross-season trap recurrence. The old re-encounter effect is neither overwritten nor pooled with this.

## Reviewer safeguards

- Mortality/release/disposition code semantics may have changed in the original 2017+ period; report pre-2017 missingness, do not backward-infer. The source contains no independent observation of site occupancy or movements following release.
- NEON official product: https://data.neonscience.org/data-products/DP1.10072.001/RELEASE-2026 ; official latest 2026 guide/issue log states `fate` adjusted to revised post-2017 categories. Previous analysis loader discarded this field.
- The original 30-site positive conditional exact-station recurrence, the 17-site negative strict 10m neighboring-trap p=0.221, 18/158 confirmed six-night trap operability STOP, and 79/80 meteorological QC STOP remain unchanged.
- Data fidelity and honest STOP are more important than a positive new effect. Claim “genus-specific detection p caused recurrence” is PROHIBITED regardless of outcome.

---

## 28 October 2026 completed original source audit — 2017+ fate is `processed`, not missing

The original frozen seven-site, two-genus fate SOURCE stage returned `STOP_EXPLICIT_RELEASE_FATE_SOURCE_SUPPORT`: 615 original night1 marked captures, of which initial conservative classification recognized 102 explicitly released, 12 dead, 16 escaped, 94 blank and **391 nonblank 2017+ recorded `fate` strings it could not classify**. The static `categoricalCodes_10072` source dictionary was absent from the selected original monthly `/data/query` API response; this did **not** show the official dictionary did not exist.

A subsequent independently logged, **source-only** original-release inspection of the 391 previously unrecognized strings (`results/neon_fate_2017plus_unmapped_processed_source_receipt_20261028.json`; [Actions 40538157364](https://github.com/zuizui0223/neon/actions/runs/40538157364)) established that **all 391 are exactly `processed`**, and **none of these 391 are truly blank**. All 391 originate in 2017+ raw records. Therefore **"79% of records missing fate" is WRONG**; the figure 21.14% was recognition coverage of the initial narrow Python classifier, not completeness of NEON metadata.

The NEON 2023 [Small Mammal Sampling Protocol, Revision O, Appendix A](https://data.neonscience.org/documents/10179/1883155/NEON.DOC.000481vO/bde7eb23-ba45-8afb-05fa-9ca5667c3482) explicitly defines the field `Fate` as history/condition of capture, with `Escaped`, `Dead`, `Not Processed`, `Processed`. Animal release normally follows appropriate handling in the same protocol, but **a `processed` record is not a separate, individually observed alive-release event or proof the animal stayed available on nights 2–3**. The 102 explicit-release source values occur in the earlier era, further exposing the shift in field vocabulary.

**Precommitted ecological decision unchanged:** the strict source gate required unambiguously documented *released alive*, with at least six original seven sites containing five such tagged firstnight captures for each fixed genus, 90 and 220 confirmed releases respectively, and >=80% known unambiguous fates. We do not rewrite `processed` as an explicitly release-confirmed event after inspecting the label distribution. The original source result therefore stays **STOP**: no new release-conditioned later-night reencounter contrast was fitted, no true genus-specific trap detection probability inferred, and the historical Microtus–Peromyscus site-equal −23.5 percentage point observation remains unmodified. Future release/availability measurement requires an independent NEON field protocol/data dictionary matched to years or independently observed handling/detection records; not lowering old thresholds or cherry-picking a revised fate interpretation.
