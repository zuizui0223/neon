# Live-trap aliasing review package manifest v4

This package is intentionally narrower than the parent NEON repository. It contains the v0.6 manuscript lane, which separates three questions that earlier versions conflated: whether repeated observations reveal materially different positions within one nominal occasion, whether the within-occasion process is serially persistent or directionally asymmetric, and whether that structure materially changes a downstream estimand.

## Manuscript
- MANUSCRIPT_MEE_LIVE_TRAP_ALIASING_V0_6.md
- SUPPLEMENTARY_METHODS_MEE_LIVE_TRAP_ALIASING_V0_3.md
- README_LIVE_TRAP_ALIASING.md
- docs/FIGURE_CAPTIONS_V4.md
- docs/SUBMISSION_STATEMENTS_V1.md
- docs/MEE_FIT_AND_LITERATURE_BOUNDARY_V3.md
- docs/MEE_PRESUBMISSION_ENQUIRY_HOLD_V4.md
- docs/MEE_SUBMISSION_READINESS_V4.md
- docs/APPLICABILITY_MATRIX_V1.md
- docs/KEY_METHOD_STATEMENTS_V1.md
- docs/TEMPORAL_EXCHANGEABILITY_REPRESENTATION_STABILITY_V1.md

## Generic positional-aliasing diagnostic
- analysis/temporal_aliasing_diagnostic_v1.py
- analysis/temporal_aliasing_bounds_v1.py
- examples/repeated_locations_example.csv
- examples/repeated_locations_example_expected.json
- docs/TEMPORAL_ALIASING_DIAGNOSTIC_USAGE_V1.md
- docs/TEMPORAL_ALIASING_GEOMETRY_V1.md

## Supplementary estimator benchmark
- analysis/simulate_temporal_aliasing_diagnostic_v2.py
- docs/SIMULATION_BENCHMARK_PLAN_V1.md
- docs/SIMULATION_BENCHMARK_CORRECTION_V2.md
- results/temporal_aliasing_simulation_benchmark_v2.json

## SCR representation-stability evidence
- analysis/simulate_scr_sigma_consequence_v1.R
- docs/SCR_SIGMA_CONSEQUENCE_SIMULATION_DESIGN_V1.md
- docs/SCR_SIGMA_EMPIRICAL_SCALE_BENCHMARK_V1.md
- docs/SCR_SIGMA_MIXTURE_THEORY_V1.md
- results/scr_sigma_consequence_simulation_v1.json
- results/scr_sigma_consequence_replicates_v1.csv
- results/san_jacinto_pema_scr_sigma_post_stop_result_v1.json
- analysis/summarize_pema_sigma_ratio_uncertainty_v1.py
- results/pema_sigma_ratio_uncertainty_sensitivity_v1.json
- analysis/pema_stationary_displacement_null_v1.R
- results/pema_stationary_displacement_null_v1.json
- results/pema_stationary_displacement_null_replicates_v1.csv
- analysis/decompose_pema_stationary_transition_mixture_v1.py
- results/pema_stationary_transition_mixture_decomposition_v1.json
- validation/pema_stationary_displacement_null_v1/eligible_pema_sessions.csv
- analysis/simulate_scr_sigma_dynamic_state_zero_shift_v2_1.R
- docs/SCR_SIGMA_DYNAMIC_STATE_ZERO_SHIFT_DIAGNOSTIC_V2_1.md
- results/scr_sigma_dynamic_state_zero_shift_v2_1.json
- results/scr_sigma_dynamic_state_zero_shift_replicates_v2_1.csv

The PEMA SCR result is explicitly post-stop exploratory evidence. It does not replace the stopped two-species confirmatory SCR programme, and its -3.3% point contrast is not treated as demonstrated equivalence. The uncertainty-sensitivity receipt records how the approximate LAST/FIRST ratio interval changes with the unknown paired estimate correlation; it is not a formal paired confidence interval. The matched 19-session stationary-displacement diagnostic asks only whether the empirical first-to-last displacement magnitude exceeds a fixed-centre stationary SCR reference; it finds stationary-compatible RMS magnitude, so an ordered state shift is not required by displacement scale, but substantially stronger same-trap persistence remains than under independent checks. The algebraic transition-mixture receipt decomposes that same frozen result into a larger point mass at zero displacement and a longer distance scale conditional on changing traps; it is post-result descriptive evidence, not a causal movement model. The dynamic-state v2.1 files contain only the independently seeded zero-shift diagnostic used to validate the stationary sequential generator; non-zero-shift cells from the earlier failed-gate run remain excluded.

