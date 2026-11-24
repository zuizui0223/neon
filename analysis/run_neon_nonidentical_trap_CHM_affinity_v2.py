"""Same-source, same-score replay with the corrected uniform proposal clock."""
import json
from analysis import run_neon_nonidentical_trap_CHM_affinity_v1 as original
from analysis.neon_nonidentical_trap_CHM_affinity_v2 import corrected_unit_test, SAMPLER_METADATA

OUT = original.ROOT / "build/neon_nonidentical_trap_CHM_affinity_uniform_v2_20261124.json"

def main():
    try:
        result=original.run(unit_test=corrected_unit_test,sampler_metadata=SAMPLER_METADATA)
        code=0
    except Exception as exc:
        result={
            "status":"STOP_SOURCE_INFRASTRUCTURE_OR_ORIGINAL_COHORT",
            "failure_stage":original.PHASE if original.PHASE in original.PHASES else "UNKNOWN_PHASE",
            "error_class":type(exc).__name__,
            "original_rest_anonymous_error_counts":exc.counts if isinstance(exc,original.OriginalRESTHistoryStop) else {},
            "original_rest_requested_responses":exc.requested if isinstance(exc,original.OriginalRESTHistoryStop) else None,
            "original_rest_valid_responses":exc.valid if isinstance(exc,original.OriginalRESTHistoryStop) else None,
            "no_original_animal_station_geolocation_dates_or_tile_urls_exported":True,
        }
        code=3
    result.update({
        "schema":"neon.mammal.nonidentical_trap_canopy_association.uniform_clock.v2",
        "historical_v1_result_preserved":True,
        "historical_v1_run_id":45245953902,
        "same_source_same_score_calibration_not_new_confirmation":True,
        "publication_hold_unchanged":True,
        "one_sided_signflip_descriptive_conditional_on_site_statistics":True,
    })
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return code

if __name__=="__main__":
    raise SystemExit(main())
