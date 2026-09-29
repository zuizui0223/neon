from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import statistics
import urllib.request
from collections import Counter, defaultdict
from datetime import date as Date
from pathlib import Path

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


EST=_load(
    "san_jacinto_estimability",
    "analysis/san_jacinto_crossscale_estimability_v1.py",
)
NULL=_load(
    "finite_iid_packing_null",
    "analysis/finite_iid_packing_null_v1.py",
)

GRID_XY=NULL.canonical_grid_7x7(6.25)


def nightly_states_selection(
    rows: list[dict],
    *,
    selection: str,
) -> tuple[list[dict],dict]:
    if selection not in {"first","last"}:
        raise ValueError("selection must be first or last")

    date_to_bout,bout_summary=EST.build_bouts(rows)
    if not (10<=len(bout_summary)<=14):
        raise RuntimeError(f"bout count outside frozen range: {len(bout_summary)}")

    sex_states=defaultdict(set)
    prepared=[]
    for index,row in enumerate(rows):
        species=EST.clean(row.get("species"))
        if species not in EST.FOCAL:
            continue
        grid=EST.clean(row.get("grid"))
        uid=EST.clean(row.get("unique_ID"))
        flag=EST.normalize_flag(row.get("flag"))
        d=EST.parse_date(row.get("date"))
        nocturnal=EST.parse_nocturnal_time(row.get("time"))

        if not uid or flag not in EST.CANONICAL_FLAGS or d is None:
            continue
        if d.isoformat() not in date_to_bout or nocturnal is None:
            continue

        bout=date_to_bout[d.isoformat()]
        sex=EST.normalize_sex(row.get("sex"))
        key4=(grid,species,uid,bout)
        if sex is not None:
            sex_states[key4].add(sex)

        prepared.append({
            "row_index":index,
            "grid":grid,
            "species":species,
            "unique_ID":uid,
            "bout_id":bout,
            "date":d.isoformat(),
            "flag":flag,
            "nocturnal_time":nocturnal,
        })

    resolved={}
    for key in {
        (x["grid"],x["species"],x["unique_ID"],x["bout_id"])
        for x in prepared
    }:
        states=sex_states.get(key,set())
        if len(states)==1:
            resolved[key]=next(iter(states))

    best={}
    for x in prepared:
        key4=(x["grid"],x["species"],x["unique_ID"],x["bout_id"])
        sex=resolved.get(key4)
        if sex is None:
            continue
        key5=(x["grid"],x["species"],x["unique_ID"],x["date"])
        rank=(x["nocturnal_time"],x["row_index"])
        if key5 not in best:
            best[key5]=(rank,x)
        elif selection=="first" and rank<best[key5][0]:
            best[key5]=(rank,x)
        elif selection=="last" and rank>best[key5][0]:
            best[key5]=(rank,x)

    out=[]
    for _,x in best.values():
        key4=(x["grid"],x["species"],x["unique_ID"],x["bout_id"])
        out.append({**x,"sex":resolved[key4]})

    out.sort(
        key=lambda x:(
            x["species"],x["grid"],x["bout_id"],x["date"],x["unique_ID"]
        )
    )

    if selection=="first":
        canonical,_=EST.nightly_states(rows)
        canonical_keys=sorted(
            (
                x["grid"],x["species"],x["unique_ID"],x["bout_id"],
                x["date"],x["flag"],x["sex"],
            )
            for x in canonical
        )
        out_keys=sorted(
            (
                x["grid"],x["species"],x["unique_ID"],x["bout_id"],
                x["date"],x["flag"],x["sex"],
            )
            for x in out
        )
        if out_keys!=canonical_keys:
            raise RuntimeError(
                "primary effect preprocessing diverges from frozen estimability preprocessing"
            )

    return out,{
        "selection":selection,
        "bout_count":len(bout_summary),
        "nightly_state_count":len(out),
    }


def flag_xy(flag: str) -> tuple[float,float]:
    try:
        return GRID_XY[str(flag).upper()]
    except KeyError as exc:
        raise ValueError(f"noncanonical flag: {flag}") from exc


