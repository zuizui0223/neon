from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import statistics
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

SPECIES={
    "PEMA":"Peromyscus maniculatus",
    "PEER":"Peromyscus eremicus",
}
CANONICAL_FLAGS={f"{r}{c}" for r in "ABCDEFG" for c in range(1,8)}
GRID_XY={
    f"{r}{c}":((c-1)*6.25,i*6.25)
    for i,r in enumerate("ABCDEFG")
    for c in range(1,8)
}
URL="https://ndownloader.figshare.com/files/33058799"
SHA256="ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"


def clean(x: object) -> str:
    return str(x or "").strip()


def parse_time(x: object) -> float | None:
    m=re.fullmatch(r"(\d{1,2}):(\d{2})",clean(x))
    if not m:
        return None
    h=int(m.group(1)); minute=int(m.group(2))
    if minute>=60:
        return None
    if 7<=h<=11:
        h+=12
    elif h==12:
        h=24
    elif 0<=h<=6:
        h+=24
    else:
        return None
    return h+minute/60.0


def flag_xy(flag: str) -> tuple[float,float]:
    return GRID_XY[flag]


def wilson_interval(success: int, total: int, z: float=1.959963984540054) -> tuple[float,float]:
    if total<=0:
        raise ValueError("total must be positive")
    p=success/total
    z2=z*z
    denom=1+z2/total
    center=(p+z2/(2*total))/denom
    half=z*math.sqrt((p*(1-p)+z2/(4*total))/total)/denom
    return center-half,center+half


def quantile(values: list[float], q: float) -> float:
    xs=sorted(float(x) for x in values)
    if not xs:
        raise ValueError("empty values")
    if len(xs)==1:
        return xs[0]
    pos=(len(xs)-1)*q
    lo=int(math.floor(pos)); hi=int(math.ceil(pos))
    if lo==hi:
        return xs[lo]
    w=pos-lo
    return xs[lo]*(1-w)+xs[hi]*w


def prepare_repeat_nights(rows: list[dict]) -> list[dict]:
    grouped=defaultdict(list)
    for index,row in enumerate(rows):
        species=clean(row.get("species"))
        if species not in SPECIES:
            continue
        uid=clean(row.get("unique_ID"))
        grid=clean(row.get("grid"))
        date=clean(row.get("date"))
        flag=clean(row.get("flag")).upper()
        t=parse_time(row.get("time"))
        if not uid or not grid or not date or flag not in CANONICAL_FLAGS or t is None:
            continue
        grouped[(species,grid,uid,date)].append({
            "row_index":index,
            "species":species,
            "grid":grid,
            "unique_ID":uid,
            "date":date,
            "flag":flag,
            "time":t,
        })

    out=[]
    for key,items in sorted(grouped.items()):
        if len(items)<2:
            continue
        first=min(items,key=lambda x:(x["time"],x["row_index"]))
        last=max(items,key=lambda x:(x["time"],x["row_index"]))
        x1,y1=flag_xy(first["flag"])
        x2,y2=flag_xy(last["flag"])
        d=float(math.hypot(x2-x1,y2-y1))
        span=float(last["time"]-first["time"])
        out.append({
            "species":key[0],
            "grid":key[1],
            "unique_ID":key[2],
            "date":key[3],
            "raw_capture_rows":len(items),
            "first_flag":first["flag"],
            "last_flag":last["flag"],
            "first_last_distance_m":d,
            "first_last_elapsed_hours":span,
            "any_flag_change":first["flag"]!=last["flag"],
            "one_spacing_shift":d>=6.25-1e-12,
        })
    return out


