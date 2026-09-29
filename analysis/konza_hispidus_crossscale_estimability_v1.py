from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


TARGET_SPECIES_NORMALIZED="ch"
PRIMARY_DAYS={1,2,3,4}


def _int(value: object) -> int | None:
    try:
        text=str(value or "").strip()
        if not text:
            return None
        return int(float(text))
    except (TypeError,ValueError):
        return None


def _sex(value: object) -> str | None:
    text=str(value or "").strip().upper()
    if text=="M":
        return "M"
    if text=="F":
        return "F"
    return None


def _mark(value: object) -> str | None:
    text=re.sub(r"[^A-Z0-9]+","",str(value or "").strip().upper())
    if not text or not re.search(r"\d",text):
        return None
    if text in {"0","00","000","0000","999","9999"}:
        return None
    return text


def strong_tokens(row: dict) -> set[str]:
    out=set()
    for prefix,column in (
        ("R","REarTag"),
        ("L","LEarTag"),
        ("T","ToeClip"),
    ):
        value=_mark(row.get(column))
        if value is not None:
            out.add(f"{prefix}:{value}")
    return out


def period_key(row: dict) -> tuple[str,str,str,str]:
    return (
        str(row.get("Recyear","")).strip(),
        str(row.get("Season","")).strip().upper(),
        str(row.get("Watershed","")).strip().upper(),
        str(row.get("Line","")).strip().upper(),
    )


def trapline_id(key: tuple[str,str,str,str]) -> str:
    return f"{key[2]}::{key[3]}"


class UnionFind:
    def __init__(self,n: int):
        self.parent=list(range(n))
        self.size=[1]*n

    def find(self,x: int) -> int:
        while self.parent[x]!=x:
            self.parent[x]=self.parent[self.parent[x]]
            x=self.parent[x]
        return x

    def union(self,a: int,b: int) -> None:
        ra=self.find(a)
        rb=self.find(b)
        if ra==rb:
            return
        if self.size[ra]<self.size[rb]:
            ra,rb=rb,ra
        self.parent[rb]=ra
        self.size[ra]+=self.size[rb]


def movement_identity_summary(rows: Iterable[dict]) -> dict:
    target=[]
    for raw in rows:
        row=dict(raw)
        if str(row.get("Species","")).strip().lower()!=TARGET_SPECIES_NORMALIZED:
            continue
        day=_int(row.get("TrapDay"))
        sta=_int(row.get("Sta"))
        if day not in PRIMARY_DAYS or sta is None or not (1<=sta<=20):
            continue
        target.append(row)

    if not target:
        return {
            "n_target_rows":0,
            "n_components":0,
            "n_valid_components":0,
            "n_recapture_male":0,
            "n_recapture_female":0,
            "n_no_strong_mark_rows":0,
            "n_invalid_sex_components":0,
            "n_invalid_same_day_station_components":0,
            "paired_n3_eligible":False,
            "paired_n5_eligible":False,
        }

    uf=UnionFind(len(target))
    owner={}
    row_tokens=[]
    no_mark=0
    for i,row in enumerate(target):
        tokens=strong_tokens(row)
        row_tokens.append(tokens)
        if not tokens:
            no_mark+=1
            continue
        for token in tokens:
            if token in owner:
                uf.union(i,owner[token])
            else:
                owner[token]=i

    groups=defaultdict(list)
    for i,tokens in enumerate(row_tokens):
        if not tokens:
            continue
        groups[uf.find(i)].append(i)

    male=0
    female=0
    invalid_sex=0
    invalid_same_day=0
    valid_components=0

    for indices in groups.values():
        sexes={
            _sex(target[i].get("Sex"))
            for i in indices
            if _sex(target[i].get("Sex")) is not None
        }
        if len(sexes)!=1:
            invalid_sex+=1
            continue

        by_day=defaultdict(set)
        for i in indices:
            day=_int(target[i].get("TrapDay"))
            sta=_int(target[i].get("Sta"))
            by_day[day].add(sta)
        if any(len(stations)>1 for stations in by_day.values()):
            invalid_same_day+=1
            continue

        valid_components+=1
        if len(by_day)<2:
            continue
        sex=next(iter(sexes))
        if sex=="M":
            male+=1
        elif sex=="F":
            female+=1

    return {
        "n_target_rows":len(target),
        "n_components":len(groups),
        "n_valid_components":valid_components,
        "n_recapture_male":male,
        "n_recapture_female":female,
        "n_no_strong_mark_rows":no_mark,
        "n_invalid_sex_components":invalid_sex,
        "n_invalid_same_day_station_components":invalid_same_day,
        "paired_n3_eligible":male>=3 and female>=3,
        "paired_n5_eligible":male>=5 and female>=5,
    }


