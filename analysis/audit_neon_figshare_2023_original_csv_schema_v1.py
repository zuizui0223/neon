#!/usr/bin/env python3
"""Verify 2023 Figshare original CSV source bytes and headers, no biology."""
from __future__ import annotations
from collections import Counter
from datetime import datetime,timezone
from hashlib import md5,sha256
from io import StringIO
from pathlib import Path
from urllib.parse import urlsplit
from urllib.error import HTTPError,URLError
from urllib.request import Request,urlopen
import csv,json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_figshare_2023_original_csv_schema_v1.json"
ARTICLE_ID=21512436
ARTICLE_VERSION=1
API=f"https://api.figshare.com/v2/articles/{ARTICLE_ID}"
FILES={
 38217891:("2018 Vole Seed Data.csv",66667,"5c58051b71eaa55cd888c87b6494a00c"),
 38217897:("Vole BLUPS.csv",108786,"ddfb7c7a7e6472dd064bc3e4edda7d81"),
 38217900:("Vole Personality Data.csv",343858,"f0d2310389cc1c02cbeabf352b0b131c")
}
PROTOCOL="docs/NEON_FIGSHARE_2023_ORIGINAL_CSV_SCHEMA_GATE_20261121.md"

def require(ok,why):
    if not ok:
        raise ValueError("NEON_FIGSHARE_2023_ORIGINAL_STOP_"+why)

def exact_file_href(url,fid):
    if not isinstance(url,str) or not url or len(url)>1024:
        return False
    v=urlsplit(url)
    return (v.scheme=="https" and v.hostname in
            ("ndownloader.figshare.com","figshare.com")
            and v.username is None and v.password is None
            and v.path.rstrip("/").endswith(f"/files/{fid}")
            and not v.fragment)

def bounded_original(url,size):
    req=Request(url,headers={
        "User-Agent":"NEON-public-Figshare-original-source/1",
        "Accept":"text/csv, application/octet-stream"
    })
    try:
        with urlopen(req,timeout=40) as response:
            require(getattr(response,"status",200)==200,
                    "PUBLIC_FILE_HTTP_STATUS")
            raw=response.read(size+1)
    except HTTPError as err:
        raise ValueError("NEON_FIGSHARE_2023_ORIGINAL_STOP_HTTP_"+str(err.code)) from err
    except (URLError,TimeoutError) as err:
        raise ValueError("NEON_FIGSHARE_2023_ORIGINAL_STOP_NETWORK_ACCESS") from err
    require(len(raw)==size,"WRONG_ORIGINAL_PUBLISHED_BYTE_SIZE")
    lower=raw[:4096].lstrip().lower()
    require(not lower.startswith((b"<html",b"<!doctype",b"{",b"pk\x03\x04")),
            "HTML_JSON_ZIP_NOT_ORIGINAL_CSV")
    require(b"\x00" not in raw[:4096],"ORIGINAL_BINARY_OR_NUL_FILE")
    return raw

def original_header_and_row_count(raw, original_filename=None):
    """Only CSV column names and number of original records, no response data."""
    try:
        original=raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("NEON_FIGSHARE_2023_ORIGINAL_STOP_UTF8") from None
    reader=csv.reader(StringIO(original,newline=""))
    try:
        headings=next(reader)
    except StopIteration:
        raise ValueError("NEON_FIGSHARE_2023_ORIGINAL_STOP_EMPTY_CSV") from None
    require(2<=len(headings)<=200,"SOURCE_FIELD_COUNT_BAD")
    # Exact pinned source HEADER diagnosis from original MD5-verified files:
    # 'Vole BLUPS.csv' has exactly one empty first header; its scientific
    # meaning was NOT established. Preserve it in raw schema, but exclude it
    # from scientific column names; never assign it an invented variable.
    empty=[i for i,k in enumerate(headings) if not k.strip()]
    require(not empty or (original_filename=="Vole BLUPS.csv" and empty==[0]),
            "SOURCE_EMPTY_HEADER_LABEL")
    usable=headings[1:] if empty else headings
    require(all(usable) and len(set(usable))==len(usable),
            "SOURCE_DUPLICATE_HEADER")
    n=0
    for row in reader:
        require(len(row)==len(headings),"ORIGINAL_RAGGED_CSV")
        n+=1
    require(n>=1,"SOURCE_NO_RECORDS")
    return {"original_column_names":headings,
            "scientific_column_names_excluding_any_source_unlabeled_first":usable,
            "source_unlabeled_header_positions":empty,
            "source_empty_first_column_excluded_from_scientific_join":bool(empty),
            "column_count":len(headings),
            "original_row_count":n}

