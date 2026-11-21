#!/usr/bin/env python3
"""Independent 2025 prairie-vole direct logger vs trap RECORD LINKAGE gate.

An initial published nine-file MD5/header audit is frozen. Open event rows
ONLY to test predeclared animal ID namespace, source dates and collar
deployments, NOT to test whether trap associations predict direct contacts.
No biological effect, dyad-positive summaries, social network coefficients,
contact frequency, or raw tag/date/coord values are exported.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import date,datetime,timezone
from io import StringIO
from pathlib import Path
from urllib.parse import urlparse
import csv,hashlib,json,re

from analysis.run_neon_prairie_vole_figshare_file_headers_v1 import (
    PIN,BASE,fetch_json,check_filename_file
)
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_prairie_vole_original_contact_trap_source_join_20261115.json"
FROZEN_ORIGINAL_MD5={
 "collar_ids.csv":"11c9ec94411df6553110101f6770c7b5",
 "proxlog_summary.csv":"d9f1379ce162695496f223c5fddd0540",
 "full_voles_trap.csv":"8b6ac53786fae959ab0087d9c39b8e13",
 "prox_full_noduplicates.csv":"29e1db3d6c0099822e1573267d9077c7",
 "rfid_trap_network_data_method.csv":"a2f4000270ab7c88b74fa39e44c39baa",
 "global_ids.csv":"4c353d8c131e99df46d98fb025709f98"
}
FIELDS={
 "collar_ids.csv":("tag","collar","date_on","date_off"),
 "proxlog_summary.csv":("date","tag","collar on","collar off","collar download","file"),
 "full_voles_trap.csv":("date","enclosure","stake.trap","tag"),
 "prox_full_noduplicates.csv":("c1","c2","date","datetime"),
 "rfid_trap_network_data_method.csv":("VertexFrom","VertexTo","TimeStart","TimeStop","DataType"),
 "global_ids.csv":("tag","sex")
}
ORIGINAL_ROWS={
 "collar_ids.csv":38,
 "proxlog_summary.csv":76,
 "full_voles_trap.csv":4454,
 "prox_full_noduplicates.csv":50741,
 "rfid_trap_network_data_method.csv":2588,
 "global_ids.csv":648
}
STAGE="REVERIFY_PINNED_BYTES"
PHASES={"REVERIFY_PINNED_BYTES","ORIGINAL_EVENT_SCHEMA",
        "ID_NAME_SPACE_AND_SEASON_TIME","COLLAR_DATE_EFFORT_FEASIBILITY"}
def good(v,label):
    if not v:raise ValueError("PUBLIC_PRAIRIE_VOLE_ID_SOURCE_STOP_"+label)
def source_bytes(name):
    aid,fid,size=PIN[name]
    obj=fetch_json(f"{BASE}/articles/{aid}")
    f=[x for x in obj.get("files",[]) if x.get("id")==fid and x.get("name")==name]
    good(obj.get("id")==aid and len(f)==1,"ARTICLE_NAME_FILE_PIN")
    f=f[0]
    good(f.get("size")==size and not f.get("is_link_only"),"FILE_SIZE_LINK")
    md5=f.get("computed_md5") or f.get("supplied_md5")
    good(isinstance(md5,str) and md5.lower()==FROZEN_ORIGINAL_MD5[name],"MD5_PROVIDER_PIN")
    raw=check_filename_file(f.get("download_url"),fid,size)
    good(len(raw)==size and hashlib.md5(raw).hexdigest()==FROZEN_ORIGINAL_MD5[name],
         "ORIGINAL_BYTES_MD5")
    return raw
def parse(name,raw):
    reader=csv.DictReader(StringIO(raw.decode("utf-8-sig")))
    good(set(FIELDS[name]) <= set(reader.fieldnames or []),"ORIGINAL_COLUMNS_"+name)
    rows=list(reader)
    good(len(rows)==ORIGINAL_ROWS[name],"ORIGINAL_ROWS_"+name)
    good(all(None not in x for x in rows),"ORIGINAL_RAGGED_"+name)
    return rows
def ident(value):
    """Exact published tag namespace. Never guess/merge based on an effect."""
    if value is None:return ""
    return str(value).strip()
def time_date(value):
    """Recognized explicit date formats only; ambiguous formats not silently guessed."""
    s=str(value or "").strip()
    if not s:return None
    if re.match(r"^\d{4}-\d\d-\d\d",s):
        try:return date.fromisoformat(s[:10])
        except ValueError:return None
    for fmt in ("%m/%d/%Y","%m/%d/%y","%Y/%m/%d",
                "%d-%b-%Y","%d-%b-%y","%m-%d-%Y"):
        try:return datetime.strptime(s.split(" ")[0],fmt).date()
        except ValueError:pass
    return None

def run():
    global STAGE
    files={name:source_bytes(name) for name in FROZEN_ORIGINAL_MD5}
    STAGE="ORIGINAL_EVENT_SCHEMA"
    tables={name:parse(name,raw) for name,raw in files.items()}
    collars=tables["collar_ids.csv"]
    traps=tables["full_voles_trap.csv"]
    logger=tables["prox_full_noduplicates.csv"]
    network=tables["rfid_trap_network_data_method.csv"]
    animals=tables["global_ids.csv"]
    summaries=tables["proxlog_summary.csv"]
    STAGE="ID_NAME_SPACE_AND_SEASON_TIME"
    tag_set={ident(r["tag"]) for r in collars if ident(r["tag"])}
    device_set={ident(r["collar"]) for r in collars if ident(r["collar"])}
    trap_set={ident(r["tag"]) for r in traps if ident(r["tag"])}
    global_set={ident(r["tag"]) for r in animals if ident(r["tag"])}
    network_set={ident(v) for r in network for v in
                 (r["VertexFrom"],r["VertexTo"]) if ident(v)}
    logger_set={ident(v) for r in logger for v in
                (r["c1"],r["c2"]) if ident(v)}
    counts={
      "logger_endpoints_as_exact_collared_animal_tag":sum(
        ident(v) in tag_set for r in logger for v in (r["c1"],r["c2"])),
      "logger_endpoints_as_exact_collar_device_id":sum(
        ident(v) in device_set for r in logger for v in (r["c1"],r["c2"])),
      "logger_endpoints_as_exact_trap_animal_tag":sum(
        ident(v) in trap_set for r in logger for v in (r["c1"],r["c2"])),
      "logger_endpoints_as_exact_global_animal_tag":sum(
        ident(v) in global_set for r in logger for v in (r["c1"],r["c2"])),
      "trap_records_tag_in_original_collar_deployments":sum(
        ident(r["tag"]) in tag_set for r in traps),
      "trap_records_tag_in_original_global_sex_table":sum(
        ident(r["tag"]) in global_set for r in traps),
      "network_endpoints_in_collar_animal_tags":sum(
        ident(v) in tag_set for r in network for v in (r["VertexFrom"],r["VertexTo"])),
      "network_endpoints_in_trapped_animal_tags":sum(
        ident(v) in trap_set for r in network for v in (r["VertexFrom"],r["VertexTo"])),
      "network_endpoints_in_global_animal_tags":sum(
        ident(v) in global_set for r in network for v in (r["VertexFrom"],r["VertexTo"])),
    }
    universe={
      "original_logger_rows":len(logger),
      "logger_endpoint_source_slots":2*len(logger),
      "original_trapping_rows":len(traps),
      "original_trap_network_rows":len(network),
      "original_collar_deployment_rows":len(collars),
      "original_logger_campaign_summary_rows":len(summaries),
      "original_global_animal_metadata_rows":len(animals),
      "distinct_original_collar_animal_tag_labels":len(tag_set),
      "distinct_original_collar_device_labels":len(device_set),
      "distinct_original_trapped_animal_tag_labels":len(trap_set),
      "distinct_original_global_animal_tag_labels":len(global_set),
      "distinct_original_proximity_endpoint_labels":len(logger_set),
      "distinct_original_trap_network_endpoint_labels":len(network_set)
    }
    STAGE="COLLAR_DATE_EFFORT_FEASIBILITY"
    # Date availability is metadata. Do NOT assert a logger was functioning
    # solely between collar-on and off or count observed dyad positives.
    date_fields={
      "collar_date_on":[r["date_on"] for r in collars],
      "collar_date_off":[r["date_off"] for r in collars],
      "logger_contact_date":[r["date"] for r in logger],
      "logger_full_timestamp":[r["datetime"] for r in logger],
      "trapping_date":[r["date"] for r in traps],
      "trapping_network_start":[r["TimeStart"] for r in network],
      "trapping_network_stop":[r["TimeStop"] for r in network],
      "logger_campaign_date":[r["date"] for r in summaries],
    }
    date_support={k:{
        "rows":len(values),
        "nonempty":sum(bool(str(v or "").strip()) for v in values),
        "parseable_calendar_dates":sum(time_date(v) is not None for v in values)
    }for k,values in date_fields.items()}
    report={
      "schema":"neon.prairie_vole_original_trap_vs_proximity_source_id_join.v1",
      "status":"SOURCE_PRAIRIE_VOLE_PUBLIC_EVENT_IDS_AND_DATES_AUDITED_NOT_CONTACT_EFFECT",
      "source":{
        "paper_doi":"10.1093/jmammal/gyaf032",
        "figshare_project":228462,
        "all_six_original_public_files_md5_and_size_verified":True,
        "original_published_md5_by_name":dict(sorted(FROZEN_ORIGINAL_MD5.items())),
        "public_source_universe":universe,
        "original_exact_identifier_memberships":counts,
        "source_date_format_support":date_support
      },
      "interpretation":{
        "logger_raw_identifier_namespace_has_NOT_been_relabelled":True,
        "collar_to_PIT_mapping_actual_eventwise_join_not_yet_performed":True,
        "logger_operable_zero_exposure_not_inferred_from_deployment":True,
        "true_zero_contact_from_nonlogged_dyads_not_authorized":True,
        "observed_network_concordance_2025_prior_authors_result_unchanged":True,
        "no_new_contact_behavior_or_niche_effect_computed":True,
        "no_animal_ID_or_raw_timestamp_exported":True,
        "neon_portal_finland_structural_original_effects_untouched":True,
        "mammal_single_manuscript_submission_HOLD":True
      },
      "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }
    return report
def main():
    global STAGE
    try:
        result=run()
        exit_code=0
    except Exception as e:
        result={
           "schema":"neon.prairie_vole_original_trap_vs_proximity_source_id_join.v1",
           "status":"STOP_ORIGINAL_FIGSHARE_ID_OR_DATE_SOURCE",
           "stopped_phase":STAGE if STAGE in PHASES else "UNKNOWN",
           "error_class":type(e).__name__,
           "no_animal_source_ID_or_effect_exported":True,
           "no_old_mammal_ecology_claim_updated":True
        }
        exit_code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    return exit_code
if __name__=="__main__":
    raise SystemExit(main())
