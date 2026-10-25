#!/usr/bin/env python3
"""Same-original-source ecological sensitivity under all-six-night trapStatus 4/5/6.

Exactly original 158 two-genus pairs, 30 physical sites, one fixed
observational control: retain only stations with certified source 4/5/6
codes on EVERY original trapping night and original >=2 genus stations in
both seasons. No climate, competition, habitat or larger spatial radius.
The complete source/variance conditions must pass before ANY NEW observed
genus-by-same-station temporal recurrence is opened.

An admissible result tests recorded trap functioning evidence, NOT
individual presence or genus-specific capture-detection probability.
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
from statistics import mean
import json,os

from analysis.run_neon_two_genus_source_v1 import original_sources_for_two_genus
from analysis.run_multiscale_density_estimability_release2026_v3 import _request_json,TOKEN_ENV
from analysis.run_neon_macro_temporal_weather_source_v1 import NEON_SITES
from analysis.neon_macro_site_selection_v1 import site_metadata_index
from analysis.neon_macro_6night_operable_trap_status_v1 import all_six_operable_source
from analysis.neon_exact_two_row_fixedmargin_v1 import (
    two_row_exact_marginal,observed_exact_unit,meta_exact_site_null
)
from analysis.run_neon_exact_two_genus_ecology_v1 import reuse_physical_sites

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_macro_6night_operable_status456_ecology_v1.json"
FROZEN=ROOT/"results/neon_macro_six_night_trapStatus456_SOURCE_STOP_20261026.json"
OLDER=ROOT/"results/neon_exact_two_genus_ecological_receipt_20261025.json"
DESIGN="docs/NEON_ALL_SIX_NIGHT_OPERABLE_TRAPSTATUS_GATE_20261026.md"
META_SEED=2026102662
META_DRAWS=20000

def require(ok:bool,msg:str):
    if not ok:raise RuntimeError("NEON_6NIGHT_OPERABLE_OBSERVATIONAL_STOP: "+msg)

def exact_null_variance_gate(units:list[dict],margins:list[dict])->dict:
    """Exact margin variance ONLY, before source-conditioned new overlap."""
    require(len(units)==len(margins),"Source and exact null variance lengths differ")
    good=[i for i,m in enumerate(margins) if m["status"]=="EXACT_NONDEGENERATE"]
    sites={units[i]["site"] for i in good}
    frac=len(good)/len(units) if units else 0
    passed=len(good)>=40 and frac>=.75 and len(sites)>=12
    return {
        "status":"OPERABLE_ALL6_UNIFORM_NULL_VARIANCE_GO" if passed
                 else "STOP_OPERABLE_ALL6_UNIFORM_NULL_INFORMATIVENESS",
        "all_six_456_original_qualifying_pairs":len(units),
        "positive_exact_null_variance_original_pairs":len(good),
        "zero_variance_original_pairs":len(units)-len(good),
        "positive_fraction_of_source_pairs":frac,
        "informative_physical_sites":len(sites),
        "minimum_informative_fraction":.75,
        "minimum_informative_pairs":40,
        "minimum_independent_sites":12,
        "passed":passed,
        "new_observed_seasonal_genus_trap_overlap_unopened_at_this_stage":True,
    }


def run()->dict:
    token=os.environ.get(TOKEN_ENV,"").strip()
    require(bool(token),"Original source access unavailable")
    old=json.loads(OLDER.read_text(encoding="utf-8"))
    locked=json.loads(FROZEN.read_text(encoding="utf-8"))
    if locked["status"]=="STOP_OPERABLE_456_SIX_NIGHT_SOURCE_SUPPORT":
        # The original fixed cohort failed the source gate (18/158 pairs).
        # Preserve that scientific STOP and avoid downloading or
        # generating any new genus×trap ecological response.
        require(locked["source_two_genus_original_pairs"]==158
                and locked["retained_pairs"]==18
                and locked["retained_physical_sites"]==8
                and locked["retained_NEON_domains"]==7
                and locked["original_source_rule"]["passed"] is False,
                "original all-six-night source STOP cohort changed")
        return {
            "schema":"neon.macro.operable_456_all_six_nights_two_genus_exact_recurrence.v1",
            "status":"STOP_ORIGINAL_ALL6_OPERABLE_STATUS456_SOURCE_GATE",
            "source_receipt":"results/neon_macro_six_night_trapStatus456_SOURCE_STOP_20261026.json",
            "original_exact_two_genus_pair_universe":158,
            "strict_all_six_456_retained_pairs":18,
            "strict_retained_independent_sites":8,
            "strict_retained_domains":7,
            "original_80pair_18site_10domain_source_threshold_unchanged":True,
            "new_operable_subcohort_ecological_Z_or_p_NOT_computed":True,
            "original_30_site_positive_capture_recurrence_unchanged":True,
            "outcome_selection_or_replacing_operability_definition_forbidden":True,
            "not_a_negative_animal_ecological_effect":True,
        }
    require(locked["status"]=="SOURCE_SIX_NIGHT_OPERABLE_456_GO"
            and locked["original_source_rule"]["passed"]
            and locked["source_two_genus_original_pairs"]==158
            and locked["source_original_physical_sites"]==30,
            "pre-effect trapStatus original source gate failed or unavailable")
    require(old["observed"]["informative_exact_two_genus_pairs"]==150
            and old["observed"]["physical_sites"]==30
            and old["status"]=="EXPLORATORY_CONDITIONAL_TWO_GENUS_RECURRENCE_POSITIVE",
            "historical original genus-specific recurrence source receipt altered")
    three,two,source,plots,traps=original_sources_for_two_genus(
        include_private_source_rows=True)
    require(len(three)==58 and len(two)==158,
            "immutable original source cohort drifted")
    official=_request_json(NEON_SITES).get("data")
    require(isinstance(official,list),"official NEON site/ecological domain metadata missing")
    sites={u["site"] for u in two}
    geo=site_metadata_index([r for r in official
                             if isinstance(r,dict) and r.get("siteCode") in sites])
    require(set(geo)==sites,"source physical sites not in published metadata")
    support,qualifying=all_six_operable_source(
        two,plots,traps,{site:geo[site]["domain"] for site in sites}
    )
    for k in ("status","source_two_genus_original_pairs","retained_pairs",
              "retained_physical_sites","retained_NEON_domains",
              "all_six_verified_status_456_stations",
              "pair_genus_station_retention_reason_counts"):
        require(support[k]==locked[k],"effect-blind status456 source facts changed")
    base={
        "schema":"neon.macro.operable_456_all_six_nights_two_genus_exact_recurrence.v1",
        "research_status":"HISTORICAL_POST_RESULT_SOURCE_CONDITIONAL_OPERABILITY_SENSITIVITY",
        "source_gate_receipt":"results/neon_macro_6night_operable_source_receipt_20261026.json",
        "prior_original_result_receipt":"results/neon_exact_two_genus_ecological_receipt_20261025.json",
        "design":DESIGN,
        "original_source":source,
        "original_strict_58_genus_source_and_effects_unchanged":True,
        "original_density_5_of_8_generality_fail_unmodified":True,
        "spatial_neighborhood_10m_strict_disjoint_null_unmodified":True,
        "not_a_new_observational_release_or_independent_replication":True,
        "source_genus_station_animal_tag_and_source_calendar_identifiers_not_exported":True,
    }
    if support["status"]!="SOURCE_SIX_NIGHT_OPERABLE_456_GO":
        return {**base,"status":"STOP_OPERABLE_456_ORIGINAL_SOURCE_COHORT",
                "new_ecological_effect_opened":False}
    margins=[two_row_exact_marginal(u["A"],u["B"]) for u in qualifying]
    variance=exact_null_variance_gate(qualifying,margins)
    if not variance["passed"]:
        return {**base,"status":"STOP_OPERABLE_456_EXACT_MARGIN_VARIANCE",
                "source_operability_replay_passed":True,
                "exact_variance_before_observations":variance,
                "new_ecological_effect_opened":False}

    # Validate unchanged OLD 30-site exact-two effect on original source,
    # not a new independent ecological finding.
    replay=defaultdict(list)
    n_old=0
    for u in two:
        m=two_row_exact_marginal(u["A"],u["B"])
        if m["status"]!="EXACT_NONDEGENERATE":continue
        z=observed_exact_unit(u["A"],u["B"],m)["z"]
        require(z is not None,"historical original unit Z unexpectedly missing")
        replay[u["site"]].append(z);n_old+=1
    oldsite=sorted(mean(z) for z in replay.values())
    frozen=old["observed"]["site_means_sorted_anonymous"]
    require(n_old==150 and len(oldsite)==len(frozen)==30
            and all(abs(a-b)<1e-8 for a,b in zip(oldsite,frozen)),
            "original 30-site recurrence source cannot be exactly replayed")

    bysite=defaultdict(list)
    private=[]
    positive_units=0
    for u,m in zip(qualifying,margins):
        if m["status"]!="EXACT_NONDEGENERATE":continue
        result=observed_exact_unit(u["A"],u["B"],m)
        z=result["z"]
        require(z is not None,"new operable 456 unit variance and observed score disagree")
        positive_units+=int(z>0)
        bysite[u["site"]].append(z)
        private.append({"site":u["site"],"observed_z":z,"exact_marginal":m})
    require(len(private)==variance["positive_exact_null_variance_original_pairs"]
            and len(bysite)==variance["informative_physical_sites"],
            "effect eligibility changed after source/variance GO")

    meta=meta_exact_site_null(private,seed=META_SEED,n_replicates=META_DRAWS)
    reused=reuse_physical_sites(two)
    clear=[q for q in private if q["site"] not in reused]
    clear_sites=len({q["site"] for q in clear})
    if len(clear)>=20 and clear_sites>=8:
        disjoint=meta_exact_site_null(clear,seed=META_SEED+200,n_replicates=META_DRAWS)
        disjoint_status="FULL_SITE_SOURCE_SEASON_KEY_REUSE_REMOVAL_COMPUTED"
    else:
        disjoint=None
        disjoint_status="STOP_FULL_SITE_SOURCE_REUSE_CLEAR_SUBSET_SUPPORT"
    full_positive=meta["observed_equal_site_mean_z"]>0 and (
        meta["independent_unit_exact_marginal_null"]["one_sided_plus_one_p"]<.05
        and meta["rank_comonotone_within_site_exact_marginal_stress"]["one_sided_plus_one_p"]<.05
    )
    clear_positive=(disjoint is not None and
        disjoint["observed_equal_site_mean_z"]>0 and
        disjoint["independent_unit_exact_marginal_null"]["one_sided_plus_one_p"]<.05
        and disjoint["rank_comonotone_within_site_exact_marginal_stress"]["one_sided_plus_one_p"]<.05
    )
    return {
        **base,
        "status":(
            "ALL_SIX_NIGHTS_456_CONDITIONAL_RECURRENCE_POSITIVE_AND_SOURCE_REUSE_ROBUST"
            if full_positive and clear_positive
            else "ALL_SIX_NIGHTS_456_CONDITIONAL_RECURRENCE_MIXED_OR_NOT_SUPPORTED"
        ),
        "new_ecological_effect_opened":True,
        "exact_variance_before_observations":variance,
        "original_30_site_old_effect_replayed_identically":True,
        "observed_operable456_same_trap_recurrence":{
            "informative_source_pairs":len(private),
            "independent_physical_sites":len(bysite),
            "positive_original_pairs":positive_units,
            "positive_site_mean_count":sum(mean(x)>0 for x in bysite.values()),
            "equal_site_mean_z":meta["observed_equal_site_mean_z"],
            "anonymous_site_mean_z_sorted":sorted(mean(x) for x in bysite.values()),
        },
        "full_conditioned_fixed_margin_site_null":meta,
        "source_reused_entire_physical_sites_removed":{
            "status":disjoint_status,
            "original_site_reuse_exclusion_sites":len(reused),
            "remaining_informative_pairs":len(clear),
            "remaining_physical_sites":clear_sites,
            "null_if_eligible":disjoint,
        },
        "decision":{
            "positive_in_both_site_coupling_scenarios":full_positive,
            "positive_under_source_reuse_disjoint_both_scenarios":clear_positive,
            "capture_trap_operability_evidence_not_individual_detection_probability":True,
            "habitat_selection_and_genus_catchability_not_identified":True,
            "no_new_10m_patch_or_temperature_or_WB_effect_estimated":True,
            "site_level_dependence_stress_not_a_proven_joint_ecological_null":True,
            "not_a_prospective_new_RELEASE_replication":True,
        },
    }


def main()->int:
    try:
        result=run();code=0
    except Exception as e:
        result={
            "schema":"neon.macro.operable_456_all_six_nights_two_genus_exact_recurrence.v1",
            "status":"STOP_OPERABLE_456_SOURCE_EFFECT_INVARIANT",
            "error_class":type(e).__name__,
            "original_observed_30_site_ecological_result_unchanged":True,
            "no_private_source_value_or_full_exception_message_exported":True,
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return code

if __name__=="__main__":
    raise SystemExit(main())
