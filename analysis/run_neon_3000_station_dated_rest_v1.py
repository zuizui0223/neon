#!/usr/bin/env python3
"""Date-effective 3000 actual NEON mammal trap coordinate SOURCE audit.

Canonical NEON REST history source for 3000 original stations. Does not rescue
or override the prior failed GraphQL/REST five-name equivalence test.
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
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_3000_station_dated_rest_v1.json"
FIVE=ROOT/"results/neon_dated_five_anchor_feasibility_receipt_20261021.json"
CURRENT_SOURCE_PHASE="PRECHECK_EXISTING_FIVE_ANCHOR_RECEIPT"


def _phase(value:str)->None:
    global CURRENT_SOURCE_PHASE
    CURRENT_SOURCE_PHASE=value


def require(ok:bool,why:str):
    if not ok:
        raise RuntimeError("NEON_3000_HISTORIC_SOURCE_STOP: "+why)


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

    # A NEW source-only route after, and NOT rescuing, the old five-name
    # GraphQL/REST preflight STOP. REST was independently valid for 150
    # original anchors: use official REST for the entire literal roster.
    from concurrent.futures import ThreadPoolExecutor
    from collections import Counter
    import urllib.error
    import time

    def get_one(job):
        full, key = job
        url = BASE+"locations/"+quote(full,safe="")+"?history=true"
        for attempt in range(4):
            try:
                raw=_request_json(url,token=token)
                obj=raw.get("data") if isinstance(raw,dict) else None
                if not isinstance(obj,dict) or obj.get("locationName")!=full:
                    raise RuntimeError("Official REST named location identity mismatch")
                history=obj.get("locationHistory")
                if not isinstance(history,list) or not history or any(not isinstance(r,dict) for r in history):
                    return key,None,"NO_VALID_HISTORY",None
                return key,obj,None,digest(raw)
            except urllib.error.HTTPError as exc:
                if exc.code in (400,404):
                    return key,None,"NO_OFFICIAL_NAMED_LOCATION",None
                if exc.code in (429,500,502,503,504) and attempt<3:
                    time.sleep(2**attempt)
                    continue
                raise RuntimeError("REST history HTTP source not accessible") from None
            except (urllib.error.URLError,TimeoutError,OSError):
                if attempt<3:
                    time.sleep(2**attempt)
                    continue
                raise RuntimeError("REST history transport retries exhausted") from None
        raise RuntimeError("Source retry exhausted")

    _phase("REST_FULL_3000_LOCATION_HISTORIES")
    source_docs={}
    rest_response_hashes=[]
    source_missing=Counter()
    with ThreadPoolExecutor(max_workers=8) as pool:
        for key,doc,reason,sha in pool.map(
            get_one, [(name,private_names[name]) for name in all_names]
        ):
            source_docs[key]=doc
            if reason is not None:source_missing[reason]+=1
            if sha is not None:rest_response_hashes.append(sha)
    require(len(source_docs)==3000,"Full authoritative REST keys not retained")

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
            "historical_position_source":"Canonical NEON REST locations endpoint, history=true",
            "concurrent_REST_workers":8,
            "requested_original_station_names":len(all_names),
            "returned_named_source_documents":len(rest_response_hashes),
            "missing_source_documents_by_class":dict(sorted(source_missing.items())),
            "REST_full_response_digest_set":digest(sorted(rest_response_hashes)),
            "failed_previous_GraphQL_REST_source_preflight_stays_STOP":True,
            "first_150_dates_reverified_against_frozen_REST_source":True,
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
        result={
            "schema":"neon.original_3000_REST_historical_locations.v1",
            "status":"STOP_OFFICIAL_REST_SOURCE_OR_ORIGINAL_DENOMINATOR",
            "failure_stage":CURRENT_SOURCE_PHASE if CURRENT_SOURCE_PHASE in
                {"PRECHECK_EXISTING_FIVE_ANCHOR_RECEIPT","ORIGINAL_MAMMAL_SOURCE_RECONSTRUCTION",
                 "BUILD_EXACT_3000_SOURCE_NAMES","REST_FULL_3000_LOCATION_HISTORIES",
                 "VERIFY_FIVE_ORIGINAL_CAPTURE_DAYS","ALL_STATION_DATE_COVERAGE",
                 "FINAL_AGGREGATE_SOURCE_RECEIPT"} else "UNCLASSIFIED",
            "error_class":type(exc).__name__,
            "previous_GraphQL_REST_preflight_STOP_preserved":True,
            "animal_site_station_dates_URLs_coordinates_or_tag_ids_exported":False,
            "ecological_habitat_or_detection_effect_estimated":False,
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
                   encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return code


if __name__=="__main__":
    raise SystemExit(main())
