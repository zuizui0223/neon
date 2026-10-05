from __future__ import annotations
import csv, hashlib, json, re, urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

URL="https://ndownloader.figshare.com/files/33058799"
SHA256="ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"
FOCAL={"CHFA","DKR","LAPM","PEER","PEMA","SKR"}
FLAGS={f"{r}{c}" for r in "ABCDEFG" for c in range(1,8)}
TARGETS={("3","winter"),("7","winter")}

def clean(x): return str(x or "").strip()

def parse_date(s):
    s=clean(s)
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

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    req=urllib.request.Request(URL,headers={"User-Agent":"neon-stage3-roster-audit/1.0"})
    raw=urllib.request.urlopen(req,timeout=180).read()
    if hashlib.sha256(raw).hexdigest()!=SHA256:
        raise RuntimeError("checksum mismatch")
    rows=list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    out={}
    for grid,seas in sorted(TARGETS):
        raw_counts=Counter()
        valid_flag_counts=Counter()
        invalid_flag_counts=Counter()
        date_parse_fail=Counter()
        flags_by_species=defaultdict(set)
        dates_by_species=defaultdict(set)
        for r in rows:
            if clean(r.get("grid"))!=grid: continue
            sp=clean(r.get("species")).upper()
            dt=parse_date(r.get("date"))
            if dt is None:
                date_parse_fail[sp]+=1
                continue
            if season(dt.month)!=seas: continue
            raw_counts[sp]+=1
            flag=clean(r.get("flag")).upper()
            dates_by_species[sp].add(clean(r.get("date")))
            if flag in FLAGS:
                valid_flag_counts[sp]+=1
                flags_by_species[sp].add(flag)
            else:
                invalid_flag_counts[sp]+=1
        out[f"{grid}|{seas}"]={
            "raw_rows_by_species":dict(sorted(raw_counts.items())),
            "valid_canonical_trap_rows_by_species":dict(sorted(valid_flag_counts.items())),
            "invalid_trap_rows_by_species":dict(sorted(invalid_flag_counts.items())),
            "focal_species_with_raw_rows":sorted(sp for sp in FOCAL if raw_counts[sp]>0),
            "focal_species_with_valid_trap_rows":sorted(sp for sp in FOCAL if valid_flag_counts[sp]>0),
            "distinct_valid_flags_by_species":{sp:sorted(v) for sp,v in sorted(flags_by_species.items())},
            "dates_by_species":{sp:sorted(v) for sp,v in sorted(dates_by_species.items())},
            "date_parse_fail_by_species":dict(sorted(date_parse_fail.items())),
        }
    result={"schema":"neon.stage3_grid_season_roster_audit.v1","targets":out}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__":
    main()
