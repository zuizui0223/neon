from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def _load_packing_module():
    path=ROOT/"analysis"/"mammal_spatial_packing_v1.py"
    spec=importlib.util.spec_from_file_location("mammal_spatial_packing_v1",path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PACKING=_load_packing_module()
VALID_STAKES=tuple(f"{row}{col}" for row in range(1,8) for col in range(1,8))
ACTIVE_TRAPS_XY=np.asarray(
    [((col-1)*6.25,(row-1)*6.25) for row in range(1,8) for col in range(1,8)],
    dtype=float,
)


def stake_xy(stake: str) -> tuple[float,float]:
    value=str(stake).strip()
    if len(value)!=2 or value not in VALID_STAKES:
        raise ValueError(f"invalid Portal primary stake: {stake!r}")
    row=int(value[0])
    col=int(value[1])
    return ((col-1)*6.25,(row-1)*6.25)


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"1","true","t","yes","y"}


def _target_species_lookup(species_rows: Iterable[dict]) -> dict[str,str]:
    out={}
    for row in species_rows:
        if str(row.get("rodent","")).strip()!="1":
            continue
        if str(row.get("censustarget","")).strip()!="1":
            continue
        if str(row.get("unidentified","")).strip()=="1":
            continue
        code=str(row.get("speciescode","")).strip()
        name=str(row.get("scientificname","")).strip()
        if code and name:
            out[code]=name
    return out


def filter_primary_capture_rows(
    capture_rows: Iterable[dict],
    species_rows: Iterable[dict],
) -> list[dict]:
    targets=_target_species_lookup(species_rows)
    out=[]
    for row in capture_rows:
        try:
            period=int(str(row.get("period","")).strip())
        except ValueError:
            continue
        if period <= 0:
            continue
        if str(row.get("species","")).strip() not in targets:
            continue
        if not str(row.get("id","")).strip():
            continue
        try:
            stake_xy(str(row.get("stake","")).strip())
        except ValueError:
            continue
        out.append(dict(row))
    return out


def _in_primary_window(year: int, month: int) -> bool:
    return (year,month) >= (2009,8) and (year,month) <= (2015,3)


def _seed(*parts: str) -> int:
    text="|".join(parts)
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16],16)


