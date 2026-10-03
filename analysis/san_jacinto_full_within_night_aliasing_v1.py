from __future__ import annotations

import argparse, csv, hashlib, json, math, re, urllib.request
from collections import defaultdict, Counter
from pathlib import Path

SPECIES={"PEMA":"Peromyscus maniculatus","PEER":"Peromyscus eremicus"}
FLAGS={f"{r}{c}" for r in "ABCDEFG" for c in range(1,8)}
XY={f"{r}{c}":((c-1)*6.25,i*6.25) for i,r in enumerate("ABCDEFG") for c in range(1,8)}
URL="https://ndownloader.figshare.com/files/33058799"
SHA256="ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"

def clean(x): return str(x or "").strip()
def parse_time(x):
    m=re.fullmatch(r"(\d{1,2}):(\d{2})",clean(x))
    if not m: return None
    h,mi=map(int,m.groups())
    if mi>=60: return None
    if 7<=h<=11: h+=12
    elif h==12: h=24
    elif 0<=h<=6: h+=24
    else: return None
    return h+mi/60

def dist(a,b):
    x1,y1=XY[a]; x2,y2=XY[b]
    return math.hypot(x2-x1,y2-y1)

def download(path):
    req=urllib.request.Request(URL,headers={"User-Agent":"san-jacinto-full-history-audit/1.0"})
    raw=urllib.request.urlopen(req,timeout=180).read()
    actual=hashlib.sha256(raw).hexdigest()
    if actual!=SHA256: raise RuntimeError(actual)
    path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(raw)
    return list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))

def audit(rows):
    groups=defaultdict(list)
    for idx,row in enumerate(rows):
        sp=clean(row.get("species"))
        if sp not in SPECIES: continue
        uid=clean(row.get("unique_ID")); grid=clean(row.get("grid")); date=clean(row.get("date"))
        flag=clean(row.get("flag")).upper(); t=parse_time(row.get("time"))
        if not uid or not grid or not date or flag not in FLAGS or t is None: continue
        groups[(sp,grid,uid,date)].append((t,idx,flag))
    out=[]
    for (sp,grid,uid,date),obs in sorted(groups.items()):
        if len(obs)<2: continue
        obs=sorted(obs)
        fs=[x[2] for x in obs]
        first,last=fs[0],fs[-1]
        unique=list(dict.fromkeys(fs))
        pairmax=max(dist(a,b) for a in fs for b in fs)
        firstlast=dist(first,last)
        out.append({
            "species":sp,"grid":grid,"unique_ID":uid,"date":date,
            "capture_count":len(fs),"unique_trap_count":len(set(fs)),
            "first_flag":first,"last_flag":last,
            "first_last_distance_m":firstlast,
            "max_pairwise_distance_m":pairmax,
            "first_last_changed":first!=last,
            "any_cross_trap_conflict":len(set(fs))>1,
            "returned_to_first_after_other_trap":(
                first==last and any(f!=first for f in fs[1:-1])
            ),
            "trap_sequence":"->".join(fs),
        })
    return out

def summarize(rows):
    ans={}
    for sp,name in SPECIES.items():
        z=[r for r in rows if r["species"]==sp]
        n=len(z)
        fl=sum(r["first_last_changed"] for r in z)
        anyc=sum(r["any_cross_trap_conflict"] for r in z)
        ret=sum(r["returned_to_first_after_other_trap"] for r in z)
        hidden=[r for r in z if r["any_cross_trap_conflict"] and not r["first_last_changed"]]
        ans[sp]={
            "scientific_name":name,
            "repeat_nights":n,
            "first_last_change_count":fl,
            "first_last_change_fraction":fl/n,
            "any_cross_trap_conflict_count":anyc,
            "any_cross_trap_conflict_fraction":anyc/n,
            "endpoint_false_negative_count":len(hidden),
            "endpoint_false_negative_fraction_all_repeat_nights":len(hidden)/n,
            "fraction_of_cross_trap_conflicts_missed_by_first_last":len(hidden)/anyc if anyc else 0,
            "returned_to_first_after_other_trap_count":ret,
            "capture_count_distribution":dict(sorted(Counter(r["capture_count"] for r in z).items())),
            "unique_trap_count_distribution":dict(sorted(Counter(r["unique_trap_count"] for r in z).items())),
        }
    allz=rows; n=len(allz); fl=sum(r["first_last_changed"] for r in allz); anyc=sum(r["any_cross_trap_conflict"] for r in allz)
    hidden=[r for r in allz if r["any_cross_trap_conflict"] and not r["first_last_changed"]]
    ans["COMBINED"]={
        "repeat_nights":n,
        "first_last_change_count":fl,"first_last_change_fraction":fl/n,
        "any_cross_trap_conflict_count":anyc,"any_cross_trap_conflict_fraction":anyc/n,
        "endpoint_false_negative_count":len(hidden),
        "endpoint_false_negative_fraction_all_repeat_nights":len(hidden)/n,
        "fraction_of_cross_trap_conflicts_missed_by_first_last":len(hidden)/anyc if anyc else 0,
    }
    return ans

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--cache",type=Path,required=True)
    ap.add_argument("--json",type=Path,required=True)
    ap.add_argument("--csv",type=Path,required=True)
    a=ap.parse_args()
    rows=audit(download(a.cache)); s=summarize(rows)
    result={
      "schema":"neon.san_jacinto_full_within_night_aliasing.v1",
      "source_sha256":SHA256,
      "species":s,
      "claim_boundary":{
        "descriptive_post_holdout_audit":True,
        "does_not_reopen_scr_sigma_stop":True,
        "first_last_is_endpoint_only":True,
      }
    }
    a.json.parent.mkdir(parents=True,exist_ok=True)
    a.json.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    with a.csv.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__": main()
