from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import urllib.request
from collections import Counter, defaultdict
from datetime import date as Date
from pathlib import Path

HELDOUT={
    "PEMA":"Peromyscus maniculatus",
    "PEER":"Peromyscus eremicus",
    "REME":"Reithrodontomys megalotis",
}
CANONICAL_FLAGS={f"{r}{c}" for r in "ABCDEFG" for c in range(1,8)}
DOWNLOAD_URL="https://ndownloader.figshare.com/files/33058799"
SHA256="ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"


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
    return h+minute/60


def build_bouts(rows: list[dict]) -> dict[str,int]:
    dates=sorted({
        d for row in rows
        if (d:=parse_date(row.get("date"))) is not None
    })
    bouts=[]; cur=[]
    for d in dates:
        if cur and (d-cur[-1]).days>7:
            bouts.append(cur); cur=[]
        cur.append(d)
    if cur:
        bouts.append(cur)
    if not (10<=len(bouts)<=14):
        raise RuntimeError(f"unexpected bout count: {len(bouts)}")
    out={}
    for i,b in enumerate(bouts,1):
        for d in b:
            out[d.isoformat()]=i
    return out


def prepare(rows: list[dict]) -> tuple[list[dict],dict]:
    date_to_bout=build_bouts(rows)
    valid=[]
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

        valid.append({
            "row_index":index,
            "species":species,
            "grid":grid,
            "unique_ID":uid,
            "flag":flag,
            "date":d.isoformat(),
            "bout_id":date_to_bout[d.isoformat()],
            "nocturnal_time":t,
        })
    return valid,dict(excluded)


def count_support(rows: list[dict]) -> dict:
    valid,excluded=prepare(rows)

    raw_by_night=defaultdict(list)
    for x in valid:
        raw_by_night[(x["species"],x["grid"],x["unique_ID"],x["date"])].append(x)

    repeat_nights=[
        items for items in raw_by_night.values()
        if len(items)>=2
    ]

    # one deterministic nightly state, earliest capture
    nightly={}
    for key,items in raw_by_night.items():
        nightly[key]=min(
            items,key=lambda x:(x["nocturnal_time"],x["row_index"])
        )

    by_individual_bout=defaultdict(list)
    for (species,grid,uid,d),x in nightly.items():
        by_individual_bout[(species,grid,uid,x["bout_id"])].append(x)

    movement_eligible=defaultdict(int)
    for (species,grid,uid,bout),items in by_individual_bout.items():
        if len({x["date"] for x in items})>=2:
            movement_eligible[(species,grid,bout)]+=1

    species_summary={}
    qualifying=[]
    for species,name in HELDOUT.items():
        reps=[
            items for items in repeat_nights
            if items[0]["species"]==species
        ]
        rep_grids={items[0]["grid"] for items in reps}
        rep_bouts={items[0]["bout_id"] for items in reps}

        events=[
            (key,n) for key,n in movement_eligible.items()
            if key[0]==species and n>=10
        ]
        event_grids={key[1] for key,n in events}

        passes=(
            len(reps)>=100
            and len(rep_grids)>=2
            and len(rep_bouts)>=6
            and len(events)>=5
            and len(event_grids)>=2
        )
        if passes:
            qualifying.append(species)

        species_summary[species]={
            "scientific_name":name,
            "repeat_capture_individual_nights":len(reps),
            "repeat_capture_grids":len(rep_grids),
            "repeat_capture_grid_counts":dict(sorted(
                Counter(items[0]["grid"] for items in reps).items()
            )),
            "repeat_capture_bouts":len(rep_bouts),
            "movement_support_events":len(events),
            "movement_support_grids":len(event_grids),
            "movement_support_grid_counts":dict(sorted(
                Counter(key[1] for key,n in events).items()
            )),
            "movement_event_eligible_individual_counts":{
                f"{key[1]}:bout{key[2]}":n
                for key,n in sorted(events)
            },
            "species_gate_passed":passes,
        }

    passed=len(qualifying)>=2
    return {
        "schema":"neon.san_jacinto_temporal_aliasing_holdout.estimability_result.v1",
        "species":species_summary,
        "programme_gate":{
            "qualifying_species":qualifying,
            "qualifying_species_count":len(qualifying),
            "passed":passed,
            "decision":(
                "authorize_temporal_aliasing_effect_lock"
                if passed else
                "stop_temporal_aliasing_holdout_not_estimable"
            ),
        },
        "valid_holdout_capture_rows":len(valid),
        "excluded_rows":excluded,
        "first_last_distance_values_inspected":False,
        "first_last_change_outcomes_inspected":False,
        "first_last_movement_sensitivity_inspected":False,
        "packing_stability_inspected":False,
        "ecological_model_fits":0,
    }


def download_rows(path: Path) -> list[dict]:
    req=urllib.request.Request(
        DOWNLOAD_URL,
        headers={"User-Agent":"san-jacinto-temporal-aliasing-estimability/1.0"},
    )
    with urllib.request.urlopen(req,timeout=180) as response:
        raw=response.read()
    actual=hashlib.sha256(raw).hexdigest()
    if actual!=SHA256:
        raise RuntimeError(f"checksum mismatch: {actual}")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(raw)
    return list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--lock",type=Path,required=True)
    parser.add_argument("--cache",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()

    lock=json.loads(args.lock.read_text())
    if lock["state"]!="frozen_before_holdout_support_counts":
        raise RuntimeError("holdout lock not frozen")
    rows=download_rows(args.cache)
    out=count_support(rows)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
