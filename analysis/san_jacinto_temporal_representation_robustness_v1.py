from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import random
import statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path

SPECIES=("CHFA","PEMA","DKR","PEER","LAPM","SKR")
SPECIES_SET=set(SPECIES)
BINS=("EARLY","MIDDLE","LATE")
BIN_INDEX={b:i for i,b in enumerate(BINS)}

def clean(x):
    return "" if x is None else str(x).strip().upper()

def parse_date(x):
    for fmt in ("%m/%d/%y","%m/%d/%Y","%Y-%m-%d"):
        try:
            return datetime.strptime(str(x).strip(),fmt).date()
        except ValueError:
            pass
    raise ValueError(x)

def season(date):
    m=parse_date(date).month
    if m in (8,9,10): return "FALL"
    if m in (11,12,1): return "WINTER"
    if m in (2,3,4): return "SPRING"
    return "SUMMER"

def valid_id(r):
    uid=clean(r.get("unique_ID"))
    if uid and uid!="NONE" and "MISSING" not in uid:
        return f"{clean(r.get('species'))}|{uid}"
    l=clean(r.get("left_tag")); rr=clean(r.get("right_tag"))
    if (l or rr) and "MISSING" not in l and "MISSING" not in rr:
        return f"{clean(r.get('species'))}|TAG:{l}/{rr}"
    v=clean(r.get("VIE"))
    if v and "MISSING" not in v:
        return f"{clean(r.get('species'))}|VIE:{v}"
    return ""

def nocturnal_time(x):
    try:
        h,m=map(int,str(x).strip().split(":"))
    except Exception:
        return 99.0
    if 7<=h<=11: h+=12
    elif h==12: h=24
    elif 0<=h<=6: h+=24
    return h+m/60

def row_score(r):
    return (BIN_INDEX[clean(r.get("time_bin"))],nocturnal_time(r.get("time")),int(r["_row"]))

def community_overlap(matrix):
    spp=[s for s in SPECIES if s in matrix and sum(matrix[s])>0]
    vals=[]
    for i,a in enumerate(spp):
        sa=sum(matrix[a])
        for b in spp[i+1:]:
            sb=sum(matrix[b])
            pa=[x/sa for x in matrix[a]]
            pb=[x/sb for x in matrix[b]]
            vals.append(1.0-0.5*sum(abs(pa[j]-pb[j]) for j in range(3)))
    return sum(vals)/len(vals) if vals else None

def unique_perms(v):
    return sorted(set(itertools.permutations(tuple(v),3)))

def percentile(xs,p):
    z=sorted(xs)
    h=(len(z)-1)*p
    lo=int(math.floor(h)); hi=int(math.ceil(h)); g=h-lo
    return z[lo]*(1-g)+z[hi]*g

def ra3_exact(matrix):
    spp=[s for s in SPECIES if s in matrix and sum(matrix[s])>0]
    choices=[unique_perms(matrix[s]) for s in spp]
    obs=community_overlap(matrix)
    vals=[]
    cur={}
    def rec(i):
        if i==len(spp):
            vals.append(community_overlap(cur)); return
        s=spp[i]
        for p in choices[i]:
            cur[s]=p
            rec(i+1)
    rec(0)
    q025=percentile(vals,.025); q975=percentile(vals,.975)
    mu=sum(vals)/len(vals)
    sd=statistics.stdev(vals) if len(vals)>1 else 0.0
    return {
        "observed":obs,"null_mean":mu,"null_sd":sd,
        "q025":q025,"q975":q975,
        "ses":(obs-mu)/sd if sd else None,
        "classification":"SEGREGATED" if obs<q025 else ("AGGREGATED" if obs>q975 else "NULL"),
        "n_null":len(vals),
    }

def ra3_mc(matrix,rng,nreps=999):
    spp=[s for s in SPECIES if s in matrix and sum(matrix[s])>0]
    obs=community_overlap(matrix)
    vals=[]
    for _ in range(nreps):
        cur={}
        for s in spp:
            v=list(matrix[s])
            rng.shuffle(v)
            cur[s]=v
        vals.append(community_overlap(cur))
    q025=percentile(vals,.025); q975=percentile(vals,.975)
    return "SEGREGATED" if obs<q025 else ("AGGREGATED" if obs>q975 else "NULL")

def matrices(rows,weights=None):
    out=defaultdict(lambda:{s:[0.0,0.0,0.0] for s in SPECIES})
    for i,r in enumerate(rows):
        sp=clean(r.get("species")); b=clean(r.get("time_bin"))
        if sp not in SPECIES_SET or b not in BIN_INDEX: continue
        k=f"{clean(r.get('grid'))}|{season(r.get('date'))}"
        w=1.0 if weights is None else weights[i]
        out[k][sp][BIN_INDEX[b]]+=w
    return out

def choose_lane(raw,mode,rng=None):
    groups=defaultdict(list); unresolved=[]
    for r in raw:
        ident=valid_id(r)
        if ident:
            groups[(clean(r.get("grid")),str(r.get("date")).strip(),ident)].append(r)
        else:
            unresolved.append(r)
    selected=list(unresolved)
    if mode=="FIRST":
        for arr in groups.values():
            selected.append(min(arr,key=row_score))
    elif mode=="LAST":
        for arr in groups.values():
            selected.append(max(arr,key=row_score))
    elif mode=="RANDOM":
        assert rng is not None
        for arr in groups.values():
            selected.append(rng.choice(arr))
    else:
        raise ValueError(mode)
    return selected

