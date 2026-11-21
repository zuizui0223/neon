#!/usr/bin/env python3
"""Source-only NEON macro biogeographic inclusion across all eligible seasons.

Original release and structural supports are checksum verified; current
public NEON /sites metadata supplies field domain, core/gradient site type and
approximate site latitude (NOT mammal station coordinates). No species/trap
habitat, existing Z result, W/B model or ecological effect is accessed.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from analysis.audit_multiscale_density_mnka_variation_v1 import _taxonomy
from analysis.audit_neon_crossseason_genus_support_v1 import source_event_support
from analysis.run_neon_crossseason_direct_site_null_calibration_v1 import (
    verified_support_gate,SOURCE_SUPPORT,
)
from analysis.run_multiscale_density_estimability_release2026_v3 import (
    PRODUCT,RELEASE,START,END,PRODUCT_URL,QUERY_URL,TOKEN_ENV,
    MAX_DOWNLOAD_WORKERS,_request_json,_site_codes,_inventory,
    _download_many,_read_plot_rows,_read_trap_rows,_candidate_nights,
)
from analysis.neon_macro_site_selection_v1 import (
    site_metadata_index,audit_geographic_selection,
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_macro_biogeographic_selection_v1.json"
NEON_SITES="https://data.neonscience.org/api/v0/sites?release=RELEASE-2026"

def must(x:bool,reason:str):
    if not x:raise RuntimeError("NEON_MACRO_BIOGEOGRAPHY_SOURCE_STOP: "+reason)

def run()->dict:
    token=os.environ.get(TOKEN_ENV,"").strip()
    must(bool(token),"original release source authorization unavailable")
    must((PRODUCT,RELEASE,START,END)==
         ("DP1.10072.001","RELEASE-2026","2015-04","2026-09"),
         "original release changed")

    sites=_site_codes(_request_json(PRODUCT_URL))
    inventory=_inventory(_request_json(QUERY_URL,token=token,body={
        "productCode":PRODUCT,"siteCodes":sites,"startDateMonth":START,
        "endDateMonth":END,"release":RELEASE,
        "package":"basic","includeProvisional":False
    }))
    pf=[x for x in inventory if "mam_perplotnight" in x["name"]]
    must(len(inventory)==3547 and len(pf)==1773,
         "published immutable source inventory changed")
    plots=[]
    for meta,raw in zip(pf,_download_many(pf,token,
                           max_workers=MAX_DOWNLOAD_WORKERS)):
        plots.extend(_read_plot_rows(raw,meta["site"],meta["month"]))
    nights,months=_candidate_nights(plots)
    tf=[x for x in inventory if "mam_pertrapnight" in x["name"]
        and (x["site"],x["month"]) in months]
    must(len(tf)==1707,"published original trap-file inventory changed")
    traps=[]
    for meta,raw in zip(tf,_download_many(tf,token,
                           max_workers=MAX_DOWNLOAD_WORKERS)):
        for row in _read_trap_rows(raw,nights):
            row["_site"]=meta["site"]
            traps.append(row)
    must((len(plots),len(traps))==(21363,1505827),
         "original source canonical row counts changed")

    units=[]
    support=source_event_support(plots,traps,_taxonomy()[1],
                                 internal_units=units)
    frozen=json.loads(SOURCE_SUPPORT.read_text(encoding="utf-8"))
    verified_support_gate(support,frozen)
    must((len(units),len({u["site"] for u in units}))==(58,14),
         "original 58-unit / 14-site source support changed")

    payload=_request_json(NEON_SITES)
    documented=payload.get("data")
    must(isinstance(documented,list),
         "official source site/biogeographic metadata missing")
    original_site_codes={str(r.get("_site") or "") for r in plots}
    # Site metadata for the *original released mammal source population*,
    # never mix in unrelated aquatic sites that did not support this product.
    filtered=[row for row in documented
              if row.get("siteCode") in original_site_codes]
    must(bool(filtered),"no original source sites in official metadata")
    meta=site_metadata_index(filtered)
    audit=audit_geographic_selection(plots,traps,units,meta)
    source_hash=hashlib.sha256(json.dumps(
        documented,sort_keys=True,separators=(",",":"),ensure_ascii=False
    ).encode()).hexdigest()
    return {
        **audit,
        "provenance":{
            "original_neon_release":RELEASE,
            "original_checksum_pinned_manifest_files":len(inventory),
            "downloaded_verified_source_files":len(pf)+len(tf),
            "source_plot_rows":len(plots),
            "source_trap_rows":len(traps),
            "official_NEON_sites_API":"GET /api/v0/sites?release=RELEASE-2026",
            "official_metadata_SHA256":source_hash,
            "source_site_metadata_rows_for_mammal_source":len(filtered),
            "same_original_58_eligible_units_30_plots_14_sites":True,
            "taxonomy_genus_source_reconstructed_not_promoted_to_species":True,
            "source_site_or_station_coordinates_exported":False,
        },
        "scientific_decision":{
            "one_unified_macroecology_research_programme":True,
            "biogeographic_sample_selection_described_not_ecological_effect":True,
            "positive_conditional_Neon_recurrence_unmodified":True,
            "original_density_5of8_vs_6_guard_still_failed":True,
            "observed_12of58_direct_coupling_STOP_unchanged":True,
            "all_sites_mechanistic_macro_extrapolation_authorized":False,
            "next":"Audit independent time-matched seasonal climate or ecosystem domain coverage and prospectively independent recurrence cohorts; do not fit post hoc habitat-selected positive historical effects.",
        },
    }

def main()->int:
    try:
        out=run()
        code=0
    except Exception as exc:
        out={
            "schema":"neon.unified_macro.biogeographic_selection_source_only.v1",
            "status":"STOP_BIOGEOGRAPHIC_SOURCE_OR_INCLUSION_AUDIT",
            "error_class":type(exc).__name__,
            "original_58_conditioned_ecological_results_unchanged":True,
            "source_site_or_individual_ids_exported":False,
            "ecological_biome_or_climate_effect_computed":False,
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",
                   encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return code

if __name__=="__main__":
    raise SystemExit(main())
