from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path

URL = "https://ndownloader.figshare.com/files/33058799"
SHA256 = "ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"
FOCAL = ("CHFA","DKR","LAPM","PEER","PEMA","SKR")
FLAGS = {f"{r}{c}" for r in "ABCDEFG" for c in range(1,8)}
EXCLUDED = {("3","winter"),("7","winter")}
REFERENCE = {
    ("1","summer"),
    ("4","fall"),("4","winter"),("4","spring"),("4","summer"),
    ("6","fall"),("6","winter"),("6","summer"),
}

def clean(x: object) -> str:
    return str(x or "").strip()

def parse_time(x: object) -> float | None:
    m = re.fullmatch(r"(\d{1,2}):(\d{2})", clean(x))
    if not m:
        return None
    h = int(m.group(1)); minute = int(m.group(2))
    if minute >= 60:
        return None
    if 7 <= h <= 11:
        h += 12
    elif h == 12:
        h = 24
    elif 0 <= h <= 6:
        h += 24
    else:
        return None
    return h + minute/60

def parse_date(x: object) -> datetime | None:
    s = clean(x)
    for fmt in ("%m/%d/%Y","%m/%d/%y","%Y-%m-%d","%m-%d-%Y","%m-%d-%y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None

def season(month: int) -> str:
    if month in (8,9,10): return "fall"
    if month in (11,12,1): return "winter"
    if month in (2,3,4): return "spring"
    if month in (5,6,7): return "summer"
    raise ValueError(month)

def download_rows() -> list[dict]:
    req=urllib.request.Request(URL,headers={"User-Agent":"neon-stage5-persistence-support/1.0"})
    with urllib.request.urlopen(req,timeout=180) as response:
        raw=response.read()
    actual=hashlib.sha256(raw).hexdigest()
    if actual!=SHA256:
        raise RuntimeError(f"checksum mismatch: {actual}")
    return list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))

def nightly_first(rows: list[dict]) -> list[dict]:
    groups=defaultdict(list)
    for idx,row in enumerate(rows):
        sp=clean(row.get("species")).upper()
        grid=clean(row.get("grid"))
        uid=clean(row.get("unique_ID"))
        date_s=clean(row.get("date"))
        flag=clean(row.get("flag")).upper()
        tt=parse_time(row.get("time"))
        dd=parse_date(date_s)
        if sp not in FOCAL or not grid or not uid or flag not in FLAGS or tt is None or dd is None:
            continue
        groups[(sp,grid,uid,date_s)].append((tt,idx,flag,dd))
    out=[]
    for (sp,grid,uid,date_s),items in groups.items():
        first=min(items,key=lambda z:(z[0],z[1]))
        dd=first[3]
        out.append({
            "species":sp,"grid":grid,"uid":uid,"date":date_s,
            "date_iso":dd.date().isoformat(),"season":season(dd.month),
            "flag":first[2],
        })
    return out

def split_dates(date_isos: list[str]) -> tuple[set[str],set[str],str|None]:
    dates=sorted(set(date_isos))
    n=len(dates)
    half=n//2
    if n % 2 == 0:
        return set(dates[:half]),set(dates[half:]),None
    return set(dates[:half]),set(dates[half+1:]),dates[half]

def summarize(rows: list[dict]) -> dict:
    nf=nightly_first(rows)
    units=defaultdict(list)
    for r in nf:
        key=(r["grid"],r["season"])
        if key in EXCLUDED:
            continue
        units[key].append(r)

    out=[]
    for grid in map(str,range(1,9)):
        for sea in ("fall","winter","spring","summer"):
            key=(grid,sea)
            if key in EXCLUDED:
                continue
            z=units.get(key,[])
            dates=[r["date_iso"] for r in z]
            early,late,discarded=split_dates(dates) if dates else (set(),set(),None)
            ez=[r for r in z if r["date_iso"] in early]
            lz=[r for r in z if r["date_iso"] in late]
            esp=sorted({r["species"] for r in ez})
            lsp=sorted({r["species"] for r in lz})
            common=sorted(set(esp)&set(lsp))
            out.append({
                "id":f"{grid}|{sea}",
                "grid":grid,
                "season":sea,
                "stage4_reference":key in REFERENCE,
                "unique_calendar_nights_total":len(set(dates)),
                "early_nights":len(early),
                "late_nights":len(late),
                "discarded_middle_night":discarded,
                "early_nightly_first_records":len(ez),
                "late_nightly_first_records":len(lz),
                "early_species":esp,
                "late_species":lsp,
                "common_species":common,
                "common_species_count":len(common),
                "common_species_with_ge2_records_each_half":[
                    sp for sp in common
                    if sum(r["species"]==sp for r in ez)>=2 and sum(r["species"]==sp for r in lz)>=2
                ],
            })

    return {
        "schema":"neon.san_jacinto_stage5_persistence_support.v1",
        "status":"support_only_no_spatial_overlap_outcomes_opened",
        "split_rule":"chronological unique calendar nights within grid-season; if odd, discard the single middle night",
        "excluded_public_source_mismatch_units":["3|winter","7|winter"],
        "stage4_reference_ids":sorted(f"{g}|{s}" for g,s in REFERENCE),
        "units":out,
        "summary":{
            "public30_units":len(out),
            "units_with_ge4_nights":sum(u["unique_calendar_nights_total"]>=4 for u in out),
            "units_with_ge3_common_species":sum(u["common_species_count"]>=3 for u in out),
            "reference_units_with_ge3_common_species":sum(u["stage4_reference"] and u["common_species_count"]>=3 for u in out),
            "units_with_ge3_common_species_ge2_records_each_half":sum(
                len(u["common_species_with_ge2_records_each_half"])>=3 for u in out
            ),
            "reference_units_with_ge3_common_species_ge2_records_each_half":sum(
                u["stage4_reference"] and len(u["common_species_with_ge2_records_each_half"])>=3 for u in out
            ),
        },
        "claim_boundary":{
            "trap_overlap_opened":False,
            "persistence_statistic_opened":False,
            "fixed_fixed_null_opened":False,
            "stage4_classification_retested":False,
        }
    }

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    result=summarize(download_rows())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
