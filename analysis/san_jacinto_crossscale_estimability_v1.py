from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import urllib.request
from collections import Counter, defaultdict
from datetime import date as Date
from pathlib import Path

FOCAL={
    "LAPM":"Perognathus longimembris brevinasus",
    "CHFA":"Chaetodipus fallax",
    "DKR":"Dipodomys simulans",
    "SKR":"Dipodomys stephensi",
}
CANONICAL_FLAGS={f"{row}{col}" for row in "ABCDEFG" for col in range(1,8)}


def clean(value: object) -> str:
    return str(value or "").strip()


def normalize_sex(value: object) -> str | None:
    text=clean(value).upper()
    return text if text in {"M","F"} else None


def normalize_flag(value: object) -> str:
    return clean(value).upper()


def parse_date(value: object) -> Date | None:
    text=clean(value)
    for sep in ("/","-"):
        parts=text.split(sep)
        if len(parts)!=3:
            continue
        try:
            nums=[int(float(x)) for x in parts]
        except ValueError:
            continue
        if nums[0]>1900:
            y,m,d=nums
        else:
            m,d,y=nums
            if y<100:
                y+=2000
        try:
            return Date(y,m,d)
        except ValueError:
            continue
    return None


def parse_nocturnal_time(value: object) -> float | None:
    text=clean(value)
    match=re.fullmatch(r"(\d{1,2}):(\d{2})",text)
    if not match:
        return None
    hour=int(match.group(1))
    minute=int(match.group(2))
    if minute>=60:
        return None
    if 7<=hour<=11:
        h=hour+12
    elif hour==12:
        h=24
    elif 0<=hour<=6:
        h=hour+24
    else:
        return None
    return h + minute/60.0


def build_bouts(rows: list[dict]) -> tuple[dict[str,int],list[dict]]:
    dates=sorted({
        d for row in rows
        if (d:=parse_date(row.get("date"))) is not None
    })
    bouts=[]
    current=[]
    for d in dates:
        if current and (d-current[-1]).days>7:
            bouts.append(current)
            current=[]
        current.append(d)
    if current:
        bouts.append(current)

    date_to_bout={}
    summary=[]
    for i,bout in enumerate(bouts,1):
        for d in bout:
            date_to_bout[d.isoformat()]=i
        summary.append({
            "bout_id":i,
            "date_start":bout[0].isoformat(),
            "date_end":bout[-1].isoformat(),
            "distinct_capture_dates":len(bout),
        })
    return date_to_bout,summary


