from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any


USER_AGENT="usgs-hispidus-source-audit/1.0"
CKAN_ROOT="https://catalog.data.gov/api/3/action/package_search"
SCIENCEBASE_ITEM_RE=re.compile(
    r"https?://(?:www\.)?sciencebase\.gov/catalog/item/([0-9a-fA-F]{24})"
)
URL_RE=re.compile(r"https?://[^\s<>\"']+")


def fetch_bytes(url: str, *, accept: str | None=None) -> tuple[bytes,int,str]:
    headers={"User-Agent":USER_AGENT}
    if accept:
        headers["Accept"]=accept
    req=urllib.request.Request(url,headers=headers)
    try:
        with urllib.request.urlopen(req,timeout=180) as response:
            return (
                response.read(),
                int(getattr(response,"status",200) or 200),
                str(response.headers.get("Content-Type","")),
            )
    except urllib.error.HTTPError as error:
        raw=error.read()
        return raw,int(error.code),str(error.headers.get("Content-Type",""))


def fetch_json(url: str) -> tuple[dict | None,int]:
    raw,status,_=fetch_bytes(url,accept="application/json")
    if status<200 or status>=300:
        return None,status
    return json.loads(raw.decode("utf-8")),status


def ckan_package(identifier: str, title_hint: str) -> dict:
    for query in (identifier,title_hint):
        url=CKAN_ROOT+"?"+urllib.parse.urlencode({"q":query,"rows":20})
        payload,status=fetch_json(url)
        if status!=200 or not payload or not payload.get("success"):
            continue
        results=((payload.get("result") or {}).get("results") or [])
        for row in results:
            blob=json.dumps(row,sort_keys=True).lower()
            if identifier.lower() in blob or title_hint.lower() in str(row.get("title","")).lower():
                return row
    raise RuntimeError("Data.gov CKAN package not resolved")


def xml_metadata(resources: list[dict]) -> list[dict]:
    out=[]
    for row in resources:
        fmt=str(row.get("format","")).strip().lower()
        url=str(row.get("url","")).strip()
        if not url or "xml" not in fmt:
            continue
        raw,status,ctype=fetch_bytes(url)
        text=raw.decode("utf-8",errors="replace")
        urls=sorted(set(URL_RE.findall(text)))
        sciencebase_ids=sorted({
            match.group(1).lower()
            for match in SCIENCEBASE_ITEM_RE.finditer(text)
        })
        out.append({
            "name":row.get("name"),
            "url":url,
            "status":status,
            "content_type":ctype,
            "size_bytes":len(raw),
            "sha256":hashlib.sha256(raw).hexdigest(),
            "sciencebase_item_ids":sciencebase_ids,
            "urls":urls[:200],
        })
    return out


def sciencebase_items(item_ids: list[str]) -> list[dict]:
    out=[]
    for item_id in item_ids:
        url=f"https://www.sciencebase.gov/catalog/item/{item_id}?format=json"
        payload,status=fetch_json(url)
        if status!=200 or payload is None:
            out.append({
                "item_id":item_id,
                "metadata_status":status,
                "files":[],
            })
            continue
        files=[]
        for row in payload.get("files",[]) or []:
            if not isinstance(row,dict):
                continue
            files.append({
                "name":row.get("name"),
                "size":row.get("size"),
                "contentType":row.get("contentType"),
                "checksum":row.get("checksum"),
                "downloadUri":row.get("downloadUri"),
                "url":row.get("url"),
            })
        out.append({
            "item_id":item_id,
            "metadata_status":status,
            "title":payload.get("title"),
            "files":files,
        })
    return out


def _candidate_download_url(row: dict) -> str | None:
    for key in ("downloadUri","url"):
        value=row.get(key)
        if isinstance(value,str) and value.startswith("http"):
            return value
    return None


def _classify_columns(columns: list[str]) -> dict[str,list[str]]:
    categories={
        "identity":[],
        "sex":[],
        "species":[],
        "capture_time":[],
        "trap_or_station":[],
        "latitude":[],
        "longitude":[],
        "site_or_plot":[],
    }
    for col in columns:
        n=re.sub(r"[^a-z0-9]+","_",col.lower()).strip("_")
        if re.search(r"(^|_)(tag|pit|ear_tag|animal_id|individual_id|unique_id|mark_id)($|_)",n):
            categories["identity"].append(col)
        if n in {"sex","gender"} or n.endswith("_sex"):
            categories["sex"].append(col)
        if re.search(r"(^|_)(species|species_code|taxon|scientific_name)($|_)",n):
            categories["species"].append(col)
        if re.search(r"(^|_)(date|datetime|time|occasion|session|night|day|year|month)($|_)",n):
            categories["capture_time"].append(col)
        if re.search(r"(^|_)(trap|station|stake|grid_cell|capture_location)($|_)",n):
            categories["trap_or_station"].append(col)
        if re.search(r"(^|_)(lat|latitude)($|_)",n):
            categories["latitude"].append(col)
        if re.search(r"(^|_)(lon|long|longitude)($|_)",n):
            categories["longitude"].append(col)
        if re.search(r"(^|_)(site|plot|grid|location)($|_)",n):
            categories["site_or_plot"].append(col)
    return categories


