from __future__ import annotations

import importlib.util
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def _load(name: str, rel: str):
    path=ROOT/rel
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE=_load("build_neon_space_v1","analysis/build_neon_space_use_sessions_v1.py")
SEXHELP=_load("sex_estimability_v1","analysis/mammal_sex_packing_estimability_v1.py")
SUPPORT=_load("sex_support_v2","analysis/mammal_sex_trap_support_v2.py")
EFFECT=_load("sex_effect_phase3","analysis/mammal_sex_effects_phase3_v1.py")


def build_neon_sex_effect_sessions(
    plot_rows: Iterable[dict],
    trap_rows: Iterable[dict],
    *,
    target_taxon_ids: set[str],
    coordinate_map: dict[str,tuple[float,float]],
) -> list[dict]:
    plots=[dict(row) for row in plot_rows]
    traps=[dict(row) for row in trap_rows]

    expected_coords: dict[str,set[str]]=defaultdict(set)
    for row in traps:
        plot=str(row.get("plotID","")).strip()
        coord=str(row.get("trapCoordinate","")).strip()
        if plot and BASE._valid_trap_coordinate(coord):
            expected_coords[plot].add(coord)

    by_event: dict[tuple[str,str,str],list[dict]]=defaultdict(list)
    for row in plots:
        key=(
            str(row.get("siteID","")).strip(),
            str(row.get("plotID","")).strip(),
            str(row.get("eventID","")).strip(),
        )
        if all(key):
            by_event[key].append(row)

    traps_by_night: dict[str,list[dict]]=defaultdict(list)
    for row in traps:
        night=str(row.get("nightuid","")).strip()
        if night:
            traps_by_night[night].append(row)

    out=[]
    for (site,plot,event),event_rows in sorted(by_event.items()):
        if len(event_rows)!=1:
            continue
        p=event_rows[0]
        if not BASE.is_primary_plotnight(p):
            continue
        night=str(p.get("nightuid","")).strip()
        if not night:
            continue
        session=traps_by_night.get(night,[])
        if not session:
            continue

        active_by_coord={}
        for row in session:
            coord=str(row.get("trapCoordinate","")).strip()
            if not BASE._valid_trap_coordinate(coord):
                continue
            if not BASE.is_usable_active_trap(str(row.get("trapStatus",""))):
                continue
            node=BASE._node_id(row)
            if node not in coordinate_map:
                continue
            active_by_coord.setdefault(coord,row)

        expected_count=len(expected_coords.get(plot,set()))
        required_active=min(90,expected_count) if expected_count else 90
        if len(active_by_coord)<required_active:
            continue

        active_nodes=[
            BASE._node_id(row)
            for _,row in sorted(active_by_coord.items())
        ]
        active_xy=np.asarray(
            [coordinate_map[node] for node in active_nodes],
            dtype=float,
        )

        grouped: dict[tuple[str,str],list[dict]]=defaultdict(list)
        for row in session:
            if not BASE.is_capture_status(str(row.get("trapStatus",""))):
                continue
            taxon=str(row.get("taxonID","")).strip()
            name=str(row.get("scientificName","")).strip()
            if taxon not in target_taxon_ids:
                continue
            if str(row.get("taxonRank","")).strip().lower()!="species":
                continue
            if str(row.get("identificationQualifier","")).strip():
                continue
            if not SEXHELP.is_heteromyid(name):
                continue
            if not str(row.get("tagID","")).strip():
                continue
            copy=dict(row)
            coord=str(row.get("trapCoordinate","")).strip()
            copy["_support_location"]=(
                coord
                if BASE._valid_trap_coordinate(coord)
                and coord in active_by_coord
                and BASE._node_id(row) in coordinate_map
                else ""
            )
            grouped[(taxon,name)].append(copy)

        date=str(p.get("collectDate","")).strip()
        year=int(date[:4]) if len(date)>=4 and date[:4].isdigit() else None
        month=int(date[5:7]) if len(date)>=7 and date[5:7].isdigit() else None

        for (taxon,name),captures in sorted(grouped.items()):
            ordered=sorted(captures,key=lambda row:str(row.get("uid","")))
            by_tag={}
            for row in ordered:
                tag=str(row.get("tagID","")).strip()
                by_tag.setdefault(tag,row)
            retained=list(by_tag.values())

            support=SUPPORT.trap_support_record(
                ordered,
                id_field="tagID",
                location_field="_support_location",
                sex_field="sex",
            )
            if not support["trap_support_valid"]:
                continue

            males=[
                row for row in retained
                if SEXHELP.normalize_sex(row.get("sex"))=="M"
            ]
            females=[
                row for row in retained
                if SEXHELP.normalize_sex(row.get("sex"))=="F"
            ]
            if len(males)<2 or len(females)<2:
                continue

            male_xy=np.asarray(
                [coordinate_map[BASE._node_id(row)] for row in males],
                dtype=float,
            )
            female_xy=np.asarray(
                [coordinate_map[BASE._node_id(row)] for row in females],
                dtype=float,
            )
            effect=EFFECT.sex_packing_effect(active_xy,male_xy,female_xy)
            if not effect["estimable"]:
                continue

            flags=EFFECT.threshold_flags(len(males),len(females))
            out.append({
                "source":"NEON",
                "site":site,
                "plot_id":plot,
                "event_id":event,
                "nightuid":night,
                "collect_date":date,
                "year":year,
                "month":month,
                "taxon_id":taxon,
                "species":name,
                "active_trap_count":len(active_by_coord),
                "expected_design_trap_count":expected_count,
                "n_total":support["n_total"],
                "n_known_sex":support["n_known_sex"],
                "n_unknown_sex":support["n_unknown_sex"],
                "known_sex_fraction":support["known_sex_fraction"],
                **flags,
                **effect,
            })
    return out


def summarize(rows: list[dict]) -> dict:
    return {
        "schema":"neon.public_mammal_sex_packing.neon_effect_sessions.v1",
        "product_code":"DP1.10072.001",
        "release":"RELEASE-2026",
        "session_count":len(rows),
        "paired_n2_sessions":sum(bool(r["paired_n2_eligible"]) for r in rows),
        "paired_n3_sessions":sum(bool(r["paired_n3_eligible"]) for r in rows),
        "paired_n5_sessions":sum(bool(r["paired_n5_eligible"]) for r in rows),
        "site_count":len({r["site"] for r in rows}),
        "species_count":len({r["species"] for r in rows}),
        "ecological_effects_extracted":True,
        "ecological_model_fits":0,
    }
