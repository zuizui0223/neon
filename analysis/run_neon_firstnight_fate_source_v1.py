#!/usr/bin/env python3
"""Rebuild original 2026 marked firstnight source and QA released fate.

This workflow reads fate statuses ONLY on original FIRST NIGHT of the
previously source-selected seven site Microtus/Peromyscus comparison.
All day2/3 capture response remains sealed; return SOURCE GO or STOP.
"""
from __future__ import annotations
import os,json
from pathlib import Path

from analysis.run_neon_two_genus_source_v1 import original_sources_for_two_genus
from analysis.audit_multiscale_density_mnka_variation_v1 import _taxonomy
from analysis.neon_macro_firstnight_reencounter_source_v1 import source_first_night_cohort
from analysis.neon_macro_firstnight_fate_source_v1 import initial_fate_source
from analysis.run_multiscale_density_estimability_release2026_v3 import TOKEN_ENV

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/"results/neon_genus_firstnight_reencounter_source_20261026.json"
OUT=ROOT/"build/neon_firstnight_source_fate_availability_20261028.json"
DESIGN="docs/NEON_FATE_RELEASE_REENCOUNTER_DESIGN_20261028.md"

def need(ok:bool,reason:str):
    if not ok:raise RuntimeError("ORIGINAL_NEON_FIRSTNIGHT_FATE_SOURCE_STOP: "+reason)

def run()->dict:
    need(bool(os.environ.get(TOKEN_ENV,"").strip()),
         "original NEON source authorization missing")
    frozen=json.loads(OLD.read_text(encoding="utf-8"))
    need(frozen["status"]=="SOURCE_MATCHED_GENUS_REENCOUNTER_COMPARISON_GO"
         and frozen["preselected_genus_pair_if_pass"]["genera"]==
             ["Microtus","Peromyscus"]
         and frozen["preselected_genus_pair_if_pass"]["shared_qualified_physical_sites"]==7,
         "previous pre-reencounter source-selected genus pair changed")
    old,two,provenance,plots,traps=original_sources_for_two_genus(
        include_private_source_rows=True, include_capture_fate=True,
    )
    need((len(old),len(two))==(58,158),
         "original source cohorts drifted after optional fate column read")
    _,bytaxon,_=_taxonomy()
    fresh,original_private=source_first_night_cohort(two,plots,traps,bytaxon)
    for key in ("status","source_firstnight_marked_animals",
                "unique_source_three_night_bouts",
                "independent_sites_with_firstnight_tagged_captures",
                "number_of_genera_with_one_plus_firstnight_captures",
                "preselected_genus_pair_if_pass"):
        need(fresh[key]==frozen[key],"historical firstnight source cohort differs")
    chosen=original_private["source_selected_genus_pair"]
    need(chosen is not None and tuple(chosen[:2])==("Microtus","Peromyscus")
         and len(chosen[2])==7,"historical private seven-site choices not reproduced")
    src,unused=initial_fate_source(
        original_private,traps,plots,bytaxon,
        selected_sites=set(chosen[2]),
    )
    return {
        **src,
        "design":DESIGN,
        "source_provenance":provenance,
        "original_source_selected_seven_sites_reproduced":True,
        "original_total_exact_two_comparisons":len(two),
        "original_total_three_plus_comparisons":len(old),
        "previous_observed_genus_reencounter_difference_not_refitted":True,
        "later_night_fate_or_return_records_not_accessed_for_new_outcome":True,
        "source_fate_categories_not_release_probability":True,
        "interpretation":(
            "Source gate GO only; do not yet claim any new conditional reencounter result"
            if src["new_post_result_source_thresholds"]["passed"] else
            "Explicit documented-release cohort insufficient; effect stays sealed"
        ),
    }

def main()->int:
    try:
        out=run()
        exitcode=0
    except Exception as e:
        out={
            "schema":"neon.macro.original_marked_firstnight_fate_source.v1",
            "status":"STOP_ORIGINAL_SOURCE_FATE_DATA_OR_INVARIANT",
            "error_class":type(e).__name__,
            "private_source_exception_message_suppressed":True,
            "original_2026_genus_reencounter_and_recurrence_effects_unchanged":True,
            "new_release_conditioned_reencounter_outcome_opened":False,
        }
        exitcode=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True))
    return exitcode
if __name__=="__main__":
    raise SystemExit(main())