def packing_night_rows(rows: Iterable[dict]) -> list[dict]:
    source=[dict(row) for row in rows]
    key=period_key(source[0]) if source else ("","","","")
    line=trapline_id(key)

    occupancy=Counter()
    target_by_day=defaultdict(list)

    for row in source:
        day=_int(row.get("TrapDay"))
        sta=_int(row.get("Sta"))
        species=str(row.get("Species","")).strip()
        if day not in PRIMARY_DAYS:
            continue

        if species and species.upper()!="X" and sta is not None and 1<=sta<=20:
            occupancy[(day,sta)]+=1

        if species.lower()==TARGET_SPECIES_NORMALIZED:
            target_by_day[day].append(row)

    out=[]
    for day in sorted(PRIMARY_DAYS):
        target=target_by_day.get(day,[])
        male=0
        female=0
        invalid_target_station=0
        for row in target:
            sta=_int(row.get("Sta"))
            sex=_sex(row.get("Sex"))
            if sta is None or not (1<=sta<=20):
                invalid_target_station+=1
                continue
            if sex=="M":
                male+=1
            elif sex=="F":
                female+=1

        overfull=sorted(
            sta for (d,sta),n in occupancy.items()
            if d==day and n>2
        )
        geometry_valid=(invalid_target_station==0 and not overfull)
        out.append({
            "year":key[0],
            "season":key[1],
            "watershed":key[2],
            "line":key[3],
            "trapline_id":line,
            "trap_day":day,
            "n_male":male,
            "n_female":female,
            "target_capture_rows":len(target),
            "invalid_target_station_rows":invalid_target_station,
            "overfull_station_count":len(overfull),
            "overfull_stations":";".join(str(x) for x in overfull),
            "trap_slot_geometry_valid":geometry_valid,
            "paired_n3_eligible":geometry_valid and male>=3 and female>=3,
            "paired_n5_eligible":geometry_valid and male>=5 and female>=5,
        })
    return out


def summarize(
    packing: list[dict],
    movement: list[dict],
) -> dict:
    packing_n5=[row for row in packing if row["paired_n5_eligible"]]
    movement_n5=[row for row in movement if row["paired_n5_eligible"]]
    packing_n3=[row for row in packing if row["paired_n3_eligible"]]
    movement_n3=[row for row in movement if row["paired_n3_eligible"]]

    p_lines={row["trapline_id"] for row in packing_n5}
    m_lines={row["trapline_id"] for row in movement_n5}
    overlap=sorted(p_lines&m_lines)

    p_overlap=[row for row in packing_n5 if row["trapline_id"] in overlap]
    m_overlap=[row for row in movement_n5 if row["trapline_id"] in overlap]
    watersheds=sorted({
        row["watershed"]
        for row in p_overlap+m_overlap
        if row["watershed"]
    })

    conditions={
        "packing_n5_nights_within_overlap_ge_20":len(p_overlap)>=20,
        "movement_n5_periods_within_overlap_ge_6":len(m_overlap)>=6,
        "overlapping_traplines_ge_6":len(overlap)>=6,
        "overlapping_watersheds_ge_3":len(watersheds)>=3,
    }
    passed=all(conditions.values())

    return {
        "schema":"neon.konza_hispidus_crossscale.estimability.v1",
        "target_species_code_metadata":"Ch",
        "target_species_code_observed":"ch",
        "target_species_match":"case_insensitive",
        "target_scientific_name":"Chaetodipus hispidus",
        "primary_n_per_sex":5,
        "diagnostic_n_per_sex":3,
        "packing":{
            "candidate_nights":len(packing),
            "paired_n3_nights":len(packing_n3),
            "paired_n5_nights":len(packing_n5),
            "paired_n5_traplines":len(p_lines),
            "paired_n5_trapline_counts":dict(sorted(Counter(row["trapline_id"] for row in packing_n5).items())),
        },
        "movement":{
            "candidate_periods":len(movement),
            "paired_n3_periods":len(movement_n3),
            "paired_n5_periods":len(movement_n5),
            "paired_n5_traplines":len(m_lines),
            "paired_n5_trapline_counts":dict(sorted(Counter(row["trapline_id"] for row in movement_n5).items())),
        },
        "crossscale_gate":{
            "overlapping_traplines":overlap,
            "overlapping_trapline_count":len(overlap),
            "overlapping_watersheds":watersheds,
            "overlapping_watershed_count":len(watersheds),
            "packing_n5_nights_within_overlap":len(p_overlap),
            "movement_n5_periods_within_overlap":len(m_overlap),
            "conditions":conditions,
            "passed":passed,
            "decision":(
                "authorize_konza_crossscale_effect_lock"
                if passed else
                "stop_konza_crossscale_not_estimable"
            ),
        },
        "packing_effects_inspected":False,
        "movement_distances_inspected":False,
        "ecological_effect_models_fit":0,
    }


def scan(rows: list[dict]) -> tuple[list[dict],list[dict],dict]:
    grouped=defaultdict(list)
    for raw in rows:
        row=dict(raw)
        key=period_key(row)
        if not all(key):
            continue
        grouped[key].append(row)

    packing=[]
    movement=[]
    for key,period_rows in sorted(grouped.items()):
        packing.extend(packing_night_rows(period_rows))
        ms=movement_identity_summary(period_rows)
        movement.append({
            "year":key[0],
            "season":key[1],
            "watershed":key[2],
            "line":key[3],
            "trapline_id":trapline_id(key),
            **ms,
        })

    return packing,movement,summarize(packing,movement)


def _read_csv(path: Path) -> list[dict]:
    with path.open(newline="",encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:
        path.write_text("",encoding="utf-8")
        return
    fields=[]
    seen=set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fields.append(key)
    with path.open("w",newline="",encoding="utf-8") as fh:
        writer=csv.DictWriter(fh,fieldnames=fields,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()

    packing,movement,summary=scan(_read_csv(args.input))
    args.output_dir.mkdir(parents=True,exist_ok=True)
    _write_csv(args.output_dir/"konza_hispidus_packing_estimability_v1.csv",packing)
    _write_csv(args.output_dir/"konza_hispidus_movement_estimability_v1.csv",movement)
    (args.output_dir/"konza_hispidus_crossscale_estimability_v1.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(summary,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
