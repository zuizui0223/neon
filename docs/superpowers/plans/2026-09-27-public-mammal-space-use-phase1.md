# Public Mammal Space-Use Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build reproducible Portal and NEON public-data session tables with a shared abundance-conditioned spatial-packing response, then produce an estimability report that determines whether the ecological models in the design are supportable.

**Architecture:** Keep data acquisition source-specific and keep the spatial statistic source-agnostic. Portal and NEON builders each translate their public capture data into the same session-level schema; a pure `mammal_spatial_packing_v1.py` module owns geometry, deterministic nulls and `Packing_z`. No ecological coefficient is fitted in Phase 1: the terminal deliverable is an auditable estimability report that freezes which species, treatments, habitats and sample-size thresholds can support Phase 2.

**Tech Stack:** Python 3.12; Python standard library; NumPy 2.1.1; GitHub Actions; public PortalData files pinned to commit `72d7ff8568052763bf6899dc462e285684cf20f6`; NSF NEON DP1.10072.001 RELEASE-2026 public API with repository secret `NEON_API_TOKEN`.

**Spec:** `docs/superpowers/specs/2026-09-27-public-mammal-space-use-design.md`

## Global Constraints

- Use only already public mammal data; do not wait for future data and do not use “fresh response” language.
- RELEASE-2026 is retrospective development data, not confirmatory evidence.
- Portal primary causal window is August 2009 through March 2015.
- Portal primary plots are current `control` and `exclosure`; exclude `removal`, negative periods, `sampled != 1`, `effort != 49`, nonrecommended QC and invalid stakes.
- NEON primary sessions are one-night diversity-grid bouts; pathogen grids are secondary only.
- Primary session eligibility is N >= 5 unique individuals; N >= 3 and N >= 8 are prespecified sensitivity thresholds.
- Common spatial response is `Packing_z = (MPD_obs - mean(MPD_null)) / sd(MPD_null)`, conditional on exact available trap geometry and N.
- Portal primary geometry is the declared 7 × 7, 6.25 m stake grid; UTM stake coordinates are audit/sensitivity geometry, not the primary geometry.
- NEON primary geometry uses actual geolocated active trap locations for the session.
- Each individual contributes at most one capture location per session.
- Taxonomic uncertainty must be resolved before ecological models; *Peromyscus maniculatus–P. leucopus* is a mandatory NEON sensitivity complex.
- Phase 1 must not choose model terms or hypotheses based on observed ecological effect sizes.

## Review Focus

- Portal treatment changes through time: every session must join treatment by exact year/month/plot and never use a static plot label.
- Portal identity quality: missing/ambiguous `id`, non-PIT histories and multiple records for one individual must have deterministic inclusion/deduplication behavior.
- NEON effort/completeness: primary sessions must use the actual active trap set and must reject multi-night/pathogen or incomplete primary sessions rather than assuming 100 traps.
- NEON taxonomy: uncertain `identificationQualifier`, identification-history corrections and cryptic complexes must be surfaced before species-level session construction.
- Null degeneracy: sessions whose conditioned MPD null has zero variance must be marked non-estimable, never assigned an artificial `Packing_z = 0`.

---

### Task 1: Freeze Public Source Manifests and Dataset Contracts

**Files:**
- Create: `validation/public_mammal_space_use_v1/source_manifest_v1.json`
- Create: `analysis/public_mammal_source_contracts_v1.py`
- Test: `tests/test_public_mammal_source_contracts.py`

**Interfaces:**
- Consumes: the design spec; Portal commit `72d7ff8568052763bf6899dc462e285684cf20f6`; NEON product/release identifiers.
- Produces: `load_source_manifest(path: Path) -> dict`; `validate_portal_contract(manifest: dict) -> None`; `validate_neon_contract(manifest: dict) -> None`.

- [ ] **Step 1: Write the failing source-contract tests**

Test exact Portal commit SHA, required Portal paths, NEON product code `DP1.10072.001`, release `RELEASE-2026`, required table names, and the rule that RELEASE-2026 is development-only.

- [ ] **Step 2: Run the tests and confirm RED**

