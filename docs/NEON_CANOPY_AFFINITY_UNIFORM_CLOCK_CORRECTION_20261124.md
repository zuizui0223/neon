# 24 November 2026 JST — canopy affinity: completed v1, mandatory null correction

## Historical observed result (not a calibrated ecological conclusion)

The original source failure was resolved on the existing frozen cohort. [Run 45245953902](https://github.com/zuizui0223/neon/actions/runs/45245953902) / job 137942792840 / artifact 14852474825 reports all 3,000 station histories, all 51 checksum-verified AOP rasters, 24,600 valid source pixels, and 36 pairs / 12 sites / 21 grids. Of 36 pairs: 15 flat-canopy, 1 zero null variance, 20 informative in 8 sites. Five of eight site means positive; mean Z=+0.49546992465599565; descriptive site signflip p=0.1875. Original decision EXPLORATORY_CANOPY_AFFINITY_NOT_SUPPORTED. The complete original JSON printed to the workflow log and the GitHub-reported artifact digest are preserved in [historical log receipt](../results/neon_canopy_affinity_v1_historical_20261124.json); ZIP bytes have not been independently verified in this review.

## Why the inferential calibration requires correction

The original v1 runner advances by ACCEPTED swaps, resampling until an eligible row pair moves. This is the same jump-chain defect already corrected for the 14-site genus×station result. The probability of exiting a fixed-margin state varies with the state (e.g. 2 vs 3 eligible row pairs in the finite 3×4 test); discarding holds changes the stationary distribution away from uniform in general. The original v1 number and non-support label remain historical, but neither is a calibrated uniform-null estimate.

## Clock-only calibration, no outcome-dependent rescue

Reuse the previously audited symmetric lazy proposal kernel from `neon_proposal_clock_v2.py`: two chains, 10,000 burn-in **proposals**, 2,000 retained draws per chain, 100 **proposals** between draws, per-chain batch-means ESS ≥200 and split Rhat <1.05, exactly the earlier corrected 14-site sampler settings. Every rejection and lazy hold counts. Same 36 original source-qualified pairs, same score, same raw observations, fixed genus and station margins, source qualification and ≥15 informative pairs / ≥8 independent sites gate unchanged. Original physical-site aggregation and one-sided signflip retained as descriptive conditional inference (not a universal joint null). No alternative canopy cutoff, taxa, months, plots, product, source cohort or statistical direction. No inference for failed mixing, and no claim of absence from nonsupport. The v1 sampler and frozen design remain archived; v2 has a distinct artifact and schema. A positive v2 result would be post-result calibration on the same data, never an independent confirmation or permission to submit.

Separate software QA failure: global frozen-paper-checks could not import rasterio after adding the source audit tests. Pin rasterio==1.4.3, the identical version used in the dedicated canopy workflow; no scientific tests are skipped or weakened.

**Current biological mainline unchanged**: same-station capture-space recurrence; canopy structure, resource biomass, competition, learning and detectability remain unresolved. One paper DRAFT / SUBMISSION HOLD.
