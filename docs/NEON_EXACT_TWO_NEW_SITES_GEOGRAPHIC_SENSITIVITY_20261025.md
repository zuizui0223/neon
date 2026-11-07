# Precommitted post-result geographic non-overlap sensitivity for exactly-two-genera NEON recurrence
**Committed 25 October 2026 AFTER the full 30-site two-genus result and the original 14-site ≥3-genus result were opened, and BEFORE opening any ecological effect within the geographical non-overlap subset.**

This is **an additional post-result robustness/transportability diagnostic**, NOT an independently preregistered confirmatory study and NOT a new source release. The 2-row exact conditional uniform null, original tag-disjoint season pairing, original effort, geographic site blocking and null-coupling strategies remain the same.

## Source-only, outcome-independent selection

From the checksum-verified **same** original NEON RELEASE-2026 seasonal source:
1. Reconstruct the unchanged 58 original **≥3 genera** seasonal units, spanning exactly **14 original physical sites**. This source site set is the old *geographic comparator*, regardless of their old observed Z magnitudes.
2. Independently reconstruct the 158 **exactly-two** units spanning 30 sites. Keep **every exact-two pair whose physical site is NOT among the original 14 source sites**; exclude every other exact-two pair. The original source-only count is **17 distinct new physical sites**, with count of seasonal pairs and included domains to be reported **before** any new spatial overlap calculation. No one may choose those new sites by effect sign or environmental desirability.
3. Require ≥8 original independent new sites and ≥20 exact-two source pairs. If unmet, STOP biological effect.
4. Compute mathematically **exact two-row null PMFs** for every selected pair WITHOUT comparing observed genus×trap season A/B overlap; require ≥75% nondegenerate exact-null variance among this new subset, ≥20 informative pairs, and ≥8 informative new physical sites. If unmet, STOP the ecological analysis.
5. Only after those source and null-variance gates pass, compute observed new-site standardized two-genus recurrence Z for each informative pair; equal-weight within the site and then between the eligible sites. Retain all negative signs. Simulate **20,000** grand-site conditional null replicates under (a) unit-independent draws from exact PMFs and (b) within-site rank-comonotone shared quantiles (stress, not universal dependence bound), seeds precommitted **2026102555/56**. Report the observed site mean and both plus-one p-values, whether positive or not, no subgroup selection.
6. Historical source-season reuse sensitivity: remove **all original exact-two units from every physical site whose site×plot×season appears in >1 exact-two seasonal pair**, without inspecting outcome signs. Calculate an additional independent/rank-coupled null only if ≥8 new sites and ≥20 informative new-site pairs remain. Otherwise STOP this sensitivity; do not relax the rule.

## Outcome interpretation fixed before the new-site result

- A positive *both-couplings* result (positive equal-site Z, each conditional p<0.05) will support a **post-result sensitivity** showing that the positive exact-two result is not **solely** driven by the physical sites already used in the historical ≥3-genus NEON positive analysis.
- An inconclusive or negative result must weaken geographic generality; report it, do not substitute another favourable region or date threshold.
- Physical-site nonoverlap in the **same RELEASE-2026** establishes geographical source disjointness from the original 14 sites, **NOT** temporally new capture sampling, independent preregistration, independent habitat mechanism verification, or independent confirmation.
- Z and p from 2-genus and ≥3-genus models cannot be pooled: taxon richness differs and old sites may contribute other source-limited interactions. Two-genus new-site effects themselves still suffer genus-specific trap detection and unmeasured stable local microhabitat alternatives.
- Source-only site universe and no observed tag overlap are not verified mortality, birth or true population replacement. No density W/B, competitor mechanism, weather or CHM-effect fitting will be reopened.
- This is part of **one unified NEON macroecological manuscript**, not A/B or a new third paper.

**Source components:** `analysis/run_neon_two_genus_source_v1.py` original source reconstruction; `analysis/neon_exact_two_row_fixedmargin_v1.py` exact null; the new-source-only geographic comparator chosen by set difference of site IDs; `results/neon_exact_two_genus_ecological_receipt_20261025.json` historical 30-site result is for audit/provenance only, not subgroup sign selection.
