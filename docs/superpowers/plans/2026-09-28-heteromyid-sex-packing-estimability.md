# Public Heteromyid Sex-Packing Estimability Implementation Plan

**Goal:** Determine, without inspecting sex-effect directions, whether Portal and NEON contain enough paired male/female heteromyid sessions to support a replicated sex-specific spatial-packing study.

**Spec:** `docs/superpowers/specs/2026-09-28-public-mammal-sex-packing-v1.md`

## Constraints

- No sex-effect coefficient, mean Delta_sex_packing, confidence interval or p-value may be computed in this phase.
- Primary gate = >=3 males and >=3 females per session.
- Sensitivity gates = >=2/sex and >=5/sex.
- Taxonomic scope is frozen to Chaetodipus, Dipodomys, Perognathus and Microdipodops.
- Portal uses all positive QC-complete effort=49 censuses from the pinned Portal commit.
- NEON uses one-night diversity-grid sessions under the existing effort/taxonomy/geometry rules.
- One spatial location per resolved individual per session.
- Only known M/F records enter sex-specific counts.
- Output may contain counts, completeness, species/site/plot replication and source overlap only.

### Task 1 — Pure sex-session helpers

Create:
- `analysis/mammal_sex_packing_estimability_v1.py`
- `tests/test_mammal_sex_packing_estimability.py`

Functions:
- `is_heteromyid(scientific_name: str) -> bool`
- `normalize_sex(value: object) -> str | None`
- `sex_count_record(rows: list[dict], id_field: str) -> dict`
- `summarize_sex_estimability(session_rows: list[dict], source: str) -> dict`

Tests first:
- genus inclusion/exclusion;
- M/F normalization and unknown exclusion;
- duplicate individual deterministic deduplication;
- >=2/3/5 paired flags;
- known-sex fraction;
- species replication counts.

### Task 2 — Portal sex-session inventory

Create:
- `analysis/build_portal_sex_packing_inventory_v1.py`
- `.github/workflows/public-mammal-sex-portal.yml`
- `tests/test_portal_sex_packing_inventory.py`

Reuse Portal source contract and stake/session filters, but do not restrict to 2009–2015 or treatment classes.

Output:
- `results/generated/portal_heteromyid_sex_sessions_v1.csv`
- `results/generated/portal_heteromyid_sex_inventory_v1.json`

Rows contain counts only:
source, species, plot, period, year, month, n_total, n_known_sex, n_male, n_female, known_sex_fraction, PIT fraction, paired_n2/n3/n5 flags.

No Packing_z_male/female is computed.

### Task 3 — NEON sex-session inventory

Create:
- `analysis/build_neon_sex_packing_inventory_v1.py`
- `analysis/run_neon_sex_packing_estimability_v1.py`
- `.github/workflows/public-mammal-sex-neon.yml`
- `tests/test_neon_sex_packing_inventory.py`

Reuse RELEASE-2026 query/downloader and primary diversity-grid rules.

Output:
- `results/generated/neon_heteromyid_sex_sessions_v1.csv`
- `results/generated/neon_heteromyid_sex_inventory_v1.json`

Rows contain counts only:
source, species, site, plot, event, year, n_total, n_known_sex, n_male, n_female, known_sex_fraction, active_trap_count, paired_n2/n3/n5 flags.

### Task 4 — Cross-source estimability gate

Create:
- `analysis/audit_heteromyid_sex_packing_estimability_v1.py`
- `.github/workflows/public-mammal-sex-estimability.yml`
- `tests/test_heteromyid_sex_packing_gate.py`
- persisted `results/heteromyid_sex_packing_estimability_v1.json`
- persisted `validation/public_mammal_sex_packing_v1/estimability_gate_v1.json`
- memo `docs/HETEROMYID_SEX_PACKING_ESTIMABILITY_V1.md`

Gate:
- Portal family passes if >=3 species each have >=10 paired_n3 sessions across >=2 plots.
- NEON family passes if >=3 species each have >=10 paired_n3 sessions across >=2 sites.
- Cross-source same-species replication passes for each species with >=10 paired_n3 sessions in both sources.
- effect_modeling_authorized only if at least one family gate passes; cross-source headline authorized only if both family gates plus >=1 shared species pass.

No effect response is computed until this gate is frozen.
