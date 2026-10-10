#!/usr/bin/env python3
"""One-pass prospective PROVISIONAL NEON ecology audit.

Only joins two immutable CI *derived artifacts*, never reads RELEASE-2026 W/B.
The frozen pre-new-outcome gate checks run BEFORE any NN2~MNKA slope is opened.
Original five-genus mode test remains inestimable if a frozen genus is sparse.
This is held-out in time/event IDs, not distinct individual tags and not a
finalized NEON release. No territorial/competition mechanism is inferred.
"""
from __future__ import annotations
import argparse
import json
import random
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import numpy as np
from analysis.multiscale_density_fixed_effects_v1 import (
    fit_slope, _design,
)
from analysis.audit_multiscale_density_centroid_geometry_v1 import spatial_nulls
from analysis.audit_peromyscus_site_uncertainty_v1 import site_sandwich

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/future_neon_provisional_holdout_v1.json"
SEED=20261008
N_NULL=199
SITE_BOOT=2000
GENERA=("Chaetodipus","Myodes","Peromyscus","Dipodomys","Sigmodon")


def join_sealed_rows(metrics:list[dict], predictors:list[dict], qc:dict) -> list[dict]:
    if qc.get("status")!="FUTURE_METRIC_QC_PASS":
        raise RuntimeError("future metric-only QC failed")
    if len(metrics)!=287 or len(predictors)!=287:
        raise RuntimeError("frozen 287-session source count drift")
    def key(x):return (x["taxon"],x["site"],x["plot_id"],x["event_id"])
    metr={key(r):r for r in metrics}
    pred={key(r):r for r in predictors}
    if len(metr)!=287 or len(pred)!=287 or set(metr)!=set(pred):
        raise RuntimeError("metric and continuous-MNKA event-taxon join identity conflict")
    joined=[]
    for k in sorted(metr):
        m=metr[k];n=pred[k]
        if m["genus"]!=n["genus"]:
            raise RuntimeError("genus mismatch across sealed independent sources")
        if int(m["m"])>int(n["frozen_repeat_supported_m"]):
            raise RuntimeError("scored matched cohort exceeds frozen structural support")
        d=date.fromisoformat(str(n["date"])[:10])
        points=[tuple(float(v) for v in p) for p in m["centroids_m"]]
        if len(points)!=int(m["m"]) or len(points)<5:
            raise RuntimeError("invalid frozen metric centroid cohort")
        if abs(float(m["D_m2"])-(float(m["B_debiased_m2"])-float(m["W_m2"])))>1e-8:
            raise RuntimeError("future W/B decomposition identity failed")
        joined.append({
            "taxon":m["taxon"],"site":m["site"],
            "plot_id":m["plot_id"],"event_id":m["event_id"],
            "genus":m["genus"],"series_id":"|".join(
                (m["taxon"],m["site"],m["plot_id"])),
            "site_month":f'{m["site"]}|{d.month:02d}',
            "year":str(d.year),
            "mnka":int(n["genus_mnka"]),
            "m":int(m["m"]),
            "W_m2":float(m["W_m2"]),
            "B_debiased_m2":float(m["B_debiased_m2"]),
            "B_observed_m2":float(m["B_observed_m2"]),
            "D_m2":float(m["D_m2"]),
            "centroids":points,
        })
    return joined


def temporal_series_subset(rows:list[dict],genera=GENERA) -> list[dict]:
    by_series=defaultdict(list)
    for r in rows:
        if r["genus"] in genera:
            by_series[r["series_id"]].append(r)
    qualified={
        key for key,rr in by_series.items()
        if len(rr)>=3 and len({int(x["mnka"]) for x in rr})>=2
    }
    return [r for r in rows if r["series_id"] in qualified and
            r["genus"] in genera]


