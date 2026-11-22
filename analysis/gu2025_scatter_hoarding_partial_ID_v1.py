#!/usr/bin/env python3
"""Partial identification of recorded scatter-hoarding from existing Gu 2025 receipt.

Retrospective, effect already known and NOT a new independent seed-level or
species-trait finding. The source is 738 Dispersal WORKSHEET ROWS, with three
distinct seed codes represented by two NONIDENTICAL rows each. Missing seed
fate (M) is UNKNOWN, never a biological non-cache outcome.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_INPUT=ROOT/"results/neon_gu2025_seed_fate_archive_20261122.json"
DEFAULT_OUTPUT=ROOT/"build/neon_gu2025_scatter_hoarding_partial_identification_20261122.json"
SPECIES=("Apodemus draco","Niviventer confucianus","Niviventer fulvescens")
FATES=("EAR","EIS","IIS","M","SHI","blank")

def guard(x,msg):
    if not x:
        raise ValueError("SOURCE_STOP_GU2025_"+msg)

def validate_receipt(data):
    guard(data.get("status")=="ARCHIVE_ROW_DESCRIPTION_ONLY","ORIGINAL_RECEIPT_STATUS")
    guard(data.get("manifest",{}).get("doi")=="10.6084/m9.figshare.29815622.v2",
          "ORIGINAL_VERSION_OR_DOI")
    actual={z.get("name"):z for z in data.get("manifest",{}).get("files",[])}
    guard(actual.get("Raw data.xlsx",{}).get("sha256")==
          "9424cc40bab0ad1d498abb91c0a961ff6aa81a1a04946d1515a14b4d6baadfcb",
          "ORIGINAL_EXCEL_SOURCE_SHA")
    guard(data.get("archive_rows")==738 and data.get("distinct_seed_codes")==735
          and data.get("nonidentical_repeated_code_groups")==3,
          "ORIGINAL_ROW_AND_ID_GRANULARITY")
    guard(data.get("pit_column_present",{}).get("Dispersal") is False,
          "UNEXPECTED_SEED_TO_RODENT_PIT")
    types=data.get("rows_by_disperser_class_and_fate",{})
    guard(set(types)=={"species_assigned","literal_not_triggered","blank","other"},
          "ACTOR_CLASS_ONTOLOGY")
    grand=0
    for v in types.values():
        guard(set(v)<=set(FATES) and all(type(n) is int and n>=0 for n in v.values()),
              "ACTOR_FATE_SOURCE_VALUES")
        grand+=sum(v.values())
    guard(grand==738 and
          sum(types["species_assigned"].values())==536 and
          types["species_assigned"].get("M")==157,
          "ORIGINAL_ACTOR_FATE_TOTALS")
    species=data.get("rows_by_assigned_species_and_fate",{})
    guard(set(species)==set(SPECIES),"ORIGINAL_SPECIES_SET_DRIFT")
    sums={z:sum(species[s].get(z,0) for s in species) for z in FATES}
    guard(all(sums.get(z)==types["species_assigned"].get(z,0) for z in FATES),
          "SPECIES_ROWS_DO_NOT_PARTITION_ACTOR_ROWS")
    guard(species["Apodemus draco"]=={"EAR":227,"M":118,"SHI":28}
          and species["Niviventer confucianus"]==
          {"EAR":83,"EIS":21,"M":37,"SHI":18}
          and species["Niviventer fulvescens"]=={"EIS":2,"M":2},
          "ORIGINAL_ACCEPTED_ROW_COUNTS_DRIFT")
    return species

def describe_one(counts):
    n=sum(counts.values())
    missing=counts.get("M",0)
    hoard=counts.get("SHI",0)
    known=n-missing
    guard(n>0 and known>0 and counts.get("blank",0)==0,
          "SPECIES_UNKNOWN_OR_BLANK_DENOMINATOR")
    return {
       "original_species_assigned_row_count":n,
       "original_SHI_record_count":hoard,
       "original_M_unknown_fate_rows":missing,
       "original_rows_with_recorded_known_fate":known,
       "conditional_SHI_fraction_AMONG_KNOWN_fates":float(Fraction(hoard,known)),
       "partial_ID_min_SHI_fraction_if_all_M_NOT_shi":float(Fraction(hoard,n)),
       "partial_ID_max_SHI_fraction_if_all_M_SHI":float(Fraction(hoard+missing,n)),
       "M_unknown_fraction":float(Fraction(missing,n)),
       "fraction_not_inferred_as_plant_recruitment_or_biomass":True,
    }

def compute(data):
    cats=validate_receipt(data)
    results={s:describe_one(cats[s]) for s in SPECIES}
    a=results["Apodemus draco"]
    n=results["Niviventer confucianus"]
    lo=Fraction(18,159)-Fraction(28+118,373)
    hi=Fraction(18+37,159)-Fraction(28,373)
    observed=Fraction(18,159-37)-Fraction(28,373-118)
    # Assume the SAME hypothetical propensity p for otherwise unobserved
    # M rows in both groups, which is a SENSITIVITY, NOT a random-missing
    # data assumption proven by source.
    # 18/159 + p*(37/159) = 28/373 + p*(118/373).
    shared_p=(Fraction(28,373)-Fraction(18,159))/(
        Fraction(37,159)-Fraction(118,373)
    )
    guard(0<shared_p<1,"SENSITIVITY_TIPPING_OUTSIDE_0_1")
    return {
      "schema":"neon.gu2025_scatter_hoarding_partial_ID_from_pinned_source_receipt.v1",
      "status":"RETROSPECTIVE_ARCHIVE_ROW_BOUND_ONLY_NOT_SEED_LEVEL_ECOLOGY",
      "original_published_article_doi":"10.1002/ece3.72409",
      "original_source_doi":"10.6084/m9.figshare.29815622.v2",
      "original_workbook_sha256":"9424cc40bab0ad1d498abb91c0a961ff6aa81a1a04946d1515a14b4d6baadfcb",
      "all_archive_dispersal_rows":738,
      "distinct_seed_codes_NOT_independent_outcome_denominator":735,
      "different_rows_sharing_one_seed_code_groups":3,
      "source_species_row_metrics":results,
      "target_row_estimand":"SHI fraction among assigned disperser SPECIES rows, fate M unknown; NOT probability per unique seed",
      "N_confucianus_minus_A_draco_cache_fraction_among_only_known_fates":float(observed),
      "N_minus_A_cache_fraction_sharp_row_partial_ID_lower":float(lo),
      "N_minus_A_cache_fraction_sharp_row_partial_ID_upper":float(hi),
      "sign_of_unconditional_record_level_species_difference_identified":False,
      "common_hypothetical_missing_M_cache_fraction_tipping_point":float(shared_p),
      "common_hypothetical_missing_M_tipping_exact_fraction":str(shared_p),
      "hypothetical_common_missing_fraction_IS_NOT_assumed_MAR_or_true_biology":True,
      "no_independent_seed_sampling_variance_or_p_value_calculated":True,
      "no_seed_species_or_weight_covariates_or_PIT_individual_effect_fitted":True,
      "published_trait_match_and_pilferage_effects_are_prior_art":True,
      "nonsynonymous_recording_stage_fate_M_not_imputed_zero":True,
      "not_replication_of_NEON_station_recurrence":True,
      "no_interspecific_competition_learning_or_natural_biomass_identified":True,
      "one_NEON_ecology_Draft_SUBMISSION_HOLD":True
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=DEFAULT_INPUT)
    p.add_argument("--output",type=Path,default=DEFAULT_OUTPUT)
    a=p.parse_args()
    source=a.source.resolve();output=a.output.resolve()
    guard(source!=output and not (output.exists() and source.samefile(output)),
          "OUTPUT_ALIASES_SOURCE")
    obj=compute(json.loads(source.read_text(encoding="utf-8")))
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(obj,sort_keys=True,indent=2))

if __name__=="__main__":
    main()
