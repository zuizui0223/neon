# MOSA published individual-identity clarification — corrected 2026-10-15

**Status:** prepared research correspondence, **not sent**. Supersedes the
2026-10-14 five-question request, because the exact author RMarkdown replay
resolved the earlier apparent one-code exception and all 140 raw MN codes
absent from the processed MN matrix.

## Provenance verified independently of spatial responses

- Leirs et al. (2023), *Scientific Data*, DOI:
  https://doi.org/10.1038/s41597-023-02700-3.
- Original raw MOSA captures: Zenodo https://doi.org/10.5281/zenodo.10049811,
  MD5 `12c04902947b91922c3f6c98760ecb54`, **49,216 rows**,
  including **45,433 raw MN-labeled capture records**.
- The authors' 55 original-date deletions and one 2004-04-13 correction,
  with first retained TOE species label, reproduce all **1,089 dates** and
  **363** three-night occasions exactly.
- Original 19,818 distinct raw MN TOE strings minus 140 not in the author
  MN matrix are **fully accounted for**: 120 absent from retained dates;
  18 initially species NA; 2 initially species TA. This is NO LONGER a
  missing-tag provenance question.
- The processed matrices contain **19,692 MN-labelled rows** comprising
  **19,678 normalized MN TOE labels** (14 whitespace-normalization
  collisions), plus **158 initially species-NA rows**. The paper's
  **19,850 MN biological individuals** cannot be inferred from those
  19,850 matrix rows.
- The frozen 153-month, 22-MNA-varying-year one-site conservative audit
  passes its *predictor-only structural* gate.
- New full-source effect-blind audit (run 38759043826) found 41
  same-code/same-calendar-date valid-station keys containing more than one
  trap location (13 keys in frozen eligible months), 169 same-station
  duplicate keys, 1 MN-first-label code with conflicting observed `SX`,
  and zero MN-first-label codes changing among known species labels.
  Any code-station/sex warning intersects repeat-supported captures in
  **14 of 153 frozen months** (15 of 6,530 repeated-code/month units).
  These are upper-bound structural warnings, **not estimated W/B bias**.
- The paper explicitly documents (i) TOE series prefixes and appended B
  for repeated patterns; (ii) corrections to raw sex/species/TOE fields
  using original paper notes; and (iii) `FLAGS` indicating corrections.
  Therefore anomaly counts must not be interpreted as biological
  identity reuse without examining those corrections.

## Remaining questions appropriate for the original authors

1. Does the reported total of **19,850 distinct Mastomys natalensis animals**
   refer to a separately corrected animal-identity product? The original
   MN-labelled capture codes and the authors' MN encounter matrix have
   19,818 and 19,678 unique normalized toe labels respectively; 19,850
   equals the *entire* author encounter matrix row count including 158
   species-NA rows. Can the authors identify the canonical biological
   individual count and archived mapping?
2. On one trapping date, how should same-TOE capture records at **multiple
   valid stations** be interpreted after raw flags and the original
   toe-correction steps? Are prior/superseded rows retained as extra capture
   entries, or are two consecutive actual captures in one morning possible?
   We can share individual raw row keys privately if needed.
3. Which `FLAGS` entries indicate corrected toe identity or station
   coordinates rather than other characteristics, and is there an
   authoritative correction log linking old and new entries? How should
   the published explicit prefix and B suffix rules be handled when a
   label conflict survives the author-date/species reconstruction?

No unresolved 140-code roster question or invented 32-code split is requested.

## Proposed concise email — **NOT SENT**

Subject: Clarification on biological TOE identities in the 2023 MOSA CMR archive

Dear Dr Mariën and coauthors,

We are preparing an independent analysis of the public long-term MOSA
capture–mark–recapture archive and have reproduced the original processing
RMarkdown's 55 date deletions, one date correction, 363 primary occasions,
and first-retained species labels exactly. Thank you for providing such a
valuable and thoroughly documented dataset.

Before using within-individual repeated positions, we would appreciate
clarification of three remaining identity points: (1) whether the paper's
19,850 distinct MN individuals correspond to a corrected individual-ID
mapping, rather than the full 19,850 encounter-matrix rows (which include
158 species-NA rows); (2) how same-TOE/same-date captures at different
stations should be interpreted after source corrections; and (3) whether
the `FLAGS` or another archived lookup identifies superseded or corrected
TOE/station entries.

Our checks use the exact checksum-verified 2023 Zenodo source and we can
supply a compact reproducibility receipt or affected raw-row references
privately. No spatial ecology effects have been analysed on this dataset.

Thank you for any guidance you can provide.

Best regards,
[research team]

## Scope / inference rule

A MOSA effect will remain **HOLD** until this biological ID issue is
documented and a separate pre-effect release is recorded. A positive
one-site MOSA density–space association would not reverse the failed
NEON multigenus criterion or identify territorial mechanisms.

Evidence:
- `results/mosa_exact_author_identity_replay_receipt_20261015.json`
- `results/mosa_frozen_conservative_mna_support_receipt_20261015.json`
- `results/mosa_effect_blind_identity_conflicts_receipt_20261015.json`
- GitHub Actions https://github.com/zuizui0223/neon/actions/runs/38759043826

The correspondence above is a draft in the repository only. It must not
be presented as already sent or answered.