def fit_mode_genus(rows:list[dict],genus:str) -> dict:
    part=[x for x in rows if x["genus"]==genus]
    support={
        "sessions":len(part),"sites":len({x["site"] for x in part}),
        "series":len({x["series_id"] for x in part}),
    }
    if support["sessions"]<10 or support["sites"]<3:
        return {**support,"status":"FROZEN_GENUS_NOT_ESTIMABLE"}
    fitted={}
    for response in ("D_m2","W_m2","B_debiased_m2"):
        try:
            x=fit_slope(part,response=response,
                nuisance=("series_id","site_month","year"),
                genus_balanced=False)
            fitted[response]={"beta_MNKA":x.beta,
                              "adjustment":"series+site_month+year"}
        except ValueError:
            # Existing fixed-model fallback, labeled and NOT rescue.
            try:
                x=fit_slope(part,response=response,
                    nuisance=("series_id",),genus_balanced=False)
                fitted[response]={"beta_MNKA":x.beta,
                    "adjustment":"series_only_original_fallback"}
            except ValueError:
                return {**support,"status":"NO_RESIDUAL_ABUNDANCE_VARIATION"}
    if abs(fitted["B_debiased_m2"]["beta_MNKA"]
          -fitted["W_m2"]["beta_MNKA"]
          -fitted["D_m2"]["beta_MNKA"])>1e-8:
        raise RuntimeError("future genus Delta slope identity mismatch")
    return {**support,"status":"PROVISIONAL_HELDOUT_DIRECTIONAL",
            "estimates":fitted}


def actual_two_null_coverage(analysis:list[dict],all_future:list[dict]) -> dict:
    """Check centroid reference availability *before* opening future NN2 effects."""
    per=[r for r in analysis if r["genus"]=="Peromyscus"]
    if not per:
        return {"eligible":0,"status":"STOP_PEROMYSCUS_NOT_ESTIMABLE"}
    pool=defaultdict(list)
    for r in all_future:
        if r["genus"]=="Peromyscus":
            pool[r["series_id"]].append(r)
    covered=0
    for row in per:
        other=sum(len(x["centroids"]) for x in pool[row["series_id"]]
                  if x["event_id"]!=row["event_id"])
        covered += other >= len(row["centroids"])
    n=len(per)
    support={
        "eligible":n,
        "sites":len({r["site"] for r in per}),
        "varying_series":len({r["series_id"] for r in per}),
        "available_other_event_centroid_reference":covered,
        "actual_two_null_available_fraction":covered/n,
        "required_fraction":.90,
    }
    pre=(
        n>=80 and support["sites"]>=10
        and support["varying_series"]>=20
        and support["varying_series"]>=15
        and support["actual_two_null_available_fraction"]>=.9
    )
    return {**support,
        "status":"METRIC_ACTUAL_TWO_NULL_GO" if pre
        else "STOP_FROZEN_FUTURE_PEROMYSCUS_GEOMETRY_SUPPORT",
        "no_NN2_effect_opened_by_this_function":True,
    }


def _site_bootstrap_slopes(rows:list[dict], responses:tuple[str,...],
                           B:int=SITE_BOOT, seed:int=SEED):
    """Literal site-cluster resampling and re-estimation of the frozen FE model."""
    rng=random.Random(seed)
    sites=sorted({r["site"] for r in rows})
    if len(sites)<10:raise RuntimeError("insufficient site-cluster support")
    source=defaultdict(list)
    for row in rows:source[row["site"]].append(row)
    values={k:[] for k in responses}
    invalid=0
    for _ in range(B):
        sampled=[rng.choice(sites) for _ in sites]
        boot=[]
        for i,site in enumerate(sampled):
            label=f"resample{i:03d}"
            for row in source[site]:
                r=dict(row)
                r["site"]=label
                r["series_id"]=label+"|"+row["series_id"]
                r["site_month"]=label+"|"+row["site_month"].split("|")[-1]
                boot.append(r)
        Z=_design(boot,("series_id","site_month","year"))
        v=np.column_stack([
            np.asarray([float(r["mnka"]) for r in boot]),
            *[np.asarray([float(r[k]) for r in boot]) for k in responses],
        ])
        coef,*_=np.linalg.lstsq(Z,v,rcond=None)
        residual=v-Z@coef
        xx=residual[:,0]
        den=float(xx@xx)
        if den<=1e-10:
            invalid+=1
            continue
        for j,k in enumerate(responses):
            values[k].append(float(xx@residual[:,j+1]/den))
    if invalid>B*.05:
        raise RuntimeError("more than five percent invalid frozen site bootstrap draws")
    out={}
    for name,v in values.items():
        a=sorted(v)
        if not a:raise RuntimeError("empty site-bootstrap slopes")
        out[name]={
            "replicates":len(a),
            "beta_percentile95":[a[int((len(a)-1)*.025)],
                                 a[int((len(a)-1)*.975)]],
            "positive_lower_bound":a[int((len(a)-1)*.025)]>0,
        }
    return {"invalid_draws":invalid,"seed":seed,"requested_B":B,
            "by_response":out}


