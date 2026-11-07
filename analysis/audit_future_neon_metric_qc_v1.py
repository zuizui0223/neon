#!/usr/bin/env python3
"""Blind prospective NEON W/B metric quality control.

The candidate source is provisional data in *full site-months absent*
RELEASE-2026. It has already passed release-event disjointness, target/m>=5
support and continuous-genus-MNKA structure checks in independent workflows.

This scorer opens the new coordinate response METRICS ONLY; deliberately does
not download or join historical MNKA, fit any abundance response, choose
genera based on effects, or examine habitat moderators. Metric QC uses the
same frozen matched-cohort estimator and fixed 95% and 1% thresholds.
"""
from __future__ import annotations

import hashlib
import json
import os
import statistics
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

from analysis.audit_multiscale_density_estimability_v1 import (
    audit as structural_audit, _capture_row,
)
from analysis.audit_future_neon_mammal_availability_v1 import (
    audit as public_availability, URL as PUBLIC_URL,
)
from analysis.audit_future_neon_plot_structure_v1 import (
    select_provisional_plot_files, START, END,
)
from analysis.audit_future_neon_capture_support_v1 import select_complete_events
from analysis.multiscale_density_metrics_v1 import session_metrics
from analysis.run_multiscale_density_estimability_release2026_v3 import (
    _request_json, _download_many, _read_plot_rows, _read_trap_rows,
    _write_csv, PRODUCT, QUERY_URL, TOKEN_ENV, MAX_DOWNLOAD_WORKERS,
)

ROOT=Path(__file__).resolve().parents[1]
LOCK=ROOT/"results/multiscale_density_target_taxon_lock_v1.json"
OUT=ROOT/"build/future_neon_metric_qc_v1.json"
ROWS=ROOT/"build/future_neon_metric_session_values_v1.json"
COMPLETE="setting complete, processing complete"
MIN_REPEAT=5
MAX_SATURATION=.30
MIN_SCORED_FRACTION=.95
MAX_NONPOS_B=.01


def _summary(xs:list[float]):
    if not xs:return {"n":0}
    vals=sorted(xs)
    return {
        "n":len(vals),"min":vals[0],
        "median":statistics.median(vals),"max":vals[-1],
    }


def compute_metric_only(
    plot_rows:list[dict], trap_rows:list[dict], target_ids:set[str],
) -> tuple[dict,list[dict]]:
    selected=select_complete_events(plot_rows)
    if len(selected["events"])!=505:
        raise RuntimeError("provisional complete three-night event count drift")
    nights=set(selected["nights"])
    compact=[{k:r.get(k,"") for k in (
        "nightuid","eventID","plotID","siteID","mammalGridSamplingType",
        "gridCompletion","collectDate")}
        for r in plot_rows if r["nightuid"] in nights]
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)
        p=root/"p.csv";t=root/"t.csv"
        _write_csv(p,compact,["nightuid","eventID","plotID","siteID",
            "mammalGridSamplingType","gridCompletion","collectDate"])
        _write_csv(t,trap_rows,["nightuid","plotID","trapCoordinate",
            "trapStatus","tagID","taxonID","scientificName",
            "identificationQualifier","taxonRank"])
        structural=structural_audit(p,t)

    eligible=[
        s for s in structural["support"]["sessions"]
        if s.get("primary_complete_session")
        and s.get("taxon") in target_ids
        and int(s.get("n_repeat_coordinate_supported_tagged_individuals",0))>=MIN_REPEAT
        and float(s.get("all_capture_trap_night_fraction_of_observed",1.))<=MAX_SATURATION
        and len(s.get("site_ids",[]))==1
        and len(s.get("genus_labels",[]))==1
    ]
    if len(eligible)!=287:
        raise RuntimeError(f"candidate m/saturation cohort drifted: {len(eligible)} != 287")

    wanted={(s["taxon"],s["site_ids"][0],s["plot_id"],s["event_id"])
            for s in eligible}
    event_tag_taxa=defaultdict(set)
    for r in trap_rows:
        if not _capture_row(r,"trapStatus","tagID"):continue
        event=selected["nights"].get(r["nightuid"])
        if event is None:continue
        tag=str(r.get("tagID") or "").strip()
        tax=str(r.get("taxonID") or "").strip()
        if tag and tax:
            event_tag_taxa[(event[0],event[1],event[2],tag)].add(tax)
    conflicting={k for k,taxa in event_tag_taxa.items() if len(taxa)>1}
    records=defaultdict(lambda:defaultdict(list))
    for r in trap_rows:
        if not _capture_row(r,"trapStatus","tagID"):continue
        event=selected["nights"].get(r["nightuid"])
        if event is None:continue
        site,plot,eid=event
        tag=str(r.get("tagID") or "").strip()
        tax=str(r.get("taxonID") or "").strip()
        key=(tax,site,plot,eid)
        if (key not in wanted or not tag or
                (site,plot,eid,tag) in conflicting):
            continue
        records[key][tag].append((r["nightuid"],r["trapCoordinate"]))

    scored=[];failed=[]
    for session in eligible:
        tax=session["taxon"]
        site=session["site_ids"][0]
        plot=session["plot_id"];event=session["event_id"]
        key=(tax,site,plot,event)
        try:
            metric=session_metrics(records[key],
                                   minimum_individuals=MIN_REPEAT)
        except ValueError as e:
            failed.append({"taxon":tax,"site":site,
                           "plot":plot,"event":event,"reason":str(e)})
            continue
        coords=[row["centroid_m"] for row in metric["individuals"]]
        scored.append({
            "taxon":tax,"genus":session["genus_labels"][0],
            "site":site,"plot_id":plot,"event_id":event,
            "m":metric["n_individuals"],
            "W_m2":metric["W_m2"],
            "B_observed_m2":metric["B_observed_m2"],
            "B_debiased_m2":metric["B_debiased_m2"],
            "D_m2":metric["B_debiased_m2"]-metric["W_m2"],
            "centroids_m":coords,
        })

    if len({(s["taxon"],s["site"],s["plot_id"],s["event_id"])
            for s in scored})!=len(scored):
        raise RuntimeError("duplicate scored future session identity")
    total=len(eligible)
    fraction=len(scored)/total
    nonpos=sum(s["B_debiased_m2"]<=0 for s in scored)
    nonposfrac=nonpos/len(scored) if scored else 1.
    outcome=(fraction>=MIN_SCORED_FRACTION and
             nonposfrac<=MAX_NONPOS_B)
    summary={
        "schema":"neon.future_mammal_metric_QC.v1",
        "status":"FUTURE_METRIC_QC_PASS" if outcome else "STOP_FUTURE_METRIC_QC",
        "source":"PROVISIONAL full site-months absent RELEASE-2026",
        "frozen_source_release":"RELEASE-2026",
        "complete_three_night_events":len(selected["events"]),
        "frozen_m_ge5_saturation_le030_session_count":total,
        "successfully_scored_sessions":len(scored),
        "metric_score_fraction":fraction,
        "required_min_score_fraction":MIN_SCORED_FRACTION,
        "nonpositive_B_debiased_count":nonpos,
        "nonpositive_B_debiased_fraction":nonposfrac,
        "max_nonpositive_B_fraction":MAX_NONPOS_B,
        "failed_session_count":len(failed),
        "failed_session_reasons":dict(Counter(s["reason"] for s in failed)),
        "sites_retained":len({r["site"] for r in scored}),
        "genera_retained":dict(sorted(Counter(r["genus"] for r in scored).items())),
        "taxa_retained":len({r["taxon"] for r in scored}),
        "median_W_m2":_summary([s["W_m2"] for s in scored])["median"] if scored else None,
        "median_B_debiased_m2":_summary([s["B_debiased_m2"] for s in scored])["median"] if scored else None,
        "new_MNKA_joined":False,
        "new_density_slopes_opened":False,
        "future_ecological_confirmation_declared":False,
        "source_provisional_not_immutable_release":True,
        "interpretation":"Metric-only QC can authorize a later locked MNKA join; it cannot demonstrate density-dependent space use or an ecological mechanism."
    }
    return summary,scored


