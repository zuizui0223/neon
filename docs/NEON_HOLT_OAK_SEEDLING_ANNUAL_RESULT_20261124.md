# Holt annual red-oak seedling association — original frozen exploratory result

24 November 2026. [Run 45378672304](https://github.com/zuizui0223/neon/actions/runs/45378672304), job 138391630299, artifact 14911254820. Original provider-pinned seedfall, seedling and capture source checks passed; 21 years (1988–2013), 118 fixed common S1 plots before exclusion of two whole plots with duplicate literal oak keys; 116 retained. All 21 years had the original covariates. All three synthetic tests and the full repository CI run 45378672150 completed successfully.

| Measure | Result |
|---|---:|
| Mouse × prior seed interaction | +0.525681 |
| Mouse slope at −1 SD seed | −0.654072 |
| Mouse slope at +1 SD seed | +0.397291 |
| Leave-one-year-out interaction range | +0.195043 to +0.768722 |
| Leave-one-year-out low-seed slope range | −1.039501 to −0.308555 |
| Baseline blocked RMSE | 1.620571 |
| Augmented blocked RMSE | 1.401336 |
| Improved time blocks | 2/3 |

The prespecified **descriptive** decision is DESCRIPTIVE_DELAYED_CONSUMER_PATTERN_SUPPORTED. The outcome is July recorded red-oak SPEC 5 / FIASP 833 standing HT1 count per 100 fixed nominal plots, not individual germination or seed fate. Predictor is previous August observed unique tagged mice, not calibrated density. Positive high-seed conditional slope is not evidence of beneficial seed dispersal. Seed variable uses previous author annual label; exact field crop cohort not independently resolved. One forest; no causal or geographic generality, no p value. The original folds include years after a target block in training; they are retrospective blocked prediction, not forecasting. Central 1996–2004 block worsened (MSE 0.4704 to 0.9663). Five alternative SPEC 5.1 records were not included, consistent with the frozen literal code. 

[Complete original stdout receipt](../results/neon_holt_oak_seedling_annual_v1_20261124.json) records GitHub's reported artifact digest; ZIP bytes have not been independently verified in this review. The old Holt spatial contrast STOP and NEON canopy non-support are unchanged. Published delayed mast/rodent mechanisms are prior art; this is a source-specific exploratory result, not independent mechanistic evidence for NEON spatial persistence.

## Next mandatory robustness question

Because HT1 is standing stock, prior observed smallest-seedling counts can predict the response even without a new seed-to-seedling transition. Evaluate one prespecified **post-result** past-trained prediction stress including prior recorded seedling stock and census gap. No alternative species effect models before that stress is interpreted. See the [fixed follow-up](NEON_HOLT_SEEDLING_STOCK_FORECAST_FROZEN_20261124.md). DRAFT / SUBMISSION HOLD.
