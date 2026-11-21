#!/usr/bin/env python3
"""Source-only NEON six-night common trap opportunity QA for two-genus pair.

Do not open or compute A×B same-genus station overlap, recurrence Z, weather
or population density, regardless of whether support passes. Fully source-
verified original RELEASE-2026 capture files. Private site, plot, animal
and station arrays are transient only and not printed to logs.
"""
from __future__ import annotations
from pathlib import Path
import json,os

from analysis.run_neon_two_genus_source_v1 import original_sources_for_two_genus
from analysis.run_multiscale_density_estimability_release2026_v3 import (
    _request_json,TOKEN_ENV
)
from analysis.run_neon_macro_temporal_weather_source_v1 import NEON_SITES
from analysis.neon_macro_site_selection_v1 import site_metadata_index
from analysis.neon_macro_six_night_effort_v1 import recorded_station_opportunity

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_macro_six_night_effort_source_v1.json"
PREVIOUS=ROOT/"results/neon_exact_two_genus_source_receipt_20261025.json"

def need(ok:bool,msg:str)->None:
    if not ok:raise RuntimeError("NEON_SIX_NIGHT_SOURCE_STOP: "+msg)

def run()->dict:
    token=os.environ.get(TOKEN_ENV,"").strip()
    need(bool(token),"original release access required")
    archived=json.loads(PREVIOUS.read_text(encoding="utf-8"))
    need(archived["status"]=="EXACT_TWO_GENUS_SOURCE_GO_NO_EFFECT_OPENED"
         and archived["exact_two_source"]["pairs"]==158
         and archived["exact_two_source"]["physical_sites"]==30,
         "original source receipt unavailable")
    strict,two,rawsource,plots,traps=original_sources_for_two_genus(
        include_private_source_rows=True
    )
    need((len(strict),len(two),len({u["site"] for u in two}))==(58,158,30),
         "original comparison sets drifted")
    published=_request_json(NEON_SITES).get("data")
    need(isinstance(published,list),"NEON site/domain source metadata missing")
    sites={u["site"] for u in two}
    source_sites=[r for r in published if isinstance(r,dict)
                  and r.get("siteCode") in sites]
    domain=site_metadata_index(source_sites)
    need(set(domain)==sites,"official NEON domain metadata incomplete")
    report,private=recorded_station_opportunity(
        two,plots,traps,{s:domain[s]["domain"] for s in sites}
    )
    return {
        **report,
        "source_provenance":{
            **rawsource,
            "NEON_release":"RELEASE-2026",
            "original_two_genus_source_receipt_revalidated":True,
            "original_3plus_genus_58_cohort_unchanged":True,
            "canonical_trap_observation_not_station_geolocation":True,
        },
        "effects_still_sealed":{
            "actual_recurrence_A_cross_B_opened":False,
            "null_overlap_or_site_Z_opened":False,
            "density_W_B_climate_habitat_effect_opened":False,
            "site_animal_genus_station_or_dates_exported":False,
            "original_exact_two_positive_effect_preserved":True,
        },
    }

def main()->int:
    try:
        result=run()
        code=0
    except Exception as exc:
        result={
            "schema":"neon.macro.six_night_common_recorded_station_support.v1",
            "status":"STOP_SOURCE_RECONSTRUCTION_OR_EFFORT_INVARIANT",
            "error_class":type(exc).__name__,
            "no_original_private_site_tag_or_station_exported":True,
            "new_ecological_effect_not_opened":True,
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return code

if __name__=="__main__":
    raise SystemExit(main())
