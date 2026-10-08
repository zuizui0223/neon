from __future__ import annotations

import argparse
import csv
import itertools
import json
import random
import statistics
from collections import Counter, defaultdict

BINS=("early","middle","late")
SPECIES=("CHFA","DKR","LAPM","PEMA","PEER","SKR")
REPS=999

def season(date):
    month=int(date.strip().split("/")[0])
    return ("winter" if month in (11,12,1) else
            "spring" if month in (2,3,4) else
            "summer" if month in (5,6,7) else "fall")

def individual_id(r):
    x=r.get("unique_ID","").strip().upper().replace(" ","")
    bad=("", "MISSING", "NONE", "NA", "N/A", "UNKNOWN", "MISSINGMISSING")
    return x if x not in bad and not x.startswith("MISSING") else ""

def vector_index(vs):
    ss=list(vs.keys())
    if len(ss)<2:
        return None
    q=[]
    for s in ss:
        xs=vs[s]
        total=sum(xs)
        if not total:
            continue
        q.append([x/total for x in xs])
    if len(q)<2:
        return None
    overlap=[]
    for a,b in itertools.combinations(q,2):
        overlap.append(1-0.5*sum(abs(x-y) for x,y in zip(a,b)))
    return sum(overlap)/len(overlap)

def quantile(a,p):
    xs=sorted(a)
    h=(len(xs)-1)*p
    j=int(h)
    return xs[j]+(h-j)*(xs[min(j+1,len(xs)-1)]-xs[j])

def permute_ra3(vectors,rng):
    vs={}
    for sp,counts in vectors.items():
        a=list(counts)
        rng.shuffle(a)
        vs[sp]=a
    return vector_index(vs)

