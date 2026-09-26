# NEON small-mammal spatial continuity

Independent repository for the ecological paper:

**Small-mammal spatial continuity is locally redundant but carried by different species across sites**

## Scientific result

### Confirmatory

Across 16 fresh National Ecological Observatory Network small-mammal sites:

- pooled-community continuity exceeded the best individual species at **0/16** sites;
- median community-minus-best-species continuity gain = **0**;
- preregistered null-adjusted sign test: **p = 1.0**;
- no strict emergent adjacency criterion occurred;
- at every site, at least one individual species satisfied every prespecified adjacency criterion;
- ORNL showed the sole weakest-link case: pooled continuity **0.25** versus best-species **1.0**.

### Exploratory positive structure

Using only frozen site summaries:

- 48 site × continuity-carrier records comprise **32 species**;
- 20/32 carrier species occur as carriers at one site only;
- no carrier species occurs at more than 3/16 sites;
- only 18/120 site pairs share any carrier species;
- median pairwise carrier-set Jaccard similarity = **0**;
- median redundancy depth = **2 species/site**.

The ecological synthesis is:

> **within-site redundancy + among-site turnover in continuity-carrier identity**

## Active Oikos submission state

The scientific and anonymous-review package is complete.

Active main text:
- `manuscript/neon_metacommunity_redundancy/MANUSCRIPT_V5_OIKOS_INITIAL_SUBMISSION.md`

CI generates:
- `oikos_main_text_anonymous.docx`
- `oikos_anonymous_review_package.zip`
- `Figure_1.png`
- `Figure_2.png`
- `Figure_3.png`
- `Figure_4.png`

Automated checks cover:
- frozen confirmatory invariants;
- deterministic exploratory carrier-turnover recomputation;
- abstract length and anonymity;
- Oikos V5 main-text structure;
- double spacing, continuous line numbers and page numbers in DOCX;
- Introduction beginning on page 2;
- author-neutral review ZIP with manifest checks;
- deterministic ZIP rebuild;
- upload-ready PNG figure generation.

Current remaining blocker:
- final author/admin metadata for the separate title page and ScholarOne declarations.

See:
- `submission/OIKOS_READINESS_V2.md`
- `submission/SUBMISSION_FORM_FIELDS_V1.md`
- `submission/TITLE_PAGE_TEMPLATE_V1.md`

## Project boundary

- Paper A — metacommunity redundancy + carrier turnover: **active submission mainline**
- Paper B — later small-mammal continuity shell: deferred until Paper A is resolved
- world-survival identifiability methods paper: outside this repository
- NEON camera-trap programme: terminally stopped and excluded

Historical `eog.*` schema names remain only inside immutable provenance files for auditability.
