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
    return {
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
