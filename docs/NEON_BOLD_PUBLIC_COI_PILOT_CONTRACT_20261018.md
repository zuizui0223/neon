# One-sample, no-specimen-ID-publication BOLD v5 COI access pilot

**Frozen 2026-10-18 after NEON RELEASE-2026 morphological metadata join and before any live BOLD record is opened.**

## Scientific need and boundary

The source-verified DP1.10072.001 earSampleID-to-DP1.10076.001 sampleID join reached 9,646 exact barcode metadata sample IDs; 4,781 *Peromyscus* tagged capture histories were linked to the NEON archive's original four BOLD metadata tables. But **10,414/10,414 BOLD taxonomy rows explicitly have `identificationMethod=morphology`**, so source metadata are **not independent DNA species validation**. The 523 differing field/BOLD `taxonID` labels reflect metadata discrepancies, NOT independently detected genetic misidentifications. Direct public COI sequence evidence is the unresolved dependency.

The BOLD Data Portal v5 publicly documents a three-stage query API:
- `https://portal.boldsystems.org/api/query/preprocessor` (validate triplet)
- `https://portal.boldsystems.org/api/query` (obtain 24-hour query_id)
- `https://portal.boldsystems.org/api/documents/<query_id>/download?format=json` (BCDM documents)

Official documentation: https://portal.boldsystems.org/api; available filter `ids:sampleid:<source-id>`. No retired v3 API will be silently substituted.

## Fixed pilot sampling without spatial outcomes

1. Download checksum-verified *original RELEASE-2026* BOLD `mam_BOLDtaxonomy` source files using the verified barcode manifest. For this one-record API feasibility check, take the earliest source file **from each distinct published source site** (sorted by source site then month); among those records choose the lexicographically first nonblank `sampleID` with genus `Peromyscus` and known `taxonID` in NEON's public target taxonomy. Sample choice is **entirely based on pre-existing source metadata, not W/B, new F/C coefficients or sequence outcome**. Its value is retained in process memory only. No real sample ID is printed, serialized, committed or attached.
2. GET the published BOLD v5 API endpoints above using a bounded connection timeout and small response-byte cap. Only use public record and DNA sequence information; do not log input sample IDs or query IDs. If v5 responds with no matching public records, 403/429, an incompatible payload, or a redirect outside BOLD, STOP rather than claim a molecular result.
3. Log only whether all three requests completed, a public record with that exact source sampleID could be verified, document count, availability of a COI sequence/marker field, and counts of potentially sequence-related keys, with no raw DNA, specimen tags, sample IDs, barcodes, field locations or taxon names.
4. **A successful public sample-ID lookup is not genetic *species validation***. A species taxon in BOLD may still be morphology-assigned. Determining which species a high-quality COI actually supports requires a declared alignment/reference/BIN assignment and independent reference quality; no such study is opened by this pilot.
5. Do not issue a high-volume sequence download or query all 9,646 samples during this connectivity probe. If the API works, freeze source/version identifiers, accession/COI quality and species-assignment criteria BEFORE a larger source-matching investigation.

## Immutable old findings

- Original eight-genus Δ positive 5/8 vs six-required **FAILED**.
- Provisional Peromyscus positive-direction Δ **NOT REPLICATED and imprecise**; five-genus future modes **NOT ESTIMABLE**.
- MOSA animal identity remains a source-level HOLD and **all MOSA W/B effects remain SEALED**.
- New Peromyscus focal-versus-congener hypothesis remains future prospective; no source-index DNA result can rescue or confirm the previous W/B development associations.
