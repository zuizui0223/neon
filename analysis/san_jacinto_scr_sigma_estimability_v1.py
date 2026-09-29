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

FOCAL={
    "PEMA":"Peromyscus maniculatus",
    "PEER":"Peromyscus eremicus",
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


def build_bouts(rows: list[dict]) -> tuple[dict[str,int],list[dict]]:
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
    summary=[]
    for i,bout in enumerate(bouts,1):
        for d in bout:
            mapping[d.isoformat()]=i
        summary.append({
            "bout_id":i,
            "start":bout[0].isoformat(),
            "end":bout[-1].isoformat(),
            "occasion_count":len(bout),
        })
    return mapping,summary


def prepare(rows: list[dict]) -> tuple[list[dict],dict]:
    date_to_bout,bout_summary=build_bouts(rows)
    valid=[]
    excluded=Counter()
    for index,row in enumerate(rows):
        species=clean(row.get("species"))
        if species not in FOCAL:
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
    return valid,{
        "excluded_rows":dict(excluded),
        "bout_summary":bout_summary,
        "valid_rows":len(valid),
    }


def session_support(rows: list[dict]) -> tuple[list[dict],dict]:
    valid,qc=prepare(rows)
    grouped=defaultdict(list)
    for row in valid:
        grouped[(row["species"],row["grid"],row["bout_id"])].append(row)

    sessions=[]
    for (species,grid,bout),items in sorted(grouped.items()):
        dates=sorted({x["date"] for x in items})
        individuals={x["unique_ID"] for x in items}

        by_id=defaultdict(list)
        for x in items:
            by_id[x["unique_ID"]].append(x)

        temporal=0
        spatial=0
        for uid,obs in by_id.items():
            by_date=defaultdict(set)
            for x in obs:
                by_date[x["date"]].add(x["flag"])
            if len(by_date)>=2:
                temporal+=1
                date_sets=list(by_date.values())
                # Effect-blind raw spatial support: there exists at least one
                # pair of different dates whose possible observed flag sets
                # are not identical.
                if any(
                    date_sets[i] != date_sets[j]
                    for i in range(len(date_sets))
                    for j in range(i+1,len(date_sets))
                ):
                    spatial+=1

        eligible=(
            len(dates)>=2
            and len(individuals)>=10
            and temporal>=5
            and spatial>=3
        )
        sessions.append({
            "species":species,
            "scientific_name":FOCAL[species],
            "grid":grid,
            "bout_id":bout,
            "occasion_count":len(dates),
            "dates":";".join(dates),
            "unique_individuals":len(individuals),
            "temporal_recapture_individuals":temporal,
            "raw_interdate_spatial_recapture_individuals":spatial,
            "eligible":eligible,
        })

    species_summary={}
    qualifying=[]
    for species,name in FOCAL.items():
        s=[x for x in sessions if x["species"]==species]
        e=[x for x in s if x["eligible"]]
        grids={x["grid"] for x in e}
        passed=len(e)>=5 and len(grids)>=2
        if passed:
            qualifying.append(species)
        species_summary[species]={
            "scientific_name":name,
            "candidate_sessions":len(s),
            "eligible_sessions":len(e),
            "eligible_grids":len(grids),
            "eligible_grid_counts":dict(sorted(
                Counter(x["grid"] for x in e).items()
            )),
            "eligible_session_ids":[
                f"{x['grid']}:bout{x['bout_id']}" for x in e
            ],
            "species_gate_passed":passed,
        }

    passed=len(qualifying)==len(FOCAL)
    result={
        "schema":"neon.san_jacinto_scr_sigma_sensitivity.estimability_result.v1",
        "species":species_summary,
        "programme_gate":{
            "qualifying_species":qualifying,
            "both_species_required":True,
            "passed":passed,
            "decision":(
                "authorize_scr_sigma_sensitivity_fit"
                if passed else
                "stop_scr_sigma_sensitivity_not_estimable"
            ),
        },
        "qc":qc,
        "species_session_support_counts_inspected":True,
        "first_sigma_inspected":False,
        "last_sigma_inspected":False,
        "sigma_ratio_inspected":False,
        "scr_models_fit":0,
    }
    return sessions,result


def download_rows(path: Path) -> list[dict]:
    req=urllib.request.Request(
        DOWNLOAD_URL,
        headers={"User-Agent":"san-jacinto-scr-sigma-estimability/1.0"},
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
        writer=csv.DictWriter(fh,fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--lock",type=Path,required=True)
    parser.add_argument("--cache",type=Path,required=True)
    parser.add_argument("--output-json",type=Path,required=True)
    parser.add_argument("--output-csv",type=Path,required=True)
    args=parser.parse_args()

    lock=json.loads(args.lock.read_text())
    if lock["state"]!="frozen_before_session_support_counts":
        raise RuntimeError("estimability lock not frozen")
    if lock["species_session_support_counts_inspected"]:
        raise RuntimeError("lock says support counts already inspected")

    rows=download_rows(args.cache)
    sessions,result=session_support(rows)
    args.output_json.parent.mkdir(parents=True,exist_ok=True)
    args.output_json.write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    write_csv(args.output_csv,sessions)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
