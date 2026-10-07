from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


def clean(x):
    return "" if x is None else str(x).strip()


def parse_date(x):
    x=clean(x)
    for fmt in ("%m/%d/%Y","%Y-%m-%d","%m/%d/%y"):
        try:
            return datetime.strptime(x,fmt).date().isoformat()
        except ValueError:
            pass
    return None


def parse_nocturnal_time(x):
    x=clean(x)
    try:
        h,m=x.split(":")
        h=int(h); m=int(m)
    except Exception:
        return None
    if not (0 <= m < 60):
        return None
    if 7 <= h <= 11:
        h += 12
    elif h == 12:
        h = 24
    elif 0 <= h <= 6:
        h += 24
    else:
        return None
    return h + m/60.0


def quantile(xs,p):
    if not xs:
        return None
    xs=sorted(xs)
    if len(xs)==1:
        return xs[0]
    h=(len(xs)-1)*p
    lo=math.floor(h); hi=math.ceil(h)
    if lo==hi:
        return xs[lo]
    g=h-lo
    return xs[lo]*(1-g)+xs[hi]*g


def cluster_times(times, gap_threshold):
    if not times:
        return []
    xs=sorted(set(times))
    clusters=[[xs[0]]]
    for x in xs[1:]:
        if x-clusters[-1][-1] > gap_threshold:
            clusters.append([x])
        else:
            clusters[-1].append(x)
    return clusters


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    with args.input.open(newline="",encoding="utf-8-sig") as f:
        rows=list(csv.DictReader(f))
    if not rows:
        raise RuntimeError("empty source")
    cols=list(rows[0].keys())

    required={"species","grid","date","time","flag","unique_ID"}
    missing=sorted(required-set(cols))

    species=Counter(clean(r.get("species")) for r in rows if clean(r.get("species")))
    grids=Counter(clean(r.get("grid")) for r in rows if clean(r.get("grid")))
    times=Counter(clean(r.get("time")) for r in rows if clean(r.get("time")))

    valid=[]
    by_night=defaultdict(list)
    for r in rows:
        d=parse_date(r.get("date"))
        t=parse_nocturnal_time(r.get("time"))
        g=clean(r.get("grid"))
        if d and t is not None and g:
            valid.append(t)
            by_night[(g,d)].append(t)

    thresholds=[0.25,0.5,0.75,1.0,1.25,1.5,2.0]
    cluster_audit={}
    for th in thresholds:
        counts=Counter()
        centers=defaultdict(list)
        for ts in by_night.values():
            cc=cluster_times(ts,th)
            counts[len(cc)] += 1
            if len(cc)==3:
                for j,c in enumerate(cc):
                    centers[j].append(statistics.median(c))
        cluster_audit[str(th)]={
            "night_cluster_count_distribution":dict(sorted(counts.items())),
            "three_cluster_nights":counts.get(3,0),
            "three_cluster_center_medians":[
                statistics.median(centers[j]) if centers[j] else None
                for j in range(3)
            ],
        }

    max_gaps=[]
    second_gaps=[]
    unique_time_counts=[]
    for ts in by_night.values():
        xs=sorted(set(ts))
        unique_time_counts.append(len(xs))
        gaps=sorted((b-a for a,b in zip(xs,xs[1:])),reverse=True)
        if gaps:
            max_gaps.append(gaps[0])
        if len(gaps)>1:
            second_gaps.append(gaps[1])

    candidate_covariate_terms=[
        "sex","gender","weight","mass","age","reproductive","pregnant",
        "lactating","scrotal","condition","ear","hind","tail","body"
    ]
    candidate_cols=[
        c for c in cols
        if any(term in c.lower() for term in candidate_covariate_terms)
    ]

    out={
        "schema":"neon.san_jacinto_within_night_sequence_audit.v1",
        "source_sha256_expected":"ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301",
        "rows":len(rows),
        "columns":cols,
        "missing_required_columns":missing,
        "species_counts":dict(species.most_common()),
        "grid_counts":dict(grids.most_common()),
        "candidate_behavioral_covariate_columns":candidate_cols,
        "valid_nocturnal_time_rows":len(valid),
        "night_units_grid_date":len(by_night),
        "nocturnal_time_quantiles":{
            "q05":quantile(valid,.05),"q25":quantile(valid,.25),"q50":quantile(valid,.5),
            "q75":quantile(valid,.75),"q95":quantile(valid,.95),
        },
        "unique_capture_time_count_per_night":{
            "median":quantile(unique_time_counts,.5),
            "q90":quantile(unique_time_counts,.9),
            "max":max(unique_time_counts) if unique_time_counts else None,
        },
        "within_night_gap_hours":{
            "largest_gap_median":quantile(max_gaps,.5),
            "largest_gap_q25":quantile(max_gaps,.25),
            "largest_gap_q75":quantile(max_gaps,.75),
            "second_largest_gap_median":quantile(second_gaps,.5),
            "second_largest_gap_q25":quantile(second_gaps,.25),
            "second_largest_gap_q75":quantile(second_gaps,.75),
        },
        "time_cluster_sensitivity":cluster_audit,
        "top_recorded_time_strings":times.most_common(30),
        "claim_boundary":{
            "check_identity_reconstructed":False,
            "empty_trap_states_available_from_capture_rows_alone":False,
            "interpretation":"This audit only assesses whether the raw capture timestamps support reconstructing repeated within-night check windows. Transition effects are not estimated here."
        }
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
