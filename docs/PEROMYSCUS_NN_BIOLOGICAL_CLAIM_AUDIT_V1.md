# Biological-claim audit after Peromyscus geometry discovery (2026-10-08)

**Status:** interpretive restriction based on already exposed RELEASE-2026 effects. Do not use to revise the frozen original 6/8 test or convert the new local geometry comparison into confirmation.

## What was observed

- Frozen development response: positive genus-balanced Δ slope, but only 5/8 genus-specific positive directions, hence **original generality STOP**.
- Post-result centroid geometry across 1,326 sessions (167 series, 40 sites) reproduced Δ exactly at +9.37176547246767 m² per MNKA, with all cohort counts and centroid-derived B_observed agreeing.
- The separate nearest-neighbor analysis generated a post-result candidate only for *Peromyscus* (956 sessions, 33 sites). Its raw nearest-neighbor squared distance decreases with genus MNKA, while its residual *slope* versus both the x/y-shuffle and other-event reference is positive. Other supported genera do not show jointly positive residual slopes.

## Important logical correction: residual slope != spatial regularity

Let `E_j = NN2_observed,j - E_null(NN2_j)`. A positive regression coefficient `beta(E~MNKA)` means **NN spacing becomes greater relative to the chosen baseline as MNKA rises**. It does NOT imply `E_j > 0` or that the animal locations are 'overdispersed', 'regular', 'territorial', or 'more separated' at high density.

For example `E=-100+2N` has positive slope even when it is negative for the entire available N range. This hypothetical example is algebra, not NEON data.

The strongest supported language at this stage is **a less negative (or more positive) geometric nearest-neighbor contrast with increasing capture-derived abundance**. To call a configuration statistically overdispersed even relative to the specified null, the data would need evidence that the *level* E>0, not only that its slope is positive, with valid uncertainty calibration.

## Observation limitations

- NN2 is computed on repeated-capture-session *trap-coordinate centroids* from 2–3 nights; no animal was continuously tracked.
- Individual selection into this matched cohort changes with event MNKA.
- Traps impose a fixed lattice; number of repeat-supported individuals m also covaries with MNKA.
- X/Y shuffling preserves the observed coordinate marginals and B, but destroys anisotropy/coordinate dependence and does not model trappability, habitat, or social interactions.
- The within-series other-event reference preserves typical captured centroid opportunities but not necessarily the time-varying m, density, composition or microhabitat.
- A post-result leave-one-site-out sign check, even across all 33 sites, does not constitute independent replication: the same RELEASE-2026 discovery data chose the candidate genus and generated its effects.
- In general SCR, spatially structured detectability and dependence matter (Stevenson et al. *Spatial correlation structures for detections of individuals in spatial capture–recapture models*; see also Gerber & Parmenter 2015, DOI 10.1890/14-0960.1). Estimated centre distributions are not equivalent to direct animal positions (see *That's not the Mona Lisa!*, Biometrics 2024).

## Review decisions

1. Keep the new exploratory *Peromyscus* result separate from the manuscript-ready live-trap aliasing methods paper.
2. Keep the original NEON 6/8 generality failure public and unchanged.
3. Future results must address (i) taxon and site heterogeneity, (ii) **actual residual levels by abundance stratum**, not merely slopes, (iii) covariance/uncertainty at the site level, and (iv) a true independent holdout or separate validated observation process.
4. Do not state 'territorial spacing', 'defensive regularity', 'anti-crowding adaptation', 'social spacing', or 'repulsion' as findings.
5. The new future Peromyscus geometry contract is a **prospective associational test**, not an identifiable mechanistic test.

## Broader biology question still open

Does crowding alter the *spatial arrangement* of sampled individual centres differently from its effect on each individual's short-term spatial variance, after detection and lattice geometry are accounted for? If replicated, this is a biological contrast worth testing for resource patchiness, conspecific interactions and demography. None of these specific mechanisms is identified by the current data.
