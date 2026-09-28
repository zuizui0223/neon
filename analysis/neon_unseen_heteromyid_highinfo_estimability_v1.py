from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import os
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HETEROMYID_GENERA={"Chaetodipus","Dipodomys","Perognathus","Microdipodops"}
DISCOVERY_SPECIES={
    "Chaetodipus penicillatus",
    "Dipodomys merriami",
    "Dipodomys ordii",
}


def _load(name: str, rel: str):
    path=ROOT/rel
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DEV=_load("neon_development","analysis/run_neon_space_use_development_v1.py")
BASE=_load("neon_sessions","analysis/build_neon_space_use_sessions_v1.py")
SEXHELP=_load("sex_estimability","analysis/mammal_sex_packing_estimability_v1.py")


def is_unseen_heteromyid(name: str) -> bool:
    parts=str(name or "").strip().split()
    if len(parts)<2:
        return False
    if parts[0] not in HETEROMYID_GENERA:
        return False
    if str(name).strip() in DISCOVERY_SPECIES:
        return False
    return parts[1].lower() not in {"sp","sp.","spp","spp."}


def _is_valid_pathogen_plotnight(row: dict) -> bool:
    method=str(
        row.get("mammalGridSamplingMethod",row.get("mammalGridSamplingType",""))
    ).strip().lower()
    completion=str(row.get("gridCompletion","")).strip().lower()
    impractical=str(row.get("samplingImpractical","")).strip()
    return (
        method=="pathogen"
        and completion==BASE.COMPLETE_GRID
        and impractical in {"","OK"}
    )


def _node_id(row: dict) -> str:
    return (
        f"{str(row.get('namedLocation','')).strip()}."
        f"{str(row.get('trapCoordinate','')).strip()}"
    )


def build_estimability_rows(
    plot_rows: list[dict],
    trap_rows: list[dict],
    *,
    target_taxon_ids: set[str],
    coordinate_map: dict[str,tuple[float,float]],
) -> list[dict]:
    event_nights=defaultdict(dict)
    for raw in plot_rows:
        row=dict(raw)
        if not _is_valid_pathogen_plotnight(row):
            continue
        site=str(row.get("siteID","")).strip()
        plot=str(row.get("plotID","")).strip()
        event=str(row.get("eventID","")).strip()
        night=str(row.get("nightuid","")).strip()
        date=str(row.get("collectDate","")).strip()
        if not site or not plot or not event or not night:
            continue
        event_nights[(site,plot,event)][night]=date

    traps_by_night=defaultdict(list)
    for raw in trap_rows:
        row=dict(raw)
        night=str(row.get("nightuid","")).strip()
        if night:
            traps_by_night[night].append(row)

    out=[]
    for (site,plot,event),night_map in sorted(event_nights.items()):
        if len(night_map)<2:
            continue
        event_rows=[]
        for night in sorted(night_map,key=lambda n:(night_map[n],n)):
            event_rows.extend(traps_by_night.get(night,[]))
        if not event_rows:
            continue

        grouped=defaultdict(list)
        for row in event_rows:
            if not BASE.is_capture_status(str(row.get("trapStatus",""))):
                continue
            taxon=str(row.get("taxonID","")).strip()
            name=str(row.get("scientificName","")).strip()
            if taxon not in target_taxon_ids:
                continue
            if not is_unseen_heteromyid(name):
                continue
            if str(row.get("taxonRank","")).strip().lower()!="species":
                continue
            if str(row.get("identificationQualifier","")).strip():
                continue
            tag=str(row.get("tagID","")).strip()
            node=_node_id(row)
            if not tag or node not in coordinate_map:
                continue
            grouped[(taxon,name)].append(dict(row))

        for (taxon,name),captures in sorted(grouped.items()):
            by_tag=defaultdict(list)
            for row in sorted(captures,key=lambda x:str(x.get("uid",""))):
                by_tag[str(row.get("tagID","")).strip()].append(row)

            n_male=0
            n_female=0
            n_conflict_or_unknown=0
            n_single_night=0
            for _,observations in sorted(by_tag.items()):
                sexes={
                    SEXHELP.normalize_sex(row.get("sex"))
                    for row in observations
                    if SEXHELP.normalize_sex(row.get("sex")) is not None
                }
                if len(sexes)!=1:
                    n_conflict_or_unknown+=1
                    continue
                sex=next(iter(sexes))
                nights={
                    str(row.get("nightuid","")).strip()
                    for row in observations
                    if str(row.get("nightuid","")).strip()
                    and _node_id(row) in coordinate_map
                }
                if len(nights)<2:
                    n_single_night+=1
                    continue
                if sex=="M":
                    n_male+=1
                elif sex=="F":
                    n_female+=1

            out.append({
                "site":site,
                "plot_id":plot,
                "event_id":event,
                "species":name,
                "taxon_id":taxon,
                "event_night_count":len(night_map),
                "n_recapture_male":n_male,
                "n_recapture_female":n_female,
                "n_conflict_or_unknown_sex":n_conflict_or_unknown,
                "n_single_night_known_sex":n_single_night,
                "paired_n3_eligible":n_male>=3 and n_female>=3,
                "paired_n5_eligible":n_male>=5 and n_female>=5,
            })
    return out