def audit_text_file(name: str, raw: bytes, content_type: str) -> dict:
    text=raw.decode("utf-8-sig",errors="replace")
    try:
        delimiter=csv.Sniffer().sniff(text[:65536],delimiters=",\t;|").delimiter
    except csv.Error:
        delimiter=","
    reader=csv.reader(text.splitlines(),delimiter=delimiter)
    try:
        columns=[str(x).strip() for x in next(reader)]
    except StopIteration:
        columns=[]
    row_count=0
    malformed=0
    for row in reader:
        if not row:
            continue
        row_count+=1
        if len(row)!=len(columns):
            malformed+=1
    structural=_classify_columns(columns)
    has_spatial=bool(
        structural["trap_or_station"]
        or (structural["latitude"] and structural["longitude"])
    )
    adequate=all([
        structural["identity"],
        structural["sex"],
        structural["species"],
        structural["capture_time"],
        has_spatial,
    ])
    return {
        "name":name,
        "content_type":content_type,
        "size_bytes":len(raw),
        "sha256":hashlib.sha256(raw).hexdigest(),
        "delimiter":repr(delimiter),
        "columns":columns,
        "data_row_count":row_count,
        "malformed_row_count":malformed,
        "structural_columns":structural,
        "has_spatial_capture_field":has_spatial,
        "structurally_adequate_for_estimability_design":bool(adequate),
    }


def audit(identifier: str, title_hint: str, output_dir: Path) -> dict:
    package=ckan_package(identifier,title_hint)
    resources=package.get("resources",[]) or []
    xml=xml_metadata(resources)
    item_ids=sorted({
        item_id
        for row in xml
        for item_id in row["sciencebase_item_ids"]
    })
    items=sciencebase_items(item_ids)

    output_dir.mkdir(parents=True,exist_ok=True)
    audited_files=[]
    for item in items:
        for row in item["files"]:
            name=str(row.get("name") or "").strip()
            url=_candidate_download_url(row)
            if not name or not url:
                continue
            lower=name.lower()
            if not lower.endswith((".csv",".txt",".tsv")):
                continue
            raw,status,ctype=fetch_bytes(url)
            if status!=200:
                audited_files.append({
                    "name":name,
                    "download_status":status,
                    "download_url":url,
                })
                continue
            path=output_dir/name.replace("/","_")
            path.write_bytes(raw)
            record=audit_text_file(name,raw,ctype)
            record["download_status"]=status
            record["download_url"]=url
            audited_files.append(record)

    adequate_files=[
        row["name"] for row in audited_files
        if row.get("structurally_adequate_for_estimability_design")
    ]

    return {
        "schema":"neon.usgs_hispidus_source_audit.v1",
        "catalog_identifier":identifier,
        "catalog_title":package.get("title"),
        "catalog_name":package.get("name"),
        "catalog_resources":[{
            "name":r.get("name"),
            "format":r.get("format"),
            "url":r.get("url"),
        } for r in resources],
        "xml_metadata":xml,
        "sciencebase_items":items,
        "audited_text_files":audited_files,
        "structurally_adequate_files":adequate_files,
        "source_adequacy_for_estimability_design":bool(adequate_files),
        "species_specific_counts_inspected":False,
        "sex_specific_counts_inspected":False,
        "movement_distances_computed":False,
        "packing_effects_computed":False,
        "ecological_effect_models_fit":0,
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--identifier",required=True)
    parser.add_argument("--title-hint",required=True)
    parser.add_argument("--cache-dir",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()

    out=audit(args.identifier,args.title_hint,args.cache_dir)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "catalog_title":out["catalog_title"],
        "sciencebase_item_count":len(out["sciencebase_items"]),
        "audited_text_files":[{
            "name":x.get("name"),
            "download_status":x.get("download_status"),
            "columns":x.get("columns"),
            "structural_columns":x.get("structural_columns"),
            "adequate":x.get("structurally_adequate_for_estimability_design"),
        } for x in out["audited_text_files"]],
        "source_adequacy_for_estimability_design":
            out["source_adequacy_for_estimability_design"],
    },indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
