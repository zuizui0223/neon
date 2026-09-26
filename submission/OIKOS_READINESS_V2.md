# Oikos submission readiness — V2

Checked against the current Nordic Society Oikos author instructions on 2026-09-26.

## Article type

**Research Paper**

The paper is empirical, prospectively designed, and framed around a general ecological distinction rather than a taxon-only extension.

## Scientific package

### PASS — confirmatory claim frozen

- 16/16 fresh sites scored
- pooled continuity > best species at 0/16 sites
- no strict emergent adjacency criterion
- universal individual-species sufficiency
- ORNL weakest-link case retained with endpoint-specific interpretation

### PASS — exploratory positive result separated

The post hoc frozen-summary extension is explicitly exploratory:

> within-site redundancy + among-site turnover in continuity-carrier identity

The exploratory analysis cannot alter the confirmatory decision.

## Oikos initial-submission materials

### PASS — anonymous main text

Active source:
`manuscript/neon_metacommunity_redundancy/MANUSCRIPT_V5_OIKOS_INITIAL_SUBMISSION.md`

Automated checks verify:
- no author-identifying strings;
- abstract <=300 words;
- no unexplained NEON/ORNL acronym in the abstract;
- no Data Availability Statement embedded in main text;
- AI-use statement is the final main-text section;
- internal claim-boundary and figure-plan scaffolding removed.

### PASS — formatted DOCX

CI produces:
`oikos_main_text_anonymous.docx`

Structural checks verify:
- author metadata blank;
- 12-point Times New Roman base style;
- double spacing;
- continuous line numbering;
- page-number field;
- Introduction forced to page 2.

A final visual check of the ScholarOne-generated review PDF remains necessary before pressing Submit.

### PASS — anonymous data/code review archive

CI produces:
`oikos_anonymous_review_package.zip`

Checks verify:
- no author-identifying repository strings;
- explicit per-file SHA-256 manifest;
- confirmatory and exploratory boundaries included;
- deterministic rebuild produces the same archive hash;
- no source-control history, repository URL, title page or cover letter included.

### PASS — Data Availability Statement

Active form text:
`submission/DATA_AVAILABILITY_STATEMENT_V2.md`

Per NSO instructions this text belongs in the submission form, not the main manuscript.

### PASS — Significance Statement

Active form text:
`submission/SIGNIFICANCE_STATEMENT_V2.md`

It now explicitly states how the study relates to prior literature and that the manuscript does not cite prior author-authored work.

### PASS — AI-use disclosure

The AI-use statement is at the end of V5 main text and identifies the tool and purposes of use.

## Remaining author-input blockers

Only administrative metadata remain:

1. final author list and order;
2. exact affiliations;
3. corresponding-author details and ORCID(s);
4. CRediT contributions;
5. funding statement;
6. conflict-of-interest declaration;
7. ethics/permit statement, if applicable;
8. acknowledgments, if any;
9. NSO equity, diversity and inclusion declaration.

These items are intentionally not inferred from repository history or prior drafts.

Use:
`submission/TITLE_PAGE_TEMPLATE_V1.md`
and
`submission/SUBMISSION_FORM_FIELDS_V1.md`

## Current status

**Scientific and anonymous-review package: complete.**

**Upload-ready files: generated automatically in CI.**

**Only author/admin metadata remain before an actual ScholarOne submission can be finalized.**
