#!/usr/bin/env python3
"""Figshare 2026 mouse/vole/station-night original file source schema ONLY.

No original ecological values, PITs, exact sites, reward amount, seed finding,
foraging outcomes, forest-type effects, interspecific interaction or learning.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime,timezone
from hashlib import md5,sha256
from io import StringIO
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.request import Request,urlopen
import csv,json

from analysis.audit_neon_figshare_2023_original_csv_schema_v1 import (
    exact_file_href,bounded_original
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_figshare_2026_original_foraging_schema_v1.json"
ARTICLE=28207769
VERSION=2
SOURCE_FILES={
51682214:("2016-2023 Capture Data.csv",1224945,"d9b8cd69378a98c520b10172b80f2c23"),
51682217:("All Foraging Clean.csv",792575,"5f823a01c8751bd360dab723f3d49faa"),
51682220:("All Station Nights.csv",35432,"1cc4f0c66043c9a96955bed1c66408e3"),
51682229:("Mouse Foraging Data Clean.csv",278572,"63adc6b8f232e423fefc2d802d25904d"),
51682232:("Vole Foraging Data Clean.csv",313588,"e05cb082df82286672f49a39df4585b2")
}
PROTOCOL="docs/NEON_FIGSHARE_2026_MOUSE_VOLE_FORAGING_SCHEMA_GATE_20261121.md"

def require(ok,reason):
    if not ok:
        raise ValueError("NEON_FIGSHARE_2026_SOURCE_STOP_"+reason)

def validate_provider_info(data):
    require(isinstance(data,dict) and data.get("id")==ARTICLE,
            "ORIGINAL_FIGSHARE_ARTICLE_ID")
    require(data.get("version")==VERSION,"ORIGINAL_ARTICLE_VERSION")
    title=data.get("title") or ""
    require(isinstance(title,str) and
            "Intraspecific and environmental variation" in title,
            "ORIGINAL_ARTICLE_TITLE")
    files=data.get("files")
    require(isinstance(files,list) and len(files)==9,
            "ORIGINAL_ARTICLE_SOURCE_FILE_COUNT")
    records={f.get("id"):f for f in files if isinstance(f,dict)}
    require(len(records)==9,"ORIGINAL_ARTICLE_DUPLICATE_IDS")
    valid={}
    for ident,(name,size,digest) in SOURCE_FILES.items():
        f=records.get(ident)
        require(isinstance(f,dict),"FROZEN_ORIGINAL_FILE_ID_MISSING")
        require(f.get("name")==name and f.get("size")==size,
                "FROZEN_ORIGINAL_FILE_NAME_SIZE_CHANGED")
        check=f.get("computed_md5") or f.get("supplied_md5") or f.get("md5")
        require(check==digest,"FROZEN_ORIGINAL_MD5_CHANGED")
        url=f.get("download_url")
        require(exact_file_href(url,ident),"NOT_OFFICIAL_PROVIDER_EXACT_FILE_URL")
        valid[ident]=url
    return valid

def original_csv_structure(raw):
    try:
        s=raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("NEON_FIGSHARE_2026_SOURCE_STOP_ORIGINAL_UTF8") from None
    rd=csv.reader(StringIO(s,newline=""))
    try:h=next(rd)
    except StopIteration:
        raise ValueError("NEON_FIGSHARE_2026_SOURCE_STOP_EMPTY_ORIGINAL_CSV") from None
    require(2<=len(h)<=200,"ORIGINAL_HEADER_COUNT")
    nonempty=[v for v in h if v.strip()]
    require(len(nonempty)>=2,"ORIGINAL_NONEMPTY_LABELS_INSUFFICIENT")
    require(len(nonempty)==len(set(nonempty)),"ORIGINAL_DUPLICATED_NAMED_COLUMNS")
    missing=[i for i,x in enumerate(h) if not x.strip()]
    hist=Counter()
    for row in rd:
        hist[len(row)]+=1
    n=sum(hist.values())
    require(n>0,"ORIGINAL_CSV_ZERO_SOURCE_ROWS")
    require(set(hist)=={len(h)},"ORIGINAL_CSV_RAGGED_ROW_WIDTH")
    return {
        "original_source_column_names":h,
        "scientific_header_names_excluding_unlabeled":nonempty,
        "unlabeled_source_column_positions":missing,
        "original_header_count":len(h),
        "original_rows":n,
        "source_row_width_histogram":dict(sorted(hist.items())),
        "no_biological_values_or_individuals_exported":True,
    }

def original_public_csvs():
    request=Request(f"https://api.figshare.com/v2/articles/{ARTICLE}",
        headers={"Accept":"application/json",
                 "User-Agent":"NEON-original-figshare-2026-schema/1"})
    try:
        with urlopen(request,timeout=40) as fh:
            require(getattr(fh,"status",200)==200,"ARTICLE_HTTP")
            raw=fh.read(1_000_001)
    except HTTPError as e:
        raise ValueError("NEON_FIGSHARE_2026_SOURCE_STOP_HTTP_"+str(e.code)) from e
    except (URLError,TimeoutError) as e:
        raise ValueError("NEON_FIGSHARE_2026_SOURCE_STOP_NETWORK") from e
    require(0<len(raw)<=1_000_000 and raw.lstrip().startswith(b"{"),
            "ARTICLE_METADATA_NOT_JSON")
    meta=json.loads(raw)
    links=validate_provider_info(meta)
    detail={}
    for ident,(name,size,digest) in SOURCE_FILES.items():
        source=bounded_original(links[ident],size)
        require(md5(source).hexdigest()==digest,
                "ORIGINAL_FILE_MD5_SOURCE_BYTES_CHANGED")
        structure=original_csv_structure(source)
        detail[name]={
            "original_figshare_file_id":ident,
            "original_published_byte_size":size,
            "original_md5_verified":digest,
            "original_sha256":sha256(source).hexdigest(),
            **structure
        }
    return {
        "schema":"neon.figshare_2026_original_mouse_vole_foraging_schema.v1",
        "status":"ORIGINAL_2026_FIVE_FILE_SCHEMA_GO_NO_BIOLOGY",
        "original_figshare_article_id":ARTICLE,
        "original_figshare_article_version":VERSION,
        "original_article_metadata_SHA256":sha256(raw).hexdigest(),
        "source_files":detail,
        "same_Penobscot_study_forest_as_original_2023_vole_source":True,
        "overlapping_dates_PITs_grids_NOT_YET_VERIFIED":True,
        "no_direct_capture_vs_sensor_effort_join_yet":True,
        "combined_foraging_and_mouse_vole_tables_may_overlap":True,
        "no_seed_finding_patch_choice_personality_or_memory_effect_computed":True,
        "not_multiple_independent_geographic_replications":True,
        "one_NEON_manuscript_Draft_SUBMISSION_HOLD":True,
        "protocol":PROTOCOL,
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
    }

def main():
    try:
        result=original_public_csvs();code=0
    except Exception as err:
        result={
            "schema":"neon.figshare_2026_original_mouse_vole_foraging_schema.v1",
            "status":"SOURCE_STOP_ORIGINAL_VERSION_FILES_OR_CSV_GRAMMAR",
            "error_type":type(err).__name__,
            "stop_reason":str(err)[:140],
            "no_mammal_behavioral_effect_computed":True
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps(result,sort_keys=True,indent=2))
    return code

if __name__=="__main__":
    raise SystemExit(main())
