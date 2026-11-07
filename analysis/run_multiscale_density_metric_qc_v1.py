#!/usr/bin/env python3
"""Metric-only QC for frozen multiscale-density W/B estimators.

This runner calculates W and B for the frozen target/complete/saturation-guarded
response sessions but does NOT calculate or join MNKA, abundance, habitat, or
any abundance-response slope.
"""
from __future__ import annotations

import json
import os
import statistics
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

from analysis.audit_multiscale_density_estimability_v1 import audit, _capture_row
from analysis.multiscale_density_metrics_v1 import session_metrics
from analysis.run_multiscale_density_estimability_release2026_v3 import (
    END, MAX_DOWNLOAD_WORKERS, PRODUCT, PRODUCT_URL, QUERY_URL, RELEASE, START,
    TOKEN_ENV, _candidate_nights, _download_many, _inventory, _read_plot_rows,
    _read_trap_rows, _request_json, _site_codes, _write_csv,
)

ROOT = Path(__file__).resolve().parents[1]
TARGET_LOCK = ROOT / "results" / "multiscale_density_target_taxon_lock_v1.json"
OUT = ROOT / "build" / "multiscale_density_metric_qc_v1.json"
MIN_REPEAT = 5
SATURATION_MAX = 0.30
MIN_SCORED_FRACTION = 0.95
MAX_NONPOSITIVE_B_FRACTION = 0.01


def q(values, p):
    x = sorted(float(v) for v in values)
    if not x:
        return None
    if len(x) == 1:
        return x[0]
    pos = (len(x) - 1) * p
    lo = int(pos)
    hi = min(lo + 1, len(x) - 1)
    f = pos - lo
    return x[lo] * (1-f) + x[hi] * f


def summarize(values):
    if not values:
        return {"n": 0}
    return {
        "n": len(values),
        "min": min(values),
        "q10": q(values, .10),
        "median": statistics.median(values),
        "q90": q(values, .90),
        "max": max(values),
    }