def build_portal_sessions(
    capture_rows: Iterable[dict],
    trapping_rows: Iterable[dict],
    plot_rows: Iterable[dict],
    species_rows: Iterable[dict],
    *,
    replicates: int=999,
) -> list[dict]:
    targets=_target_species_lookup(species_rows)
    captures=filter_primary_capture_rows(capture_rows,species_rows)

    effort={}
    for row in trapping_rows:
        try:
            key=(
                int(str(row.get("year","")).strip()),
                int(str(row.get("month","")).strip()),
                int(str(row.get("period","")).strip()),
                str(row.get("plot","")).strip(),
            )
        except ValueError:
            continue
        effort[key]=dict(row)

    treatment={}
    for row in plot_rows:
        try:
            key=(
                int(str(row.get("year","")).strip()),
                int(str(row.get("month","")).strip()),
                str(row.get("plot","")).strip(),
            )
        except ValueError:
            continue
        treatment[key]=str(row.get("treatment","")).strip().lower()

    grouped=defaultdict(list)
    for row in captures:
        try:
            year=int(str(row["year"]).strip())
            month=int(str(row["month"]).strip())
            period=int(str(row["period"]).strip())
        except (KeyError,ValueError):
            continue
        plot=str(row.get("plot","")).strip()
        species=str(row.get("species","")).strip()
        if not _in_primary_window(year,month):
            continue
        e=effort.get((year,month,period,plot))
        if e is None:
            continue
        if str(e.get("sampled","")).strip()!="1":
            continue
        if str(e.get("effort","")).strip()!="49":
            continue
        if str(e.get("qcflag","")).strip()!="1":
            continue
        trt=treatment.get((year,month,plot))
        if trt not in {"control","exclosure"}:
            continue
        grouped[(year,month,period,plot,species,trt)].append(row)

    results=[]
    for (year,month,period,plot,species,trt),rows in sorted(grouped.items()):
        # Lowest numeric recordID wins for duplicate individual records.
        def record_key(row: dict):
            raw=str(row.get("recordID","")).strip()
            try:
                return (0,int(raw))
            except ValueError:
                return (1,raw)

        by_id={}
        for row in sorted(rows,key=record_key):
            ident=str(row.get("id","")).strip()
            by_id.setdefault(ident,row)

        retained=list(by_id.values())
        observed=np.asarray(
            [stake_xy(str(row["stake"]).strip()) for row in retained],
            dtype=float,
        )
        n=len(retained)
        seed=_seed("portal",str(year),str(month),str(period),plot,species)
        score=PACKING.packing_score(
            observed,
            ACTIVE_TRAPS_XY,
            replicates=replicates,
            seed=seed,
        )
        pit=sum(_truthy(row.get("pit_tag","")) for row in retained)
        estimable=bool(score["estimable"])
        results.append({
            "source":"Portal",
            "site":"Portal",
            "plot_id":plot,
            "period":period,
            "year":year,
            "month":month,
            "species_code":species,
            "species":targets[species],
            "treatment":trt,
            "n_unique_individuals":n,
            "unique_individual_capture_count":n,
            "effort":49,
            "qcflag":1,
            "pit_reliable_count":pit,
            "pit_reliable_fraction":pit/n if n else None,
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


def summarize_portal_sessions(sessions: Iterable[dict]) -> dict:
    rows=list(sessions)
    by_species_treatment: dict[str, dict[str, int]] = {}
    for row in rows:
        species=str(row["species"])
        treatment=str(row["treatment"])
        by_species_treatment.setdefault(species,{}).setdefault(treatment,0)
        by_species_treatment[species][treatment]+=1
    pit_values=[
        float(row["pit_reliable_fraction"])
        for row in rows
        if row.get("pit_reliable_fraction") is not None
    ]
    years=[int(row["year"]) for row in rows]
    periods=[int(row["period"]) for row in rows]
    return {
        "session_count":len(rows),
        "species_count":len({str(row["species"]) for row in rows}),
        "eligible_n3":sum(bool(row["sensitivity_n3_eligible"]) for row in rows),
        "eligible_n5":sum(bool(row["primary_n5_eligible"]) for row in rows),
        "eligible_n8":sum(bool(row["sensitivity_n8_eligible"]) for row in rows),
        "packing_estimable_count":sum(bool(row.get("packing_estimable")) for row in rows),
        "median_pit_reliable_fraction":(
            statistics.median(pit_values) if pit_values else None
        ),
        "year_range":[min(years),max(years)] if years else None,
        "period_range":[min(periods),max(periods)] if periods else None,
        "species_treatment_session_counts":by_species_treatment,
    }


def audit_portal_utm_stakes(rows: Iterable[dict]) -> dict:
    by_key: dict[tuple[str,str], list[tuple[float,float]]] = defaultdict(list)
    for row in rows:
        if str(row.get("type","")).strip().lower()!="stake":
            continue
        plot=str(row.get("plot","")).strip()
        number=str(row.get("number","")).strip()
        if number not in VALID_STAKES:
            continue
        try:
            east=float(row.get("east",""))
            north=float(row.get("north",""))
        except (TypeError,ValueError):
            continue
        if not np.isfinite(east) or not np.isfinite(north):
            continue
        by_key[(plot,number)].append((east,north))

    duplicates=sum(len(values)-1 for values in by_key.values() if len(values)>1)
    by_plot: dict[str, list[tuple[float,float]]] = defaultdict(list)
    for (plot,_),values in sorted(by_key.items()):
        by_plot[plot].append(values[0])

    nearest=[]
    for points in by_plot.values():
        if len(points)<2:
            continue
        xy=np.asarray(points,dtype=float)
        diff=xy[:,None,:]-xy[None,:,:]
        dist=np.sqrt(np.sum(diff*diff,axis=2))
        np.fill_diagonal(dist,np.inf)
        nearest.extend(float(x) for x in np.min(dist,axis=1))

    return {
        "unique_valid_plot_stake_coordinates":len(by_key),
        "duplicate_plot_stake_coordinate_rows":duplicates,
        "plot_count_with_valid_stakes":len(by_plot),
        "median_empirical_nearest_stake_distance_m":(
            float(np.median(nearest)) if nearest else None
        ),
        "ideal_primary_stake_spacing_m":6.25,
    }


def _read_csv(path: Path) -> list[dict]:
    with path.open(newline="",encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def _write_session_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:
        path.write_text("",encoding="utf-8")
        return
    fields=list(rows[0].keys())
    with path.open("w",newline="",encoding="utf-8") as fh:
        writer=csv.DictWriter(fh,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--portal-dir",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--replicates",type=int,default=999)
    args=parser.parse_args()

    capture_rows=_read_csv(args.portal_dir/"Rodents"/"Portal_rodent.csv")
    trapping_rows=_read_csv(args.portal_dir/"Rodents"/"Portal_rodent_trapping.csv")
    species_rows=_read_csv(args.portal_dir/"Rodents"/"Portal_rodent_species.csv")
    plot_rows=_read_csv(args.portal_dir/"SiteandMethods"/"Portal_plots.csv")
    utm_rows=_read_csv(args.portal_dir/"SiteandMethods"/"Portal_UTMCoords.csv")

    sessions=build_portal_sessions(
        capture_rows,
        trapping_rows,
        plot_rows,
        species_rows,
        replicates=args.replicates,
    )
    args.output_dir.mkdir(parents=True,exist_ok=True)
    _write_session_csv(args.output_dir/"portal_space_use_sessions_v1.csv",sessions)

    primary_capture_rows=filter_primary_capture_rows(capture_rows,species_rows)
    inventory={
        "schema":"neon.public_mammal_space_use.portal_inventory.v1",
        "portal_commit_sha":"72d7ff8568052763bf6899dc462e285684cf20f6",
        "primary_window":["2009-08","2015-03"],
        "raw_capture_row_count":len(capture_rows),
        "primary_taxon_period_stake_identity_capture_row_count":len(primary_capture_rows),
        "basic_capture_rows_excluded":len(capture_rows)-len(primary_capture_rows),
        **summarize_portal_sessions(sessions),
        "utm_coordinate_audit":audit_portal_utm_stakes(utm_rows),
        "ecological_model_fits":0,
    }
    (args.output_dir/"portal_space_use_inventory_v1.json").write_text(
        json.dumps(inventory,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(inventory,sort_keys=True))


if __name__=="__main__":
    main()