def packing_effect_rows(
    states: list[dict],
) -> list[dict]:
    grouped=defaultdict(list)
    for row in states:
        grouped[(row["species"],row["grid"],row["date"])].append(row)

    support=np.asarray([GRID_XY[key] for key in sorted(GRID_XY)],dtype=float)
    out=[]
    for (species,grid,d),items in sorted(grouped.items()):
        male=[x for x in items if x["sex"]=="M"]
        female=[x for x in items if x["sex"]=="F"]
        if len(male)<2 or len(female)<2:
            continue

        male_xy=np.asarray([flag_xy(x["flag"]) for x in male],dtype=float)
        female_xy=np.asarray([flag_xy(x["flag"]) for x in female],dtype=float)
        m=NULL.packing_score_iid_exact(male_xy,support)
        f=NULL.packing_score_iid_exact(female_xy,support)
        if not m["estimable"] or not f["estimable"]:
            continue

        out.append({
            "species":species,
            "scientific_name":EST.FOCAL[species],
            "grid":grid,
            "date":d,
            "n_male":len(male),
            "n_female":len(female),
            "paired_n2_eligible":True,
            "paired_n3_eligible":len(male)>=3 and len(female)>=3,
            "packing_z_male":m["packing_z"],
            "packing_z_female":f["packing_z"],
            "delta_packing":m["packing_z"]-f["packing_z"],
            "male_mpd_m":m["mpd_observed"],
            "female_mpd_m":f["mpd_observed"],
            "male_null_sd_m":m["mpd_null_sd"],
            "female_null_sd_m":f["mpd_null_sd"],
            "null_mode":m["null_mode"],
        })
    return out


def individual_movement_value(items: list[dict]) -> float | None:
    if len(items)<2:
        return None
    ordered=sorted(items,key=lambda x:(x["date"],x["row_index"]))
    values=[]
    for left,right in zip(ordered,ordered[1:]):
        d1=Date.fromisoformat(left["date"])
        d2=Date.fromisoformat(right["date"])
        days=(d2-d1).days
        if days<=0:
            continue
        x1,y1=flag_xy(left["flag"])
        x2,y2=flag_xy(right["flag"])
        distance=math.hypot(x2-x1,y2-y1)
        values.append(math.log1p(distance/days))
    if not values:
        return None
    return float(statistics.median(values))


def movement_effect_rows(
    states: list[dict],
) -> list[dict]:
    by_individual=defaultdict(list)
    for row in states:
        by_individual[
            (
                row["species"],row["grid"],row["bout_id"],
                row["unique_ID"],row["sex"],
            )
        ].append(row)

    event_values=defaultdict(lambda:{"M":[],"F":[]})
    for (species,grid,bout,uid,sex),items in by_individual.items():
        value=individual_movement_value(items)
        if value is not None:
            event_values[(species,grid,bout)][sex].append(value)

    out=[]
    for (species,grid,bout),sex_values in sorted(event_values.items()):
        male=sex_values["M"]
        female=sex_values["F"]
        if len(male)<2 or len(female)<2:
            continue
        male_mean=float(statistics.mean(male))
        female_mean=float(statistics.mean(female))
        out.append({
            "species":species,
            "scientific_name":EST.FOCAL[species],
            "grid":grid,
            "bout_id":bout,
            "n_male_movers":len(male),
            "n_female_movers":len(female),
            "paired_n2_eligible":True,
            "paired_n3_eligible":len(male)>=3 and len(female)>=3,
            "male_mean_individual_log1p_m_per_day":male_mean,
            "female_mean_individual_log1p_m_per_day":female_mean,
            "delta_movement":male_mean-female_mean,
        })
    return out


