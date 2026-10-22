"""Private-data-safe failure stages for live NEON GraphQL/REST source QA.

Only fixed enum phases and exception CLASS are reported. Never append
exception messages, source queries, UTM, animal IDs or station names to
Action logs, README/PR text or downloadable CI artifacts.
"""
from __future__ import annotations

SOURCE_PHASES=frozenset({
    "PRECHECK_EXISTING_FIVE_ANCHOR_RECEIPT",
    "ORIGINAL_MAMMAL_SOURCE_RECONSTRUCTION",
    "BUILD_EXACT_3000_SOURCE_NAMES",
    "GRAPHQL_FIVE_NAME_PREFLIGHT",
    "GRAPHQL_FIVE_NAME_PARSE",
    "REST_GRAPHQL_HISTORY_EQUIVALENCE",
    "GRAPHQL_FULL_3000_BATCHES",
    "VERIFY_FIVE_ORIGINAL_CAPTURE_DAYS",
    "ALL_STATION_DATE_COVERAGE",
    "FINAL_AGGREGATE_SOURCE_RECEIPT",
})



# Every category is an invariant literal, never generated from source values.
SAFE_REST_GRAPHQL_DIFF_GROUPS=frozenset({
    "ROOT_LOCATION_NAME",
    "ROOT_LOCATION_PROPERTIES",
    "ROOT_PROJECTED_CRS",
    "HISTORY_NUMBER_OF_RECORDS",
    "HISTORY_VALIDITY_INTERVAL",
    "HISTORY_CURRENT_FIELD",
    "HISTORY_UTM_COORDINATES",
    "HISTORY_PROJECTED_CRS",
    "HISTORY_LOCATION_PROPERTIES",
    "MALFORMED_SOURCE_FIELDS",
    "OTHER_CANONICAL_FIELDS",
    "CANONICAL_COMPARISON_PARSE_ERROR",
})


def _safe_properties(items):
    if items is None:
        return {}
    if not isinstance(items,list):
        raise ValueError("Malformed source properties")
    result={}
    for value in items:
        if not isinstance(value,dict):
            raise ValueError("Malformed source property row")
        name=str(value.get("locationPropertyName") or "")
        content=value.get("locationPropertyValue")
        if not name:
            raise ValueError("Unnamed source property")
        if name in result and str(result[name])!=str(content):
            raise ValueError("Conflicting source property")
        result[name]=None if content is None else str(content)
    return result


def _safe_iso(t):
    from datetime import datetime,timezone
    if t is None or str(t).strip()=="":
        return None
    dt=datetime.fromisoformat(str(t).strip().replace("Z","+00:00"))
    if dt.tzinfo is not None:
        dt=dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt.isoformat(timespec="seconds")


def _source_coordinates(row):
    from math import isfinite
    out=[]
    for k in ("locationUtmEasting","locationUtmNorthing"):
        value=row.get(k)
        if value is None:
            out.append(None)
        else:
            f=float(value)
            if not isfinite(f):
                raise ValueError("Source coordinate is non-finite")
            out.append(f)
    return tuple(out)


def _projected_source_crs(row,parent):
    zone=row.get("locationUtmZone") or parent.get("locationUtmZone")
    if zone is not None:
        zone=int(zone)
    hemisphere=str(
        row.get("locationUtmHemisphere") or
        parent.get("locationUtmHemisphere") or ""
    ).strip().upper()
    return zone,hemisphere


def safe_rest_graphql_diff_groups(rest:dict, gql:dict) -> list[str]:
    """Diagnose unequal REST/GraphQL fields without returning ANY values.

    This is reporting-only; it never declares sources equivalent. The
    hard original comparison remains mandatory until an independently
    justified, tested canonical semantics is established.
    """
    groups=set()
    try:
        if not isinstance(rest,dict) or not isinstance(gql,dict):
            raise ValueError("Malformed source")
        if rest.get("locationName")!=gql.get("locationName"):
            groups.add("ROOT_LOCATION_NAME")
        if _projected_source_crs(rest,rest)!=_projected_source_crs(gql,gql):
            groups.add("ROOT_PROJECTED_CRS")
        if _safe_properties(rest.get("locationProperties")) != _safe_properties(gql.get("locationProperties")):
            groups.add("ROOT_LOCATION_PROPERTIES")
        h1,h2=rest.get("locationHistory"),gql.get("locationHistory")
        if not isinstance(h1,list) or not isinstance(h2,list):
            groups.add("MALFORMED_SOURCE_FIELDS")
        else:
            if len(h1)!=len(h2):
                groups.add("HISTORY_NUMBER_OF_RECORDS")
            def key(row):
                if not isinstance(row,dict):
                    raise ValueError("Malformed historical source row")
                return (_safe_iso(row.get("locationStartDate")),
                        _safe_iso(row.get("locationEndDate")))
            one=sorted(h1,key=lambda r:str(key(r)))
            two=sorted(h2,key=lambda r:str(key(r)))
            for row_a,row_b in zip(one,two):
                if key(row_a)!=key(row_b):
                    groups.add("HISTORY_VALIDITY_INTERVAL")
                ca,cb=row_a.get("current"),row_b.get("current")
                def truth(x):
                    if isinstance(x,bool):return x
                    if isinstance(x,str) and x.strip().lower() in {"true","false"}:
                        return x.strip().lower()=="true"
                    return x
                if truth(ca)!=truth(cb):
                    groups.add("HISTORY_CURRENT_FIELD")
                if _source_coordinates(row_a)!=_source_coordinates(row_b):
                    groups.add("HISTORY_UTM_COORDINATES")
                if _projected_source_crs(row_a,rest)!=_projected_source_crs(row_b,gql):
                    groups.add("HISTORY_PROJECTED_CRS")
                if _safe_properties(row_a.get("locationProperties"))!=_safe_properties(row_b.get("locationProperties")):
                    groups.add("HISTORY_LOCATION_PROPERTIES")
    except (ValueError,KeyError,TypeError,OverflowError):
        groups.add("MALFORMED_SOURCE_FIELDS")
    return sorted(groups)


