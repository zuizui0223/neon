from __future__ import annotations

import argparse, csv, hashlib, json, re, urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

URL="https://ndownloader.figshare.com/files/33058799"
SHA256="ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"
FOCAL=("CHFA","DKR","LAPM","PEER","PEMA","SKR")
FLAGS={f"{r}{c}" for r in "ABCDEFG" for c in range(1,8)}

def clean(x): return str(x or "").strip()

def parse_date(s):
    s=clean(s)
    fmts=("%m/%d/%Y","%m/%d/%y","%Y-%m-%d","%m-%d-%Y","%m-%d-%y")
    for fmt in fmts:
        try: return datetime.strptime(s,fmt)
        except ValueError: pass
    return None

def season(month):
    if month in (8,9,10): return "fall"
    if month in (11,12,1): return "winter"
    if month in (2,3,4): return "spring"
    if month in (5,6,7): return "summer"
    raise ValueError(month)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    req=urllib.request.Request(URL,headers={"User-Agent":"neon-stage3-support-audit/1.0"})
    raw=urllib.request.urlopen(req,timeout=180).read()
    if hashlib.sha256(raw).hexdigest()!=SHA256: raise RuntimeError("checksum mismatch")
    rows=list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))

    invalid_dates=Counter()
    focal_raw=Counter()
    focal_valid_date=Counter()
    per_unit=defaultdict(Counter)
    per_unit_rows=defaultdict(Counter)
    target_records=[]

    for row in rows:
        sp=clean(row.get("species")).upper()
        if sp not in FOCAL: continue
        focal_raw[sp]+=1
        ds=clean(row.get("date"))
        d=parse_date(ds)
        if d is None:
            invalid_dates[ds]+=1
            continue
        focal_valid_date[sp]+=1
        g=clean(row.get("grid"))
        seas=season(d.month)
        fl=clean(row.get("flag")).upper()
        if g and fl in FLAGS:
            per_unit[(g,seas)][sp]+=1
            per_unit_rows[(g,seas)][sp]+=1
        if g in {"3","7"} and seas=="winter":
            target_records.append({
                "grid":g,"species":sp,"date":ds,"flag":fl,
                "time":clean(row.get("time")),
                "has_unique_id":bool(clean(row.get("unique_ID")))
            })

    units=[]
    for g in map(str,range(1,9)):
        for s in ("fall","winter","spring","summer"):
            counts=per_unit[(g,s)]
            units.append({
                "grid":g,"season":s,
                "species_with_valid_spatial_rows":sorted(counts),
                "species_count":len(counts),
                "row_counts":dict(sorted(counts.items())),
                "pema_present":"PEMA" in counts,
            })

    out={
        "schema":"neon.san_jacinto_published_matrix_support_audit.v1",
        "status":"support_only_no_cscore_or_null_outcome",
        "raw_rows":len(rows),
        "focal_raw_rows":dict(focal_raw),
        "focal_valid_date_rows":dict(focal_valid_date),
        "invalid_focal_date_strings":dict(invalid_dates),
        "grid_seasons":units,
        "target_grid3_grid7_winter_records":target_records,
        "checks":{
            "all_32_have_at_least_3_species":all(u["species_count"]>=3 for u in units),
            "pema_present_all_32":all(u["pema_present"] for u in units),
        }
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__": main()
