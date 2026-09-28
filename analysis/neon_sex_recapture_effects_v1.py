from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import os
import statistics
from collections import defaultdict
from pathlib import Path

from scipy.stats import t as student_t

ROOT=Path(__file__).resolve().parents[1]


def _load(name: str, rel: str):
    path=ROOT/rel
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EST=_load(
    "sex_recapture_estimability",
    "analysis/neon_sex_recapture_estimability_v1.py",
)
DEV=EST.DEV
BASE=EST.BASE
SEXHELP=EST.SEXHELP


def individual_movement_records(
    captures: list[dict],
    coordinate_map: dict[str,tuple[float,float]],
) -> list[dict]:
    by_tag=defaultdict(list)
    for row in captures:
        tag=str(row.get("tagID","")).strip()
        if tag:
            by_tag[tag].append(dict(row))

    out=[]
    for tag,observations in sorted(by_tag.items()):
        sexes={
            SEXHELP.normalize_sex(row.get("sex"))
            for row in observations
            if SEXHELP.normalize_sex(row.get("sex")) is not None
        }
        if len(sexes)!=1:
            continue
        sex=next(iter(sexes))

        by_night={}
        for row in sorted(
            observations,
            key=lambda x:(
                str(x.get("collectDate","")).strip(),
                str(x.get("nightuid","")).strip(),
                str(x.get("uid","")).strip(),
            ),
        ):
            night=str(row.get("nightuid","")).strip()
            node=EST._node_id(row)
            if not night or node not in coordinate_map:
                continue
            by_night.setdefault(night,row)

        ordered=sorted(
            by_night.values(),
            key=lambda x:(
                str(x.get("collectDate","")).strip(),
                str(x.get("nightuid","")).strip(),
            ),
        )
        if len(ordered)<2:
            continue

        displacements=[]
        for left,right in zip(ordered,ordered[1:]):
            lx,ly=coordinate_map[EST._node_id(left)]
            rx,ry=coordinate_map[EST._node_id(right)]
            dx=float(rx)-float(lx)
            dy=float(ry)-float(ly)
            displacements.append(float(math.hypot(dx,dy)))

        if not displacements:
            continue
        median_m=float(statistics.median(displacements))
        out.append({
            "tag_id":tag,
            "sex":sex,
            "night_count":len(ordered),
            "successive_displacement_count":len(displacements),
            "median_successive_displacement_m":median_m,
            "log1p_median_successive_displacement":math.log1p(median_m),
        })
    return out


def build_recapture_effect_rows(
    plot_rows: list[dict],
    trap_rows: list[dict],
    *,
    target_taxon_ids: set[str],
    coordinate_map: dict[str,tuple[float,float]],
    candidate_species: set[str],
) -> list[dict]:
    event_nights=defaultdict(dict)
    for raw in plot_rows:
        row=dict(raw)
        if not EST._is_valid_pathogen_plotnight(row):
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
            if taxon not in target_taxon_ids or name not in candidate_species:
                continue
            if str(row.get("taxonRank","")).strip().lower()!="species":
                continue
            if str(row.get("identificationQualifier","")).strip():
                continue
            tag=str(row.get("tagID","")).strip()
            node=EST._node_id(row)
            if not tag or node not in coordinate_map:
                continue
            grouped[(taxon,name)].append(dict(row))

        for (taxon,name),captures in sorted(grouped.items()):
            individuals=individual_movement_records(captures,coordinate_map)
            males=[
                row["log1p_median_successive_displacement"]
                for row in individuals if row["sex"]=="M"
            ]
            females=[
                row["log1p_median_successive_displacement"]
                for row in individuals if row["sex"]=="F"
            ]
            if len(males)<2 or len(females)<2:
                continue
            male_median=float(statistics.median(males))
            female_median=float(statistics.median(females))
            out.append({
                "source":"NEON",
                "site":site,
                "plot_id":plot,
                "event_id":event,
                "species":name,
                "taxon_id":taxon,
                "event_night_count":len(night_map),
                "n_recapture_male":len(males),
                "n_recapture_female":len(females),
                "male_median_log1p_displacement":male_median,
                "female_median_log1p_displacement":female_median,
                "delta_sex_movement":male_median-female_median,
                "paired_n2_eligible":len(males)>=2 and len(females)>=2,
                "paired_n3_eligible":len(males)>=3 and len(females)>=3,
                "paired_n5_eligible":len(males)>=5 and len(females)>=5,
            })
    return out


