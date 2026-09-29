from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


USER_AGENT="powdermill-dataone-source-audit/1.0"
CN="https://cn.dataone.org/cn/v2"
PACKAGE_TOKEN="knb-lter-vcr"
PACKAGE_NUMBER="67"

EXPECTED_COLUMNS=[
    "animal_id","is_new","species_code","period","time","date","quadrat","sex",
    "sex_unknown","weight","sex_shrew","scrotal_male","inguinal_male",
    "pregnant","open_vulva","large_nipples",
]


def request(url: str, *, timeout: int=180) -> tuple[int,dict[str,str],bytes]:
    req=urllib.request.Request(
        url,
        headers={"User-Agent":USER_AGENT,"Accept":"*/*"},
    )
    try:
        with urllib.request.urlopen(req,timeout=timeout) as response:
            return (
                int(response.status),
                {k.lower():v for k,v in response.headers.items()},
                response.read(),
            )
    except urllib.error.HTTPError as error:
        return (
            int(error.code),
            {k.lower():v for k,v in error.headers.items()},
            error.read(),
        )


def solr_search() -> list[dict]:
    params=urllib.parse.urlencode({
        "q":f'identifier:*{PACKAGE_TOKEN}*',
        "wt":"json",
        "rows":"1000",
    })
    status,headers,raw=request(f"{CN}/query/solr/?{params}")
    if status!=200:
        raise RuntimeError(f"DataONE Solr query failed: HTTP {status}")
    payload=json.loads(raw.decode("utf-8"))
    docs=((payload.get("response") or {}).get("docs") or [])
    return [doc for doc in docs if isinstance(doc,dict)]


def package_version(identifier: str) -> int | None:
    patterns=(
        rf"/{re.escape(PACKAGE_TOKEN)}/{PACKAGE_NUMBER}/(\d+)(?:/|$)",
        rf"{re.escape(PACKAGE_TOKEN)}[./]{PACKAGE_NUMBER}[./](\d+)",
    )
    for pattern in patterns:
        match=re.search(pattern,str(identifier))
        if match:
            return int(match.group(1))
    return None


def relevant_docs(docs: list[dict]) -> tuple[int,list[dict]]:
    rows=[]
    versions=[]
    for doc in docs:
        identifier=str(doc.get("identifier",""))
        version=package_version(identifier)
        if version is None:
            continue
        versions.append(version)
        rows.append((version,doc))
    if not rows:
        raise RuntimeError("DataONE index returned no documents for package 67")
    latest=max(versions)
    selected=[doc for version,doc in rows if version==latest]
    return latest,selected


def resolver_url(pid: str) -> str:
    return f"{CN}/resolve/{urllib.parse.quote(pid,safe='')}"


def looks_like_data_format(doc: dict) -> bool:
    fmt=str(doc.get("formatId","")).lower()
    identifier=str(doc.get("identifier","")).lower()
    if "metadata" in identifier or "resource_map" in identifier:
        return False
    return (
        fmt.startswith("text/")
        or "csv" in fmt
        or "plain" in fmt
        or "/package/data/" in identifier
    )


