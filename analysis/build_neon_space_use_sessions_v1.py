from __future__ import annotations

import hashlib
import importlib.util
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
COMPLETE_GRID="setting complete, processing complete"
CRYPTIC_COMPLEX={
    "Peromyscus maniculatus",
    "Peromyscus leucopus",
}


def _load_packing_module():
    path=ROOT/"analysis"/"mammal_spatial_packing_v1.py"
    spec=importlib.util.spec_from_file_location("mammal_spatial_packing_v1",path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PACKING=_load_packing_module()


def is_primary_plotnight(row: dict) -> bool:
    method=str(
        row.get("mammalGridSamplingMethod",row.get("mammalGridSamplingType",""))
    ).strip().lower()
    completion=str(row.get("gridCompletion","")).strip().lower()
    impractical=str(row.get("samplingImpractical","")).strip()
    return (
        method=="diversity"
        and completion==COMPLETE_GRID
        and impractical in {"","OK"}
    )


def is_usable_active_trap(status: str) -> bool:
    value=str(status).strip()
    return value.startswith("4 -") or value.startswith("5 -") or value.startswith("6 -")


def is_capture_status(status: str) -> bool:
    value=str(status).strip()
    return value.startswith("4 -") or value.startswith("5 -")


def _valid_trap_coordinate(value: object) -> bool:
    coord=str(value).strip().upper()
    if not coord or "X" in coord:
        return False
    return len(coord)>=2 and coord[0].isalpha() and coord[1:].isdigit()


def _node_id(row: dict) -> str:
    return f"{str(row.get('namedLocation','')).strip()}.{str(row.get('trapCoordinate','')).strip()}"


def coordinate_map_from_trap_rows(rows: Iterable[dict]) -> dict[str, tuple[float,float]]:
    by_plot_node: dict[str,dict[str,list[tuple[float,float]]]]=defaultdict(lambda: defaultdict(list))
    for raw in rows:
        row=dict(raw)
        plot=str(row.get("plotID","")).strip()
        node=_node_id(row)
        coord=str(row.get("trapCoordinate","")).strip()
        if not plot or not node or not _valid_trap_coordinate(coord):
            continue
        try:
            lat=float(row.get("decimalLatitude"))
            lon=float(row.get("decimalLongitude"))
        except (TypeError,ValueError):
            continue
        if not math.isfinite(lat) or not math.isfinite(lon):
            continue
        by_plot_node[plot][node].append((lat,lon))

    result: dict[str,tuple[float,float]]={}
    earth_radius_m=6371008.8
    for plot in sorted(by_plot_node):
        nodes=by_plot_node[plot]
        if not nodes:
            continue
        canonical={
            node:(
                statistics.median(v[0] for v in values),
                statistics.median(v[1] for v in values),
            )
            for node,values in nodes.items()
        }
        origin_node=sorted(canonical)[0]
        lat0,lon0=canonical[origin_node]
        lat0_rad=math.radians(lat0)
        for node,(lat,lon) in canonical.items():
            x=earth_radius_m*math.cos(lat0_rad)*math.radians(lon-lon0)
            y=earth_radius_m*math.radians(lat-lat0)
            result[node]=(x,y)
    return result


def summarize_neon_sessions(sessions: Iterable[dict]) -> dict:
    rows=[dict(row) for row in sessions]
    species_habitat: dict[str,Counter]=defaultdict(Counter)
    for row in rows:
        species_habitat[str(row.get("species",""))][str(row.get("nlcd_class",""))]+=1
    active=[int(row["active_trap_count"]) for row in rows if row.get("active_trap_count") not in (None,"")]
    years=[int(row["year"]) for row in rows if row.get("year") not in (None,"")]
    return {
        "schema":"neon.public_mammal_space_use.neon_inventory.v1",
        "session_count":len(rows),
        "site_count":len({str(row.get("site","")) for row in rows if str(row.get("site",""))}),
        "plot_count":len({str(row.get("plot_id","")) for row in rows if str(row.get("plot_id",""))}),
        "event_count":len({str(row.get("event_id","")) for row in rows if str(row.get("event_id",""))}),
        "species_count":len({str(row.get("species","")) for row in rows if str(row.get("species",""))}),
        "eligible_n3":sum(bool(row.get("sensitivity_n3_eligible")) for row in rows),
        "eligible_n5":sum(bool(row.get("primary_n5_eligible")) for row in rows),
        "eligible_n8":sum(bool(row.get("sensitivity_n8_eligible")) for row in rows),
        "packing_estimable_count":sum(bool(row.get("packing_estimable")) for row in rows),
        "cryptic_complex_session_count":sum(bool(row.get("cryptic_complex_sensitivity")) for row in rows),
        "uncertain_capture_rows_excluded":sum(int(row.get("uncertain_capture_rows_excluded",0) or 0) for row in rows),
        "history_linked_capture_count":sum(int(row.get("history_linked_capture_count",0) or 0) for row in rows),
        "active_trap_count_range":[min(active),max(active)] if active else None,
        "year_range":[min(years),max(years)] if years else None,
        "species_habitat_session_counts":{
            species:dict(sorted(counts.items()))
            for species,counts in sorted(species_habitat.items())
        },
        "ecological_model_fits":0,
    }


def _geometry_fingerprint(points: np.ndarray) -> str:
    ordered=sorted((float(x),float(y)) for x,y in np.asarray(points,dtype=float))
    return hashlib.sha256(repr(ordered).encode("utf-8")).hexdigest()


def _seed(geometry_fp: str, n: int) -> int:
    text=f"neon-public-mammal-packing|{geometry_fp}|{n}"
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16],16)


