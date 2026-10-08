from __future__ import annotations

# AI assistance disclosure: This file was drafted or refactored with OpenAI ChatGPT (GPT-5.6 Sol, September 2026); it remains under author responsibility and is verified by repository tests/workflows.

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


def wilson_interval(success: int, total: int, z: float=Z95) -> tuple[float,float]:
    if total<=0 or success<0 or success>total:
        raise ValueError("invalid binomial counts")
    p=success/total
    z2=z*z
    denom=1+z2/total
    center=(p+z2/(2*total))/denom
    half=z*math.sqrt((p*(1-p)+z2/(4*total))/total)/denom
    low=0.0 if success==0 else max(0.0,center-half)
    high=1.0 if success==total else min(1.0,center+half)
    return low,high


def quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    if not 0<=q<=1:
        raise ValueError("q must lie in [0,1]")
    xs=sorted(float(x) for x in values)
    if len(xs)==1:
        return xs[0]
    pos=(len(xs)-1)*q
    lo=math.floor(pos); hi=math.ceil(pos)
    if lo==hi:
        return xs[lo]
    w=pos-lo
    return xs[lo]*(1-w)+xs[hi]*w


def first_last_spans(
    records: Iterable[dict],
    *,
    individual_col: str,
    night_col: str,
    time_col: str,
    coordinate_cols: list[str],
) -> tuple[list[dict],dict]:
    grouped=defaultdict(list)
    excluded=0
    total_rows=0

    for index,raw in enumerate(records):
        total_rows+=1
        row=dict(raw)
        individual=str(row.get(individual_col,"")).strip()
        night=str(row.get(night_col,"")).strip()
        if not individual or not night:
            excluded+=1
            continue
        try:
            time=float(row[time_col])
            coord=tuple(float(row[col]) for col in coordinate_cols)
        except (KeyError,TypeError,ValueError):
            excluded+=1
            continue
        if not math.isfinite(time) or not all(math.isfinite(x) for x in coord):
            excluded+=1
            continue
        grouped[(individual,night)].append((time,index,coord))

    spans=[]
    single=0
    for (individual,night),items in sorted(grouped.items()):
        if len(items)<2:
            single+=1
            continue
        ordered=sorted(items,key=lambda x:(x[0],x[1]))
        first=ordered[0]
        last=ordered[-1]
        span=euclidean(first[2],last[2])
        spans.append({
            "individual":individual,
            "night":night,
            "observation_count":len(items),
            "first_time":first[0],
            "last_time":last[0],
            "elapsed_time":last[0]-first[0],
            "span":span,
        })

    return spans,{
        "input_rows":total_rows,
        "excluded_invalid_rows":excluded,
        "individual_nights":len(grouped),
        "single_observation_individual_nights":single,
        "repeat_observation_individual_nights":len(spans),
    }


def summarize_spans(
    spans: list[dict],
    *,
    material_scale: float,
) -> dict:
    scale=float(material_scale)
    if not math.isfinite(scale) or scale<=0:
        raise ValueError("material_scale must be finite and positive")
    if not spans:
        return {
            "repeat_observation_individual_nights":0,
            "material_scale":scale,
            "material_shift_count":0,
            "material_shift_fraction":None,
            "wilson95_low":None,
            "wilson95_high":None,
        }

    distances=[float(x["span"]) for x in spans]
    shifted=sum(d>=scale-1e-12 for d in distances)
    low,high=wilson_interval(shifted,len(distances))
    ratios=[d/scale for d in distances]
    elapsed=[float(x["elapsed_time"]) for x in spans]
    return {
        "repeat_observation_individual_nights":len(spans),
        "material_scale":scale,
        "material_shift_count":shifted,
        "material_shift_fraction":shifted/len(distances),
        "wilson95_low":low,
        "wilson95_high":high,
        "median_span":float(statistics.median(distances)),
        "q75_span":quantile(distances,0.75),
        "q90_span":quantile(distances,0.90),
        "max_span":max(distances),
        "median_span_in_material_scales":float(statistics.median(ratios)),
        "q90_span_in_material_scales":quantile(ratios,0.90),
        "median_elapsed_time":float(statistics.median(elapsed)),
    }


def observed_transition_energy_scale(
    spans: Iterable[float],
    total_occasions: int,
) -> float:
    """Conservative per-axis second-moment scale of exposed transitions.

    Singly observed occasions contribute to the denominator but have no
    directly observed first-to-last displacement, so their observed
    contribution is zero. This is an observation-process lower-bound summary,
    not an assertion that their latent displacement was zero.
    """
    xs=[float(x) for x in spans]
    n=int(total_occasions)
    if n<=0 or len(xs)>n:
        raise ValueError("total_occasions must be positive and >= number of exposed spans")
    if any((not math.isfinite(x) or x<0) for x in xs):
        raise ValueError("spans must be finite and nonnegative")
    return math.sqrt(sum(x*x for x in xs)/(2.0*n))


