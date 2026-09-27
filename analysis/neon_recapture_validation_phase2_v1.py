from __future__ import annotations

import hashlib
import importlib.util
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]


def _load_module(name: str, path: Path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILDER=_load_module(
    "neon_sessions",
    ROOT/"analysis"/"build_neon_space_use_sessions_v1.py",
)
PACKING=_load_module(
    "mammal_spatial_packing",
    ROOT/"analysis"/"mammal_spatial_packing_v1.py",
)
UTILS=_load_module(
    "phase2_utils",
    ROOT/"analysis"/"public_mammal_phase2_utils_v1.py",
)


def successive_displacements(
    points: Iterable[tuple[str,str,float,float]],
) -> list[float]:
    rows=sorted(
        [(str(date),str(night),float(x),float(y)) for date,night,x,y in points],
        key=lambda row:(row[0],row[1]),
    )
    by_night={}
    for row in rows:
        by_night.setdefault(row[1],row)
    ordered=sorted(by_night.values(),key=lambda row:(row[0],row[1]))
    out=[]
    for left,right in zip(ordered,ordered[1:]):
        dx=right[2]-left[2]
        dy=right[3]-left[3]
        out.append(float((dx*dx+dy*dy)**0.5))
    return out


def individual_movement_summaries(
    rows: Iterable[dict],
    coordinate_map: dict[str,tuple[float,float]],
) -> dict[str,float]:
    grouped=defaultdict(list)
    for raw in rows:
        row=dict(raw)
        tag=str(row.get("tagID","")).strip()
        night=str(row.get("nightuid","")).strip()
        date=str(row.get("collectDate","")).strip()
        node=str(row.get("node","")).strip()
        if not tag or not night or not node or node not in coordinate_map:
            continue
        x,y=coordinate_map[node]
        grouped[tag].append((date,night,float(x),float(y),node))

    out={}
    for tag,obs in grouped.items():
        nights={row[1] for row in obs}
        nodes={row[4] for row in obs}
        if len(nights)<2 or len(nodes)<2:
            continue
        displacements=successive_displacements([
            (date,night,x,y) for date,night,x,y,_ in obs
        ])
        if not displacements or max(displacements)<=0:
            continue
        out[tag]=float(statistics.median(displacements))
    return out


def event_movement_summary(
    rows: Iterable[dict],
    coordinate_map: dict[str,tuple[float,float]],
    *,
    min_moving_individuals: int,
) -> dict:
    individual=individual_movement_summaries(rows,coordinate_map)
    values=list(individual.values())
    if len(values)<int(min_moving_individuals):
        return {
            "estimable":False,
            "moving_individual_count":len(values),
            "median_individual_displacement_m":None,
            "individual_median_displacements_m":individual,
            "non_estimable_reason":"too_few_moving_individuals",
        }
    return {
        "estimable":True,
        "moving_individual_count":len(values),
        "median_individual_displacement_m":float(statistics.median(values)),
        "individual_median_displacements_m":individual,
        "non_estimable_reason":None,
    }


def _node_id(row: dict) -> str:
    return (
        f"{str(row.get('namedLocation','')).strip()}."
        f"{str(row.get('trapCoordinate','')).strip()}"
    )


def _packing_seed(
    taxon_id: str,
    scientific_name: str,
    nightuid: str,
    n: int,
) -> int:
    text=f"pathogen-first-night|{taxon_id}|{scientific_name}|{nightuid}|{n}"
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16],16)


