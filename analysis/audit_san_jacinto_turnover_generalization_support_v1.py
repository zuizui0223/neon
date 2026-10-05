from __future__ import annotations
import argparse,csv,hashlib,json,re,urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path

URL="https://ndownloader.figshare.com/files/33058799"
SHA256="ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"
FOCAL=("CHFA","DKR","LAPM","PEER","PEMA","SKR")
FLAGS={f"{r}{c}" for r in "ABCDEFG" for c in range(1,8)}

def clean(x): return str(x or "").strip()
def parse_time(x):
    m=re.fullmatch(r"(\d{1,2}):(\d{2})",clean(x))
    if not m:return None
    h=int(m.group(1)); mi=int(m.group(2))
    if mi>=60:return None
    if 7<=h<=11:h+=12
    elif h==12:h=24
    elif 0<=h<=6:h+=24
    else:return None
    return h+mi/60
def parse_date(x):
    s=clean(x)
    for fmt in ("%m/%d/%Y","%m/%d/%y","%Y-%m-%d","%m-%d-%Y","%m-%d-%y"):
        try:return datetime.strptime(s,fmt)
        except ValueError:pass
    return None
def season(m):
    if m in (8,9,10):return "fall"
    if m in (11,12,1):return "winter"
    if m in (2,3,4):return "spring"
    if m in (5,6,7):return "summer"
    raise ValueError(m)
def download():
    req=urllib.request.Request(URL,headers={"User-Agent":"neon-turnover-generalization-support/1.0"})
    raw=urllib.request.urlopen(req,timeout=180).read()
    if hashlib.sha256(raw).hexdigest()!=SHA256:raise RuntimeError("checksum mismatch")
    return list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
def nightly_first(rows):
    g=defaultdict(list)
    for i,r in enumerate(rows):
        sp=clean(r.get("species")).upper(); grid=clean(r.get("grid")); uid=clean(r.get("unique_ID"))
        ds=clean(r.get("date")); fl=clean(r.get("flag")).upper(); tt=parse_time(r.get("time")); dd=parse_date(ds)
        if sp not in FOCAL or not grid or not uid or fl not in FLAGS or tt is None or dd is None:continue
        g[(sp,grid,uid,ds)].append((tt,i,fl,dd))
    out=[]
    for (sp,grid,uid,ds),items in g.items():
        x=min(items,key=lambda z:(z[0],z[1])); dd=x[3]
        out.append({"species":sp,"grid":grid,"uid":uid,"date_iso":dd.date().isoformat(),"season":season(dd.month),"flag":x[2]})
    return out
def split(z):
    dates=sorted({r["date_iso"] for r in z}); h=len(dates)//2
    if len(dates)%2==0:return set(dates[:h]),set(dates[h:]),None
    return set(dates[:h]),set(dates[h+1:]),dates[h]
def unit_support(z):
    eD,lD,mid=split(z); e=[r for r in z if r["date_iso"] in eD]; l=[r for r in z if r["date_iso"] in lD]
    bridge={(r["species"],r["uid"]) for r in e}&{(r["species"],r["uid"]) for r in l}
    e=[r for r in e if (r["species"],r["uid"]) not in bridge]; l=[r for r in l if (r["species"],r["uid"]) not in bridge]
    support=[]
    for sp in FOCAL:
        ei={r["uid"] for r in e if r["species"]==sp}; li={r["uid"] for r in l if r["species"]==sp}
        support.append({"species":sp,"early_only_individuals":len(ei),"late_only_individuals":len(li),
                        "early_only_records":sum(r["species"]==sp for r in e),"late_only_records":sum(r["species"]==sp for r in l)})
    eligible=[x["species"] for x in support if x["early_only_individuals"]>=1 and x["late_only_individuals"]>=1]
    return {"bridge_individuals_removed":len(bridge),"early_only_individuals":len({(r["species"],r["uid"]) for r in e}),
            "late_only_individuals":len({(r["species"],r["uid"]) for r in l}),"eligible_species":eligible,
            "eligible_species_count":len(eligible),"species_support":support,"early_nights":len(eD),"late_nights":len(lD),"discarded_middle":mid}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--stage5",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);args=ap.parse_args()
    s5=json.loads(args.stage5.read_text()); ids=[u["id"] for u in s5["units"]]
    nf=nightly_first(download()); by=defaultdict(list)
    for r in nf:by[f'{r["grid"]}|{r["season"]}'].append(r)
    units=[]
    for id in ids:
        x=unit_support(by[id]); grid,sea=id.split("|")
        units.append({"id":id,"grid":grid,"season":sea,"stage4_reference":next(u["stage4_reference"] for u in s5["units"] if u["id"]==id),**x})
    elig=[u for u in units if u["eligible_species_count"]>=3]
    result={"schema":"neon.san_jacinto_turnover_generalization_support.v1",
      "status":"support_only_no_post_turnover_overlap_opened",
      "source_universe":"22 units already eligible in frozen Stage5 temporal-persistence analysis",
      "units":units,
      "summary":{"source_units":len(units),"turnover_eligible_units":len(elig),"turnover_eligible_physical_grids":len({u["grid"] for u in elig}),
                 "reference_turnover_eligible_units":sum(u["stage4_reference"] and u["eligible_species_count"]>=3 for u in units),
                 "bridge_individuals_removed_total":sum(u["bridge_individuals_removed"] for u in units)},
      "claim_boundary":{"overlap_opened":False,"null_opened":False,"effect_direction_opened":False}}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__":main()