def _local_geometry(all_future:list[dict], analysis:list[dict], support:dict,
                    *, boot_B:int=SITE_BOOT):
    if support["status"]!="METRIC_ACTUAL_TWO_NULL_GO":
        return {"status":"STOP_FROZEN_FUTURE_PEROMYSCUS_GEOMETRY_SUPPORT",
                "support":support,"spatial_NN_effects_opened":False}
    per=sorted([r for r in analysis if r["genus"]=="Peromyscus"],
        key=lambda x:(x["taxon"],x["site"],x["plot_id"],x["event_id"]))
    series_pool=defaultdict(list)
    for r in all_future:
        if r["genus"]=="Peromyscus":
            series_pool[r["series_id"]].append(r)
    rng=random.Random(SEED)
    values=[]
    for row in per:
        other=[p for rr in series_pool[row["series_id"]]
               if rr["event_id"]!=row["event_id"]
               for p in rr["centroids"]]
        geom=spatial_nulls(row["centroids"],other,
                           rng=rng,replicates=N_NULL)
        values.append({
            **{k:v for k,v in row.items() if k!="centroids"},
            "nn_squared_m2":geom["nn_squared_m2"],
            "nn_excess_xy_m2":geom["nn_excess_xy_m2"],
            "nn_excess_series_m2":geom["nn_excess_series_m2"],
        })
    # The frozen eligibility gate permits up to 10% missing null-B reference.
    # Use one deterministic complete-case cohort for BOTH primary responses,
    # not a post-result selected or response-dependent cohort.
    dual=[r for r in values if r["nn_excess_series_m2"] is not None]
    if len(dual)/len(values)<.90:
        raise RuntimeError("dual-null eligible fraction fell below frozen 90%")
    if len(dual)<80 or len({r["site"] for r in dual})<10 or len({
            r["series_id"] for r in dual})<20:
        raise RuntimeError("dual-null cohort fails frozen temporal/geographic gate")
    original_response_count=len(values)
    values=dual

    primary_names=("nn_excess_xy_m2","nn_excess_series_m2")
    primary={}
    for response in primary_names:
        f=fit_slope(values,response=response,
            nuisance=("series_id","site_month","year"),genus_balanced=False)
        primary[response]=f.beta
    boot=_site_bootstrap_slopes(values,primary_names,B=boot_B,seed=SEED)
    signs=all(primary[k]>0 for k in primary_names)
    interval_pass=all(boot["by_response"][k]["positive_lower_bound"]
                      for k in primary_names)
    extras={}
    for response in ("nn_squared_m2","B_observed_m2"):
        f=fit_slope(values,response=response,
             nuisance=("series_id","site_month","year"),genus_balanced=False)
        extras[response]=f.beta
    # m controls adopted AFTER discovery but BEFORE new future outcome.
    m_sensitivity={
        response:site_sandwich(values,response,("m",))
        for response in primary_names
    }
    robust_after_m=all(
        m_sensitivity[k]["ci95_normal_approx"][0]>0
        for k in primary_names)
    status=(
        "PROVISIONAL_FUTURE_GEOMETRY_PRIMARY_PASS"
        if signs and interval_pass else
        "PROVISIONAL_FUTURE_GEOMETRY_PRIMARY_FAIL"
    )
    if status.endswith("PASS") and not robust_after_m:
        status="PROVISIONAL_UNADJUSTED_PASS_BUT_M_SENSITIVE"
    return {
        "status":status,"support":support,
        "primary_beta":primary,
        "site_cluster_bootstrap95":boot,
        "secondary_raw_NN_and_B_beta":extras,
        "post_discovery_pre_future_m_adjustment":m_sensitivity,
        "m_sensitive_robustness_lower95_both_positive":robust_after_m,
        "number_of_future_eligible_sessions":original_response_count,
        "number_of_complete_case_two_null_sessions":len(values),
        "independent_release_finalization_required":True,
        "causal_interaction_or_territoriality_demonstrated":False,
    }


