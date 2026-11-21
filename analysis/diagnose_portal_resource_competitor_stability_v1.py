#!/usr/bin/env python3
"""After-outcome diagnostic only: fixed model leave-plot / leave-year transport.

No source filtering, alternate ecological model, "best subgroup" selection,
learning/biomass inference, or new primary threshold. Original 2020-25
resource × competitor outcome remains unchanged and exploratory.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
import json

from analysis.portal_external_id_niche_source_v1 import FILES,get_source
from analysis.audit_portal_resources_competition_learning_source_v1 import (
    NEW_FILES,original_extra
)
from analysis.run_portal_resource_competition_holdout_ecology_v1 import (
    ecology_source_rows,fit_fixed,
)
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_portal_resource_competitor_postresult_stability_20261120.json"
PHASE="VERIFY_FROZEN_ORIGINAL_SOURCE"

def fitted_or_stop(rows):
    try:
        control,exclosure,interaction=fit_fixed(rows)
    except Exception as exc:
        return {"estimable":False,"failure_class":type(exc).__name__}
    return {"estimable":True,"control":control,
            "exclosure":exclosure,"interaction":interaction}

def diagnostics(rows):
    from math import isfinite
    plots=sorted({u["plot"] for u in rows})
    years=sorted({u["start_year"] for u in rows})
    orig=fitted_or_stop(rows)
    if not orig["estimable"] or len(rows)!=114 or len(plots)!=18 or len(years)!=3:
        raise ValueError("FROZEN_ORIGINAL_114_18_3_PRIMARY_DRIFT")
    if abs(orig["control"]-(-.11064319013971634)) > 1e-10 or (
        abs(orig["interaction"]-.12954017554977257)>1e-10
    ):
        raise ValueError("FROZEN_ORIGINAL_ESTIMATE_NOT_REPRODUCED")
    byyear=[]
    for year in years:
        d=[x for x in rows if x["start_year"]!=year]
        v=fitted_or_stop(d)
        byyear.append({"omitted_start_year":year,"fitted_pairs":len(d),**v})
    byplot=[]
    for plot in plots:
        d=[x for x in rows if x["plot"]!=plot]
        byplot.append(fitted_or_stop(d))
    validplot=[x for x in byplot if x["estimable"]]
    validyear=[x for x in byyear if x["estimable"]]
    samples=defaultdict(list)
    for row in rows:
        samples[(row["plot"],row["start_year"])].append(row["x"])
    group_sizes=[len(z) for z in samples.values()]
    unique_x=sum(len({round(x,12) for x in z}) for z in samples.values())
    repeats=sum(len(z)-len({round(x,12) for x in z}) for z in samples.values())
    def ranges(dat,name):
        if not dat:
            return None
        v=[z[name] for z in dat]
        if any(not isfinite(x) for x in v):
            raise ValueError("NONFINITE_LEAVE_OUT_ESTIMATE")
        return [min(v),max(v)]
    return {
        "schema":"neon.portal_plant_change_competitor_postresult_stability.v1",
        "status":"POSTRESULT_SAME_FROZEN_MODEL_DIAGNOSTIC_NOT_CONFIRMATORY",
        "primary_frozen_effects_unchanged":orig,
        "identifiability_and_temporal_support":{
            "frozen_plot_month_year_pairs":len(rows),
            "frozen_independent_original_plots":len(plots),
            "start_years_with_pairs":len(years),
            "distinct_plot_x_startyear_resource_exposure_groups":len(samples),
            "original_pairs_reusing_plot_year_resource_information":repeats,
            "distinct_resource_change_values_across_plot_years":unique_x,
            "min_pairs_per_plot_year_group":min(group_sizes),
            "max_pairs_per_plot_year_group":max(group_sizes),
            "all_plant_resource_measurements_are_plot_not_49_stake":True,
        },
        "leave_one_original_plot_out":{
            "n_plots_removed_in_turn":len(plots),
            "n_estimable_original_model":len(validplot),
            "resource_slope_control_range":ranges(validplot,"control"),
            "resource_slope_exclosure_range":ranges(validplot,"exclosure"),
            "interaction_slope_range":ranges(validplot,"interaction"),
            "positive_interaction_count":sum(d["interaction"]>0 for d in validplot),
            "negative_control_slope_count":sum(d["control"]<0 for d in validplot),
            "failures_all_retained":dict(Counter(d.get("failure_class") for d in byplot if not d["estimable"]))
        },
        "leave_one_original_start_year_out":{
            "n_years_removed_in_turn":len(years),
            "year_omission_records":byyear,
            "n_estimable_original_model":len(validyear),
            "resource_slope_control_range":ranges(validyear,"control"),
            "interaction_slope_range":ranges(validyear,"interaction"),
            "positive_interaction_count":sum(d["interaction"]>0 for d in validyear),
            "negative_control_slope_count":sum(d["control"]<0 for d in validyear),
            "failures_all_retained":dict(Counter(d.get("failure_class") for d in byyear if not d["estimable"]))
        },
        "scientific_limits":{
            "post_result_diagnostic_not_hypothesis_confirmation":True,
            "three_start_years_not_sufficient_for_regime_inference":True,
            "same_plot_months_and_years_not_independent_samples":True,
            "no_biomass_or_learning_evidence":True,
            "no_change_to_original_Portal_NEON_Finland_Structural_outcomes":True,
            "submission_HOLD":True,
        },
        "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }

def run():
    global PHASE
    source={p:get_source(p) for p in FILES}
    for path in NEW_FILES:
        source[path]=original_extra(path)
    PHASE="RECONSTRUCT_UNMODIFIED_ORIGINAL_2020_25_ESTIMAND"
    _,rows,_,_,_=ecology_source_rows(source)
    PHASE="POSTRESULT_LEAVE_PLOT_YEAR_DIAGNOSTIC"
    return diagnostics(rows)

def main():
    global PHASE
    try:
        obj=run()
        code=0
    except Exception as e:
        obj={
            "schema":"neon.portal_plant_change_competitor_postresult_stability.v1",
            "status":"STOP_FROZEN_MODEL_DIAGNOSTIC",
            "stage":PHASE,"failure_class":type(e).__name__,
            "failure_label":str(e)[:150],
            "no_alternate_models_or_outcome_filtering":True,
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n")
    print(json.dumps(obj,sort_keys=True,indent=2))
    return code
if __name__=="__main__":
    raise SystemExit(main())
