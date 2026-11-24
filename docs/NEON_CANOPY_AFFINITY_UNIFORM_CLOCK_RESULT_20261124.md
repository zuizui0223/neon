# 24 November 2026 — corrected canopy analysis: closure

The original source infrastructure recovered and the same frozen 36 seasonal pairs at 12 physical sites / 21 grids were evaluated with a corrected symmetric lazy proposal-clock sampler. Run [45310729767](https://github.com/zuizui0223/neon/actions/runs/45310729767), job 138165508808, artifact 14882379049. All 51 checksum-verified raster tiles and 24,600 valid source pixels reproduced. The raster and location-history response SHA sets match v1; the manifest metadata response SHA set differs, so we do not claim every raw metadata byte is identical. The same 3,480 original MD5/size-verified capture source files were recovered from the 3,547-file manifest, 58 original pairs / 30 grids / 14 sites.

| Measure | Historical accepted-only v1 | Corrected proposal-clock v2 |
|---|---:|---:|
| Informative pairs | 20 | 20 |
| Physical sites | 8 | 8 |
| Positive site means | 5 | 5 |
| Flat canopy pairs | 15 | 15 |
| Zero null variance pairs | 1 | 1 |
| Equal-site mean Z | 0.4954699247 | 0.4805483892 |
| Descriptive one-sided site signflip p | 0.1875 | 0.20703125 |

**Decision: EXPLORATORY_CANOPY_AFFINITY_NOT_SUPPORTED.** No further same-release canopy subgroup, cutoff, alternative radius, source cohort or vegetation product search to rescue the outcome. This is not equivalence, a zero-effect proof or evidence against ground-level cover generally. The signflip is conditional on observed site statistics and not a demonstrated universal dependence null. The primary exact-station recurrence remains the existing conditional capture-space pattern, not a detection-corrected habitat mechanism. The corrected canopy test is the same-data calibration of an exploratory outcome, not independent confirmation.

Four additional synthetic sampler tests and ten historical tests passed. Full repository QA run [45310729625](https://github.com/zuizui0223/neon/actions/runs/45310729625) passed 879 tests (3 skipped). Archived aggregate result printed in original workflow logs with GitHub-reported artifact digest: [receipt](../results/neon_canopy_affinity_uniform_v2_20261124.json). Artifact ZIP itself has not been independently downloaded/verified here.

Next research goal is an independently collected, directly measured temporally preceding food-resource / ground-cover source, not more NEON CHM fitting. One unified paper DRAFT / SUBMISSION HOLD.