def run(metric_file:Path,pair_file:Path,qc_file:Path,
        *,boot_B:int=SITE_BOOT)->dict:
    metrics=json.loads(metric_file.read_text(encoding="utf-8"))
    paired=json.loads(pair_file.read_text(encoding="utf-8"))
    qc=json.loads(qc_file.read_text(encoding="utf-8"))
    rows=join_sealed_rows(metrics,paired,qc)
    filtered=temporal_series_subset(rows)
    group={g:fit_mode_genus(filtered,g) for g in GENERA}
    full_estimable=all(group[g]["status"]=="PROVISIONAL_HELDOUT_DIRECTIONAL"
                       for g in GENERA)
    per=actual_two_null_coverage(filtered,rows)
    # Original fixed five-genus test is separate, and can never be rescued
    # by the Peromyscus-only follow-up if a frozen genus is missing.
    future_geometry=_local_geometry(rows,filtered,per,boot_B=boot_B)
    return {
        "schema":"neon.future_provisional_mammal_ecology_holdout.v1",
        "status":"PROVISIONAL_EVENT_HELDOUT_OBSERVATIONAL",
        "source_metric_only_run":38046250920,
        "source_MNKA_history_run":"FIRST_COMPLETE_PREDICTOR_MANIFEST_WORKFLOW",
        "new_disjoint_source_metric_sessions":len(rows),
        "new_temporally_varying_analysis_sessions":len(filtered),
        "genera":group,
        "original_five_genus_future_mode":{
            "support_status":"STRUCTURALLY_ESTIMABLE" if full_estimable
                else "NOT_ESTIMABLE_ALL_FIVE_FROZEN_GENERA",
            "original_6_of_8_development_guard":"FAILED_UNCHANGED",
            "new_five_genus_mode_confirmed":False,
        },
        "peromyscus_future_geometry":future_geometry,
        "future_response_provisional_not_fixed_official_release":True,
        "old_RELEASE2026_spatial_response_reused":False,
        "distinct_new_events_but_overlap_of_tagged_individual_histories":True,
        "causal_territorial_mechanism_claimed":False,
        "interpretation":"New out-of-release event-level validation is not finalized while provisional, and cross-release tags may persist; no cherry-picking genus or null rules.",
    }


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--metric",type=Path,required=True)
    a.add_argument("--mnka",type=Path,required=True)
    a.add_argument("--metric-qc",type=Path,required=True)
    a.add_argument("--output",type=Path,default=OUT)
    opt=a.parse_args()
    try:
        result=run(opt.metric,opt.mnka,opt.metric_qc)
    except (RuntimeError,ValueError) as exc:
        result={
            "schema":"neon.future_provisional_mammal_ecology_holdout.v1",
            "status":"STOP_FROZEN_FUTURE_HOLDOUT_GATE",
            "error":str(exc),"new_effect_not_promoted":True,
        }
    opt.output.parent.mkdir(parents=True,exist_ok=True)
    opt.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    if result["status"]=="STOP_FROZEN_FUTURE_HOLDOUT_GATE":
        raise SystemExit(3)
