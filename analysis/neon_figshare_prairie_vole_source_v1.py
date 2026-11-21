#!/usr/bin/env python3
"""Read-only Figshare project source feasibility for close vole encounters.

Only public metadata and original provider MD5/size declarations. Does NOT
read animal ID, contact, trap encounters, outcome arrays or effect values.
Follow-up sampling or ecological modeling is forbidden until schema frozen.
"""
from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from urllib.request import Request,urlopen
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_prairie_vole_independent_contact_figshare_source_20261115.json"
PROJECT_ID=228462
API="https://api.figshare.com/v2"
CONTACT_TERMS=("prox","contact","collar","logger","social")
TRAP_TERMS=("trap","capture","livetrapp","live_trap","station")
CANDIDATE_SUFFIXES=(".csv",".tsv",".txt",".parquet",".feather",".rds",".xlsx",".zip")
MAX_ITEMS=200
MAX_ARTICLES=35
PHASE="PUBLIC_FIGSHARE_PROJECT"

def api_json(path):
    if not path.startswith("/"):raise ValueError("Path only")
    req=Request(API+path,headers={
        "Accept":"application/json","User-Agent":"NEON-mammal-contact-source-preflight/1"
    })
    with urlopen(req,timeout=75) as r:
        data=r.read(4_000_001)
    if len(data)>4_000_000:raise ValueError("PUBLIC_METADATA_RESPONSE_TOO_BIG")
    return json.loads(data.decode("utf-8"))

def classify(filenames):
    """Only a candidate; never treat metadata names as verified raw biology."""
    names=sorted({str(x).strip() for x in filenames if str(x).strip()})
    lower=[name.lower() for name in names]
    tabular=[name for name in names if name.lower().endswith(CANDIDATE_SUFFIXES)]
    contact=[name for name in tabular if any(t in name.lower() for t in CONTACT_TERMS)]
    trap=[name for name in tabular if any(t in name.lower() for t in TRAP_TERMS)]
    return {"any_tabular_source":bool(tabular),
            "tabular_source_filenames":tabular,
            "candidate_contact_filenames":contact,
            "candidate_trap_filenames":trap,
            "metadata_names_only_not_verified_schema":True}

