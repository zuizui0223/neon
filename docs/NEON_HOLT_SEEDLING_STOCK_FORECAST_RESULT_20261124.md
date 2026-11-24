# Holt prior-stock and past-trained stress — closure

24 November 2026. [Run 45380336938](https://github.com/zuizui0223/neon/actions/runs/45380336938), job 138397402446, artifact 14914725613. All 21 original target years and 116 original nominal plots recovered. Previous-census support passed in 21/21 years, 10 initial training years and 11 past-only prediction years. All three synthetic tests and full CI run 45380336831 succeeded.

| Quantity | Original descriptive association (v1) | Stock-adjusted ridge stress |
|---|---:|---:|
| Mouse × previous-label seed | +0.525681 | +0.481382 |
| Mouse slope at low seed | −0.654072 | −0.476009 |
| Mouse slope at high seed | +0.397291 | +0.486754 |

The original v1 OLS and new ridge coefficients are not directly identical estimands. Their signs persist, not a new confirmation or proof of sign reversal within supported resource range.

On the 11 common expanding-window prediction years, persistence RMSE 1.473207, stock/seed/weather/year/gap baseline 1.516982, mouse-augmented 1.575181. Augmented worsened vs baseline by 3.84%, vs persistence by 6.92%. First era (3 years) baseline 0.940389 -> augmented 0.894204; second era (8 years) baseline 1.683025 -> augmented 1.764027. Failed three of five prespecified gates (beats stock baseline, beats persistence, both eras improve); two directional gates passed. **POST_RESULT_STOCK_FORECAST_STRESS_NOT_SUPPORTED.** Close this annual-model lane without trying alternate lags, years, species, model penalties, or subgroups to rescue it. The earlier exploratory result stays in the ledger but does not demonstrate forecasting or a causal resource-dependent function. Neither model identifies actual recruitment, seed survival, dispersal, predation, or linkage to NEON capture-space recurrence. Same forest, same data, observational. Exact crop label unresolved.

[Aggregate original workflow-log receipt](../results/neon_holt_seedling_stock_forecast_v1_20261124.json). Artifact ZIP not independently downloaded/verified in this review. Main NEON submission remains HOLD.
