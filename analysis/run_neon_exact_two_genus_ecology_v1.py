#!/usr/bin/env python3
"""First exact-two genus conditional ecological recurrence from NEON RELEASE-2026.

Historical post-result exploratory extension, never independent replication.
FROZEN: exact-two units disjoint from 58 original >=3 genus units; exact
uniform two-row fixed-margin null; no old accepted-only jump chain.
SOURCE-WIDE variance feasibility evaluated BEFORE opening any observed
two-season same-genus station overlap; honest STOP is a valid outcome.

Keep original site, plot, tag, genus and trap identifiers in RAM only.
"""
from __future__ import annotations

from collections import Counter,defaultdict
import json
from pathlib import Path
from statistics import mean

from analysis.run_neon_two_genus_source_v1 import original_sources_for_two_genus
from analysis.neon_exact_two_row_fixedmargin_v1 import (
    two_row_exact_marginal,observed_exact_unit,meta_exact_site_null
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_exact_two_genus_ecological_effect_v1.json"
PRE_EFF=ROOT/"results/neon_exact_two_genus_source_receipt_20261025.json"
DESIGN="docs/NEON_EXACT_TWO_GENUS_MACRO_EXPANSION_20261025.md"
EXACT="docs/NEON_EXACT_TWO_GENUS_EXACT_NULL_ADDENDUM_20261025.md"

SEED=2026102511
DRAWS=20000
MIN_INFORMATIVE_FRACTION=.75
MIN_INFORMATIVE_UNITS=40
MIN_INFORMATIVE_SITES=8


def verify(ok:bool,msg:str)->None:
    if not ok:
        raise RuntimeError("NEON_EXACT_TWO_EFFECT_FROZEN_STOP: "+msg)


def reuse_physical_sites(units:list[dict])->set[str]:
    byperiod=defaultdict(Counter)
    for u in units:
        site=u["site"];plot=tuple(u["site_plot"]);q=u["season_ordinal"]
        for season in (q,q+1):
            byperiod[site][(plot,season)]+=1
    return {site for site,counts in byperiod.items()
            if any(v>1 for v in counts.values())}


def marginal_source_gate(
    units:list[dict],marginals:list[dict],*,min_sites=MIN_INFORMATIVE_SITES,
    min_units=MIN_INFORMATIVE_UNITS,
    min_fraction=MIN_INFORMATIVE_FRACTION
)->dict:
    """Effect-blind: checks only whether exact uniform conditional null moves."""
    verify(len(units)==len(marginals)==158,"158 fixed exact-two source units changed")
    included=[i for i,v in enumerate(marginals) if v["status"]=="EXACT_NONDEGENERATE"]
    eligible_sites={units[i]["site"] for i in included}
    needed_fraction=len(included)/len(units)
    passed=(len(included)>=min_units
            and len(eligible_sites)>=min_sites
            and needed_fraction>=min_fraction)
    source_reused=reuse_physical_sites(units)
    clean=[i for i in included if units[i]["site"] not in source_reused]
    clean_sites={units[i]["site"] for i in clean}
    # Sensitivity was always original-source entire site omission, not
    # outcome selection.
    sens_go=len(clean)>=40 and len(clean_sites)>=8
    return {
        "status":("EXACT_NULL_INFORMATION_GO" if passed
                  else "STOP_EXACT_NULL_TOO_FEW_INFORMATIVE_UNITS"),
        "source_exact_two_pairs":158,
        "null_informative_pairs":len(included),
        "null_zero_variance_pairs":len(units)-len(included),
        "null_informative_fraction":needed_fraction,
        "null_informative_physical_sites":len(eligible_sites),
        "minimum_units":min_units,
        "minimum_sites":min_sites,
        "minimum_informative_fraction":min_fraction,
        "passed":passed,
        "source_reuse_entire_sites_to_exclude":len(source_reused),
        "source_clean_original_pairs":sum(u["site"] not in source_reused for u in units),
        "source_clean_informative_pairs":len(clean),
        "source_clean_informative_physical_sites":len(clean_sites),
        "source_clean_sensitivity_eligible":sens_go,
        "marginal_variance_gate_does_not_compute_observed_recurrence":True,
    }


def source_checked() -> tuple[list[dict],dict,dict]:
    locked=json.loads(PRE_EFF.read_text(encoding="utf-8"))
    verify(locked["status"]=="EXACT_TWO_GENUS_SOURCE_GO_NO_EFFECT_OPENED"
           and locked["precommitted_source_gate"]["passed"],"pre-effect source GO missing")
    verify((locked["exact_two_source"]["pairs"],
            locked["exact_two_source"]["physical_sites"],
            locked["exact_two_source"]["domains"])==(158,30,15),
           "original macro source coverage changed")
    verify((locked["original_strict_primary"]["pairs"],
            locked["original_strict_primary"]["sites"])==(58,14),
           "historical positive 3+ cohort changed")
    strict,exact,source=original_sources_for_two_genus()
    verify(len(strict)==58 and len(exact)==158
           and len({u["site"] for u in exact})==30,
           "original two/three source cohort inconsistent")
    rereuse=reuse_physical_sites(exact)
    verify(len(rereuse)==locked["exact_two_source"]["source_season_reuse_physical_sites"],
           "source-only reused physical sites changed")
    verify(sum(u["site"] not in rereuse for u in exact)==
           locked["exact_two_source"]["source_whole_site_disjoint_sensitivity_pairs"],
           "original source-disjoint seasonal count changed")
    return sorted(exact,key=lambda u:(u["site"],tuple(u["site_plot"]),u["season_ordinal"])),source,locked


def run()->dict:
    units,source,locked=source_checked()
    verify(SEED==2026102511 and DRAWS==20000
           and MIN_INFORMATIVE_FRACTION==.75 and
           MIN_INFORMATIVE_UNITS==40 and MIN_INFORMATIVE_SITES==8,
           "frozen two-row exact null meta inference settings drifted")
    marginal=[two_row_exact_marginal(u["A"],u["B"]) for u in units]
    support=marginal_source_gate(units,marginal)
    source_base={
        "schema":"neon.macro.exactly_two_genus_uniform_recurrence.v1",
        "research_status":"POST_RESULT_2026_EXPLORATORY_SAME_RELEASE_NOT_INDEPENDENT_REPLICATION",
        "source":source,
        "source_support_receipt":"results/neon_exact_two_genus_source_receipt_20261025.json",
        "source_scope":"158 disjoint exact-two comparisons, 30 physical sites and 15 domains",
        "precommitted_design":DESIGN,
        "pre_effect_exact_null_addendum":EXACT,
        "two_row_marginal_exact_not_mcmc":True,
        "variance_source_support":support,
        "original_58_three_genus_effect_not_recomputed":True,
        "original_density_eight_genus_5of8_failure_not_reclassified":True,
        "source_animal_site_plot_genus_station_identifiers_exported":False,
        "site_dependent_conditional_null_not_proven_worst_case":True,
    }
    if not support["passed"]:
        return {**source_base,
                "status":"STOP_EXACT_TWO_GENUS_VARIANCE_SUPPORT",
                "new_exact_two_ecological_overlap_opened":False,
                "site_level_meta_null_computed":False}

    private=[]
    informative_nonzero=0
    positive_units=0
    for u,mar in zip(units,marginal):
        if mar["status"]!="EXACT_NONDEGENERATE":
            continue
        unit=observed_exact_unit(u["A"],u["B"],mar)
        verify(unit["status"]=="EXACT_NONDEGENERATE",
               "valid source marginal gave zero variance on observation")
        private.append({
            "site":u["site"],
            "observed_z":unit["z"],
            "exact_marginal":mar,
        })
        informative_nonzero+=1
        positive_units+=int(unit["z"]>0)
    verify(informative_nonzero==support["null_informative_pairs"],
           "informative eligibility changed during effect opening")

    bysite=defaultdict(list)
    for u in private:bysite[u["site"]].append(u["observed_z"])
    site_means=[mean(z) for site,z in sorted(bysite.items())]
    verify(len(site_means)==support["null_informative_physical_sites"],
           "geographical site grouping changed")
    full=meta_exact_site_null(private,seed=SEED,n_replicates=DRAWS)
    verify(abs(full["observed_equal_site_mean_z"]-mean(site_means))<1e-12,
           "observed equal-site means mismatch")
    source_reused=reuse_physical_sites(units)
    clean=[u for u in private if u["site"] not in source_reused]
    if support["source_clean_sensitivity_eligible"]:
        clean_model=meta_exact_site_null(clean,seed=SEED+200,n_replicates=DRAWS)
        sens_status="SOURCE_DEFINED_WHOLE_SITE_EXCLUSION_COMPUTED"
    else:
        clean_model=None
        sens_status="STOP_SOURCE_DISJOINT_INSUFFICIENT_INFORMATIVE_PAIRS_OR_SITES"
    p_ind=full["independent_unit_exact_marginal_null"]["one_sided_plus_one_p"]
    p_com=full["rank_comonotone_within_site_exact_marginal_stress"]["one_sided_plus_one_p"]
    passed=(full["observed_equal_site_mean_z"]>0 and p_ind<.05 and p_com<.05)
    return {
        **source_base,
        "status":("EXPLORATORY_CONDITIONAL_TWO_GENUS_RECURRENCE_POSITIVE"
                  if passed else "EXPLORATORY_CONDITIONAL_TWO_GENUS_RECURRENCE_NOT_SUPPORTED"),
        "new_exact_two_ecological_overlap_opened":True,
        "observed":{
            "informative_exact_two_genus_pairs":informative_nonzero,
            "positive_unit_Z_count":positive_units,
            "physical_sites":len(site_means),
            "positive_physical_site_mean_count":sum(x>0 for x in site_means),
            "corrected_equal_site_mean_Z":mean(site_means),
            "median_physical_site_mean_Z":sorted(site_means)[len(site_means)//2],
            "site_means_sorted_anonymous":[float(x) for x in sorted(site_means)],
            "standardized_null_is_exact_uniform_fixed_margin_for_two_rows":True,
        },
        "full_exact_two_genus_conditional_meta_null":full,
        "source_disjoint_sensitivity_status":sens_status,
        "source_disjoint_exact_two_genus_conditional_meta_null":clean_model,
        "site_level_meta_null_computed":True,
        "no_pooled_p_or_Z_from_existing_58_three_genus_pairs":True,
        "claim_boundary":{
            "positive_under_both_exploratory_site_couplings":passed,
            "post_result_historical_exploratory_not_confirmatory":True,
            "original_release_same_observational_system":True,
            "conditional_not_a_demographic_turnover_estimator":True,
            "genus_specific_detectability_not_excluded":True,
            "habitat_filtering_cause_not_identified":True,
            "biotic_competition_not_identified":True,
            "site_overlaps_with_original_14_not_independent_replication":True,
            "no_density_W_B_or_climate_biogeographic_effect_fitted":True,
        },
    }


def main()->int:
    try:
        value=run()
        exitcode=0
    except Exception as exc:
        value={
            "schema":"neon.macro.exactly_two_genus_uniform_recurrence.v1",
            "status":"STOP_SOURCE_OR_EXACT_NULL_CODE",
            "error_class":type(exc).__name__,
            "original_58_three_genus_result_unchanged":True,
            "private_source_identifiers_or_traceback_not_exported":True,
        }
        exitcode=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(value,indent=2,sort_keys=True))
    return exitcode

if __name__=="__main__":
    raise SystemExit(main())
