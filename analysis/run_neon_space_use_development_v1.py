from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import os
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

ROOT=Path(__file__).resolve().parents[1]
PRODUCT_CODE="DP1.10072.001"
RELEASE="RELEASE-2026"
QUERY_URL="https://data.neonscience.org/api/v0/data/query"
PRODUCT_URL=f"https://data.neonscience.org/api/v0/products/{PRODUCT_CODE}?release={RELEASE}"
TAXONOMY_URL=(
    "https://data.neonscience.org/api/v0/taxonomy?"
    "taxonTypeCode=SMALL_MAMMAL&verbose=true&offset=0&limit=1000"
)
USER_AGENT="neon-public-mammal-space-use-development/1.0"
REQUIRED_TABLES=("mam_identificationHistory","mam_perplotnight","mam_pertrapnight")


def _load_builder():
    path=ROOT/"analysis"/"build_neon_space_use_sessions_v1.py"
    spec=importlib.util.spec_from_file_location("build_neon_space_use_sessions_v1",path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILDER=_load_builder()


def collect_site_codes(value: object) -> set[str]:
    result=set()
    if isinstance(value,dict):
        site=value.get("siteCode")
        if isinstance(site,str) and site.strip():
            result.add(site.strip())
        for child in value.values():
            result.update(collect_site_codes(child))
    elif isinstance(value,list):
        for child in value:
            result.update(collect_site_codes(child))
    return result


def _table_from_name(name: str) -> str | None:
    for table in REQUIRED_TABLES:
        if f".{table}." in name or table in name:
            return table
    return None


def select_required_files(payload: dict, *, release: str) -> list[dict]:
    data=payload.get("data",{})
    releases=data.get("releases",[])
    matches=[row for row in releases if isinstance(row,dict) and row.get("release")==release]
    if len(matches)!=1:
        raise RuntimeError(f"expected exactly one {release} block")
    selected={}
    for package in matches[0].get("packages",[]):
        if not isinstance(package,dict):
            continue
        if str(package.get("packageType","")).strip().lower()!="expanded":
            continue
        site=str(package.get("siteCode","")).strip()
        month=str(package.get("month","")).strip()
        for row in package.get("files",[]):
            if not isinstance(row,dict):
                continue
            name=str(row.get("name",""))
            if not name.lower().endswith(".csv"):
                continue
            table=_table_from_name(name)
            if table is None:
                continue
            item={
                "table":table,
                "site_code":site,
                "month":month,
                "name":name,
                "url":str(row.get("url","")),
                "md5":str(row.get("md5","")).lower(),
                "size":int(row.get("size",0) or 0),
            }
            key=(site,month,table,name,item["md5"])
            selected[key]=item
    return [
        selected[key]
        for key in sorted(selected,key=lambda x:(x[2],x[0],x[1],x[3],x[4]))
    ]


def target_taxa_from_taxonomy(payload: dict) -> tuple[set[str],dict[str,str]]:
    ids=set()
    names={}
    for row in payload.get("data",[]):
        if not isinstance(row,dict):
            continue
        if str(row.get("dwc:taxonRank","")).strip().lower()!="species":
            continue
        if str(row.get("taxonProtocolCategory","")).strip().lower()!="target":
            continue
        taxon=str(row.get("taxonID","")).strip()
        name=str(row.get("dwc:scientificName","")).strip()
        if taxon and name:
            ids.add(taxon)
            names[taxon]=name
    return ids,dict(sorted(names.items()))


def taxonomy_uncertainty_summary(rows: Iterable[dict]) -> list[dict]:
    grouped: dict[tuple[str,str,str],Counter]=defaultdict(Counter)
    for raw in rows:
        row=dict(raw)
        site=str(row.get("siteID","")).strip()
        taxon=str(row.get("taxonID","")).strip()
        name=str(row.get("scientificName","")).strip()
        if not site or not taxon or not name:
            continue
        key=(site,taxon,name)
        grouped[key]["capture_rows"]+=1
        if str(row.get("identificationQualifier","")).strip():
            grouped[key]["qualified"]+=1
        if str(row.get("identificationHistoryID","")).strip():
            grouped[key]["history"]+=1
    return [
        {
            "site":site,
            "taxon_id":taxon,
            "species":name,
            "capture_row_count":counts["capture_rows"],
            "qualified_capture_row_count":counts["qualified"],
            "history_linked_capture_row_count":counts["history"],
        }
        for (site,taxon,name),counts in sorted(grouped.items())
    ]


def _request_json(url: str, *, token: str, body: dict | None=None) -> dict:
    headers={"User-Agent":USER_AGENT}
    if token:
        headers["X-API-Token"]=token
    data=None
    method="GET"
    if body is not None:
        headers["Content-Type"]="application/json"
        data=json.dumps(body,separators=(",",":"),sort_keys=True).encode("utf-8")
        method="POST"
    request=urllib.request.Request(url,data=data,method=method,headers=headers)
    with urllib.request.urlopen(request,timeout=180) as response:
        payload=json.loads(response.read().decode("utf-8"))
    if not isinstance(payload,dict):
        raise RuntimeError("NEON endpoint returned non-object JSON")
    return payload


def _download_csv(row: dict, *, token: str) -> tuple[list[dict],int]:
    headers={"User-Agent":USER_AGENT}
    if token:
        headers["X-API-Token"]=token
    request=urllib.request.Request(row["url"],headers=headers)
    with urllib.request.urlopen(request,timeout=300) as response:
        raw=response.read()
    if int(row["size"]) and len(raw)!=int(row["size"]):
        raise RuntimeError(f"size mismatch for {row['name']}")
    md5=str(row.get("md5",""))
    if md5 and len(md5)==32 and hashlib.md5(raw).hexdigest()!=md5:
        raise RuntimeError(f"md5 mismatch for {row['name']}")
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    return list(reader),len(raw)


def _capture_rows_for_taxonomy_summary(rows: Iterable[dict], target_ids: set[str]) -> list[dict]:
    result=[]
    for row in rows:
        if str(row.get("taxonID","")).strip() not in target_ids:
            continue
        if not BUILDER.is_capture_status(str(row.get("trapStatus",""))):
            continue
        result.append(dict(row))
    return result


def _write_csv(path: Path, rows: list[dict], *, fieldnames: list[str] | None=None) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    if fieldnames is None:
        fieldnames=[]
        seen=set()
        for row in rows:
            for key in row:
                if key not in seen:
                    seen.add(key)
                    fieldnames.append(key)
    with path.open("w",newline="",encoding="utf-8") as fh:
        writer=csv.DictWriter(fh,fieldnames=fieldnames,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def run_development(*, token: str, output_dir: Path, replicates: int=999) -> dict:
    product=_request_json(PRODUCT_URL,token=token)
    sites=sorted(collect_site_codes(product))
    if not sites:
        raise RuntimeError("no NEON sites discovered from release metadata")
    taxonomy=_request_json(TAXONOMY_URL,token=token)
    target_ids,target_names=target_taxa_from_taxonomy(taxonomy)
    if not target_ids:
        raise RuntimeError("no target small-mammal species discovered")

    all_sessions=[]
    all_taxonomy_summary=[]
    file_count=0
    byte_count=0
    query_count=0
    site_stops=[]

    for index,site in enumerate(sites,start=1):
        print(f"NEON_SITE_START {index}/{len(sites)} {site}",flush=True)
        query={
            "productCode":PRODUCT_CODE,
            "siteCodes":[site],
            "startDateMonth":"2013-01",
            "endDateMonth":"2026-09",
            "release":RELEASE,
            "package":"expanded",
            "includeProvisional":False,
        }
        try:
            payload=_request_json(QUERY_URL,token=token,body=query)
            query_count+=1
            files=select_required_files(payload,release=RELEASE)
            table_rows={table:[] for table in REQUIRED_TABLES}
            for row in files:
                records,nbytes=_download_csv(row,token=token)
                table_rows[row["table"]].extend(records)
                file_count+=1
                byte_count+=nbytes

            trap_rows=table_rows["mam_pertrapnight"]
            plot_rows=table_rows["mam_perplotnight"]
            history_rows=table_rows["mam_identificationHistory"]
            if not trap_rows or not plot_rows:
                site_stops.append({"site_code":site,"status":"no_required_capture_tables"})
                print(f"NEON_SITE_STOP {site} no_required_capture_tables",flush=True)
                continue

            coordinate_map=BUILDER.coordinate_map_from_trap_rows(trap_rows)
            sessions=BUILDER.build_neon_sessions(
                plot_rows,
                trap_rows,
                target_taxon_ids=target_ids,
                coordinate_map=coordinate_map,
                history_rows=history_rows,
                replicates=replicates,
            )
            all_sessions.extend(sessions)
            all_taxonomy_summary.extend(
                taxonomy_uncertainty_summary(
                    _capture_rows_for_taxonomy_summary(trap_rows,target_ids)
                )
            )
            print(
                f"NEON_SITE_DONE {site} plot_rows={len(plot_rows)} "
                f"trap_rows={len(trap_rows)} sessions={len(sessions)}",
                flush=True,
            )
        except Exception as error:
            site_stops.append({
                "site_code":site,
                "status":"development_site_error",
                "detail":f"{type(error).__name__}: {error}",
            })
            print(
                f"NEON_SITE_ERROR {site} {type(error).__name__}: {error}",
                flush=True,
            )

    if not all_sessions:
        raise RuntimeError("NEON development run produced no sessions")

    inventory=BUILDER.summarize_neon_sessions(all_sessions)
    inventory.update({
        "product_code":PRODUCT_CODE,
        "release":RELEASE,
        "inferential_status":"retrospective_development_only",
        "available_site_count":len(sites),
        "processed_site_count":len({row["site"] for row in all_sessions}),
        "target_taxon_count":len(target_ids),
        "target_taxa":target_names,
        "data_query_requests":query_count,
        "downloaded_required_file_count":file_count,
        "downloaded_required_bytes":byte_count,
        "site_stops":site_stops,
        "ecological_model_fits":0,
    })

    output_dir.mkdir(parents=True,exist_ok=True)
    _write_csv(output_dir/"neon_diversity_space_use_sessions_v1.csv",all_sessions)
    _write_csv(
        output_dir/"neon_taxonomy_uncertainty_v1.csv",
        all_taxonomy_summary,
        fieldnames=[
            "site","taxon_id","species","capture_row_count",
            "qualified_capture_row_count","history_linked_capture_row_count",
        ],
    )
    (output_dir/"neon_space_use_inventory_v1.json").write_text(
        json.dumps(inventory,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return inventory


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,default=ROOT/"results"/"generated")
    parser.add_argument("--replicates",type=int,default=999)
    args=parser.parse_args()
    token=os.environ.get("NEON_API_TOKEN","").strip()
    if not token:
        raise RuntimeError("NEON_API_TOKEN is required")
    inventory=run_development(
        token=token,
        output_dir=args.output_dir,
        replicates=args.replicates,
    )
    print("NEON_DEVELOPMENT_SUMMARY "+json.dumps({
        "session_count":inventory["session_count"],
        "eligible_n3":inventory["eligible_n3"],
        "eligible_n5":inventory["eligible_n5"],
        "eligible_n8":inventory["eligible_n8"],
        "species_count":inventory["species_count"],
        "site_count":inventory["site_count"],
        "site_stop_count":len(inventory["site_stops"]),
        "ecological_model_fits":inventory["ecological_model_fits"],
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
