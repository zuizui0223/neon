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
