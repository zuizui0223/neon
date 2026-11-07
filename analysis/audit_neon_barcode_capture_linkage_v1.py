#!/usr/bin/env python3
"""NEON RELEASE-2026 sample-key linkage only: earSampleID vs BOLD sampleID.

This intentionally DOES NOT calculate movement, W, B, spatial distances,
density responses, specimen-level species assignments or genetic error
rates. It inspects the source-released tables and exports aggregate counts,
field/BOLD metadata *consistency*, identificationMethod frequencies and
join-key ambiguity. BOLD metadata is not proof of a DNA-validated species.

Original barcode files and capture source files are MD5/size checked by
the exact historical NEON reader. Raw sample IDs, tags, animal coordinates,
barcode sequences or specimen taxonomy rows are NEVER printed or serialized.
"""
from __future__ import annotations

import csv
import io
import json
import os
from collections import Counter, defaultdict
from pathlib import Path

from analysis.audit_neon_barcode_schema_v1 import (
    BARCODE_PRODUCT, extract_inventory, classify_file
)
from analysis.audit_multiscale_density_mnka_variation_v1 import (
    _capture_status, _taxonomy
)
from analysis.run_multiscale_density_estimability_release2026_v3 import (
    PRODUCT as CAPTURE_PRODUCT, RELEASE, QUERY_URL, TOKEN_ENV,
    _download_many, _inventory, _request_json, _site_codes
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_barcode_capture_linkage_v1.json"
SCHEMA=ROOT/"results/neon_barcode_release2026_schema_receipt_20261018.json"
START="2015-04"
END="2023-11"
NEUTRAL={"","NA","N/A","NULL"}


def value(row: dict, field: str) -> str:
    return str(row.get(field) or "").strip()


def known_code(text: object) -> str | None:
    t=str(text or "").strip()
    if t.upper() in NEUTRAL:
        return None
    # The source field describes one sample, not an arbitrary list; a
    # multi-value field is a distinct ambiguity, never silently split.
    return t


def choose_field(headers: list[str], canonical: str) -> str:
    matches=[k for k in headers if k.casefold()==canonical.casefold()]
    if len(matches)!=1:
        raise ValueError(f"Missing or ambiguous canonical source field {canonical}")
    return matches[0]


def parse_capture_file(raw: bytes, meta: dict, genus_by_taxon: dict[str,str]) -> dict:
    """Internal row-level source features, not user-visible exports."""
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    headers=list(reader.fieldnames or [])
    keys={k:choose_field(headers,k) for k in
          ("earSampleID","trapStatus","tagID","plotID","taxonID")}
    # Exact original 3-night source-event filter is not applied in this
    # key-coverage stage: barcode sampling also occurs on other trap nights.
    # This denominator is *not* the 1536-session W/B analysis universe.
    sample_events=[]
    stats=Counter()
    for r in reader:
        stats["all_trap_rows"]+=1
        if not _capture_status(value(r,keys["trapStatus"])):
            continue
        stats["capture_rows"]+=1
        taxon=value(r,keys["taxonID"])
        genus=genus_by_taxon.get(taxon)
        tag=known_code(value(r,keys["tagID"]))
        if genus is None:
            stats["capture_rows_outside_target_taxonomy"]+=1
            continue
        stats["target_captures"]+=1
        if not tag:
            stats["target_captures_no_tag"]+=1
            continue
        sample=known_code(value(r,keys["earSampleID"]))
        stats["target_captures_tagged"]+=1
        if not sample:
            continue
        stats["target_captures_with_ear_sampleID"]+=1
        if "|" in sample:
            stats["target_ear_sampleID_multivalue_rows"]+=1
            continue
        sample_events.append({
            "sample":sample,
            "history":(meta["site"],value(r,keys["plotID"]),tag),
            "site":meta["site"],
            "capture_year":meta["month"][:4],
            "genus":genus,
            "taxon":taxon,
        })
    return {"observations":sample_events,"counts":dict(stats),
            "earSampleID_column_verified":True}


def source_barcode_rows(
    files: list[dict], token: str, table: str
) -> tuple[dict[str,dict],dict]:
    chosen=[r for r in files if classify_file(r["name"])==table]
    if not chosen:
        raise ValueError("Missing barcode original source table: "+table)
    rawfiles=_download_many(chosen,token,max_workers=6)
    records={}
    counts=Counter()
    methods=Counter()
    for meta,raw in zip(chosen,rawfiles):
        reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
        fields=list(reader.fieldnames or [])
        samplekey=choose_field(fields,"sampleID")
        if table=="mam_BOLDtaxonomy":
            taxonomyfields=[choose_field(fields,k) for k in
                            ("taxonID","genus","species","identificationMethod")]
        else:
            taxonomyfields=[]
            choose_field(fields,"fieldID")
        for row in reader:
            counts["source_rows"]+=1
            sample=known_code(value(row,samplekey))
            if sample is None:
                counts["source_rows_missing_sampleID"]+=1
                continue
            if "|" in sample:
                counts["multivalue_sampleID_rows"]+=1
                continue
            target=records.setdefault(sample,{
                "sites":set(),"months":set(),"values":set(),"rows":0,
            })
            target["sites"].add(meta["site"])
            target["months"].add(meta["month"])
            target["rows"]+=1
            if table=="mam_BOLDtaxonomy":
                tup=tuple(value(row,k) for k in taxonomyfields)
                target["values"].add(tup)
                method=tup[3].strip()
                methods[method if method else "<blank>"]+=1
            else:
                # Voucher metadata may be repeated across reporting periods;
                # equality must be checked before accepting the sample key.
                target["values"].add(value(row,choose_field(fields,"fieldID")))
    counts["distinct_source_sampleIDs"]=len(records)
    counts["source_sampleIDs_with_multiple_rows"]=sum(v["rows"]>1 for v in records.values())
    counts["source_sampleIDs_at_multiple_sites"]=sum(len(v["sites"])>1 for v in records.values())
    counts["source_sampleIDs_with_conflicting_values"]=sum(len(v["values"])>1 for v in records.values())
    out={
        "table":table,"source_files_MD5_verified":len(chosen),
        **dict(counts),
        "taxonomy_identification_method_category_counts":(
            dict(sorted(methods.items(), key=lambda x:(-x[1],x[0]))[:16])
            if table=="mam_BOLDtaxonomy" else {}
        ),
        "taxonomy_identification_methods_remainder":(
            sum(methods.values())-sum(c for _v,c in sorted(methods.items(),
                key=lambda x:(-x[1],x[0]))[:16])
            if table=="mam_BOLDtaxonomy" else 0
        ),
    }
    return records,out


def summarize_keys(
    capture_rows: list[dict],
    barcode_taxonomy: dict,
    barcode_voucher: dict,
    genus_by_taxon: dict,
) -> dict:
    """Join only exact source IDs; report aggregate counts, no source labels."""
    sample_histories=defaultdict(set)
    sample_sites=defaultdict(set)
    sample_taxa=defaultdict(set)
    sample_years=defaultdict(set)
    history_genus=defaultdict(set)
    history_ear=defaultdict(set)
    for z in capture_rows:
        sample=z["sample"]; h=z["history"]
        sample_histories[sample].add(h)
        sample_sites[sample].add(z["site"])
        sample_taxa[sample].add(z["taxon"])
        sample_years[sample].add(z["capture_year"])
        history_genus[h].add(z["genus"])
        history_ear[h].add(sample)

    per_genus_histories=defaultdict(set)
    history_barcoded=defaultdict(set)
    link_sample_count=Counter()
    ambiguity=Counter()
    taxon_status=Counter()
    method_counts=Counter()
    capture_years=defaultdict(Counter)
    direct_linked_sampleIDs=set()
    for sample,hset in sample_histories.items():
        for h in hset:
            if "Peromyscus" in history_genus[h]:
                per_genus_histories["Peromyscus"].add(h)
        tax=barcode_taxonomy.get(sample)
        vou=barcode_voucher.get(sample)
        if tax is None:
            ambiguity["earSampleID_not_in_barcode_taxonomy"]+=1
            continue
        if vou is None:
            ambiguity["earSampleID_not_in_BOLD_voucherInfo"]+=1
            continue
        if len(hset)!=1:
            ambiguity["earSampleID_reused_between_animal_histories"]+=1
            continue
        if len(sample_sites[sample])!=1 or len(tax["sites"])!=1 or len(vou["sites"])!=1:
            ambiguity["sample_site_not_unique"]+=1
            continue
        if next(iter(sample_sites[sample])) not in tax["sites"] or tax["sites"]!=vou["sites"]:
            ambiguity["barcode_and_capture_site_mismatch"]+=1
            continue
        if len(tax["values"])!=1 or len(vou["values"])!=1:
            ambiguity["conflicting_barcode_taxonomy_or_voucherInfo"]+=1
            continue
        h=next(iter(hset))
        direct_linked_sampleIDs.add(sample)
        history_barcoded[h].add(sample)
        link_sample_count["unambiguous_samples_with_BOLD_taxonomy_and_voucher"]+=1
        if "Peromyscus" in history_genus[h]:
            link_sample_count["unambiguous_peromyscus_sample_links"]+=1
        barcode_tuple=next(iter(tax["values"]))
        taxon_id=barcode_tuple[0];method=barcode_tuple[3] or "<blank>"
        method_counts[method]+=1
        if taxon_id not in genus_by_taxon:
            taxon_status["BOLD_taxonID_outside_target_or_blank"]+=1
        elif len(sample_taxa[sample])!=1:
            taxon_status["field_sample_has_multiple_taxonID_labels"]+=1
        elif taxon_id in sample_taxa[sample]:
            taxon_status["metadata_same_taxonID"]+=1
        else:
            taxon_status["metadata_different_taxonID"]+=1
        for year in sample_years[sample]:
            capture_years[year]["linked_samples"]+=1

    all_histories=set(history_genus)
    peromyscus_histories={h for h,genera in history_genus.items() if "Peromyscus" in genera}
    peromyscus_with_BOLD={h for h in history_barcoded if h in peromyscus_histories}
    if any(len(s)!=1 for s in sample_histories.values() if False):
        raise AssertionError("unreachable code")
    return {
        "captured_samples_with_nonblank_single_earSampleID":len(sample_histories),
        "captured_sample_IDs_in_BOLD_taxonomy":sum(s in barcode_taxonomy for s in sample_histories),
        "captured_sample_IDs_in_BOLD_voucherInfo":sum(s in barcode_voucher for s in sample_histories),
        "capture_unique_histories_with_earSampleID":len(history_ear),
        "capture_unique_Peromyscus_histories_with_earSampleID":len(peromyscus_histories),
        "capture_unique_histories_with_unambiguous_BOLD_join":len(history_barcoded),
        "capture_unique_Peromyscus_histories_with_unambiguous_BOLD_join":len(peromyscus_with_BOLD),
        "Peromyscus_history_sample_link_coverage_within_ear_sampled_histories":(
            len(peromyscus_with_BOLD)/len(peromyscus_histories)
            if peromyscus_histories else None
        ),
        "source_key_anomalies":dict(ambiguity),
        "metadata_taxonID_consistency_not_DNA_verification":dict(taxon_status),
        "BOLD_identificationMethod_count_in_linked_samples":dict(method_counts),
        "capture_year_of_matched_sample_count":dict(sorted(capture_years.items())),
        "no_raw_sample_IDs_or_animal_labels_exported":True,
        "DNA_sequence_quality_or_species_identity_proven":False,
    }


def run() -> dict:
    token=os.environ.get(TOKEN_ENV,"").strip()
    if not token: raise RuntimeError("NEON_API_TOKEN required")
    if RELEASE!="RELEASE-2026": raise RuntimeError("Not frozen release")
    meta=json.loads(SCHEMA.read_text(encoding="utf-8"))
    if meta["status"]!="BARCODE_SOURCE_SCHEMA_VERIFIED_NO_BIOLOGICAL_MATCHES":
        raise RuntimeError("Original barcode source schema not verified")
    if meta["inventory_unique_files"]!=3536:
        raise RuntimeError("Barcode release metadata manifest drift")
    genus_targets=_taxonomy()[1]
    barcode_product_json=_request_json(
        f"https://data.neonscience.org/api/v0/products/{BARCODE_PRODUCT}"
    )
    barcode_sites=_site_codes(barcode_product_json)
    barcode_query=_request_json(
        QUERY_URL,token=token,
        body={
            "productCode":BARCODE_PRODUCT,"siteCodes":barcode_sites,
            "startDateMonth":START,"endDateMonth":END,
            "release":RELEASE,"package":"basic","includeProvisional":False,
        },
    )
    barcode_files=extract_inventory(barcode_query)
    if len(barcode_files)!=meta["inventory_unique_files"]:
        raise RuntimeError("Barcode source manifest size differs from frozen schema receipt")
    taxonomy,tax_stats=source_barcode_rows(barcode_files,token,"mam_BOLDtaxonomy")
    voucher,vou_stats=source_barcode_rows(barcode_files,token,"mam_BOLDvoucherInfo")

    cap_query=_request_json(
        QUERY_URL,token=token,
        body={
            "productCode":CAPTURE_PRODUCT,"siteCodes":barcode_sites,
            "startDateMonth":START,"endDateMonth":END,
            "release":RELEASE,"package":"basic","includeProvisional":False,
        },
    )
    cap_files=[x for x in _inventory(cap_query) if "mam_pertrapnight" in x["name"]]
    if not cap_files:
        raise RuntimeError("No historical pertrapnight capture source")
    raw_traps=_download_many(cap_files,token,max_workers=6)
    captured=[]
    overall=Counter()
    year_file_counts=Counter()
    for source,raw in zip(cap_files,raw_traps):
        item=parse_capture_file(raw,source,genus_targets)
        captured.extend(item["observations"])
        overall.update(item["counts"])
        year_file_counts[source["month"][:4]]+=1

    join=summarize_keys(captured,taxonomy,voucher,genus_targets)
    if join["capture_unique_Peromyscus_histories_with_unambiguous_BOLD_join"]==0:
        status="STOP_NO_UNAMBIGUOUS_PEROMYSCUS_BARCODE_SOURCE_LINK"
    else:
        status="BOLD_SAMPLE_ID_LINK_VERIFIED_METADATA_ONLY_NOT_DNA_VALIDATED"
    return {
        "schema":"neon.barcode_capture_sample_key_linkage.v1",
        "status":status,
        "sources":{
            "release":RELEASE,"barcode_product":BARCODE_PRODUCT,
            "box_trapping_product":CAPTURE_PRODUCT,
            "window":f"{START} through {END}",
            "barcode_inventory_files":len(barcode_files),
            "barcode_taxonomy_files_MD5_verified":tax_stats["source_files_MD5_verified"],
            "barcode_voucher_files_MD5_verified":vou_stats["source_files_MD5_verified"],
            "box_pertrapnight_files_MD5_verified":len(cap_files),
            "box_files_by_capture_year":dict(sorted(year_file_counts.items())),
            "source_data_scope":"All published basic pertrapnight files for barcode-covered sites and study years, not frozen historical W/B response sessions",
            "barcode_manifest_citation":"results/neon_barcode_release2026_schema_receipt_20261018.json",
        },
        "capture_source_counts":dict(overall),
        "BOLD_taxonomy_source_counts":tax_stats,
        "BOLD_voucher_source_counts":vou_stats,
        "source_sample_key_join":join,
        "scientific_boundary":{
            "sample_key_link_proves_genetic_species":False,
            "BOLD_metadata_species_conflict_proves_DNA_misidentification":False,
            "DNA_sequence_quality_assessed":False,
            "barcode_samples_random_population_subset":False,
            "biological_peromyscus_F_C_U_reclassified":False,
            "W_B_spatial_metrics_opened":False,
            "MOSA_spatial_effects_opened":False,
            "8_genus_original_generalization":"FAILED_5_OF_8",
            "original_provisional_directional_holdout":"NOT_REPLICATED_IMPRECISE",
            "next":"Evaluate source identificationMethod and independent quality-controlled COI/BOLD calls; verify barcode sample selection and key conflicts before any prospective species F/C×W/B ecological outcomes.",
        },
    }


def main():
    try:
        result=run()
    except Exception as exc:
        result={
            "schema":"neon.barcode_capture_sample_key_linkage.v1",
            "status":"STOP_BARCODE_SAMPLE_LINKAGE_SOURCE_ERROR",
            "diagnostic":str(exc)[:850],
            "W_B_spatial_metrics_opened":False,
        }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if result["status"]=="BOLD_SAMPLE_ID_LINK_VERIFIED_METADATA_ONLY_NOT_DNA_VALIDATED" else 3


if __name__=="__main__":
    raise SystemExit(main())
