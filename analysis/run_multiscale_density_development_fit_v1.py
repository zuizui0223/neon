#!/usr/bin/env python3
"""First frozen ecological development fit for multiscale density accommodation.

This is the first place where W/B metrics are joined to genus-level MNKA.
RELEASE-2026 remains development data; no result from this runner is
confirmatory.

To avoid duplicated scientific logic, the runner calls the already validated
metric-QC and MNKA-support pipelines, joins their session-level outputs, applies
the frozen joint model contract, and evaluates the predeclared generality guard.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from analysis.audit_multiscale_density_mnka_variation_v1 import run as run_mnka
from analysis.multiscale_density_fixed_effects_v1 import evaluate_frozen_model
from analysis.run_multiscale_density_metric_qc_v1 import run as run_metric_qc

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "results" / "multiscale_density_joint_model_contract_v1.json"
OUT = ROOT / "build" / "multiscale_density_development_fit_v1.json"

FROZEN_GENERA = [
    "Chaetodipus",
    "Dipodomys",
    "Microtus",
    "Myodes",
    "Napaeozapus",
    "Onychomys",
    "Peromyscus",
    "Sigmodon",
]


def _date_parts(value: str) -> tuple[str, str]:
    text = str(value or "").strip()
    try:
        d = date.fromisoformat(text[:10])
    except ValueError as exc:
        raise ValueError(f"invalid or missing event date: {value!r}") from exc
    return str(d.year), f"{d.month:02d}"


def _key(row: dict) -> tuple[str, str, str, str]:
    return (
        str(row["taxon"]),
        str(row["site"]),
        str(row["plot_id"]),
        str(row["event_id"]),
    )


def _eligible_series(rows: list[dict]) -> set[str]:
    by_series: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_series[row["series_id"]].append(row)
    eligible = set()
    for series_id, vals in by_series.items():
        if len(vals) < 3:
            continue
        if len({int(v["mnka"]) for v in vals}) < 2:
            continue
        eligible.add(series_id)
    return eligible


def run() -> dict:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract["state"] != "FROZEN_BEFORE_FIRST_W_B_X_MNKA_JOIN":
        raise RuntimeError("joint model contract is not in the expected frozen state")

    metric = run_metric_qc()
    if not metric["decision"]["metric_qc_passed"]:
        raise RuntimeError("metric QC did not pass")

    mnka = run_mnka()
    paired = mnka.get("paired_sessions")
    if not isinstance(paired, list):
        raise RuntimeError("MNKA runner did not return paired_sessions")

    metric_by_key = {_key(row): row for row in metric["sessions"]}
    if len(metric_by_key) != len(metric["sessions"]):
        raise RuntimeError("duplicate metric session key")
    mnka_by_key = {_key(row): row for row in paired}
    if len(mnka_by_key) != len(paired):
        raise RuntimeError("duplicate MNKA session key")

    joined = []
    metric_without_mnka = []
    for key, m in metric_by_key.items():
        n = mnka_by_key.get(key)
        if n is None:
            metric_without_mnka.append(key)
            continue
        year, month = _date_parts(n.get("event_date", ""))
        genus = str(m["genus"])
        if genus != str(n["genus"]):
            raise RuntimeError(f"genus mismatch for {key}: {genus} vs {n['genus']}")
        row = {
            "taxon": str(m["taxon"]),
            "genus": genus,
            "site": str(m["site"]),
            "plot_id": str(m["plot_id"]),
            "event_id": str(m["event_id"]),
            "event_date": str(n["event_date"]),
            "year": year,
            "month": month,
            "site_month": f"{m['site']}|{month}",
            "series_id": f"{m['taxon']}|{m['site']}|{m['plot_id']}",
            "mnka": int(n["mnka"]),
            "unique_tagged_individuals": int(n["unique_tagged_individuals"]),
            "coordinate_supported_individuals": int(
                n["coordinate_supported_individuals"]
            ),
            "repeat_supported_individuals_structural": int(
                n["repeat_supported_individuals"]
            ),
            "repeat_supported_fraction": float(
                n["repeat_supported_fraction"]
            ),
            "all_capture_trap_night_fraction": float(
                n["all_capture_trap_night_fraction"]
            ),
            "W_m2": float(m["W_m2"]),
            "B_observed_m2": float(m["B_observed_m2"]),
            "B_debiased_m2": float(m["B_debiased_m2"]),
            "D_m2": float(m["B_debiased_m2"]) - float(m["W_m2"]),
            "n_individuals": int(m["n_individuals"]),
        }
        joined.append(row)

    if metric_without_mnka:
        raise RuntimeError(
            f"{len(metric_without_mnka)} metric sessions lack frozen MNKA pairing"
        )

    frozen = [row for row in joined if row["genus"] in set(FROZEN_GENERA)]
    eligible_series = _eligible_series(frozen)
    analysis_rows = [row for row in frozen if row["series_id"] in eligible_series]

    if not analysis_rows:
        raise RuntimeError("no analysis rows after frozen series rule")
    if set(FROZEN_GENERA) - {row["genus"] for row in analysis_rows}:
        missing = sorted(set(FROZEN_GENERA) - {row["genus"] for row in analysis_rows})
        raise RuntimeError(f"frozen genera missing from final analysis rows: {missing}")

    model = evaluate_frozen_model(
        analysis_rows,
        frozen_genera=FROZEN_GENERA,
    )

    # Linear identity must hold exactly up to floating error under an identical
    # design matrix and weights.
    identity_error = abs(
        float(model["primary_delta"]["beta"])
        - float(model["secondary_slopes"]["difference_identity_check"])
    )
    if identity_error > 1e-8:
        raise RuntimeError(f"delta identity mismatch: {identity_error}")

    by_genus = Counter(row["genus"] for row in analysis_rows)
    by_taxon = Counter(row["taxon"] for row in analysis_rows)
    by_site = Counter(row["site"] for row in analysis_rows)

    primary_beta = float(model["primary_delta"]["beta"])
    beta_w = float(model["secondary_slopes"]["beta_W"])
    beta_b = float(model["secondary_slopes"]["beta_B_debiased"])
    if model["decision"]["development_cross_scale_support"]:
        ecological_class = (
            "PACKING_STRONG_FORM"
            if model["decision"]["strong_form_supported"]
            else "CROSS_SCALE_ACCOMMODATION_WITHOUT_STRONG_SIGN_FORM"
        )
    elif primary_beta <= 0:
        ecological_class = "NO_CROSS_SCALE_ACCOMMODATION"
    else:
        ecological_class = "POSITIVE_POOLED_DELTA_WITH_REPLICATION_GUARD_FAILURE"

    return {
        "schema": "neon.multiscale_density.development_fit.v1",
        "status": "RELEASE2026_DEVELOPMENT_RESULT",
        "contract": str(CONTRACT.relative_to(ROOT)),
        "support": {
            "metric_scored_sessions": len(metric["sessions"]),
            "mnka_paired_sessions": len(paired),
            "joined_sessions": len(joined),
            "frozen_genus_sessions_before_series_rule": len(frozen),
            "analysis_sessions": len(analysis_rows),
            "analysis_series": len(eligible_series),
            "taxon_concepts": len(by_taxon),
            "genera": len(by_genus),
            "sites": len(by_site),
            "sessions_by_genus": dict(sorted(by_genus.items())),
            "sessions_by_taxon": dict(sorted(by_taxon.items())),
        },
        "model": model,
        "ecological_classification": {
            "class": ecological_class,
            "delta_beta_m2_per_mnka": primary_beta,
            "beta_W_m2_per_mnka": beta_w,
            "beta_B_debiased_m2_per_mnka": beta_b,
            "interpretation_boundary": (
                "association within repeated taxon x plot series after frozen "
                "calendar adjustment; RELEASE-2026 is development data and "
                "does not establish causal density effects"
            ),
        },
        "identity_check": {
            "beta_D": primary_beta,
            "beta_B_minus_beta_W": float(
                model["secondary_slopes"]["difference_identity_check"]
            ),
            "absolute_error": identity_error,
        },
        "analysis_rows": analysis_rows,
        "effect_boundary": {
            "W_joined_to_MNKA": True,
            "B_joined_to_MNKA": True,
            "abundance_response_slopes_opened": True,
            "habitat_moderators_opened": False,
            "future_confirmatory_response_opened": False,
        },
    }


def main() -> int:
    result = run()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    model = result["model"]
    print(json.dumps({
        "status": result["status"],
        "support": result["support"],
        "primary_delta": model["primary_delta"],
        "secondary_slopes": model["secondary_slopes"],
        "positive_genus_count": model["positive_genus_count"],
        "leave_one_genus_out": model["leave_one_genus_out"],
        "sensitivities": model["sensitivities"],
        "decision": model["decision"],
        "ecological_classification": result["ecological_classification"],
        "effect_boundary": result["effect_boundary"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
