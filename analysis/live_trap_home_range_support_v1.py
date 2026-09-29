from __future__ import annotations
import argparse,csv,hashlib,json,re,urllib.request
from collections import defaultdict
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
    h=int(m.group(1)); minute=int(m.group(2))
    if minute>=60: return None
    if 7<=h<=11: h+=12
    elif h==12: h=24
    elif 0<=h<=6: h+=24
    else: return None
    return h+minute/60

def cross(o,a,b):
    return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])

def noncollinear(flags):
    pts=sorted({XY[f] for f in flags})
    if len(pts)<3: return False
    for i in range(1,len(pts)-1):
        for j in range(i+1,len(pts)):
            if abs(cross(pts[0],pts[i],pts[j]))>1e-12: return True
    return False

def nightly_representations(rows):
    grouped=defaultdict(list)
    for idx,row in enumerate(rows):
        sp=clean(row.get("species"))
        if sp not in SPECIES: continue
        grid=clean(row.get("grid")); uid=clean(row.get("unique_ID"))
        date=clean(row.get("date")); flag=clean(row.get("flag")).upper()
        t=parse_time(row.get("time"))
        if not grid or not uid or not date or flag not in FLAGS or t is None: continue
        grouped[(sp,grid,uid,date)].append((t,idx,flag))
    first={}; last={}
    for key,items in grouped.items():
        ordered=sorted(items)
        first[key]=ordered[0][2]; last[key]=ordered[-1][2]
    return first,last

def count_support(rows,lock):
    first,last=nightly_representations(rows)
    ids=sorted({k[:3] for k in first})
    details={sp:[] for sp in SPECIES}
    for sp,grid,uid in ids:
        keys=sorted(k for k in first if k[:3]==(sp,grid,uid))
        f=[first[k] for k in keys]; l=[last[k] for k in keys]
        nf=noncollinear(f); nl=noncollinear(l)
        eligible=(
            len(keys)>=int(lock["eligibility"]["distinct_capture_nights_min"])
            and len(set(f))>=int(lock["eligibility"]["unique_flags_first_min"])
            and len(set(l))>=int(lock["eligibility"]["unique_flags_last_min"])
            and nf and nl
        )
        details[sp].append({
            "grid":grid,"unique_ID":uid,"capture_nights":len(keys),
            "unique_flags_first":len(set(f)),"unique_flags_last":len(set(l)),
            "noncollinear_first":nf,"noncollinear_last":nl,"eligible":eligible
        })
    counts={sp:sum(bool(r["eligible"]) for r in rs) for sp,rs in details.items()}
    passed=(
        counts["PEMA"]>=int(lock["species_support_gate"]["PEMA_min_individuals"])
        and counts["PEER"]>=int(lock["species_support_gate"]["PEER_min_individuals"])
    )
    return {
      "schema":"neon.live_trap_aliasing.downstream_home_range_estimability.v1",
      "eligible_individuals":counts,
      "candidate_individuals":{sp:len(v) for sp,v in details.items()},
      "species_details":details,
      "programme_gate":{"passed":passed,"decision":lock["pass_decision"] if passed else lock["fail_decision"]},
      "first_area_inspected":False,"last_area_inspected":False,
      "area_differences_inspected":False,"rms_radius_differences_inspected":False,
      "ecological_model_fits":0
    }

def download():
    req=urllib.request.Request(URL,headers={"User-Agent":"live-trap-home-range-support/1.0"})
    with urllib.request.urlopen(req,timeout=180) as r: raw=r.read()
    if hashlib.sha256(raw).hexdigest()!=SHA256: raise RuntimeError("source checksum mismatch")
    return list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--lock",type=Path,required=True); ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    lock=json.loads(a.lock.read_text())
    if lock["state"]!="frozen_before_home_range_support_counts": raise RuntimeError("lock not frozen")
    out=count_support(download(),lock)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"eligible_individuals":out["eligible_individuals"],"programme_gate":out["programme_gate"]},indent=2))
if __name__=="__main__": main()
