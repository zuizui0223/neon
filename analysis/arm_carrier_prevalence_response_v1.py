from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"validation"/"carrier_prevalence_mechanism_v1"
PROTOCOL=BASE/"protocol_v1.json"
ROSTER=BASE/"fresh_roster_lock_v1.json"
TRAIT_LOCK=BASE/"target_pool_traits_lock_v1.json"
TRAIT_DATA=ROOT/"data"/"derived"/"combine_target_pool_traits_v1.csv"
RESPONSE_PROTOCOL=BASE/"response_protocol_v1.json"
AUTH=BASE/"response_authorization_v1.json"
RUNNER=ROOT/"analysis"/"run_carrier_prevalence_response_once_v1.py"
NULL=ROOT/"analysis"/"count_conditioned_carrier_null_v1.py"
ROSTER_IMPL=ROOT/"analysis"/"capture_carrier_prevalence_fresh_roster_v1.py"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def canonical_sha(x):
    return hashlib.sha256(
        json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
    ).hexdigest()

def main():
    required=[PROTOCOL,ROSTER,TRAIT_LOCK,TRAIT_DATA,RUNNER,NULL,ROSTER_IMPL]
    missing=[str(p) for p in required if not p.exists()]
    if missing:
        raise RuntimeError(f"cannot arm response; missing {missing}")

    protocol=load(PROTOCOL)
    roster=load(ROSTER)
    traits=load(TRAIT_LOCK)

    if roster.get("programme")!=protocol["programme"]:
        raise RuntimeError("roster programme mismatch")
    if roster.get("response_endpoint_requests")!=0 or roster.get("biological_response_bytes_opened")!=0:
        raise RuntimeError("fresh roster is not response-blind")
    if traits.get("response_endpoint_requests")!=0 or traits.get("biological_response_bytes_opened")!=0:
        raise RuntimeError("trait pool is not response-blind")
    if roster["taxonomy_metadata_fingerprint"]!=traits["neon_taxonomy_fingerprint"]:
        raise RuntimeError("roster and trait pool taxonomy fingerprints differ")

    sites=list(roster["selected_site_codes"])
    min_sites=int(protocol["aggregate_test"]["minimum_scored_sites"])
    if len(sites)<min_sites:
        raise RuntimeError(
            f"fresh denominator has only {len(sites)} sites; minimum is {min_sites}; "
            "do not open biological response"
        )

    rp={
        "schema":"neon.carrier_prevalence_mechanism.response_protocol.v1",
        "programme":protocol["programme"],
        "state":"frozen_before_biological_response_access",
        "fresh_roster_fingerprint":roster["fingerprint"],
        "target_pool_traits_fingerprint":traits["fingerprint"],
        "fixed_site_codes":sites,
        "taxonomy_metadata_fingerprint":roster["taxonomy_metadata_fingerprint"],
        "expected_target_taxon_count":roster["eligible_target_taxon_count"],
        "authentication":{
            "token_environment_variable":"NEON_API_TOKEN",
            "token_header":"X-API-Token",
            "token_must_not_be_committed":True
        },
        "response_query":{
            "method":"POST",
            "endpoint":"https://data.neonscience.org/api/v0/data/query",
            "body":{
                "productCode":"DP1.10072.001",
                "siteCodes":sites,
                "startDateMonth":"2010-01",
                "endDateMonth":"2026-09",
                "release":"RELEASE-2026",
                "package":"basic",
                "includeProvisional":False
            },
            "maximum_authenticated_query_requests":1,
            "no_fallback_release":True,
            "no_fallback_package":True
        },
        "file_selection":{
            "table":"mam_pertrapnight",
            "suffix":".csv",
            "require_md5":True,
            "verify_size":True,
            "verify_md5":True,
            "no_other_tables":True
        },
        "required_columns":["namedLocation","trapCoordinate","trapStatus","taxonID"],
        "capture_semantics":{
            "normalized_status":"strip and lowercase trapStatus",
            "positive_if_all":[
                "status contains capture",
                "status does not contain no capture",
                "taxonID belongs to frozen target set"
            ],
            "node_key":"namedLocation + '.' + trapCoordinate"
        },
        "uncertain_coordinate_policy":{
            "x_coordinate_if":"uppercase trapCoordinate contains X",
            "action":"exclude row prospectively from all spatial metrics; count excluded target-positive rows and distinct X node labels"
        },
        "registry_integrity":{
            "unknown_non_x_positive_node":"response-consumed site STOP",
            "registry_repair_allowed":False,
            "site_replacement_allowed":False
        },
        "site_estimability":protocol["site_estimability"],
        "count_conditioned_null":protocol["count_conditioned_null"],
        "aggregate_test":protocol["aggregate_test"],
        "secondary_predeclared":protocol["secondary_predeclared"],
        "secondary_grid_conditioned_null":protocol["secondary_grid_conditioned_null"],
        "integrity":{
            "biological_response_endpoint_requests_at_freeze":0,
            "biological_response_bytes_opened_at_freeze":0,
            "model_fits":0,
            "rerun_after_authenticated_query_starts":False,
            "post_response_metric_changes":False,
            "post_response_site_changes":False
        }
    }
    rp["fingerprint"]=canonical_sha(rp)
    RESPONSE_PROTOCOL.write_text(json.dumps(rp,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    hashes={
        "protocol_v1.json":sha_file(PROTOCOL),
        "fresh_roster_lock_v1.json":sha_file(ROSTER),
        "target_pool_traits_lock_v1.json":sha_file(TRAIT_LOCK),
        "combine_target_pool_traits_v1.csv":sha_file(TRAIT_DATA),
        "response_protocol_v1.json":sha_file(RESPONSE_PROTOCOL),
        "run_carrier_prevalence_response_once_v1.py":sha_file(RUNNER),
        "count_conditioned_carrier_null_v1.py":sha_file(NULL),
        "capture_carrier_prevalence_fresh_roster_v1.py":sha_file(ROSTER_IMPL)
    }
    auth={
        "schema":"neon.carrier_prevalence_mechanism.response_authorization.v1",
        "programme":protocol["programme"],
        "authorization_state":"authorized_once_only_biological_response_execution",
        "response_protocol_fingerprint":rp["fingerprint"],
        "fresh_roster_fingerprint":roster["fingerprint"],
        "target_pool_traits_fingerprint":traits["fingerprint"],
        "fixed_site_count":len(sites),
        "token_secret_name":"NEON_API_TOKEN",
        "maximum_authenticated_query_requests":1,
        "expected_output":"results/carrier_prevalence_response_v1.json",
        "rerun_after_authenticated_query_starts":False,
        "post_response_site_repair_allowed":False,
        "post_response_metric_change_allowed":False,
        "required_file_sha256":hashes,
        "authorization_consumed":False
    }
    auth["fingerprint"]=canonical_sha(auth)
    AUTH.write_text(json.dumps(auth,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    print(json.dumps({
        "fixed_site_count":len(sites),
        "fixed_site_codes":sites,
        "response_protocol_fingerprint":rp["fingerprint"],
        "authorization_fingerprint":auth["fingerprint"],
        "response_endpoint_requests":0,
        "biological_response_bytes_opened":0
    },sort_keys=True))

if __name__=="__main__":
    main()
