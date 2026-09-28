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
    "unseen_estimability",
    "analysis/neon_unseen_heteromyid_highinfo_estimability_v1.py",
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
            displacements.append(float(math.hypot(float(rx)-float(lx),float(ry)-float(ly))))

        if not displacements:
            continue
        median_m=float(statistics.median(displacements))
        out.append({
            "tag_id":tag,
            "sex":sex,
            "night_count":len(ordered),
            "median_successive_displacement_m":median_m,
            "log1p_median_successive_displacement":math.log1p(median_m),
        })
    return out


def build_effect_rows(
    plot_rows: list[dict],
    trap_rows: list[dict],
    *,
    target_taxon_ids: set[str],
    coordinate_map: dict[str,tuple[float,float]],
    species_set: set[str],
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
        if site and plot and event and night:
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

        grouped=defaultdict(list)
        for row in event_rows:
            if not BASE.is_capture_status(str(row.get("trapStatus",""))):
                continue
            taxon=str(row.get("taxonID","")).strip()
            name=str(row.get("scientificName","")).strip()
            if taxon not in target_taxon_ids or name not in species_set:
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
            males=[r["log1p_median_successive_displacement"] for r in individuals if r["sex"]=="M"]
            females=[r["log1p_median_successive_displacement"] for r in individuals if r["sex"]=="F"]
            if len(males)<3 or len(females)<3:
                continue
            male=float(statistics.median(males))
            female=float(statistics.median(females))
            out.append({
                "site":site,
                "plot_id":plot,
                "event_id":event,
                "species":name,
                "taxon_id":taxon,
                "n_recapture_male":len(males),
                "n_recapture_female":len(females),
                "delta_movement":male-female,
                "paired_n3_eligible":len(males)>=3 and len(females)>=3,
                "paired_n5_eligible":len(males)>=5 and len(females)>=5,
            })
    return out


def _t_summary(values: list[float]) -> dict:
    values=[float(v) for v in values]
    n=len(values)
    if n==0:
        return {"n":0,"mean":None,"ci95_low":None,"ci95_high":None,"sd":None,"se":None,"df":None}
    mean=float(statistics.mean(values))
    if n<2:
        return {"n":n,"mean":mean,"ci95_low":None,"ci95_high":None,"sd":None,"se":None,"df":0}
    sd=float(statistics.stdev(values))
    se=sd/math.sqrt(n)
    df=n-1
    c=float(student_t.ppf(0.975,df))
    return {"n":n,"mean":mean,"ci95_low":mean-c*se,"ci95_high":mean+c*se,"sd":sd,"se":se,"df":df}


def movement_effect(rows: list[dict], *, species_set: list[str], n_min: int) -> dict:
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
            by_site[row["site"]].append(float(row["delta_movement"]))
        site_means={site:float(statistics.mean(vals)) for site,vals in sorted(by_site.items())}
        values=list(site_means.values())
        effect=float(statistics.mean(values)) if values else None
        ci=_t_summary(values)
        species_results.append({
            "species":species,
            "event_count":len(srows),
            "site_count":len(site_means),
            "site_means":site_means,
            "effect":effect,
            "ci95_low":ci["ci95_low"],
            "ci95_high":ci["ci95_high"],
        })

    effects=[row["effect"] for row in species_results if row["effect"] is not None]
    complete=len(effects)==len(species_set)
    family=_t_summary(effects if complete else [])
    positive=[row["species"] for row in species_results if row["effect"] is not None and row["effect"]>0]
    required_positive=math.ceil((2/3)*len(species_set))
    passed=(
        complete
        and family["mean"] is not None
        and family["mean"]>0
        and family["ci95_low"] is not None
        and family["ci95_low"]>0
        and len(positive)>=required_positive
    )
    return {
        "n_min_per_sex":n_min,
        "species":species_results,
        "family":{
            "effect":family["mean"],
            "ci95_low":family["ci95_low"],
            "ci95_high":family["ci95_high"],
            "species_count":family["n"],
            "df":family["df"],
        },
        "positive_species":positive,
        "required_positive_species":required_positive,
        "decision":(
            "replicated_highinfo_positive_support"
            if passed else
            "no_replicated_highinfo_positive_support"
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


def run(*, token: str, output_dir: Path, gate: dict) -> dict:
    if gate["gate"]["decision"]!="authorize_unseen_species_movement_effects":
        raise RuntimeError("estimability gate did not authorize validation effects")

    species_set=sorted(gate["gate"]["qualifying_species"])
    sites=sorted({
        site
        for species in species_set
        for site in gate["species"][species]["n3_sites"]
    })

    product=DEV._request_json(DEV.PRODUCT_URL,token=token)
    available=sorted(DEV.collect_site_codes(product))
    unknown=sorted(set(sites)-set(available))
    if unknown:
        raise RuntimeError(f"gate sites absent from release: {unknown}")
    taxonomy=DEV._request_json(DEV.TAXONOMY_URL,token=token)
    target_ids,_=DEV.target_taxa_from_taxonomy(taxonomy)

    rows=[]
    stops=[]
    for index,site in enumerate(sites,start=1):
        print(f"UNSEEN_HET_EFFECT_SITE_START {index}/{len(sites)} {site}",flush=True)
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
            files=DEV.select_required_files(payload,release=DEV.RELEASE)
            table_rows={table:[] for table in DEV.REQUIRED_TABLES}
            for file_row in files:
                records,_=DEV._download_csv(file_row,token=token)
                table_rows[file_row["table"]].extend(records)

            trap_rows=table_rows["mam_pertrapnight"]
            plot_rows=table_rows["mam_perplotnight"]
            registry_xy=DEV.location_registry_xy(site)
            coordinate_map=DEV.coordinate_map_for_site(trap_rows,registry_xy)
            rows.extend(build_effect_rows(
                plot_rows,trap_rows,
                target_taxon_ids=target_ids,
                coordinate_map=coordinate_map,
                species_set=set(species_set),
            ))
        except Exception as error:
            stops.append({"site_code":site,"status":"site_error","detail":f"{type(error).__name__}: {error}"})

    for species in species_set:
        expected5=int(gate["species"][species]["paired_n5_events"])
        observed5=sum(r["species"]==species and r["paired_n5_eligible"] for r in rows)
        expected3=int(gate["species"][species]["paired_n3_events"])
        observed3=sum(r["species"]==species and r["paired_n3_eligible"] for r in rows)
        if observed5!=expected5 or observed3!=expected3:
            raise RuntimeError(
                f"{species}: effect counts n5={observed5}/{expected5}, n3={observed3}/{expected3}"
            )

    primary=movement_effect(rows,species_set=species_set,n_min=5)
    sensitivity=movement_effect(rows,species_set=species_set,n_min=3)
    result={
        "schema":"neon.heteromyid_high_information_movement_validation.effect.v1",
        "qualifying_species":species_set,
        "effect_sites":sites,
        "primary":primary,
        "sensitivity_n3":sensitivity,
        "sensitivity_can_rescue_primary":False,
        "validation_species_movement_magnitudes_inspected":True,
        "movement_effect_models_fit":1,
        "site_stops":stops,
    }
    output_dir.mkdir(parents=True,exist_ok=True)
    _write_csv(output_dir/"unseen_heteromyid_highinfo_effect_events_v1.csv",rows)
    (output_dir/"unseen_heteromyid_highinfo_effect_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    return result


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--gate",type=Path,required=True)
    args=parser.parse_args()
    token=os.environ.get("NEON_API_TOKEN","").strip()
    if not token:
        raise RuntimeError("NEON_API_TOKEN is required")
    result=run(token=token,output_dir=args.output_dir,gate=json.loads(args.gate.read_text()))
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
