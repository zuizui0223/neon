# MOSA biological identity — pre-effect decision boundary (15 October 2026)

## Decision
**Structural predictor support: GO. Biological-animal identity and spatial ecology: HOLD.**

The checksum-verified authors' first-retained-species roster contains 19,678 normalized MN-labelled TOE codes. Fourteen whitespace-normalized collisions are excluded in the frozen conservative predictor audit. The strict within-month, three-consecutive-MN-capture-night rule supports 153 months; 22 calendar years have at least two MNA levels and 147 eligible months fall in those years. This is adequate *structural* support, not evidence for an ecological effect. The published 19,850 encounter-matrix rows do not establish 19,850 distinct biological MN animals.

## Next effect-blind identity gate
1. Using exactly the original verified source bytes, author RMarkdown date edits, first-retained species assignment, and published matrix, construct a tag-by-date-by-station conflict audit. Preserve raw verbatim TOE, normalized TOE, species, sex (if reported), date and coordinates in private computational intermediates; export aggregate counts only.
2. Check simultaneous contradictory positions for the same code and capture night; conflicting species/sex labels; anomalous first–last histories; and codes appearing in the authors' matrix more than once after normalization. Do not interpret a long time span alone as proof of reuse.
3. For the frozen 153 eligible months, quantify **without computing W, B, centroids or MNA-spatial slopes**: how many repeat-supported tags, months, and calendar years are affected by ambiguous identities. Keep the denominator as the original 153, not a newly selected favorable cohort.
4. Distinguish (a) demonstrably contradictory identity, (b) plausible but unverified identity, and (c) no detected conflict. Absence of detected conflict is not proof that one code equals one biological animal. The 14 whitespace collisions are already excluded; never silently merge or split other codes.
5. Seek original authors' clarification of the biological individual definition and handling of recycled TOE codes. Record the answer or absence of an answer and whether the published identity can be reproduced.
6. **Do not unseal W/B or MNA effects** until a separately documented decision states whether identity ambiguity can affect the primary 153-month cohort, and the original preregistered inclusion rule is satisfied. If the rule cannot be established, STOP. No substitution of the authors' 363 bouts or post-outcome threshold changes.

## Biological question, if released
Does increasing local abundance in a single long-term *Mastomys natalensis* population covary with changes in within-animal short-term capture-coordinate variance W versus among-animal observed centroid variance B? The primary locked coefficient is the MNA slope of Delta=B-W, with month and year fixed effects and year-block uncertainty. Strong packing additionally requires beta_W<0 and beta_B>=0. Also report W+B and detection/cohort sensitivity.

## Inferential boundaries
- One Tanzanian grid is one independent site; repeated years do not create independent populations.
- The 30×10 lattice is not geometrically equivalent to NEON's 10×10 grid.
- MNA is a marked-animal abundance index, not true population density.
- Neither a positive nor negative MOSA result rescues NEON's failed 6/8 genus criterion, its inestimable five-genus future confirmation, or the imprecise Peromyscus holdout.
- No territory, active avoidance, competition, home-range mechanism or causal density effect can be claimed from three-night trap coordinates alone.

## Evidence
- `results/mosa_frozen_conservative_mna_support_receipt_20261015.json`
- `results/mosa_exact_author_identity_replay_receipt_20261015.json`
- `results/mosa_author_verified_bout_support_receipt_20261015.json`
- `results/mosa_one_species_spatial_allocation_pre_effect_contract_v1.json`
- GitHub Actions 38703326511 (structural gate PASS).

## 2026-10-15 refinement: distinguish code reuse from harmless capture duplication

A capture row is not a biological individual, and multiple rows for the same code on the same night are not automatically distinct animals. The identity audit must report **three separate denominators**: all author-first-MN normalized codes, the 19,664 codes remaining after the 14 known whitespace collisions, and the subset contributing repeated positions to the frozen 153-month cohort. Report the number of affected months and years, not just the number of anomalous rows.

For each retained code and date, aggregate the set of *distinct valid station labels*; classify (1) one station with multiple records as repeated logging, (2) multiple stations on one date as spatially conflicting capture histories requiring source/field interpretation, and (3) cross-species or incompatible sex records as identity concerns. Do not assume two stations on one date necessarily indicate two animals without checking the capture protocol. For the W/B cohort, count a code as potentially influential only if it appears on >=2 different nights within a frozen eligible month. The **potentially affected** count is an upper bound, not a measured W/B bias.

Do not mistake the absence of >24-month histories among the selected codes for definitive identity proof. A reused code within a shorter interval may still be possible; conversely a long history can represent a genuine long-lived animal. The only safe ecological inference remains HOLD until this uncertainty is characterized.

## 2026-10-16 source-verified identity and FLAGS audit — new evidence, HOLD retained

Successful GitHub Actions runs **38759043826** (first identity conflict audit)
and **38759703345** (correction `FLAGS` and literal TOE-series check) used
the same MD5-verified published capture source, the original authors' exact
55 date removals/one correction, the first-retained MN roster and the **same**
frozen strict 153-month cohort. Both runs recomputed the original month-by-
month repeated-individual m support exactly. The synthetic tests and the
general frozen-paper checks passed.

**Source-level counts, not biological effects:**

- **19,678** authored first-MN normalized codes; **14** whitespace
  collisions remain excluded; **19,664** noncolliding codes.
- **6,530** distinct repeated-code × month units for the 153 fixed months,
  representing **4,875** repeat-supported distinct codes.
