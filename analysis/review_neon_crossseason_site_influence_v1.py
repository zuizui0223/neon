#!/usr/bin/env python3
"""Post-result, explicitly EXPLORATORY independent-site influence diagnostics.

Only previously archived 14 site means are read. No NEON animal record,
trap/genus matrix, new spatial effect, site identifier or post-hoc threshold
selection is involved. The originally preregistered site test is immutable.
"""
from __future__ import annotations

import json
from pathlib import Path
from itertools import product
from math import isfinite
from statistics import mean

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"results/neon_crossseason_genus_template_ecology_receipt_20261019.json"
OUT=ROOT/"build/neon_crossseason_site_influence_exploratory_v1.json"


def exact_site_signflip(values:list[float]) -> dict:
    """One-sided exact sign flip of an arithmetic physical-site mean."""
    if not 1<=len(values)<=18:
        raise ValueError("exact physical-site signflip accepts 1..18 site means")
    if any(not isinstance(x,(int,float)) or isinstance(x,bool)
           or not isfinite(x) for x in values):
        raise ValueError("non-finite site-mean standardised ecological effect")
    n=len(values)
    observed=mean(values)
    total=1<<n
    extreme=0
    # Enumerate sign patterns, no pseudo site identifiers or seasons.
    for mask in range(total):
        signed=sum(v*(1 if mask&(1<<i) else -1)
                   for i,v in enumerate(values))/n
        extreme+=signed>=observed-1e-12
    return {
        "sites_remaining":n,
        "mean_standardized_site_effect":float(observed),
        "one_sided_p":extreme/total,
        "number_site_sign_combinations":total,
        "positive_sites":sum(x>0 for x in values),
    }


def sensitivity_from_site_means(site_values:list[float]) -> dict:
    """All leave-one-out, plus strongest one/three exclusions; exploratory."""
    z=sorted(site_values)
    if len(z)<4 or len(z)>18:
        raise ValueError("review requires 4..18 original physical-site summaries")
    loo=[
        exact_site_signflip(z[:i]+z[i+1:])
        for i in range(len(z))
    ]
    return {
        "all_single_site_omission_count":len(z),
        "smallest_leave_one_site_out_p":min(x["one_sided_p"] for x in loo),
        "largest_leave_one_site_out_p":max(x["one_sided_p"] for x in loo),
        "lowest_leave_one_site_out_mean":min(x["mean_standardized_site_effect"] for x in loo),
        "highest_leave_one_site_out_mean":max(x["mean_standardized_site_effect"] for x in loo),
        "strongest_one_positive_site_removed":exact_site_signflip(z[:-1]),
        "strongest_three_positive_sites_removed":exact_site_signflip(z[:-3]),
        "original_site_Z_ranks_in_anonymized_sorted_order":list(range(1,len(z)+1)),
        "post_result_influence_tests_not_separate_confirmatory_p_values":True,
    }


def review_receipt(original:dict) -> dict:
    primary=original.get("independent_site_ecology",{})
    if original.get("status")!="SUPPORT_MULTI_SITE_GENUS_TEMPLATE_REASSEMBLY":
        raise ValueError("precommitted positive primary source result not present")
    if not primary.get("ecological_site_level_criterion_passed"):
        raise ValueError("precommitted site criterion not present")
    z=primary["site_Z_means_sorted_ascending"]
    if len(z)!=14 or primary["physical_sites"]!=14:
        raise ValueError("expected exactly original 14 geographical sites")
    exact=exact_site_signflip(z)
    if abs(exact["mean_standardized_site_effect"]-primary["site_mean_Z_mean"])>1e-10:
        raise ValueError("precommitted mean Z does not recompute")
    if abs(exact["one_sided_p"]-primary["one_sided_site_signflip_p"])>1e-12:
        raise ValueError("precommitted exact site p does not recompute")
    if exact["positive_sites"]!=primary["positive_site_means"]:
        raise ValueError("precommitted site-sign count does not recompute")
    if original["claim_boundary"]["causal_competition_or_habitat_filtering_proven"] is not False:
        raise ValueError("unsupported causal biology was promoted")
    return {
        "schema":"neon.crossseason_site_influence_exploratory.v1",
        "status":"EXPLORATORY_SITE_INFLUENCE_NOT_NEW_CONFIRMATORY_TEST",
        "source":"results/neon_crossseason_genus_template_ecology_receipt_20261019.json",
        "original_frozen_primary_sites":len(z),
        "original_frozen_primary_mean_Z":primary["site_mean_Z_mean"],
        "original_frozen_primary_positive_sites":primary["positive_site_means"],
        "original_frozen_primary_p":primary["one_sided_site_signflip_p"],
        "original_frozen_primary_sign_combinations":exact["number_site_sign_combinations"],
        "influence_diagnostics":sensitivity_from_site_means(z),
        "interpretation":{
            "null_signflip_conditioning":"The sign-flip p is conditional on the already estimated unit Z scores and assumes appropriate physical-site sign exchangeability",
            "post_result_sensitivity_not_frozen_confirmation":True,
            "no_geographic_or_species_moderator_is_selected":True,
            "mechanism_habitat_filtering_competition_not_identified":True,
            "independent_14_sites_not_58_units":True,
            "positive_original_main_test_unchanged":True,
        },
        "exploratory_not_preregistered":True,
        "new_original_spatial_effects_opened":False,
        "habitat_filtering_mechanism_identified":False,
        "causal_interactions_identified":False,
        "source_geographic_or_individual_IDs_exported":False,
        "original_density_paper_status":"FAILED_5_OF_8",
        "MOSA_WB_status":"SEALED",
    }


def main() -> None:
    j=json.loads(SOURCE.read_text(encoding="utf-8"))
    result=review_receipt(j)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
                   encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
