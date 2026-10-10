#!/usr/bin/env python3
"""Strictly effect-blind prospective NEON capture-support gate.

Read provisional, non-RELEASE-2026 site-months only. The script opens capture
IDs and coordinate PRESENCE for a locked support gate, never numeric coordinates,
W, B, or the MNKA-response slopes. Future response fitting remains prohibited
until release segregation, genus-level MNKA variation and all support
thresholds are evaluated and locked.
"""
from __future__ import annotations

import json
import os
import tempfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from analysis.audit_multiscale_density_estimability_v1 import audit
from analysis.audit_future_neon_plot_structure_v1 import (
    select_provisional_plot_files, COMPLETE, START, END,
    FROZEN_RELEASE,
)
from analysis.audit_future_neon_mammal_availability_v1 import (
    audit as availability, URL as PRODUCT_URL_PUBLIC,
)
from analysis.run_multiscale_density_estimability_release2026_v3 import (
    _request_json,_download_many,_read_plot_rows,_read_trap_rows,
    _write_csv, PRODUCT, QUERY_URL, TOKEN_ENV, MAX_DOWNLOAD_WORKERS,
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/future_neon_capture_support_v1.json"
TAXON_LOCK=ROOT/"results/multiscale_density_target_taxon_lock_v1.json"
MODE_GENERA=("Chaetodipus","Myodes","Peromyscus","Dipodomys","Sigmodon")
SEVEN_TAXA=("CHHI","PEBO","PEGO","PELE","PEMA","DIOR","SIHI")


def select_complete_events(plot_rows: list[dict]) -> dict:
    by_event=defaultdict(list)
    for r in plot_rows:
        if all(r.get(k) for k in ("siteID","plotID","eventID","nightuid")):
            by_event[(r["siteID"],r["plotID"],r["eventID"])].append(r)
    chosen={}
    night_to_event={}
    for key,rows in by_event.items():
        site,plot,event=key
        nights={x["nightuid"] for x in rows}
        if site=="SRER" or len(nights)!=3 or {x["gridCompletion"] for x in rows}!={COMPLETE}:
            continue
        dates=sorted({x["collectDate"] for x in rows if x["collectDate"]})
        if not dates: continue
        # Parse collection date; no imputation from filename or global calendar.
        d=date.fromisoformat(dates[0][:10])
        chosen[key]={"date":d,"nights":nights}
        for n in nights:
            if n in night_to_event:
                raise RuntimeError("future nightuid maps to multiple events")
            night_to_event[n]=key
    return {"events":chosen,"nights":night_to_event}


def summarize_effect_blind_support(sessions: list[dict], target_ids: set[str]) -> dict:
    eligible=[]
    for s in sessions:
        if not s.get("primary_complete_session"):continue
        if s.get("taxon") not in target_ids:continue
        if int(s.get("n_repeat_coordinate_supported_tagged_individuals",0))<5:continue
        if float(s.get("all_capture_trap_night_fraction_of_observed",1.0))>0.30:continue
        if len(s.get("site_ids",[]))!=1 or len(s.get("genus_labels",[]))!=1:continue
        eligible.append({
            "taxon":s["taxon"],"site":s["site_ids"][0],
            "genus":s["genus_labels"][0],
            "plot":s["plot_id"],"event":s["event_id"],
            "repeat_supported_individuals":int(s["n_repeat_coordinate_supported_tagged_individuals"]),
            "saturation":float(s["all_capture_trap_night_fraction_of_observed"])
        })
    genus_counts=Counter(r["genus"] for r in eligible)
    tax_counts=Counter(r["taxon"] for r in eligible)
    mode={}
    for genus in MODE_GENERA:
        g=[r for r in eligible if r["genus"]==genus]
        mode[genus]={"eligible_response_sessions":len(g),
                    "sites":len({r["site"] for r in g}),
                    "taxon_plot_series":len({(r["taxon"],r["site"],r["plot"]) for r in g}),
                    "series_with_ge3_sessions":sum(n>=3 for n in Counter(
                        (r["taxon"],r["site"],r["plot"]) for r in g).values())}
    fixed_taxa={}
    for taxon in SEVEN_TAXA:
        t=[r for r in eligible if r["taxon"]==taxon]
        fixed_taxa[taxon]={"eligible_response_sessions":len(t),
                          "sites":len({r["site"] for r in t}),
                          "series_with_ge3_sessions":sum(n>=3 for n in Counter(
                              (r["site"],r["plot"]) for r in t).values())}
    return {
        "eligible_target_taxon_sessions_m5_saturation30":len(eligible),
        "target_taxa_with_support":len(tax_counts),
        "genera_with_support":len(genus_counts),
        "sites_with_support":len({r["site"] for r in eligible}),
        "mode_genus_support":mode,
        "frozen_taxon_support":fixed_taxa,
        "genus_counts":dict(sorted(genus_counts.items())),
        "mnka_variation_checked":False,
        "individual_centroid_positions_extracted":False,
        "spatial_distances_computed":False,
        "future_W_B_response_opened":False,
    }


def run() -> dict:
    token=os.environ.get(TOKEN_ENV,"").strip()
    if not token:raise RuntimeError("NEON_API_TOKEN is required")
    lock=json.loads(TAXON_LOCK.read_text())
    target_ids=set(lock["target_taxon_ids"])
    public=availability(_request_json(PRODUCT_URL_PUBLIC),"2026-10-10")
    candidates={(x["site"],x["month"]) for x in public["site_month_candidates"]
                if START<=x["month"]<=END}
    sites=sorted({s for s,_ in candidates})
    if not sites:raise RuntimeError("no full site-month outside frozen release")
    q=_request_json(QUERY_URL,token=token,
        body={"productCode":PRODUCT,"siteCodes":sites,
              "startDateMonth":START,"endDateMonth":END,
              "package":"basic","includeProvisional":True})
    plots=select_provisional_plot_files(q,candidates,kind="mam_perplotnight")["files"]
    traps=select_provisional_plot_files(q,candidates,kind="mam_pertrapnight")["files"]
    if not plots or not traps:raise RuntimeError("missing provisional plot or trap inventory")
    plot_rows=[]
    for f,raw in zip(plots,_download_many(plots,token,max_workers=MAX_DOWNLOAD_WORKERS)):
        plot_rows.extend(_read_plot_rows(raw,f["site"],f["month"]))
    selected=select_complete_events(plot_rows)
    nights=set(selected["nights"])
    if len(selected["events"])!=505:
        raise RuntimeError("preflight verified 505 complete provisional events drifted")
    trap_rows=[]
    for f,raw in zip(traps,_download_many(traps,token,max_workers=MAX_DOWNLOAD_WORKERS)):
        trap_rows.extend(_read_trap_rows(raw,nights))
    # Numeric trapCoordinate is NEVER read as a geometric point: audit() checks
    # only that a value exists and a tag occurs on at least two distinct nights.
    flat_plot=[{k:r.get(k,"") for k in (
        "nightuid","eventID","plotID","siteID","mammalGridSamplingType",
        "gridCompletion","collectDate")} for r in plot_rows if r["nightuid"] in nights]
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/"plots.csv";t=Path(td)/"traps.csv"
        _write_csv(p,flat_plot,["nightuid","eventID","plotID","siteID",
            "mammalGridSamplingType","gridCompletion","collectDate"])
        _write_csv(t,trap_rows,["nightuid","plotID","trapCoordinate",
            "trapStatus","tagID","taxonID","scientificName",
            "identificationQualifier","taxonRank"])
        result=audit(p,t)
    support=summarize_effect_blind_support(result["support"]["sessions"],target_ids)
    return {
        "schema":"neon.future_mammal_capture_support.v1",
        "status":"EFFECT_BLIND_PROVISIONAL_CAPTURE_SUPPORT_ONLY",
        "source":"PROVISIONAL months absent RELEASE-2026, 2025-01..2026-09, checked by site-month",
        "plot_files_MD5_verified":len(plots),"trap_files_MD5_verified":len(traps),
        "exact_three_night_complete_events":len(selected["events"]),
        "capture_trap_night_rows_processed":len(trap_rows),
        "support":support,
        "release2026_same_month_excluded":True,
        "event_id_disjointness_against_all_old_months_checked":False,
        "independent_confirmation_authorized":False,
        "future_MNKA_within_series_variation_checked":False,
        "next_gate":"Verify historical event-ID disjointness and 3+ events / two distinct future-only genus MNKA values in each fixed taxon/genus, before opening any future spatial outcome.",
        "provisional_version_warning":"Live provisional records are mutable; freeze source file hashes and cross-check against subsequent official release before promoting replication."
    }


if __name__=="__main__":
    output=run()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(output,indent=2,sort_keys=True))
