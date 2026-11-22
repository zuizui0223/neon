#!/usr/bin/env python3
"""Reproduce published roe deer RESOURCE closure time-state contrasts.

Prior-art positive experimental ecological comparator, NOT new NEON biology.
Original PNAS 2021 author data, pinned Git v1.0 commit and Git blob SHA.
The original cognition/memory model is NOT rerun here, only behavioral state
use before, during, and after food-station access manipulation.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
from datetime import datetime,timezone
from hashlib import sha1,sha256
from io import StringIO
from pathlib import Path
import csv,json,subprocess

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_ranc2021_resource_closure_positive_control_20261122.json"
SRC_COMMIT="58cd85c863d50346df0c7b0d3ecfde97f8a5dfdb"
FILES={
    "Ranc_et_al_2021_PNAS_data_population_ts.txt":
        "18bebe5527828a9ff975d3f35c6b7553d67a3064",
    "Ranc_et_al_2021_PNAS_data_population_tslv.txt":
        "918f5b981b4dc55c71347549d72815cf0b8db497"
}
HEADERS={
    "Ranc_et_al_2021_PNAS_data_population_ts.txt":
        ["exp_id","current_state_code","res_access_m","light_i",
         "light_r","light_abs_r","min_temp"],
    "Ranc_et_al_2021_PNAS_data_population_tslv.txt":
        ["exp_id","tslv_m","tslv_a","access_m","access_a"]
}
PHASES=("before_accessible","closed_inaccessible","reopened_accessible")
STATES=("1","2","3")
INVALID="-9999"
EXPECTED=26841
N_EXPERIMENTS=25
PROTOCOL="docs/NEON_ROE_DEER_RESOURCE_CLOSURE_POSITIVE_CONTROL_FROZEN_20261122.md"

def require(ok,label):
    if not ok:raise ValueError("RANC2021_SOURCE_STOP_"+label)

def source_blob_sha(raw):
    return sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def load_verified(directory):
    raw={}
    for name,want_sha in FILES.items():
        path=directory/name
        data=path.read_bytes()
        require(source_blob_sha(data)==want_sha,"GITHUB_BLOB_SHA_CHANGED_"+name)
        raw[name]=data
    def parse(name):
        try:text=raw[name].decode("utf-8-sig")
        except UnicodeDecodeError:
            raise ValueError("RANC2021_SOURCE_STOP_ORIGINAL_NON_UTF8") from None
        reader=csv.DictReader(StringIO(text))
        require(reader.fieldnames==HEADERS[name],"ORIGINAL_SOURCE_HEADER_DRIFT")
        values=list(reader)
        require(all(None not in row and None not in row.values() for row in values),
                "ORIGINAL_CSV_RAGGED")
        return values
    time=parse("Ranc_et_al_2021_PNAS_data_population_ts.txt")
    init=parse("Ranc_et_al_2021_PNAS_data_population_tslv.txt")
    require(len(time)==EXPECTED,"ORIGINAL_HOURLY_ROW_COUNT_DRIFT")
    require(len(init)==N_EXPERIMENTS,"ORIGINAL_INITIALIZATION_EXPERIMENTS_DRIFT")
    init_ids=[x["exp_id"] for x in init]
    require(len(init_ids)==len(set(init_ids)),"DUPLICATE_INITIALIZATION_IDS")
    return time,init,{
        p:{"git_blob_sha1":FILES[p],
           "original_file_sha256":sha256(raw[p]).hexdigest(),
           "source_file_bytes":len(raw[p])} for p in FILES
    }

def phase_source_report(time,init):
    """Pure function for synthetic tests and original data, no model fitting."""
    original_ids={r["exp_id"] for r in init}
    require(len(original_ids)==len(init),"DUPLICATE_SOURCE_INITIALIZATION_ANIMAL_YEAR")
    grouped=defaultdict(list)
    closed=set()
    last_id=None
    for row in time:
        exp=row["exp_id"]
        require(exp in original_ids,"TIME_SOURCE_EXPERIMENT_NOT_INITIALIZED")
        if exp!=last_id:
            require(exp not in closed,"SOURCE_EXPERIMENT_ROWS_NONCONTIGUOUS")
            if last_id is not None:closed.add(last_id)
            last_id=exp
        state=row["current_state_code"]
        access=row["res_access_m"]
        require(state in (*STATES,INVALID) and access in ("0","1"),
                "UNEXPECTED_STATE_OR_MANIPULATED_ACCESS")
        grouped[exp].append((access,state))
    require(set(grouped)==original_ids,"TIME_INITIALIZATION_SOURCE_ID_MISMATCH")
    totals=defaultdict(Counter)
    animal_phase_fractions=[]
    animal_changes=[]
    missing=Counter()
    for exp,seq in grouped.items():
        phases=[]
        for access,state in seq:
            if not phases or phases[-1]["access"]!=access:
                phases.append({"access":access,"states":Counter()})
            phases[-1]["states"][state]+=1
        require([x["access"] for x in phases]==["1","0","1"],
                "NOT_EXACT_ORIGINAL_1_0_1_MANIPULATION_SEQUENCE")
        row={}
        for pname,part in zip(PHASES,phases):
            nvalid=sum(part["states"][c] for c in STATES)
            nmiss=part["states"][INVALID]
            require(nvalid>=24,"PHASE_VALID_HOURS_BELOW_24_SOURCE_STOP")
            missing[pname]+=nmiss
            totals[pname].update(part["states"])
            row[pname]={
                "m":part["states"]["1"]/nvalid,
                "a":part["states"]["2"]/nvalid,
                "v":part["states"]["3"]/nvalid,
                "valid_hours":nvalid,
                "missing_hours":nmiss,
            }
        animal_phase_fractions.append(row)
        animal_changes.append({
            "closure_minus_before":row[PHASES[1]]["m"]-row[PHASES[0]]["m"],
            "reopen_minus_closure":row[PHASES[2]]["m"]-row[PHASES[1]]["m"],
            "reopen_minus_before":row[PHASES[2]]["m"]-row[PHASES[0]]["m"]
        })
    n=len(animal_phase_fractions)
    require(n>=1,"NO_EXPERIMENT_SERIES")
    def mean(a):return sum(a)/len(a)
    means={
       phase:{
          "animal_year_equal_weighted_fraction_manipulated_M":
             mean([rec[phase]["m"] for rec in animal_phase_fractions]),
          "animal_year_equal_weighted_fraction_alternative_A":
             mean([rec[phase]["a"] for rec in animal_phase_fractions]),
          "animal_year_equal_weighted_fraction_vegetation_V":
             mean([rec[phase]["v"] for rec in animal_phase_fractions]),
          "source_observed_valid_hours":sum(totals[phase][s] for s in STATES),
          "source_missing_state_hours_minus9999":totals[phase][INVALID],
          "pooled_observed_hour_fraction_M_not_independent_sample":
              totals[phase]["1"]/sum(totals[phase][s] for s in STATES)
       } for phase in PHASES
    }
    differences={key:mean([x[key] for x in animal_changes]) for key in
                ("closure_minus_before","reopen_minus_closure","reopen_minus_before")}
    return {
        "source_animal_year_experimental_sequences":n,
        "source_hourly_rows":len(time),
        "source_hourly_missing_recorded_state_rows":sum(missing.values()),
        "three_original_phases_1_access_0_closed_1_reopen_verified_for_all":True,
        "source_three_phase_state_use":means,
        "mean_within_original_animal_year_differences_M_fraction":differences,
        "original_animal_year_count_where_M_declines_during_closure":
            sum(x["closure_minus_before"]<0 for x in animal_changes),
        "original_animal_year_count_where_M_rises_after_reopening":
            sum(x["reopen_minus_closure"]>0 for x in animal_changes),
        "original_individual_ANIMAL_YEAR_not_independent_ANIMAL":True,
        "no_animal_ID_or_original_individual_trajectory_exported":True
    }

def run(data_dir,repo_path=None):
    if repo_path is not None:
        commit=subprocess.check_output(
            ["git","-C",str(repo_path),"rev-parse","HEAD"],text=True).strip()
        require(commit==SRC_COMMIT,"UPSTREAM_ORIGINAL_GIT_COMMIT")
    times,init,source=load_verified(data_dir)
    result=phase_source_report(times,init)
    require(result["source_animal_year_experimental_sequences"]==N_EXPERIMENTS,
            "ORIGINAL_25_SOURCE_TRAJECTORIES")
    return {
        "schema":"neon.ranc2021_original_experimental_resource_closure_state_reproduction.v1",
        "status":"ORIGINAL_PNAS_RESOURCE_MANIPULATION_PRIOR_ART_REPRODUCED_NOT_NEON_MECHANISM",
        "original_published_paper":"Ranc et al. 2021 PNAS 10.1073/pnas.2014856118",
        "original_source_zenodo_doi":"10.5281/zenodo.4609649",
        "original_github_repo":"ranc-n/Ranc-et-al.-PNAS-2021",
        "original_github_git_commit":SRC_COMMIT,
        "original_git_blob_source_checksums":source,
        **result,
        "source_accessibility_manipulated_at_a_food_station_not_natural_resource_biomass":True,
        "state_1_means_at_station_not_successful_eating_when_closed":True,
        "does_not_by_itself_distinguish_memory_from_perception_or_omniscience":True,
        "original_paper_memory_model_and_half_lives_ALREADY_PUBLISHED_NOT_REFITTED":True,
        "not_a_test_of_populations_replacing_individuals_or_competitor_exclusion":True,
        "cannot_meta_pool_roe_deer_state_fraction_and_NEON_genus_trap_Z":True,
        "this_is_method_positive_control_not_NEW_NEON_ecological_discovery":True,
        "NEON_unified_ecological_manuscript_DRAFT_SUBMISSION_HOLD":True,
        "frozen_protocol":PROTOCOL,
        "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--source-dir",type=Path,required=True)
    a.add_argument("--repo-dir",type=Path,required=True)
    a.add_argument("--output",type=Path,default=OUT)
    args=a.parse_args()
    paths={args.source_dir/name for name in FILES}
    p=args.output.resolve()
    require(all(p!=x.resolve() for x in paths),"OUTPUT_MAY_NOT_OVERWRITE_PUBLISHED_INPUT")
    try:
        obj=run(args.source_dir,args.repo_dir)
        exitcode=0
    except Exception as e:
        obj={"schema":"neon.ranc2021_original_experimental_resource_closure_state_reproduction.v1",
             "status":"SOURCE_STOP_ORIGINAL_PINNED_REPRODUCTION",
             "error_type":type(e).__name__,"stop_reason":str(e)[:180],
             "no_new_biological_effect_inferred":True}
        exitcode=3
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(obj,sort_keys=True,indent=2))
    return exitcode

if __name__=="__main__":
    raise SystemExit(main())
