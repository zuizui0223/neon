#!/usr/bin/env python3
"""Post-result but source-defined geographic disjointness sensitivity for NEON.

Compares only EXACTLY-two-genus seasonal pairs at physical sites absent
from the original fourteen 3+ genus positive study. Both are same historical
RELEASE-2026 and not prospectively independent; no taxon/habitat selection
or genotype/detection inference is authorized.

Source and exact null variance gate BEFORE opening new-site observed overlap.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from statistics import mean,median
from pathlib import Path
import json

from analysis.run_neon_two_genus_source_v1 import original_sources_for_two_genus
from analysis.run_multiscale_density_estimability_release2026_v3 import _request_json
from analysis.neon_macro_site_selection_v1 import site_metadata_index
from analysis.neon_exact_two_row_fixedmargin_v1 import (
    two_row_exact_marginal,observed_exact_unit,meta_exact_site_null,
)
from analysis.run_neon_exact_two_genus_ecology_v1 import reuse_physical_sites

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_exact_two_new_site_geographic_sensitivity_v1.json"
FROZEN=ROOT/"results/neon_exact_two_genus_source_receipt_20261025.json"
META="https://data.neonscience.org/api/v0/sites?release=RELEASE-2026"
SEED=2026102555
DRAWS=20000


def need(ok:bool,reason:str):
    if not ok:raise RuntimeError("SOURCE_GEOGRAPHIC_NONOVERLAP_STOP: "+reason)


def split_geographically(strict:list[dict],two:list[dict])->dict:
    old_sites={u["site"] for u in strict}
    new_sites={u["site"] for u in two}-old_sites
    included=[u for u in two if u["site"] in new_sites]
    excluded=[u for u in two if u["site"] in old_sites]
    need(len(old_sites)==14 and len({u["site"] for u in two})==30
         and len(new_sites)==17,
         "old 14 and exactly-two new 17 geographical source sites changed")
    need(len(included)+len(excluded)==158 and
         not ({u["site"] for u in included}&old_sites),
         "source-only new physical sites overlap original positive cohort")
    return {"new_source_units":included,"new_sites":new_sites,
            "old_sites":old_sites,
            "source_pairs_covered":len(included),
            "source_pairs_excluded_at_old_sites":len(excluded),
            "original_58_three_plus_site_count":len(old_sites),
            "exact_two_new_site_count":len(new_sites)}


def variance_gate(units:list[dict],marginal:list[dict])->dict:
    """No observed cross-season genus trap overlap evaluated."""
    need(len(units)==len(marginal),"source/marginal length changed")
    sites={u["site"] for u in units}
    kept=[i for i,v in enumerate(marginal) if v["status"]=="EXACT_NONDEGENERATE"]
    informative_sites={units[i]["site"] for i in kept}
    frac=len(kept)/len(units) if units else 0.0
    enough=(len(units)>=20 and len(sites)>=8
            and len(kept)>=20 and len(informative_sites)>=8
            and frac>=.75)
    return {
        "status":"NEW_SITE_SOURCE_AND_NULL_VARIANCE_GO" if enough else "STOP_GEOGRAPHICAL_SOURCE_OR_EXACT_NULL_SUPPORT",
        "source_pair_count":len(units),
        "source_physical_site_count":len(sites),
        "exact_null_informative_pairs":len(kept),
        "exact_null_zero_variance_pairs":len(units)-len(kept),
        "informative_fraction":frac,
        "informative_physical_site_count":len(informative_sites),
        "minimum_original_new_site_pairs":20,
        "minimum_original_new_sites":8,
        "minimum_informative_pairs":20,
        "minimum_informative_sites":8,
        "minimum_informative_fraction":.75,
        "passed":enough,
        "no_observed_pair_overlap_yet_computed":True,
    }


def run()->dict:
    source_pre=json.loads(FROZEN.read_text(encoding="utf-8"))
    need(source_pre["status"]=="EXACT_TWO_GENUS_SOURCE_GO_NO_EFFECT_OPENED",
         "original source-approved two-genus cohort missing")
    strict,two,provenance=original_sources_for_two_genus()
    source=split_geographically(strict,two)
    units=sorted(source["new_source_units"],key=lambda u:(u["site"],tuple(u["site_plot"]),u["season_ordinal"]))
    raw=_request_json(META)
    documented=raw.get("data")
    need(isinstance(documented,list),"official site/domain source unavailable")
    relevant=source["new_sites"]|source["old_sites"]
    meta=site_metadata_index([r for r in documented if r.get("siteCode") in relevant])
    need(all(s in meta for s in relevant),"old/new source site metadata incomplete")
    original_domains={meta[x]["domain"] for x in source["old_sites"]}
    new_domains={meta[x]["domain"] for x in source["new_sites"]}

    marginal=[two_row_exact_marginal(u["A"],u["B"]) for u in units]
    gate=variance_gate(units,marginal)
    base={
        "schema":"neon.exact_two.original14_vs_new17_site_source_sensitivity.v1",
        "research_status":"AFTER_FULL_30_SITE_RESULT_POST_RESULT_SAME_RELEASE_SENSITIVITY",
        "source":{
            **provenance,
            "source_exact_two_pairs":158,
            "source_strict_original_three_plus_pairs":58,
            "new_site_exact_two_pairs":source["source_pairs_covered"],
            "exact_two_pairs_from_overlapping_original14_sites":source["source_pairs_excluded_at_old_sites"],
            "original_three_plus_physical_sites":14,
            "geographically_new_exact_two_physical_sites":len(source["new_sites"]),
            "new_site_ecological_domains":len(new_domains),
            "new_ecological_domains_not_in_original_strict14":len(new_domains-original_domains),
            "NEON_metadata_from_release_sites_endpoint":True,
            "geographical_source_selection_does_not_use_original_Z":True,
        },
        "feasibility":gate,
        "method":{
            "exact_hypergeometric_unit_fixed_margin_null":True,
            "site_equal_weight":True,
            "meta_null_replicates_per_dependency_scenario":DRAWS,
            "meta_seed":SEED,
            "comonotone_null_not_all_dependency_bound":True,
            "pre_effect_design":"docs/NEON_EXACT_TWO_NEW_SITES_GEOGRAPHIC_SENSITIVITY_20261025.md",
        },
        "original_three_plus_effect_unchanged":True,
        "original_eight_genus_density_5of8_fail_preserved":True,
        "no_source_site_genus_animal_or_station_identifiers_exported":True,
        "not_independent_release_or_preregistration":True,
    }
    if not gate["passed"]:
        return {**base,
                "status":"STOP_NEW_SITE_GEOGRAPHIC_OR_EXACT_NULL_SUPPORT",
                "new_site_observed_recurrence_effect_opened":False}

    private=[]
    for u,m in zip(units,marginal):
        if m["status"]!="EXACT_NONDEGENERATE":
            continue
        z=observed_exact_unit(u["A"],u["B"],m)
        need(z["z"] is not None,"positive exact-null variance produced missing unit Z")
        private.append({"site":u["site"],"observed_z":z["z"],"exact_marginal":m})
    need(len(private)==gate["exact_null_informative_pairs"],
         "original marginal gate membership changed after effects")
    bysite=defaultdict(list)
    for item in private:bysite[item["site"]].append(item["observed_z"])
    site_means=sorted(mean(vals) for vals in bysite.values())
    meta_result=meta_exact_site_null(private,seed=SEED,n_replicates=DRAWS)
    need(meta_result["sites"]==gate["informative_physical_site_count"],
         "source geographical site-cluster count changed")
    reuse=reuse_physical_sites(two)
    # Source defined over FULL exact-two cohort, independent of observed
    # new site Z or original site-group direction.
    clean=[row for row in private if row["site"] not in reuse]
    clean_sites=len({u["site"] for u in clean})
    if len(clean)>=20 and clean_sites>=8:
        cleaner=meta_exact_site_null(clean,seed=SEED+200,n_replicates=DRAWS)
        sens_status="WHOLE_SITE_SOURCE_REUSE_EXCLUSION_COMPUTED"
    else:
        cleaner=None
        sens_status="STOP_WHOLE_SITE_SOURCE_DISJOINT_SUBCOHORT_UNDERPOWERED"
    nullind=meta_result["independent_unit_exact_marginal_null"]["one_sided_plus_one_p"]
    nullcoupled=meta_result["rank_comonotone_within_site_exact_marginal_stress"]["one_sided_plus_one_p"]
    positive=(meta_result["observed_equal_site_mean_z"]>0 and nullind<.05 and nullcoupled<.05)
    return {
        **base,
        "status":("NEW_PHYSICAL_SITES_POSITIVE_CONDITIONAL_EXPLORATORY_SENSITIVITY"
                  if positive else "NEW_PHYSICAL_SITES_NO_CONDITIONAL_EXPLORATORY_POSITIVE_SUPPORT"),
        "new_site_observed_recurrence_effect_opened":True,
        "observed_geographically_nonoverlap_sites":{
            "informative_exact_two_pairs":len(private),
            "physical_sites":len(bysite),
            "positive_site_mean_count":sum(x>0 for x in site_means),
            "equal_site_mean_z":meta_result["observed_equal_site_mean_z"],
            "site_median_z":median(site_means),
            "source_distinct_anonymous_site_mean_z_sorted":site_means,
        },
        "conditional_new_site_meta_null":meta_result,
        "whole_site_source_reuse_exclusion":{
            "status":sens_status,
            "source_new_site_excluded_due_to_reuse_count":len(source["new_sites"]&reuse),
            "remaining_informative_pairs":len(clean),
            "remaining_physical_sites":clean_sites,
            "conditional_meta_null":cleaner,
        },
        "scientific_inference":{
            "positive_under_both_conditional_site_null_scenarios":positive,
            "post_result_geographic_sensitivity_not_predeclared_independent_replication":True,
            "old_and_new_sites_physically_disjoint":True,
            "new_17_sites_same_2026_release_capture_process":True,
            "not_true_demographic_replacement":True,
            "not_genus_detection_calibrated":True,
            "not_habitat_or_competition_mechanism":True,
            "not_joint_density_W_B_effect":True,
        },
    }


def main()->int:
    try:
        result=run()
        code=0
    except Exception as exc:
        result={
            "schema":"neon.exact_two.original14_vs_new17_site_source_sensitivity.v1",
            "status":"STOP_GEOGRAPHIC_SOURCE_OR_MODEL_ERROR",
            "error_class":type(exc).__name__,
            "old_14_site_effect_unchanged":True,
            "new_geographic_effect_unavailable":True,
            "private_identifiers_not_exported":True,
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return code

if __name__=="__main__":
    raise SystemExit(main())