Run: `python -m unittest tests.test_public_mammal_source_contracts -v`

Expected: FAIL because the contract module and manifest do not yet exist.

- [ ] **Step 3: Implement the source manifest and validation module**

Portal required files:
- `Rodents/Portal_rodent.csv`
- `Rodents/Portal_rodent_trapping.csv`
- `Rodents/Portal_rodent_species.csv`
- `SiteandMethods/Portal_plots.csv`
- `SiteandMethods/Portal_UTMCoords.csv`

NEON required logical tables:
- `mam_perplotnight`
- `mam_pertrapnight`
- `mam_identificationHistory`

Record source URLs/identifiers but never commit a token.

- [ ] **Step 4: Run source-contract tests and confirm GREEN**

Run: `python -m unittest tests.test_public_mammal_source_contracts -v`

Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `Freeze public mammal source contracts`

---

### Task 2: Implement the Shared Spatial-Packing Statistic

**Files:**
- Create: `analysis/mammal_spatial_packing_v1.py`
- Test: `tests/test_mammal_spatial_packing.py`

**Interfaces:**
- Consumes: unique-individual capture coordinates, the available trap-coordinate array for one session, deterministic seed and replicate count.
- Produces:
  - `mean_pairwise_distance(points_xy: np.ndarray) -> float`
  - `packing_null(active_traps_xy: np.ndarray, n_individuals: int, *, replicates: int, seed: int) -> dict`
  - `packing_score(observed_xy: np.ndarray, active_traps_xy: np.ndarray, *, replicates: int, seed: int) -> dict`
  - result keys: `n_individuals`, `mpd_observed`, `mpd_null_mean`, `mpd_null_sd`, `packing_z`, `estimable`, `non_estimable_reason`.

- [ ] **Step 1: Write failing geometry and null tests**

Pin:
- two-point MPD;
- three-point MPD;
- deterministic null under a fixed seed;
- exact enumeration when `C(M, N) <= 999`;
- Monte Carlo with 999 replicates otherwise;
- error when N exceeds active traps;
- non-estimable when N < 2 at the function level;
- non-estimable when null SD = 0.

- [ ] **Step 2: Run the tests and confirm RED**

Run: `python -m unittest tests.test_mammal_spatial_packing -v`

- [ ] **Step 3: Implement the minimal pure statistic module**

Use Euclidean coordinates in metres. Do not add species, source or habitat logic to this module.

- [ ] **Step 4: Run tests and confirm GREEN**

Run: `python -m unittest tests.test_mammal_spatial_packing -v`

- [ ] **Step 5: Commit**

Commit message: `Add abundance-conditioned mammal spatial packing statistic`

---

### Task 3: Build Portal Session Table

**Files:**
- Create: `analysis/build_portal_space_use_sessions_v1.py`
- Create: `.github/workflows/public-mammal-portal-development.yml`
- Test: `tests/test_portal_space_use_sessions.py`
- Runtime output: `results/generated/portal_space_use_sessions_v1.csv`
- Runtime output: `results/generated/portal_space_use_inventory_v1.json`

**Interfaces:**
- Consumes: Task 1 manifest; Task 2 `packing_score`; Portal CSVs pinned to the frozen commit.
- Produces one row per `species × plot × positive period` with:
  - `source`, `site`, `plot_id`, `period`, `year`, `month`, `species`
  - `treatment`, `n_unique_individuals`, `effort`, `qcflag`
  - `mpd_observed_m`, `mpd_null_mean_m`, `mpd_null_sd_m`, `packing_z`
  - `primary_n5_eligible`, `sensitivity_n3_eligible`, `sensitivity_n8_eligible`
  - identity-quality counts including PIT-reliable fraction.

- [ ] **Step 1: Write failing synthetic Portal tests**

Cover:
- negative period exclusion;
- `sampled = 0` exclusion;
- effort < 49 exclusion from the primary table;
- exact year/month/plot treatment join;
- `control` and `exclosure` recognition;
- exclusion of all-rodent removal;
- deterministic one-row-per-individual deduplication;
- ideal 7 × 7 geometry from stake labels 11–77 at 6.25 m;
- invalid/off-plot stakes rejected;
- PIT-quality summary retained.

