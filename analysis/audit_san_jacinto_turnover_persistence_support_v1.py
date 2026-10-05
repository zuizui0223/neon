from __future__ import annotations

import argparse, csv, hashlib, json, re, urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path

URL="https://ndownloader.figshare.com/files/33058799"
SHA256="ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"
FOCAL=("CHFA","DKR","LAPM","PEER","PEMA","SKR")
FLAGS={f"{r}{c}" for r in "ABCDEFG" for c in range(1,8)}
REFERENCE={
 ("1","summer"),
 ("4","fall"),("4","winter"),("4","spring"),("4","summer"),
 ("6","fall"),("6","winter"),("6","summer"),
}

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
    req=urllib.request.Request(URL,headers={"User-Agent":"neon-turnover-support/1.0"})
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

def split_dates(rows):
    dates=sorted({r["date_iso"] for r in rows}); n=len(dates); h=n//2
    if n%2==0: return set(dates[:h]),set(dates[h:]),None
    return set(dates[:h]),set(dates[h+1:]),dates[h]

def summarize(rows):
    nf=nightly_first(rows)
    units=defaultdict(list)
    for r in nf:
        k=(r["grid"],r["season"])
        if k in REFERENCE: units[k].append(r)

    out=[]
    for grid,sea in sorted(REFERENCE):
        z=units[(grid,sea)]
        early_dates,late_dates,middle=split_dates(z)
        e=[r for r in z if r["date_iso"] in early_dates]
        l=[r for r in z if r["date_iso"] in late_dates]

        eids={(r["species"],r["uid"]) for r in e}
        lids={(r["species"],r["uid"]) for r in l}
        bridge=eids & lids
        e2=[r for r in e if (r["species"],r["uid"]) not in bridge]
        l2=[r for r in l if (r["species"],r["uid"]) not in bridge]

        sp=[]
        for s in FOCAL:
            er=[r for r in e2 if r["species"]==s]; lr=[r for r in l2 if r["species"]==s]
            ei={r["uid"] for r in er}; li={r["uid"] for r in lr}
            sp.append({
              "species":s,
              "early_only_records":len(er),"late_only_records":len(lr),
              "early_only_individuals":len(ei),"late_only_individuals":len(li),
              "early_only_traps":len({r["flag"] for r in er}),
              "late_only_traps":len({r["flag"] for r in lr}),
              "bridge_individuals_removed":sum(1 for ss,_ in bridge if ss==s),
            })
        out.append({
          "id":f"{grid}|{sea}","grid":grid,"season":sea,
          "early_nights":len(early_dates),"late_nights":len(late_dates),"discarded_middle_night":middle,
          "early_records_before_bridge_removal":len(e),"late_records_before_bridge_removal":len(l),
          "bridge_individuals_removed":len(bridge),
          "early_only_records_after_bridge_removal":len(e2),"late_only_records_after_bridge_removal":len(l2),
          "early_only_individuals":len({(r["species"],r["uid"]) for r in e2}),
          "late_only_individuals":len({(r["species"],r["uid"]) for r in l2}),
          "species_support":sp,
          "species_with_ge1_individual_each_half":[x["species"] for x in sp if x["early_only_individuals"]>=1 and x["late_only_individuals"]>=1],
          "species_with_ge2_individuals_each_half":[x["species"] for x in sp if x["early_only_individuals"]>=2 and x["late_only_individuals"]>=2],
          "species_with_ge2_records_each_half":[x["species"] for x in sp if x["early_only_records"]>=2 and x["late_only_records"]>=2],
        })
    return {
      "schema":"neon.san_jacinto_turnover_persistence_support.v1",
      "status":"support_only_bridge_individuals_removed_no_overlap_outcomes_opened",
      "reference_units":[f"{g}|{s}" for g,s in sorted(REFERENCE)],
      "split_rule":"same chronological equal-half split as frozen Stage-5 persistence; discard middle night when odd",
      "removal_rule":"remove from BOTH halves every species x individual ID observed at least once in both EARLY and LATE",
      "units":out,
      "summary":{
        "reference_units":len(out),
        "units_with_ge3_species_ge1_individual_each_half":sum(len(u["species_with_ge1_individual_each_half"])>=3 for u in out),
        "units_with_ge3_species_ge2_individuals_each_half":sum(len(u["species_with_ge2_individuals_each_half"])>=3 for u in out),
        "units_with_ge3_species_ge2_records_each_half":sum(len(u["species_with_ge2_records_each_half"])>=3 for u in out),
        "bridge_individuals_removed_total":sum(u["bridge_individuals_removed"] for u in out),
        "early_only_individuals_total":sum(u["early_only_individuals"] for u in out),
        "late_only_individuals_total":sum(u["late_only_individuals"] for u in out),
      },
      "claim_boundary":{
        "trap_overlap_opened":False,"turnover_persistence_statistic_opened":False,
        "fixed_fixed_null_opened":False,"threshold_selected_from_outcome":False
      }
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path,required=True); args=ap.parse_args()
    x=summarize(download_rows()); args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n"); print(json.dumps(x,indent=2,sort_keys=True))
if __name__=="__main__": main()
