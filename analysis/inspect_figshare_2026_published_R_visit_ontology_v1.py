#!/usr/bin/env python3
"""Checksum-verified original 2026 Figshare R source-code ontology audit.

Does NOT execute published R code, import any original seed/animal response
rows, extract estimates, or change the failed 80% visit-ID consistency gate.
Reports limited static source-code contexts to identify author Visit.ID and
Time.start semantics. Source R is original prior art.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime,timezone
from hashlib import md5,sha256
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlsplit
import json,re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_figshare_2026_original_R_visit_ID_ontology_20261122.json"
API="https://api.figshare.com/v2/articles/28207769"
FILE_ID=51823913
NAME="Main Analysis - Clean.R"
SIZE=68819
MD5="b5f99bfd6b800cdecb435dfb23f6e6b9"
TOPICS=("Visit.ID","Time.start","Time.end","Video","Unique_station_ind_ID","First.Visit","Time.searching")
MAX_BOUNDED_EXCERPTS=16

def require(ok,label):
    if not ok:raise ValueError("ORIGINAL_R_SEMANTICS_SOURCE_STOP_"+label)

def fetch_script():
    with urlopen(Request(API,headers={"Accept":"application/json",
        "User-Agent":"NEON-visit-code-source-audit/1"}),timeout=35) as resp:
        raw=resp.read(1_000_001)
    require(0<len(raw)<=1_000_000 and raw.lstrip().startswith(b"{"),
            "ORIGINAL_ARTICLE_META_MISSING")
    js=json.loads(raw)
    require(js.get("id")==28207769 and js.get("version")==2,
            "FIGSHARE_ARTICLE_VERSION_DRIFT")
    f=next((x for x in js.get("files",[]) if x.get("id")==FILE_ID),None)
    require(f is not None and f.get("name")==NAME and f.get("size")==SIZE and
            (f.get("computed_md5") or f.get("supplied_md5"))==MD5,
            "ORIGINAL_SCRIPT_METADATA_NAME_MD5_SIZE_DRIFT")
    url=f.get("download_url","")
    o=urlsplit(url)
    require(o.scheme=="https" and
            o.hostname in ("ndownloader.figshare.com","figshare.com") and
            o.path.rstrip("/").endswith(f"/files/{FILE_ID}"),
            "NOT_EXACT_FIGSHARE_PROVIDER_SCRIPT")
    with urlopen(Request(url,headers={"Accept":"text/plain",
            "User-Agent":"NEON-visit-code-source-audit/1"}),timeout=35) as resp:
        buf=resp.read(SIZE+1)
    require(len(buf)==SIZE and md5(buf).hexdigest()==MD5,
            "ORIGINAL_SCRIPT_RAW_BYTE_MD5_CHANGED")
    return buf.decode("utf-8-sig"),sha256(buf).hexdigest()

def inspect_source(original,script_sha):
    count=Counter()
    lines=original.splitlines()
    hits=[]
    for i,line in enumerate(lines,1):
        matched=[t for t in TOPICS if t in line]
        for t in matched:count[t]+=1
        if matched:
            # Only short bounded code contexts for ontology diagnostics.
            # No raw animal/seed rows. Full published R code never exported.
            excerpt=line.strip()
            if excerpt and not excerpt.startswith("#") and len(hits)<MAX_BOUNDED_EXCERPTS:
                hits.append({"source_line_number":i,
                             "source_variable_mentions":matched,
                             "bounded_original_method_code":excerpt[:100]})
    return {
        "schema":"neon.figshare2026_original_author_R_visit_identity_source.v1",
        "status":"PUBLISHED_ORIGINAL_R_VISIT_ONTOLOGY_SOURCE_ONLY",
        "original_figshare_article_id":28207769,
        "original_figshare_version":2,
        "original_R_script_publisher_file_ID":FILE_ID,
        "original_R_script_SHA256":script_sha,
        "original_R_script_byte_size_MD5_verified":SIZE,
        "original_R_script_line_count":len(lines),
        "original_method_topic_line_counts":dict(sorted(count.items())),
        "limited_source_method_snippets_for_inhouse_diagnosis":hits,
        "no_original_R_executed":True,
        "no_original_animal_observation_rows_read":True,
        "no_resource_learning_competition_or_visit_effect_estimated":True,
        "prior_2026_Figshare_visit_consistency_STOP_unchanged":True,
        "single_NEON_Draft_SUBMISSION_HOLD":True
    }

def main():
    try:
        s,sha=fetch_script()
        out=inspect_source(s,sha)
        code=0
    except Exception as e:
        out={"schema":"neon.figshare2026_original_author_R_visit_identity_source.v1",
             "status":"SOURCE_SCRIPT_ONTOLOGY_STOP",
             "error_type":type(e).__name__,
             "source_error_label":str(e)[:160],
             "original_visit_effect_unopened":True}
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,sort_keys=True,indent=2))
    return code

if __name__=="__main__":
    raise SystemExit(main())
