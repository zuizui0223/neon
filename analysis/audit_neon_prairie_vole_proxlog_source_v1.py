#!/usr/bin/env python3
"""Source-only inventory of published prairie-vole paired ProxLog/trap data.

The 2025 paper estimates MRQAP R²~0.02 on n=24 in ONE enclosure.
Inventory ONLY publisher-declared file names, sizes and checksums.
No per-vole PIT ID, collar ID, encounter, sensor event, 0/1 network edge,
capture location or observed response is downloaded or opened here.
"""
from __future__ import annotations
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
import hashlib,json,os

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_prairie_vole_proxlog_figshare_metadata_20261115.json"
PROJECT_ID=228462
PROJECT_URL="https://api.figshare.com/v2/projects/228462"
ARTICLES_URL="https://api.figshare.com/v2/projects/228462/articles"
PAPER_DOI="10.1093/jmammal/gyaf032"
MAX_METADATA_BYTES=2_000_000
STAGE="CHECK_FIGSHARE_PROJECT_ID"

def public_json(url):
    request=Request(url,headers={
        "Accept":"application/json",
        "User-Agent":"NEON-independent-mammal-evidence-source-inventory/1.0"
    })
    with urlopen(request,timeout=90) as response:
        payload=response.read(MAX_METADATA_BYTES+1)
    if len(payload)>MAX_METADATA_BYTES:
        raise ValueError("Public publisher metadata oversize")
    return json.loads(payload)

def canonical_hash(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,
        separators=(",",":")).encode("utf-8")).hexdigest()

def inventory():
    global STAGE
    project=public_json(PROJECT_URL)
    if not isinstance(project,dict) or project.get("id")!=PROJECT_ID:
        raise ValueError("The publisher's project identity does not match original paper")
    STAGE="PUBLIC_FIGSHARE_ARTICLE_LIST"
    entries=public_json(ARTICLES_URL+"?page=1&page_size=100")
    if isinstance(entries,dict):
        entries=entries.get("data",entries.get("articles"))
    if not isinstance(entries,list):
        raise ValueError("Original project articles list is not a JSON array")
    if len(entries)>=100:
        raise ValueError("Unverified Figshare article pagination: stop before assuming complete")
    STAGE="PUBLISHER_DECLARED_FILE_METADATA_ONLY"
    rows=[];articles=[]
    for entry in entries:
        article_id=entry.get("id")
        if not isinstance(article_id,int):
            raise ValueError("Article ID missing from published project listing")
        article=public_json("https://api.figshare.com/v2/articles/"+str(article_id))
        if not isinstance(article,dict) or article.get("id")!=article_id:
            raise ValueError("Figshare article identity mismatch")
        attached=article.get("files",[])
        if not isinstance(attached,list):
            raise ValueError("Figshare article files metadata not a list")
        articles.append({"id":article_id,
                         "title":str(article.get("title",""))[:200],
                         "published_date":article.get("published_date"),
                         "version":article.get("version"),
                         "declared_files":len(attached)})
        for f in attached:
            if not isinstance(f,dict):
                raise ValueError("Invalid Figshare file metadata")
            # Source-only file summaries are not a licence to download raw dyad labels.
            name=str(f.get("name",""))[:255]
            size=f.get("size")
            fid=f.get("id")
            if not name or not isinstance(size,int) or size<0 or not isinstance(fid,int):
                raise ValueError("File identity or provider original length missing")
            rows.append({"article_id":article_id,"file_id":fid,
                         "name":name,"bytes":size,
                         "supplier_md5":f.get("supplied_md5",f.get("computed_md5")),
                         "is_link_only":f.get("is_link_only",False)})
    names=[x["name"].lower() for x in rows]
    keywords={
        "capture_or_trap_filename_count":sum(any(w in n for w in ("trap","capture","pit")) for n in names),
        "logger_or_proximity_filename_count":sum(any(w in n for w in ("prox","logger","contact","ble","rssi")) for n in names),
        "network_or_edge_filename_count":sum(any(w in n for w in ("edge","network","matrix","adjac","assoc")) for n in names),
        "device_effort_or_deployment_filename_count":sum(any(w in n for w in ("deployment","collar","effort","battery","device")) for n in names),
    }
    return {
        "schema":"neon.prairie_vole_proxlog_trapping_independent_source_inventory.v1",
        "status":"PUBLISHED_FIGSHARE_FILE_METADATA_VERIFIED_NO_BIOLOGICAL_RECORDS_READ",
        "source_reference":{
            "paper_DOI":PAPER_DOI,
            "paper_year":2025,
            "public_project_ID":PROJECT_ID,
            "public_figshare_project_url":"https://figshare.com/projects/Journal_of_Mammalogy_-_Methods_for_measuring_fine-scale_social_proximity_in_small_mammals/228462",
            "official_project_metadata_sha256":canonical_hash(project),
            "official_articles_summary_sha256":canonical_hash(articles),
            "source_metadata_only_not_raw_event_or_response":True,
            "paper_one_seminatural_0_1ha_enclosure":True,
            "paper_24_nodes_both_detection_networks":True,
            "paper_MRQAP_R_squared_0_02_ALREADY_PUBLISHED":True,
        },
        "file_support":{
            "published_articles":len(articles),
            "declared_file_count":len(rows),
            "total_declared_bytes":sum(x["bytes"] for x in rows),
            "filename_category_counts":keywords,
            "articles":articles,
            "original_file_id_name_size_and_md5":rows,
            "no_individual_collar_crosswalk_inferred_from_filenames":True,
            "single_enclosure_not_a_multisite_ecological_replication":True,
        },
        "source_identification_next_step":"A separate source-only schema/header gate must inspect original file headers (no rows) and approve exactly matched trapping dyad IDs, independent logger dyad IDs, time/exposure and collar-to-animal mapping before scoring.",
        "ecological_claims_not_authorized":{
            "logger_independent_of_mammal_trapping_detection":False,
            "multisite_mammal_space_use_replication":False,
            "contact_transmission_or_social_bond_confirmed":False,
            "same_bank_vole_dyad_observation_source":False,
            "no_original_NEON_Portal_Finland_or_Structural_animal_responses_opened":True,
            "no_external_proxlog_network_effect_opened":True,
        },
        "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }

def main():
    global STAGE
    try:
        result=inventory()
        code=0
    except Exception as exc:
        result={
            "schema":"neon.prairie_vole_proxlog_trapping_independent_source_inventory.v1",
            "status":"STOP_EXTERNAL_FIGSHARE_SOURCE_ACCESS_OR_METADATA",
            "failed_stage":STAGE,
            "error_class":type(exc).__name__,
            "no_sensor_contact_or_animal_ID_row_read":True,
            "no_NEON_Portal_Finland_or_Structural_result_recalculated":True,
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return code

if __name__=="__main__":
    raise SystemExit(main())
