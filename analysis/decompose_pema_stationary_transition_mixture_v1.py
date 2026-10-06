from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def quantile_type8(values: list[float], p: float) -> float:
    """Match R quantile(type=8), used by the parent stationary-null analysis."""
    if not values:
        raise ValueError("empty quantile input")
    x = sorted(values)
    n = len(x)
    h = (n + 1.0 / 3.0) * p + 1.0 / 3.0
    if h <= 1:
        return x[0]
    if h >= n:
        return x[-1]
    j = math.floor(h)
    gamma = h - j
    return (1.0 - gamma) * x[j - 1] + gamma * x[j]


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stationary-json", type=Path, required=True)
    ap.add_argument("--replicates-csv", type=Path, required=True)
    ap.add_argument("--output-json", type=Path, required=True)
    args = ap.parse_args()

    stationary = json.loads(args.stationary_json.read_text(encoding="utf-8"))
    rows = load_rows(args.replicates_csv)
    observed = stationary["observed"]

    obs_changed = float(observed["changed_fraction"])
    obs_same = 1.0 - obs_changed
    obs_radial_rms = float(observed["radial_rms_m"])
    obs_changed_rms = obs_radial_rms / math.sqrt(obs_changed)

    supported = []
    for cell in stationary["cells"]:
        if int(cell["n_success"]) <= 0:
            continue
        sigma = float(cell["sigma"])
        g0 = float(cell["g0"])
        cell_rows = [
            r for r in rows
            if r["success"] == "TRUE"
            and math.isclose(float(r["sigma"]), sigma, rel_tol=0, abs_tol=1e-12)
            and math.isclose(float(r["g0"]), g0, rel_tol=0, abs_tol=1e-12)
        ]
        if not cell_rows:
            raise RuntimeError(f"missing replicate rows for sigma={sigma}, g0={g0}")

        changed_rms = [
            float(r["radial_rms_m"]) / math.sqrt(float(r["changed_fraction"]))
            for r in cell_rows
        ]
        same = [1.0 - float(r["changed_fraction"]) for r in cell_rows]

        q025 = quantile_type8(changed_rms, 0.025)
        q50 = quantile_type8(changed_rms, 0.5)
        q975 = quantile_type8(changed_rms, 0.975)
        s025 = quantile_type8(same, 0.025)
        s50 = quantile_type8(same, 0.5)
        s975 = quantile_type8(same, 0.975)

        supported.append({
            "sigma": sigma,
            "g0": g0,
            "n": len(cell_rows),
            "observed_changed_rms_m": obs_changed_rms,
            "null_changed_rms_median": q50,
            "null_changed_rms_q025": q025,
            "null_changed_rms_q975": q975,
            "upper_tail_fraction": sum(v >= obs_changed_rms for v in changed_rms) / len(changed_rms),
            "observed_changed_rms_above_q975": obs_changed_rms > q975,
            "observed_same_trap_fraction": obs_same,
            "null_same_trap_median": s50,
            "null_same_trap_q025": s025,
            "null_same_trap_q975": s975,
            "observed_same_trap_above_q975": obs_same > s975,
        })

    primary = next(
        x for x in supported
        if math.isclose(x["sigma"], 8.707, abs_tol=1e-12)
        and math.isclose(x["g0"], 0.15, abs_tol=1e-12)
    )

    out = {
        "schema": "neon.pema_stationary_transition_mixture_decomposition.v1",
        "status": "post_result_algebraic_decomposition_of_frozen_stationary_reference",
        "empirical_scope": stationary["empirical_scope"],
        "identity": "E[R^2] = P(R>0) * E[R^2 | R>0] because same-trap repeat nights have R=0 on the fixed lattice",
        "observed": {
            "changed_fraction": obs_changed,
            "same_trap_fraction": obs_same,
            "radial_rms_m": obs_radial_rms,
            "changed_night_rms_m": obs_changed_rms,
        },
        "primary": {
            "sigma": primary["sigma"],
            "g0": primary["g0"],
            "null_same_trap_median": primary["null_same_trap_median"],
            "null_same_trap_q025": primary["null_same_trap_q025"],
            "null_same_trap_q975": primary["null_same_trap_q975"],
            "null_changed_rms_median": primary["null_changed_rms_median"],
            "null_changed_rms_q025": primary["null_changed_rms_q025"],
            "null_changed_rms_q975": primary["null_changed_rms_q975"],
            "changed_rms_upper_tail_fraction": primary["upper_tail_fraction"],
        },
        "supported_cells": supported,
        "robustness": {
            "supported_cell_count": len(supported),
            "same_trap_above_q975_cells": sum(x["observed_same_trap_above_q975"] for x in supported),
            "changed_rms_above_q975_cells": sum(x["observed_changed_rms_above_q975"] for x in supported),
            "changed_rms_upper_tail_fraction_min": min(x["upper_tail_fraction"] for x in supported),
            "changed_rms_upper_tail_fraction_max": max(x["upper_tail_fraction"] for x in supported),
        },
        "claim_boundary": {
            "causal_mechanism_identified": False,
            "handling_effect_identified": False,
            "preregistered_endpoint": False,
            "interpretation": (
                "The empirical sequence redistributes second-moment mass toward more "
                "zero-displacement repeats and, conditional on changing traps, longer "
                "displacements than the independent-check stationary reference. This is "
                "a post-result decomposition, not a causal movement model."
            ),
        },
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
