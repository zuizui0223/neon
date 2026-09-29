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
from datetime import date as Date
from pathlib import Path

HELDOUT={
    "PEMA":"Peromyscus maniculatus",
    "PEER":"Peromyscus eremicus",
}
CANONICAL_FLAGS={f"{r}{c}" for r in "ABCDEFG" for c in range(1,8)}
GRID_XY={
    f"{r}{c}":((c-1)*6.25,ri*6.25)
    for ri,r in enumerate("ABCDEFG")
    for c in range(1,8)
}
DOWNLOAD_URL="https://ndownloader.figshare.com/files/33058799"
SHA256="ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"
Z95=1.959963984540054


def clean(x: object) -> str:
    return str(x or "").strip()


def parse_date(x: object) -> Date | None:
    text=clean(x)
    for sep in ("/","-"):
        parts=text.split(sep)
        if len(parts)!=3:
            continue
        try:
            vals=[int(float(v)) for v in parts]
        except ValueError:
            continue
        if vals[0]>1900:
            y,m,d=vals
        else:
            m,d,y=vals
            if y<100:
                y+=2000
        try:
            return Date(y,m,d)
        except ValueError:
            pass
    return None


def parse_nocturnal_time(x: object) -> float | None:
    m=re.fullmatch(r"(\d{1,2}):(\d{2})",clean(x))
    if not m:
        return None
    h=int(m.group(1))
    minute=int(m.group(2))
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
    return h+minute/60


def build_bouts(rows: list[dict]) -> dict[str,int]:
    dates=sorted({
        d for row in rows
        if (d:=parse_date(row.get("date"))) is not None
    })
    bouts=[]; current=[]
    for d in dates:
        if current and (d-current[-1]).days>7:
            bouts.append(current); current=[]
        current.append(d)
    if current:
        bouts.append(current)
    if not (10<=len(bouts)<=14):
        raise RuntimeError(f"unexpected bout count: {len(bouts)}")
    mapping={}
    for i,bout in enumerate(bouts,1):
        for d in bout:
            mapping[d.isoformat()]=i
    return mapping


def flag_xy(flag: str) -> tuple[float,float]:
    return GRID_XY[str(flag).upper()]


def distance_m(a: str, b: str) -> float:
    x1,y1=flag_xy(a)
    x2,y2=flag_xy(b)
    return float(math.hypot(x2-x1,y2-y1))


def wilson_interval(successes: int, n: int, z: float=Z95) -> tuple[float,float]:
    if n<=0:
        raise ValueError("n must be positive")
    p=successes/n
    z2=z*z
    denom=1+z2/n
    center=(p+z2/(2*n))/denom
    half=z*math.sqrt((p*(1-p)+z2/(4*n))/n)/denom
    return max(0.0,center-half),min(1.0,center+half)


def prepare_repeat_nights(rows: list[dict]) -> tuple[list[dict],dict]:
    date_to_bout=build_bouts(rows)
    grouped=defaultdict(list)
    excluded=Counter()

    for index,row in enumerate(rows):
        species=clean(row.get("species"))
        if species not in HELDOUT:
            continue
        grid=clean(row.get("grid"))
        uid=clean(row.get("unique_ID"))
        flag=clean(row.get("flag")).upper()
        d=parse_date(row.get("date"))
        t=parse_nocturnal_time(row.get("time"))

        if not uid:
            excluded["missing_id"]+=1; continue
        if flag not in CANONICAL_FLAGS:
            excluded["invalid_flag"]+=1; continue
        if d is None or d.isoformat() not in date_to_bout:
            excluded["invalid_date"]+=1; continue
        if t is None:
            excluded["invalid_time"]+=1; continue

        key=(species,grid,uid,d.isoformat())
        grouped[key].append({
            "row_index":index,
            "species":species,
            "grid":grid,
            "unique_ID":uid,
            "date":d.isoformat(),
            "bout_id":date_to_bout[d.isoformat()],
            "flag":flag,
            "time":t,
        })

    repeat=[]
    for key,items in sorted(grouped.items()):
        if len(items)<2:
            continue
        ordered=sorted(items,key=lambda x:(x["time"],x["row_index"]))
        first=ordered[0]
        last=ordered[-1]
        d=distance_m(first["flag"],last["flag"])
        repeat.append({
            "species":first["species"],
            "scientific_name":HELDOUT[first["species"]],
            "grid":first["grid"],
            "unique_ID":first["unique_ID"],
            "date":first["date"],
            "bout_id":first["bout_id"],
            "capture_rows":len(items),
            "first_flag":first["flag"],
            "last_flag":last["flag"],
            "first_time":first["time"],
            "last_time":last["time"],
            "elapsed_hours":float(last["time"]-first["time"]),
            "changed":first["flag"]!=last["flag"],
            "distance_m":d,
            "trap_spacings":d/6.25,
        })

    return repeat,dict(excluded)


