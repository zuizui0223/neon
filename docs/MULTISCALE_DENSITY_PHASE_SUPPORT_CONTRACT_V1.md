# Density-history / spatial-memory candidate — support-only contract v1

**Date:** 2026-10-08. **Status:** NEW EXPLORATORY QUESTION, NOT PART OF FROZEN PRIMARY DENSITY GENERALITY TEST.

## Ecology question and rationale

Can a small-mammal assemblage with the **same current abundance index** have a different W (within-individual trapping-location variance) and B (between-individual centre dispersion) depending on whether its abundance index rose or fell since the preceding event? This would mean contemporaneous density is insufficient to capture spatial organization. Biological possibilities include demography, dispersal, priority effects and delayed redistribution; the available records cannot identify these mechanisms directly.

A density × population-cycle phase association has precedent (Bogdziewicz et al., *Ecology and Evolution*, 2016, DOI: 10.1002/ece3.2513). Thus **hysteresis alone is not an unprecedented phenomenon**. The novel candidate, if replicated, concerns *allocation across within- and between-individual spatial scales*, not another decreasing-home-range-with-density plot.

## Existing immutable claims

- The frozen genus-balanced Δ slope is positive, but the original 6/8 generality guard failed (5/8).
- The five development-derived modes and their future RELEASE-2026-excluded confirmation gates remain unchanged.
- Do not reclassify this new phase analysis as a rescue of the original failed test.
- San Jacinto within-night capture-order results are separately on **ECOLOGICAL_MECHANISM_HOLD**, because the trap prior-occupant effect is established prior art.

## Exposure and support rules frozen before opening any phase × W/B effects

Input: RELEASE-2026 target capture event histories and genus-level event MNKA, with the already frozen complete three-night standard-grid, saturation <=0.30 and m>=5 rules. The current support audit is **blind to W and B**; any later phase × W/B fit using RELEASE-2026 is exploratory only, not confirmation.

- Keep development mode genera fixed: packing `Chaetodipus, Myodes, Peromyscus` and compression `Dipodomys, Sigmodon`.
- Chronologically order **same target taxon × site × plot** events by collection date.
- For event t, define the phase using `MNKA_t - MNKA_(t-1)`: increasing (>0), decreasing (<0), stable (=0).
- Only define a finite-lag phase for successive eligible response events separated by **at most 370 days**. Report <=120, 121–370 and >370 day gap support separately.
- Structural matched support requires two response events within the **same taxon × plot series**, one increasing and one decreasing, with current MNKA differing by **at most 2**.
- Pairs are overlapping support opportunities, not independent replicate samples. Report distinct series and sites.
- Required before proposing an exploratory mode-level phase fit: **both fixed modes separately** must have >=20 pairs, >=10 distinct paired taxon×plot series and >=3 distinct paired sites. These thresholds are support minima, not adjusted statistical significance.
- If either mode fails: **stop cross-mode phase analysis and report unestimable**, not a post-hoc one-mode success.
- If the support audit reveals duplicate dates or nonpositive time gaps, inspect chronology first; no phase effect until resolved.

## Irreducible limitations

Genus MNKA is **retrospective**, interpolating individual known-alive intervals using captures that happened *after* the event; apparent growth and decline can be partially reconstructed with future information. It is not a prospective abundance signal necessarily available to animals. Missing bouts, imperfect capture, site-specific seasonal changes and repeated sampling impose additional confounding. A phase association would not demonstrate biological memory, priority effects or social competition.

Even if support passes and phase associations are later fitted, preregister a future-data protocol separately. Do not conflate retrospective support with causal or independent evidence.

## Execution

```bash
python -m unittest discover -s tests -p 'test_multiscale_density_phase_support_v1.py' -v
NEON_API_TOKEN=... python -m analysis.audit_multiscale_density_phase_support_v1
```

Output is a **structural receipt only**, in `build/multiscale_density_phase_support_v1.json`. It does not evaluate a single W/B slope.
