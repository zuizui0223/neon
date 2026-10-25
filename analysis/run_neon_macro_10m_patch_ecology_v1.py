#!/usr/bin/env python3
"""Exploratory NEON 10m rook-neighbor genus patch spatial recurrence.

Original same-release source only: 158 EXACT two-genus adjacent-season
pairs, 30 physical sites, same six-night recorded trapping stations.
The newly tested neighbor score is conditioned mathematically on the
ALREADY observed exact-station genus overlap so self-trap matching
alone cannot account for a conditional neighbor signal.

Source and exact conditional neighbor variance gates MUST pass BEFORE
opening any new observed neighbor score. Every conditioned unit's null
draw is independent directly from uniform finite target; site-level
20k null calibrations explore nested dependence, not true catchability.
"""
from __future__ import annotations
import json,os
from pathlib import Path
from collections import defaultdict
from statistics import mean

from analysis.run_neon_two_genus_source_v1 import original_sources_for_two_genus
from analysis.run_multiscale_density_estimability_release2026_v3 import (
    _request_json,TOKEN_ENV
)
from analysis.run_neon_macro_temporal_weather_source_v1 import NEON_SITES
from analysis.neon_macro_site_selection_v1 import site_metadata_index
from analysis.neon_macro_six_night_effort_v1 import recorded_station_opportunity
from analysis.neon_exact_two_row_fixedmargin_v1 import (
    two_row_exact_marginal,observed_exact_unit
)
from analysis.run_neon_exact_two_genus_ecology_v1 import reuse_physical_sites
from analysis.neon_macro_10m_patch_conditional_v1 import (
    conditional_patch_profile,observed_patch,iid_conditional_patch_null,
    geometry_coverage
)
from analysis.neon_crossseason_direct_site_null_v1 import direct_site_null_calibration

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_macro_10m_patch_conditioned_exact_station_v1.json"
OLD=ROOT/"results/neon_macro_six_night_common_station_recurrence_receipt_20261025.json"
EFFORT=ROOT/"results/neon_macro_six_night_recorded_station_support_20261025.json"
DESIGN="docs/NEON_10M_PATCH_BEYOND_EXACT_STATION_DESIGN_20261025.md"
SEED_UNIT=2026102531
SEED_META=2026102532
DRAWS_UNIT=2000
DRAWS_META=20000
MIN_INF=80
MIN_SITES=18
SENS_MIN_SITE=8
SENS_MIN_PAIR=25


def require(cond:bool,why:str):
    if not cond:
        raise ValueError("NEON_10M_PATCH_ORIGINAL_SOURCE_STOP: "+why)


def conditional_variance_support(
    units:list[dict], profiles:list[dict],
    *,min_informative_pairs:int=MIN_INF,min_sites:int=MIN_SITES,
)->dict:
    """New neighborhood score is not opened here; conditioning on OLD O."""
    require(len(units)==len(profiles)==158,
            "exactly-two original 158 source units not preserved")
    indices=[i for i,p in enumerate(profiles)
             if p["status"]=="EXACT_CONDITIONAL_NEIGHBOR_VARIANCE_POSITIVE"]
    site_n=len({units[i]["site"] for i in indices})
    passed=len(indices)>=min_informative_pairs and site_n>=min_sites
    return {
        "status":"SOURCE_AND_PATCH_CONDITIONAL_VARIANCE_GO" if passed
                 else "STOP_EXACT_CONDITIONED_NEIGHBOR_VARIANCE_SUPPORT",
        "original_source_pairs":len(units),
        "exact_conditional_variance_positive_pairs":len(indices),
        "exact_conditional_variance_zero_pairs":len(units)-len(indices),
        "informative_physical_sites":site_n,
        "minimum_predeclared_informative_pairs":min_informative_pairs,
        "minimum_predeclared_independent_sites":min_sites,
        "passed":passed,
        "source_same_trap_overlap_already_opened_and_conditioned":True,
        "new_neighborhood_observed_score_NOT_yet_opened":True,
        "geographic_source_ids_not_exported":True,
    }