- **41** code/date keys observed at more than one valid station in the full
  author-retained source; **13** such keys are in the frozen eligible months;
  **169** same-code/date keys repeat the **same** station.
- **38** distinct code labels account for the 41 multi-station same-day
  keys; all **38** already have explicit slash-delimited series prefixes.
  No station-warning code has a literal trailing ` B` suffix.
- Across the full retained first-MN code history, **one** code has both
  known `SX` sexes; **zero** have two different known species labels.
- **11** suspect code labels enter repeat-supported cohorts, in **15** of
  **6,530** repeated-code/month units. Their presence creates an upper
  bound of **14 of the original 153 months (9.2%)** potentially affected;
  same-month direct station conflicts affect **10** months. It is false
  to call the remaining 139 months independently verified true individuals.
- Of **44,426** author-retained species-MN capture rows under first-MN
  codes, **5,430** contain a nonblank `FLAGS` value. Nevertheless,
  **0/41** multi-station same-day keys have any flagged entry; none of
  the 38 station-warning codes has a `FLAGS` entry elsewhere in its
  retained species-MN history. Nonblank `FLAGS` do not prove an identity
  error is resolved; blank `FLAGS` do not prove an error.

Published protocol says trap checking takes place once each morning;
the DATE is the morning a trap was checked. Multiple distinct stations
assigned to the same code and morning require source-level explanation.
The authors *also* document toe-series prefixes and a `B` suffix as
disambiguation, as well as sex/species/capture-note corrections. Thus
multi-station keys cannot simply be treated as biological repeat moves
or definite tag reuse. See Leirs et al. 2023,
https://doi.org/10.1038/s41597-023-02700-3.

**Decision:** This audit narrows the potential contamination footprint,
but does not reconcile the article's reported 19,850 MN biological
individuals or identify what happened to the 41 conflicting code/day
locations. The next decision requires author documentation of the
canonical individual-to-TOE mapping, or a formally recorded STOP.
No W/B, centroids or MNA–space coefficients may be opened as a
consequence of this audit. Do not lower eligibility or retrospectively
replace the original cohort with author-363-bout sensitivity.

Artifacts:
- `results/mosa_effect_blind_identity_conflicts_receipt_20261015.json`
- `results/mosa_effect_blind_identity_flags_receipt_20261016.json`
- `docs/MOSA_PUBLISHED_INDIVIDUAL_ID_AUTHORS_CLARIFICATION_20261014.md`
  (corrected query draft only; **not sent**).

## Author encounter matrix cannot settle same-day station contradictions

The published processing RMarkdown's *encounter-matrix conversion* constructs
one binary capture column per retained date with
`df[i,pmatch(ID2$DATE,date)]=1`. It saves the source fields for **only
the first captured record** as `character=rbind(character,ID2[1,4:12])`.
Multiple source rows for a TOE on one date are consequently collapsed to a
single capture indicator, **not** adjudicated as one of two different station
coordinates. The matrix also retains first-record X/Y characteristics, not
a per-night trajectory.

Thus the authors' verified encounter matrix is authoritative for the
calendar and first species-label crosswalk, but **cannot independently
resolve** which source trap position, if any, is correct for the 41
same-day/multiple-station code/date keys. It must not be reinterpreted as
proof of biological identity or used as an invented spatial response
dataset. See the original authors' publicly released RMarkdown:
https://github.com/Joachimmarien/MOSA/blob/main/2_markdown%20Processing%20data.Rmd.

An independent experimental/protocol note is required for same-day
multi-station captures and toe-code reuse, not merely the encounter
matrix's binary row label. This is a missing interpretation of capture
events, not an invitation to select the convenient first or last station.

## 2026-10-16 completed exclusion sensitivity — all original bouts retain support

The result was frozen **before** computation in
`docs/MOSA_EFFECT_BLIND_WARNING_EXCLUSION_STRESS_TEST_20261016.md`.
The exact original-source/checksum-verified
[GitHub Actions 38818948192](https://github.com/zuizui0223/neon/actions/runs/38818948192)
completed successfully with the 153 original month identifiers, 6,530 repeated-code/month units and the original MNA predictor all unchanged.

**Observed sensitivity:** discard all **39** author-first-MN code labels with
any observed full-history same-day multi-station warning (38 codes), known
male/female SX inconsistency (1 code), or known between-species
inconsistency (0). The original 14 affected months lose one repeat-supported
code in 13 cases and two in one case. The remaining 139 months lose none.
**All 153/153** retain >=5 repeated individuals, with post-removal minimum
m exactly **5**. **All 22** original MNA-varying years remain, with **147**
eligible months in those years. The original 60-month, 10-year source
support thresholds thus pass without altering any primary cohort.

**This is a narrow but useful biological-data feasibility result.** The
observed explicit conflicts are too sparse to destroy the repeated-animal
support needed to *ask* the cross-scale population question. It does
**not** establish that every unflagged tag denotes one true animal,
that original MNA is unbiased, or that W/B or Delta density associations
are identifiable. A sensitivity support result is not a measured
biological spatial effect. The article's 19,850 MN individual-to-TOE
mapping and 41 same-day/multi-station source keys remain unresolved.

**STOP the loop of further opportunistic same-data ID checks.** The next
scientific dependency is an external authoritative corrected-ID table or
written interpretation of the toe-code and same-day station capture
protocol. Until then keep the MOSA W/B and MNA×space analysis sealed and
the ecological PR in Draft/HOLD. Do not convert a stress-support PASS
into an override of the pre-effect source identity requirement.

Reproducible record:
`results/mosa_warning_removal_support_receipt_20261016.json`.