def audit_metadata(meta):
    require(isinstance(meta,dict),"ARTICLE_META_TYPE")
    require(meta.get("id")==ARTICLE_ID,"ARTICLE_ID_CHANGED")
    require(meta.get("version")==ARTICLE_VERSION,"ARTICLE_VERSION_CHANGED")
    require("Predation risk and personality" in meta.get("title",""),
            "ARTICLE_TITLE_MISMATCH")
    inventory=meta.get("files")
    require(isinstance(inventory,list) and len(inventory)==5,
            "PROVIDER_FILE_COUNT_CHANGED")
    lookup={x.get("id"):x for x in inventory if isinstance(x,dict)}
    require(len(lookup)==5,"PROVIDER_DUPLICATE_FILE_ID")
    selected={}
    for fid,(name,size,digest) in FILES.items():
        x=lookup.get(fid)
        require(isinstance(x,dict),"PINNED_PROVIDER_FILE_ID_MISSING")
        require(x.get("name")==name and x.get("size")==size,
                "PINNED_SOURCE_NAME_OR_SIZE_DRIFT")
        published=x.get("computed_md5") or x.get("supplied_md5") or x.get("md5")
        require(published==digest,"PINNED_PROVIDER_MD5_DRIFT")
        href=x.get("download_url")
        require(exact_file_href(href,fid),"PINNED_PROVIDER_DOWNLOAD_HREF_WRONG")
        selected[fid]=href
    return selected

def inventory_source():
    req=Request(API,headers={"Accept":"application/json",
                              "User-Agent":"NEON-original-article-locked-source/1"})
    try:
        with urlopen(req,timeout=30) as response:
            require(getattr(response,"status",200)==200,"ARTICLE_API_STATUS")
            buf=response.read(1_000_001)
    except HTTPError as err:
        raise ValueError("NEON_FIGSHARE_2023_ORIGINAL_STOP_ARTICLE_HTTP_"+str(err.code)) from err
    except (URLError,TimeoutError) as err:
        raise ValueError("NEON_FIGSHARE_2023_ORIGINAL_STOP_ARTICLE_NETWORK") from err
    require(0<len(buf)<=1_000_000 and buf.lstrip().startswith(b"{"),
            "ARTICLE_METADATA_NOT_JSON")
    try:
        meta=json.loads(buf)
    except ValueError:
        raise ValueError("NEON_FIGSHARE_2023_ORIGINAL_STOP_META_JSON") from None
    return audit_metadata(meta),sha256(buf).hexdigest()

def source_report():
    links,meta_digest=inventory_source()
    details={}
    for fid,(name,size,digest) in FILES.items():
        raw=bounded_original(links[fid],size)
        require(md5(raw).hexdigest()==digest,"PINNED_ORIGINAL_FILE_MD5_MISMATCH")
        fields=original_header_and_row_count(raw,name)
        details[name]={
            "provider_file_id":fid,"original_bytes":size,
            "provider_original_MD5_verified":digest,
            "original_file_SHA256":sha256(raw).hexdigest(),
            **fields,"no_original_biological_values_exported":True
        }
    return {
        "schema":"neon.figshare_2023_behavior_original_csv_source_only.v1",
        "status":"ORIGINAL_SOURCE_CSV_BYTES_AND_HEADERS_GO_NO_BIOLOGY",
        "original_article_id":ARTICLE_ID,
        "original_article_version":ARTICLE_VERSION,
        "original_article_metadata_sha256":meta_digest,
        "published_source_doi":"10.6084/m9.figshare.21512436.v1",
        "original_3_csv_byte_and_schema_receipts":details,
        "not_a_verified_animal_patch_seed_exposure_join":True,
        "no_seed_selection_personality_risk_or_learned_memory_effect_estimated":True,
        "secondary_2026_dataset_not_used":True,
        "previous_NEON_Portal_Finland_Structural_results_unchanged":True,
        "NEON_one_manuscript_DRAFT_SUBMISSION_HOLD":True,
        "protocol":PROTOCOL,
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
    }

def main():
    try:
        report=source_report()
        status=0
    except Exception as err:
        report={
            "schema":"neon.figshare_2023_behavior_original_csv_source_only.v1",
            "status":"SOURCE_STOP_ORIGINAL_BYTES_OR_SCHEMA_NO_ECOLOGICAL_RESULT",
            "error_type":type(err).__name__,
            "stop_reason":str(err)[:180],
            "any_risk_seed_or_vole_outcomes_unestimated":True,
            "no_source_or_effect_imputation":True
        }
        status=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps(report,sort_keys=True,indent=2))
    return status

if __name__=="__main__":
    raise SystemExit(main())
