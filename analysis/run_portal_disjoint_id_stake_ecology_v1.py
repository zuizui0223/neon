#!/usr/bin/env python3
"""Portal rodent individual-disjoint source-frozen ecology: exact 7x7 stakes.

Retrospective exploratory OUTCOME after separately committed protocol
docs/NEON_PORTAL_INDIVIDUAL_DISJOINT_SPATIAL_ECOLOGY_PROTOCOL_20261115.md
and source-only action #43677338828. No NEON or Structural outcome refit.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime,timezone
from math import fsum
from pathlib import Path
from random import Random
from statistics import mean,median
import json

from analysis.portal_external_id_niche_source_v1 import (
    FILES,YEARS,TRT,MIN_NEW_ID,MIN_STAKE,
    get_source,csv_rows,i,stake,audit
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/portal_identity_disjoint_stake_ecology_20261115.json"
STAKES=tuple(10*r+c for r in range(1,8) for c in range(1,8))
SOURCE_MIN_PAIRS=30
MIN_PLOTS_PER_TREATMENT=4
BOOTSTRAP=10000
BOOTSTRAP_SEED=2026111514

def gate(ok,what):
    if not ok:raise ValueError("FROZEN_PORTAL_ECOLOGY_STOP_"+what)

def remove_shared_individuals(A,B):
    """Delete ALL individual IDs observed in both census records."""
    common=set(A)&set(B)
    return ({k:v for k,v in A.items() if k not in common},
            {k:v for k,v in B.items() if k not in common},
            len(common))

def station_collision_and_reference(stations_a,stations_b,
                                    all_capture_a,all_capture_b):
    """Species individual-disjoint observed same-stake overlap vs fixed refs."""
    if not stations_a or not stations_b or not all_capture_a or not all_capture_b:
        raise ValueError("Empty original individual or species-blind station reference")
    for sample in (stations_a,stations_b,all_capture_a,all_capture_b):
        if any(v not in STAKES for v in sample):
            raise ValueError("Noncanonical original 7x7 capture stake")
    a=Counter(stations_a);b=Counter(stations_b)
    ca=Counter(all_capture_a);cb=Counter(all_capture_b)
    nA=len(stations_a);nB=len(stations_b)
    mA=len(all_capture_a);mB=len(all_capture_b)
    o=fsum(a[s]/nA*b[s]/nB for s in STAKES)
    e=fsum(ca[s]/mA*cb[s]/mB for s in STAKES)
    return {"observed":o,"speciesblind":o-e,"uniform":o-1/49,"source_reference":e}

def ecological_source(records):
    # Independent original 436-pair source is reconstructed before
    # any overlap calculations. Source IDs and stake positions remain
    # private and are never written to the result artifact.
    original=audit(records)
    support=original.get("source_only_summary",{}).get("source_pair_counts",{})
    gate(original["status"]=="SOURCE_PORTAL_DISJOINT_ID_STAKE_GO_NO_NICHE_EFFECT",
         "ORIGINAL_SOURCE_NOT_GO")
    gate(support["qualified_different_observed_ID_species_pairs"]==436
         and support["qualified_control"]==227
         and support["qualified_exclosure"]==209,
         "ORIGINAL_SOURCE_436_227_209_DRIFT")

    taxa,_=csv_rows(records["Rodents/Portal_rodent_species.csv"],
        ("speciescode","scientificname","rodent","granivore","censustarget","unidentified"))
    target={row["speciescode"].strip() for row in taxa if
            row["rodent"]=="1" and row["granivore"]=="1"
            and row["censustarget"]=="1" and row["unidentified"]=="0"}
    treatments,_=csv_rows(records["SiteandMethods/Portal_plots.csv"],
                          ("year","month","plot","treatment"))
    bytrt={(i(row["year"]),i(row["month"]),i(row["plot"])):
            (row["treatment"] or "").strip().lower() for row in treatments}

    trap,_=csv_rows(records["Rodents/Portal_rodent_trapping.csv"],
        ("year","month","period","plot","sampled","effort","qcflag"))
    sessions={};month_events=defaultdict(list)
    for row in trap:
        year=i(row["year"]);month=i(row["month"])
        period=i(row["period"]);plot=i(row["plot"])
        if None in (year,month,period,plot) or not YEARS[0]<=year<=YEARS[1] or period<=0:
            continue
        k=(plot,year,month,period)
        if k in sessions:raise ValueError("Duplicate original trapping census")
        treat=bytrt.get((year,month,plot))
        effort=i(row["effort"])
        eligible=(row["sampled"]=="1" and row["qcflag"]=="1"
                 and effort is not None and 48<=effort<=49 and treat in TRT)
        sessions[k]=(eligible,treat)
        if eligible:month_events[(plot,year,month)].append(k)

    rodent,_=csv_rows(records["Rodents/Portal_rodent.csv"],
        ("year","month","period","plot","stake","species","id"))
    # A captured individual is used at most once in a single source
    # census; conflicting stakes for the same ID are removed, NOT chosen.
    location=defaultdict(lambda:defaultdict(lambda:defaultdict(set)))
    observation=Counter()
    for row in rodent:
        key=(i(row["plot"]),i(row["year"]),i(row["month"]),i(row["period"]))
        if key not in sessions or not sessions[key][0]:
            continue
        sp=(row["species"] or "").strip()
        if sp not in target:continue
        animal=(row["id"] or "").strip()
        station=stake(row["stake"])
        if not animal or animal.lower() in ("na","nan","null") or station is None:
            continue
        location[key][sp][animal].add(station)
        observation["source_original_valid_identity_and_stake_rows"]+=1
    normalized={};invalid_multistake=Counter()
    for key,per_species in location.items():
        table=defaultdict(dict)
        for sp,animals in per_species.items():
            for ident,source_stakes in animals.items():
                if len(source_stakes)!=1:
                    invalid_multistake["source_ids_with_conflicting_same_census_stakes"]+=1
                    continue
                table[sp][ident]=next(iter(source_stakes))
        normalized[key]=table

    outcomes=[]
    excluded_shared=Counter()
    for plot,year,month in sorted(month_events):
        if year>=YEARS[1]:continue
        A=month_events[(plot,year,month)]
        B=month_events.get((plot,year+1,month),[])
        if len(A)!=1 or len(B)!=1:continue
        a,b=A[0],B[0]
        treatment=sessions[a][1]
        if treatment not in TRT or sessions[b][1]!=treatment:continue
        grouped_a=normalized.get(a,{})
        grouped_b=normalized.get(b,{})
        # Species-blind original row/station opportunity reference includes
        # focal species, conservatively. Every unique captured animal x taxon
        # contributes once in each year, never assuming trap-detection p.
        mix_a=Counter(st for spp,animals in grouped_a.items()
                      for animal,st in animals.items())
        mix_b=Counter(st for spp,animals in grouped_b.items()
                      for animal,st in animals.items())
        if not mix_a or not mix_b:continue
        for sp in sorted(set(grouped_a)&set(grouped_b)):
            all_a=grouped_a[sp];all_b=grouped_b[sp]
            new_a,new_b,n_shared=remove_shared_individuals(all_a,all_b)
            excluded_shared["removed_shared_observed_identifiers"]+=n_shared
            if min(len(new_a),len(new_b))<MIN_NEW_ID:
                continue
            if min(len(set(new_a.values())),len(set(new_b.values())))<MIN_STAKE:
                continue
            scores=station_collision_and_reference(
                list(new_a.values()),list(new_b.values()),
                list(st for n in mix_a for st in [n] for _ in range(mix_a[n])),
                list(st for n in mix_b for st in [n] for _ in range(mix_b[n])))
            outcomes.append({
                # Private, NEVER export these raw grouping identifiers
                "plot":plot,"year":year,"month":month,"species":sp,
                "treatment":treatment,"observed":scores["observed"],
                "uniform":scores["uniform"],"speciesblind":scores["speciesblind"],
                "ref":scores["source_reference"],"nA":len(new_a),"nB":len(new_b),
            })
    counts=Counter(x["treatment"] for x in outcomes)
    original_plots={t:{r["plot"] for r in outcomes if r["treatment"]==t} for t in TRT}
    source_go=(len(outcomes)>=SOURCE_MIN_PAIRS and
               all(len(original_plots[t])>=MIN_PLOTS_PER_TREATMENT for t in TRT))
    if not source_go:
        return {
            "schema":"neon.portal_individual_disjoint_stake_ecology.v1",
            "status":"STOP_PORTAL_AFTER_AMBIGUOUS_ID_REMOVAL_SOURCE_SUPPORT",
            "original_436_source_pairs_preserved":True,
            "retained_species_plot_year_pairs":len(outcomes),
            "original_source_treatment_comparisons":dict(sorted(counts.items())),
            "plots_per_treatment":{t:len(original_plots[t]) for t in TRT},
            "ambiguous_source_ID_counts":dict(invalid_multistake),
            "no_spatial_overlap_effect_or_p_value_exported":True,
        }

    by_plot=defaultdict(lambda:defaultdict(list))
    by_species=defaultdict(list)
    for x in outcomes:
        by_plot[x["plot"]][x["treatment"]].append(x)
        by_species[x["species"]].append(x)
    plots=sorted(by_plot)
    # Fixed whole-plot resampling preserves within-site year repetition.
    def from_sample(sample,metric):
        plot_values=[]
        bytrt=defaultdict(list)
        for plot in sample:
            p=by_plot[plot]
            vals=[v[metric] for group in p.values() for v in group]
            plot_values.append(mean(vals))
            for tr in TRT:
                if p.get(tr):bytrt[tr].append(mean(z[metric] for z in p[tr]))
        z={t:mean(bytrt[t]) if bytrt[t] else None for t in TRT}
        diff=z["exclosure"]-z["control"] if all(v is not None for v in z.values()) else None
        return mean(plot_values),z,diff
    all_plots,base_treat,base_diff=from_sample(plots,"speciesblind")
    uniform_mean,uniform_treat,uniform_diff=from_sample(plots,"uniform")
    rng=Random(BOOTSTRAP_SEED)
    boot_mean=[];boot_diff=[]
    for _ in range(BOOTSTRAP):
        sample=[plots[rng.randrange(len(plots))] for __ in plots]
        v,tr,d=from_sample(sample,"speciesblind")
        boot_mean.append(v)
        if d is not None:boot_diff.append(d)
    boot_mean.sort();boot_diff.sort()
    gate(len(boot_diff)>=0.95*BOOTSTRAP,"WHOLE_PLOT_BOOTSTRAP_GROUP_COVERAGE")

    def stats(vs):
        return {"min":min(vs),"median":median(vs),"max":max(vs),"mean":mean(vs),
                "positive":sum(v>0 for v in vs),
                "negative":sum(v<0 for v in vs),
                "zero":sum(v==0 for v in vs)}
    total=stats([r["speciesblind"] for r in outcomes])
    # All taxa reported. Never cherry-pick based on effect signs.
    taxa_report={
        sp:{"source_pairs":len(vs),"raw_pair_mean_speciesblind_excess":mean(x["speciesblind"] for x in vs),
            "raw_pair_mean_uniform_excess":mean(x["uniform"] for x in vs),
            "plot_clusters":len({x["plot"] for x in vs})}
        for sp,vs in sorted(by_species.items())
    }
    return {
        "schema":"neon.portal_individual_disjoint_stake_ecology.v1",
        "status":"EXTERNAL_PORTAL_OBSERVED_STAKE_RECURRENCE_EXPLORATORY_NOT_NICHE_CAUSATION",
        "source_provenance":{
            "original_portal_git_commit":"afd75933249ae60f3a5e9dab00b354f219e5e045",
            "original_github_source_file_blobs_verified":True,
            "original_preoutcome_source_436_pairs_go":True,
            "source_preoutcome_action_run":43677338828,
            "ecological_test_protocol_precommitted":"docs/NEON_PORTAL_INDIVIDUAL_DISJOINT_SPATIAL_ECOLOGY_PROTOCOL_20261115.md",
            "portal_is_one_physical_landscape":True,
        },
        "unit_and_support":{
            "retained_source_individual_disjoint_species_plot_year_pairs":len(outcomes),
            "control_comparisons":counts["control"],"exclosure_comparisons":counts["exclosure"],
            "original_unique_plot_clusters_total":len(plots),
            "original_plot_clusters_by_treatment":{t:len(original_plots[t]) for t in TRT},
            "original_Neon_and_Structural_response_not_read":True,
            "ambiguous_same_census_multistake_IDs_removed":dict(invalid_multistake),
            "shared_observed_ID_removal_count_by_source":dict(excluded_shared),
        },
        "observed_species_stake_collision":{
            "definition":"probability two observed ID-disjoint same-species individuals from adjacent-year same-month censuses are recorded at the exact same Portal stake",
            "uniform_49_stake_baseline_collision":1/49,
            "all_species_census_specific_station_reference":"dot product of plot-year all-target-granivore capture-station shares, INCLUDING focal species; a conservative observed-source reference",
            "raw_pair_speciesblind_excess_summary":total,
            "equal_original_plot_speciesblind_mean_excess":all_plots,
            "equal_plot_speciesblind_bootstrap95":[boot_mean[250],boot_mean[9749]],
            "equal_original_plot_uniform_mean_excess":uniform_mean,
            "equal_plot_speciesblind_by_treatment":base_treat,
            "equal_plot_uniform_by_treatment":uniform_treat,
            "equal_plot_exclosure_minus_control_speciesblind":base_diff,
            "equal_plot_exclosure_minus_control_bootstrap95":[boot_diff[int(.025*len(boot_diff))],boot_diff[min(len(boot_diff)-1,int(.975*len(boot_diff))-1)]],
            "equal_plot_exclosure_minus_control_uniform":uniform_diff,
            "species_code_source_counts_and_exploratory_effects":taxa_report,
            "plot_cluster_bootstrap_draws":BOOTSTRAP,
            "plot_cluster_seed":BOOTSTRAP_SEED,
            "no_p_values_computed":True,
        },
        "scientific_interpretation":{
            "measured_only_observed_species_capture_station_recurrence":True,
            "true_niche_realized_resource_selection_or_individual_survival_NOT_identified":True,
            "bait_trap_location_and_species_specific_detectability_unmeasured":True,
            "long_term_competitor_exclosure_vs_control_not_repeated_randomized_event_effect":True,
            "2019_Portal_Chaetodipus_patch_prior_art_and_2022_rodent_spatial_niche_prior_art":True,
            "this_is_retrospective_independent_source_not_preregistered_external_confirmation":True,
            "one_geographical_Portal_field_system_with_many_corrrelated_plot_years":True,
            "NEON_original_corrected_14site_Z_and_failure_gates_UNCHANGED":True,
            "Structural_529_ultrarare_island_maps_not_used":True,
        },
        "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }

def main():
    try:
        source={path:get_source(path) for path in FILES}
        result=ecological_source(source)
        code=0
    except Exception as exc:
        result={
            "schema":"neon.portal_individual_disjoint_stake_ecology.v1",
            "status":"STOP_PORTAL_ORIGINAL_SOURCE_OR_ANALYSIS",
            "error_class":type(exc).__name__,
            "no_old_NEON_or_Structural_response_recomputed":True,
            "raw_animal_ID_plot_month_or_stake_not_exported":True,
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True))
    return code

if __name__=="__main__":raise SystemExit(main())
