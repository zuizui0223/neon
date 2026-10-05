from __future__ import annotations
import csv, hashlib, json, urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

URL="https://ndownloader.figshare.com/files/33058799"
SHA256="ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"

def clean(x): return str(x or "").strip()

def parse_date(x):
    s=clean(x)
    for fmt in ("%m/%d/%Y","%m/%d/%y","%Y-%m-%d","%m-%d-%Y","%m-%d-%y"):
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
    raw=urllib.request.urlopen(urllib.request.Request(URL,headers={"User-Agent":"neon-stage3-denominator-audit/1.0"}),timeout=180).read()
    if hashlib.sha256(raw).hexdigest()!=SHA256: raise RuntimeError("checksum mismatch")
    rows=list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    targets={("3","winter"),("7","winter")}
    out={}
    for grid,seas in targets:
        rr=[]
        for i,r in enumerate(rows):
            if clean(r.get("grid"))!=grid: continue
            dt=parse_date(r.get("date"))
            if dt is None or season(dt.month)!=seas: continue
            rr.append((i,r,dt))
        counts=Counter(clean(r.get("species")).upper() for _,r,_ in rr)
        by_species={}
        for sp in sorted(counts):
            sr=[(i,r,dt) for i,r,dt in rr if clean(r.get("species")).upper()==sp]
            by_species[sp]={
                "rows":len(sr),
                "unique_ids":len({clean(r.get("unique_ID")) for _,r,_ in sr if clean(r.get("unique_ID"))}),
                "flags":sorted({clean(r.get("flag")).upper() for _,r,_ in sr if clean(r.get("flag"))}),
                "dates":sorted({dt.date().isoformat() for _,_,dt in sr}),
                "times":sorted({clean(r.get("time")) for _,r,_ in sr if clean(r.get("time"))}),
                "blank_uid_rows":sum(not clean(r.get("unique_ID")) for _,r,_ in sr),
                "blank_flag_rows":sum(not clean(r.get("flag")) for _,r,_ in sr),
            }
        out[f"{grid}|{seas}"]={"total_rows":len(rr),"species_counts":dict(counts),"species":by_species}
    Path("results").mkdir(exist_ok=True)
    Path("results/san_jacinto_stage3_two_unit_denominator_audit_v1.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
