#!/usr/bin/env python3
"""Descriptive effective-domain loss in NEON mammal eligibility selection.

This is *sampling representativeness*, not a new rodent habitat-selection
or ecological recurrence effect. No binomial/chi-square p-value is claimed:
803 season pairs belong to repeated plots and physical sites, not
independent observations.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/"results/neon_macro_biogeographic_selection_receipt_20261025.json"
OUT=ROOT/"results/neon_macro_eligibility_concentration_20261025.json"


def diversity(values: list[int])->dict:
    if not values or any(not isinstance(v,int) or v<0 for v in values):
        raise ValueError("Invalid original source count vector")
    total=sum(values)
    if total<=0:raise ValueError("Source counts contain no positive values")
    proportions=[v/total for v in values if v>0]
    H=-sum(p*math.log(p) for p in proportions)
    return {
        "sample_pairs":total,
        "domains_with_positive_pairs":len(proportions),
        "shannon_entropy_nats":H,
        "effective_shannon_domains":math.exp(H),
        "inverse_simpson_effective_domains":1/sum(p*p for p in proportions),
        "largest_single_domain_fraction":max(proportions),
        "weights_are_nested_pairs_not_independent_sites":True,
    }


def run(data:dict)->dict:
    if data.get("status")!="SOURCE_ONLY_MACRO_SELECTION_RECONSTRUCTED":
        raise ValueError("Original source selection census not verified")
    domains=data["domain_grouped_source_only"]
    original=data["original_source_denominators"]
    candidate=[x["source_adjacent_season_candidate_pairs"] for x in domains.values()]
    strict=[x["primary_eligible_pairs"] for x in domains.values()]
    cc=diversity(candidate)
    qq=diversity(strict)
    if (cc["sample_pairs"],qq["sample_pairs"],
        cc["domains_with_positive_pairs"],qq["domains_with_positive_pairs"]) != (803,58,18,10):
        raise ValueError("Original cross-domain NEON source denominator drifted")
    if original["physical_sites_with_one_or_more_candidate_pairs"]!=42:
        raise ValueError("Original physical site coverage changed")
    return {
        "schema":"neon.unified_macro.source_eligibility_domain_concentration.v1",
        "record_date":"2026-10-25",
        "status":"SOURCE_ONLY_GEOGRAPHIC_REPRESENTATIVENESS_DESCRIBED",
        "source":"results/neon_macro_biogeographic_selection_receipt_20261025.json",
        "all_candidate_pairs":cc,
        "strict_eligible_pairs":qq,
        "eligible_fraction_of_original_candidate_pairs":qq["sample_pairs"]/cc["sample_pairs"],
        "strict_to_candidate_effective_shannon_domain_ratio":qq["effective_shannon_domains"]/cc["effective_shannon_domains"],
        "effective_shannon_domain_loss":cc["effective_shannon_domains"]-qq["effective_shannon_domains"],
        "scientific_scope":{
            "original_source_response_sampling_only":True,
            "number_of_physical_sites_with_candidate_seasons":42,
            "number_of_physical_sites_with_strict_pairs":14,
            "no_ecological_recurrence_effect_for_nonqualified_sites":True,
            "no_random_sample_assumption_for_pairs":True,
            "descriptive_no_clustered_p_value":True,
            "no_biological_competition_habitat_or_climate_effect":True,
            "interpretation":"effective number of source domains represented by weighted pair counts, not number of independent biological ecosystems or taxon-level ecological persistence",
        },
    }


def main()->None:
    source=json.loads(INPUT.read_text(encoding="utf-8"))
    result=run(source)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],
                      "candidate_effective_domains":result["all_candidate_pairs"]["effective_shannon_domains"],
                      "strict_effective_domains":result["strict_eligible_pairs"]["effective_shannon_domains"],
                      "ratio":result["strict_to_candidate_effective_shannon_domain_ratio"],
                      "no_effect_fitted":True},indent=2))

if __name__=="__main__":
    main()
