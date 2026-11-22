# Release-frozen small mammal ear-tissue-to-BOLD source linkage, before ecology

**Frozen 18 October 2026, after BOLD schema inventory and before any barcode row/earSampleID join.**

## Purpose and provenance

Verify whether the published **RELEASE-2026** NEON small mammal DNA barcode (DP1.10076.001) can be connected unambiguously to the **RELEASE-2026** box trapping (DP1.10072.001) ear-sample records, in particular for *Peromyscus* source animals. **No spatial W, B, Δ, density effect, activity centre or home range may be opened in this source-level audit.**

The original barcode product includes 884 files per BOLD collection, specimen, taxonomy and voucher table for 2016-03 through 2023-11, covering 46 source sites in the inspected versioned release. These tables have a common `sampleID`. The original `mam_pertrapnight` is expected to include `earSampleID` but the **actual key overlap, site/date agreement and ambiguous duplicates have not been observed at the time this contract is frozen**.

The source releases are immutable and all downloaded bytes must match the published MD5 and byte count; initial table headers must match the recorded checked original table schemas or stop. Query barcodes over 2015-04 through 2023-11 (there were no barcode table files before 2016-03 in the source inventory), and box trapping over 2015-04 through 2023-11 at all barcode-available sites. Do not access 2024–2026 box trapping or any provisional file.

## Exact source keys and counts, before reading any biological species outcomes

- The canonical BOLD key is exact nonblank `sampleID` in `mam_BOLDvoucherInfo` and `mam_BOLDtaxonomy`. Do not treat the BOLD `fieldID` as a surrogate for `earSampleID` without its own explicit source-confirmed contract.
- The canonical capture key is exact nonblank `earSampleID` in `mam_pertrapnight`. A box-trap record must be a true capture by the frozen historical `_capture_status` rule and have a nonblank source `tagID`. The animal key is `(site, plotID, tagID)`. No source ID, barcode, sample ID, genome sequence or actual coordinate is exported.
- Neutral missing markers (`NA`, `N/A`, `NULL`, empty) are not sample IDs. Multiple IDs in a field separated by `|` are flagged ambiguous and cannot be silently split.
- Repeated records with identical sampleID and the same animal history can be deduplicated *for matching counts only*. If one exact sampleID occurs in multiple animal histories, **exclude that sampleID from unambiguous joins** and report the count.
- If barcode `sampleID` occurs in multiple source sites or has conflicting taxonomy rows, report conflict and exclude from automatic species confirmation. The barcode `mam_BOLDvoucherInfo` must be present for a taxonomy sample to be called cross-table verifiable.
- Count capture rows with `earSampleID` and the distinct animal histories represented, the distinct barcode sample IDs, matched sample IDs, matched marked-animal histories, repeated/ambiguous sample keys, Peromyscus-subset sample coverage, and overlaps by capture year; **use population counts only for animals observed in the source window, not inference about the entire 2015–2026 NEON universe**.
- Summarize **frequency of `mam_BOLDtaxonomy.identificationMethod`** and completeness of `species` and `taxonID`, as captured in source metadata. A BOLD taxonomy table field is **not** by itself molecular confirmation, because source sample metadata can reflect field/morphological assignment. Do not automatically relabel a field `taxonID` using barcode metadata.
- Compare field and BOLD taxonomy codes only when both exact NEON target `taxonID` codes are available and unambiguous. Report identity agreement/disagreement as **metadata consistency**, not a measured genetic misidentification rate. Never print specimen identifiers or per-animal differences.
- Barcoding is targeted (at most 95 individuals per domain per year under the published sampling design); linked specimens are not a probability sample of all captured mammals. A barcode hit fraction therefore estimates **data link coverage**, not population-level species error, and must not be extrapolated to unsequenced animals.
- If **either source is inaccessible**, canonical key is missing, no matching keys exist, or checksum/identity uniqueness fails, publish a reproducible `STOP` receipt. Do not manufacture a crosswalk from similar strings or convenient taxa.

## Output and publication boundary

Release only aggregate per-year/site-count and Peromyscus-source identity coverage with `source_count`, `matched_count`, `ambiguous_count`, `species_label_metadata_status`, `identificationMethod` category counts, and source MD5/inventory totals. Suppress tiny per-site per-species cells and do not expose barcodes or tag IDs. First finish the source-linkage audit; an explicit separate effect-blind barcode taxonomy/quality protocol will determine whether any source matched sample supplies defensible DNA-based species evidence.

**No past NEON W/B outcome changes**: original 8-genus 6/8 generality criterion FAILED (5/8); provisional time-heldout *Peromyscus* directional replication FAILED/IMPRECISE; five-genus mode test NOT ESTIMABLE; MOSA effects remain SEALED. The prospective focal species vs congener hypothesis remains a proposed future ecological study, not a confirmed result.