def state_mixing_sensitivity(
    spans: Iterable[float],
    total_occasions: int,
    sigma_ref: float | None = None,
) -> dict:
    """Second-moment benchmark linking observed transitions to SCR sigma.

    Under a zero-mean approximately isotropic within-occasion state transition,
    a single stationary half-normal spatial scale has the dense-detector
    benchmark sigma_eff/sigma ~= sqrt(1 + A_sigma^2), where
    A_sigma = observed_transition_energy_scale / sigma_ref.

    This is a scale diagnostic, not a correction and not a claim that the
    reference sigma is the true empirical sigma.
    """
    xs=[float(x) for x in spans]
    scale=observed_transition_energy_scale(xs,total_occasions)
    out={
        "all_occasion_count":int(total_occasions),
        "exposed_repeat_occasion_count":len(xs),
        "observed_per_axis_transition_scale":scale,
        "sigma_ref":None,
        "state_mixing_ratio_A_sigma":None,
        "second_moment_predicted_sigma_ratio":None,
        "second_moment_predicted_relative_change":None,
        "ten_percent_materiality_A_sigma":math.sqrt(1.10**2-1.0),
    }
    if sigma_ref is not None:
        sigma=float(sigma_ref)
        if not math.isfinite(sigma) or sigma<=0:
            raise ValueError("sigma_ref must be finite and positive")
        A=scale/sigma
        ratio=math.sqrt(1.0+A*A)
        out.update({
            "sigma_ref":sigma,
            "state_mixing_ratio_A_sigma":A,
            "second_moment_predicted_sigma_ratio":ratio,
            "second_moment_predicted_relative_change":ratio-1.0,
        })
    return out


def movement_sensitivity_bound(span_t: float, span_u: float) -> float:
    a=float(span_t); b=float(span_u)
    if not math.isfinite(a) or not math.isfinite(b) or a<0 or b<0:
        raise ValueError("spans must be finite and nonnegative")
    return a+b


def mpd_sensitivity_bound(spans: Iterable[float]) -> float:
    xs=[float(x) for x in spans]
    if not xs or any((not math.isfinite(x) or x<0) for x in xs):
        raise ValueError("spans must be a non-empty finite nonnegative collection")
    return 2.0*statistics.mean(xs)


def standardized_mpd_sensitivity_bound(
    spans: Iterable[float],
    null_sd: float,
) -> float:
    sd=float(null_sd)
    if not math.isfinite(sd) or sd<=0:
        raise ValueError("null_sd must be finite and positive")
    return mpd_sensitivity_bound(spans)/sd


def main() -> int:
    parser=argparse.ArgumentParser(
        description="Diagnose temporal positional aliasing in repeated-location data."
    )
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--individual-col",required=True)
    parser.add_argument("--night-col",required=True)
    parser.add_argument("--time-col",required=True)
    parser.add_argument("--coordinate-col",action="append",dest="coordinate_cols",required=True)
    parser.add_argument("--material-scale",type=float,required=True)
    parser.add_argument("--sigma-ref",type=float,default=None)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()

    with args.input.open(newline="",encoding="utf-8-sig") as fh:
        records=list(csv.DictReader(fh))

    spans,qc=first_last_spans(
        records,
        individual_col=args.individual_col,
        night_col=args.night_col,
        time_col=args.time_col,
        coordinate_cols=args.coordinate_cols,
    )
    out={
        "schema":"temporal_aliasing_diagnostic.v1",
        "qc":qc,
        "span_summary":summarize_spans(
            spans,
            material_scale=args.material_scale,
        ),
        "state_mixing_sensitivity":state_mixing_sensitivity(
            [float(x["span"]) for x in spans],
            qc["individual_nights"],
            args.sigma_ref,
        ),
        "bounds":{
            "movement":"|d(F_t,F_u)-d(L_t,L_u)| <= span_t + span_u",
            "mpd":"|MPD(F)-MPD(L)| <= 2*mean(span_i)",
            "standardized_mpd":"|z_F-z_L| <= 2*mean(span_i)/null_sd",
        },
        "interpretation_boundary":(
            "Observed first-last spans are protocol-conditioned positional uncertainty; "
            "they are not unrestricted movement paths or home-range estimates. "
            "The state-mixing calculation is a second-moment sensitivity benchmark "
            "under an approximately zero-mean isotropic transition, not an empirical "
            "bias correction or an estimate of latent movement on singly observed occasions."
        ),
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