- [ ] **Step 2: Run tests and confirm RED**

Run: `python -m unittest tests.test_portal_space_use_sessions -v`

- [ ] **Step 3: Implement Portal parsing and session construction**

Primary geometry uses row/column encoded by the 49 valid stake IDs; `Portal_UTMCoords.csv` is read only for a coordinate-consistency audit.

- [ ] **Step 4: Run tests and confirm GREEN**

- [ ] **Step 5: Add the Portal development workflow**

Workflow downloads only pinned public Portal files, builds session/inventory artifacts, and never fits an ecological model.

- [ ] **Step 6: Run the workflow on real public Portal data**

Expected output includes:
- period/year range;
- capture rows retained/excluded by rule;
- counts of eligible sessions at N >= 3/5/8;
- species × treatment replication;
- identity-quality summary.

- [ ] **Step 7: Commit**

Commit message: `Build Portal public mammal spatial-packing sessions`

---

### Task 4: Build NEON Diversity-Grid Session Table

**Files:**
- Create: `analysis/build_neon_space_use_sessions_v1.py`
- Create: `.github/workflows/public-mammal-neon-development.yml`
- Test: `tests/test_neon_space_use_sessions.py`
- Runtime output: `results/generated/neon_diversity_space_use_sessions_v1.csv`
- Runtime output: `results/generated/neon_space_use_inventory_v1.json`
- Runtime output: `results/generated/neon_taxonomy_uncertainty_v1.csv`

**Interfaces:**
- Consumes: Task 1 manifest; Task 2 `packing_score`; NEON RELEASE-2026 `mam_perplotnight`, `mam_pertrapnight`, identification history and location metadata.
- Produces one row per `species × site × diversity plotID × eventID` with:
  - source/session IDs and date/year;
  - species/taxonID;
  - `nlcdClass`;
  - `n_unique_individuals`;
  - active-trap count;
  - `gridCompletion`;
  - `packing_z` and MPD/null components;
  - taxonomy-certainty status;
  - N >= 3/5/8 eligibility flags.

- [ ] **Step 1: Write failing synthetic NEON tests**

Cover:
- diversity versus pathogen filtering;
- one-night event requirement;
- `nightuid` join;
- actual active-trap set construction;
- gridCompletion failure;
- missing tagID exclusion;
- one location per tagID;
- uncertain `identificationQualifier` removed from the primary species-level table;
- identification-history correction applied before session grouping;
- *P. maniculatus–P. leucopus* records flagged for mandatory sensitivity;
- sessions with null SD = 0 retained as non-estimable rather than assigned zero.

- [ ] **Step 2: Run tests and confirm RED**

Run: `python -m unittest tests.test_neon_space_use_sessions -v`

- [ ] **Step 3: Implement NEON table normalization and taxonomic audit**

Separate pure row-normalization helpers from network/download logic so the tests never need the live API.

- [ ] **Step 4: Run tests and confirm GREEN**

- [ ] **Step 5: Add the NEON development workflow**

Use `NEON_API_TOKEN` only from GitHub Actions secret. Query RELEASE-2026 once per workflow, verify file sizes/hashes when exposed by NEON, and upload derived session/inventory artifacts rather than raw response files.

- [ ] **Step 6: Run the workflow on public RELEASE-2026**

Expected inventory reports:
- sites/plots/events available;
- diversity versus pathogen counts;
- active-trap distributions;
- identification-uncertainty counts;
- eligible sessions at N >= 3/5/8;
- species × habitat replication.

- [ ] **Step 7: Commit**

Commit message: `Build NEON public mammal spatial-packing sessions`

---

### Task 5: Harmonize Habitat and Treatment Context Without Looking at Effect Sizes

**Files:**
- Create: `data/external/neon_nlcd_group_lookup_v1.csv`
- Create: `analysis/public_mammal_context_v1.py`
- Test: `tests/test_public_mammal_context.py`