def calculate(rows,label,seed):
    counts=defaultdict(lambda: defaultdict(lambda:[0,0,0]))
    spatial=defaultdict(lambda: defaultdict(set))
    for r in rows:
        s=r["species"].strip().upper()
        b=r["time_bin"].strip().lower()
        g=r["grid"].strip()
        f=r["flag"].strip().upper()
        d=r["date"].strip()
        if s not in SPECIES or b not in BINS or g not in [str(i) for i in range(1,9)]:
            continue
        k=(g,season(d))
        counts[k][s][BINS.index(b)]+=1
        if f and len(f)==2 and f[0] in "ABCDEFG" and f[1] in "1234567":
            spatial[k][s].add(f)
    rng=random.Random(seed)
    per=[]
    for k in sorted(counts):
        group=counts[k]
        obs=vector_index(group)
        if obs is None:
            continue
        null=[permute_ra3(group,rng) for _ in range(REPS)]
        null=[x for x in null if x is not None]
        mu=statistics.mean(null)
        sd=statistics.stdev(null)
        ses=(obs-mu)/sd if sd>0 else None
        all_sp=[s for s in group if sum(group[s])>0]
        cscore=[]
        for a,b in itertools.combinations(all_sp,2):
            if a not in spatial[k] or b not in spatial[k]:
                continue
            A,B=spatial[k][a],spatial[k][b]
            cscore.append((len(A)-len(A&B))*(len(B)-len(A&B)))
        per.append({
            "grid":k[0],"season":k[1],"species_count":len(all_sp),
            "species":sorted(all_sp),
            "recorded_capture_count":sum(sum(v) for v in group.values()),
            "temporal_overlap":obs,
            "ra3_null_mean":mu,
            "ra3_null_sd":sd,
            "temporal_ses":ses,
            "temporal_aggregation":obs>quantile(null,.975),
            "temporal_segregation":obs<quantile(null,.025),
            "spatial_cscore_unstandardized":statistics.mean(cscore) if cscore else None,
        })
    return per

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    with open(args.input,encoding="utf-8-sig",newline="") as h:
        raw=list(csv.DictReader(h))
    qualifying=sorted(raw,key=lambda r:("early","middle","late").index(r["time_bin"].strip().lower()) if r["time_bin"].strip().lower() in BINS else 3)
    first=[]
    seen=set()
    n_identifiable=0
    n_unknown=0
    for i,r in enumerate(qualifying):
        s=r["species"].strip().upper()
        if s not in SPECIES:
            continue
        uid=individual_id(r)
        if uid:
            n_identifiable+=1
            key=(r["grid"].strip(),r["date"].strip(),s,uid)
            if key in seen:
                continue
            seen.add(key)
        else:
            n_unknown+=1
        first.append(r)
    allcap=calculate(raw,"all",20261008)
    dedup=calculate(first,"first_per_marked_individual_night",20261009)
    k=lambda z:(z["grid"],z["season"])
    a={k(x):x for x in allcap}
    b={k(x):x for x in dedup}
    common=sorted(set(a)&set(b))
    paired=[]
    for key in common:
        x,y=a[key],b[key]
        paired.append({
            "grid":key[0],"season":key[1],
            "capture_count_all":x["recorded_capture_count"],
            "capture_count_first":y["recorded_capture_count"],
            "overlap_all":x["temporal_overlap"],
            "overlap_first":y["temporal_overlap"],
            "delta_overlap_first_minus_all":y["temporal_overlap"]-x["temporal_overlap"],
            "temporal_RA3_aggregation_all":x["temporal_aggregation"],
            "temporal_RA3_aggregation_first":y["temporal_aggregation"],
            "temporal_RA3_segregation_all":x["temporal_segregation"],
            "temporal_RA3_segregation_first":y["temporal_segregation"],
            "Cscore_all_unstandardized":x["spatial_cscore_unstandardized"],
            "Cscore_first_unstandardized":y["spatial_cscore_unstandardized"],
        })
    def summary(z):
        return {
            "grid_seasons":len(z),
            "aggregation":sum(x["temporal_aggregation"] for x in z),
            "segregation":sum(x["temporal_segregation"] for x in z),
            "mean_temporal_overlap":statistics.mean(x["temporal_overlap"] for x in z),
        }
    deltas=[x["delta_overlap_first_minus_all"] for x in paired]
    out={
        "schema":"neon.san_jacinto_recapture_niche_sensitivity.v1",
        "status":"exploratory_reanalysis_after_original_publication",
        "source_capture_rows":len(raw),
        "rows_after_first_individual_night_filter":len(first),
        "identifiable_source_rows":n_identifiable,
        "unidentified_source_rows_kept_as_singletons":n_unknown,
        "all_captures":summary(allcap),
        "first_per_marked_individual_night":summary(dedup),
        "paired_grid_seasons":paired,
        "paired_mean_delta_overlap":statistics.mean(deltas),
        "paired_median_delta_overlap":statistics.median(deltas),
        "grid_seasons_delta_positive":sum(x>0 for x in deltas),
        "grid_seasons_delta_negative":sum(x<0 for x in deltas),
        "comparison_with_published_reference":{
            "published_temporal_aggregation_grid_seasons":7,
            "published_temporal_segregation_grid_seasons":0,
            "replicates_published_aggregation_count":summary(allcap)["aggregation"]==7,
            "replicates_published_segregation_count":summary(allcap)["segregation"]==0,
        },
        "method":{
            "index":"mean pairwise Czekanowski overlap of 3 check-bin capture-proportion vectors",
            "null":"RA3 row-wise random permutation of the 3 bin proportions within each species, 999 randomizations per grid-season",
            "spatial_cscore":"Unstandardized descriptive C-score only; not a reproduction of the paper's SIM9 fixed-fixed spatial significance test",
            "filter":"Keep earliest time_bin per named marked animal x species x grid x date. Rows without usable unique_ID retained as separate capture records.",
        },
        "claim_boundary":{
            "causal_measurement_effect_identified":False,
            "original_spatial_partitioning_significance_reproduced":False,
            "temporal_RA3_exact_original_implementation_guaranteed":False,
            "warning":"Changes upon thinning recaptures can reflect detection weighting and information loss; they do not by themselves imply trapping caused changes in natural animal behavior.",
        }
    }
    with open(args.output,"w",encoding="utf-8") as h:
        json.dump(out,h,indent=2,sort_keys=True)
        h.write("\n")
    print(json.dumps({
        "all_captures":out["all_captures"],
        "first_per_marked_individual_night":out["first_per_marked_individual_night"],
        "paired_mean_delta_overlap":out["paired_mean_delta_overlap"],
        "paired_median_delta_overlap":out["paired_median_delta_overlap"],
        "grid_seasons_delta_positive":out["grid_seasons_delta_positive"],
        "grid_seasons_delta_negative":out["grid_seasons_delta_negative"],
        "comparison_with_published_reference":out["comparison_with_published_reference"],
    },indent=2,sort_keys=True))

if __name__=="__main__":
    main()
