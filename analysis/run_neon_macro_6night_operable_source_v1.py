#!/usr/bin/env python3
"""Original source-only NEON trapStatus 4/5/6 all-six-night support audit.

No original genus same-trap observed recurrence opened; no density,
habitat, thermal, patch, occupation or true species-specific detection fit.
"""
from __future__ import annotations
import json,os
from pathlib import Path
from analysis.run_neon_two_genus_source_v1 import original_sources_for_two_genus
from analysis.run_multiscale_density_estimability_release2026_v3 import _request_json,TOKEN_ENV
from analysis.run_neon_macro_temporal_weather_source_v1 import NEON_SITES
from analysis.neon_macro_site_selection_v1 import site_metadata_index
from analysis.neon_macro_6night_operable_trap_status_v1 import all_six_operable_source

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_macro_6night_operable_status456_source_v1.json"
FROZEN=ROOT/"results/neon_exact_two_genus_source_receipt_20261025.json"
DESIGN="docs/NEON_ALL_SIX_NIGHT_OPERABLE_TRAPSTATUS_GATE_20261026.md"

def require(p:bool,s:str):
    if not p:raise RuntimeError("NEON_OPERABLE_SOURCE_STOP: "+s)

def run()->dict:
    token=os.environ.get(TOKEN_ENV,"").strip()
    require(bool(token),"NEON source access missing")
    locked=json.loads(FROZEN.read_text(encoding="utf-8"))
    require((locked["status"],locked["exact_two_source"]["pairs"],
             locked["exact_two_source"]["physical_sites"])==
            ("EXACT_TWO_GENUS_SOURCE_GO_NO_EFFECT_OPENED",158,30),
            "previous source cohort altered")
    three,two,source,plots,traps=original_sources_for_two_genus(
        include_private_source_rows=True
    )
    require(len(three)==58 and len(two)==158
            and len({u["site"] for u in two})==30,
            "original release group altered")
    meta=_request_json(NEON_SITES).get("data")
    require(isinstance(meta,list),"NEON official domain data unavailable")
    sites={u["site"] for u in two}
    geo=site_metadata_index([
        r for r in meta if isinstance(r,dict) and r.get("siteCode") in sites
    ])
    require(set(geo)==sites,"one or more source sites missing official domain")
    summary,private=all_six_operable_source(
        two,plots,traps,{s:geo[s]["domain"] for s in sites}
    )
    require(len(private)==summary["retained_pairs"],
            "source grouped rows do not match retained pair count")
    return {
        **summary,
        "design":DESIGN,
        "provenance":{
            **source,
            "release":"RELEASE-2026",
            "official_NEON_trapStatus_category_semantics":"0_1_2_3_EXCLUDE__4_5_6_OPERABLE",
            "original_threeplus_source_58_invariant":True,
            "checksum_verified_original_source":True,
        },
        "effects_sealed":{
            "source_only_stage":True,
            "no_new_observed_genus_A_cross_B_trap_overlap":True,
            "no_source_averaged_new_Z_or_p_value":True,
            "no_original_animal_site_genus_station_or_exact_capture_dates_exported":True,
            "original_30_site_exact_two_Z_unmodified":True,
            "original_14_site_three_plus_Z_unmodified":True,
            "original_density_genus_5of8_FAIL_unmodified":True,
        },
    }

def main()->int:
    try:
        d=run();exitcode=0
    except Exception as e:
        d={
            "schema":"neon.macro.six_night_neon_operable_456_source_v1",
            "status":"STOP_OPERABLE_456_ORIGINAL_SOURCE_OR_SCHEMA",
            "error_class":type(e).__name__,
            "private_exception_message_and_source_identifiers_suppressed":True,
            "no_new_ecological_effect_calculated":True,
        }
        exitcode=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(d,indent=2,sort_keys=True))
    return exitcode

if __name__=="__main__":
    raise SystemExit(main())
