from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PRIMARY_SEX_COUNT_MIN=3
PHASE1_TOTAL_N_SCREEN=5
HETEROMYID_GENERA={"Chaetodipus","Dipodomys","Perognathus","Microdipodops"}


def _load_module(name: str, path: Path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE=_load_module(
    "run_neon_space_use_development_v1",
    ROOT/"analysis"/"run_neon_space_use_development_v1.py",
)
BUILDER=_load_module(
    "build_neon_sex_packing_inventory_v1",
    ROOT/"analysis"/"build_neon_sex_packing_inventory_v1.py",
)


def primary_gate_sites_from_phase1(phase1: dict) -> list[str]:
    """Return every site that can possibly contain a >=3/sex primary session.

    A paired >=3/sex session has total N >= 6. Therefore any species-site
    capable of entering the primary gate must already occur in the frozen
    Phase-1 N>=5 species-site inventory. The screen is response-derived but
    effect-blind and is used only to avoid downloading sites that cannot
    change the primary estimability decision.
    """
    if 2*PRIMARY_SEX_COUNT_MIN < PHASE1_TOTAL_N_SCREEN:
        raise RuntimeError("primary sex threshold no longer implies Phase-1 N screen")
    counts=((phase1.get("neon") or {}).get("n5_species_site_session_counts") or {})
    sites=set()
    for species,site_map in counts.items():
        genus=str(species).split(" ",1)[0]
        if genus not in HETEROMYID_GENERA:
            continue
        for site,count in (site_map or {}).items():
            if int(count or 0)>0:
                sites.add(str(site))
    return sorted(sites)


def build_inventory(
    sessions: list[dict],
    *,
    available_site_count: int,
    processed_site_count: int,
    target_taxon_count: int,
    data_query_requests: int,
    downloaded_required_file_count: int,
    downloaded_required_bytes: int,
    site_stops: list[dict],
) -> dict:
    out=BUILDER.summarize_neon_sex_sessions(sessions)
    out.update({
        "available_site_count":int(available_site_count),
        "processed_site_count":int(processed_site_count),
        "target_taxon_count":int(target_taxon_count),
        "data_query_requests":int(data_query_requests),
        "downloaded_required_file_count":int(downloaded_required_file_count),
        "downloaded_required_bytes":int(downloaded_required_bytes),
        "site_stops":list(site_stops),
        "ecological_effects_inspected":False,
        "ecological_model_fits":0,
    })
    return out


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:
        path.write_text("",encoding="utf-8")
        return
    fields=[]
    seen=set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fields.append(key)
    with path.open("w",newline="",encoding="utf-8") as fh:
        writer=csv.DictWriter(fh,fieldnames=fields,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def run_estimability(*, token: str, output_dir: Path, site_codes: list[str] | None=None) -> dict:
    product=BASE._request_json(BASE.PRODUCT_URL,token=token)
    available_sites=sorted(BASE.collect_site_codes(product))
    if not available_sites:
        raise RuntimeError("no NEON sites discovered")
    if site_codes is None:
        sites=available_sites
    else:
        unknown=sorted(set(site_codes)-set(available_sites))
        if unknown:
            raise RuntimeError(f"requested sites absent from NEON release metadata: {unknown}")
        sites=sorted(set(site_codes))

    taxonomy=BASE._request_json(BASE.TAXONOMY_URL,token=token)
    target_ids,_=BASE.target_taxa_from_taxonomy(taxonomy)
    if not target_ids:
        raise RuntimeError("no target small-mammal taxa discovered")

    all_sessions=[]
    file_count=0
    byte_count=0
    query_count=0
    site_stops=[]

    for index,site in enumerate(sites,start=1):
        print(f"SEX_NEON_SITE_START {index}/{len(sites)} {site}",flush=True)
        query={
            "productCode":BASE.PRODUCT_CODE,
            "siteCodes":[site],
            "startDateMonth":"2013-01",
            "endDateMonth":"2026-09",
            "release":BASE.RELEASE,
            "package":"expanded",
            "includeProvisional":False,
        }
        try:
            payload=BASE._request_json(BASE.QUERY_URL,token=token,body=query)
            query_count+=1
            files=BASE.select_required_files(payload,release=BASE.RELEASE)
            table_rows={table:[] for table in BASE.REQUIRED_TABLES}
            for row in files:
                records,nbytes=BASE._download_csv(row,token=token)
                table_rows[row["table"]].extend(records)
                file_count+=1
                byte_count+=nbytes

            plot_rows=table_rows["mam_perplotnight"]
            trap_rows=table_rows["mam_pertrapnight"]
            if not plot_rows or not trap_rows:
                site_stops.append({"site_code":site,"status":"no_required_capture_tables"})
                continue

            sessions=BUILDER.build_neon_sex_sessions(
                plot_rows,
                trap_rows,
                target_taxon_ids=target_ids,
            )
            all_sessions.extend(sessions)
            print(
                f"SEX_NEON_SITE_DONE {site} sessions={len(sessions)} "
                f"plot_rows={len(plot_rows)} trap_rows={len(trap_rows)}",
                flush=True,
            )
        except Exception as error:
            site_stops.append({
                "site_code":site,
                "status":"estimability_site_error",
                "detail":f"{type(error).__name__}: {error}",
            })
            print(f"SEX_NEON_SITE_ERROR {site} {type(error).__name__}: {error}",flush=True)

    if not all_sessions:
        raise RuntimeError("NEON sex estimability produced no sessions")

    processed=len({str(row.get("site","")) for row in all_sessions if str(row.get("site",""))})
    inventory=build_inventory(
        all_sessions,
        available_site_count=len(available_sites),
        processed_site_count=processed,
        target_taxon_count=len(target_ids),
        data_query_requests=query_count,
        downloaded_required_file_count=file_count,
        downloaded_required_bytes=byte_count,
        site_stops=site_stops,
    )

    output_dir.mkdir(parents=True,exist_ok=True)
    _write_csv(output_dir/"neon_heteromyid_sex_sessions_v1.csv",all_sessions)
    (output_dir/"neon_heteromyid_sex_inventory_v1.json").write_text(
        json.dumps(inventory,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return inventory


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,default=ROOT/"results"/"generated")
    parser.add_argument("--sites",nargs="*",default=None)
    args=parser.parse_args()
    token=os.environ.get("NEON_API_TOKEN","").strip()
    if not token:
        raise RuntimeError("NEON_API_TOKEN is required")
    inventory=run_estimability(token=token,output_dir=args.output_dir,site_codes=args.sites)
    print("NEON_SEX_ESTIMABILITY "+json.dumps({
        "session_count":inventory["session_count"],
        "paired_n2_sessions":inventory["paired_n2_sessions"],
        "paired_n3_sessions":inventory["paired_n3_sessions"],
        "paired_n5_sessions":inventory["paired_n5_sessions"],
        "species_count":inventory["species_count"],
        "site_stop_count":len(inventory["site_stops"]),
        "ecological_effects_inspected":inventory["ecological_effects_inspected"],
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
