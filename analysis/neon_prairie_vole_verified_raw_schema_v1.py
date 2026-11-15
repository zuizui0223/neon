#!/usr/bin/env python3
"""Exact original public Figshare logger and capture CSV: headers and counts only.

Provider file id, byte length, MD5 fixed from source-only Figshare metadata.
Does not read/tag-score animal contact or capture biology; no IDs exported.
"""
from __future__ import annotations
from datetime import datetime,timezone
from pathlib import Path
from hashlib import md5,sha256
from urllib.request import Request,urlopen
from io import StringIO
import csv,json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_prairie_vole_verified_raw_schema_20261115.json"
PIN={
 "collar_ids.csv":(50635479,1550,"11c9ec94411df6553110101f6770c7b5"),
 "proxlog_summary.csv":(50636031,2378,"d9f1379ce162695496f223c5fddd0540"),
 "full_voles_trap.csv":(50636346,185698,"8b6ac53786fae959ab0087d9c39b8e13"),
 "prox_full_noduplicates.csv":(50636655,1973533,"29e1db3d6c0099822e1573267d9077c7"),
 "rfid_trap_network_data_method.csv":(50636994,93557,"a2f4000270ab7c88b74fa39e44c39baa"),
 "collar_success_long.csv":(50637150,862,"e2b5075c1ead340cdeb07d6a8b93d752"),
 "global_ids.csv":(50637252,7174,"4c353d8c131e99df46d98fb025709f98")
}
STAGE="GET_PROVIDER_EXACT_RAW_BYTES"

def get_original(name):
    file_id,size,md5_expected=PIN[name]
    req=Request("https://ndownloader.figshare.com/files/"+str(file_id),
                headers={"User-Agent":"NEON-prairie-vole-sensor-source-audit/1"})
    with urlopen(req,timeout=120) as r:
        raw=r.read(size+1)
    if len(raw)!=size or md5(raw).hexdigest()!=md5_expected:
        raise ValueError("PUBLIC_SOURCE_SIZE_OR_PROVIDER_MD5_MISMATCH")
    return raw

def header_and_shape(raw):
    rdr=csv.DictReader(StringIO(raw.decode("utf-8-sig")))
    header=rdr.fieldnames or []
    if len(header)!=len(set(header)) or not header or any(not x for x in header):
        raise ValueError("SOURCE_COLUMNS_DUPLICATED_OR_MISSING")
    n=bad=0
    for row in rdr:
        n+=1
        if None in row or any(x is None for x in row.values()):bad+=1
    return {"column_names":header,"source_data_rows":n,"ragged_rows":bad}

def audit():
    global STAGE
    if sum(x[1] for x in PIN.values())>2_500_000:
        raise ValueError("PUBLIC_SOURCE_SIZE_BUDGET_EXCEEDED")
    raws={name:get_original(name) for name in PIN}
    STAGE="CHECK_PUBLIC_CSV_HEADERS_AND_ROW_SHAPES"
    summary={}
    for name in sorted(raws):
        ident,sz,h=PIN[name]
        record=header_and_shape(raws[name])
        if record["ragged_rows"] or not record["source_data_rows"]:
            raise ValueError("SOURCE_RAGGED_OR_EMPTY_"+name)
        summary[name]={
            "source_file_id":ident,"verified_size_bytes":sz,
            "verified_provider_MD5":h,**record
        }
    required=("prox_full_noduplicates.csv","full_voles_trap.csv",
              "collar_ids.csv","global_ids.csv")
    if any(name not in summary for name in required):
        raise ValueError("MISSING_PAIRED_SOURCE_CATEGORY")
    return {
        "schema":"neon.prairie_vole_original_paired_detector_source_schema.v1",
        "status":"SOURCE_ORIGINAL_LOGGER_AND_TRAP_CSV_GO_HEADERS_ONLY",
        "source_metadata":{
            "figshare_public_project_id":228462,
            "original_study_DOI":"10.1093/jmammal/gyaf032",
            "published_source_count":len(summary),
            "original_source_total_bytes":sum(x[1] for x in PIN.values()),
            "all_file_size_and_provider_MD5_verified":True,
            "schema_summary_SHA256":sha256(json.dumps(
                summary,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        },
        "headers_and_row_counts":summary,
        "source_next_gate":{
            "raw_proximity_and_trapping_event_linkage_NOT_yet_verified":True,
            "published_collar_PIT_ID_mapping_must_be_validated":True,
            "same_time_window_and_logger_operability_required":True,
            "device_losses_cannot_be_called_contact_absence":True,
            "one_original_enclosed_vole_population_only":True
        },
        "scientific_boundary":{
            "zero_original_animal_contact_or_trap_event_outcomes_scored":True,
            "no_exact_PIT_tag_animal_ID_device_ID_date_or_coordinate_exported":True,
            "published_2025_original_R2_0_02_is_prior_art":True,
            "NEON_Portal_Finland_Structural_original_effects_not_reopened":True,
            "one_NEON_manuscript_DRAFT_SUBMISSION_HOLD":True
        },
        "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }

def main():
    global STAGE
    try: result=audit();code=0
    except Exception as exc:
        result={
            "schema":"neon.prairie_vole_original_paired_detector_source_schema.v1",
            "status":"STOP_FIGSHARE_ORIGINAL_RAW_TRANSPORT_OR_SCHEMA",
            "failed_stage":STAGE,"error_class":type(exc).__name__,
            "no_biological_event_outcome_scored":True
        };code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return code
if __name__=="__main__":raise SystemExit(main())