def build_source():
    token=os.environ.get(TOKEN_ENV,"").strip()
    require(bool(token),"original RELEASE-2026 provider token missing")
    frozen=json.loads(EFFORT.read_text(encoding="utf-8"))
    old=json.loads(OLD.read_text(encoding="utf-8"))
    require(frozen["status"]=="SOURCE_COMMON_SIX_NIGHT_RECORDED_STATION_GO"
            and frozen["retained_pairs"]==158 and frozen["retained_independent_physical_sites"]==30,
            "previous six-night recorded station source receipt missing")
    require(old["status"]=="OBSERVATION_MATCHED_STATION_EXPLORATORY_RECURRENCE_POSITIVE"
            and old["observed"]["informative_seasonal_pairs"]==150
            and old["observed"]["independent_physical_sites"]==30,
            "prior corrected six-night same-station ecological receipt changed")
    strict,two,src,plots,traps=original_sources_for_two_genus(include_private_source_rows=True)
    require(len(strict)==58 and len(two)==158,"original source episode group drift")
    sites={x["site"] for x in two}
    published=_request_json(NEON_SITES).get("data")
    require(isinstance(published,list),"official source domain metadata unavailable")
    metadata=site_metadata_index([r for r in published
                                  if isinstance(r,dict) and r.get("siteCode") in sites])
    require(set(metadata)==sites,"original sites missing source domain")
    support,units=recorded_station_opportunity(
        two,plots,traps,{s:metadata[s]["domain"] for s in sites}
    )
    require(support["status"]=="SOURCE_COMMON_SIX_NIGHT_RECORDED_STATION_GO"
            and support["retained_pairs"]==158
            and support["retained_NEON_ecological_domains"]==15
            and support["all_six_recorded_station_count_distribution"]==
            frozen["all_six_recorded_station_count_distribution"],
            "six-night original station intersection no longer reproduces")
    # Verify the old conditional genus same-station effects without using
    # any new neighbor statistic.
    siteZ=defaultdict(list)
    nold=0
    for u in units:
        mar=two_row_exact_marginal(u["A"],u["B"])
        if mar["status"]!="EXACT_NONDEGENERATE":continue
        z=observed_exact_unit(u["A"],u["B"],mar)["z"]
        require(z is not None,"old exact unit had no standardized score")
        siteZ[u["site"]].append(z)
        nold+=1
    grand=mean(mean(values) for values in siteZ.values())
    require(nold==150 and len(siteZ)==30
            and abs(grand-old["observed"]["site_weighted_mean_Z"])<1e-8,
            "old 30-site ecological station recurrence cannot be reconstructed")
    return sorted(units,key=lambda u:(u["site"],tuple(u["site_plot"]),u["season_ordinal"])),src,two,support