def summarize(rows: list[dict]) -> dict:
    names=sorted({row["species"] for row in rows})
    species={}
    for name in names:
        srows=[row for row in rows if row["species"]==name]
        p3=[row for row in srows if row["paired_n3_eligible"]]
        p5=[row for row in srows if row["paired_n5_eligible"]]
        species[name]={
            "event_count":len(srows),
            "paired_n3_events":len(p3),
            "paired_n5_events":len(p5),
            "n3_sites":sorted({row["site"] for row in p3}),
            "n5_sites":sorted({row["site"] for row in p5}),
        }

    qualifying=[
        name for name,row in species.items()
        if row["paired_n5_events"]>=5
    ]
    qualifying_sites=sorted({
        site
        for name in qualifying
        for site in species[name]["n5_sites"]
    })
    passed=len(qualifying)>=3 and len(qualifying_sites)>=3

    return {
        "schema":"neon.heteromyid_high_information_movement_validation.estimability.v1",
        "product_code":DEV.PRODUCT_CODE,
        "release":DEV.RELEASE,
        "discovery_species_excluded":sorted(DISCOVERY_SPECIES),
        "candidate_species_count":len(species),
        "event_species_rows":len(rows),
        "species":species,
        "gate":{
            "minimum_qualifying_species":3,
            "minimum_primary_events_per_species":5,
            "minimum_distinct_sites_over_qualifying_species":3,
            "qualifying_species":qualifying,
            "qualifying_sites":qualifying_sites,
            "passed":passed,
            "decision":(
                "authorize_unseen_species_movement_effects"
                if passed else
                "stop_unseen_species_not_estimable"
            ),
        },
        "validation_species_movement_magnitudes_inspected":False,
        "movement_effect_models_fit":0,
    }


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:
        path.write_text("",encoding="utf-8")
        return
    fields=list(rows[0].keys())
    with path.open("w",newline="",encoding="utf-8") as fh:
        writer=csv.DictWriter(fh,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run(*, token: str, output_dir: Path) -> dict:
    product=DEV._request_json(DEV.PRODUCT_URL,token=token)
    sites=sorted(DEV.collect_site_codes(product))
    taxonomy=DEV._request_json(DEV.TAXONOMY_URL,token=token)
    target_ids,_=DEV.target_taxa_from_taxonomy(taxonomy)

    rows=[]
    stops=[]
    query_count=0
    file_count=0
    byte_count=0

    for index,site in enumerate(sites,start=1):
        print(f"UNSEEN_HET_EST_SITE_START {index}/{len(sites)} {site}",flush=True)
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
            for file_row in files:
                records,nbytes=DEV._download_csv(file_row,token=token)
                table_rows[file_row["table"]].extend(records)
                file_count+=1
                byte_count+=nbytes

            plot_rows=table_rows["mam_perplotnight"]
            trap_rows=table_rows["mam_pertrapnight"]
            if not plot_rows or not trap_rows:
                stops.append({"site_code":site,"status":"no_required_capture_tables"})
                continue

            registry_xy=DEV.location_registry_xy(site)
            coordinate_map=DEV.coordinate_map_for_site(trap_rows,registry_xy)
            if not coordinate_map:
                stops.append({"site_code":site,"status":"no_trap_coordinates"})
                continue

            site_rows=build_estimability_rows(
                plot_rows,
                trap_rows,
                target_taxon_ids=target_ids,
                coordinate_map=coordinate_map,
            )
            rows.extend(site_rows)
            print(f"UNSEEN_HET_EST_SITE_DONE {site} rows={len(site_rows)}",flush=True)
        except Exception as error:
            stops.append({
                "site_code":site,
                "status":"site_error",
                "detail":f"{type(error).__name__}: {error}",
            })
            print(
                f"UNSEEN_HET_EST_SITE_ERROR {site} {type(error).__name__}: {error}",
                flush=True,
            )

    result=summarize(rows)
    result.update({
        "available_site_count":len(sites),
        "processed_site_count":len({row["site"] for row in rows}),
        "data_query_requests":query_count,
        "downloaded_required_file_count":file_count,
        "downloaded_required_bytes":byte_count,
        "site_stops":stops,
    })

    output_dir.mkdir(parents=True,exist_ok=True)
    _write_csv(output_dir/"unseen_heteromyid_highinfo_estimability_events_v1.csv",rows)
    (output_dir/"unseen_heteromyid_highinfo_estimability_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    token=os.environ.get("NEON_API_TOKEN","").strip()
    if not token:
        raise RuntimeError("NEON_API_TOKEN is required")
    result=run(token=token,output_dir=args.output_dir)
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
