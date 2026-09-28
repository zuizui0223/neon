from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def _load(name: str, rel: str):
    path=ROOT/rel
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NET=_load(
    "run_neon_sex_estimability_v1",
    "analysis/run_neon_sex_packing_estimability_v1.py",
)
BUILDER=_load(
    "build_neon_sex_effect_phase3",
    "analysis/build_neon_sex_effects_phase3_v1.py",
)


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
        w=csv.DictWriter(fh,fieldnames=fields,extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def run(*, token: str, output_dir: Path, site_codes: list[str]) -> dict:
    product=NET.BASE._request_json(NET.BASE.PRODUCT_URL,token=token)
    available_sites=sorted(NET.BASE.collect_site_codes(product))
    unknown=sorted(set(site_codes)-set(available_sites))
    if unknown:
        raise RuntimeError(f"requested sites absent from NEON release metadata: {unknown}")

    taxonomy=NET.BASE._request_json(NET.BASE.TAXONOMY_URL,token=token)
    target_ids,_=NET.BASE.target_taxa_from_taxonomy(taxonomy)
    if not target_ids:
        raise RuntimeError("no target small-mammal taxa discovered")

    all_sessions=[]
    site_stops=[]
    file_count=0
    byte_count=0
    query_count=0

    for index,site in enumerate(sorted(set(site_codes)),start=1):
        print(f"SEX_EFFECT_NEON_SITE_START {index}/{len(site_codes)} {site}",flush=True)
        try:
            query=NET.build_query_for_site(site,package="expanded")
            payload=NET.BASE._request_json(
                NET.BASE.QUERY_URL,token=token,body=query
            )
            query_count+=1
            files=NET.BASE.select_required_files(payload,release=NET.BASE.RELEASE)
            table_rows={table:[] for table in NET.BASE.REQUIRED_TABLES}
            for row in files:
                records,nbytes=NET.BASE._download_csv(row,token=token)
                table_rows[row["table"]].extend(records)
                file_count+=1
                byte_count+=nbytes

            plot_rows=table_rows["mam_perplotnight"]
            trap_rows=table_rows["mam_pertrapnight"]
            if not plot_rows or not trap_rows:
                site_stops.append({
                    "site_code":site,
                    "status":"no_required_capture_tables",
                })
                continue

            registry_xy=NET.BASE.location_registry_xy(site)
            coordinate_map=NET.BASE.coordinate_map_for_site(
                trap_rows,registry_xy
            )
            if not coordinate_map:
                site_stops.append({
                    "site_code":site,
                    "status":"no_coordinate_map",
                })
                continue

            sessions=BUILDER.build_neon_sex_effect_sessions(
                plot_rows,
                trap_rows,
                target_taxon_ids=target_ids,
                coordinate_map=coordinate_map,
            )
            all_sessions.extend(sessions)
            print(
                f"SEX_EFFECT_NEON_SITE_DONE {site} sessions={len(sessions)}",
                flush=True,
            )
        except Exception as error:
            site_stops.append({
                "site_code":site,
                "status":"effect_site_error",
                "detail":f"{type(error).__name__}: {error}",
            })
            print(
                f"SEX_EFFECT_NEON_SITE_ERROR {site} "
                f"{type(error).__name__}: {error}",
                flush=True,
            )

    if not all_sessions:
        raise RuntimeError("NEON sex effect extraction produced no sessions")

    inv=BUILDER.summarize(all_sessions)
    inv.update({
        "available_site_count":len(available_sites),
        "processed_site_count":len({
            str(row.get("site",""))
            for row in all_sessions if str(row.get("site",""))
        }),
        "screen_sites":sorted(set(site_codes)),
        "data_query_requests":query_count,
        "downloaded_required_file_count":file_count,
        "downloaded_required_bytes":byte_count,
        "site_stops":site_stops,
    })

    output_dir.mkdir(parents=True,exist_ok=True)
    _write_csv(
        output_dir/"neon_heteromyid_sex_effect_sessions_v1.csv",
        all_sessions,
    )
    (output_dir/"neon_heteromyid_sex_effect_inventory_v1.json").write_text(
        json.dumps(inv,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return inv


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--sites",nargs="+",required=True)
    args=parser.parse_args()

    token=os.environ.get("NEON_API_TOKEN","").strip()
    if not token:
        raise RuntimeError("NEON_API_TOKEN is required")

    inv=run(token=token,output_dir=args.output_dir,site_codes=args.sites)
    print(json.dumps(inv,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