def nightly_states(rows: list[dict]) -> tuple[list[dict],dict]:
    date_to_bout,bout_summary=build_bouts(rows)
    if not (10<=len(bout_summary)<=14):
        raise RuntimeError(f"bout count outside frozen range: {len(bout_summary)}")

    # First gather M/F states for each identity within a bout.
    sex_states=defaultdict(set)
    invalid_time_rows=0
    noncanonical_flag_rows=0
    missing_id_rows=0

    prepared=[]
    for index,row in enumerate(rows):
        species=clean(row.get("species"))
        if species not in FOCAL:
            continue
        grid=clean(row.get("grid"))
        uid=clean(row.get("unique_ID"))
        flag=normalize_flag(row.get("flag"))
        d=parse_date(row.get("date"))
        nocturnal=parse_nocturnal_time(row.get("time"))

        if not uid:
            missing_id_rows+=1
            continue
        if flag not in CANONICAL_FLAGS:
            noncanonical_flag_rows+=1
            continue
        if d is None or d.isoformat() not in date_to_bout:
            continue
        if nocturnal is None:
            invalid_time_rows+=1
            continue

        bout=date_to_bout[d.isoformat()]
        sex=normalize_sex(row.get("sex"))
        identity=(grid,species,uid)
        identity_bout=(grid,species,uid,bout)
        if sex is not None:
            sex_states[identity_bout].add(sex)

        prepared.append({
            "row_index":index,
            "grid":grid,
            "species":species,
            "unique_ID":uid,
            "identity":identity,
            "bout_id":bout,
            "date":d.isoformat(),
            "flag":flag,
            "nocturnal_time":nocturnal,
        })

    resolved_sex={}
    no_sex=0
    conflict=0
    for key in {(x["grid"],x["species"],x["unique_ID"],x["bout_id"]) for x in prepared}:
        states=sex_states.get(key,set())
        if len(states)==1:
            resolved_sex[key]=next(iter(states))
        elif len(states)==0:
            no_sex+=1
        else:
            conflict+=1

    # Exactly one nightly position per individual: earliest nocturnal time,
    # row-index tie break.
    best={}
    for x in prepared:
        key4=(x["grid"],x["species"],x["unique_ID"],x["bout_id"])
        sex=resolved_sex.get(key4)
        if sex is None:
            continue
        key5=(x["grid"],x["species"],x["unique_ID"],x["date"])
        candidate=(x["nocturnal_time"],x["row_index"],x)
        if key5 not in best or candidate[:2] < best[key5][:2]:
            best[key5]=candidate

    states=[]
    for _,_,x in best.values():
        key4=(x["grid"],x["species"],x["unique_ID"],x["bout_id"])
        states.append({
            **x,
            "sex":resolved_sex[key4],
        })

    qc={
        "bout_summary":bout_summary,
        "bout_count":len(bout_summary),
        "invalid_time_rows_in_focal_species":invalid_time_rows,
        "noncanonical_flag_rows_in_focal_species":noncanonical_flag_rows,
        "missing_identity_rows_in_focal_species":missing_id_rows,
        "identity_bouts_without_resolved_sex":no_sex,
        "identity_bouts_with_conflicting_sex":conflict,
        "nightly_state_count":len(states),
    }
    return states,qc