def run():
    token=os.environ.get(TOKEN_ENV,"").strip()
    if not token:raise RuntimeError("NEON_API_TOKEN required")
    target=set(json.loads(LOCK.read_text())["target_taxon_ids"])
    public=public_availability(_request_json(PUBLIC_URL),"2026-10-10")
    candidate={(s["site"],s["month"]) for s in public["site_month_candidates"]
               if START<=s["month"]<=END}
    sites=sorted({s for s,_ in candidate})
    q=_request_json(QUERY_URL,token=token,
        body={"productCode":PRODUCT,"siteCodes":sites,
              "startDateMonth":START,"endDateMonth":END,
              "package":"basic","includeProvisional":True})
    plots=select_provisional_plot_files(q,candidate,kind="mam_perplotnight")["files"]
    traps=select_provisional_plot_files(q,candidate,kind="mam_pertrapnight")["files"]
    if len(plots)!=301 or len(traps)!=301:
        raise RuntimeError("expected 301 checksum-verified files of each type")
    plot_rows=[]
    for f,raw in zip(plots,_download_many(
            plots,token,max_workers=MAX_DOWNLOAD_WORKERS)):
        plot_rows.extend(_read_plot_rows(raw,f["site"],f["month"]))
    selected=select_complete_events(plot_rows)
    capture=[]
    for f,raw in zip(traps,_download_many(
            traps,token,max_workers=MAX_DOWNLOAD_WORKERS)):
        capture.extend(_read_trap_rows(raw,set(selected["nights"])))
    summary,scored=compute_metric_only(plot_rows,capture,target)
    for name,files in (("plot",plots),("trap",traps)):
        summary[f"{name}_inventory_digest_SHA256"]=hashlib.sha256(
            json.dumps([(r["site"],r["month"],r["name"],r["md5"])
                        for r in files],sort_keys=True).encode()).hexdigest()
    summary["provisional_trap_rows_processed"]=len(capture)
    return summary,scored


if __name__=="__main__":
    try:
        report,scored=run()
    except (RuntimeError,ValueError) as e:
        report={"schema":"neon.future_mammal_metric_QC.v1",
                "status":"STOP_METRIC_SOURCE_OR_QC_ERROR",
                "diagnostic":str(e),"new_MNKA_joined":False,
                "new_density_slopes_opened":False}
        scored=[]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if scored:
        ROWS.write_text(json.dumps(scored,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))
    if report["status"]!="FUTURE_METRIC_QC_PASS":
        raise SystemExit(3)
