# Live-trap aliasing review package manifest v1

This package is intentionally narrower than the parent NEON repository.

## Manuscript
- MANUSCRIPT_MEE_LIVE_TRAP_ALIASING_V0_2.md
- SUPPLEMENTARY_METHODS_MEE_LIVE_TRAP_ALIASING_V0_1.md
- README_LIVE_TRAP_ALIASING.md
- docs/FIGURE_CAPTIONS_V1.md
- docs/SUBMISSION_STATEMENTS_V1.md
- docs/MEE_FIT_AND_LITERATURE_BOUNDARY_V2.md
- docs/MEE_PRESUBMISSION_ENQUIRY_DRAFT_V1.md
- docs/MEE_PRESUBMISSION_ENQUIRY_READY_V2.md
- docs/APPLICABILITY_MATRIX_V1.md
- docs/KEY_METHOD_STATEMENTS_V1.md

## Generic method
- analysis/temporal_aliasing_diagnostic_v1.py
- analysis/temporal_aliasing_bounds_v1.py
- analysis/simulate_temporal_aliasing_diagnostic_v1.py
- examples/repeated_locations_example.csv
- examples/repeated_locations_example_expected.json
- docs/TEMPORAL_ALIASING_DIAGNOSTIC_USAGE_V1.md
- docs/TEMPORAL_ALIASING_GEOMETRY_V1.md
- docs/SIMULATION_BENCHMARK_PLAN_V1.md

## Generic tests
- tests/test_temporal_aliasing_diagnostic.py
- tests/test_temporal_aliasing_example.py
- tests/test_temporal_aliasing_bounds.py
- tests/test_temporal_aliasing_simulation.py

## Prospectively held-out empirical validation
- analysis/san_jacinto_positional_aliasing_v1.py
- tests/test_san_jacinto_positional_aliasing.py
- results/san_jacinto_positional_aliasing_result_v1.json
- validation/san_jacinto_positional_aliasing_v1/effect_lock_v1.json
- validation/san_jacinto_positional_aliasing_v1/result_artifact_v1.json
- validation/san_jacinto_positional_aliasing_v1/programme_final_decision_v1.json

## Observation-process context
- analysis/live_trap_aliasing_denominator_audit_v1.py
- tests/test_live_trap_aliasing_denominator_audit.py
- validation/live_trap_aliasing_v1/denominator_audit_v1.json
- results/temporal_aliasing_simulation_benchmark_v1.json
- validation/live_trap_aliasing_v1/downstream_home_range_estimability_lock_v1.json
- validation/live_trap_aliasing_v1/downstream_home_range_estimability_v1.json
- validation/live_trap_aliasing_v1/downstream_home_range_stop_v1.json

## Figures
- figures/figure1_observation_process.png
- figures/figure1_observation_process.pdf
- figures/figure2_simulation_benchmark.png
- figures/figure2_simulation_benchmark.pdf
- figures/figure3_heldout_validation.png
- figures/figure3_heldout_validation.pdf
- figures/figure4_denominator_and_span.png
- figures/figure4_denominator_and_span.pdf
- analysis/plot_live_trap_aliasing_figures_v1.py

## Manuscript claim invariants
- tests/test_live_trap_aliasing_manuscript_v0_2.py

## Environment / license
- LICENSE
- requirements-aliasing.txt
- requirements-figures.txt

## Explicitly excluded
- stopped sex-packing branches and outputs;
- carrier/Oikos manuscript material;
- unrelated NEON mammal analyses;
- exploratory heteromyid discovery-effect tables;
- raw third-party data files (downloaded from the cited public source by checksum-controlled scripts where needed).
