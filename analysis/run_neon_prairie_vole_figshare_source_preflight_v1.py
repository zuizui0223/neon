#!/usr/bin/env python3
"""Independent direct-contact observation public-source eligibility only.

Read Figshare public project metadata / public article file manifest. Do not
download animal-level response content or infer dyad matching from paper
summary. Source-only audit before frozen downstream effect protocol.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json
import re

PROJECT=228462
BASE="https://api.figshare.com/v2"
MAX_PAGE=10
MAX_ITEMS=300
MAX_RESPONSE_BYTES=2_000_000
OUT=Path(__file__).resolve().parents[1]/"build/neon_prairie_vole_logger_figshare_metadata_20261115.json"
STATE="API_PROJECT_METADATA"
STAGES=("API_PROJECT_METADATA","API_PROJECT_ARTICLE_IDS","ARTICLE_FILE_MANIFESTS","EVALUATE_SCHEMA_SOURCE")
def _get(url):
    req=Request(url,headers={
       "Accept":"application/json",
       "User-Agent":"NEON-mammal-independent-contact-public-source/1.0"
    })
    with urlopen(req,timeout=65) as response:
        if response.status!=200:raise ValueError("PUBLIC_API_NON_200")
        body=response.read(MAX_RESPONSE_BYTES+1)
        if len(body)>MAX_RESPONSE_BYTES:raise ValueError("PUBLIC_RESPONSE_TOO_LARGE")
    return json.loads(body.decode("utf-8"))
def _safe(value,length=95):
    """Do not export personal metadata, animal tags, file download URLs."""
    return re.sub(r"[^a-zA-Z0-9_.,()\- ]","_",str(value))[:length]

def run():
    global STATE
    proj=_get(f"{BASE}/projects/{PROJECT}")
    if not isinstance(proj,dict) or int(proj.get("id") or 0)!=PROJECT:
        raise ValueError("FIGSHARE_PROJECT_ID_MISMATCH")
    STATE="API_PROJECT_ARTICLE_IDS"
    lite=[];seen=set()
    for page in range(1,MAX_PAGE+1):
        this=_get(f"{BASE}/projects/{PROJECT}/articles?page={page}&page_size=100")
        if not isinstance(this,list):raise ValueError("PUBLIC_ARTICLE_LIST_INVALID")
        if not this:break
        for a in this:
            if not isinstance(a,dict) or not isinstance(a.get("id"),int):
                raise ValueError("FIGSHARE_ARTICLE_METADATA_INVALID")
            if a["id"] in seen:raise ValueError("DUPLICATE_FIGSHARE_ARTICLE")
            seen.add(a["id"]);lite.append(a)
        if len(lite)>MAX_ITEMS:raise ValueError("PUBLIC_PROJECT_TOO_MANY_ARTICLES")
        if len(this)<100:break
    if not lite:raise ValueError("FIGSHARE_PROJECT_HAS_NO_PUBLIC_ARTICLES")
    STATE="ARTICLE_FILE_MANIFESTS"
    detail=[]
    for a in lite:
        x=_get(f"{BASE}/articles/{a['id']}")
        if x.get("id")!=a["id"] or not isinstance(x.get("files"),list):
            raise ValueError("PUBLIC_ARTICLE_SOURCE_FILES_INVALID")
        files=x["files"]
        detail.append({
            "public_article_id":a["id"],
            "public_article_title":_safe(x.get("title") or a.get("title")),
            "public_article_doi":_safe(x.get("doi") or ""),
            "published_date":_safe(x.get("published_date") or ""),
            "published_files":[{
                "name":_safe(f.get("name") or ""),
                "size":f.get("size"),
                "file_id":f.get("id"),
                "md5_present":bool(f.get("supplied_md5") or f.get("computed_md5")),
                "is_link_only":bool(f.get("is_link_only",False)),
            }for f in files],
        })
    STATE="EVALUATE_SCHEMA_SOURCE"
    allfiles=[f for a in detail for f in a["published_files"]]
    name_counts=Counter()
    for f in allfiles:
        x=f["name"].lower()
        for label,terms in {
            "trap_related":("trap","capture","live","location","social_network"),
            "proximity_related":("prox","logger","contact","collar","signal","rssi"),
            "id_deployment_related":("tag","animal","pit","deployment","metadata","map","collar_ids","global_ids","_ids"),
            "code_related":(".r",".rmd",".py",".ipynb"),
        }.items():
            if any(term in x for term in terms):name_counts[label]+=1
    source_gate=(name_counts["trap_related"]>0 and
                 name_counts["proximity_related"]>0 and
                 name_counts["id_deployment_related"]>0)
    return {
        "schema":"neon.prairie_vole_independent_logger_public_source_preflight.v1",
        "status":"PUBLIC_FIGSHARE_POTENTIAL_DYAD_SOURCE_FILES_FOUND_NOT_YET_ID_JOINED"
                 if source_gate else
                 "STOP_FIGSHARE_NO_FILENAME_LEVEL_BOTH_DETECTOR_EVIDENCE",
        "source":{
            "paper_doi":"10.1093/jmammal/gyaf032",
            "published_project_url":"https://figshare.com/projects/Journal_of_Mammalogy_-_Methods_for_measuring_fine-scale_social_proximity_in_small_mammals/228462",
            "public_figshare_project_id":PROJECT,
            "number_public_articles":len(detail),
            "number_files":len(allfiles),
            "file_name_semantics_counts":dict(sorted(name_counts.items())),
            "public_articles_and_files":detail,
        },
        "evidence_gate":{
            "filename_preflight_potential_both_observation_sources":source_gate,
            "original_raw_proximity_and_capture_bytes_downloaded":False,
            "original_individual_animal_PIT_or_collared_IDs_exposed":False,
            "true_dyad_match_confirmed":False,
            "paired_exposure_effort_confirmed":False,
            "actual_neon_trap_catchability_calibrated":False,
            "this_is_not_new_biological_effect_or_habitat_use":True,
        },
        "original_niche_research_results_preserved":{
            "NEON_genus_capture_position_Z":True,
            "Portal_436_exact_stake_source_reference_non_support":True,
            "Finland_102_dyad_capture_centroid_exploratory":True,
            "Structural_island_graph_heldout_unchanged":True,
        },
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
    }
def main():
    global STATE
    try:
        output=run()
        exit_code=0
    except Exception as e:
        output={
            "schema":"neon.prairie_vole_independent_logger_public_source_preflight.v1",
            "status":"STOP_FIGSHARE_PUBLIC_SOURCE_ACCESS_OR_SCHEMA",
            "phase":STATE if STATE in STAGES else "UNKNOWN",
            "error_class":type(e).__name__,
            "no_raw_animal_dyads_or_contact_data_opened":True,
            "no_old_mammal_ecology_results_opened":True,
        }
        exit_code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps(output,indent=2,sort_keys=True))
    return exit_code
if __name__=="__main__":
    raise SystemExit(main())
