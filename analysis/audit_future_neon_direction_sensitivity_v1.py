#!/usr/bin/env python3
"""Post-result direction audit of frozen future provisional W/B contrast.

Uses ONLY two previously acquired independent prospectively frozen derived
artifacts. Does NOT change the original model or response-inclusion rules,
and does NOT rescue failure by species/habitat filtering.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from analysis.run_future_neon_provisional_holdout_v1 import (
    join_sealed_rows, temporal_series_subset, fit_mode_genus,
)
from analysis.audit_peromyscus_site_uncertainty_v1 import site_sandwich
from analysis.multiscale_density_fixed_effects_v1 import fit_slope

OUT=Path("build/future_neon_direction_sensitivity_v1.json")
EXPECTED={
    "Peromyscus":{
        "W_m2":-2.246436271749609,
        "B_debiased_m2":-9.319401210900125,
        "D_m2":-7.072964939150511,
    },
    "Dipodomys":{
        "W_m2":-19.096116831750734,
        "B_debiased_m2":8.097757909021789,
        "D_m2":27.19387474077252,
    }
}


def run(metrics, predictors, qc):
    a=join_sealed_rows(metrics,predictors,qc)
    x=temporal_series_subset(a)
    genera={}
    for genus in EXPECTED:
        part=[r for r in x if r["genus"]==genus]
        base=fit_mode_genus(x,genus)
        if base["status"]!="PROVISIONAL_HELDOUT_DIRECTIONAL":
            raise RuntimeError("previously opened direction source became inestimable")
        for name,want in EXPECTED[genus].items():
            beta=base["estimates"][name]["beta_MNKA"]
            if abs(beta-want)>1e-8:
                raise RuntimeError(f"{genus} {name} prospective point-slope drift")
        loo={}
        sites=sorted({r["site"] for r in part})
        for site in sites:
            kept=[r for r in part if r["site"]!=site]
            # Same fixed model, not a new subset hypothesis.
            try:
                f=fit_slope(kept,response="D_m2",
                    nuisance=("series_id","site_month","year"),
                    genus_balanced=False)
                loo[site]=f.beta
            except ValueError:
                loo[site]=None
        slopes=[v for v in loo.values() if v is not None]
        genus_out={
            "n":len(part),"sites":len(sites),
            "D_original_heldout_beta":base["estimates"]["D_m2"]["beta_MNKA"],
            "direction_prediction":">0" if genus=="Peromyscus" else "<0",
            "direction_replication_supported":(
                base["estimates"]["D_m2"]["beta_MNKA"]>0
                if genus=="Peromyscus"
                else base["estimates"]["D_m2"]["beta_MNKA"]<0),
            "post_result_leave_one_site_out":{
                "successful_omissions":len(slopes),
                "sites":len(sites),
                "min_beta_D":min(slopes) if slopes else None,
                "max_beta_D":max(slopes) if slopes else None,
                "positive_count":sum(v>0 for v in slopes),
                "negative_count":sum(v<0 for v in slopes),
            },
        }
        if len(part)>=80 and len(sites)>=10:
            genus_out["post_result_site_cluster_uncertainty"]={
                response:site_sandwich(part,response)
                for response in ("W_m2","B_debiased_m2","D_m2")
            }
            genus_out["post_result_m_adjusted_D"]=site_sandwich(
                part,"D_m2",("m",))
            genus_out["post_result_m_and_B_observed_adjusted_D"]=site_sandwich(
                part,"D_m2",("m","B_observed_m2"))
        else:
            genus_out["site_cluster_uncertainty_status"]="NOT_RELIABLY_ESTIMABLE_WITH_FEW_SITES"
        genera[genus]=genus_out
    return {
        "schema":"neon.future_neon_direction_sensitivity.v1",
        "status":"PROVISIONAL_POST_RESULT_SENSITIVITY_ONLY",
        "source_future_holdout_run":38046615310,
        "raw_new_metric_sessions":len(a),
        "fixed_timevarying_sessions":len(x),
        "original_five_genus_future_mode_test":"NOT_ESTIMABLE_ALL_FIVE_FROZEN_GENERA",
        "genera":genera,
        "no_new_model_or_genus_selection":True,
        "new_provisional_data_are_not_finalized_official_release":True,
        "original_development_6_of_8_general_guard":"FAILED_UNCHANGED",
        "biological_claim_boundary":"Direction failure in prospective new observations, not a causal demonstration of a temporal regime shift; site omissions and m controls are descriptive AFTER outcomes."
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--metric",type=Path,required=True)
    p.add_argument("--mnka",type=Path,required=True)
    p.add_argument("--qc",type=Path,required=True)
    opt=p.parse_args()
    try:
        v=run(json.loads(opt.metric.read_text()),
              json.loads(opt.mnka.read_text()),
              json.loads(opt.qc.read_text()))
    except (RuntimeError,ValueError) as e:
        v={"schema":"neon.future_neon_direction_sensitivity.v1",
           "status":"STOP_SOURCE_OR_DIRECTION_REPRODUCIBILITY",
           "error":str(e),"original_guards_unchanged":True}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
    print(json.dumps(v,indent=2,sort_keys=True))
    if v["status"]!="PROVISIONAL_POST_RESULT_SENSITIVITY_ONLY":
        raise SystemExit(3)
