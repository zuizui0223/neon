from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def _load_module(name: str, path: Path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DEV=_load_module(
    "neon_development",
    ROOT/"analysis"/"run_neon_space_use_development_v1.py",
)
MOVEMENT=_load_module(
    "neon_recapture_validation",
    ROOT/"analysis"/"neon_recapture_validation_phase2_v1.py",
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
        writer=csv.DictWriter(fh,fieldnames=fields,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def run_recapture_validation(
    *,
    token: str,
    output_dir: Path,
    replicates: int=999,
) -> dict:
    product=DEV._request_json(DEV.PRODUCT_URL,token=token)
    sites=sorted(DEV.collect_site_codes(product))
    taxonomy=DEV._request_json(DEV.TAXONOMY_URL,token=token)
    target_ids,target_names=DEV.target_taxa_from_taxonomy(taxonomy)

    validation_rows=[]
    site_stops=[]
    query_count=0
    file_count=0
    byte_count=0

    for index,site in enumerate(sites,start=1):
        print(f"RECAPTURE_SITE_START {index}/{len(sites)} {site}",flush=True)
        query={
            "productCode":DEV.PRODUCT_CODE,
            "siteCodes":[site],
            "startDateMonth":"2013-01",
            "endDateMonth":"2026-09",
            "release":DEV.RELEASE,
            "package":"expanded",
            "includeProvisional":False,
        }
        try:
            payload=DEV._request_json(DEV.QUERY_URL,token=token,body=query)
            query_count+=1
            files=DEV.select_required_files(payload,release=DEV.RELEASE)
            table_rows={table:[] for table in DEV.REQUIRED_TABLES}
            for row in files:
                records,nbytes=DEV._download_csv(row,token=token)
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

            registry_xy=DEV.location_registry_xy(site)
            coordinate_map=DEV.coordinate_map_for_site(trap_rows,registry_xy)
            if not coordinate_map:
                site_stops.append({
                    "site_code":site,
                    "status":"no_trap_coordinates",
                })
                continue

            rows=MOVEMENT.build_pathogen_validation_rows(
                plot_rows,
                trap_rows,
                target_taxon_ids=target_ids,
                coordinate_map=coordinate_map,
                replicates=replicates,
            )
            validation_rows.extend(rows)
            print(
                f"RECAPTURE_SITE_DONE {site} validation_rows={len(rows)}",
                flush=True,
            )
        except Exception as error:
            site_stops.append({
                "site_code":site,
                "status":"site_error",
                "detail":f"{type(error).__name__}: {error}",
            })
            print(
                f"RECAPTURE_SITE_ERROR {site} {type(error).__name__}: {error}",
                flush=True,
            )

    output_dir.mkdir(parents=True,exist_ok=True)
    event_csv=output_dir/"neon_recapture_validation_events_v1.csv"
    _write_csv(event_csv,validation_rows)

    payload={
        "schema":"neon.public_mammal_space_use.recapture_validation_phase2.v1",
        "product_code":DEV.PRODUCT_CODE,
        "release":DEV.RELEASE,
        "inferential_status":"retrospective_secondary_validation",
        "available_site_count":len(sites),
        "raw_validation_event_rows":len(validation_rows),
        "target_taxon_count":len(target_ids),
        "target_taxa":target_names,
        "data_query_requests":query_count,
        "downloaded_required_file_count":file_count,
        "downloaded_required_bytes":byte_count,
        "site_stops":site_stops,
        "eligibility":{
            "first_night_min_unique_individuals":5,
            "min_moving_individuals_per_event":3,
            "min_events_per_species_site_stratum":5,
            "movement_summary":"median of individual median successive-night displacement",
            "packing_summary":"first-night abundance- and geometry-conditioned Packing_z",
        },
        "ecological_model_fits":0,
    }

    if validation_rows:
        try:
            df=MOVEMENT.prepare_validation_frame(
                validation_rows,
                min_events_per_stratum=5,
            )
            result=MOVEMENT.fit_validation_model(df)
            payload.update({
                "status":"estimable",
                "model":{
                    "formula":"log1p_movement ~ packing_z + z_logN + C(species_site)",
                    "covariance":"HC3",
                    "nobs":int(result.nobs),
                    "design_rank":int(__import__("numpy").linalg.matrix_rank(result.model.exog)),
                    "design_columns":int(result.model.exog.shape[1]),
                    "rsquared":float(result.rsquared),
                    "species_site_strata":sorted(df["species_site"].unique()),
                    "stratum_count":int(df["species_site"].nunique()),
                },
                "coefficients":{
                    "packing_z":MOVEMENT.UTILS.coefficient_record(result,"packing_z"),
                    "z_logN":MOVEMENT.UTILS.coefficient_record(result,"z_logN"),
                },
                "ecological_model_fits":1,
            })
        except Exception as error:
            payload.update({
                "status":"non_estimable_under_frozen_gate",
                "non_estimable_reason":f"{type(error).__name__}: {error}",
            })
    else:
        payload.update({
            "status":"non_estimable_under_frozen_gate",
            "non_estimable_reason":"no event-species rows met first-night packing and movement gates",
        })

    out_json=output_dir/"neon_recapture_validation_phase2_v1.json"
    out_json.write_text(
        json.dumps(payload,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return payload


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--replicates",type=int,default=999)
    args=parser.parse_args()
    token=os.environ.get("NEON_API_TOKEN","").strip()
    if not token:
        raise RuntimeError("NEON_API_TOKEN is required")
    payload=run_recapture_validation(
        token=token,
        output_dir=args.output_dir,
        replicates=args.replicates,
    )
    print("RECAPTURE_VALIDATION_SUMMARY "+json.dumps({
        "status":payload["status"],
        "raw_validation_event_rows":payload["raw_validation_event_rows"],
        "ecological_model_fits":payload["ecological_model_fits"],
        "site_stop_count":len(payload["site_stops"]),
        "packing_effect":(
            payload.get("coefficients",{}).get("packing_z",{}).get("estimate")
        ),
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
