# Spatial patch recurrence independent of exact station matching: NEON 10 m hypothesis
**Commit date 25 October 2026 — NEW historical same-release exploratory ecological endpoint, drafted BEFORE opening any nearest-neighbor outcome, meta-null, or site-mean results.**

## Biological problem and novelty

Current observational result: in the NEON small-mammal 10×10 grids, season A and B have a positive same-genus, same-station recurrence pattern after excluding individuals detected in both seasons. This could be stable taxon-linked habitat sorting OR taxon-specific detection at a fixed trap. A new discriminating spatial question is:

> **Conditional on the EXACT number of same-genus same-trap matches, is the capture distribution of different sampled animals of the same genus also unusually similar across neighboring stations 10 m apart?**

This is **local patch-scale spatial reassembly beyond exact trap identity**. The NEON small-mammal user guide documents physically arranged 10×10 standard grids with 10 m trap spacing; the predecessor V6's extremely broad neighbor threshold collapsed the grid. Here the primary neighborhood is *only* immediate horizontal/vertical (rook) neighbors on that nominal 10 m grid (not diagonal sqrt(2)×10 m, not radius 20/30/150 m). This does not require uncertain absolute historical geographical positions; it assumes the official trap-coordinate grid adjacency remained valid across seasons. Relocated traps, imprecise named source historical positions and genre-dependent detection remain limitations.

Official protocol: https://www.neonscience.org/data-collection/small-mammals and source guide https://data.neonscience.org/api/v0/documents/NEON_smammal_userGuide_vE1?inline=true.

## Source and cohort lock

The original **RELEASE-2026 DP1.10072.001** checksum-pinned 2015-04..2026-09, **158 exactly-two qualifying genera** adjacent-season pairs in 30 physical sites / 15 ecological domains, selected under all originally approved source rules. Two season-exclusive observed animal tag sets, 3-night bouts, >=90 original stations/night and earliest season bouts. No source-pair or site selected by old Z sign, climate, geography, density response or neighborhood outcome. The original strict ≥3-genus 58-pair paper and old density W/B generality FAIL remain immutable. Replaying the 158 source pairs must reproduce the published original source and all 30 anonymized corrected *same-station* site mean Z values.

First-stage effort support: only original recorded stations present at all six nights (from source-only `results/neon_macro_six_night_recorded_station_support_20261025.json`), ensuring ≥90 common stations and unchanged two-genus within-season source margins; all 158 source pairs passed prior source-only inspection. For comparability, the **primary patch test uses these six-night common recorded positions**, not shifted or interpolated coordinates; season-A and -B genotype rows restricted identically to these positions.

## Primary ecological statistic: immediate 10 m rook-neighbor recurrence

For each genus `g`, season-A occupied stations `A_g` and season-B `B_g`, define `N_g(t)=1` if there is a **different** station `s∈A_g` with coordinate row or column displacement exactly one and other coordinate displacement zero (nominal 10 m). The primary raw score is:

`S = sum_{g∈{g1,g2}} sum_{t∈B_g} N_g(t)`.

No credit for `s=t` in the neighborhood score; if a B station equals an A station, it can only score via a **second distinct A station** in its 10 m rook neighborhood. Both genus row totals, each station's genus richness in season B, the original named station layout and **the observed exact same-genus same-trap overlap** are held invariant under its null.

### Exact fixed margins AND exact observed self-overlap conditioned null

Within season B, traps with 0 or 2 genus labels are forced. At every singleton-genus trap station `t`, let binary `X_t=1` indicate B-genus1 and `X_t=0` indicate B-genus2. Fix the number `a=ΣX_t` to preserve genus prevalence. Let `w_t = 1(t∈A_g1)-1(t∈A_g2)∈{-1,0,+1}`. The already-known original exact-station overlap has the form `O=O_fixed + Σ_t w_t X_t`, and is conditioned on its ACTUAL observed count `O_obs`.

All assignments satisfying `ΣX=a` and `Σ wX=O_obs−O_fixed` are EQUALLY probable under the conditional uniform fixed-margin null. Group singleton stations by `w=-1,0,+1`. For any triple of genus1 selection counts `k- , k0 , k+` satisfying these constraints, assign exact integer combinatorial weight `C(n-,k-) C(n0,k0) C(n+,k+)`. Choose that triple with exact integer probability, then sample uniformly without replacement `k` stations within each stratum. This **directly samples** the exact conditional uniform fixed-margin target without any accepted-only MCMC or Metropolis approximation.