def normalized_matrices(raw):
    out=defaultdict(lambda:{s:[0.0,0.0,0.0] for s in SPECIES})
    groups=defaultdict(list); unresolved=[]
    for r in raw:
        ident=valid_id(r)
        if ident:
            groups[(clean(r.get("grid")),str(r.get("date")).strip(),ident)].append(r)
        else:
            unresolved.append(r)
    for r in unresolved:
        sp=clean(r.get("species")); b=clean(r.get("time_bin"))
        if sp in SPECIES_SET and b in BIN_INDEX:
            k=f"{clean(r.get('grid'))}|{season(r.get('date'))}"
            out[k][sp][BIN_INDEX[b]]+=1.0
    for arr in groups.values():
        sp=clean(arr[0].get("species"))
        bins=sorted({clean(r.get("time_bin")) for r in arr if clean(r.get("time_bin")) in BIN_INDEX})
        if not bins: continue
        w=1.0/len(bins)
        k=f"{clean(arr[0].get('grid'))}|{season(arr[0].get('date'))}"
        for b in bins:
            out[k][sp][BIN_INDEX[b]]+=w
    return out

def lane_summary(mats):
    units={k:ra3_exact(v) for k,v in sorted(mats.items())}
    counts={"AGGREGATED":0,"SEGREGATED":0,"NULL":0}
    for v in units.values(): counts[v["classification"]]+=1
    return {"classification_counts":counts,"units":units}

def qsummary(xs):
    z=sorted(xs)
    return {
        "min":z[0],"q025":percentile(z,.025),"q25":percentile(z,.25),
        "median":percentile(z,.5),"q75":percentile(z,.75),
        "q975":percentile(z,.975),"max":z[-1],"mean":sum(z)/len(z)
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--random-representations",type=int,default=100)
    ap.add_argument("--random-null-reps",type=int,default=999)
    ap.add_argument("--seed",type=int,default=20261007)
    args=ap.parse_args()

    with args.input.open(newline="",encoding="utf-8-sig") as f:
        raw=list(csv.DictReader(f))
    focal=[]
    for i,r in enumerate(raw):
        r["_row"]=i
        if clean(r.get("species")) in SPECIES_SET and clean(r.get("time_bin")) in BIN_INDEX:
            focal.append(r)

    all_m=matrices(focal)
    first_rows=choose_lane(focal,"FIRST")
    last_rows=choose_lane(focal,"LAST")
    norm_m=normalized_matrices(focal)

    deterministic={
        "ALL":lane_summary(all_m),
        "FIRST":lane_summary(matrices(first_rows)),
        "LAST":lane_summary(matrices(last_rows)),
        "INDIVIDUAL_NIGHT_NORMALIZED":lane_summary(norm_m),
    }

    rng=random.Random(args.seed)
    random_counts=[]
    per_unit=defaultdict(lambda:{"AGGREGATED":0,"SEGREGATED":0,"NULL":0})
    for rep in range(args.random_representations):
        sel=choose_lane(focal,"RANDOM",rng)
        mats=matrices(sel)
        c={"AGGREGATED":0,"SEGREGATED":0,"NULL":0}
        for k,m in mats.items():
            cls=ra3_mc(m,rng,args.random_null_reps)
            c[cls]+=1
            per_unit[k][cls]+=1
        random_counts.append(c)

    random_summary={
        "representations":args.random_representations,
        "null_reps_per_unit":args.random_null_reps,
        "aggregated_count":qsummary([x["AGGREGATED"] for x in random_counts]),
        "segregated_count":qsummary([x["SEGREGATED"] for x in random_counts]),
        "null_count":qsummary([x["NULL"] for x in random_counts]),
        "per_unit_fraction":{
            k:{s:v/args.random_representations for s,v in d.items()}
            for k,d in sorted(per_unit.items())
        }
    }

    # Species-level phase shifts for deterministic single-state lanes.
    def profile(rows):
        m={s:[0,0,0] for s in SPECIES}
        for r in rows:
            m[clean(r["species"])][BIN_INDEX[clean(r["time_bin"])]]+=1
        return {
            s:{
                "counts":m[s],
                "proportions":[x/sum(m[s]) for x in m[s]]
            } for s in SPECIES
        }

    out={
        "schema":"neon.san_jacinto_temporal_representation_robustness.v1",
        "status":"post_result_representation_robustness",
        "source_sha256_expected":"ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301",
        "support":{
            "all_capture_rows":len(focal),
            "first_rows":len(first_rows),
            "last_rows":len(last_rows),
            "grid_seasons":len(all_m)
        },
        "deterministic_lanes":deterministic,
        "random_one_capture_per_individual_night":random_summary,
        "species_profiles":{
            "ALL":profile(focal),
            "FIRST":profile(first_rows),
            "LAST":profile(last_rows)
        },
        "claim_boundary":{
            "undisturbed_activity_reconstructed":False,
            "capture_effect_identified":False,
            "interpretation":"FIRST and LAST impose opposite event-order censoring; RANDOM and individual-night normalization remove within-night multiplicity without privileging the same temporal edge. Agreement across these lanes supports robustness of relative community overlap, not unbiased absolute activity timing."
        }
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "support":out["support"],
        "deterministic_counts":{k:v["classification_counts"] for k,v in deterministic.items()},
        "random_count_summary":random_summary,
        "species_profiles":out["species_profiles"],
    },indent=2,sort_keys=True))

if __name__=="__main__":
    main()