def check():
    global PHASE
    meta=api_json("/projects/"+str(PROJECT_ID))
    if not isinstance(meta,dict) or meta.get("id")!=PROJECT_ID:
        raise ValueError("PUBLIC_PROJECT_ID_OR_SCHEMA_WRONG")
    PHASE="PUBLIC_FIGSHARE_PROJECT_ARTICLES"
    listings=[]
    for page in range(1,1+MAX_ITEMS//100):
        x=api_json("/projects/"+str(PROJECT_ID)+"/articles?page="+str(page)+"&page_size=100")
        if not isinstance(x,list):
            raise ValueError("PUBLIC_PROJECT_ARTICLES_NOT_LIST")
        listings.extend(x)
        if len(x)<100:break
    if not listings or len(listings)>MAX_ARTICLES:
        raise ValueError("NO_OR_TOO_MANY_PUBLIC_SOURCE_ARTICLES")
    ids=[]
    for x in listings:
        if not isinstance(x,dict) or not isinstance(x.get("id"),int):
            raise ValueError("PROJECT_LIST_ARTICLE_ID_INVALID")
        ids.append(x["id"])
    if len(ids)!=len(set(ids)):
        raise ValueError("DUPLICATE_PUBLIC_ARTICLE_ID")
    PHASE="PUBLIC_ARTICLE_DECLARED_FILES"
    articles=[];filenames=[]
    for article_id in sorted(ids):
        detail=api_json("/articles/"+str(article_id))
        if not isinstance(detail,dict) or detail.get("id")!=article_id:
            raise ValueError("PUBLIC_ARTICLE_DETAIL_MISMATCH")
        source_files=detail.get("files")
        if not isinstance(source_files,list):
            raise ValueError("PUBLIC_ARTICLE_FILE_LIST_MISSING")
        files=[]
        for f in source_files:
            if (not isinstance(f,dict) or not isinstance(f.get("id"),int)
                or not isinstance(f.get("name"),str)
                or not isinstance(f.get("size"),int)
                or f["size"]<0):
                raise ValueError("INVALID_PUBLIC_FILE_METADATA")
            files.append({"id":f["id"],"name":f["name"],
                          "size_bytes":f["size"],
                          "provider_declared_MD5":f.get("computed_md5"),
                          "provider_declared_download_url":f.get("download_url")})
            filenames.append(f["name"])
        articles.append({
            "article_id":article_id,
            "title":detail.get("title"),
            "public_version":detail.get("version"),
            "published_date":detail.get("published_date"),
            "doi":detail.get("doi"),
            "files":files
        })
    names=classify(filenames)
    status=("CANDIDATE_PUBLISHED_BOTH_SENSOR_SOURCE_METADATA_ONLY"
           if names["candidate_contact_filenames"]
           and names["candidate_trap_filenames"]
           else "HOLD_PUBLISHED_CONTACT_TRAP_SOURCE_NOT_ESTABLISHED_FROM_FILES")
    digest=sha256(json.dumps(articles,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return {
        "schema":"neon.external_mammal_direct_contact_versus_capture_figshare_metadata.v1",
        "status":status,
        "original_study":"Davidson et al. 2025, Journal of Mammalogy, 10.1093/jmammal/gyaf032",
        "project_url":"https://figshare.com/projects/Journal_of_Mammalogy_-_Methods_for_measuring_fine-scale_social_proximity_in_small_mammals/228462",
        "project_id":PROJECT_ID,
        "project_title":meta.get("title"),
        "provider_article_list_MD5_or_SHA_not_invented":True,
        "provider_metadata_json_SHA256":digest,
        "public_article_count":len(articles),
        "public_files_count":sum(len(x["files"]) for x in articles),
        "article_and_file_manifest":articles,
        "public_metadata_filename_screen":names,
        "biology_reported_by_original_authors_not_refit":{
            "same_vole_paired_network_individuals":24,
            "published_MRQAP_R2":0.02,
            "published_QAP_matrix_correlation":0.148,
            "proximity_logger_spatial_threshold_cm_approx":[5,6],
            "original_enclosure_count":1,
            "original_biological_result_not_new":True
        },
        "pre_specified_next_source_gate":{
            "must_download_provider_MD5_verifiable_original_raw_files":True,
            "need_animal_or_collar_ID_timestamp_proximity_records":True,
            "need_exact_original_capture_sample_by_individual_and_trap_station":True,
            "need_simultaneous_recording_windows_and_logger_active_effort":True,
            "need_published_PIT_to_collar_crosswalk_and_recovery":True,
            "do_not_infer_absent_contact_from_missing_device":True,
            "one_enclosure_not_geographic_replication":True
        },
        "ecological_claim_boundary":{
            "this_probe_only_public_metadata":True,
            "no_actual_animal_ids_coordinates_contact_or_capture_rows_opened":True,
            "no_new_contact_or_trap_species_effect_estimated":True,
            "source_file_names_do_not_establish_biological_schema":True,
            "published_MRQAP_does_not_validate_Finland_dyad_contacts":True,
            "NEON_Portal_Finland_Structural_original_effects_not_reopened":True,
            "neon_manuscript_remains_DRAFT_SUBMISSION_HOLD":True
        },
        "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }

def main():
    try:
        result=check()
        code=0
    except Exception as exc:
        result={
            "schema":"neon.external_mammal_direct_contact_versus_capture_figshare_metadata.v1",
            "status":"STOP_PUBLIC_FIGSHARE_METADATA_ACCESS_OR_IDENTITY",
            "stage":PHASE,
            "error_class":type(exc).__name__,
            "no_animal_contact_or_capture_values_read":True,
            "original_NEON_vole_Portal_Structural_unchanged":True
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return code

if __name__=="__main__":raise SystemExit(main())