def first_night_population_packing(
    event_rows: Iterable[dict],
    coordinate_map: dict[str,tuple[float,float]],
    *,
    taxon_id: str,
    scientific_name: str,
    replicates: int,
) -> dict:
    rows=[dict(row) for row in event_rows]
    night_keys=sorted({
        (str(row.get("collectDate","")).strip(),str(row.get("nightuid","")).strip())
        for row in rows
        if str(row.get("nightuid","")).strip()
    })
    if not night_keys:
        return {
            "first_night":None,
            "n_unique_individuals":0,
            "packing_z":None,
            "packing_estimable":False,
            "non_estimable_reason":"no_event_night",
        }
    first_date,first_night=night_keys[0]
    first=[row for row in rows if str(row.get("nightuid","")).strip()==first_night]

    active_nodes=[]
    seen_active=set()
    for row in first:
        if not BUILDER.is_usable_active_trap(str(row.get("trapStatus",""))):
            continue
        node=_node_id(row)
        if node not in coordinate_map or node in seen_active:
            continue
        seen_active.add(node)
        active_nodes.append(node)

    by_tag={}
    for row in first:
        if not BUILDER.is_capture_status(str(row.get("trapStatus",""))):
            continue
        if str(row.get("taxonID","")).strip()!=str(taxon_id):
            continue
        if str(row.get("scientificName","")).strip()!=str(scientific_name):
            continue
        if str(row.get("taxonRank","")).strip().lower()!="species":
            continue
        if str(row.get("identificationQualifier","")).strip():
            continue
        tag=str(row.get("tagID","")).strip()
        node=_node_id(row)
        if not tag or node not in coordinate_map:
            continue
        by_tag.setdefault(tag,node)

    observed_nodes=list(by_tag.values())
    n=len(observed_nodes)
    if n<2 or len(active_nodes)<n:
        return {
            "first_night":first_night,
            "first_date":first_date,
            "n_unique_individuals":n,
            "active_trap_count":len(active_nodes),
            "packing_z":None,
            "packing_estimable":False,
            "validation_n5_eligible":False,
            "non_estimable_reason":"insufficient_first_night_geometry",
        }

    observed=np.asarray([coordinate_map[node] for node in observed_nodes],dtype=float)
    active=np.asarray([coordinate_map[node] for node in active_nodes],dtype=float)
    score=PACKING.packing_score(
        observed,
        active,
        replicates=replicates,
        seed=_packing_seed(str(taxon_id),str(scientific_name),first_night,n),
    )
    return {
        "first_night":first_night,
        "first_date":first_date,
        "n_unique_individuals":n,
        "active_trap_count":len(active_nodes),
        "packing_z":score["packing_z"],
        "packing_estimable":bool(score["estimable"]),
        "validation_n5_eligible":bool(score["estimable"]) and n>=5,
        "non_estimable_reason":score["non_estimable_reason"],
    }




def _is_valid_pathogen_plotnight(row: dict) -> bool:
    method=str(
        row.get("mammalGridSamplingMethod",row.get("mammalGridSamplingType",""))
    ).strip().lower()
    completion=str(row.get("gridCompletion","")).strip().lower()
    impractical=str(row.get("samplingImpractical","")).strip()
    return (
        method=="pathogen"
        and completion==BUILDER.COMPLETE_GRID
        and impractical in {"","OK"}
    )