def _mode(values: list[str]) -> str:
    clean=[v for v in values if v]
    if not clean:
        return ""
    counts=Counter(clean)
    return sorted(counts,key=lambda x:(-counts[x],x))[0]


def build_neon_sessions(
    plot_rows: Iterable[dict],
    trap_rows: Iterable[dict],
    *,
    target_taxon_ids: set[str],
    coordinate_map: dict[str, tuple[float,float]],
    history_rows: Iterable[dict],
    replicates: int=999,
) -> list[dict]:
    plots=[dict(row) for row in plot_rows]
    traps=[dict(row) for row in trap_rows]
    history_ids={
        str(row.get("identificationHistoryID","")).strip()
        for row in history_rows
        if str(row.get("identificationHistoryID","")).strip()
    }

    expected_coords: dict[str,set[str]]=defaultdict(set)
    for row in traps:
        plot=str(row.get("plotID","")).strip()
        coord=str(row.get("trapCoordinate","")).strip()
        if plot and _valid_trap_coordinate(coord):
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
        # Primary diversity analysis requires exactly one trapping night in the bout.
        if len(event_rows)!=1:
            continue
        p=event_rows[0]
        if not is_primary_plotnight(p):
            continue
        night=str(p.get("nightuid","")).strip()
        if not night:
            continue
        session_traps=traps_by_night.get(night,[])
        if not session_traps:
            continue

        active_by_coord={}
        for row in session_traps:
            coord=str(row.get("trapCoordinate","")).strip()
            if not _valid_trap_coordinate(coord):
                continue
            if not is_usable_active_trap(str(row.get("trapStatus",""))):
                continue
            node=_node_id(row)
            if node not in coordinate_map:
                continue
            active_by_coord.setdefault(coord,row)

        expected_count=len(expected_coords.get(plot,set()))
        required_active=min(90,expected_count) if expected_count else 90
        if len(active_by_coord) < required_active:
            continue

        active_nodes=[
            _node_id(row)
            for _,row in sorted(active_by_coord.items())
        ]
        active_xy=np.asarray([coordinate_map[node] for node in active_nodes],dtype=float)
        geometry_fp=_geometry_fingerprint(active_xy)

        eligible_raw=[]
        uncertain_by_taxon_name=Counter()
        for row in session_traps:
            if not is_capture_status(str(row.get("trapStatus",""))):
                continue
            taxon=str(row.get("taxonID","")).strip()
            name=str(row.get("scientificName","")).strip()
            if taxon not in target_taxon_ids:
                continue
            if str(row.get("taxonRank","")).strip().lower()!="species":
                continue
            qualifier=str(row.get("identificationQualifier","")).strip()
            if qualifier:
                uncertain_by_taxon_name[(taxon,name)]+=1
                continue
            tag=str(row.get("tagID","")).strip()
            if not tag:
                continue
            node=_node_id(row)
            if node not in coordinate_map:
                continue
            eligible_raw.append(row)

        grouped: dict[tuple[str,str],list[dict]]=defaultdict(list)
        for row in eligible_raw:
            key=(str(row["taxonID"]).strip(),str(row["scientificName"]).strip())
            grouped[key].append(row)

        for (taxon,name),rows in sorted(grouped.items()):
            by_tag={}
            for row in sorted(rows,key=lambda x:str(x.get("uid",""))):
                tag=str(row.get("tagID","")).strip()
                by_tag.setdefault(tag,row)
            retained=list(by_tag.values())
            n=len(retained)
            observed=np.asarray(
                [coordinate_map[_node_id(row)] for row in retained],
                dtype=float,
            )
            score=PACKING.packing_score(
                observed,
                active_xy,
                replicates=replicates,
                seed=_seed(geometry_fp,n),
            )
            nlcd=_mode([
                str(row.get("nlcdClass","")).strip()
                for row in session_traps
            ])
            history_linked=sum(
                bool(str(row.get("identificationHistoryID","")).strip())
                and str(row.get("identificationHistoryID","")).strip() in history_ids
                for row in retained
            )
            date=str(p.get("collectDate","")).strip()
            year=int(date[:4]) if len(date)>=4 and date[:4].isdigit() else None
            estimable=bool(score["estimable"])
            results.append({
                "source":"NEON",
                "site":site,
                "plot_id":plot,
                "event_id":event,
                "nightuid":night,
                "collect_date":date,
                "year":year,
                "mammal_grid_sampling_method":"diversity",
                "grid_completion":str(p.get("gridCompletion","")).strip(),
                "nlcd_class":nlcd,
                "taxon_id":taxon,
                "species":name,
                "n_unique_individuals":n,
                "active_trap_count":len(active_by_coord),
                "expected_design_trap_count":expected_count,
                "uncertain_capture_rows_excluded":uncertain_by_taxon_name[(taxon,name)],
                "history_linked_capture_count":history_linked,
                "cryptic_complex_sensitivity":name in CRYPTIC_COMPLEX,
                "mpd_observed_m":score["mpd_observed"],
                "mpd_null_mean_m":score["mpd_null_mean"],
                "mpd_null_sd_m":score["mpd_null_sd"],
                "packing_z":score["packing_z"],
                "packing_estimable":estimable,
                "packing_non_estimable_reason":score["non_estimable_reason"],
                "null_mode":score["null_mode"],
                "null_draw_count":score["null_draw_count"],
                "sensitivity_n3_eligible":estimable and n>=3,
                "primary_n5_eligible":estimable and n>=5,
                "sensitivity_n8_eligible":estimable and n>=8,
            })
    return results
