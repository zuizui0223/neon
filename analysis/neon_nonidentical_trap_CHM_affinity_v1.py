#!/usr/bin/env python3
"""One exploratory NEON genus canopy-affinity recurrence test at OTHER traps.

Source-verified AOP CHM (structural canopy, NOT food) and original NEON
genus×trap occupancy after source-detected shared PIT tags excluded.
Season-B fixed genus row totals AND trap column margins preserved by the
same accepted 2x2 switch-chain used in the established NEON null.

NEVER exports original genus/station/site/taxonomic or canopy height values.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from math import isfinite,sqrt
from random import Random
from statistics import mean,stdev

from analysis.neon_crossseason_template_null_v1 import (
    TRAPS,TRAP_INDEX,_bits,_single_swap,_lag1,signflip_site_mean_test
)

MIN_PAIRS=15
MIN_SITES=8
SEED=2026112207
DRAWS=1500
BURNIN=1000
SWAPS=30
MIN_ESS=150

def require(condition,label):
    if not condition:raise ValueError("NEON_NOVEL_TRAP_CHM_STOP_"+label)

def rank100(height):
    """Deterministic midranks (0,1): tie aware and 100 canonical traps."""
    require(set(height)==set(TRAPS) and len(height)==100,
            "NOT_ORIGINAL_100_CHM_STATIONS")
    vals=[height[t] for t in TRAPS]
    require(all(type(z) in (int,float) and isfinite(z) for z in vals),
            "NONFINITE_ORIGINAL_CHM_PIXEL")
    sorted_pairs=sorted((z,i) for i,z in enumerate(vals))
    mid=[None]*100
    j=0
    while j<100:
        k=j+1
        while k<100 and sorted_pairs[k][0]==sorted_pairs[j][0]:
            k+=1
        rank_avg=(j+1+k)/2.0
        scale=(rank_avg-0.5)/100.0
        for pos in range(j,k):mid[sorted_pairs[pos][1]]=scale
        j=k
    return dict(zip(TRAPS,mid))

def exclusive_score(A,B,ranks_a,ranks_b):
    """A preference × B preference at NEW genus-specific stations only."""
    require(isinstance(A,dict) and isinstance(B,dict) and set(A)==set(B)
            and len(A)>=3, "GENERA_SET_OR_COUNT_DRIFT")
    require(set(ranks_a)==set(TRAPS) and set(ranks_b)==set(TRAPS),
            "MISSING_ORIGINAL_CANOPY_RANKS")
    genera=sorted(A)
    signals=[]
    n_novel=0
    for g in genera:
        aa=A[g]; bb=B[g]
        require(isinstance(aa,set) and isinstance(bb,set)
                and len(aa)>=2 and len(bb)>=2
                and aa<=set(TRAPS) and bb<=set(TRAPS),
                "ORIGINAL_GENUS_TRAP_ROSTER_INCOMPLETE")
        pa=mean(ranks_a[t] for t in aa)-0.5
        novel=bb-aa
        if novel:
            n_novel+=1
            pb=mean(ranks_b[t] for t in novel)-0.5
        else:
            pb=0.
        signals.append(pa*pb)
    return float(mean(signals)),n_novel

def from_masks(labels,masks):
    out={}
    for g,mask in zip(labels,masks):
        out[g]={t for t,i in TRAP_INDEX.items() if mask&(1<<i)}
    return out

def original_unit_test(A,B,heightA,heightB,*,seed,n_draws=DRAWS,
                       burnin=BURNIN,swaps=SWAPS,min_ess=MIN_ESS):
    ra,rb=rank100(heightA),rank100(heightB)
    result={
        "genus_count":len(A),"source_original_100_CHM_midrank_stations":100,
        "season_B_genus_row_and_station_column_margins_fixed":True,
        "B_exact_original_genus_same_station_hits_excluded_from_score":True,
        "source_CHM_may_follow_animal_capture":True,
        "one_sided_positive_canopy_affinity_direction_fixed":True
    }
    if len(set(heightA.values()))==1 or len(set(heightB.values()))==1:
        return {**result,"status":"UNINFORMATIVE_ONE_CANOPY_HEIGHT"}
    observed,n_novel=exclusive_score(A,B,ra,rb)
    result["original_genera_with_novel_B_stations"]=n_novel
    if n_novel<2:
        return {**result,"status":"UNINFORMATIVE_FEWER_THAN_TWO_NOVEL_B_GENERA"}
    labels=sorted(B)
    origin=[_bits(B[g]) for g in labels]
    current=origin.copy()
    original_row=[m.bit_count() for m in origin]
    def margins(rows):
        trap_cols=[sum((mask>>i)&1 for mask in rows) for i in range(100)]
        return [m.bit_count() for m in rows],trap_cols
    wantrow,wantcol=margins(origin)
    rng=Random(seed)
    proposals=0;accepted=0
    def advance(count):
        nonlocal proposals,accepted
        for _ in range(count):
            ok=False
            for __ in range(10000):
                proposals+=1
                if _single_swap(current,rng):
                    accepted+=1;ok=True;break
            if not ok:return False
        return True
    if not advance(burnin):
        return {**result,"status":"UNINFORMATIVE_SOURCE_FIXED_MARGINS_NO_SWAPS"}
    values=[]
    for _ in range(n_draws):
        if not advance(swaps):
            return {**result,"status":"UNINFORMATIVE_SOURCE_FIXED_MARGIN_CHAIN_STOP"}
        alt=from_masks(labels,current)
        t,_=exclusive_score(A,alt,ra,rb)
        values.append(t)
    require(margins(current)==(wantrow,wantcol) and
            original_row==wantrow, "NULL_DID_NOT_PRESERVE_ORIGINAL_FIXED_MARGINS")
    sd=stdev(values)
    avg=mean(values)
    rho=_lag1(values)
    rho_plus=max(0.,min(0.9999,rho))
    ess=n_draws*(1-rho_plus)/(1+rho_plus)
    result.update({
        "null_draws":n_draws,"accepted_fixed_margin_swaps":accepted,
        "source_null_accepted_swap_proposal_fraction":accepted/proposals,
        "observed_nonidentical_trap_canopy_affinity_score":observed,
        "null_score_mean":avg,"null_score_sd":sd,"null_score_lag1":rho,
        "approx_null_effective_draws":ess
    })
    if sd<=1e-12:
        result.update({"status":"UNINFORMATIVE_ZERO_NULL_VARIANCE","z":None})
    elif ess<min_ess:
        result.update({"status":"UNINFORMATIVE_NULL_ESS_TOO_LOW","z":None})
    else:
        result.update({"status":"INFORMATIVE_NONIDENTICAL_TRAP_CANOPY_NULL",
                       "z":(observed-avg)/sd})
    return result

def summarize_original_sites(original_units,site_vectors,*,source_pairs,
                             source_sites,source_plots):
    """Private site identifiers used only transiently; no private keys output."""
    require((source_pairs,source_sites,source_plots)==(36,12,21),
            "ORIGINAL_CHM_36_12_21_SOURCE_COHORT_DRIFT")
    require(len(original_units)==source_pairs,
            "SOURCE_SELECTED_PAIRS_CHANGING_ORIGINAL_DENOMINATOR")
    counts=Counter(z["status"] for z in original_units)
    site_data={k:mean(v) for k,v in site_vectors.items() if v}
    n=sum(len(v) for v in site_vectors.values())
    enough=n>=MIN_PAIRS and len(site_data)>=MIN_SITES
    base={
        "schema":"neon.crossseason_genus_canopy_affinity_excluding_identical_traps.v1",
        "source_selected_original_season_pairs":source_pairs,
        "source_selected_original_physical_sites":source_sites,
        "source_selected_original_mammal_grids":source_plots,
        "null_status_counts":dict(sorted(counts.items())),
        "original_source_informative_comparisons":n,
        "original_source_informative_physical_sites":len(site_data),
        "source_inference_min_pairs":MIN_PAIRS,
        "source_inference_min_independent_sites":MIN_SITES,
        "no_original_site_genus_station_or_canopy_pixel_values_exported":True
    }
    if not enough:
        return {**base,"status":"STOP_CANOPY_AFFINITY_TOO_FEW_INFORMATIVE_SITES_OR_PAIRS",
                "site_level_canopy_ecological_effect":None}
    means=list(site_data.values())
    test=signflip_site_mean_test(means,seed=SEED)
    supported=test["site_mean_Z_mean"]>0 and test["one_sided_site_signflip_p"]<.05
    return {**base,
            "status":("EXPLORATORY_CANOPY_AFFINITY_SUPPORTED_CONDITIONAL"
                      if supported else "EXPLORATORY_CANOPY_AFFINITY_NOT_SUPPORTED"),
            "site_level_canopy_ecological_effect":{
                **test,
                "not_independent_prospective_confirmation":True,
                "not_direct_habitat_choice_or_detection_corrected":True
            }}
