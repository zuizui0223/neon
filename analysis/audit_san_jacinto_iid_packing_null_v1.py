from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def _load():
    path=ROOT/"analysis"/"finite_iid_packing_null_v1.py"
    spec=importlib.util.spec_from_file_location("iidnull",path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NULL=_load()


def audit() -> dict:
    grid=NULL.canonical_grid_7x7(6.25)
    support=np.asarray([grid[k] for k in sorted(grid)],dtype=float)
    rows=[]
    means=[]
    for n in range(2,31):
        moment=NULL.exact_iid_mpd_null_moments(support,n)
        means.append(moment["mean"])
        rows.append({
            "n":n,
            "mean":moment["mean"],
            "sd":moment["sd"],
            "variance":moment["variance"],
            "kernel_variance":moment["kernel_variance"],
            "shared_pair_covariance":moment["shared_pair_covariance"],
        })

    mean_spread=max(means)-min(means)
    return {
        "schema":"neon.san_jacinto_crossscale.iid_packing_mechanical_audit.v1",
        "geometry":"canonical_7x7_6.25m",
        "support_count":49,
        "null_mode":"exact_iid_uniform_finite_support_with_replacement",
        "n_range":[2,30],
        "null_mean_spread":mean_spread,
        "all_sd_positive":all(row["sd"]>0 for row in rows),
        "expected_standardized_score":0.0,
        "expected_male_minus_female_standardized_score":0.0,
        "rows":rows,
        "passes":mean_spread<1e-12 and all(row["sd"]>0 for row in rows),
        "observed_ecological_effects_inspected":False,
        "ecological_model_fits":0,
    }


def main() -> int:
    out=audit()
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