def run()->dict:
    require((SEED_UNIT,SEED_META,DRAWS_UNIT,DRAWS_META,MIN_INF,MIN_SITES)==
            (2026102531,2026102532,2000,20000,80,18),
            "pre-outcome conditional patch null settings modified")
    units,src,full_two,original_support=build_source()
    profiles=[conditional_patch_profile(u["A"],u["B"]) for u in units]
    gate=conditional_variance_support(units,profiles)
    base={
        "schema":"neon.macro.exact_two_10m_patch_given_original_same_trap.v1",
        "design":DESIGN,
        "research_status":"HISTORICAL_SAME_RELEASE_POST_RESULT_NEW_SPATIAL_SCALE_EXPLORATION",
        "original_source":src,
        "geometry_nominal_10m_rook":geometry_coverage(),
        "source_common_six_night_original_pairs":original_support["retained_pairs"],
        "source_common_six_night_physical_sites":original_support["retained_independent_physical_sites"],
        "source_common_six_night_domains":original_support["retained_NEON_ecological_domains"],
        "source_conditional_null_variance_gate":gate,
        "old_exact_two_genus_150pair_30site_Z_reproduced_before_patch_outcome":True,
        "conditioning_on_previously_opened_exact_station_overlap":True,
        "unresolved_taxon_specific_catchability_and_microhabitat":True,
        "new_site_genus_trap_animal_exact_date_or_source_IDs_never_exported":True,
        "old_58_strict_recurrence_and_WB_density_5of8_fail_unchanged":True,
    }
    if not gate["passed"]:
        return {
            **base,
            "status":"STOP_EXACT_TWO_10M_NEIGHBOR_CONDITIONAL_VARIANCE",
            "new_observed_patch_recurrence_opened":False,
            "conditional_site_meta_null_opened":False,
        }
    unit_private=[]
    bysite=defaultdict(list)
    positive_units=0
    for idx,(u,p) in enumerate(zip(units,profiles)):
        if p["status"]!="EXACT_CONDITIONAL_NEIGHBOR_VARIANCE_POSITIVE":
            continue
        obs=observed_patch(u["A"],u["B"],p)
        z=obs["Z_patch_given_exact_station_overlap"]
        draw=iid_conditional_patch_null(p,seed=SEED_UNIT+idx,n_draws=DRAWS_UNIT)
        require(len(draw)==DRAWS_UNIT,"Direct iid patch null missing draws")
        unit_private.append({
            "site":u["site"],"observed_unit_z":z,
            "null_unit_z_draws":draw,
        })
        bysite[u["site"]].append(z)
        positive_units+=int(z>0)
    require(len(unit_private)==gate["exact_conditional_variance_positive_pairs"]
            and len(bysite)==gate["informative_physical_sites"],
            "new neighborhood effect eligibility changed after gate")
    site_mean=[mean(values) for values in bysite.values()]
    meta=direct_site_null_calibration(unit_private,seed=SEED_META,n_replicates=DRAWS_META)
    require(abs(meta["observed_equal_site_weighted_mean_Z"]-mean(site_mean))<1e-10,
            "conditional 10m score site equal-weight aggregation inconsistent")
    reused_sites=reuse_physical_sites(full_two)
    clean=[u for u in unit_private if u["site"] not in reused_sites]
    clean_sites=len({u["site"] for u in clean})
    if len(clean)>=SENS_MIN_PAIR and clean_sites>=SENS_MIN_SITE:
        clean_cal=direct_site_null_calibration(clean,seed=SEED_META+200,n_replicates=DRAWS_META)
        clean_status="SOURCE_WHOLE_PHYSICAL_SITE_REUSE_EXCLUSION_CALIBRATED"
    else:
        clean_cal=None
        clean_status="STOP_SITE_REUSE_REMOVAL_NOT_ENOUGH_PATCH_UNITS"
    p_ind=meta["independent_unit_marginal_null"]["one_sided_p"]
    p_cop=meta["comonotone_within_site_marginal_null"]["one_sided_p"]
    positive=(meta["observed_equal_site_weighted_mean_Z"]>0
              and p_ind<.05 and p_cop<.05)
    return {
        **base,
        "status":("POSITIVE_EXPLORATORY_10M_PATCH_RECURRENCE_BEYOND_SAME_TRAP_OVERLAP"
                  if positive else "NO_POSITIVE_10M_PATCH_EFFECT_BEYOND_FIXED_EXACT_TRAP_OVERLAP"),
        "new_observed_patch_recurrence_opened":True,
        "observed":{
            "informative_source_pairs":len(unit_private),
            "positive_pair_Z":positive_units,
            "physical_sites":len(site_mean),
            "positive_site_mean_count":sum(x>0 for x in site_mean),
            "equal_physical_site_mean_Z_neighbor_given_same_station_overlap":mean(site_mean),
            "anonymous_site_mean_patch_Z_sorted":[float(z) for z in sorted(site_mean)],
        },
        "conditional_site_meta_null":meta,
        "site_reused_season_exclusion":{
            "status":clean_status,
            "source_excluded_whole_physical_site_count":len(reused_sites),
            "remaining_informative_pairs":len(clean),
            "remaining_physical_sites":clean_sites,
            "conditional_site_meta_null":clean_cal,
        },
        "inference":{
            "positive_if_both_conditional_scenarios":positive,
            "unit_sampler_is_direct_iid_exact_conditional_uniform_target":True,
            "per_unit_null_moments_analytical_not_mcmc":True,
            "conditioned_original_exact_same_trap_observed_overlap":True,
            "no_diagonal_or_later_radius_selected":True,
            "old_stable_genus_at_exact_trap_not_automatically_proof_of_patch":True,
            "correlated_genus_catchability_at_neighbor_traps_not_excluded":True,
            "persistent_10m_microhabitat_not_separated_from_detection":True,
            "no_true_demographic_turnover_or_home_range_claim":True,
            "no_independent_new_release_or_confirmation":True,
            "site_comonotone_stress_not_proven_joint_dependency_bound":True,
            "no_density_WB_or_air_temperature_effect_fitted":True,
        },
    }


def main()->int:
    try:
        record=run()
        code=0
    except Exception as e:
        record={
            "schema":"neon.macro.exact_two_10m_patch_given_original_same_trap.v1",
            "status":"STOP_SOURCE_CONDITIONAL_UNIFORM_NULL_OR_MODEL_INVARIANT",
            "error_class":type(e).__name__,
            "old_30_site_exact_trap_recurrence_unchanged":True,
            "private_site_taxon_tag_station_source_values_suppressed":True,
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(record,indent=2,sort_keys=True))
    return code


if __name__=="__main__":
    raise SystemExit(main())
