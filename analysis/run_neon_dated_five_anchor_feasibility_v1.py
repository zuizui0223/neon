#!/usr/bin/env python3
"""Real source: date-validity of five NEON mammal trap-location histories.

Preserves the 58 frozen genus spatial-recurrence units/30 plots/14 physical
sites and their original 3+3 capture dates; queries 150 literal source-named
locationHistory arrays. No canopy sampling, genus occupancy by habitat,
movement/density ecological effect or site coordinate exported.
"""
from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import json
import os
from pathlib import Path
from urllib.parse import quote
import urllib.error

from analysis.run_neon_habitat_source_link_v1 import (
    reconstruct, _request_json, BASE, TOKEN_ENV, digest
)
from analysis.audit_neon_dated_five_anchor_feasibility_v1 import (
    ANCHORS,select_original_location_history,summarize_five_anchor_date_history,
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_dated_five_anchor_feasibility_v1.json"
ORIGINAL_FIVE=ROOT/"results/neon_five_anchor_chm_source_receipt_20261020.json"


def require(ok:bool,msg:str)->None:
    if not ok:
        raise RuntimeError("FROZEN_ORIGINAL_SOURCE_DATE_AUDIT_STOP: "+msg)


def fetch_one(
    key: tuple[str,str], anchor:str, base_name:str, token:str
) -> tuple[tuple[str,str,str],list[dict]|None,str|None,str|None]:
    full=base_name+"."+anchor
    try:
        payload=_request_json(
            BASE+"locations/"+quote(full,safe="")+"?history=true",
            token=token
        )
        records=select_original_location_history(payload,full)
        return (key[0],key[1],anchor),records,digest(payload),None
    except urllib.error.HTTPError as exc:
        return (key[0],key[1],anchor),None,None,"HTTP_STATUS_"+str(exc.code)
    except ValueError:
        return (key[0],key[1],anchor),None,None,"LOCATION_HISTORY_OR_SOURCE_SCHEMA_ERROR"
    except Exception:
        return (key[0],key[1],anchor),None,None,"SOURCE_TRANSPORT_OR_UNKNOWN_ERROR"


def run()->dict:
    token=os.environ.get(TOKEN_ENV,"").strip()
    require(bool(token),"immutable original NEON source authorization unavailable")
    source_five=json.loads(ORIGINAL_FIVE.read_text(encoding="utf-8"))
    require(
        source_five["status"]=="FIVE_NAMED_CHM_REFERENCE_ANCHORS_AUDITED_NOT_HABITAT_EFFECT"
        and source_five["original_plots"]==30
        and source_five["original_anchor_attempts"]==150
        and source_five["valid_anchors"]==150
        and source_five["earlier_E5_30_valid_19_zero_reproduced"],
        "original 150 CHM reference anchor source fixture has changed",
    )

    units,cohort,sites,names,source=reconstruct(token)
    require((len(units),len(cohort),len(sites))==(58,30,14),
            "original 58/30/14 NEON source cohort drifted")
    require(all(len(names.get(key,set()))==1 for key in cohort),
            "original plot base namedLocation is ambiguous")
    require(tuple(ANCHORS)==("A1","A10","J1","J10","E5"),
            "frozen literal named station list changed")
    # Fail closed if source_event_support has not preserved *actual* dates.
    for unit in units:
        aa=unit.get("capture_dates_A")
        bb=unit.get("capture_dates_B")
        require(
            isinstance(aa,(tuple,list)) and isinstance(bb,(tuple,list))
            and len(aa)==3 and len(bb)==3,
            "original three plus three source capture dates not available",
        )

    jobs=[
        (key,anchor,next(iter(names[key])))
        for key in sorted(cohort) for anchor in ANCHORS
    ]
    require(len(jobs)==150,"original five named stations×30 plots were changed")
    history={}
    sha256=[]
    errors=Counter()
    with ThreadPoolExecutor(max_workers=6) as ex:
        for key,records,sha,error in ex.map(
            lambda j: fetch_one(j[0],j[1],j[2],token),jobs
        ):
            history[key]=records
            if sha is not None:
                sha256.append(sha)
            if error is not None:
                errors[error]+=1
    result=summarize_five_anchor_date_history(
        units,history,
        expected_pairs=58,expected_sites=14,expected_plots=30,
        min_pairs=40,min_sites=8,min_plots=20,
    )
    require(result["fixed_original_anchor_date_attempts"]==1740,
            "original 58×6×5 source date denominator drifted")
    return {
        **result,
        "source_provenance":{
            "NEON_capture_release":"RELEASE-2026",
            "live_location_API_not_pinned_to_capture_release":True,
            "UTC_retrieved_at":datetime.now(timezone.utc).isoformat(),
            "original_source_checksum_verified":True,
            "source_capture_cohort":source,
            "original_captured_genus_spatial_test_unchanged":True,
            "original_150_location_names_queried":len(jobs),
            "history_payloads_returned":len(sha256),
            "source_document_SHA256_digest_set":digest(sorted(sha256)),
            "source_query_failure_categories":dict(sorted(errors.items())),
            "captured_animal_site_plot_station_date_or_coordinates_exported":False,
        },
        "decision":{
            "safe_to_expand_to_100_named_historical_stations_if_gate_passes":result["historical_capture_day_location_gate_passed"],
            "this_is_environmental_source_feasibility_only":True,
            "measured_CHM_is_2022_2024_not_historical_2015_2026":True,
            "all_four_documented_historical_geolocation_issue_plots_retained":True,
            "no_habitat_selection_detection_or_competition_effect_estimated":True,
            "no_density_W_B_effect_reopened":True,
            "MOSA_W_B_effects":"SEALED",
            "next":(
                "If source date-history coverage passes, retrieve full 100 exact named stations per original plot and evaluate time-specific CRS and geoNEON uncertainty as pre-effect source QA; do not fit habitat on E5 current positions."
                if result["historical_capture_day_location_gate_passed"] else
                "STOP historic trap-habitat linking on these live location-history records; do not substitute current station coordinates and do not retrofit positive genus ecology. Seek authoritative historical location archive or independent compatible habitat/detection source."
            ),
        },
    }


def main()->int:
    try:
        report=run()
        exit_code=0  # A source-valid scientific STOP is a valid result.
    except Exception as exc:
        report={
            "schema":"neon.historical_location.five_anchor_date_coverage.v1",
            "status":"STOP_SOURCE_OR_HISTORICAL_LOCATION_FEASIBILITY_RUN",
            "failure_class":type(exc).__name__,
            "source_specific_capture_dates_or_station_coordinates_exported":False,
            "habitat_or_genus_spatial_effects_opened":False,
        }
        exit_code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))
    return exit_code


if __name__=="__main__":
    raise SystemExit(main())
