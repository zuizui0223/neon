#!/usr/bin/env python3
"""Effect-blind continuous-history NEON MNKA support across release boundaries.

Validation ordering:
(1) verify old/new checksum-locked perplotnight identities are disjoint;
(2) select the *same* complete 3-night standard bouts in both sources;
(3) read only capture identity and target taxon, not numeric coordinates;
(4) construct continuous known-alive intervals in time-ordered old+new events;
(5) compare provisional-only and boundary-continuous genus MNKA support.

No new W/B, NN, biological slopes or future hypothesis decisions are opened.
Provisional source remains mutable even if identifier disjointness passes.
"""
from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from pathlib import Path

from analysis.audit_future_neon_release_disjointness_v1 import compare_identifiers
from analysis.audit_future_neon_capture_support_v1 import (
    select_complete_events, summarize_effect_blind_support,
)
from analysis.audit_future_neon_mnka_support_v1 import (
    future_only_mnka_support, MODE_GENERA, FROZEN_TAXA,
)
from analysis.audit_future_neon_null_b_support_v1 import (
    null_b_screen_on_varying_series,
)
from analysis.audit_future_neon_mammal_availability_v1 import (
    audit as public_inventory, URL as PRODUCT_META_URL,
)
from analysis.audit_future_neon_plot_structure_v1 import (
    select_provisional_plot_files, START as NEW_START, END as NEW_END,
    FROZEN_RELEASE,
)
from analysis.audit_multiscale_density_estimability_v1 import (
    _capture_row, audit as structural_audit,
)
from analysis.audit_multiscale_density_mnka_variation_v1 import _taxonomy
from analysis.run_multiscale_density_estimability_release2026_v3 import (
    _request_json, _inventory, _download_many, _read_plot_rows,
    _read_trap_rows, _write_csv, PRODUCT, QUERY_URL, TOKEN_ENV,
    MAX_DOWNLOAD_WORKERS,
)
import tempfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/future_neon_continuous_mnka_support_v1.json"
LOCK=ROOT/"results/multiscale_density_target_taxon_lock_v1.json"
OLD_START="2015-04"
END="2026-09"


def _event_order(selected_old: dict, selected_new: dict):
    """A site-plot event has one integer calendar order across both sources."""
    events=dict(selected_old["events"])
    if set(events)&set(selected_new["events"]):
        raise RuntimeError("event identity overlap across data releases")
    events.update(selected_new["events"])
    by_plot=defaultdict(list)
    for key,entry in events.items():
        by_plot[key[:2]].append((entry["date"],key))
    index={}
    for arr in by_plot.values():
        for i,(_,key) in enumerate(sorted(arr,key=lambda p:(p[0],p[1][2]))):
            index[key]=i
    night=dict(selected_old["nights"])
    if set(night)&set(selected_new["nights"]):
        raise RuntimeError("night identity overlap across data releases")
    night.update(selected_new["nights"])
    return index,night


def continuous_known_alive_mnka(
    old_traps:list[dict], new_traps:list[dict],
    old_selected:dict,new_selected:dict,
    taxonomy_genera:dict[str,str], target_ids:set[str],
) -> dict:
    """Compute categorical genus MNKA for the *new* sessions only."""
    indexes,night_event=_event_order(old_selected,new_selected)
    tag_genera=defaultdict(set)
    tag_events=defaultdict(set)
    old_tags=set();new_tags=set()
    old_capture_rows=0;new_capture_rows=0
    for origin,rows in (("old",old_traps),("new",new_traps)):
        for row in rows:
            if not _capture_row(row,"trapStatus","tagID"):
                continue
            tid=str(row.get("taxonID") or "").strip()
            tag=str(row.get("tagID") or "").strip()
            if tid not in target_ids or not tag:
                continue
            genus=taxonomy_genera.get(tid)
            if not genus:raise RuntimeError(f"missing frozen target genus for {tid}")
            event=night_event.get(str(row.get("nightuid") or ""))
            if event is None:continue
            key=(event[0],event[1],tag)
            tag_genera[key].add(genus)
            tag_events[key].add(event)
            if origin=="old":
                old_tags.add(key)
                old_capture_rows+=1
            else:
                new_tags.add(key)
                new_capture_rows+=1

    crossed=old_tags & new_tags
    intervals=defaultdict(list)
    excluded_cross_genus=0
    for tag,gs in tag_genera.items():
        if len(gs)!=1:
            excluded_cross_genus+=1
            continue
        vals=sorted(indexes[k] for k in tag_events[tag])
        if vals:
            intervals[(tag[0],tag[1],next(iter(gs)))].append((vals[0],vals[-1]))
    by_plot=defaultdict(dict)
    for (site,plot,genus),hist in intervals.items():
        by_plot[(site,plot)][genus]=hist

    result={}
    for (site,plot,event),_ in new_selected["events"].items():
        i=indexes[(site,plot,event)]
        for genus,hist in by_plot.get((site,plot),{}).items():
            result[(site,plot,event,genus)]=sum(lo<=i<=hi for lo,hi in hist)

    return {
        "new_event_genus_mnka":result,
        "history_audit":{
            "captured_tag_histories_old":len(old_tags),
            "captured_tag_histories_new":len(new_tags),
            "tag_histories_crossing_source_boundary":len(crossed),
            "tag_histories_excluded_cross_genus":excluded_cross_genus,
            "target_tagged_capture_rows_old":old_capture_rows,
            "target_tagged_capture_rows_new":new_capture_rows,
            "continuous_known_alive_intervals":sum(map(len,intervals.values())),
        },
    }