def _mean_ci_t(values: list[float]) -> dict:
    values=[float(x) for x in values]
    n=len(values)
    if n==0:
        return {
            "n":0,"mean":None,"sd":None,"standard_error":None,
            "df":None,"ci95_low":None,"ci95_high":None,"estimable":False,
        }
    mean=float(statistics.mean(values))
    if n<2:
        return {
            "n":n,"mean":mean,"sd":None,"standard_error":None,
            "df":0,"ci95_low":None,"ci95_high":None,"estimable":False,
        }
    sd=float(statistics.stdev(values))
    se=sd/math.sqrt(n)
    df=n-1
    critical=float(student_t.ppf(0.975,df))
    return {
        "n":n,"mean":mean,"sd":sd,"standard_error":se,"df":df,
        "ci95_low":mean-critical*se,
        "ci95_high":mean+critical*se,
        "estimable":True,
    }


def movement_effect(
    rows: list[dict],
    *,
    species_set: list[str],
    n_min: int,
) -> dict:
    species_results=[]
    for species in species_set:
        srows=[
            row for row in rows
            if row["species"]==species
            and int(row["n_recapture_male"])>=n_min
            and int(row["n_recapture_female"])>=n_min
        ]
        by_site=defaultdict(list)
        for row in srows:
            by_site[row["site"]].append(float(row["delta_sex_movement"]))
        site_means={
            site:float(statistics.mean(values))
            for site,values in sorted(by_site.items())
        }
        summary=_mean_ci_t(list(site_means.values()))
        species_results.append({
            "species":species,
            "event_count":len(srows),
            "site_count":len(site_means),
            "site_means":site_means,
            "effect":summary["mean"],
            "sd_across_sites":summary["sd"],
            "standard_error":summary["standard_error"],
            "df":summary["df"],
            "ci95_low":summary["ci95_low"],
            "ci95_high":summary["ci95_high"],
            "estimable":summary["estimable"],
        })

    all_estimable=all(row["estimable"] for row in species_results)
    if all_estimable:
        family=_mean_ci_t([row["effect"] for row in species_results])
        status="estimable"
    else:
        family=_mean_ci_t([])
        status="non_estimable_full_frozen_species_set"

    return {
        "n_min_per_sex":n_min,
        "species":species_results,
        "family":{
            "status":status,
            "effect":family["mean"],
            "species_count":family["n"],
            "sd_across_species":family["sd"],
            "standard_error":family["standard_error"],
            "df":family["df"],
            "ci95_low":family["ci95_low"],
            "ci95_high":family["ci95_high"],
            "estimable":family["estimable"] and all_estimable,
        },
    }


