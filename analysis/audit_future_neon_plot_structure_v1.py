#!/usr/bin/env python3
"""Effect-blind provisional NEON three-night session support after RELEASE-2026.

Never download mam_pertrapnight (capture, tag, taxon, or coordinates).
Use NEON product metadata to select full site-months outside RELEASE-2026;
download only per-plot-night scheduling records with published MD5 verification.
No W/B, MNKA, spatial slopes, or genus response is opened.
"""
from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from pathlib import Path

from analysis.audit_future_neon_mammal_availability_v1 import audit as inventory_audit, URL as PRODUCT_URL_PUBLIC
from analysis.run_multiscale_density_estimability_release2026_v3 import (
    _request_json, _site_codes, _download_many, _read_plot_rows,
    PRODUCT, QUERY_URL, TOKEN_ENV, MAX_DOWNLOAD_WORKERS,
)

OUT=Path("build/future_neon_mammal_plot_structure_v1.json")
END="2026-09"
START="2025-01"
FROZEN_RELEASE="RELEASE-2026"
COMPLETE="setting complete, processing complete"


def select_provisional_plot_files(query: dict, candidates: set[tuple[str,str]]) -> dict:
    data=query.get("data")
    if not isinstance(data,dict):
        raise RuntimeError("unrecognized NEON data query response")
    blocks=data.get("releases")
    if not isinstance(blocks,list):
        raise RuntimeError("NEON query lacks release blocks")
    labels=[]
    by_key={}
    for b in blocks:
        release=str(b.get("release") or "").strip()
        labels.append(release)
        if release==FROZEN_RELEASE:
            continue
        for pkg in b.get("packages",[]):
            site=str(pkg.get("siteCode") or "")
            month=str(pkg.get("month") or "")
            if (site,month) not in candidates:
                continue
            if pkg.get("packageType")!="basic":
                continue
            for f in pkg.get("files",[]):
                name=str(f.get("name") or "")
                if "mam_perplotnight" not in name or not name.lower().endswith(".csv"):
                    continue
                row={"site":site,"month":month,"name":name,
                     "size":f.get("size"),"md5":str(f.get("md5") or "").lower(),
                     "url":str(f.get("url") or ""),"release":release}
                if not isinstance(row["size"],int) or row["size"]<=0:
                    raise RuntimeError("invalid plot-night file size")
                if len(row["md5"])!=32 or not row["url"].startswith("https://"):
                    raise RuntimeError("missing verifiable plot-night bytes")
                k=(site,month,name)
                if k in by_key and by_key[k]!=row:
                    raise RuntimeError("conflicting duplicate candidate plot-night file")
                by_key[k]=row
    return {"release_labels":sorted(set(labels)),
            "files":[by_key[k] for k in sorted(by_key)]}


def event_structure(plot_rows: list[dict]) -> dict:
    event_nights=defaultdict(set)
    event_completions=defaultdict(set)
    event_dates=defaultdict(set)
    for r in plot_rows:
        key=(r["siteID"],r["plotID"],r["eventID"])
        if any(not x for x in key):
            continue
        event_nights[key].add(r["nightuid"])
        event_completions[key].add(r["gridCompletion"])
        event_dates[key].add(r["collectDate"])
    exact=[]
    n_night=Counter()
    invalid_completeness=0
    for (site,plot,event),nights in event_nights.items():
        if site=="SRER":
            continue
        n_night[len(nights)]+=1
        if len(nights)!=3: continue
        if event_completions[(site,plot,event)]!={COMPLETE}:
            invalid_completeness+=1
            continue
        if len(event_dates[(site,plot,event)])<1: continue
        exact.append((site,plot,event))
    by_plot=Counter((s,p) for s,p,_ in exact)
    by_site=Counter(s for s,_,_ in exact)
    return {
        "plot_night_records":len(plot_rows),
        "distinct_plot_events":len(event_nights),
        "night_count_histogram":dict(sorted(n_night.items())),
        "exact_three_night_complete_standard_events":len(exact),
        "exact_three_night_not_complete":invalid_completeness,
        "eligible_distinct_sites":len(by_site),
        "eligible_distinct_site_plots":len(by_plot),
        "site_plots_with_at_least_three_events":sum(n>=3 for n in by_plot.values()),
        "sites_with_at_least_three_events":sum(n>=3 for n in by_site.values()),
        "events_by_site":dict(sorted(by_site.items())),
        "new_event_keys_not_checked_against_prior_release":True,
        "capture_or_taxon_support_estimated":False
    }


def run() -> dict:
    token=os.environ.get(TOKEN_ENV,"").strip()
    if not token: raise RuntimeError("NEON_API_TOKEN is required")
    product=_request_json(PRODUCT_URL_PUBLIC)
    public=inventory_audit(product,"2026-10-10")
    if public.get("status") not in ("INVENTORY_ONLY_CANDIDATE_MONTHS",
                                    "NO_FULLY_NEW_SITE_MONTHS_IN_INVENTORY"):
        raise RuntimeError("future public inventory comparison did not pass")
    candidates={(x["site"],x["month"]) for x in public["site_month_candidates"]
                if START<=x["month"]<=END}
    sites=sorted({s for s,_ in candidates})
    if not sites:
        return {"schema":"neon.future_mammal_plot_support.v1",
                "status":"STOP_NO_INDEPENDENT_SITE_MONTHS","W_B_opened":False}
    query=_request_json(
        QUERY_URL,token=token,
        body={"productCode":PRODUCT,"siteCodes":sites,"startDateMonth":START,
              "endDateMonth":END,"package":"basic","includeProvisional":True},
    )
    selection=select_provisional_plot_files(query,candidates)
    files=selection["files"]
    if not files:
        return {"schema":"neon.future_mammal_plot_support.v1",
                "status":"STOP_NO_VALID_PROVISIONAL_PLOT_FILES",
                "public_candidate_site_months":len(candidates),
                "release_labels":selection["release_labels"],
                "W_B_opened":False,"capture_records_opened":False}
    raw=_download_many(files,token,max_workers=MAX_DOWNLOAD_WORKERS)
    rows=[]
    for f,data in zip(files,raw):
        rows.extend(_read_plot_rows(data,f["site"],f["month"]))
    return {
        "schema":"neon.future_mammal_plot_support.v1",
        "state":"STRUCTURE_ONLY_BEFORE_ANY_HELDOUT_RESPONSES",
        "status":"FUTURE_PROVISIONAL_BOUT_STRUCTURE_AUDITED",
        "scope":{"as_of":"2026-10-10",
                 "start":START,"end":END,
                 "source_release_excluded":FROZEN_RELEASE,
                 "public_candidate_site_months":len(candidates),
                 "provisional_plot_files_with_MD5_validated":len(files),
                 "source_release_labels":selection["release_labels"]},
        "structure":event_structure(rows),
        "W_B_opened":False,"capture_records_opened":False,
        "individual_or_taxon_values_opened":False,"MNKA_opened":False,
        "independent_ecological_confirmation":False,
        "next_gate":"Check exact event/nightuid and tag history non-overlap against RELEASE-2026 and locked target taxonomy; m>=5 and trap saturation effect-blind; do not open future W/B if those fail.",
        "interpretation":"Provisional plot structure is not enough to claim response support; future release may revise it, and three-night bout counts do not imply tagged repeat-supported individuals."
    }


def main():
    result=run()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
