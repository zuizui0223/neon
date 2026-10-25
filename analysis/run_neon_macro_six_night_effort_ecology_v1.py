#!/usr/bin/env python3
"""Original NEON exactly-two genus spatial recurrence under six-night common
recorded station opportunity (source-conditional observation QC only).

Original 158 pair cohort, same RELEASE-2026. The source-only all-six
station and 2+ genus support gates MUST pass before the exact-null
marginal variance gate. Cross-season genus×station overlap opened only
after variance eligibility is locked. No source IDs or climate modeled.
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
from statistics import mean
import json,os

from analysis.run_neon_two_genus_source_v1 import original_sources_for_two_genus
from analysis.run_multiscale_density_estimability_release2026_v3 import (
    _request_json,TOKEN_ENV
)
from analysis.run_neon_macro_temporal_weather_source_v1 import NEON_SITES
from analysis.neon_macro_site_selection_v1 import site_metadata_index
from analysis.neon_macro_six_night_effort_v1 import recorded_station_opportunity
from analysis.neon_exact_two_row_fixedmargin_v1 import (
    two_row_exact_marginal,observed_exact_unit,meta_exact_site_null,
)
from analysis.run_neon_exact_two_genus_ecology_v1 import reuse_physical_sites

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_macro_six_night_station_matched_recurrence_v1.json"
SOURCE=ROOT/"results/neon_macro_six_night_recorded_station_support_20261025.json"
ORIGINAL=ROOT/"results/neon_exact_two_genus_ecological_receipt_20261025.json"
DESIGN="docs/NEON_MACRO_SIX_NIGHT_COMMON_TRAP_OPPORTUNITY_20261025.md"
SEED=2026102558
META_DRAWS=20000

def check(ok:bool,why:str)->None:
    if not ok:raise RuntimeError("SIX_NIGHT_RECORDED_STATION_EFFECT_STOP: "+why)

def _variance_gate(units:list[dict],marginals:list[dict])->dict:
    """No observed A×B genus station overlap opened here."""
    if len(units)!=len(marginals):raise ValueError("Source and exact null count mismatched")
    included=[i for i,m in enumerate(marginals) if m["status"]=="EXACT_NONDEGENERATE"]
    site_count=len({units[i]["site"] for i in included})
    ok=(len(units)>=80 and len({u["site"] for u in units})>=18
        and len(included)>=40 and site_count>=12
        and len(included)/len(units)>=.75)
    return {
        "status":"SOURCE_SIX_NIGHT_EXACT_NULL_VARIANCE_GO" if ok else "STOP_SIX_NIGHT_EXACT_NULL_VARIANCE",
        "original_common_station_source_pairs":len(units),
        "informative_exact_null_pairs":len(included),
        "source_zero_variance_pairs":len(units)-len(included),
        "informative_independent_physical_sites":site_count,
        "fraction_of_original_common_station_pairs_informative":len(included)/len(units) if units else 0.,
        "minimum_predeclared_informative_fraction":.75,
        "minimum_predeclared_informative_pairs":40,
        "minimum_predeclared_sites":12,
        "passed":ok,
        "no_observed_A_cross_B_overlap_or_Z_yet_computed":True,
    }

def run()->dict:
    token=os.environ.get(TOKEN_ENV,"").strip()
    check(bool(token),"NEON original release authorization missing")
    frozen=json.loads(SOURCE.read_text(encoding="utf-8"))
    original=json.loads(ORIGINAL.read_text(encoding="utf-8"))
    check(frozen["status"]=="SOURCE_COMMON_SIX_NIGHT_RECORDED_STATION_GO"
          and frozen["retained_pairs"]==158
          and frozen["retained_independent_physical_sites"]==30
          and frozen["all_six_recorded_station_count_distribution"]["min"]==93,
          "source-only six-night published receipt no longer matches")
    check(original["observed"]["informative_exact_two_genus_pairs"]==150
          and original["observed"]["physical_sites"]==30,
          "historical original two-row ecological receipt drifted")
    strict,two,source,plot_rows,trap_rows=original_sources_for_two_genus(
        include_private_source_rows=True
    )
    check((len(strict),len(two),len({x["site"] for x in two}))==(58,158,30),
          "original seasonal source selection changed")
    sites={u["site"] for u in two}
    raw=_request_json(NEON_SITES).get("data")
    check(isinstance(raw,list),"official NEON domains unavailable")
    geo=site_metadata_index([r for r in raw if isinstance(r,dict) and r.get("siteCode") in sites])
    check(set(geo)==sites,"original site/domain join incomplete")
    footprint,restricted=recorded_station_opportunity(
        two,plot_rows,trap_rows,{s:geo[s]["domain"] for s in sites}
    )
    for key in ("status","retained_pairs","retained_independent_physical_sites",
                "retained_NEON_ecological_domains",
                "all_six_recorded_station_count_distribution"):
        check(footprint[key]==frozen[key],"original six-night source-only metrics changed")
    base={
        "schema":"neon.macro.six_night_common_recorded_station_exact_two_recurrence.v1",
        "research_status":"HISTORICAL_POST_RESULT_OBSERVATION_OPPORTUNITY_SENSITIVITY",
        "source_receipt":"results/neon_macro_six_night_recorded_station_support_20261025.json",
        "prior_ecology_receipt":"results/neon_exact_two_genus_ecological_receipt_20261025.json",
        "source_provenance":source,
        "fixed_design":DESIGN,
        "original_three_plus_58_positive_effect_not_recomputed":True,
        "original_density_eight_genus_5of8_generality_fail_not_changed":True,
        "genus_specific_catchability_still_unmeasured":True,
        "raw_animal_site_plot_genus_station_or_exact_dates_never_exported":True,
    }
    if footprint["status"]!="SOURCE_COMMON_SIX_NIGHT_RECORDED_STATION_GO":
        return {**base,"status":"STOP_RECORDED_COMMON_SIX_NIGHT_STATION_SOURCE_COVERAGE",
                "source_only_recorded_station_support":footprint,
                "new_observed_ecology_effect_opened":False}

    null=[two_row_exact_marginal(u["A"],u["B"]) for u in restricted]
    gate=_variance_gate(restricted,null)
    if not gate["passed"]:
        return {**base,"status":"STOP_COMMON_STATION_EXACT_NULL_VARIANCE_SUPPORT",
                "original_station_source_support_unchanged":True,
                "variance_pre_effect":gate,"new_observed_ecology_effect_opened":False}

    # Historical original-pair scores replay independently to ensure
    # revised station restriction does not alter existing target data.
    oldbysite=defaultdict(list)
    for unit in two:
        m=two_row_exact_marginal(unit["A"],unit["B"])
        if m["status"]!="EXACT_NONDEGENERATE":
            continue
        z=observed_exact_unit(unit["A"],unit["B"],m)["z"]
        check(z is not None,"Original known informative two-row null has no Z")
        oldbysite[unit["site"]].append(z)
    old_means=sorted(mean(x) for x in oldbysite.values())
    previous=original["observed"]["site_means_sorted_anonymous"]
    check(len(old_means)==len(previous)==30
          and all(abs(a-b)<1e-8 for a,b in zip(old_means,previous)),
          "historical original 30-site Z no longer reproduces")

    private=[]
    npositive=0
    bysite=defaultdict(list)
    for u,m in zip(restricted,null):
        if m["status"]!="EXACT_NONDEGENERATE":
            continue
        r=observed_exact_unit(u["A"],u["B"],m)
        check(r["z"] is not None,"exact uniform-null variance inconsistent with observed")
        zz=float(r["z"])
        npositive+=int(zz>0)
        private.append({"site":u["site"],"observed_z":zz,"exact_marginal":m})
        bysite[u["site"]].append(zz)
    check(len(private)==gate["informative_exact_null_pairs"]
          and len(bysite)==gate["informative_independent_physical_sites"],
          "original pre-effect denominator changed")
    meta=meta_exact_site_null(private,seed=SEED,n_replicates=META_DRAWS)
    source_reused=reuse_physical_sites(two)
    clean=[x for x in private if x["site"] not in source_reused]
    clean_site=len({x["site"] for x in clean})
    if len(clean)>=20 and clean_site>=8:
        cleanresult=meta_exact_site_null(clean,seed=SEED+200,n_replicates=META_DRAWS)
        cleanstatus="SOURCE_WHOLE_SITE_SEASON_REUSE_SENSITIVITY_FIT"
    else:
        cleanresult=None
        cleanstatus="STOP_WHOLE_SITE_SOURCE_REUSE_SUPPORT"
    p1=meta["independent_unit_exact_marginal_null"]["one_sided_plus_one_p"]
    p2=meta["rank_comonotone_within_site_exact_marginal_stress"]["one_sided_plus_one_p"]
    positive=(meta["observed_equal_site_mean_z"]>0 and p1<.05 and p2<.05)
    return {
        **base,
        "status":("OBSERVATION_MATCHED_STATION_EXPLORATORY_RECURRENCE_POSITIVE"
                  if positive else "OBSERVATION_MATCHED_STATION_EXPLORATORY_RECURRENCE_NOT_SUPPORTED"),
        "original_station_source_support_unchanged":True,
        "variance_pre_effect":gate,
        "historical_original_30_site_Z_exactly_replayed":True,
        "new_observed_ecology_effect_opened":True,
        "observed":{
            "site_weighted_mean_Z":meta["observed_equal_site_mean_z"],
            "informative_seasonal_pairs":len(private),
            "independent_physical_sites":len(bysite),
            "positive_unit_Z_count":npositive,
            "positive_site_mean_count":sum(mean(values)>0 for values in bysite.values()),
            "anonymous_site_means_sorted":[float(mean(values)) for site,values in sorted(bysite.items(),key=lambda x:mean(x[1]))],
        },
        "original_same_release_30_site_mean_Z_reference":original["observed"]["corrected_equal_site_mean_Z"],
        "conditional_meta_exact_two_row_marginal":meta,
        "whole_site_reused_season_sensitivity_status":cleanstatus,
        "whole_site_reused_season_sensitivity":cleanresult,
        "claim_boundary":{
            "recorded_station_roster_not_proof_of_operable_traps":True,
            "positive_under_both_conditional_null_scenarios":positive,
            "not_an_independent_new_biological_release":True,
            "source_season_temporal_dependence_not_fully_resolved":True,
            "genus_specific_catchability_or_stable_microhabitat_not_excluded":True,
            "no_climate_or_density_mechanism_fitted":True,
            "two_row_exact_marginal_uniform_null_not_full_site_joint_null":True,
        },
    }

def main()->int:
    try:
        result=run()
        code=0
    except Exception as e:
        result={
            "schema":"neon.macro.six_night_common_recorded_station_exact_two_recurrence.v1",
            "status":"STOP_SIX_NIGHT_RECORDED_TRAP_SOURCE_OR_EFFECT_INVARIANT",
            "error_class":type(e).__name__,
            "no_source_name_or_private_exception_values_exported":True,
            "original_neon_recurrence_effects_unchanged":True,
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return code

if __name__=="__main__":
    raise SystemExit(main())
