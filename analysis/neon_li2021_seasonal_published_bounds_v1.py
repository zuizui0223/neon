"""Reproduce descriptive partial-identification arithmetic on Li et al. 2021
published two-decimal percentages. Do not reconstruct unreported seed counts.
Integer units are 0.01 percentage points, not probabilities or sample sizes.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"data/neon_li2021_seasonal_published_fates_20261124.json"
RESULT=ROOT/"results/neon_li2021_seasonal_published_fate_bounds_20261124.json"
CATEGORIES={"IS","PS","PR","IR","HR","MR"}

def season_bounds(f):
    if set(f)!=CATEGORIES or any(type(v) is not int or v<0 for v in f.values()) or sum(f.values())!=10000:
        raise ValueError("PRINTED_FATE_PARTITION_NOT_100_PERCENT")
    pred=f["PS"]+f["PR"];cache=f["HR"];intact=f["IR"]+cache;u=f["MR"]
    return {"predation":[pred,pred+u],"cache":[cache,cache+u],
            "intact_moved":[intact,intact+u],
            "predation_minus_cache":[pred-cache-u,pred-cache+u]}

def diff(x,y):
    return [x[0]-y[1],x[1]-y[0]]

def calculate(src):
    if set(src["fates"])!={"spring","autumn"}:
        raise ValueError("EXPECTED_TWO_PUBLISHED_SEASONS")
    v={k:season_bounds(src["fates"][k]) for k in ("spring","autumn")}
    s,a=v["spring"],v["autumn"]
    d={"spring_minus_autumn_predation":diff(s["predation"],a["predation"]),
       "autumn_minus_spring_cache":diff(a["cache"],s["cache"]),
       "autumn_minus_spring_intact_moved":diff(a["intact_moved"],s["intact_moved"]),
       "spring_minus_autumn_predation_minus_cache":diff(s["predation_minus_cache"],a["predation_minus_cache"])}
    # Each difference endpoint uses <=6 printed numbers; if each was
    # rounded to nearest 0.01 percentage point, total error <=0.03 pp.
    pad=3
    return {"schema":"neon.li2021.seasonal_published_fate_bounds.v1","source_doi":src["source"]["doi"],
            "units":src["units"],"analysis_unit":"one published study, two pooled season samples; no seed-level inference",
            "season_bounds":v,"contrasts":d,
            "no_raw_seed_counts_reconstructed":True,"bounds_not_sampling_intervals":True,
            "seasonal_causal_effect_not_identified":True,
            "recorded_point_differences":{"spring_minus_autumn_predation":s["predation"][0]-a["predation"][0],
                 "autumn_minus_spring_cache":a["cache"][0]-s["cache"][0],
                 "autumn_minus_spring_intact_moved":a["intact_moved"][0]-s["intact_moved"][0]},
            "rounding_conservative_padding_each_difference_endpoint":pad,
            "predation_difference_positive_even_with_rounding":d["spring_minus_autumn_predation"][0]-pad>0,
            "cache_difference_sign_identified":d["autumn_minus_spring_cache"][0]>0 or d["autumn_minus_spring_cache"][1]<0}

def main():
    got=calculate(json.loads(SOURCE.read_text()))
    if got!=json.loads(RESULT.read_text()):
        raise ValueError("FROZEN_PUBLISHED_AGGREGATE_RECEIPT_DRIFT")
    print(json.dumps(got,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":raise SystemExit(main())
