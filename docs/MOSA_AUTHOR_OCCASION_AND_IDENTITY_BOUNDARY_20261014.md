# MOSA authoritative capture occasions and individual-ID boundary (2026-10-14)

**Scientific status: source-provenance correction, external MOSA ecological effects remain SEALED.**

## Byte-verified sources

The published Zenodo 2023 MOSA raw captures contain 49,216 records, including
45,433 Mastomys natalensis records with 19,818 distinct TOE strings.
The author's public processing RMarkdown loads the GitHub source in
Joachimmarien/MOSA, commit 298283987854d7423205f422ed3c59399afbb7b2.
Its raw CSV has the same canonical Git blob SHA-1
(6463d3561d7d4fa6d43ecd6d482430b00ae64919) as the Zenodo original
(MD5 12c04902947b91922c3f6c98760ecb54). The two publicly pinned
sources therefore have **identical bytes**. A GitHub-versus-Zenodo
source version difference is excluded as the explanation of the count mismatch.

The author time-variable table (MD5 ca051ba1fafee9f384be976730a5e84e)
holds 363 exact three-consecutive-night primary trapping occasions,
with 1,089 unique nights; 59 occasions cross calendar months.
The older screen of 182 calendar months containing exactly three
consecutive MN-capture dates is **not** the authors' occasion filter.
The earlier 135/140 omission result applies only to that conservative
proxy and must not be cited as 135 author-excluded tagged animals.

## Correct original-versus-author code roster audit

| Structural property | Count |
|---|---:|
| Raw MN distinct TOE values | 19,818 |
| Author MN matrix distinct TOE values | 19,678 |
| Raw MN TOE values absent from author MN matrix | 140 |
| Missing codes with all original captures off authors' official dates | 119 |
| Missing codes with any raw MN capture on author dates | 21 |
| Those with a valid in-grid capture on an author date | 11 |
| Among those 11, also seen in the authors' species-NA matrix | 10 |
| Missing codes captured at valid grid stations on at least two author dates | 7 |
| Among those 7, also seen in author species-NA rows | 6 |
| Two valid dates, no flagged capture, absent from both author MN and NA | **1** |

These counts are nested or overlapping, not additive.
Matching a TOE value in the species-NA matrix is **not** evidence that
the underlying animal was Mastomys natalensis.
Likewise, on-date raw MN data are not guaranteed to survive every
published intermediate preprocessing step.

The published claim of 19,850 unique MN individuals remains unresolved.
The author MN matrix has 19,692 rows (14 more than 19,678 distinct TOE
values), plus 158 species-NA rows. The exact arithmetic
19,818 - 140 + 14 + 158 = 19,850 matches total author matrix **rows**,
NOT validated unique MN animals. It cannot repair the identity discrepancy.

## Biological inference boundary

Until the author source-to-matrix identity crosswalk is reconciled,
do not calculate or infer external MOSA MNA or spatial variance W/B
against local abundance. Never invent 32 identities, split TOE codes
post hoc or relabel species-NA rows. A one-site Mastomys series cannot
rescue the failed NEON development 6/8 genera test nor the inestimable
future five-genus mode test. NEON's provisional Peromyscus positive
density-variance response did not replicate in direction with adequate
precision, and no temporal biological regime flip is established.

The author's RMarkdown has additional date-specific deletions, a documented
2004 date correction and an explicit exclusion of the reserved
NO_CAPTURE TOE string. Whether that exact reserved value explains the
sole two-night valid-station residual is a **separate source check**.
No TOE strings or per-individual spatial histories are disclosed here.

## Provenance

- Author time schema: https://github.com/zuizui0223/neon/actions/runs/38420996118
- Author official occasion source reconciliation:
  https://github.com/zuizui0223/neon/actions/runs/38421811063
- Missing code subgroup count:
  https://github.com/zuizui0223/neon/actions/runs/38422828399
- GitHub-versus-Zenodo byte equivalence:
  https://github.com/zuizui0223/neon/actions/runs/38423788306

Next: finalize reserved-code verification. If the one residual is not a
documented non-animal placeholder, ask the authors for the exact
MOSA source-to-encounter-matrix row mapping and their unique MN animal
count definition before unlocking any ecological effect.
