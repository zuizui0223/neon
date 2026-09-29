from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

from scipy.stats import t as student_t


def equal_weight_random_effects(
    effects: list[float],
    standard_errors: list[float],
) -> dict:
    if len(effects)!=len(standard_errors) or len(effects)<2:
        raise ValueError("at least two matched effects and standard errors are required")
    y=[float(x) for x in effects]
    se=[float(x) for x in standard_errors]
    if any(x<0 or not math.isfinite(x) for x in se):
        raise ValueError("standard errors must be finite and nonnegative")

    k=len(y)
    mean=statistics.mean(y)
    between_observed=statistics.variance(y)
    sampling_variances=[x*x for x in se]
    mean_sampling=statistics.mean(sampling_variances)

    # For equal-weight species estimates y_s = theta_s + e_s,
    # E[sample variance(y_s)] = tau^2 + mean(v_s).
    tau2=max(0.0,between_observed-mean_sampling)

    # Equal-weight mean variance:
    # Var(mean y) = tau^2/k + sum(v_s)/k^2.
    variance=tau2/k + sum(sampling_variances)/(k*k)
    family_se=math.sqrt(variance)
    df=k-1
    critical=float(student_t.ppf(0.975,df))
    return {
        "species_count":k,
        "effect":mean,
        "observed_species_variance":between_observed,
        "mean_species_sampling_variance":mean_sampling,
        "tau2_method_of_moments":tau2,
        "standard_error":family_se,
        "df":df,
        "ci95_low":mean-critical*family_se,
        "ci95_high":mean+critical*family_se,
        "method":"equal_weight_species_random_effects_moments_with_within_species_variance",
    }


def family_from_rows(rows: list[dict]) -> dict:
    return equal_weight_random_effects(
        [row["effect"] for row in rows],
        [row["standard_error"] for row in rows],
    )


def audit(packing: dict, recapture: dict) -> dict:
    portal=family_from_rows(packing["primary"]["Portal"]["species"])
    neon=family_from_rows(packing["primary"]["NEON"]["species"])
    movement_primary=family_from_rows(recapture["primary"]["species"])
    movement_n5=family_from_rows(
        recapture["sensitivities"]["n_min_5_per_sex"]["species"]
    )

    return {
        "schema":"neon.public_mammal_sex_packing.family_uncertainty_audit.v1",
        "date":"2026-09-29",
        "purpose":"propagate spatial-unit uncertainty into equal-weight family means without changing frozen primary estimands",
        "packing":{
            "Portal":portal,
            "NEON":neon,
        },
        "recapture":{
            "primary_n3":movement_primary,
            "sensitivity_n5":movement_n5,
        },
        "rulings":{
            "phase3_primary_decision_changes":False,
            "recapture_primary_decision_changes":False,
            "n5_previous_interval_supported":False,
            "n5_point_estimate_sign_concordance_retained":all(
                row["effect"]>0
                for row in recapture["sensitivities"]["n_min_5_per_sex"]["species"]
            ),
            "n5_interpretation":"hypothesis_generating_sign_concordance_only",
        },
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--packing",type=Path,required=True)
    parser.add_argument("--recapture",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()

    out=audit(
        json.loads(args.packing.read_text()),
        json.loads(args.recapture.read_text()),
    )
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
