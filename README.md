# NEON small-mammal local spatial cohesion

Independent repository for the ecological paper:

**Local spatial cohesion in small mammals is redundant across species but context-dependent across sites**

## Scientific result

### 1. Original confirmatory programme

Across 16 response-naive National Ecological Observatory Network small-mammal sites:

- pooling species increased the declared local spatial-cohesion fraction beyond the best individual species at **0/16** sites;
- median pooled-minus-best-species gain = **0**;
- preregistered null-adjusted sign test: **p = 1.0**;
- no strict emergent adjacency criterion occurred;
- every site contained at least one individually sufficient species;
- ORNL showed the sole weakest-link case: pooled cohesion **0.25** versus best species **1.0**.

The endpoint is a **no-isolated-occurrence** criterion, not whole-landscape dispersal connectivity.

### 2. Carrier identity and ecological roles

Across the original 16 sites:

- 48 site × carrier records comprise **32 species**;
- 20/32 carrier species occur as carriers at one site only;
- no carrier species occurs at more than 3/16 sites;
- only 18/120 site pairs share any carrier species;
- median pairwise carrier-set Jaccard similarity = **0**;
- trophic groups among carriers: **13 granivores, 10 herbivores, 7 omnivores, 2 predators**;
- 12/13 multi-carrier sites span multiple trophic groups;
- MOAB and OAES contain carriers from all four primary trophic groups.

Thus the shared property is not general functional equivalence. Different ecosystem-effect roles converge on the same local spatial-response state.

### 3. Independent prospective mechanism validation

All 11 remaining response-blind structurally eligible sites were frozen and then consumed once:

**SRER, STEI, STER, TALL, TEAK, TOOL, TREE, UKFS, WOOD, WREF, YELL**

Primary count-conditioned result:

- scored sites: **11/11**, stops: **0**;
- median site carrier excess = **-0.0804**;
- positive site effects = **4/11**;
- one-sided exact sign test: **p = 0.8867**;
- positive spatial organization beyond prevalence was **not supported**.

Predeclared grid-conditioned decomposition:

- median between-grid allocation component = **-0.0804**;
- median within-grid organization component = **0**;
- positive within-grid site effects = **0/11**;
- grid-conditioned expectation reproduced observed carrier state exactly in **66/68** eligible species × site records.

Among 15 species repeated across fresh sites, **10/15 switched carrier ↔ non-carrier state**.

The current ecological synthesis is:

> **Local spatial cohesion is a context-dependent species × site state. Ecologically different species can converge on it, but the same species can leave that state at another site because its grid-scale occurrence allocation changes.**

Grid identity is a spatial stratum and potential habitat proxy, not a measured habitat covariate.

## Active Oikos submission state

The V6 scientific and anonymous-review package is CI-complete.

Active main text:
- `manuscript/neon_metacommunity_redundancy/MANUSCRIPT_V6_MECHANISM_VALIDATED_DRAFT.md`

Active cover letter:
- `manuscript/neon_metacommunity_redundancy/COVER_LETTER_OIKOS_V5.md`

CI generates:
- `oikos_main_text_anonymous.docx`
- `oikos_anonymous_review_package.zip`
- `Figure_1.png`
- `Figure_2.png`
- `Figure_3.png`
- `Figure_4.png`
- `Figure_5.png`

Automated checks cover:
- original 16-site frozen confirmatory invariants;
- carrier-turnover and all-32 niche-role recomputation;
- frozen standardized trait diagnostics;
- 11-site once-only mechanism response values;
- count-conditioned and grid-conditioned decomposition identities;
- V6 abstract length, anonymity and claim boundaries;
- double spacing, continuous line numbers and page numbers in DOCX;
- Introduction beginning on page 2;
- author-neutral review ZIP with deterministic manifest checks;
- Figure 1–5 PNG generation.

Current remaining blocker:
- final author/admin metadata for the separate title page and ScholarOne declarations.

See:
- `submission/OIKOS_READINESS_V3.md`
- `submission/SUBMISSION_FORM_FIELDS_V2.md`
- `submission/TITLE_PAGE_TEMPLATE_V2.md`
- `submission/SIGNIFICANCE_STATEMENT_V3.md`
- `submission/DATA_AVAILABILITY_STATEMENT_V3.md`

## Project boundary

- Paper A — local spatial cohesion, carrier turnover and fresh mechanism validation: **active submission mainline**
- Paper B — later small-mammal continuity shell: deferred until Paper A is resolved
- world-survival identifiability methods paper: outside this repository
- NEON camera-trap programme: terminally stopped and excluded

Historical `eog.*` schema names remain only inside immutable provenance files for auditability.