def run(*, include_centroid_coordinates: bool = False) -> dict:
    """Optional geometry-only output; default preserves frozen metric result."""

    token = os.environ.get(TOKEN_ENV, "").strip()
    if not token:
        raise RuntimeError("NEON_API_TOKEN is required")
    target_ids = set(json.loads(TARGET_LOCK.read_text())["target_taxon_ids"])

    sites = _site_codes(_request_json(PRODUCT_URL))
    query = _request_json(
        QUERY_URL,
        token=token,
        body={
            "productCode": PRODUCT,
            "siteCodes": sites,
            "startDateMonth": START,
            "endDateMonth": END,
            "release": RELEASE,
            "package": "basic",
            "includeProvisional": False,
        },
    )
    inventory = _inventory(query)

    plot_files = [r for r in inventory if "mam_perplotnight" in r["name"]]
    plot_raw = _download_many(plot_files, token, max_workers=MAX_DOWNLOAD_WORKERS)
    plot_rows = []
    for meta, raw in zip(plot_files, plot_raw):
        plot_rows.extend(_read_plot_rows(raw, meta["site"], meta["month"]))

    candidate_nights, candidate_site_months = _candidate_nights(plot_rows)
    trap_files = [
        r for r in inventory
        if "mam_pertrapnight" in r["name"]
        and (r["site"], r["month"]) in candidate_site_months
    ]
    trap_raw = _download_many(trap_files, token, max_workers=MAX_DOWNLOAD_WORKERS)
    trap_rows = []
    for meta, raw in zip(trap_files, trap_raw):
        rows = _read_trap_rows(raw, candidate_nights)
        for row in rows:
            row["_site"] = meta["site"]
        trap_rows.extend(rows)

    compact_plot = [
        {k: row[k] for k in (
            "nightuid","eventID","plotID","siteID","mammalGridSamplingType",
            "gridCompletion","collectDate"
        )}
        for row in plot_rows if row["nightuid"] in candidate_nights
    ]

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        p = root / "p.csv"; t = root / "t.csv"
        _write_csv(p, compact_plot, [
            "nightuid","eventID","plotID","siteID","mammalGridSamplingType",
            "gridCompletion","collectDate"
        ])
        _write_csv(t, trap_rows, [
            "nightuid","plotID","trapCoordinate","trapStatus","tagID","taxonID",
            "scientificName","identificationQualifier","taxonRank"
        ])
        structural = audit(p, t)

    frozen_sessions = [
        s for s in structural["support"]["sessions"]
        if s.get("primary_complete_session")
        and s["taxon"] in target_ids
        and int(s.get("n_repeat_coordinate_supported_tagged_individuals",0)) >= MIN_REPEAT
        and float(s.get("all_capture_trap_night_fraction_of_observed",1.0)) <= SATURATION_MAX
    ]

    # Map nights to frozen event/plot and identify event-level taxonomy conflicts.
    night_meta = {}
    for row in compact_plot:
        night_meta[row["nightuid"]] = (row["plotID"], row["eventID"])

    event_tag_taxa = defaultdict(set)
    for row in trap_rows:
        if not _capture_row(row, "trapStatus", "tagID"):
            continue
        meta = night_meta.get(row["nightuid"])
        if meta is None:
            continue
        plot, event = meta
        tag = str(row.get("tagID","")).strip()
        taxon = str(row.get("taxonID","")).strip()
        if tag and taxon:
            event_tag_taxa[(plot,event,tag)].add(taxon)
    conflicted = {k for k,v in event_tag_taxa.items() if len(v) > 1}

    wanted = {(s["taxon"],s["plot_id"],s["event_id"]) for s in frozen_sessions}
    records = defaultdict(lambda: defaultdict(list))
    same_night_coordinate_sets = defaultdict(lambda: defaultdict(set))
    for row in trap_rows:
        if not _capture_row(row, "trapStatus", "tagID"):
            continue
        meta = night_meta.get(row["nightuid"])
        if meta is None:
            continue
        plot,event = meta
        taxon = str(row.get("taxonID","")).strip()
        tag = str(row.get("tagID","")).strip()
        key=(taxon,plot,event)
        if key not in wanted or not tag or (plot,event,tag) in conflicted:
            continue
        records[key][tag].append((row["nightuid"],row["trapCoordinate"]))
        same_night_coordinate_sets[(key,tag)][row["nightuid"]].add(
            str(row["trapCoordinate"]).strip()
        )

    scored=[]
    failed=[]
    individual_same_night_conflicts=0
    for s in frozen_sessions:
        key=(s["taxon"],s["plot_id"],s["event_id"])
        for tag, by_night in [
            (tag, same_night_coordinate_sets[(key,tag)])
            for tag in records[key]
        ]:
            if any(len({x for x in coords if x}) > 1 for coords in by_night.values()):
                individual_same_night_conflicts += 1
        try:
            m=session_metrics(records[key], minimum_individuals=MIN_REPEAT)
        except ValueError as exc:
            failed.append({
                "taxon":s["taxon"],"plot_id":s["plot_id"],"event_id":s["event_id"],
                "reason":str(exc),
            })
            continue
        scored.append({
            "taxon":s["taxon"],
            "genus":s["genus_labels"][0] if len(s["genus_labels"])==1 else "",
            "site":s["site_ids"][0] if len(s["site_ids"])==1 else "",
            "plot_id":s["plot_id"],
            "event_id":s["event_id"],
            "n_individuals":m["n_individuals"],
            "n_excluded_or_inconsistent":len(m["excluded_or_inconsistent_tag_ids"]),
            **({
                "individual_centroid_coordinates_m": [
                    record["centroid_m"] for record in m["individuals"]
                ],
            } if include_centroid_coordinates else {}),
            "W_m2":m["W_m2"],
            "B_observed_m2":m["B_observed_m2"],
            "centroid_noise_correction_m2":m["centroid_noise_correction_m2"],
            "B_debiased_m2":m["B_debiased_m2"],
        })

    n_frozen=len(frozen_sessions)
    n_scored=len(scored)
    scored_fraction=n_scored/n_frozen if n_frozen else 0.0
    nonpositive=sum(x["B_debiased_m2"] <= 0 for x in scored)
    nonpositive_fraction=nonpositive/n_scored if n_scored else 1.0

    taxa={x["taxon"] for x in scored}; genera={x["genus"] for x in scored if x["genus"]}
    sites_sc={x["site"] for x in scored if x["site"]}
    gs=Counter(); gsites=defaultdict(set)
    for x in scored:
        if x["genus"]:
            gs[x["genus"]]+=1
            if x["site"]: gsites[x["genus"]].add(x["site"])
    replicated_genera=[
        {"genus":g,"sessions":gs[g],"sites":len(gsites[g])}
        for g in sorted(gs)
        if gs[g] >= 10 and len(gsites[g]) >= 2
    ]

    gate={
        "scored_fraction": {
            "observed":scored_fraction,"required_minimum":MIN_SCORED_FRACTION,
            "pass":scored_fraction >= MIN_SCORED_FRACTION,
        },
        "nonpositive_B_debiased_fraction": {
            "observed":nonpositive_fraction,
            "required_maximum":MAX_NONPOSITIVE_B_FRACTION,
            "pass":nonpositive_fraction <= MAX_NONPOSITIVE_B_FRACTION,
        },
        "taxon_concepts":{"observed":len(taxa),"required_minimum":4,"pass":len(taxa)>=4},
        "resolved_genera":{"observed":len(genera),"required_minimum":2,"pass":len(genera)>=2},
        "sites":{"observed":len(sites_sc),"required_minimum":6,"pass":len(sites_sc)>=6},
        "replicated_genera":{
            "observed":len(replicated_genera),"required_minimum":2,
            "pass":len(replicated_genera)>=2,
        },
    }
    passed=all(v["pass"] for v in gate.values())

    return {
        "schema":"neon.multiscale_density.metric_qc.v1",
        "status":"METRIC_QC_PASS" if passed else "METRIC_QC_STOP",
        "source":{
            "product":PRODUCT,"release":RELEASE,"query_start":START,"query_end":END,
            "target_lock":str(TARGET_LOCK.relative_to(ROOT)),
            "metric_contract":"results/multiscale_density_metric_contract_v1.json",
        },
        "support":{
            "frozen_target_guarded_sessions":n_frozen,
            "successfully_scored_sessions":n_scored,
            "failed_sessions":len(failed),
            "failed_examples":failed[:20],
            "individual_same_night_multi_coordinate_conflicts":individual_same_night_conflicts,
            "taxon_concepts":len(taxa),"resolved_genera":len(genera),
            "sites":len(sites_sc),"replicated_genera":replicated_genera,
        },
        "metric_distributions":{
            "W_m2":summarize([x["W_m2"] for x in scored]),
            "B_observed_m2":summarize([x["B_observed_m2"] for x in scored]),
            "centroid_noise_correction_m2":summarize(
                [x["centroid_noise_correction_m2"] for x in scored]
            ),
            "B_debiased_m2":summarize([x["B_debiased_m2"] for x in scored]),
            "B_debiased_nonpositive_count":nonpositive,
            "B_debiased_nonpositive_fraction":nonpositive_fraction,
        },
        "gate_checks":gate,
        "decision":{
            "metric_qc_passed":passed,
            "abundance_join_authorized":passed,
            "next_gate":(
                "freeze joint W/B ~ genus-MNKA model contract before opening slopes"
                if passed else
                "STOP simple coordinate route; do not alter m, truncate B, or change geometry to rescue"
            ),
        },
        "sessions":scored,
        "effect_boundary":{
            "W_opened_for_metric_qc":True,
            "B_opened_for_metric_qc":True,
            "MNKA_joined":False,
            "abundance_response_slopes_opened":False,
            "habitat_moderators_opened":False,
        },
    }


def main():
    result=run()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":result["status"],
        "support":{k:v for k,v in result["support"].items() if k!="failed_examples"},
        "metric_distributions":result["metric_distributions"],
        "gate_checks":result["gate_checks"],
        "decision":result["decision"],
        "effect_boundary":result["effect_boundary"],
    },indent=2,sort_keys=True))
    return 0 if result["decision"]["metric_qc_passed"] else 3


if __name__=="__main__":
    raise SystemExit(main())