**Interfaces:**
- Consumes: raw NEON NLCD codes/classes and Portal treatment labels.
- Produces:
  - `map_neon_nlcd(value: str) -> str` with exactly `forest`, `shrub_scrub`, `grassland_herbaceous`, `cropland_pasture`, `wetland`, `other_rare`;
  - `portal_competition_context(treatment: str) -> str | None` returning `control`, `kangaroo_rat_exclosure` or `None`.

- [ ] **Step 1: Write failing mapping tests**

Pin every observed NLCD class from the NEON inventory to one frozen broad group and every Portal treatment label in the 2009-08 to 2015-03 window to an allowed context or exclusion.

- [ ] **Step 2: Run tests and confirm RED**

- [ ] **Step 3: Implement frozen lookup tables**

No response coefficient or `Packing_z` value may be read while defining the lookup.

- [ ] **Step 4: Run tests and confirm GREEN**

- [ ] **Step 5: Commit**

Commit message: `Freeze public mammal ecological context mappings`

---

### Task 6: Produce the Cross-Dataset Estimability Audit

**Files:**
- Create: `analysis/audit_public_mammal_estimability_v1.py`
- Create: `tests/test_public_mammal_estimability.py`
- Runtime output: `results/public_mammal_estimability_v1.json`
- Runtime output: `data/derived/public_mammal_session_inventory_v1.csv`
- Create: `docs/PUBLIC_MAMMAL_ESTIMABILITY_V1.md`

**Interfaces:**
- Consumes: Portal session table from Task 3; NEON session table from Task 4; mappings from Task 5.
- Produces a decision report; it does **not** fit H1–H4.

- [ ] **Step 1: Write failing audit tests**

Require the report to contain:
- Portal sessions/species at N >= 3/5/8 by control/exclosure;
- number of Portal species with >=5 eligible sessions in both treatment contexts;
- NEON sessions/species at N >= 3/5/8;
- NEON species with >=5 eligible sessions in >=2 habitat groups;
- species with repeated sessions across >=2 sites;
- pathogen-grid recapture secondary estimability;
- shared Portal–NEON species meeting source-specific estimability;
- explicit non-estimable reasons;
- no ecological coefficient/p-value fields.

- [ ] **Step 2: Run tests and confirm RED**

Run: `python -m unittest tests.test_public_mammal_estimability -v`

- [ ] **Step 3: Implement the audit**

The audit may summarize `Packing_z` availability and distributions only for data-quality checks; it must not select model formulas based on association signs or significance.

- [ ] **Step 4: Run tests and full repository CI**

Run:
- `python -m unittest discover -s tests -v`
- standard repository CI.

Expected: all tests PASS.

- [ ] **Step 5: Write the estimability memo**

`docs/PUBLIC_MAMMAL_ESTIMABILITY_V1.md` must answer only:
- which planned contrasts are estimable;
- which species/context combinations have enough replication;
- which data-quality problems require a design amendment;
- whether H1–H4 can proceed as written.

- [ ] **Step 6: Commit**

Commit message: `Audit estimability of public mammal space-use study`

---

### Task 7: Freeze the Phase-2 Modeling Gate

**Files:**
- Create only if Task 6 passes: `validation/public_mammal_space_use_v1/estimability_gate_v1.json`
- Create only if design amendments are needed: a new reviewed spec version before any model implementation.

**Interfaces:**
- Consumes: Task 6 estimability report.
- Produces the immutable set of species, session-quality gates and context contrasts allowed into Phase 2.

- [ ] **Step 1: Evaluate the design against the estimability report without fitting ecological models**

Decision options:
- `proceed_as_designed`;
- `amend_design_before_modeling`;
- `stop_insufficient_estimability`.

- [ ] **Step 2: If proceeding, freeze the exact estimability gate**

Record:
- source-data fingerprints;
- included/excluded taxa rules;
- N threshold;
- minimum sessions/species/context replication;
- Portal treatment window;
- NEON habitat mapping fingerprint;
- session-table fingerprints.

- [ ] **Step 3: Run integrity tests**

Verify Phase 2 cannot silently change those values.

- [ ] **Step 4: Commit**

Commit message: `Freeze public mammal modeling estimability gate`

Phase 2 ecological-model implementation requires a separate reviewed implementation plan after this gate is known.
