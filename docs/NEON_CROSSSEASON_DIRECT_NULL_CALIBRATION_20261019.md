# Secondary direct Monte Carlo calibration of the NEON site-mean recurrence statistic
## Post-result verification plan, frozen before this calibration is executed

**Declared 2026-10-19 after the originally positive 14-site sign-flip result was already opened.**
This diagnostic is **NOT preregistered independent confirmation** and MUST NOT replace
or relabel the original frozen site sign-flip criterion. The original result was
14 sites, 58 seasonal units, 11 positive physical site means, mean site Z
+0.8007420166137748, and a one-sided sign-flip p=0.00115966796875.
The site's original null is a fixed-fixed season-B occupancy swap chain. The
new question is whether a **direct simulated distribution of the original
site-mean statistic** is compatible with that positive observation without
requiring signed site means to be exchangeable/symmetric.

### Frozen conditional calibration protocol

1. Reload exactly the same source `RELEASE-2026` and re-run the original
   58 unit fixed-fixed chains with **IDENTICAL** original unit seed
   `2026101901 + sorted_unit_index`, 2,000 draws, 1,000 accepted burn-in
   swaps and 40 accepted swaps between draws; do not alter the 14 sites, 30
   plots, genera, tag overlap, structural masks, sampling seasons, or null
   margins. The existing null implementation optionally accepts a private,
   in-memory vector of 2,000 raw simulated overlap counts; this option must
   not change any public original unit result.
2. **Fail closed** unless all 58 unit Z, genus occupied-cell counts, source
   eligibility counts, and reconstructed 14 sorted physical site means
   exactly reproduce the immutable original receipt to numerical tolerance
   1e-9. This is a check on code stability, *not* a new hypothesis fit.
3. Per source unit i convert each simulated overlap to
   `z_i* = (O_i* - original_null_mean_i)/original_null_sd_i`. Hold each
   source unit's season A fixed and draw only B with the same row/column
   margins. The null vector is kept in ephemeral process memory, never
   serialized, logged, committed or included in GitHub Actions artifacts.
4. Form the same original **equal-physical-site-weighted** statistic for a
   synthetic full dataset: within each site average one randomly selected
   `z_i*` per included season pair, then average the site means across the
   original 14 physical sites. Preserve the site→unit membership of all 58
   units; DO NOT count season pairs as 58 independent sites. For this
   explicit **conditional product-null** use 100,000 independent draws
   with replacement from each unit's empirical null-chain vector, seeded
   separately at `2026101902`.
5. Report the directly calibrated one-sided empirical probability
   `p_direct=(1 + #simulated T>=original T)/(100001)`,
   the binomial Monte Carlo SE, simulated T null mean/SD/quantiles, original
   site means and number of sites and units. Keep raw site codes, trap
   positions, genus labels and animal IDs entirely out of exported JSON.
6. A conditional simulation-tail p<0.05 is a **supporting
   calibration**, never another fully independent positive
   confirmation. If p>=0.05, or computation fails, report it and
   **downgrade** inferential strength without repairing the original
   primary test by post-result subsetting or changing the simulation.
7. **Major limitation to state regardless of outcome:** site units may
   share season-A and season-B observation periods, since contiguous
   season pairs in one plot can share an occasion. This product-null
   randomizes each unit's B independently while keeping all observed A
   matrices fixed. Hence it preserves the original per-unit margins and
   site weighting, but **does not fully reproduce joint covariance between
   overlapping seasonal pairs**. A small p does not by itself resolve
   shared-season dependence, unknown genus-specific detection, local
   habitat filtering, or source taxonomic/individual identity errors.
   Record the count of shared site×plot×season observation-period keys
   across multiple pair roles as a transparent dependency diagnostic.

### Scientific conclusion boundaries

- A small direct p supports a **genus-associated recurrent trap-location
  observation pattern** conditional on the specified product-null, not
  competition, territoriality, within-genus species identity, demographic
  birth/death/replacement, landscape mechanisms or full home ranges.
- There is no new W/B density fit, no rescue of the earlier 5/8
  failure against a required 6/8 rule, no rescue of provisional
  Peromyscus nonreplication, no retrospective F/C×W/B inference and no
  opening of external MOSA W/B effects.
- The existing `NEON_SPATIAL_TEMPLATE_REASSEMBLY_ECOLOGY_V0_1.md`
  remains a draft pending independent null and detection review.