For each singleton station, define `v_t=N_g1(t)-N_g2(t)∈{-1,0,+1}`. The score `S=S_fixed+Σ v_t X_t`. The exact conditional **mean and variance** of S under all assignments at fixed margins and O can be derived analytically by weighted (multivariate) hypergeometric sample moments over the integer-weighted selection triples; no observed nearest-neighbor S is opened to decide whether conditional variance is nonzero. The *observed exact-station overlap O* is already a historical opened outcome and is necessarily used to condition on it; no claim that the new null is completely independent of prior outcomes.

### Gate before the NEW neighbor statistic is opened

- Before any observed S: at least **80 of the 158 original pairs** must have positive exact-conditional S variance, at least **18 independent physical sites**. These are NEW post-result source/conditional-null feasibility thresholds, not retroactive primary preregistration. If insufficient, STOP and archive the information limitation without inspecting S.
- In the source-defined complete-geometry cohort, report **all 158** original pair denominators and zero-variance units; no optional selection based on the positive/negative effect.
- If GO, standardize each informative pair `Z_neighbor=(S_obs−E_0 S)/SD_0 S`. Average by original physical site, then site-equal. Report positive site means, all negative means, grand mean, and site-count; no group/year/biome fishing.
- Draw exactly **2,000 DIRECT IID conditional assignment samples per informative unit**, fixed source sort and seed **2026102531+unit_index**; every null sample must preserve B row totals, trap column richness and exact observed O. Use direct sampling (NOT a Markov chain); no Rhat, artificial accepted-swap time or 2-row uniform unrestricted null substitution.
- Draw **20,000** grand-site null replicates using independently sampled conditional null overlap values across units; repeat with all unit null ranks perfectly comonotone inside a physical site (a stronger positive dependence *stress*, not a proven worst-case bound or actual site joint ecological process), fixed meta seeds **2026102532/33**. Both are historical post-result conditional scenarios, not independent new biological datasets.
- Ecological positive evidence requires site-equal observed `Z_neighbor>0` **AND both** predeclared conditional p-values <0.05. Otherwise report mixed/negative/neutral result without rescue by another distance band.
- Source site-reuse sensitivity: omit ENTIRE physical sites with any site×plot×season key appearing in >1 of the original 158 exact-two pairs, selected before reading new S. Recalibrate only if ≥8 remaining physical sites and ≥25 informative seasonal pairs; otherwise STOP the sensitivity without softening the gate.
- Original corrected 30-site exact-station Z and fixed margins stay unchanged; do NOT pool original 10m-neighbor Z or p with the historical same-station Z or ≥3-genus Z. A positive patch score conditioned on exact-station O is a distinct estimand.

## Interpreting the possible result

**Positive patch effect beyond same-trap overlap:** evidence that the *spatial arrangement* of genus labels at immediately adjacent named stations can recur at a nominal 10 m scale even after exact-trap genus persistence is mathematically held constant. This would weaken an exclusively fixed-trap identity explanation. However correlated catchability at neighboring traps, stable habitat/refuge preferences, field taxonomic assignments, source-season dependence and non-independent old site cohorts are NOT eliminated. No causal "habitat sorting" proof, true occupancy or whole-animal population turnover.

**Zero/negative or insufficient variance:** supports a narrower claim restricted to exact-station taxonomic recurrence, no new patch-level generalization. Do not re-label as a failure of the already verified same-station ecological result.

**Macroecology setting:** retain all independently geolocated source sites and ecological domains, but do not fit a new climate, density, canopy, or genus effect by fishing the new patch Z. A site-level predictive macrocontext model is future work on a genuinely unobserved source cohort with calibrated detection and independent environmental measurements.

**ONE manuscript** `manuscript/NEON_SPATIAL_MACROECOLOGY_UNIFIED_V0_4.md`; no Paper A/B split or separate method paper. Historical original 5/8 W/B density generality FAIL and new thermal-QC 79<80 STOP must remain explicit.
