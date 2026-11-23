from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def interval(sigma_first: float, se_first: float, sigma_last: float, se_last: float, rho: float) -> dict:
    log_ratio = math.log(sigma_last / sigma_first)
    a = se_first / sigma_first
    b = se_last / sigma_last
    se = math.sqrt(a*a + b*b - 2.0*rho*a*b)
    lo = math.exp(log_ratio - 1.96*se)
    hi = math.exp(log_ratio + 1.96*se)
    return {
        "rho": rho,
        "se_log_ratio": se,
        "ratio_lcl95": lo,
        "ratio_ucl95": hi,
        "relative_change_lcl95": lo - 1.0,
        "relative_change_ucl95": hi - 1.0,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pema-json", type=Path, required=True)
    ap.add_argument("--output-json", type=Path, required=True)
    args = ap.parse_args()

    source = json.loads(args.pema_json.read_text(encoding="utf-8"))
    p = source["primary_model"]
    sf, sef = float(p["first"]["sigma_m"]), float(p["first"]["SE"])
    sl, sel = float(p["last"]["sigma_m"]), float(p["last"]["SE"])
    log_ratio = math.log(sl/sf)
    a, b = sef/sf, sel/sl
    rhos = [0.0, 0.25, 0.5, 0.75, 0.9]
    sensitivity = [interval(sf, sef, sl, sel, r) for r in rhos]

    se_max = (log_ratio - math.log(0.9)) / 1.96
    rho_needed = (a*a + b*b - se_max*se_max) / (2.0*a*b)

    out = {
        "schema": "neon.pema_sigma_ratio_uncertainty_sensitivity.v1",
        "status": "post_result_uncertainty_sensitivity_not_formal_paired_ci",
        "source": "results/san_jacinto_pema_scr_sigma_post_stop_result_v1.json",
        "point_estimate": {
            "sigma_first_m": sf,
            "se_first_m": sef,
            "sigma_last_m": sl,
            "se_last_m": sel,
            "ratio_last_first": sl/sf,
            "relative_change": sl/sf - 1.0,
            "log_ratio": log_ratio,
        },
        "method": {
            "description": "First-order delta-method sensitivity for log(sigma_LAST/sigma_FIRST) as a function of the unknown correlation between the paired FIRST and LAST sigma estimates.",
            "se_log_sigma_first": a,
            "se_log_sigma_last": b,
            "formula": "Var(log ratio) ~= SE_F^2/sigma_F^2 + SE_L^2/sigma_L^2 - 2*rho*(SE_F/sigma_F)*(SE_L/sigma_L)",
            "correlation_grid": rhos,
            "z_value": 1.96,
            "contextual_ratio_band": [0.9, 1.1],
        },
        "sensitivity": sensitivity,
        "zero_correlation_reference": interval(sf, sef, sl, sel, 0.0),
        "correlation_required_for_95pct_interval_inside_contextual_band": rho_needed,
        "claim_boundary": {
            "formal_paired_confidence_interval": False,
            "equivalence_test": False,
            "correlation_estimated_from_data": False,
            "interpretation": "The -3.3% point contrast is small, but marginal SEs alone do not establish equivalence. Under a zero-correlation reference the approximate 95% ratio interval is 0.844-1.109. A paired estimate correlation above about 0.721 would be required for this delta-method interval to lie fully inside the contextual 0.9-1.1 band.",
        },
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