def parse_record_block(raw: bytes) -> dict:
    text=raw.decode("utf-8-sig",errors="replace")
    lines=text.splitlines()

    best=None
    for start in range(min(80,len(lines))):
        reader=csv.reader(lines[start:],delimiter=",",quotechar='"')
        counts=[]
        rows=[]
        for i,row in enumerate(reader):
            if not row:
                continue
            counts.append(len(row))
            rows.append(row)
            if len(counts)>=50:
                break
        if len(counts)<5:
            continue
        exact=sum(c==len(EXPECTED_COLUMNS) for c in counts)
        score=exact/len(counts)
        if best is None or score>best["score"]:
            best={
                "start_line_zero_based":start,
                "score":score,
                "sample_field_counts":counts,
            }

    if best is None or best["score"]<0.9:
        return {
            "record_block_found":False,
            "documented_schema_match":False,
            "expected_field_count":len(EXPECTED_COLUMNS),
        }

    start=best["start_line_zero_based"]
    reader=csv.reader(lines[start:],delimiter=",",quotechar='"')
    row_count=0
    malformed=0
    first_rows_field_counts=[]
    for row in reader:
        if not row:
            continue
        if len(first_rows_field_counts)<20:
            first_rows_field_counts.append(len(row))
        if len(row)==len(EXPECTED_COLUMNS):
            row_count+=1
        else:
            malformed+=1

    return {
        "record_block_found":True,
        "record_start_line_one_based":start+1,
        "record_field_count":len(EXPECTED_COLUMNS),
        "documented_columns":EXPECTED_COLUMNS,
        "documented_schema_match":best["score"]>=0.9,
        "data_row_count":row_count,
        "nonconforming_rows_after_record_start":malformed,
        "first_record_field_counts":first_rows_field_counts,
    }


def summarize_doc(doc: dict) -> dict:
    keys=(
        "identifier","title","formatId","size","checksum","dateUploaded",
        "dateModified","authoritativeMN","replicaMN","datasource",
    )
    return {key:doc.get(key) for key in keys if key in doc}


def audit(output_dir: Path) -> dict:
    docs=solr_search()
    latest_version,latest_docs=relevant_docs(docs)

    candidate_docs=[
        doc for doc in latest_docs
        if looks_like_data_format(doc)
    ]
    output_dir.mkdir(parents=True,exist_ok=True)

    resolved=[]
    for index,doc in enumerate(candidate_docs):
        pid=str(doc.get("identifier","")).strip()
        if not pid:
            continue
        url=resolver_url(pid)
        status,headers,raw=request(url)
        record={
            "document":summarize_doc(doc),
            "resolver_url":url,
            "http_status":status,
            "content_type":headers.get("content-type"),
            "bytes_received":len(raw),
        }
        if status==200 and raw:
            record["sha1"]=hashlib.sha1(raw).hexdigest()
            record["sha256"]=hashlib.sha256(raw).hexdigest()
            structure=parse_record_block(raw)
            record["structure"]=structure
            if structure.get("documented_schema_match"):
                path=output_dir/f"candidate_{index:02d}.txt"
                path.write_bytes(raw)
                record["cached_as"]=path.name
        resolved.append(record)

    adequate=[
        row for row in resolved
        if row.get("structure",{}).get("documented_schema_match")
        and row.get("structure",{}).get("data_row_count",0)>100
    ]

    return {
        "schema":"neon.powdermill_crossscale.source_audit.v1",
        "package_series":f"{PACKAGE_TOKEN}.{PACKAGE_NUMBER}",
        "latest_dataone_package_version":latest_version,
        "dataone_documents_at_latest_version":[
            summarize_doc(doc) for doc in latest_docs
        ],
        "resolved_candidate_objects":resolved,
        "documented_expected_columns":EXPECTED_COLUMNS,
        "source_adequacy_for_estimability_design":len(adequate)==1,
        "adequate_object_count":len(adequate),
        "adequate_object_identifiers":[
            row["document"].get("identifier") for row in adequate
        ],
        "geometry_note":"documented 10x10 stations at 10 m spacing with two trap slots per station",
        "species_specific_counts_inspected":False,
        "sex_specific_counts_inspected":False,
        "movement_distances_computed":False,
        "packing_effects_computed":False,
        "ecological_effect_models_fit":0,
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--cache-dir",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    out=audit(args.cache_dir)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "latest_dataone_package_version":out["latest_dataone_package_version"],
        "source_adequacy_for_estimability_design":
            out["source_adequacy_for_estimability_design"],
        "adequate_object_identifiers":out["adequate_object_identifiers"],
        "resolved_candidate_objects":out["resolved_candidate_objects"],
    },indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
