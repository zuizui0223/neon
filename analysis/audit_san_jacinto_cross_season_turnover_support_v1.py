from __future__ import annotations

import argparse, csv, hashlib, json, re, urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path

URL="https://ndownloader.figshare.com/files/33058799"
SHA256="ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"
FOCAL=("CHFA","DKR","LAPM","PEER","PEMA","SKR")
FLAGS={f"{r}{c}" for r in "ABCDEFG" for c in range(1,8)}
SEASON_ORDER=("fall","winter","spring","summer")
SEASON_PAIRS=(("fall","winter"),("winter","spring"),("spring","summer"))

def clean(x): return str(x or "").strip()

def parse_time(x):
    m=re.fullmatch(r"(\d{1,2}):(\d{2})",clean(x))
    if not m: return None
    h=int(m.group(1)); minute=int(m.group(2))
    if minute>=60: return None
    if 7<=h<=11: h+=12
    elif h==12: h=24
    elif 0<=h<=6: h+=24
    else: return None
    return h+minute/60

def parse_date(x):
    s=clean(x)
    for fmt in ("%m/%d/%Y","%m/%d/%y","%Y-%m-%d","%m-%d-%Y","%m-%d-%y"):
        try: return datetime.strptime(s,fmt)
        except ValueError: pass
    return None

def season(m):
    if m in (8,9,10): return "fall"
    if m in (11,12,1): return "winter"
    if m in (2,3,4): return "spring"
    if m in (5,6,7): return "summer"
    raise ValueError(m)

def download_rows():
    req=urllib.request.Request(URL,headers={"User-Agent":"neon-cross-season-support/1.0"})
    raw=urllib.request.urlopen(req,timeout=180).read()
    if hashlib.sha256(raw).hexdigest()!=SHA256: raise RuntimeError("checksum mismatch")
    return list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))

def nightly_first(rows):
    groups=defaultdict(list)
    for idx,row in enumerate(rows):
        sp=clean(row.get("species")).upper(); grid=clean(row.get("grid"))
        uid=clean(row.get("unique_ID")); ds=clean(row.get("date"))
        flag=clean(row.get("flag")).upper(); tt=parse_time(row.get("time")); dd=parse_date(ds)
        if sp not in FOCAL or not grid or not uid or flag not in FLAGS or tt is None or dd is None: continue
        groups[(sp,grid,uid,ds)].append((tt,idx,flag,dd))
    out=[]
    for (sp,grid,uid,ds),items in groups.items():
        first=min(items,key=lambda z:(z[0],z[1])); dd=first[3]
        out.append({"species":sp,"grid":grid,"uid":uid,"date_iso":dd.date().isoformat(),
                    "season":season(dd.month),"flag":first[2]})
    return out

def summarize(rows):
    nf=nightly_first(rows)
    units=[]
    for grid in map(str,range(1,9)):
        gz=[r for r in nf if r["grid"]==grid]
        for a,b in SEASON_PAIRS:
            za=[r for r in gz if r["season"]==a]
            zb=[r for r in gz if r["season"]==b]
            aids={(r["species"],r["uid"]) for r in za}
            bids={(r["species"],r["uid"]) for r in zb}
            bridge=aids & bids
            aa=[r for r in za if (r["species"],r["uid"]) not in bridge]
            bb=[r for r in zb if (r["species"],r["uid"]) not in bridge]
            ss=[]
            for sp in FOCAL:
                ar=[r for r in aa if r["species"]==sp]
                br=[r for r in bb if r["species"]==sp]
                ai={r["uid"] for r in ar}; bi={r["uid"] for r in br}
                ss.append({
                    "species":sp,
                    "season_a_individuals":len(ai),"season_b_individuals":len(bi),
                    "season_a_records":len(ar),"season_b_records":len(br),
                    "season_a_traps":len({r["flag"] for r in ar}),
                    "season_b_traps":len({r["flag"] for r in br}),
                    "bridge_individuals_removed":sum(1 for s,_ in bridge if s==sp),
                })
            common1=[x["species"] for x in ss if x["season_a_individuals"]>=1 and x["season_b_individuals"]>=1]
            common2=[x["species"] for x in ss if x["season_a_individuals"]>=2 and x["season_b_individuals"]>=2]
            common2r=[x["species"] for x in ss if x["season_a_records"]>=2 and x["season_b_records"]>=2]
            units.append({
                "id":f"{grid}|{a}->{b}","grid":grid,"season_a":a,"season_b":b,
                "bridge_individuals_removed":len(bridge),
                "season_a_exclusive_individuals":len({(r["species"],r["uid"]) for r in aa}),
                "season_b_exclusive_individuals":len({(r["species"],r["uid"]) for r in bb}),
                "common_species_ge1_individual_each":common1,
                "common_species_ge2_individuals_each":common2,
                "common_species_ge2_records_each":common2r,
                "species_support":ss,
            })
    eligible1=[u for u in units if len(u["common_species_ge1_individual_each"])>=3]
    eligible2=[u for u in units if len(u["common_species_ge2_individuals_each"])>=3]
    grids1=sorted({u["grid"] for u in eligible1})
    grids2=sorted({u["grid"] for u in eligible2})
    return {
        "schema":"neon.san_jacinto_cross_season_turnover_support.v1",
        "status":"support_only_complete_cross_season_individual_turnover_no_spatial_overlap_opened",
        "representation":"NIGHT_FIRST",
        "season_pairs":["fall->winter","winter->spring","spring->summer"],
        "removal_rule":"remove from BOTH seasons every species x individual ID observed in both seasons before any spatial-overlap statistic",
        "units":units,
        "summary":{
            "candidate_grid_season_pairs":len(units),
            "pairs_with_ge3_common_species_ge1_individual_each":len(eligible1),
            "physical_grids_with_ge1_eligible_pair_ge1_rule":len(grids1),
            "eligible_physical_grids_ge1_rule":grids1,
            "pairs_with_ge3_common_species_ge2_individuals_each":len(eligible2),
            "physical_grids_with_ge1_eligible_pair_ge2_rule":len(grids2),
            "eligible_physical_grids_ge2_rule":grids2,
            "bridge_individuals_removed_total":sum(u["bridge_individuals_removed"] for u in units),
        },
        "claim_boundary":{
            "cross_season_overlap_opened":False,
            "fixed_fixed_null_opened":False,
            "effect_direction_opened":False,
            "eligibility_threshold_selected_from_outcome":False,
        }
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path,required=True); args=ap.parse_args()
    x=summarize(download_rows()); args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(x,indent=2,sort_keys=True))
if __name__=="__main__": main()
