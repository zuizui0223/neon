"""Conservative cache bounds from Lu & Zhang 2004, Tables 3 and 4."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"data/neon_lu2004_published_seasonal_release_counts_20261124.json"
RESULT=ROOT/"results/neon_lu2004_seasonal_cache_removal_ceiling_20261124.json"

def diff(a,b):
    if a["released"]!=b["released"]:raise ValueError("UNEQUAL_DENOMINATORS")
    return {"lower_numerator":a["hoarded"]-b["removed"],"upper_numerator":a["removed"]-b["hoarded"],"denominator":a["released"]}

def calculate(src):
    rows=src["rows"]
    if len(rows)!=6 or {(r[0],r[1]) for r in rows}!={(h,s) for h in ("low","high") for s in ("spring","summer","autumn")}:
        raise ValueError("ORIGINAL_SIX_RELEASE_CELLS_REQUIRED")
    if [r[5] for r in rows]!=src["table3_hoarded_sample_counts"]:raise ValueError("CACHE_COUNT_CROSSCHECK")
    sums={};hab={};bad=[]
    for h,s,n,r,surface,c,e,m in rows:
        if any(type(v) is not int or v<0 for v in (n,r,surface,c,e,m)) or not 0<=c<=r<=n==600:
            raise ValueError("INVALID_PUBLISHED_COUNTS")
        gap=r-surface-c-e-m
        if gap:bad.append({"habitat":h,"season":s,"removed_minus_listed_fate_sum":gap})
        a=sums.setdefault(s,{"released":0,"removed":0,"hoarded":0})
        a["released"]+=n;a["removed"]+=r;a["hoarded"]+=c
        hab.setdefault(h,{})[s]={"released":n,"removed":r,"hoarded":c}
    def comparisons(x):
        return {a+"_minus_"+b:diff(x[a],x[b]) for a,b in (("spring","summer"),("autumn","summer"),("autumn","spring"))}
    return {"schema":"neon.lu2004.seasonal_cache_removal_ceiling.v1","source_doi":src["source"]["doi"],
            "table_partition_mismatches":bad,"season_counts":sums,"comparisons":comparisons(sums),
            "habitat_comparisons":{h:comparisons(v) for h,v in hab.items()},
            "conditional_on_reported_removed_and_hoarded_counts":True,"not_complete_fate_partition":True,
            "not_total_predation_or_recruitment":True,"bounds_not_sampling_intervals":True}

def main():
    out=calculate(json.loads(SOURCE.read_text()))
    if out!=json.loads(RESULT.read_text()):raise ValueError("FROZEN_RECEIPT_MISMATCH")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0
if __name__=="__main__":raise SystemExit(main())
