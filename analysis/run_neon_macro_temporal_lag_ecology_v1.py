#!/usr/bin/env python3
"""Post-result, source-precommitted association of actual seasonal sampling lag
and mathematically exact two-genus station recurrence, with two-way site and
transition adjustment. Never reinterpret an observed association as climate,
memory, real demographic turnover or a confirmed causal mammal mechanism.
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import json
from statistics import mean

from analysis.run_neon_two_genus_source_v1 import original_sources_for_two_genus
from analysis.run_neon_macro_temporal_weather_source_v1 import bout_start_gap
from analysis.neon_exact_two_row_fixedmargin_v1 import (
    two_row_exact_marginal,observed_exact_unit
)
from analysis.neon_macro_site_fixed_lag_model_v1 import site_fixed_lag_model
from analysis.run_neon_exact_two_genus_ecology_v1 import reuse_physical_sites

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"results/neon_macro_temporal_weather_source_receipt_20261025.json"
OLD=ROOT/"results/neon_exact_two_genus_ecological_receipt_20261025.json"
OUT=ROOT/"build/neon_macro_temporal_lag_ecology_v1.json"
SEED=2026102516
BOOTSTRAPS=2000


def require(ok:bool,why:str)->None:
    if not ok:raise RuntimeError("MACRO_LAG_ORIGINAL_SOURCE_AND_EFFECT_STOP: "+why)


def _corrected_source_and_variance()->tuple[list[dict],list[dict],dict]:
    source=json.loads(SOURCE.read_text(encoding="utf-8"))
    old=json.loads(OLD.read_text(encoding="utf-8"))
    require(source["status"]=="SOURCE_ONLY_LAG_AND_TOWER_WEATHER_AVAILABILITY_AUDITED"
            and source["lag_effect_source_precheck"]["source_only_non_effect_prerequisites_pass"],
            "original lag-date feasibility did not pass")
    require(old["status"]=="EXPLORATORY_CONDITIONAL_TWO_GENUS_RECURRENCE_POSITIVE"
            and old["variance_source_support"]["passed"]
            and old["observed"]["informative_exact_two_genus_pairs"]==150,
            "original exact-two source effect receipt altered")
    original_strict,two,source_info=original_sources_for_two_genus()
    two.sort(key=lambda u:(u["site"],tuple(u["site_plot"]),u["season_ordinal"]))
    require(len(two)==158 and len(original_strict)==58
            and len({u["site"] for u in two})==30,
            "original two-genus + three-genus source population drift")
    # ONLY exact conditional NULL VARIANCE and source capture-day gaps.
    # This construction does not compare original source season A with B
    # on the same genus/trap position yet.
    marg=[]
    source_gap=[]
    by_site=defaultdict(list)
    catcount={}
    for u in two:
        m=two_row_exact_marginal(u["A"],u["B"])
        g=bout_start_gap(u)
        require(0<g<400,"original date missing or invalid")
        marg.append(m)
        source_gap.append(g)
        if m["status"]=="EXACT_NONDEGENERATE":
            by_site[u["site"]].append(g)
            cat=u["season_ordinal"]%4
            catcount[cat]=catcount.get(cat,0)+1
    num=sum(v["status"]=="EXACT_NONDEGENERATE" for v in marg)
    varying=sum(len(set(g))>=2 for g in by_site.values())
    wide=sum(len(g)>=2 and max(g)-min(g)>=30 for g in by_site.values())
    enough=(num>=100 and varying>=15 and wide>=8 and len(catcount)>=3)
    pre={
        "source_exact_two_pairs":len(two),
        "historical_exact_null_informative_pairs":num,
        "physical_sites_with_two_or_more_distinct_original_start_gaps":varying,
        "physical_sites_with_source_gap_range_at_least_30_days":wide,
        "original_transition_classes":sorted(catcount),
        "source_only_no_G_x_observed_Z_relationship_opened":True,
        "lag_effect_gate_pass":enough,
        "source_untouched_original_58_threeplus_pairs":len(original_strict),
    }
    if not enough:
        return two,marg,{"status":"STOP_LAG_FEASIBILITY_BEFORE_RESPONSE_ASSOCIATION",
                         "pre_effect_source_check":pre,
                         "source":source_info}
    return two,marg,{"status":"LAG_FEASIBILITY_GO_ORIGINAL_EFFECT_REPLAY_NEXT",
                     "pre_effect_source_check":pre,
                     "source":source_info}


def run()->dict:
    two,marg,source_check=_corrected_source_and_variance()
    head={
        "schema":"neon.macro.exact_two_genus_temporal_persistence_lag.v1",
        "research_status":"POST_RESULT_SAME_NEON_RELEASE_2026_EXPLORATORY_NOT_INDEPENDENT_VALIDATION",
        "source_result":"results/neon_macro_temporal_weather_source_receipt_20261025.json",
        "original_exact_null_effect_result":"results/neon_exact_two_genus_ecological_receipt_20261025.json",
        "source_frozen_design":"docs/NEON_MACRO_TEMPORAL_PERSISTENCE_CONTEXT_20261025.md",
        "source_and_variance":source_check,
        "old_corrected_original_threeplus_result_untouched":True,
        "old_eight_genus_density_generality_failed_unchanged":True,
        "no_genus_site_station_animal_or_source_date_identity_exported":True,
        "no_site_climate_variable_or_mechanism_fitted":True,
        "not_a_trial_of_true_demographic_replacement_or_cognitive_memory":True,
    }
    if source_check["status"]!="LAG_FEASIBILITY_GO_ORIGINAL_EFFECT_REPLAY_NEXT":
        return {**head,"status":"STOP_EXPLORATORY_LAG_SOURCE_FEASIBILITY",
                "lag_Z_regression_opened":False}
    old=json.loads(OLD.read_text(encoding="utf-8"))
    records=[]
    bysite=defaultdict(list)
    source_reused_sites=reuse_physical_sites(two)
    for u,m in zip(two,marg):
        if m["status"]!="EXACT_NONDEGENERATE":
            continue
        z=observed_exact_unit(u["A"],u["B"],m)["z"]
        require(z is not None,"original accepted exact-null variance mismatch")
        site=u["site"]
        bysite[site].append(z)
        records.append({
            "site":site,"z":z,
            "gap_days":bout_start_gap(u),
            "transition":u["season_ordinal"]%4,
        })
    site_means=sorted(mean(items) for items in bysite.values())
    original_means=old["observed"]["site_means_sorted_anonymous"]
    require(len(site_means)==len(original_means)==30
            and all(abs(a-b)<1e-8 for a,b in zip(site_means,original_means))
            and len(records)==150
            and abs(mean(site_means)-old["observed"]["corrected_equal_site_mean_Z"])<1e-9,
            "original 150-source exact-null corrected ecological Zs do not reproduce")

    primary=site_fixed_lag_model(records,seed=SEED,n_bootstrap=BOOTSTRAPS)
    clean=[r for r in records if r["site"] not in source_reused_sites]
    clean_sites=len({r["site"] for r in clean})
    clean_variation=sum(len({r["gap_days"] for r in clean if r["site"]==s})>=2
                        for s in {r["site"] for r in clean})
    if len(clean)>=30 and clean_sites>=8 and clean_variation>=5:
        secondary=site_fixed_lag_model(clean,seed=SEED+200,n_bootstrap=BOOTSTRAPS)
        secondary_status=secondary["status"]
    else:
        secondary=None
        secondary_status="STOP_HISTORICAL_ENTIRE_REUSED_SITE_SUBSET_INSUFFICIENT_LAG_SUPPORT"
    return {
        **head,
        "status":(
            "EXPLORATORY_TEMPORAL_LAG_ASSOCIATION_ESTIMATED"
            if primary["status"]=="EXPLORATORY_SITE_AND_TRANSITION_ADJUSTED_LAG_ESTIMATED"
            else "STOP_TEMPORAL_LAG_MODEL_FULL_RANK_OR_BOOTSTRAP"
        ),
        "replayed_original_two_genus_site_effects_exactly":True,
        "lag_Z_regression_opened":True,
        "primary_exact_two_site_and_season_adjusted_lag":primary,
        "whole_source_reused_physical_site_exclusion":{
            "excluded_physical_sites_count":len(source_reused_sites),
            "remaining_informative_pairs":len(clean),
            "remaining_physical_sites":clean_sites,
            "sites_with_two_plus_distinct_actual_gaps":clean_variation,
            "secondary_status":secondary_status,
            "secondary_model":secondary,
        },
        "scientific_limits":{
            "conditional_genus_capture_station_recurrence_not_true_occupancy":True,
            "source_2026_outcome_already_opened_before_lag_question":True,
            "temporal_gap_correlational_not_mechanism":True,
            "within_site_source_season_reuse_still_possible_in_full_model":True,
            "site_block_bootstrap_not_full_joint_null":True,
            "not_independent_new_release_or_new_preregistration":True,
            "no_climate_weather_values_fitted":True,
        },
    }


def main()->int:
    try:
        r=run()
        code=0
    except Exception as e:
        r={
            "schema":"neon.macro.exact_two_genus_temporal_persistence_lag.v1",
            "status":"STOP_ORIGINAL_SOURCE_OR_TEMPORAL_LAG_FIT",
            "error_class":type(e).__name__,
            "private_original_identity_or_exception_not_exported":True,
            "old_corrected_neon_recurrence_and_density_results_not_modified":True,
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(r,indent=2,sort_keys=True))
    return code

if __name__=="__main__":
    raise SystemExit(main())