def build_pathogen_validation_rows(
    plot_rows: Iterable[dict],
    trap_rows: Iterable[dict],
    *,
    target_taxon_ids: set[str],
    coordinate_map: dict[str,tuple[float,float]],
    replicates: int,
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

    output=[]
    for (site,plot,event),night_map in sorted(event_nights.items()):
        if len(night_map)<2:
            continue
        event_rows=[]
        for night in sorted(night_map,key=lambda n:(night_map[n],n)):
            event_rows.extend(traps_by_night.get(night,[]))
        if not event_rows:
            continue

        taxon_pairs=sorted({
            (
                str(row.get("taxonID","")).strip(),
                str(row.get("scientificName","")).strip(),
            )
            for row in event_rows
            if BUILDER.is_capture_status(str(row.get("trapStatus","")))
            and str(row.get("taxonID","")).strip() in target_taxon_ids
            and str(row.get("taxonRank","")).strip().lower()=="species"
            and not str(row.get("identificationQualifier","")).strip()
            and str(row.get("tagID","")).strip()
            and str(row.get("scientificName","")).strip()
        })

        for taxon,name in taxon_pairs:
            movement_rows=[]
            for row in event_rows:
                if not BUILDER.is_capture_status(str(row.get("trapStatus",""))):
                    continue
                if str(row.get("taxonID","")).strip()!=taxon:
                    continue
                if str(row.get("scientificName","")).strip()!=name:
                    continue
                if str(row.get("taxonRank","")).strip().lower()!="species":
                    continue
                if str(row.get("identificationQualifier","")).strip():
                    continue
                tag=str(row.get("tagID","")).strip()
                node=_node_id(row)
                if not tag or node not in coordinate_map:
                    continue
                movement_rows.append({
                    "tagID":tag,
                    "collectDate":str(row.get("collectDate","")).strip(),
                    "nightuid":str(row.get("nightuid","")).strip(),
                    "node":node,
                })

            movement=event_movement_summary(
                movement_rows,
                coordinate_map,
                min_moving_individuals=3,
            )
            if not movement["estimable"]:
                continue

            packing=first_night_population_packing(
                event_rows,
                coordinate_map,
                taxon_id=taxon,
                scientific_name=name,
                replicates=replicates,
            )
            if not packing.get("validation_n5_eligible",False):
                continue

            first_date=str(packing.get("first_date",""))
            year=int(first_date[:4]) if len(first_date)>=4 and first_date[:4].isdigit() else None
            output.append({
                "site":site,
                "plot_id":plot,
                "event_id":event,
                "year":year,
                "taxon_id":taxon,
                "species":name,
                "first_night":packing["first_night"],
                "n_unique_individuals":packing["n_unique_individuals"],
                "active_trap_count":packing["active_trap_count"],
                "packing_z":packing["packing_z"],
                "moving_individual_count":movement["moving_individual_count"],
                "median_individual_displacement_m":movement["median_individual_displacement_m"],
            })
    return output


def prepare_validation_frame(
    rows: Iterable[dict],
    *,
    min_events_per_stratum: int,
) -> pd.DataFrame:
    clean=[]
    for raw in rows:
        row=dict(raw)
        try:
            packing=float(row.get("packing_z"))
            n=int(row.get("n_unique_individuals"))
            movement=float(row.get("median_individual_displacement_m"))
            movers=int(row.get("moving_individual_count"))
        except (TypeError,ValueError):
            continue
        if not np.isfinite(packing) or not np.isfinite(movement):
            continue
        if n<5 or movers<3 or movement<0:
            continue
        species=str(row.get("species","")).strip()
        site=str(row.get("site","")).strip()
        event=str(row.get("event_id","")).strip()
        if not species or not site or not event:
            continue
        clean.append({
            "species":species,
            "site":site,
            "species_site":f"{species}|{site}",
            "event_id":event,
            "packing_z":packing,
            "n_unique_individuals":n,
            "median_individual_displacement_m":movement,
            "moving_individual_count":movers,
            "log1p_movement":float(np.log1p(movement)),
        })
    df=pd.DataFrame(clean)
    if df.empty:
        raise ValueError("no recapture validation rows remain")
    counts=df["species_site"].value_counts()
    keep=set(counts[counts>=int(min_events_per_stratum)].index)
    df=df.loc[df["species_site"].isin(keep)].copy()
    if df.empty:
        raise ValueError("no species-site strata meet the event replication gate")
    df["z_logN"]=UTILS.z_log_n(df["n_unique_individuals"].to_numpy())
    return df.sort_values(["species_site","event_id"]).reset_index(drop=True)


def fit_validation_model(df: pd.DataFrame):
    model=smf.ols(
        "log1p_movement ~ packing_z + z_logN + C(species_site)",
        data=df,
    )
    UTILS.assert_full_rank(model.exog,model.exog_names)
    return model.fit(cov_type="HC3")