def summarize_species(rows: list[dict], species: str) -> dict:
    srows=[x for x in rows if x["species"]==species]
    if not srows:
        raise RuntimeError(f"no repeat nights for {species}")

    changed=[x for x in srows if x["changed"]]
    n=len(srows)
    k=len(changed)
    low,high=wilson_interval(k,n)
    changed_dist=[x["distance_m"] for x in changed]
    all_dist=[x["distance_m"] for x in srows]
    elapsed=[x["elapsed_hours"] for x in srows]

    grid_counts=Counter(x["grid"] for x in srows)
    bout_counts=Counter(x["bout_id"] for x in srows)

    individual_changed=defaultdict(list)
    for x in srows:
        individual_changed[(x["grid"],x["unique_ID"])].append(int(x["changed"]))
    repeatability=[
        statistics.mean(vals)
        for vals in individual_changed.values()
        if len(vals)>=3
    ]

    leave_one_grid=[]
    for grid in sorted(grid_counts):
        kept=[x for x in srows if x["grid"]!=grid]
        if not kept:
            continue
        kk=sum(x["changed"] for x in kept)
        nn=len(kept)
        lo,hi=wilson_interval(kk,nn)
        leave_one_grid.append({
            "excluded_grid":grid,
            "n":nn,
            "changed":kk,
            "fraction":kk/nn,
            "ci95_low":lo,
            "ci95_high":hi,
        })

    return {
        "species":species,
        "scientific_name":HELDOUT[species],
        "repeat_capture_nights":n,
        "grid_count":len(grid_counts),
        "bout_count":len(bout_counts),
        "grid_counts":dict(sorted(grid_counts.items())),
        "bout_counts":{str(k):v for k,v in sorted(bout_counts.items())},
        "changed_nights":k,
        "changed_fraction":k/n,
        "changed_fraction_ci95_low":low,
        "changed_fraction_ci95_high":high,
        "changed_distance_median_m":float(statistics.median(changed_dist)) if changed_dist else None,
        "changed_distance_mean_m":float(statistics.mean(changed_dist)) if changed_dist else None,
        "all_night_distance_median_m":float(statistics.median(all_dist)),
        "all_night_distance_mean_m":float(statistics.mean(all_dist)),
        "all_night_distance_q90_m":float(statistics.quantiles(all_dist,n=10,method="inclusive")[8]),
        "all_night_distance_max_m":max(all_dist),
        "elapsed_hours_median":float(statistics.median(elapsed)),
        "fraction_ge_1_spacing":sum(x["distance_m"]>=6.25 for x in srows)/n,
        "fraction_ge_2_spacings":sum(x["distance_m"]>=12.5 for x in srows)/n,
        "fraction_ge_3_spacings":sum(x["distance_m"]>=18.75 for x in srows)/n,
        "individuals_with_ge3_repeat_nights":len(repeatability),
        "individual_changed_fraction_median":(
            float(statistics.median(repeatability)) if repeatability else None
        ),
        "leave_one_grid_out":leave_one_grid,
    }


def evaluate(summary: dict) -> dict:
    conditions={
        "changed_fraction_gt_0_25":summary["changed_fraction"]>0.25,
        "wilson_ci95_low_gt_0_25":summary["changed_fraction_ci95_low"]>0.25,
        "changed_distance_median_ge_6_25":(
            summary["changed_distance_median_m"] is not None
            and summary["changed_distance_median_m"]>=6.25
        ),
        "repeat_nights_ge_100":summary["repeat_capture_nights"]>=100,
        "grids_ge_2":summary["grid_count"]>=2,
        "bouts_ge_6":summary["bout_count"]>=6,
    }
    return {
        "conditions":conditions,
        "passed":all(conditions.values()),
    }


def analyze(rows: list[dict], support_provenance: dict) -> dict:
    repeat,excluded=prepare_repeat_nights(rows)

    expected={
        sp:int(info["repeat_capture_individual_nights"])
        for sp,info in support_provenance["heldout_species_support"].items()
    }
    observed=Counter(x["species"] for x in repeat)
    for species,n in expected.items():
        if int(observed.get(species,0))!=n:
            raise RuntimeError(
                f"{species} repeat-night support mismatch: "
                f"{observed.get(species,0)} != {n}"
            )

    summaries={sp:summarize_species(repeat,sp) for sp in HELDOUT}
    gates={sp:evaluate(summaries[sp]) for sp in HELDOUT}
    passed=all(gates[sp]["passed"] for sp in HELDOUT)

    return {
        "schema":"neon.san_jacinto_intranight_aliasing.result.v1",
        "species":summaries,
        "species_gates":gates,
        "programme_gate":{
            "both_species_required":True,
            "passed":passed,
            "decision":(
                "confirm_intranight_positional_aliasing_across_cricetids"
                if passed else
                "stop_intranight_aliasing_not_replicated"
            ),
        },
        "excluded_rows":excluded,
        "distance_values_inspected":True,
        "changed_values_inspected":True,
        "ecological_model_fits":0,
    },repeat


def download_rows(path: Path) -> list[dict]:
    req=urllib.request.Request(
        DOWNLOAD_URL,
        headers={"User-Agent":"san-jacinto-intranight-aliasing/1.0"},
    )
    with urllib.request.urlopen(req,timeout=180) as response:
        raw=response.read()
    actual=hashlib.sha256(raw).hexdigest()
    if actual!=SHA256:
        raise RuntimeError(f"checksum mismatch: {actual}")
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
    parser.add_argument("--support-provenance",type=Path,required=True)
    parser.add_argument("--cache",type=Path,required=True)
    parser.add_argument("--output-json",type=Path,required=True)
    parser.add_argument("--output-csv",type=Path,required=True)
    args=parser.parse_args()

    lock=json.loads(args.lock.read_text())
    if lock["state"]!="frozen_before_holdout_aliasing_outcomes":
        raise RuntimeError("effect lock not frozen")
    if lock["pema_outcomes_inspected"] or lock["peer_outcomes_inspected"]:
        raise RuntimeError("effect lock says outcomes already inspected")

    rows=download_rows(args.cache)
    result,detail=analyze(
        rows,
        json.loads(args.support_provenance.read_text()),
    )
    args.output_json.parent.mkdir(parents=True,exist_ok=True)
    args.output_json.write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    write_csv(args.output_csv,detail)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
