from __future__ import annotations

import importlib.util
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from analysis import mammal_sex_trap_support_v2 as SUPPORT

ROOT=Path(__file__).resolve().parents[1]


def _load_module(name: str, path: Path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE=_load_module(
    "build_neon_space_use_sessions_v1",
    ROOT/"analysis"/"build_neon_space_use_sessions_v1.py",
)
SEXHELP=_load_module(
    "mammal_sex_packing_estimability_v1",
    ROOT/"analysis"/"mammal_sex_packing_estimability_v1.py",
)


def build_neon_support_sessions(
    plot_rows: Iterable[dict],
    trap_rows: Iterable[dict],
    *,
    target_taxon_ids: set[str],
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

    results=[]
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

        active_coords={
            str(row.get("trapCoordinate","")).strip()
            for row in session
            if BASE._valid_trap_coordinate(row.get("trapCoordinate"))
            and BASE.is_usable_active_trap(str(row.get("trapStatus","")))
        }
        expected_count=len(expected_coords.get(plot,set()))
        required_active=min(90,expected_count) if expected_count else 90
        if len(active_coords)<required_active:
            continue

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
                if BASE._valid_trap_coordinate(coord) and coord in active_coords
                else ""
            )
            grouped[(taxon,name)].append(copy)

        date=str(p.get("collectDate","")).strip()
        year=int(date[:4]) if len(date)>=4 and date[:4].isdigit() else None
        for (taxon,name),captures in sorted(grouped.items()):
            ordered=sorted(captures,key=lambda row:str(row.get("uid","")))
            support=SUPPORT.trap_support_record(
                ordered,
                id_field="tagID",
                location_field="_support_location",
                sex_field="sex",
            )
            results.append({
                "source":"NEON",
                "site":site,
                "plot_id":plot,
                "event_id":event,
                "nightuid":night,
                "collect_date":date,
                "year":year,
                "taxon_id":taxon,
                "species":name,
                "active_trap_count":len(active_coords),
                "expected_design_trap_count":expected_count,
                **support,
            })
    return results


def summarize(rows: list[dict]) -> dict:
    out=SUPPORT.summarize_support_sessions(rows,source="NEON")
    out.update({
        "schema":"neon.public_mammal_sex_packing.neon_trap_support.v2",
        "product_code":"DP1.10072.001",
        "release":"RELEASE-2026",
        "inferential_status":"retrospective_public_data_support_estimability",
        "support_rule":"first retained record per individual; retained capture trap must be active and all retained locations must be unique within session",
    })
    return out
