from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Iterable

Z95=1.959963984540054


def euclidean(a: tuple[float,...], b: tuple[float,...]) -> float:
    if len(a)!=len(b) or not a:
        raise ValueError("coordinates must be non-empty and dimension-matched")
    if not all(math.isfinite(x) for x in (*a,*b)):
        raise ValueError("coordinates must be finite")
    return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))


def wilson_interval(success: int,total: int,z: float=Z95) -> tuple[float,float]:
    if total<=0 or success<0 or success>total:
        raise ValueError("invalid binomial counts")
    p=success/total; z2=z*z; den=1+z2/total
    center=(p+z2/(2*total))/den
    half=z*math.sqrt((p*(1-p)+z2/(4*total))/total)/den
    return (0.0 if success==0 else max(0.0,center-half),
            1.0 if success==total else min(1.0,center+half))


def quantile(values: list[float],q: float) -> float | None:
    if not values: return None
    xs=sorted(float(x) for x in values)
    pos=(len(xs)-1)*q; lo=math.floor(pos); hi=math.ceil(pos)
    if lo==hi: return xs[lo]
    w=pos-lo
    return xs[lo]*(1-w)+xs[hi]*w


def positional_diameter(coords: Iterable[tuple[float,...]]) -> float:
    xs=list(coords)
    if len(xs)<2: return 0.0
    return max(euclidean(xs[i],xs[j])
               for i in range(len(xs)) for j in range(i+1,len(xs)))


def occasion_geometry(
    records: Iterable[dict],
    *,
    individual_col: str,
    occasion_col: str,
    time_col: str,
    coordinate_cols: list[str],
) -> tuple[list[dict],dict]:
    grouped=defaultdict(list)
    excluded=0; total_rows=0
    for index,raw in enumerate(records):
        total_rows+=1
        row=dict(raw)
        individual=str(row.get(individual_col,"")).strip()
        occasion=str(row.get(occasion_col,"")).strip()
        if not individual or not occasion:
            excluded+=1; continue
        try:
            time=float(row[time_col])
            coord=tuple(float(row[c]) for c in coordinate_cols)
        except (KeyError,TypeError,ValueError):
            excluded+=1; continue
        if not math.isfinite(time) or not all(math.isfinite(x) for x in coord):
            excluded+=1; continue
        grouped[(individual,occasion)].append((time,index,coord))

    rows=[]; single=0
    for (individual,occasion),items in sorted(grouped.items()):
        ordered=sorted(items,key=lambda x:(x[0],x[1]))
        if len(ordered)<2:
            single+=1; continue
        coords=[x[2] for x in ordered]
        endpoint=euclidean(coords[0],coords[-1])
        diameter=positional_diameter(coords)
        rows.append({
            "individual":individual,
            "occasion":occasion,
            "observation_count":len(ordered),
            "first_time":ordered[0][0],
            "last_time":ordered[-1][0],
            "elapsed_time":ordered[-1][0]-ordered[0][0],
            "endpoint_span":endpoint,
            "positional_diameter":diameter,
            "endpoint_equals_diameter":abs(endpoint-diameter)<=1e-12,
        })
    return rows,{
        "input_rows":total_rows,
        "excluded_invalid_rows":excluded,
        "individual_occasions":len(grouped),
        "single_observation_individual_occasions":single,
        "repeat_observation_individual_occasions":len(rows),
    }


def summarize_metric(values: list[float],scale: float) -> dict:
    if not values:
        return {
            "count":0,"material_count":0,"material_fraction":None,
            "wilson95_low":None,"wilson95_high":None,
        }
    k=sum(v>=scale-1e-12 for v in values)
    lo,hi=wilson_interval(k,len(values))
    ratios=[v/scale for v in values]
    return {
        "count":len(values),
        "material_count":k,
        "material_fraction":k/len(values),
        "wilson95_low":lo,"wilson95_high":hi,
        "median":statistics.median(values),
        "q75":quantile(values,.75),"q90":quantile(values,.90),"max":max(values),
        "median_in_material_scales":statistics.median(ratios),
        "q90_in_material_scales":quantile(ratios,.90),
    }


def summarize_geometry(rows: list[dict],*,material_scale: float,total_occasions: int) -> dict:
    scale=float(material_scale)
    if not math.isfinite(scale) or scale<=0:
        raise ValueError("material_scale must be finite and positive")
    endpoint=[float(x["endpoint_span"]) for x in rows]
    diameter=[float(x["positional_diameter"]) for x in rows]
    endpoint_material=[x>=scale-1e-12 for x in endpoint]
    diameter_material=[x>=scale-1e-12 for x in diameter]
    hidden=sum(d and not e for d,e in zip(diameter_material,endpoint_material))
    diameter_k=sum(diameter_material)
    return {
        "material_scale":scale,
        "endpoint_span":summarize_metric(endpoint,scale),
        "positional_diameter":summarize_metric(diameter,scale),
        "endpoint_false_negative_count":hidden,
        "endpoint_false_negative_fraction_repeat":(
            hidden/len(rows) if rows else None
        ),
        "fraction_of_material_diameter_events_missed_by_endpoint":(
            hidden/diameter_k if diameter_k else None
        ),
        "all_occasion_directly_observed_material_diameter_lower_bound":(
            diameter_k/total_occasions if total_occasions else None
        ),
    }


def representative_distance_bound(diameter_t: float,diameter_u: float) -> float:
    a=float(diameter_t); b=float(diameter_u)
    if not math.isfinite(a) or not math.isfinite(b) or a<0 or b<0:
        raise ValueError("diameters must be finite and nonnegative")
    return a+b


def mpd_representative_bound(diameters: Iterable[float]) -> float:
    xs=[float(x) for x in diameters]
    if not xs or any(not math.isfinite(x) or x<0 for x in xs):
        raise ValueError("diameters must be non-empty finite nonnegative")
    return 2.0*statistics.mean(xs)


def main() -> int:
    ap=argparse.ArgumentParser(description="Diagnose within-occasion positional aliasing using full observed geometry.")
    ap.add_argument("--input",type=Path,required=True)
    ap.add_argument("--individual-col",required=True)
    ap.add_argument("--occasion-col",required=True)
    ap.add_argument("--time-col",required=True)
    ap.add_argument("--coordinate-col",action="append",dest="coordinate_cols",required=True)
    ap.add_argument("--material-scale",type=float,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    with a.input.open(newline="",encoding="utf-8-sig") as fh:
        records=list(csv.DictReader(fh))
    rows,qc=occasion_geometry(
        records,
        individual_col=a.individual_col,
        occasion_col=a.occasion_col,
        time_col=a.time_col,
        coordinate_cols=a.coordinate_cols,
    )
    summary=summarize_geometry(
        rows,
        material_scale=a.material_scale,
        total_occasions=qc["individual_occasions"],
    )
    out={
        "schema":"temporal_aliasing_diagnostic.v2",
        "qc":qc,
        "geometry_summary":summary,
        "bounds":{
            "arbitrary_representative_interoccasion_distance":
              "|d(R_t,R_u)-d(R'_t,R'_u)| <= diameter_t + diameter_u",
            "arbitrary_representative_mpd":
              "|MPD(R)-MPD(R')| <= 2*mean(diameter_i)",
        },
        "interpretation_boundary":(
            "Positional diameter uses all valid observed positions within an occasion. "
            "It bounds sensitivity to any two representative-position rules whose selected "
            "positions are among those observations. Endpoint span is retained as a directional "
            "first-to-last summary but can be zero for A-to-B-to-A histories."
        ),
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