def future_series_variation(
    sessions:list[dict], target_ids:set[str],
    continuous_mnka:dict,
) -> dict:
    """Keep fixed target/m/saturation inclusion before any abundance effects."""
    by_series=defaultdict(list)
    matched=0
    missing=0
    for s in sessions:
        if not s.get("primary_complete_session") or s.get("taxon") not in target_ids:
            continue
        if int(s.get("n_repeat_coordinate_supported_tagged_individuals",0))<5:
            continue
        if float(s.get("all_capture_trap_night_fraction_of_observed",1.0))>0.30:
            continue
        if len(s.get("site_ids",[]))!=1 or len(s.get("genus_labels",[]))!=1:
            continue
        site=s["site_ids"][0];genus=s["genus_labels"][0]
        n=continuous_mnka.get((site,s["plot_id"],s["event_id"],genus))
        if n is None:
            missing+=1
            continue
        matched+=1
        by_series[(s["taxon"],site,s["plot_id"],genus)].append(n)

    def summarize(test):
        supported=[(k,x) for k,x in by_series.items() if test(k)
                   and len(x)>=3 and len(set(x))>=2]
        return {
            "varying_series":len(supported),
            "sessions_in_varying_series":sum(len(x) for _,x in supported),
            "sites_with_varying_series":len({k[1] for k,_ in supported}),
        }
    return {
        "candidate_sessions_paired":matched,
        "candidate_sessions_missing_genus_mnka":missing,
        "mode_genera":{g:summarize(lambda k,g=g:k[3]==g) for g in MODE_GENERA},
        "frozen_taxa":{t:summarize(lambda k,t=t:k[0]==t) for t in FROZEN_TAXA},
        "W_B_opened":False,
        "spatial_distance_opened":False,
    }


def _load(files:list[dict],token:str,kind:str,nights:set[str]|None=None):
    arr=[]
    for f,raw in zip(files,_download_many(
            files,token,max_workers=MAX_DOWNLOAD_WORKERS)):
        if kind=="plots":
            arr.extend(_read_plot_rows(raw,f["site"],f["month"]))
        elif kind=="traps":
            if nights is None: raise ValueError("trap reader requires accepted nights")
            arr.extend(_read_trap_rows(raw,nights))
        else: raise ValueError(kind)
    return arr


