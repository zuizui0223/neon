# External species identity validation for the NEON conspecific–congeneric experiment

**Prepared 18 October 2026; no barcode-linked animal identities or spatial effects analysed.** This is the next distinct, source-authenticated evidence dependency after the historical *Peromyscus* F/C predictor-only feasibility audit.

## Biological purpose

The NEON RELEASE-2026 historical structural audit found that focal species and congeneric known-alive indices can vary independently across 33 NEON sites. But explicit field-identification uncertainty alters the unresolved Peromyscus genus-MNKA fraction from 9.59% to **53.35%** in a deliberately conservative multi-occasion index. That is **not** a 53% misidentification rate. To ask whether conspecific versus congeneric numbers lead to different responses within animals W and among observed centres B, first obtain an **independent check of which field-assigned species labels are biologically credible**.

Crucially, NEON has a public **Small mammal sequences DNA barcode** data product, **DP1.10076.001**, containing COI barcoding and BOLD-linked specimen taxonomic information. NEON's user guide describes `earSampleID` in the box-trapping `mam_pertrapnight` table (DP1.10072.001) as the linking key to that barcode product. This is an actionable data bridge, not a speculative unavailable DNA source.

Official source references:
- https://data.neonscience.org/data-products/DP1.10076.001
- https://data.neonscience.org/data-products/DP1.10076.001/RELEASE-2026
- https://data.neonscience.org/documents/10179/2838366/NEON_DNAbarcoding_userGuide_vB/cb0f2f96-ff0f-bee1-8363-8e86c3ccd323?version=1.0 — specifically section 3.6.3 regarding `earSampleID`
- https://data.neonscience.org/api/v0/documents/quick-start-guides/NEON.QSG.DP1.10072.001v1?fallback=html&inline=true — `identificationQualifier` field indicates doubts in field taxon determination.

## Source-only validation sequence, before any W/B ecology

1. Pin the exact versioned **RELEASE-2026** barcode dataset inventory and checksum-verified `mam_BOLDcollectionData`, `mam_BOLDspecimenDetails`, `mam_BOLDtaxonomy` and `mam_BOLDvoucherInfo` tables wherever present; do not silently mix provisional new sequences or later corrected historical releases into the frozen historical comparison.
2. Inspect actual source data dictionary/CSV headers to identify the canonical counterpart of `earSampleID` in the barcode tables. **Fail closed on missing or ambiguous key.** Verify raw box-trap source `earSampleID` is linked to one source animal history `site × plot × tagID`, guarding against duplicates, samples with missing tag and multi-animal sample codes. Count coverage; do not publish animal/tag IDs.
3. Join only immutable specimen/sample identifiers and **quality-controlled taxonomic determinations** to originally stable field-taxon codes. A BOLD record with a genus-only assignment or ambiguous reference match must remain U, not a species-level correction. Where the DNA-assigned species conflicts with field IDs, report discrepancy as a warning and document authoritative metadata rather than automatically reclassifying all captures.
4. Independently summarize F/C/U composition at the source level and study the size and direction of possible identification changes in *Peromyscus*, **without computing W/B, distance, centroid, Δ or abundance–space slopes**. Aggregate by species and site counts only where non-identifying.
5. Make sampling selection explicit: NEON's barcode programme prioritizes taxonomically difficult rodents and is not a random draw of captured animals. Therefore the disagreement rate in barcoded samples **cannot be extrapolated as population-level misidentification without a selection model**.
6. Reassess residual independent predictor variation after original taxon×plot, site×calendar-month and year controls, and after a predeclared U handling plan; retain old failure records and do not reduce site/session thresholds to obtain a positive result.

## Interpretability / design STOP

- A linked ear-punch barcode at one moment need not characterize multiple original individuals if raw tag records are recycled or ambiguous. Do not forcibly propagate a barcode to unrelated captures.
- Unlinked or failed sequencing remains U; lack of sequence is **not** proof of correct field identification.
- An independent species-label validation is needed but **not sufficient** to infer competition, territoriality, true density or full home ranges from three-night trap locations.
- If barcode product coverage or joinability is too poor in the relevant focal species × site×plot series, STOP species-specific future ecological claims until independent sampling can validate identities; do not use only the favorable barcoded subset to rescue the previously failed original 8-genus packing hypothesis.
- Even if linked predictor structure is feasible, the F/C×W/B ecological question still requires truly new response-unconsumed capture events, detection controls and independent site replication. The 2025–26 provisional outcomes already opened in NEON do **not** count as unseen future validation.

## Status at preparation

- Published DP1.10076.001 and `earSampleID` link are verified from NEON documentation.
- **No** actual DNA-barcode CSV, BOLD taxonomic matches, matching sample IDs, matched sample counts, individual reclassification, or spatial W/B effects have been fetched/computed by this plan.
- Original NEON developmental 6/8 generality criterion **FAIL (5/8)**, temporal *Peromyscus* positive-sign result **NOT REPLICATED/IMPRECISE**, five-genus test **NOT ESTIMABLE**, MOSA external effects **SEALED**; ecology manuscript remains DRAFT/HOLD.