## Post-result temporal-direction audit
- analysis/audit_time_reversal_symmetry_v1.py
- results/time_reversal_symmetry_audit_v1.json

This audit is exploratory and non-rescuing. It tests grid-stratified first-to-last directional imbalance with grid × individual cluster sign flips; failure to reject is consistency evidence, not proof of time-reversal symmetry.

## Observation-process calibration stop
- analysis/calibrate_san_jacinto_observation_process_v3.R
- docs/SAN_JACINTO_OBSERVATION_CALIBRATION_V3.md
- validation/san_jacinto_scr_sigma_v1/observation_calibration_v3.json

The v3 calibration fitted no downstream SCR model. Zero of 12 independently validated candidates from a 204-cell observation-only search reproduced all four empirical targets, so the simple release-centred transient-state model was stopped rather than promoted as a San Jacinto mechanism.

## Prospectively held-out positional non-uniqueness validation
- analysis/san_jacinto_positional_aliasing_v1.py
- tests/test_san_jacinto_positional_aliasing.py
- results/san_jacinto_positional_aliasing_result_v1.json
- validation/san_jacinto_positional_aliasing_v1/effect_lock_v1.json
- validation/san_jacinto_positional_aliasing_v1/programme_final_decision_v1.json

## Observation-process context and stopped downstream gate
- analysis/live_trap_aliasing_denominator_audit_v1.py
- analysis/audit_live_trap_aliasing_individual_cluster_v1.py
- analysis/audit_live_trap_night_label_semantics_v1.py
- validation/live_trap_aliasing_v1/denominator_audit_v1.json
- validation/live_trap_aliasing_v1/individual_cluster_sensitivity_v1.json
- validation/live_trap_aliasing_v1/simulation_correction_receipt_v2.json
- validation/live_trap_aliasing_v1/downstream_home_range_estimability_lock_v1.json
- validation/live_trap_aliasing_v1/downstream_home_range_support_summary_v1.json
- validation/live_trap_aliasing_v1/night_label_semantics_audit_v1.json

## Figures
- figures/figure1_observation_process.png / .pdf
- figures/figure2_simulation_benchmark.png / .pdf
- figures/figure3_heldout_validation.png / .pdf
- figures/figure4_denominator_and_span.png / .pdf
- analysis/plot_live_trap_aliasing_figures_v2.py

## Manuscript and generic tests
- tests/test_temporal_aliasing_diagnostic.py
- tests/test_temporal_aliasing_example.py
- tests/test_temporal_aliasing_bounds.py
- tests/test_temporal_aliasing_simulation_v2.py
- tests/test_live_trap_aliasing_denominator_audit.py
- tests/test_live_trap_aliasing_individual_cluster_v1.py
- tests/test_live_trap_night_label_semantics_v1.py
- tests/test_live_trap_aliasing_manuscript_v0_6.py

## Environment / license
- LICENSE
- requirements-aliasing.txt
- requirements-figures.txt

## Explicitly excluded
- stopped sex-packing branches and outputs;
- carrier/Oikos manuscript material;
- unrelated NEON mammal analyses;
- exploratory heteromyid discovery-effect tables;
- raw third-party data files;
- detailed individual-level downstream-support tables containing third-party animal identifiers;
- repository-specific workflow/run/commit provenance that could compromise double-anonymous review;
- the provenance-rich PEMA workflow receipt;
- calibrated-SCR v2 outputs that did not reproduce the empirical observation-process targets closely enough to support an “empirically matched” claim;
- non-zero-shift outputs from the sequential dynamic-state benchmark: the original 24-replicate null gate failed narrowly, and although an independent 96-replicate null-only diagnostic later passed, the already-opened non-zero cells are not retroactively promoted.