def summarize_preflight_diff_groups(differences:list[list[str]]) -> dict:
    """Only whitelisted category COUNTs are allowed into public STOP JSON."""
    from collections import Counter
    if not isinstance(differences,list):
        raise ValueError("Original preflight comparison must be a list")
    counts=Counter()
    for groups in differences:
        if not isinstance(groups,list) or any(
            not isinstance(k,str) or k not in SAFE_REST_GRAPHQL_DIFF_GROUPS
            for k in groups
        ):
            raise ValueError("Unsafe diagnostic key is not on source whitelist")
        counts.update(set(groups))
    return {
        "source_documents_compared":len(differences),
        "source_documents_with_differences":sum(bool(x) for x in differences),
        "safe_field_group_counts":dict(sorted(counts.items())),
        "any_actual_coordinates_or_source_station_names_exported":False,
        "source_preflight_mismatch_not_considered_valid":True,
    }


class SourcePreflightMismatch(ValueError):
    def __init__(self, sanitized_aggregate:dict):
        # Never include source values in exception messages.
        super().__init__("REST GraphQL source history equality failed")
        self.safe_source_diagnostics=sanitized_aggregate


def source_stop_receipt(stage:str,exc:Exception)->dict:
    """Sanitize diagnostic: report no exception message, URL or site label."""
    known=stage if stage in SOURCE_PHASES else "UNCLASSIFIED_SOURCE_PHASE"
    if isinstance(exc,ValueError):
        group="SOURCE_HISTORY_OR_COMPARISON_SCHEMA"
    elif isinstance(exc,KeyError):
        group="MISSING_SOURCE_RESPONSE_FIELD"
    elif isinstance(exc,TypeError):
        group="SOURCE_RESPONSE_FIELD_TYPE"
    elif isinstance(exc,RuntimeError):
        group="SOURCE_RUNTIME_INVARIANT_OR_REMOTE_ERROR"
    else:
        group="OTHER_SOURCE_FAILURE"
    extra={}
    if isinstance(exc,SourcePreflightMismatch):
        candidate=exc.safe_source_diagnostics
        if isinstance(candidate,dict):
            # Validate the complete content again; no unsanitized exception
            # data are ever emitted in GitHub logs or artifacts.
            try:
                count=candidate["source_documents_compared"]
                records=candidate["source_documents_with_differences"]
                groups=candidate["safe_field_group_counts"]
                if (isinstance(count,int) and 0<=count<=5
                    and isinstance(records,int) and 0<=records<=count
                    and isinstance(groups,dict)
                    and all(k in SAFE_REST_GRAPHQL_DIFF_GROUPS and
                            isinstance(v,int) and 0<=v<=count
                            for k,v in groups.items())):
                    extra={"safe_source_discrepancy_groups":candidate}
            except (KeyError,TypeError):
                pass
    return {
        **extra,
        "schema":"neon.mammal.original_100_station_dated_source_QA.v1",
        "status":"STOP_SOURCE_GRAPHQL_REST_EQUIVALENCE_OR_ORIGINAL_COHORT",
        "failure_stage":known,
        "safe_reason_class":group,
        "error_class":type(exc).__name__,
        "source_station_or_animal_ids_exported":False,
        "original_100_station_coordinate_values_exported":False,
        "any_habitat_or_density_W_B_effect_computed":False,
        "no_private_exception_message_emitted":True,
        "original_14site_genus_recurrence_effect_not_modified":True,
    }
