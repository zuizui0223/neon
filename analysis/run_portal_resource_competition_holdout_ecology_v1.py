#!/usr/bin/env python3
"""Pre-frozen Portal 2020-25 plant-abundance × competitor-access ecology.

Plot-level *captured species composition* change versus *preceding plant-count*
change, with fixed plot, month, and start-year effects. No learning parameter,
no exact-trap niche claim and no reuse of original 1996-2019 response outcomes.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from math import isfinite, log1p
from pathlib import Path
import json

import numpy as np

from analysis.portal_external_id_niche_source_v1 import (
    FILES, TRT, get_source, csv_rows, i, stake,
)
from analysis.audit_portal_resources_competition_learning_source_v1 import (
    NEW_FILES, original_extra, cohort_source_only, strict_survey_census,
    strict_plant_match, YR_START, YR_END,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/neon_portal_resource_competitor_holdout_ecology_v1.json"
PROTOCOL = "docs/NEON_PORTAL_RESOURCE_COMPETITOR_OUTCOME_FROZEN_20261120.md"
SEED = 2026112071
BOOT = 2000
MIN_BOOT = 1800
MIN_ROW_N = 60
MIN_SITE_N = 10
MIN_SITES_PER_TRT = 4
MIN_ANIMALS = 5
PHASE = "REPRODUCE_FROZEN_SOURCE_GO"

def require(value, reason):
    if not value:
        raise ValueError("PORTAL_RC_ECOLOGY_STOP_" + reason)

def tv_distance(a, b):
    """Total variation between two taxon-count distributions."""
    require(bool(a) and bool(b), "NONEMPTY_SOURCE_COUNTS")
    require(all(isinstance(n, int) and n >= 0 for n in list(a.values())+list(b.values())),
            "VALID_NONNEGATIVE_COUNTS")
    sa, sb = sum(a.values()), sum(b.values())
    require(sa > 0 and sb > 0, "NONZERO_SOURCE_TOTALS")
    return 0.5 * sum(abs(a.get(t,0)/sa-b.get(t,0)/sb)
                     for t in set(a)|set(b))

def original_plant_abundance(source, quad_census):
    """Aggregate counts per censused QUADRAT; zero only where censused==1."""
    stream, fields = csv_rows(source["Plants/Portal_plant_quadrats.csv"],
        ("year","season","plot","quadrat","species","abundance","cover","cf","notes"))
    totals = defaultdict(float)
    source_rows = Counter()
    for row in stream:
        y,p,q = i(row["year"]),i(row["plot"]),i(row["quadrat"])
        if y is None or p is None or q is None or not YR_START <= y <= YR_END:
            continue
        key=(y,(row["season"] or "").strip().lower(),p)
        if q not in quad_census.get(key,set()):
            source_rows["plant_original_rows_not_confirmed_censused"] += 1
            continue
        try:
            count=float(row["abundance"])
        except (ValueError,TypeError):
            require(False, "PLANT_ABUNDANCE_NONNUMERIC_IN_CENSUSED_QUADRAT")
        require(isfinite(count) and count >= 0,
                "PLANT_ABUNDANCE_NEGATIVE_OR_INFINITE")
        totals[key] += count
        source_rows["plant_original_numeric_censused_species_rows"] += 1
    per_censused_quadrat = {
        key: total/len(quad_census[key])
        for key,total in totals.items() if len(quad_census[key]) >= 12
    }
    return per_censused_quadrat,dict(sorted(source_rows.items()))

def fixed_capture_events(source, treatments, effort):
    """2020+ exact plot/month/tag species source, never 1996-2019 effects."""
    valid_sess={}
    plot_month=defaultdict(list)
    for row in effort:
        year,month,plot,period,day=(i(row[c]) for c in
                                  ("year","month","plot","period","day"))
        if None in (year,month,plot,period,day):
            continue
        if not YR_START <= year <= YR_END or period <= 0:
            continue
        if row["sampled"]!="1" or row["qcflag"]!="1" or i(row["effort"]) not in (48,49):
            continue
        state=treatments.get((plot,year,month))
        if not state or state["treatment"] not in TRT:
            continue
        key=(plot,year,month,period)
        require(key not in valid_sess,"DUPLICATE_STANDARD_EFFORT_SESSION")
        valid_sess[key]={"day":day,"treatment":state["treatment"]}
        plot_month[(plot,year,month)].append(key)
    pairs=[]
    for plot,year,month in sorted(plot_month):
        if year >= YR_END:
            continue
        A=plot_month[(plot,year,month)]
        B=plot_month.get((plot,year+1,month),[])
        if len(A)!=1 or len(B)!=1:
            continue
        a,b=A[0],B[0]
        if valid_sess[a]["treatment"]!=valid_sess[b]["treatment"]:
            continue
        pairs.append((a,b))
    require(len(valid_sess)==860 and len(pairs)==453,
            "FROZEN_PRE_PLANT_EVENTS_860_453")
    return valid_sess,pairs

def ecology_source_rows(source):
    """Source GO must reproduce before model data are unsealed."""
    global PHASE
    gate=cohort_source_only(source)
    require(gate["status"]=="SOURCE_GO_NO_RESOURCE_OR_MAMMAL_EFFECT_OPENED",
            "FROZEN_69_ID_AND_PLANT_SOURCE_GATE_FAILED")
    source_v=gate["new_2020_2025_outcome_blind_animal_source"]
    require(source_v["eligible_pairs_with_numeric_plant_source_both_years"]==69
            and source_v["source_physical_plot_count_with_numeric_plant"]==17
            and source_v["source_distinct_species_codes_with_numeric_plant"]==3,
            "FROZEN_69_17_3_SOURCE_DRIFT")
    PHASE="PRECOMMITTED_ANIMAL_CAPTURE_COMPOSITION_AND_PLANT_ABUNDANCE"
    quad,numeric,dates,plantmeta=strict_survey_census(source)
    per_quadrat,plant_row_counts=original_plant_abundance(source,quad)
    tax_stream,_=csv_rows(source["Rodents/Portal_rodent_species.csv"],
        ("speciescode","rodent","granivore","censustarget","unidentified"))
    target={row["speciescode"].strip() for row in tax_stream
            if row["rodent"]=="1" and row["granivore"]=="1"
            and row["censustarget"]=="1" and row["unidentified"]=="0"}
    treatments,_=csv_rows(source["SiteandMethods/Portal_plots.csv"],
        ("year","month","plot","treatment","resourcetreatment","anttreatment"))
    by_treatment={}
    for row in treatments:
        key=(i(row["plot"]),i(row["year"]),i(row["month"]))
        require(key not in by_treatment,"DUPLICATE_TREATMENT_META")
        by_treatment[key]=row
    effort,_=csv_rows(source["Rodents/Portal_rodent_trapping.csv"],
        ("year","month","day","plot","period","sampled","qcflag","effort"))
    valid_sess,pairs=fixed_capture_events(source,by_treatment,effort)
    qualified=[]
    for a,b in pairs:
        pa = strict_plant_match(
            (a[0],a[1],a[2],valid_sess[a]["day"]),quad,numeric,dates)
        pb = strict_plant_match(
            (b[0],b[1],b[2],valid_sess[b]["day"]),quad,numeric,dates)
        if pa and pb:
            require(pa["source_plant_key"]!=pb["source_plant_key"],
                    "REUSING_PLANT_CENSUS_IN_TWO_YEARS")
            qualified.append((a,b,pa["source_plant_key"],pb["source_plant_key"]))
    require(len(qualified)==203,"FROZEN_203_PRIOR_90D_PLANT_SOURCE_DRIFT")
    need={event for a,b,_,_ in qualified for event in (a,b)}
    rows,fields=csv_rows(source["Rodents/Portal_rodent.csv"],
        ("year","month","plot","period","stake","species","id"))
    by_event=defaultdict(lambda:defaultdict(set))
    ignored=Counter()
    for row in rows:
        year=i(row["year"])
        if year is None or not YR_START <= year <= YR_END:
            continue
        event=(i(row["plot"]),year,i(row["month"]),i(row["period"]))
        if event not in need:
            continue
        taxon=(row["species"] or "").strip()
        tag=(row["id"] or "").strip()
        if taxon not in target or not tag or tag.lower() in ("na","nan","null") or (
            stake(row["stake"]) is None
        ):
            ignored["source_non_target_or_missing_tag_or_stake"]+=1
            continue
        by_event[event][tag].add(taxon)
    census_counts={}
    for ev in need:
        counts=Counter()
        for tag,code_set in by_event[ev].items():
            if len(code_set)!=1:
                ignored["same_census_id_multiple_species_removed"]+=1
                continue
            counts[next(iter(code_set))]+=1
        census_counts[ev]=counts
    ecology=[]
    exclusion=Counter()
    for a,b,plant_a,plant_b in qualified:
        aa,bb=census_counts[a],census_counts[b]
        if min(sum(aa.values()),sum(bb.values()))<MIN_ANIMALS:
            exclusion["fewer_than_five_individuals_in_either_census"]+=1
            continue
        if plant_a not in per_quadrat or plant_b not in per_quadrat:
            exclusion["no_numeric_matched_original_plant_count"]+=1
            continue
        p_a,p_b=per_quadrat[plant_a],per_quadrat[plant_b]
        ecological_y=tv_distance(aa,bb)
        ecological_x=abs(log1p(p_b)-log1p(p_a))
        require(0<=ecological_y<=1 and isfinite(ecological_x),
                "FINITE_RESPONSE_EXPOSURE")
        ecology.append({
            "plot":a[0],"month":a[2],"start_year":a[1],
            "treatment":valid_sess[a]["treatment"],
            "y":ecological_y,"x":ecological_x,
            "n_animal_A":sum(aa.values()),"n_animal_B":sum(bb.values()),
            "plotblock":str(a[0]),
        })
    return gate,ecology,plant_row_counts,dict(sorted(ignored.items())),dict(sorted(exclusion.items()))

def model_matrix(rows):
    """Plot FE + month FE + start-year FE + x + x:exclosure."""
    plots=sorted({r["plotblock"] for r in rows})
    months=sorted({r["month"] for r in rows})
    years=sorted({r["start_year"] for r in rows})
    col=len(plots)+max(0,len(months)-1)+max(0,len(years)-1)+2
    X=np.zeros((len(rows),col),dtype=float)
    Y=np.zeros(len(rows),dtype=float)
    plot_idx={s:i for i,s in enumerate(plots)}
    mon_idx={s:i for i,s in enumerate(months[1:])}
    year_idx={s:i for i,s in enumerate(years[1:])}
    for k,rec in enumerate(rows):
        X[k,plot_idx[rec["plotblock"]]]=1.
        if rec["month"] in mon_idx:
            X[k,len(plots)+mon_idx[rec["month"]]]=1.
        if rec["start_year"] in year_idx:
            X[k,len(plots)+len(mon_idx)+year_idx[rec["start_year"]]]=1.
        X[k,-2]=rec["x"]
        X[k,-1]=rec["x"]*(rec["treatment"]=="exclosure")
        Y[k]=rec["y"]
    require(len(rows)>=col and np.linalg.matrix_rank(X)==col,
            "MODEL_DESIGN_FULL_RANK_NOT_MET")
    return X,Y

def fit_fixed(rows):
    X,y=model_matrix(rows)
    beta=np.linalg.lstsq(X,y,rcond=None)[0]
    require(np.all(np.isfinite(beta)),"NONFINITE_MODEL_BETA")
    return float(beta[-2]), float(beta[-2]+beta[-1]),float(beta[-1])

def treatment_plot_mean_difference(rows):
    by_plot=defaultdict(list)
    treatments={}
    for r in rows:
        by_plot[r["plotblock"]].append(r["y"])
        old=treatments.setdefault(r["plotblock"],r["treatment"])
        require(old==r["treatment"],"TREATMENT_CHANGED_WITHIN_MODEL_PLOT")
    group=defaultdict(list)
    for k,v in by_plot.items():
        group[treatments[k]].append(float(np.mean(v)))
    require(all(len(group[t])>=MIN_SITES_PER_TRT for t in TRT),
            "TREATMENT_PLOT_COUNT")
    return float(np.mean(group["exclosure"])-np.mean(group["control"]))

def fitting_and_bootstrap(rows):
    sites={r["plot"] for r in rows}
    by_trt={t:{r["plot"] for r in rows if r["treatment"]==t} for t in TRT}
    require(len(rows)>=MIN_ROW_N and len(sites)>=MIN_SITE_N and
            all(len(by_trt[t])>=MIN_SITES_PER_TRT for t in TRT),
            "FROZEN_MODEL_SOURCE_SAMPLE_SIZE")
    primary=fit_fixed(rows)
    descriptive=treatment_plot_mean_difference(rows)
    bysite=defaultdict(list)
    for item in rows:
        bysite[item["plot"]].append(item)
    rng=np.random.default_rng(SEED)
    boots=[]
    failed=0
    for j in range(BOOT):
        sampled=[]
        for t in TRT:
            options=sorted(by_trt[t])
            draw=rng.choice(options,size=len(options),replace=True)
            for idx,site in enumerate(draw):
                for item in bysite[int(site)]:
                    sampled.append({
                        **item,
                        "plotblock":f"bootstrap_{t}_{idx}"
                    })
        try:
            estimate=fit_fixed(sampled)
            difference=treatment_plot_mean_difference(sampled)
        except ValueError:
            failed+=1
            continue
        boots.append((*estimate,difference))
    require(len(boots)>=MIN_BOOT,"CLUSTER_BOOTSTRAP_VALID_DRAWS_LOW")
    a=np.asarray(boots)
    ci=np.quantile(a,[.025,.975],axis=0).T
    trt_count=Counter(r["treatment"] for r in rows)
    return {
        "source_plot_month_year_pairs":len(rows),
        "independent_original_plot_clusters":len(sites),
        "plots_per_original_competitor_access_state":
            {t:len(by_trt[t]) for t in TRT},
        "counts_of_source_pairs_by_original_treatment":dict(sorted(trt_count.items())),
        "distinct_original_start_years":len({r["start_year"] for r in rows}),
        "distinct_original_months":len({r["month"] for r in rows}),
        "plot_level_capture_composition_total_variation":{
            "mean":float(np.mean([r["y"] for r in rows])),
            "min":float(min(r["y"] for r in rows)),
            "max":float(max(r["y"] for r in rows)),
        },
        "source_plot_level_plant_count_change":{
            "measure":"absolute change in log1p(plant individuals per censused 0.25m2 quadrat), not biomass",
            "mean":float(np.mean([r["x"] for r in rows])),
            "min":float(min(r["x"] for r in rows)),
            "max":float(max(r["x"] for r in rows)),
        },
        "plot_FE_month_FE_year_FE_resource_slope_control":{
            "beta":primary[0],"site_stratified_bootstrap95":ci[0].tolist(),
            "predicted_direction":"positive",
        },
        "plot_FE_month_FE_year_FE_resource_slope_exclosure":{
            "beta":primary[1],"site_stratified_bootstrap95":ci[1].tolist(),
        },
        "plot_FE_resource_by_competitor_access_interaction":{
            "beta":primary[2],"site_stratified_bootstrap95":ci[2].tolist(),
            "direction_prior":"unspecified",
        },
        "unadjusted_plot_equal_exclosure_minus_control_capture_turnover":{
            "estimate":descriptive,"site_stratified_bootstrap95":ci[3].tolist(),
            "not_causal_competitor_effect":True,
            "not_estimated_in_plot_fixed_effects_model":True,
        },
        "uncertainty":{
            "site_stratified_bootstrap_valid_draws":len(boots),
            "source_fixed_draws_requested":BOOT,
            "rank_deficient_bootstrap_draws":failed,
            "rng_seed":SEED,
            "no_individual_or_quadrat_pseudoreplication_for_site_CI":True,
            "all_intervals_descriptive_not_independent_confirmatory":True,
        }
    }

def run():
    global PHASE
    source={p:get_source(p) for p in FILES}
    for p in NEW_FILES:
        source[p]=original_extra(p)
    src,ecology,plantcounts,ignore,drop=ecology_source_rows(source)
    PHASE="PREFROZEN_ECOLOGICAL_MODEL_FITTING"
    result=fitting_and_bootstrap(ecology)
    return {
        "schema":"neon.portal_plant_change_x_competitor_ecology_holdout.v1",
        "status":"PORTAL_TEMPORAL_HOLDOUT_EXPLORATORY_CAPTURES_NOT_CAUSAL_NICHE",
        "frozen_protocol":PROTOCOL,
        "source":{
            "immutable_original_portal_commit":src["published_source"]["original_git_commit"],
            "all_eight_original_git_blob_hashes_verified":True,
            "pre_effect_source_run":"https://github.com/zuizui0223/neon/actions/runs/44760271257",
            "pre_effect_source_gate":"SOURCE_GO_NO_RESOURCE_OR_MAMMAL_EFFECT_OPENED",
            "same_203_plot_year_month_pair_universe_not_rescoped":True,
            "same_69_id_disjoint_species_pair_source_GO_not_claimed_as_effect":True,
            "plant_raw_numeric_membership_check":plantcounts,
            "original_rodent_source_exclusions":ignore,
            "model_eligibility_exclusions":drop,
        },
        "ecological_results":result,
        "scientific_limits":{
            "not_actual_biomass_food_seed_energy_or_accessibility":True,
            "not_49_station_microhabitat_selection":True,
            "not_learning_or_reward_memory":True,
            "not_fitness_demographic_death_immigration":True,
            "original_competitor_treatment_confounded_with_historical_plot_state":True,
            "entire_data_source_one_Portal_desert_landscape":True,
            "not_heldout_geographically_or_independent_camera_behavior":True,
            "original_NEON_Finland_Portal1996_2019_Structural_effects_unchanged":True,
            "single_manuscript_still_DRAFT_SUBMISSION_HOLD":True
        },
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
    }

def main():
    global PHASE
    try:
        out=run()
        code=0
    except Exception as error:
        out={
            "schema":"neon.portal_plant_change_x_competitor_ecology_holdout.v1",
            "status":"STOP_ORIGINAL_SOURCE_OR_PRESPECIFIED_MODEL",
            "stopped_stage":PHASE,
            "error_type":type(error).__name__,
            "stop_label":str(error)[:160],
            "no_favorable_subgroup_or_alternate_model_tried":True,
            "all_historical_2020_earlier_biology_unchanged":True,
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,sort_keys=True,indent=2))
    return code

if __name__=="__main__":
    raise SystemExit(main())
