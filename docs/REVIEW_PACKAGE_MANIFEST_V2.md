# Live-trap aliasing review package manifest v2

This package is intentionally narrower than the parent NEON repository. It contains the v0.4 manuscript lane in which the downstream SCR consequence benchmark replaces the earlier estimator-only simulation as the main simulation result.

## Manuscript
- MANUSCRIPT_MEE_LIVE_TRAP_ALIASING_V0_4.md
- SUPPLEMENTARY_METHODS_MEE_LIVE_TRAP_ALIASING_V0_3.md
- README_LIVE_TRAP_ALIASING.md
- docs/FIGURE_CAPTIONS_V3.md
- docs/SUBMISSION_STATEMENTS_V1.md
- docs/MEE_FIT_AND_LITERATURE_BOUNDARY_V2.md
- docs/MEE_PRESUBMISSION_ENQUIRY_HOLD_V4.md
- docs/MEE_SUBMISSION_READINESS_V4.md
- docs/APPLICABILITY_MATRIX_V1.md
- docs/KEY_METHOD_STATEMENTS_V1.md

## Generic diagnostic and supplementary estimator benchmark
- analysis/temporal_aliasing_diagnostic_v1.py
- analysis/temporal_aliasing_bounds_v1.py
- analysis/simulate_temporal_aliasing_diagnostic_v2.py
- docs/SIMULATION_BENCHMARK_CORRECTION_V2.md
- examples/repeated_locations_example.csv
- examples/repeated_locations_example_expected.json
- docs/TEMPORAL_ALIASING_DIAGNOSTIC_USAGE_V1.md
- docs/TEMPORAL_ALIASING_GEOMETRY_V1.md
- docs/SIMULATION_BENCHMARK_PLAN_V1.md
- results/temporal_aliasing_simulation_benchmark_v2.json

## Main downstream SCR consequence benchmark
- analysis/simulate_scr_sigma_consequence_v1.R
- docs/SCR_SIGMA_CONSEQUENCE_SIMULATION_DESIGN_V1.md
- docs/SCR_SIGMA_EMPIRICAL_SCALE_BENCHMARK_V1.md
- docs/SCR_SIGMA_MIXTURE_THEORY_V1.md
- results/scr_sigma_consequence_simulation_v1.json
- results/scr_sigma_consequence_replicates_v1.csv

## Prospectively held-out empirical validation
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
- tests/test_live_trap_aliasing_manuscript_v0_4.py

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
- any PEMA-only post-stop SCR result unless it is later explicitly added as exploratory evidence with its stopping history intact.