def summarize(rows: list[dict], lock: dict) -> dict:
    species_result={}
    species_passes=[]
    for species,name in SPECIES.items():
        srows=[r for r in rows if r["species"]==species]
        expected=int(lock["species"][species]["support_repeat_capture_nights"])
        if len(srows)!=expected:
            raise RuntimeError(
                f"{species} repeat-night count {len(srows)} != frozen support {expected}"
            )

        shifted=sum(bool(r["one_spacing_shift"]) for r in srows)
        low,high=wilson_interval(shifted,len(srows))
        fraction=shifted/len(srows)

        grid_rows={}
        passing_grids=[]
        for grid in sorted({r["grid"] for r in srows}):
            grows=[r for r in srows if r["grid"]==grid]
            gshift=sum(bool(r["one_spacing_shift"]) for r in grows)
            gfraction=gshift/len(grows)
            eligible=len(grows)>=int(lock["spatial_replication"]["grid_repeat_night_min"])
            passed=(
                eligible
                and gfraction>float(
                    lock["spatial_replication"]["grid_shift_fraction_min_exclusive"]
                )
            )
            if passed:
                passing_grids.append(grid)
            grid_rows[grid]={
                "repeat_capture_nights":len(grows),
                "one_spacing_shift_count":gshift,
                "one_spacing_shift_fraction":gfraction,
                "eligible_for_spatial_replication":eligible,
                "grid_replication_passed":passed,
            }

        species_gate=(
            low>float(lock["primary"]["material_fraction"])
            and len(passing_grids)>=int(lock["spatial_replication"]["grids_passing_min"])
        )
        if species_gate:
            species_passes.append(species)

        distances=[float(r["first_last_distance_m"]) for r in srows]
        spans=[float(r["first_last_elapsed_hours"]) for r in srows]
        species_result[species]={
            "scientific_name":name,
            "repeat_capture_nights":len(srows),
            "one_spacing_shift_count":shifted,
            "one_spacing_shift_fraction":fraction,
            "wilson95_low":low,
            "wilson95_high":high,
            "material_fraction_threshold":lock["primary"]["material_fraction"],
            "any_flag_change_count":sum(bool(r["any_flag_change"]) for r in srows),
            "any_flag_change_fraction":sum(bool(r["any_flag_change"]) for r in srows)/len(srows),
            "median_first_last_distance_m":statistics.median(distances),
            "q75_first_last_distance_m":quantile(distances,0.75),
            "q90_first_last_distance_m":quantile(distances,0.90),
            "max_first_last_distance_m":max(distances),
            "median_elapsed_hours":statistics.median(spans),
            "q90_elapsed_hours":quantile(spans,0.90),
            "grid_results":grid_rows,
            "spatial_replication_passing_grids":passing_grids,
            "spatial_replication_passing_grid_count":len(passing_grids),
            "species_gate_passed":species_gate,
        }

    programme_pass=set(species_passes)==set(lock["programme"]["required_species"])
    return {
        "schema":"neon.san_jacinto_positional_aliasing.result.v1",
        "species":species_result,
        "programme_gate":{
            "species_passing":species_passes,
            "passed":programme_pass,
            "decision":(
                lock["programme"]["pass"]
                if programme_pass else lock["programme"]["fail"]
            ),
        },
        "heldout_first_last_distances_inspected":True,
        "heldout_change_outcomes_inspected":True,
        "ecological_model_fits":0,
    }


def download_rows(path: Path) -> list[dict]:
    req=urllib.request.Request(URL,headers={"User-Agent":"san-jacinto-positional-aliasing/1.0"})
    with urllib.request.urlopen(req,timeout=180) as response:
        raw=response.read()
    actual=hashlib.sha256(raw).hexdigest()
    if actual!=SHA256:
        raise RuntimeError(f"source checksum mismatch: {actual}")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(raw)
    return list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:
        path.write_text("",encoding="utf-8"); return
    fields=list(rows[0].keys())
    with path.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=fields)
        w.writeheader(); w.writerows(rows)


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--lock",type=Path,required=True)
    parser.add_argument("--cache",type=Path,required=True)
    parser.add_argument("--output-json",type=Path,required=True)
    parser.add_argument("--output-csv",type=Path,required=True)
    args=parser.parse_args()

    lock=json.loads(args.lock.read_text())
    if lock["state"]!="frozen_before_holdout_positional_outcomes":
        raise RuntimeError("positional-aliasing lock not frozen")
    rows=download_rows(args.cache)
    repeat=prepare_repeat_nights(rows)
    result=summarize(repeat,lock)
    args.output_json.parent.mkdir(parents=True,exist_ok=True)
    args.output_json.write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    write_csv(args.output_csv,repeat)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
