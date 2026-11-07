# External species identity validation for the NEON conspecific–congeneric experiment

**Prepared 18 October 2026; no barcode-linked animal identities or spatial effects analysed.** This is the next distinct, source-authenticated evidence dependency after the historical *Peromyscus* F/C predictor-only feasibility audit.

## 2026-10-18 verified source linkage and COI API STOP

**The source feasibility has now been measured, but no species has been independently confirmed by DNA.** Both published products were pinned to `RELEASE-2026` and every inspected source CSV passed the official file byte-count/MD5 checks.

- Barcode source (DP1.10076.001): 884 `mam_BOLDtaxonomy` files and 884 `mam_BOLDvoucherInfo` files, each with 10,414 source rows and 10,412 distinct nonblank `sampleID` values. The source date window matching the project is 2016-03 through 2023-11.
- Box-trapping source (DP1.10072.001): 1,605 source `mam_pertrapnight` CSVs examined over 2015-04 through 2023-11. Source keys `earSampleID` and `sampleID` matched **9,646** exact archival samples with both BOLD tables, representing **9,617** distinct tagged-animal histories. Of *Peromyscus* tagged histories with any ear sample (19,130), **4,781** were unambiguously linked (24.99% **conditional on having an ear sample**, not coverage of all animals or independent genetic quality).
- The barcode `mam_BOLDtaxonomy.identificationMethod` was **`morphology` for all 10,414 rows**. The metadata therefore cannot itself independently verify the field-assigned species. Among the 9,646 linked sample IDs, 9,121 had agreeing exact field/BOLD `taxonID` metadata, 523 differed and 2 were unresolvable under the original NEON taxonomy; these numbers are **not** a sequenced-sample misidentification rate. Do not transfer BOLD metadata morphology labels into F/C as genetic truth.
- The BOLD v5 *public API* was tested in a single-record, deterministic, preregistered sample-ID pilot. The GitHub-hosted runner received **HTTP 403 at the preprocessor endpoint** (original sample ID never printed, no sequence returned). This is an endpoint-access STOP, **not** evidence that BOLD lacks corresponding sequences. Do not repeatedly try the same blocked endpoint, guess query IDs, or replace the original source with a changing BOLD snapshot without version control.
- DNA confirmation now depends on an authoritative sampleID → public BOLD processID / accession / immutable sequence export with recorded marker, sequence length, ambiguity fraction and contamination/QC; **none of this evidence is yet available for the matched 4,781 *Peromyscus* histories in the current workflow**. BOLD public data packages may help, but their whole-library reference snapshots are large and not a substitute for an unambiguous sample crosswalk.
- Even if high-quality COI records become accessible, mitochondrial markers alone cannot exclude hybrid ancestry or introgression. `P. leucopus` and `P. maniculatus` have documented secondary contact and gene flow (e.g. https://doi.org/10.1038/hdy201757); a prospective ecology study must include independent taxonomic reference validity, and nuclear/other marker validation when hybrid/admixed individuals matter.

**Science decision:** source sample linkage **GO**, molecular species confirmation **NOT ESTABLISHED**, independent prospective F/C×W/B ecological effect **SEALED**, original eight-genus generality and provisional holdout failures unchanged. Detailed machine-readable receipts:

- `results/neon_barcode_release2026_schema_receipt_20261018.json`
- `results/neon_barcode_capture_sample_key_linkage_receipt_20261018.json`
- `results/neon_bold_public_coi_single_sample_probe_receipt_20261018.json`

Next substantive action is a NEON/BOLD-supported *sequence-to-sample* crosswalk or alternative independently confirmed species identity source, not another regression of already-consumed W/B effects.

---

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