def run() -> dict:
    token=os.environ.get(TOKEN_ENV,"").strip()
    if not token:raise RuntimeError("NEON_API_TOKEN required")
    locked=set(json.loads(LOCK.read_text())["target_taxon_ids"])
    live_targets, genus_by_taxon, _=_taxonomy()
    if not locked.issubset(live_targets):
        raise RuntimeError("historical frozen target IDs no longer mapped as target")
    public=public_inventory(_request_json(PRODUCT_META_URL),"2026-10-10")
    cand={(r["site"],r["month"]) for r in public["site_month_candidates"]
          if NEW_START<=r["month"]<=NEW_END}
    sites=sorted({s for s,_ in cand})
    if not sites:raise RuntimeError("no candidate new site-month")

    new_q=_request_json(QUERY_URL,token=token,
        body={"productCode":PRODUCT,"siteCodes":sites,
              "startDateMonth":NEW_START,"endDateMonth":END,
              "package":"basic","includeProvisional":True})
    new_plot_files=select_provisional_plot_files(new_q,cand,kind="mam_perplotnight")["files"]
    new_trap_files=select_provisional_plot_files(new_q,cand,kind="mam_pertrapnight")["files"]
    old_q=_request_json(QUERY_URL,token=token,
        body={"productCode":PRODUCT,"siteCodes":sites,
              "startDateMonth":OLD_START,"endDateMonth":END,
              "release":FROZEN_RELEASE,"package":"basic","includeProvisional":False})
    old_inventory=_inventory(old_q)
    old_plot_files=[r for r in old_inventory if "mam_perplotnight" in r["name"]]
    old_trap_files=[r for r in old_inventory if "mam_pertrapnight" in r["name"]]
    if not (new_plot_files and new_trap_files and old_plot_files and old_trap_files):
        raise RuntimeError("old/new perplotnight or pertrapnight inventory missing")

    old_plot=_load(old_plot_files,token,"plots")
    new_plot=_load(new_plot_files,token,"plots")
    independence=compare_identifiers(old_plot,new_plot)
    if independence["status"]!="IDENTIFIER_DISJOINTNESS_PASS":
        raise RuntimeError("future independent event/night UID identity guard failed")
    old_selected=select_complete_events(old_plot)
    new_selected=select_complete_events(new_plot)
    if len(new_selected["events"])!=505:
        raise RuntimeError("future complete three-night event universe drifted")

    old_trap=_load(old_trap_files,token,"traps",set(old_selected["nights"]))
    new_trap=_load(new_trap_files,token,"traps",set(new_selected["nights"]))

    # Reproduce current frozen target, m >= 5, and saturation <= 0.30 support
    # from provisional capture records; do not calculate numeric distances.
    selected_nights=set(new_selected["nights"])
    plot_selected=[{k:r.get(k,"") for k in (
        "nightuid","eventID","plotID","siteID","mammalGridSamplingType",
        "gridCompletion","collectDate")}
        for r in new_plot if r["nightuid"] in selected_nights]
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/"plot.csv";t=Path(td)/"trap.csv"
        _write_csv(p,plot_selected,["nightuid","eventID","plotID","siteID",
            "mammalGridSamplingType","gridCompletion","collectDate"])
        _write_csv(t,new_trap,["nightuid","plotID","trapCoordinate","trapStatus",
            "tagID","taxonID","scientificName","identificationQualifier","taxonRank"])
        structured=structural_audit(p,t)
    sessions=structured["support"]["sessions"]
    support=summarize_effect_blind_support(sessions,locked)
    if support["eligible_target_taxon_sessions_m5_saturation30"]!=287:
        raise RuntimeError("new capture-support cohort drifted")

    continuous=continuous_known_alive_mnka(
        old_trap,new_trap,old_selected,new_selected,genus_by_taxon,locked)
    variations=future_series_variation(
        sessions,locked,continuous["new_event_genus_mnka"])
    null_b_screen=null_b_screen_on_varying_series(
        sessions,locked,continuous["new_event_genus_mnka"])

    # Historical source ID and output history counts only; no raw tag IDs.
    return {
        "schema":"neon.future_mammal_continuous_mnka_support.v1",
        "status":"EFFECT_BLIND_CONTINUOUS_HISTORY_SUPPORT_ONLY",
        "source":"RELEASE-2026 historical identity + disjoint PROVISIONAL new capture tags",
        "old_plot_files_MD5_verified":len(old_plot_files),
        "old_trap_files_MD5_verified":len(old_trap_files),
        "new_plot_files_MD5_verified":len(new_plot_files),
        "new_trap_files_MD5_verified":len(new_trap_files),
        "old_complete_three_night_events":len(old_selected["events"]),
        "new_complete_three_night_events":len(new_selected["events"]),
        "new_eligible_target_sessions":support["eligible_target_taxon_sessions_m5_saturation30"],
        "identifier_disjointness_status":independence["status"],
        "history":continuous["history_audit"],
        "continuous_MNKA_future_only_response_support":variations,
        "continuous_MNKA_varying_series_null_B_structural_screen":null_b_screen,
        "future_only_history_comparator":future_only_mnka_support(
            new_trap,new_selected,sessions,locked),
        "future_W_B_opened":False,
        "historical_W_B_reused":False,
        "future_density_effects_opened":False,
        "true_future_confirmation_established":False,
        "ecological_claim_boundary":"Only response-independent future predictor support. Provisional files can be revised; tagged-history interval interpolation is retrospective, not a causal density measurement.",
    }


if __name__=="__main__":
    try:
        result=run()
    except (RuntimeError,ValueError) as exc:
        result={
            "schema":"neon.future_mammal_continuous_mnka_support.v1",
            "status":"STRUCTURAL_STOP_HISTORY_OR_RELEASE_ID_FAILURE",
            "diagnostic":str(exc),
            "future_W_B_opened":False,"ecological_confirmation":False,
        }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    if result["status"]!="EFFECT_BLIND_CONTINUOUS_HISTORY_SUPPORT_ONLY":
        raise SystemExit(3)