def assert_primary_support_matches(
    packing_rows: list[dict],
    movement_rows: list[dict],
    estimability: dict,
) -> dict:
    checks={}
    for species in EST.FOCAL:
        p_counts=Counter(
            row["grid"] for row in packing_rows
            if row["species"]==species and row["paired_n3_eligible"]
        )
        m_counts=Counter(
            row["grid"] for row in movement_rows
            if row["species"]==species and row["paired_n3_eligible"]
        )
        expected_p={
            str(k):int(v)
            for k,v in estimability["species"][species]["packing"][
                "paired_n3_grid_counts"
            ].items()
        }
        expected_m={
            str(k):int(v)
            for k,v in estimability["species"][species]["movement"][
                "paired_n3_grid_counts"
            ].items()
        }
        actual_p=dict(sorted((str(k),int(v)) for k,v in p_counts.items()))
        actual_m=dict(sorted((str(k),int(v)) for k,v in m_counts.items()))
        if actual_p!=expected_p:
            raise RuntimeError(
                f"{species} packing support mismatch: {actual_p} != {expected_p}"
            )
        if actual_m!=expected_m:
            raise RuntimeError(
                f"{species} movement support mismatch: {actual_m} != {expected_m}"
            )
        checks[species]={
            "packing_primary_grid_counts":actual_p,
            "movement_primary_grid_counts":actual_m,
        }
    return checks


def download_rows(source_receipt: dict, path: Path) -> list[dict]:
    source=next(
        x for x in source_receipt["files"]
        if x["name"]=="year round trap data.csv"
    )
    req=urllib.request.Request(
        source["download_url"],
        headers={"User-Agent":"san-jacinto-crossscale-effects/1.0"},
    )
    with urllib.request.urlopen(req,timeout=180) as response:
        raw=response.read()
    actual=hashlib.sha256(raw).hexdigest()
    if actual!=source["sha256"]:
        raise RuntimeError(f"source checksum mismatch: {actual}")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(raw)
    return list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:
        path.write_text("",encoding="utf-8")
        return
    fields=list(rows[0].keys())
    with path.open("w",newline="",encoding="utf-8") as fh:
        writer=csv.DictWriter(fh,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def extract(
    rows: list[dict],
    estimability: dict,
) -> dict:
    first,qc_first=nightly_states_selection(rows,selection="first")
    last,qc_last=nightly_states_selection(rows,selection="last")

    packing_first=packing_effect_rows(first)
    movement_first=movement_effect_rows(first)
    support_checks=assert_primary_support_matches(
        packing_first,movement_first,estimability
    )

    packing_last=packing_effect_rows(last)
    movement_last=movement_effect_rows(last)

    return {
        "packing_first":packing_first,
        "movement_first":movement_first,
        "packing_last":packing_last,
        "movement_last":movement_last,
        "inventory":{
            "schema":"neon.san_jacinto_crossscale.effect_extraction.v1",
            "primary_support_checks":support_checks,
            "first_nightly_state_count":qc_first["nightly_state_count"],
            "last_nightly_state_count":qc_last["nightly_state_count"],
            "packing_first_n2_rows":len(packing_first),
            "packing_first_n3_rows":sum(x["paired_n3_eligible"] for x in packing_first),
            "movement_first_n2_rows":len(movement_first),
            "movement_first_n3_rows":sum(x["paired_n3_eligible"] for x in movement_first),
            "packing_effects_computed":True,
            "movement_distances_computed":True,
            "ecological_effect_models_fit":0,
        },
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-receipt",type=Path,required=True)
    parser.add_argument("--estimability",type=Path,required=True)
    parser.add_argument("--cache",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()

    source=json.loads(args.source_receipt.read_text())
    estimability=json.loads(args.estimability.read_text())
    rows=download_rows(source,args.cache)
    out=extract(rows,estimability)

    args.output_dir.mkdir(parents=True,exist_ok=True)
    for key,filename in (
        ("packing_first","packing_first_v1.csv"),
        ("movement_first","movement_first_v1.csv"),
        ("packing_last","packing_last_v1.csv"),
        ("movement_last","movement_last_v1.csv"),
    ):
        write_csv(args.output_dir/filename,out[key])
    (args.output_dir/"effect_extraction_inventory_v1.json").write_text(
        json.dumps(out["inventory"],indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(out["inventory"],indent=2,sort_keys=True))


if __name__=="__main__":
    raise SystemExit(main())
