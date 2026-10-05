from __future__ import annotations
import csv, hashlib, json, urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path

URL="https://ndownloader.figshare.com/files/33058799"
SHA256="ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"
FOCAL=("CHFA","DKR","LAPM","PEER","PEMA","SKR")
FLAGS={f"{r}{c}" for r in "ABCDEFG" for c in range(1,8)}

def clean(x): return str(x or "").strip()
def pdate(x):
    s=clean(x)
    for fmt in ("%m/%d/%Y","%m/%d/%y","%Y-%m-%d","%m-%d-%Y","%m-%d-%y"):
        try:return datetime.strptime(s,fmt)
        except ValueError:pass
    return None
def season(m):
    if m in (8,9,10): return "fall"
    if m in (11,12,1): return "winter"
    if m in (2,3,4): return "spring"
    if m in (5,6,7): return "summer"

raw=urllib.request.urlopen(urllib.request.Request(URL,headers={"User-Agent":"neon-low-richness-audit/1.0"}),timeout=180).read()
assert hashlib.sha256(raw).hexdigest()==SHA256
rows=list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
out={}
for grid in ("3","7"):
    key=f"{grid}|winter"
    rec=defaultdict(lambda:{"rows":0,"valid_flag_rows":0,"flags":[],"dates":[],"raw_species_spellings":set()})
    for r in rows:
        if clean(r.get("grid"))!=grid: continue
        dt=pdate(r.get("date"))
        if dt is None or season(dt.month)!="winter": continue
        sp=clean(r.get("species")).upper()
        rr=rec[sp]
        rr["rows"]+=1
        rr["raw_species_spellings"].add(clean(r.get("species")))
        rr["dates"].append(clean(r.get("date")))
        fl=clean(r.get("flag")).upper()
        if fl in FLAGS:
            rr["valid_flag_rows"]+=1
            rr["flags"].append(fl)
    out[key]={}
    for sp,rr in sorted(rec.items()):
        out[key][sp]={
            "focal":sp in FOCAL,
            "rows":rr["rows"],
            "valid_flag_rows":rr["valid_flag_rows"],
            "unique_valid_flags":sorted(set(rr["flags"])),
            "date_min":min(rr["dates"]) if rr["dates"] else None,
            "date_max":max(rr["dates"]) if rr["dates"] else None,
            "raw_species_spellings":sorted(rr["raw_species_spellings"]),
        }
print(json.dumps(out,indent=2,sort_keys=True))
