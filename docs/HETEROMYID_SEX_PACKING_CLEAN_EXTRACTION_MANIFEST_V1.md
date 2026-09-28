# Clean extraction manifest — heteromyid sex-packing programme

Date: 2026-09-29

Purpose: define the minimal material to extract into an independent manuscript repository if and only if the frozen manuscript gate authorizes a paper. This manifest does not authorize a manuscript.

## Keep: design and validation

- docs/superpowers/specs/2026-09-28-public-mammal-sex-packing-v1.md
- docs/superpowers/specs/2026-09-29-public-mammal-sex-packing-null-amendment.md
- docs/superpowers/specs/2026-09-29-heteromyid-sex-packing-phase3-analysis-lock.md
- docs/superpowers/specs/2026-09-29-heteromyid-sex-recapture-validation-lock.md
- docs/superpowers/specs/2026-09-29-heteromyid-recapture-interpretation-gate.md
- docs/HETEROMYID_SEX_PACKING_LITERATURE_BOUNDARY_V1.md
- validation/public_mammal_sex_packing_v1/

## Keep: packing metric and sex-packing analysis

- analysis/mammal_spatial_packing_exact_v2.py
- analysis/audit_sex_packing_mechanical_null_v2.py
- analysis/mammal_sex_packing_estimability_v1.py
- analysis/mammal_sex_trap_support_v2.py
- analysis/build_portal_sex_packing_inventory_v1.py
- analysis/build_neon_sex_packing_inventory_v1.py
- analysis/run_neon_sex_packing_estimability_v1.py
- analysis/build_portal_sex_trap_support_v2.py
- analysis/build_neon_sex_trap_support_v2.py
- analysis/run_neon_sex_trap_support_v2.py
- analysis/freeze_sex_trap_support_gate_v2.py
- analysis/mammal_sex_effects_phase3_v1.py
- analysis/build_portal_sex_effects_phase3_v1.py
- analysis/build_neon_sex_effects_phase3_v1.py
- analysis/run_neon_sex_effects_phase3_v1.py
- analysis/analyze_heteromyid_sex_packing_phase3_v1.py

## Keep: recapture validation if authorized/estimable

- analysis/neon_sex_recapture_estimability_v1.py
- analysis/neon_sex_recapture_effects_v1.py

## Keep: source/provenance helpers actually imported by the above

- analysis/build_neon_space_use_sessions_v1.py
- analysis/build_portal_space_use_sessions_v1.py
- analysis/run_neon_space_use_development_v1.py
- analysis/capture_carrier_prevalence_fresh_roster_v1.py

Before extraction, imported helper functions should be copied into a small dedicated utility module where practical so that the paper repository does not inherit unrelated carrier-analysis code.

## Keep: results

- results/heteromyid_sex_packing_mechanical_null_v2.json
- results/heteromyid_sex_packing_phase3_summary_v1.json
- results/heteromyid_sex_recapture_effect_v1.json only if produced
- workflow artifact provenance receipts

Raw/public source data should remain downloaded reproducibly from pinned Portal/NEON sources and should not be committed merely to make the new repository self-contained.

## Keep: tests

- tests/test_mammal_spatial_packing_exact_v2.py
- tests/test_sex_packing_mechanical_null_v2.py
- tests/test_mammal_sex_trap_support_v2.py
- tests/test_sex_trap_support_gate_v2.py
- tests/test_mammal_sex_effects_phase3.py
- tests/test_heteromyid_sex_packing_phase3.py
- tests/test_neon_sex_recapture_estimability.py
- tests/test_neon_sex_recapture_effects.py

## Do not carry into the independent paper repository

- stopped `public_mammal_space_use_v1` Phase-1/2 result code and manuscript remnants;
- Oikos carrier/cohesion manuscript material;
- unrelated NEON carrier analyses;
- old Monte-Carlo sex-null implementation except the compact failure receipt needed for provenance;
- workflow development duplicates that do not reproduce a frozen result.

## Extraction boundary

Do not create the manuscript repository merely because Phase-3 ran. Create it only if the frozen recapture interpretation gate authorizes a manuscript, or if a later explicitly pre-specified publication decision says the robust Portal null itself is being written as a methods/result note.