def manuscript_decision(
    primary: dict,
    interpretation_gate: dict,
) -> dict:
    family=primary["family"]
    positive_species=[
        row["species"] for row in primary["species"]
        if row.get("effect") is not None and row["effect"]>0
    ]
    if not family.get("estimable"):
        decision=interpretation_gate["decisions"]["non_estimable"]
    elif family["effect"]<=0:
        decision=interpretation_gate["decisions"]["nonpositive"]
    elif family["ci95_low"] is None or family["ci95_low"]<=0:
        decision=interpretation_gate["decisions"]["positive_but_ci_overlaps_zero"]
    elif len(positive_species)<int(
        interpretation_gate["authorize_decoupling_if"]["minimum_positive_species"]
    ):
        decision=interpretation_gate["decisions"]["positive_but_ci_overlaps_zero"]
    else:
        decision=interpretation_gate["decisions"]["pass"]
    return {
        "decision":decision,
        "positive_species":positive_species,
        "positive_species_count":len(positive_species),
        "family_effect_positive":(
            family.get("effect") is not None and family["effect"]>0
        ),
        "family_ci95_low_above_zero":(
            family.get("ci95_low") is not None and family["ci95_low"]>0
        ),
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


def run(
    *,
    token: str,
    output_dir: Path,
    estimability_gate: dict,
    interpretation_gate: dict,
) -> dict:
    if estimability_gate["gate"]["decision"] != (
        "authorize_sex_specific_recapture_displacement"
    ):
        raise RuntimeError("recapture estimability gate did not authorize effects")

    species_set=list(estimability_gate["gate"]["qualifying_species"])
    product=DEV._request_json(DEV.PRODUCT_URL,token=token)
    sites=sorted(DEV.collect_site_codes(product))
    taxonomy=DEV._request_json(DEV.TAXONOMY_URL,token=token)
    target_ids,_=DEV.target_taxa_from_taxonomy(taxonomy)

    rows=[]
    site_stops=[]
    query_count=0
    file_count=0
    byte_count=0

    for index,site in enumerate(sites,start=1):
        print(f"SEX_RECAP_EFFECT_SITE_START {index}/{len(sites)} {site}",flush=True)
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
                site_stops.append({"site_code":site,"status":"no_required_capture_tables"})
                continue

            registry_xy=DEV.location_registry_xy(site)
            coordinate_map=DEV.coordinate_map_for_site(trap_rows,registry_xy)
            if not coordinate_map:
                site_stops.append({"site_code":site,"status":"no_trap_coordinates"})
                continue

            site_rows=build_recapture_effect_rows(
                plot_rows,
                trap_rows,
                target_taxon_ids=target_ids,
                coordinate_map=coordinate_map,
                candidate_species=set(species_set),
            )
            rows.extend(site_rows)
            print(
                f"SEX_RECAP_EFFECT_SITE_DONE {site} rows={len(site_rows)}",
                flush=True,
            )
        except Exception as error:
            site_stops.append({
                "site_code":site,
                "status":"site_error",
                "detail":f"{type(error).__name__}: {error}",
            })
            print(
                f"SEX_RECAP_EFFECT_SITE_ERROR {site} "
                f"{type(error).__name__}: {error}",
                flush=True,
            )

    for species in species_set:
        expected=int(
            estimability_gate["species"][species]["paired_n3_events"]
        )
        observed=sum(
            row["species"]==species and row["paired_n3_eligible"]
            for row in rows
        )
        if observed!=expected:
            raise RuntimeError(
                f"{species} movement effect N>=3 events {observed} "
                f"!= estimability gate {expected}"
            )

    primary=movement_effect(rows,species_set=species_set,n_min=3)
    sensitivity_n2=movement_effect(rows,species_set=species_set,n_min=2)
    sensitivity_n5=movement_effect(rows,species_set=species_set,n_min=5)
    decision=manuscript_decision(primary,interpretation_gate)

    output_dir.mkdir(parents=True,exist_ok=True)
    _write_csv(
        output_dir/"heteromyid_sex_recapture_effect_events_v1.csv",
        rows,
    )

    result={
        "schema":"neon.public_mammal_sex_packing.recapture_effect.v1",
        "product_code":DEV.PRODUCT_CODE,
        "release":DEV.RELEASE,
        "qualifying_species":species_set,
        "primary":primary,
        "sensitivities":{
            "n_min_2_per_sex":sensitivity_n2,
            "n_min_5_per_sex":sensitivity_n5,
        },
        "manuscript_gate":decision,
        "phase3_primary_decision":"no_replicated_positive_support",
        "data_query_requests":query_count,
        "downloaded_required_file_count":file_count,
        "downloaded_required_bytes":byte_count,
        "site_stops":site_stops,
        "sex_specific_movement_magnitudes_inspected":True,
        "movement_effect_models_fit":1,
    }
    (output_dir/"heteromyid_sex_recapture_effect_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--estimability-gate",type=Path,required=True)
    parser.add_argument("--interpretation-gate",type=Path,required=True)
    args=parser.parse_args()

    token=os.environ.get("NEON_API_TOKEN","").strip()
    if not token:
        raise RuntimeError("NEON_API_TOKEN is required")

    result=run(
        token=token,
        output_dir=args.output_dir,
        estimability_gate=json.loads(args.estimability_gate.read_text()),
        interpretation_gate=json.loads(args.interpretation_gate.read_text()),
    )
    print(json.dumps({
        "primary":result["primary"],
        "manuscript_gate":result["manuscript_gate"],
    },indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
