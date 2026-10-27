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
