#!/usr/bin/env python3
"""Public original R analysis code source-only ontology check (NEVER execute R).

Reads checksum-pinned 2023 Figshare 'Main Analysis Script.R' by original
publisher file ID. Prints only bounded relevant code lines to diagnose
which original source columns represent cover vs forestry management.
No original seed choice, animal tag, foraging data or coefficient is read.
"""
from __future__ import annotations
from datetime import datetime,timezone
from hashlib import md5,sha256
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlsplit
from urllib.error import HTTPError,URLError
import json,re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_figshare_2023_original_R_risk_code_ontology_20261121.json"
ARTICLE_ID=21512436
VERSION=1
FID=38217888
FNAME="Main Analysis Script.R"
EXPECTED_SIZE=54662
EXPECTED_MD5="b209339b7d0f1f2a7be3b00ebd6fbf4d"
API=f"https://api.figshare.com/v2/articles/{ARTICLE_ID}"

def require(ok,label):
    if not ok:
        raise ValueError("ORIGINAL_R_COVER_CODE_STOP_"+label)

def original_script():
    with urlopen(Request(API,headers={"Accept":"application/json",
                "User-Agent":"NEON-foraging-ontology/1"}),timeout=40) as h:
        metadata=json.loads(h.read(1_000_001))
    require(metadata["id"]==ARTICLE_ID and metadata["version"]==VERSION,
            "ORIGINAL_FIGSHARE_ARTICLE_ID_VERSION")
    files=metadata.get("files")
    require(isinstance(files,list) and len(files)==5,
            "SOURCE_FILE_COUNT_CHANGE")
    f=next((z for z in files if z.get("id")==FID),None)
    require(f is not None and f["name"]==FNAME and f["size"]==EXPECTED_SIZE
            and (f.get("computed_md5") or f.get("supplied_md5"))==EXPECTED_MD5,
            "ORIGINAL_SCRIPT_META_SIZE_MD5_CHANGE")
    url=f["download_url"]
    u=urlsplit(url)
    require(u.scheme=="https" and
            u.hostname in ("ndownloader.figshare.com","figshare.com")
            and u.path.rstrip("/").endswith(f"/files/{FID}"),
            "ORIGINAL_SCRIPT_URL_NOT_AUTHORIZED_PROVIDER")
    with urlopen(Request(url,headers={"Accept":"text/plain",
                "User-Agent":"NEON-foraging-ontology/1"}),timeout=40) as h:
        raw=h.read(EXPECTED_SIZE+1)
    require(len(raw)==EXPECTED_SIZE and md5(raw).hexdigest()==EXPECTED_MD5,
            "ORIGINAL_SCRIPT_RAW_MD5_OR_SIZE")
    try:
        return raw.decode("utf-8-sig"),sha256(raw).hexdigest()
    except UnicodeDecodeError:
        raise ValueError("ORIGINAL_R_COVER_CODE_STOP_UTF8") from None

def audit_text(text,original_sha):
    """Only STATIC author code lines involving methodological ontology."""
    found=[]
    names=("SITE_ID","TREAT","PRED_PRES")
    for lineno,line in enumerate(text.splitlines(),1):
        if not any(re.search(r"\b"+re.escape(name)+r"\b",line) for name in names):
            continue
        # Text is author-supplied CODE, no original DATA row. Avoid exporting
        # all analysis code: only 20 source code lines at most, <=180 chars each.
        found.append({"original_R_line":lineno,
                      "source_code_excerpt":line.strip()[:180]})
    return {
        "schema":"neon.figshare2023_original_script_risk_ontology.v1",
        "status":"ORIGINAL_PUBLISHED_R_SOURCE_ONTOLOGY_INSPECTION_ONLY",
        "article_id":ARTICLE_ID,"article_version":VERSION,
        "original_script_file_id":FID,"original_script_md5_verified":EXPECTED_MD5,
        "original_script_sha256":original_sha,
        "number_of_original_R_lines_with_structural_source_variables":len(found),
        "up_to_twenty_original_method_code_lines":found[:20],
        "risk_or_silviculture_labels_not_reclassified_by_this_source_audit":True,
        "no_original_Figshare_CSV_biological_rows_read":True,
        "original_R_script_not_executed":True,
        "no_learning_resource_competition_or_PRED_PRES_effect_fitted":True,
        "one_NEON_ecology_paper_Draft_SUBMISSION_HOLD":True,
        "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }

def main():
    try:
        s,h=original_script()
        out=audit_text(s,h);code=0
    except Exception as e:
        out={"schema":"neon.figshare2023_original_script_risk_ontology.v1",
             "status":"ORIGINAL_SCRIPT_SOURCE_STOP",
             "error_type":type(e).__name__,"reason":str(e)[:160],
             "no_original_behaviour_or_mammal_effect_accessed":True}
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print(json.dumps(out,sort_keys=True,indent=2))
    return code

if __name__=="__main__":
    raise SystemExit(main())
