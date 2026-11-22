#!/usr/bin/env python3
"""NEON RELEASE-2026 independent cross-season genus niche-template support.

Only capture sample keys, complete three-night efforts, original source genus
and tag uniqueness enter. No inter-season genus×trap intersection or spatial
recurrence outcomes are computed by this PRE-EFFECT runner.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from analysis.run_multiscale_density_estimability_release2026_v3 import (
    PRODUCT, RELEASE, START, END, PRODUCT_URL, QUERY_URL, TOKEN_ENV,
    MAX_DOWNLOAD_WORKERS, _request_json, _site_codes, _inventory,
    _download_many, _read_plot_rows, _read_trap_rows, _candidate_nights,
)
from analysis.audit_multiscale_density_mnka_variation_v1 import _taxonomy
from analysis.audit_neon_crossseason_genus_support_v1 import source_event_support

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_crossseason_genus_template_support_v1.json"
ORIGINAL=ROOT/"results/neon_u_adjusted_fixed_total_predictor_receipt_20261019.json"


def require(condition: bool, msg: str) -> None:
    if not condition:
        raise RuntimeError("SOURCE-INVARIANT STOP: "+msg)


def run() -> dict:
    token=os.environ.get(TOKEN_ENV,"").strip()
    if not token:
        raise RuntimeError("Original RELEASE-2026 source token unavailable")
    prior=json.loads(ORIGINAL.read_text(encoding="utf-8"))
    source=prior["source_invariants"]
    require(RELEASE=="RELEASE-2026" and START=="2015-04" and END=="2026-09",
            "not original pinned release and date range")
    require(source["original_source_target_sessions"]==1536 and
            source["original_target_histories"]==47360,
            "original historical NEON source support changed")

    all_target,genus_by_taxon,_=_taxonomy()
    require(bool(all_target) and "PEMA" in all_target,
            "official target taxonomy missing original capture taxa")
    sites=_site_codes(_request_json(PRODUCT_URL))
    inventory=_inventory(_request_json(
        QUERY_URL,token=token,body={
            "productCode":PRODUCT,"siteCodes":sites,
            "startDateMonth":START,"endDateMonth":END,
            "release":RELEASE,"package":"basic","includeProvisional":False,
        }
    ))
    plot_files=[r for r in inventory if "mam_perplotnight" in r["name"]]
    require(len(inventory)==3547 and len(plot_files)==1773,
            "original checksum-pinned structural file inventory changed")

    plots=[]
    for meta,raw in zip(plot_files,_download_many(
        plot_files,token,max_workers=MAX_DOWNLOAD_WORKERS
    )):
        plots.extend(_read_plot_rows(raw,meta["site"],meta["month"]))
    nights,site_months=_candidate_nights(plots)
    require(bool(nights),"Original NEON three-night event support missing")
    trap_files=[r for r in inventory
                if "mam_pertrapnight" in r["name"]
                and (r["site"],r["month"]) in site_months]
    require(len(trap_files)==1707,
            "original source trap-file denominator changed")
    traps=[]
    for meta,raw in zip(trap_files,_download_many(
        trap_files,token,max_workers=MAX_DOWNLOAD_WORKERS
    )):
        for row in _read_trap_rows(raw,nights):
            row["_site"]=meta["site"]
            traps.append(row)

    support=source_event_support(plots,traps,genus_by_taxon)
    return {
        **support,
        "original_NEON_source_provenance":{
            "release":RELEASE,"product":PRODUCT,
            "start":START,"end":END,
            "source_files_MD5_and_size_verified":len(inventory),
            "perplotnight_files_MD5_verified":len(plot_files),
            "pertrapnight_files_MD5_verified":len(trap_files),
            "target_taxonomy_ids_in_public_lookup":len(all_target),
            "valid_candidate_nightUIDs":len(nights),
            "source_plot_rows_loaded":len(plots),
            "source_trap_rows_loaded":len(traps),
            "same_original_source_as_historical_F_C_U_predictor_audits":True,
        },
        "study_claim":{
            "study":"NEON genus-level across-season template occurrence, distinct from source San Jacinto species-level signal",
            "precommit":"docs/NEON_CROSS_SEASON_GENUS_SPATIAL_TEMPLATE_DESIGN_20261019.md",
            "San_Jacinto_positive_prior_seen_before_design":True,
            "this_support_not_null_model":True,
            "individual_turnover_exclusion":True,
            "source_canonical_genus_may_group_cryptic_species":True,
            "mammal_genus_not_equivalent_to_species_ecology":True,
            "W_B_or_density_spatial_results_reused":False,
            "original_multigenus_density_claim":"FAILED_5_OF_8",
            "original_F_C_fixed_total_comparisons":"QUALIFIER_CONSERVATIVE_0_SAME_SEASON_PAIRS",
            "MOSA_effects":"SEALED",
        },
    }


def main() -> int:
    try:
        result=run()
    except Exception as exc:
        result={
            "schema":"neon.crossseason_genus_individual_replacement_support.v1",
            "status":"STOP_SOURCE_OR_STRUCTURAL_NIGHT_EFFORT",
            "diagnostic":str(exc)[:600],
            "source_genus_trap_occupancy_A_B_calculated":False,
            "crossseason_spatial_overlap_opened":False,
            "W_B_density_effects_opened":False,
        }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
                   encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    # Fail CI on source error; a valid structural STOP is a scientific
    # result and can succeed as a workflow while keeping spatial seal.
    return 3 if result["status"]=="STOP_SOURCE_OR_STRUCTURAL_NIGHT_EFFORT" else 0


if __name__=="__main__":
    raise SystemExit(main())
