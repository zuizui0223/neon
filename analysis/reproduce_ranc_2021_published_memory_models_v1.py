#!/usr/bin/env python3
"""Reproduce original PNAS roe-deer mechanistic model objective scores.

Original public model code, original author fitted parameters, original fixed
time-series and initialization, same pinned Git commit v1.0. No new model fit,
AIC invented parameter count, NEON learning or spatial-niche claim.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime,timezone
from hashlib import sha1,sha256
from io import StringIO
from math import isfinite
from pathlib import Path
import json
import subprocess

from analysis.reproduce_ranc_2021_resource_closure_state_use_v1 import (
    SRC_COMMIT,load_verified,phase_source_report
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_ranc2021_original_memory_model_scores_20261122.json"
PROTOCOL="docs/NEON_ROE_DEER_ORIGINAL_MEMORY_MODEL_REPRO_FROZEN_20261122.md"
MODELS={
    "omniscience":("config_omniscience_best.txt",
                   "5578459a7ee89b4222bce884f377aecc6a0f2b5e","0"),
    "perception":("config_perception_best.txt",
                  "02fe4c97cdae83eb0b32faf1931ba23b97d96c3f","1"),
    "memory":("config_memory_best.txt",
              "f7da45032f81013c17e04bb63c9549cb65da1eab","3")
}
CPP=("Main.cpp","Calculate_attraction.cpp","Calculate_probability.cpp",
     "Likelihood.cpp","Load_config_parameters.cpp","Load_other_inputs.cpp",
     "Load_time_series.cpp","Memory_dynamics.cpp")
PARAMS=("output_directory_path","time_series_path","initialization_data_path")

def require(condition,code):
    if not condition:
        raise ValueError("RANC_ORIGINAL_MODEL_SOURCE_STOP_"+code)

def git_blob(raw):
    return sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def corrected_paths_only(original_text,new_paths,model_type):
    """Change only original path values; preserve original numeric config."""
    rows=original_text.splitlines(keepends=True)
    require(rows and rows[0].strip()=="parameter;value",
            "ORIGINAL_FITTED_CONFIG_HEADER")
    values={}
    revised=[]
    for row in rows[1:]:
        body=row.rstrip("\r\n")
        # The pinned original author configs have TWO terminal blank lines.
        # They are part of the source file, not an extra model parameter.
        # Preserve them exactly without relaxing numeric parameter checks.
        if not body.strip():
            require(not values or "att_decay_rate" in values,
                    "NONTERMINAL_CONFIG_BLANK")
            revised.append((None,None,row))
            continue
        require(";" in body,"FITTED_CONFIG_GRAMMAR")
        k,v=body.split(";",1)
        require(k not in values,"DUPLICATE_ORIGINAL_CONFIG_KEY")
        values[k]=v
        sep=row[len(body):]
        revised.append((k,v,sep))
    require(set(new_paths)==set(PARAMS),"REQUIRED_PATH_ONLY_PATCH")
    require(set(PARAMS).issubset(values) and values.get("model_type")==model_type,
            "ORIGINAL_MODEL_TYPE_OR_PATHS_CHANGED")
    require(len(values)==15,"ORIGINAL_15_CONFIG_PARAMS_CHANGED")
    final=[rows[0]]
    for k,v,sep in revised:
        if k is None:
            final.append(sep)
            continue
        newval=new_paths[k] if k in new_paths else v
        require(isinstance(newval,str) and "\n" not in newval and ";" not in newval,
                "INVALID_NEW_LOCAL_PATH")
        final.append(k+";"+newval+sep)
    patched="".join(final)
    original_nonpaths={k:v for k,v in values.items() if k not in PARAMS}
    new_values={}
    for line in patched.splitlines()[1:]:
        if not line.strip():
            continue  # source's exact terminal blank lines; never a parameter
        k,v=line.split(";",1)
        new_values[k]=v
    require({k:v for k,v in new_values.items() if k not in PARAMS}==original_nonpaths,
            "NUMERIC_OR_MODEL_PARAMETERS_ALTERED")
    require(all(new_values[k]==new_paths[k] for k in PARAMS),
            "LOCAL_SOURCE_PATH_PATCH_FAILED")
    return patched

def compile_original(repository,run_dir):
    source_dir=repository/"Code"
    sources=[source_dir/name for name in CPP]
    require(all(p.exists() and p.is_file() for p in sources),"PINNED_ORIGINAL_CPP_MISSING")
    require((source_dir/"header.h").exists(),"PINNED_ORIGINAL_CPP_HEADER_MISSING")
    program=run_dir/"original_roe_deer_program"
    cmd=["g++","-std=c++11","-O2",*[str(x) for x in sources],"-o",str(program)]
    completed=subprocess.run(cmd,capture_output=True,text=True,timeout=180,check=False)
    require(completed.returncode==0,"PINNED_ORIGINAL_CPP_COMPILE_FAILED")
    require(program.exists() and program.stat().st_size>0,"ORIGINAL_PROGRAM_MISSING")
    return program

def reproduce(repo_dir,workdir):
    try:
        git_head=subprocess.check_output(
            ["git","-C",str(repo_dir),"rev-parse","HEAD"],text=True,timeout=20
        ).strip()
    except (subprocess.CalledProcessError,FileNotFoundError):
        raise ValueError("RANC_ORIGINAL_MODEL_SOURCE_STOP_GIT_HEAD_UNAVAILABLE") from None
    require(git_head==SRC_COMMIT,"ORIGINAL_REPO_COMMIT_NOT_PINNED")
    time,init,source_hashes=load_verified(repo_dir)
    source_counts=phase_source_report(time,init)
    require(source_counts["source_animal_year_experimental_sequences"]==25
            and source_counts["source_hourly_rows"]==26841,
            "ORIGINAL_25_TRAJECTORIES_26841_HOURS_SOURCE_DRIFT")
    workdir.mkdir(parents=True,exist_ok=True)
    program=compile_original(repo_dir,workdir)
    score={}
    configs={}
    for label,(name,blob,typecode) in MODELS.items():
        path=repo_dir/"Configuration_files"/name
        raw=path.read_bytes()
        require(git_blob(raw)==blob,"ORIGINAL_PUBLIC_CONFIG_BLOB_DRIFT_"+label)
        text=raw.decode("utf-8-sig")
        dest=workdir/label
        dest.mkdir(exist_ok=True)
        # C++ author code concatenates output path with filename, requiring '/'.
        new_paths={
            "output_directory_path":str(dest.resolve())+"/",
            "time_series_path":str(
                (repo_dir/"Ranc_et_al_2021_PNAS_data_population_ts.txt").resolve()
            ),
            "initialization_data_path":str(
                (repo_dir/"Ranc_et_al_2021_PNAS_data_population_tslv.txt").resolve()
            )
        }
        copied=corrected_paths_only(text,new_paths,typecode)
        config_path=dest/"local_original_fitted_config.txt"
        config_path.write_text(copied,encoding="utf-8")
        result=subprocess.run([str(program),"-config",str(config_path)],
                              capture_output=True,text=True,timeout=240,check=False)
        require(result.returncode==0,"ORIGINAL_FITTED_MODEL_RUNTIME_"+label)
        objective_path=dest/"objective_function.csv"
        require(objective_path.exists(),"ORIGINAL_OBJECTIVE_FILE_NOT_WRITTEN_"+label)
        objective_lines=objective_path.read_text().strip().splitlines()
        require(len(objective_lines)==1,"ORIGINAL_OBJECTIVE_MORE_THAN_ONE_LINE_"+label)
        try:objective=float(objective_lines[0])
        except ValueError:
            raise ValueError("RANC_ORIGINAL_MODEL_SOURCE_STOP_NONNUMERIC_OBJECTIVE_"+label) from None
        require(isfinite(objective),"ORIGINAL_FITTED_OBJECTIVE_NONFINITE_"+label)
        probabilities=dest/"state_probabilities.csv"
        require(probabilities.exists(),"ORIGINAL_AUTHOR_PROBABILITY_FILE_MISSING_"+label)
        with probabilities.open(encoding="utf-8") as handle:
            original_header=handle.readline().strip()
            nrow=sum(1 for _ in handle)
        require(original_header=="exp_id;current_state;prob_M;prob_A;prob_V"
                and nrow==26841,"ORIGINAL_AUTHOR_PROBABILITY_SOURCE_SHAPE_CHANGED_"+label)
        score[label]=objective
        configs[label]={
            "original_public_config":name,
            "original_Git_blob_SHA1":blob,
            "original_config_raw_SHA256":sha256(raw).hexdigest(),
            "original_model_type":typecode,
            "original_fitted_parameter_values_unchanged":True,
            "output_source_state_probability_rows_checked":nrow,
            "no_original_output_probabilities_published":True,
        }
    return {
        "schema":"neon.ranc2021_original_published_memory_perception_omniscience_loglikelihood.v1",
        "status":"ORIGINAL_PUBLISHED_PNAS_MODEL_OBJECTIVES_REPRODUCED_PRIOR_ART",
        "original_public_Git_commit":SRC_COMMIT,
        "original_PNAS_DOI":"10.1073/pnas.2014856118",
        "original_Zenodo_DOI":"10.5281/zenodo.4609649",
        "original_25_animal_years_and_26841_hourly_states_verified":True,
        "original_source_time_data_git_sha1":source_hashes,
        "original_three_published_best_model_fit_configs":configs,
        "original_published_fitted_objectives_by_model":score,
        "difference_in_original_log_likelihood_memory_minus_perception":
            score["memory"]-score["perception"],
        "difference_in_original_log_likelihood_memory_minus_omniscience":
            score["memory"]-score["omniscience"],
        "higher_original_fitted_objective_value_is_better_within_same_input":True,
        "no_new_optimization_AIC_BIC_or_independent_holdout_scoring":True,
        "model_parameter_counts_and_cognitive_half_lives_NOT_reestimated":True,
        "model_score_ranking_is_prior_published_in_PNAS_not_new_NEON_discovery":True,
        "source_individual_year_ids_and_state_probabilities_NOT_exported":True,
        "original_cpp_compiled_and_executed_from_pinned_public_code":True,
        "not_a_resource_competition_learning_model_fit_to_NEON_small_mammals":True,
        "NEON_unified_Draft_SUBMISSION_HOLD":True,
        "frozen_protocol":PROTOCOL,
        "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-dir",type=Path,required=True)
    p.add_argument("--work-dir",type=Path,default=ROOT/"build/original_pnas_model_tmp")
    p.add_argument("--output",type=Path,default=OUT)
    args=p.parse_args()
    try:
        result=reproduce(args.repo_dir,args.work_dir)
        exitcode=0
    except Exception as e:
        result={
            "schema":"neon.ranc2021_original_published_memory_perception_omniscience_loglikelihood.v1",
            "status":"ORIGINAL_SOURCE_CPP_OR_MODEL_OBJECTIVE_STOP",
            "error_type":type(e).__name__,
            "reason":str(e)[:180],
            "no_unsupported_NEON_learning_or_memory_effect_estimated":True
        }
        exitcode=3
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,sort_keys=True,indent=2))
    return exitcode

if __name__=="__main__":
    raise SystemExit(main())
