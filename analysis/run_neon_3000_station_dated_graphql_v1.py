#!/usr/bin/env python3
"""Date-effective 3000 actual NEON mammal trap coordinate SOURCE audit.

Public NEON findLocations GraphQL batches (<=500) are REST-equivalence
checked on five original source names before using full source data.
No 10m-grid coordinate synthesis, no genus × canopy or detection/competition
model, no retrospective habitat exposure from current 2022–24 imagery.

All real source site, plot, station, date, coordinates and sample IDs stay
in process memory. Released artifact contains only source aggregate counts,
location-document digests and reason categories.
"""
from __future__ import annotations

from datetime import datetime,timezone
from collections import Counter
import json
import os
from pathlib import Path
from urllib.parse import quote

from analysis.run_neon_habitat_source_link_v1 import (
    reconstruct, _request_json, BASE, TOKEN_ENV, digest
)
from analysis.neon_dated_station_location_v1 import station_labels_10x10
from analysis.neon_graphql_dated_station_source_v1 import (
    GRAPHQL_QUERY,batch_names,parse_graphql_locations,
    canonical_station_history_for_comparison,
    summarize_full_station_dated_coverage,
)
from analysis.audit_neon_dated_five_anchor_feasibility_v1 import (
    summarize_five_anchor_date_history
)
from analysis.audit_neon_lineage_environmental_source_coverage_v1 import (
    GEO_LOCATION_ISSUE_GRIDS
)
from analysis.neon_graphql_source_diagnostic_v1 import (
    source_stop_receipt, safe_rest_graphql_diff_groups,
    summarize_preflight_diff_groups, SourcePreflightMismatch,
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_3000_station_dated_graphql_v1.json"
FIVE=ROOT/"results/neon_dated_five_anchor_feasibility_receipt_20261021.json"
GRAPHQL="https://data.neonscience.org/graphql"
MAX_BATCH=500
COMPARE_REST=5
CURRENT_SOURCE_PHASE="PRECHECK_EXISTING_FIVE_ANCHOR_RECEIPT"


def _phase(value:str)->None:
    global CURRENT_SOURCE_PHASE
    CURRENT_SOURCE_PHASE=value


def require(ok:bool,why:str):
    if not ok:
        raise RuntimeError("NEON_3000_HISTORIC_SOURCE_STOP: "+why)


def _gql(names:list[str],token:str)->dict:
    require(0<len(names)<=MAX_BATCH,"invalid official GraphQL batch size")
    raw=_request_json(
        GRAPHQL,token=token,
        body={
            "query":GRAPHQL_QUERY,
            "variables":{"query":{"locationNames":names}},
        },
    )
    if raw.get("errors"):
        raise RuntimeError("Official GraphQL schema or server returned errors")
    return raw


def run()->dict:
    token=os.environ.get(TOKEN_ENV,"").strip()
    require(bool(token),"valid NEON source authorization required")
    five=json.loads(FIVE.read_text(encoding="utf-8"))
    require(five["status"]=="HISTORICAL_FIVE_ANCHOR_CAPTURE_DATE_SOURCE_GO"
            and five["anchor_date_valid"]==1740
            and five["all_five_anchors_valid_for_all_six_original_dates_pairs"]==58
            and five["sites_with_at_least_one_fully_valid_plot"]==14
            and five["plots_fully_valid_for_all_included_capture_days"]==30,
            "frozen five-location original capture day gate has changed")
    _phase("ORIGINAL_MAMMAL_SOURCE_RECONSTRUCTION")
    units,cohort,sites,names,source=reconstruct(token)
    require((len(units),len(cohort),len(sites))==(58,30,14),
            "original source population no longer 58/30/14")
    require(all(len(names.get(p,set()))==1 for p in cohort),
            "one source namedLocation required for each original plot")
    stations=station_labels_10x10()
    require(len(stations)==100 and stations[0]=="A1" and stations[-1]=="J10",
            "source canonical 100 station roster drifted")

    # Keep plot-station source names and source keys in ephemeral process
    # memory only. Never print IDs in errors, logs or result artifacts.
    _phase("BUILD_EXACT_3000_SOURCE_NAMES")
    private_names={
        next(iter(names[plot]))+"."+station:(plot[0],plot[1],station)
        for plot in sorted(cohort) for station in stations
    }
    require(len(private_names)==3000,
            "The original source named 30×100 stations nonuniquely")
    all_names=sorted(private_names)

    # Equivalence preflight against the known-good original REST history.
    original_five=all_names[:COMPARE_REST]
    _phase("GRAPHQL_FIVE_NAME_PREFLIGHT")
    check_response=_gql(original_five,token)
    _phase("GRAPHQL_FIVE_NAME_PARSE")
    check_docs=parse_graphql_locations(check_response,original_five)
    require(len(check_docs)==COMPARE_REST,
            "GraphQL lacks a complete verified five-name source preflight")
    _phase("REST_GRAPHQL_HISTORY_EQUIVALENCE")
    REST_sha=[]
    safe_differences=[]
    for name in original_five:
        rest=_request_json(BASE+"locations/"+quote(name,safe="")+"?history=true",
                           token=token)
        rest_obj=rest.get("data")
        require(isinstance(rest_obj,dict),
                "Original REST source location metadata invalid")
        details=safe_rest_graphql_diff_groups(rest_obj,check_docs[name])
        # A normalization/shape issue is not license to bypass original
        # source equality. It becomes a SOURCE STOP with aggregate groups.
        try:
            equivalent=(
                canonical_station_history_for_comparison(rest_obj)==
                canonical_station_history_for_comparison(check_docs[name])
            )
        except (ValueError,TypeError,KeyError,OverflowError):
            equivalent=False
            details=sorted(set(details)|{"CANONICAL_COMPARISON_PARSE_ERROR"})
        if not equivalent and not details:
            details=["OTHER_CANONICAL_FIELDS"]
        safe_differences.append(details)
        REST_sha.append(digest(rest))
    if any(safe_differences):
        raise SourcePreflightMismatch(
            summarize_preflight_diff_groups(safe_differences)
        )

    _phase("GRAPHQL_FULL_3000_BATCHES")
    source_docs={}
    graphql_response_hashes=[]
    n_returned=0
    n_batches=0
    for group in batch_names(all_names,MAX_BATCH):
        payload=_gql(group,token)
        docs=parse_graphql_locations(payload,group)
        n_batches+=1
        n_returned+=len(docs)
        graphql_response_hashes.append(digest(payload))
        for name in group:
            key=private_names[name]
            source_docs[key]=docs.get(name)
    require(n_batches==6 and len(source_docs)==3000,
            "Original six official GraphQL batches did not cover full source")

    # The existing source-dated five-anchor test MUST independently
    # reproduce 1740/1740 from the multi-fetch metadata before any
    # 100-station source georeferencing conclusion is released.
    original_five_names=("A1","A10","J1","J10","E5")
    five_histories={
        (site,plot,station):(
            doc.get("locationHistory") if doc is not None else None
        )
        for (site,plot,station),doc in source_docs.items()
        if station in original_five_names
    }
    _phase("VERIFY_FIVE_ORIGINAL_CAPTURE_DAYS")
    five_recheck=summarize_five_anchor_date_history(
        units,five_histories,
        expected_pairs=58,expected_sites=14,expected_plots=30,
        min_pairs=40,min_sites=8,min_plots=20,
    )
    require(five_recheck["anchor_date_valid"]==1740
            and five_recheck["all_five_anchors_valid_for_all_six_original_dates_pairs"]==58,
            "Original REST 150-anchor historical source not reproduced from GraphQL")

    flagged={
        (site,plot)
        for site,plot in cohort
        if plot in GEO_LOCATION_ISSUE_GRIDS
    }
    require(len(flagged)==4,"Published four-grid geolocation source issue roster changed")

    _phase("ALL_STATION_DATE_COVERAGE")
    audit=summarize_full_station_dated_coverage(
        units,source_docs,expected_pairs=58,expected_sites=14,
        expected_plots=30,min_pairs=40,min_sites=8,min_plots=20,
        historically_flagged_plots=flagged,
    )
    require(audit["original_source_plots_geolocation_issue_count"]==4
            and audit["fixed_original_station_date_attempts"]==34800,
            "Canonical source original 34,800-day geolocation denominator drifted")
    _phase("FINAL_AGGREGATE_SOURCE_RECEIPT")
    return {
        **audit,
        "source_provenance":{
            "original_mammal_release":"RELEASE-2026",
            "live_location_API_is_not_versioned_to_CAPTURE_release":True,
            "live_location_retrieved_at_UTC":datetime.now(timezone.utc).isoformat(),
            "original_captured_source":source,
            "original_genus_template_cohort_58_30_14_unchanged":True,
            "batch_API":"NEON official GraphQL findLocations(LocationQuery.locationNames)",
            "GRAPHQL_max_names_allowed_by_docs":1000,
            "max_names_per_actual_request":MAX_BATCH,
            "GraphQL_batches_checked":n_batches,
            "requested_original_station_names":len(all_names),
            "returned_named_source_documents":n_returned,
            "first_five_source_names_verified_against_REST_histories":COMPARE_REST,
            "REST_equivalence_probe_source_digest_set":digest(sorted(REST_sha)),
            "GraphQL_full_response_digest_set":digest(sorted(graphql_response_hashes)),
            "first_150_dates_reverified_against_original_REST_history":True,
            "raw_source_site_and_station_names_and_coords_exported":False,
        },
        "science_scope":{
            "historical_station_source_coverage_passed":audit["source_date_and_geographic_coverage_gate_passed"],
            "historical_station_positions_not_inferred_from_five_anchors":True,
            "geoNEON_coordinate_uncertainty_is_rule_based_not_95percent_bounds":True,
            "2022_2024_CHM_does_not_prove_habitat_at_all_2015_2026_events":True,
            "all_100_station_CHM_heights_sampled":False,
            "genus_habitat_detection_or_competition_effect_computed":False,
            "original_corrected_seasonal_recurrence_inference_unchanged":True,
            "previous_density_6of8_genus_rule":"FAILED_5_OF_8",
            "MOSA_W_B_effects":"SEALED",
            "next":(
                "Georeferenced 100-station source support met. Map only direct/date-valid positions to CRC-checked CHM and explicitly quantify time mismatch before any habitat/detection inference."
                if audit["source_date_and_geographic_coverage_gate_passed"] else
                "STOP trap-specific habitat mechanism inference: authoritative historical CRS, station uncertainty and position coverage do not meet frozen thresholds. Do not use contemporary E5 or extrapolate 5 anchors as complete grids."
            ),
        },
    }


def main()->int:
    try:
        result=run()
        code=0 # A real scientific source STOP still produces a valid receipt.
    except Exception as exc:
        result=source_stop_receipt(CURRENT_SOURCE_PHASE,exc)
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
                   encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return code


if __name__=="__main__":
    raise SystemExit(main())
