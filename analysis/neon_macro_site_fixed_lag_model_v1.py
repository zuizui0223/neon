"""Site-balanced WLS with exact site fixed effects for exploratory lag effects.

All outcomes are already-inspected historical NEON exact-two-genera Z scores.
This module is pure calculation: no private NEON source, no URL, no
ecological effect opened until a separately verified source date gate.
"""
from __future__ import annotations
from collections import defaultdict
from math import isfinite
from random import Random
from statistics import mean
import numpy as np


def _source_rows(records:list[dict]) -> tuple[dict[str,list[tuple[float,float,int]]],tuple[int,...]]:
    if not isinstance(records,list) or not records:
        raise ValueError("Site-record input missing")
    bysite=defaultdict(list)
    cats=set()
    for r in records:
        site=r.get("site")
        try:
            z=float(r["z"])
            lag=float(r["gap_days"])
            category=r["transition"]
        except (KeyError,TypeError,ValueError):
            raise ValueError("Missing finite gap/Z and transition source data") from None
        if not isinstance(site,str) or not site or not isfinite(z) or not isfinite(lag) or lag<=0 or lag>=400:
            raise ValueError("Invalid source physical site or actual capture-day gap")
        if isinstance(category,bool) or not isinstance(category,int) or category not in (0,1,2,3):
            raise ValueError("Bad meteorological transition source class")
        bysite[site].append((lag/30.0,z,category))
        cats.add(category)
    return dict(bysite),tuple(sorted(cats))


def _fit(grouped:dict[str,list[tuple[float,float,int]]],categories:tuple[int,...],
         sampled_sites:list[str]) -> float|None:
    """Source-site-balanced Frisch-Waugh-Lovell fixed-site dummy projection.

    Sampled sites may repeat under whole-site bootstrap, and each duplicated
    draw is a SEPARATE site cluster. Empty or no within-site variance is
    a rank-deficient bootstrap replicate, not a fabricated numeric slope.
    """
    k=len(categories)
    if k<3:
        return None
    cols=k # lag + (k-1) season-category contrasts
    features=[]
    target=[]
    for site in sampled_sites:
        group=grouped[site]
        n=len(group)
        if n<2:
            continue
        X=np.zeros((n,cols),dtype=float)
        yy=np.zeros(n,dtype=float)
        for i,(lag,z,cat) in enumerate(group):
            X[i,0]=lag
            yy[i]=z
            for j,t in enumerate(categories[1:],start=1):
                X[i,j]=float(cat==t)
        # Every physical-site total weight exactly 1 (not every pair
        # weight 1): full within-site FE elimination, then WLS.
        X=(X-X.mean(axis=0))*np.sqrt(1/n)
        yy=(yy-yy.mean())*np.sqrt(1/n)
        features.append(X)
        target.append(yy)
    if not features:
        return None
    X=np.concatenate(features,axis=0)
    y=np.concatenate(target)
    if np.linalg.matrix_rank(X)!=cols:
        return None
    ans=np.linalg.lstsq(X,y,rcond=None)[0]
    beta=float(ans[0])
    if not isfinite(beta):
        return None
    return beta


def site_fixed_lag_model(
    records:list[dict],*,seed:int=2026102516,n_bootstrap:int=2000,
    min_fraction_valid:float=.95,
)->dict:
    if not isinstance(seed,int) or isinstance(seed,bool) or not isinstance(n_bootstrap,int) or n_bootstrap<100:
        raise ValueError("Invalid preregistered site-bootstrap configuration")
    grouped,cats=_source_rows(records)
    sites=sorted(grouped)
    observed=_fit(grouped,cats,sites)
    if observed is None:
        return {"status":"STOP_SITE_TRANSITION_FIXED_EFFECTS_RANK_DEFICIENT",
                "outcome_slope_estimated":False,
                "source_sites":len(sites),"transition_classes":list(cats)}
    rng=Random(seed)
    boots=[]
    bad=0
    for b in range(n_bootstrap):
        sample=[sites[rng.randrange(len(sites))] for _ in sites]
        fit=_fit(grouped,cats,sample)
        if fit is None:bad+=1
        else:boots.append(fit)
    fraction=len(boots)/n_bootstrap
    if fraction<min_fraction_valid:
        return {"status":"STOP_SITE_BOOTSTRAP_SINGULAR_TOO_OFTEN",
                "outcome_slope_estimated":False,
                "source_sites":len(sites),"transition_classes":list(cats),
                "bootstrap_requested":n_bootstrap,"bootstrap_valid":len(boots),
                "bootstrap_valid_fraction":fraction}
    boots.sort()
    def q(z):
        i=z*(len(boots)-1)
        lo=int(i)
        hi=min(len(boots)-1,lo+1)
        return boots[lo]+(boots[hi]-boots[lo])*(i-lo)
    lose=[]
    for dropped in sites:
        fit=_fit(grouped,cats,[s for s in sites if s!=dropped])
        if fit is not None:lose.append(fit)
    if len(lose)!=len(sites):
        return {"status":"STOP_LEAVE_ONE_SITE_OUT_MODEL_RANK_FAILURE",
                "outcome_slope_estimated":False,
                "source_sites":len(sites),"LOSO_valid_sites":len(lose)}
    paired=[]
    for site,vals in grouped.items():
        if len(vals)>=2:
            gaps=[row[0] for row in vals]
            zz=[row[1] for row in vals]
            paired.extend((g-mean(gaps),z-mean(zz)) for g,z in zip(gaps,zz))
    x=np.array([z[0] for z in paired])
    y=np.array([z[1] for z in paired])
    correlation=float(np.corrcoef(x,y)[0,1]) if x.size>3 and np.std(x)>0 and np.std(y)>0 else None
    return {
        "schema":"neon.macro.exact_two_genus_site_fixed_temporal_lag.v1",
        "status":"EXPLORATORY_SITE_AND_TRANSITION_ADJUSTED_LAG_ESTIMATED",
        "number_original_informative_units":len(records),
        "physical_sites":len(sites),
        "transition_types_with_original_data":list(cats),
        "slope_standardized_recurrence_Z_per_30_capture_gap_days":observed,
        "whole_physical_site_bootstrap_seed":seed,
        "whole_site_bootstrap_draws_requested":n_bootstrap,
        "whole_site_bootstrap_draws_valid":len(boots),
        "bootstrap_two_sided_percentile_95_interval":[q(.025),q(.975)],
        "leave_one_entire_physical_site_out_slope_min":min(lose),
        "leave_one_entire_physical_site_out_slope_max":max(lose),
        "LOSO_fraction_with_same_slope_sign_as_full":sum(observed*e>0 for e in lose)/len(lose),
        "within_site_unadjusted_gap_vs_Z_correlation_descriptive":correlation,
        "no_environmental_or_detection_causal_effect_claimed":True,
        "no_raw_source_site_animal_capture_date_or_station_values_exported":True,
        "historical_observed_ecological_Zs_not_independent_new_release_data":True,
        "no_pooled_Z_from_3plus_strict_original_or_density_W_B":True,
        "site_bootstrap_not_a_proven_full_temporal_dependency_null":True,
    }