def count_support(rows: list[dict]) -> dict:
    states,qc=nightly_states(rows)

    packing_groups=defaultdict(list)
    by_individual_bout=defaultdict(list)
    for x in states:
        packing_groups[(x["species"],x["grid"],x["date"])].append(x)
        by_individual_bout[
            (x["species"],x["grid"],x["bout_id"],x["unique_ID"],x["sex"])
        ].append(x)

    packing_rows=[]
    for (species,grid,d),items in sorted(packing_groups.items()):
        males={x["unique_ID"] for x in items if x["sex"]=="M"}
        females={x["unique_ID"] for x in items if x["sex"]=="F"}
        packing_rows.append({
            "species":species,
            "scientific_name":FOCAL[species],
            "grid":grid,
            "date":d,
            "n_male":len(males),
            "n_female":len(females),
            "paired_n2_eligible":len(males)>=2 and len(females)>=2,
            "paired_n3_eligible":len(males)>=3 and len(females)>=3,
        })

    movement_counts=defaultdict(lambda:{"M":0,"F":0})
    for (species,grid,bout,uid,sex),items in by_individual_bout.items():
        dates={x["date"] for x in items}
        if len(dates)>=2:
            movement_counts[(species,grid,bout)][sex]+=1

    movement_rows=[]
    for (species,grid,bout),counts in sorted(movement_counts.items()):
        movement_rows.append({
            "species":species,
            "scientific_name":FOCAL[species],
            "grid":grid,
            "bout_id":bout,
            "n_male_movers":counts["M"],
            "n_female_movers":counts["F"],
            "paired_n2_eligible":counts["M"]>=2 and counts["F"]>=2,
            "paired_n3_eligible":counts["M"]>=3 and counts["F"]>=3,
        })

    species_summary={}
    qualifying=[]
    for species,name in FOCAL.items():
        p=[x for x in packing_rows if x["species"]==species]
        m=[x for x in movement_rows if x["species"]==species]
        p2=[x for x in p if x["paired_n2_eligible"]]
        p3=[x for x in p if x["paired_n3_eligible"]]
        m2=[x for x in m if x["paired_n2_eligible"]]
        m3=[x for x in m if x["paired_n3_eligible"]]

        p3_grids={x["grid"] for x in p3}
        m3_grids={x["grid"] for x in m3}
        overlap=sorted(p3_grids & m3_grids)
        overlap_p=sum(x["grid"] in overlap for x in p3)
        overlap_m=sum(x["grid"] in overlap for x in m3)

        p_pass=len(p3)>=10 and len(p3_grids)>=2
        m_pass=len(m3)>=5 and len(m3_grids)>=2
        matched=(
            len(overlap)>=2
            and overlap_p>=10
            and overlap_m>=5
        )
        cross=p_pass and m_pass and matched
        if cross:
            qualifying.append(species)

        species_summary[species]={
            "scientific_name":name,
            "packing":{
                "paired_n2_sessions":len(p2),
                "paired_n3_sessions":len(p3),
                "paired_n3_grids":len(p3_grids),
                "paired_n3_grid_counts":dict(sorted(Counter(x["grid"] for x in p3).items())),
            },
            "movement":{
                "paired_n2_events":len(m2),
                "paired_n3_events":len(m3),
                "paired_n3_grids":len(m3_grids),
                "paired_n3_grid_counts":dict(sorted(Counter(x["grid"] for x in m3).items())),
            },
            "overlapping_primary_grids":overlap,
            "overlap_packing_n3_sessions":overlap_p,
            "overlap_movement_n3_events":overlap_m,
            "packing_gate_passed":p_pass,
            "movement_gate_passed":m_pass,
            "matched_grid_gate_passed":matched,
            "crossscale_gate_passed":cross,
        }

    genera={FOCAL[s].split()[0] for s in qualifying}
    program_pass=len(qualifying)>=2 and len(genera)>=2
    result={
        "schema":"neon.san_jacinto_crossscale.estimability_result.v1",
        "primary_n_per_sex_min":3,
        "diagnostic_n_per_sex_min":2,
        "species":species_summary,
        "programme_gate":{
            "qualifying_species":qualifying,
            "qualifying_species_count":len(qualifying),
            "qualifying_genera":sorted(genera),
            "qualifying_genera_count":len(genera),
            "passed":program_pass,
            "decision":(
                "authorize_san_jacinto_crossscale_effect_lock"
                if program_pass else
                "stop_san_jacinto_crossscale_not_estimable"
            ),
        },
        "preprocessing_qc":qc,
        "species_by_sex_support_counts_inspected":True,
        "packing_effects_computed":False,
        "movement_distances_computed":False,
        "ecological_effect_models_fit":0,
    }
    return result,packing_rows,movement_rows


def download_verified(receipt: dict, path: Path) -> list[dict]:
    source=next(x for x in receipt["files"] if x["name"]=="year round trap data.csv")
    req=urllib.request.Request(source["download_url"],headers={"User-Agent":"san-jacinto-estimability/1.0"})
    with urllib.request.urlopen(req,timeout=180) as response:
        raw=response.read()
    actual=hashlib.sha256(raw).hexdigest()
    if actual!=source["sha256"]:
        raise RuntimeError("source checksum mismatch")
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
        w=csv.DictWriter(fh,fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-receipt",type=Path,required=True)
    parser.add_argument("--design-lock",type=Path,required=True)
    parser.add_argument("--cache",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()

    lock=json.loads(args.design_lock.read_text())
    if lock["state"]!="frozen_before_species_sex_support_counts":
        raise RuntimeError("estimability design is not frozen")
    if lock["species_by_sex_support_counts_inspected"]:
        raise RuntimeError("design lock says counts were already inspected")

    receipt=json.loads(args.source_receipt.read_text())
    rows=download_verified(receipt,args.cache)
    result,packing,movement=count_support(rows)

    args.output_dir.mkdir(parents=True,exist_ok=True)
    write_csv(args.output_dir/"packing_support_v1.csv",packing)
    write_csv(args.output_dir/"movement_support_v1.csv",movement)
    (args.output_dir/"estimability_result_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
