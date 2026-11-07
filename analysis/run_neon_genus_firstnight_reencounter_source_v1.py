#!/usr/bin/env python3
"""Effect-blind NEON genus-firstnight 3-night re-encounter SOURCE gate.

Original source release and exact-two primary episodes reproduced; no
day2/3 tag re-encounter matching or ecological detection outcomes opened.
"""
from __future__ import annotations
import json,os
from pathlib import Path

from analysis.run_neon_two_genus_source_v1 import original_sources_for_two_genus
from analysis.audit_multiscale_density_mnka_variation_v1 import _taxonomy
from analysis.neon_macro_firstnight_reencounter_source_v1 import source_first_night_cohort
from analysis.run_multiscale_density_estimability_release2026_v3 import (
    TOKEN_ENV
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_genus_firstnight_reencounter_source_20261026.json"
PRIOR=ROOT/"results/neon_exact_two_genus_source_receipt_20261025.json"
DESIGN="docs/NEON_GENUS_FIRST_NIGHT_REENCOUNTER_SOURCE_GATE_20261026.md"

def check(value:bool,why:str):
    if not value:raise ValueError("GENUS_FIRSTNIGHT_SOURCE_INVARIANT_STOP: "+why)

def run()->dict:
    token=os.environ.get(TOKEN_ENV,"").strip()
    check(bool(token),"NEON access token missing")
    prior=json.loads(PRIOR.read_text(encoding="utf-8"))
    check(prior["exact_two_source"]["pairs"]==158
          and prior["exact_two_source"]["physical_sites"]==30
          and prior["status"]=="EXACT_TWO_GENUS_SOURCE_GO_NO_EFFECT_OPENED",
          "frozen original first source population missing")
    old,exact,manifest,plots,traps=original_sources_for_two_genus(
        include_private_source_rows=True
    )
    check(len(old)==58 and len(exact)==158 and len({u["site"] for u in exact})==30,
          "original two-plus- and three-plus source units changed")
    all_taxa,bytaxon,names=_taxonomy()
    check(bool(all_taxa) and bool(bytaxon),"NEON provider taxonomy missing")
    report,private=source_first_night_cohort(
        exact,plots,traps,bytaxon
    )
    check(report["unique_source_three_night_bouts"]==293
          and report["original_exact_two_season_pairs"]==158,
          "original season-overlap support unexpectedly changed")
    return {
        **report,
        "source":{
            **manifest,
            "original_NEON_release":"RELEASE-2026",
            "original_strict_58_comparisons_preserved":True,
            "original_exact_two_158_comparisons_preserved":True,
            "authoritative_original_NEON_target_genus_taxonomy":True,
            "source_selected_by_firstnight_tagged_capture_only":True,
        },
        "design":DESIGN,
        "outcome_still_sealed":{
            "source_only_before_day2_day3_individual_matching":True,
            "new_genus_recapture_fraction_or_difference_not_computed":True,
            "original_genus_exact_trap_spatial_Z_unchanged":True,
            "old_failed_all_six_456_operability_source_gate_unchanged":True,
            "old_failed_eight_genus_density_5of8_generalization_unchanged":True,
            "old_climate_79_of_80_QC_STOP_unchanged":True,
            "private_original_taxon_tag_event_site_station_dates_not_exported":True,
        },
    }

def main()->int:
    try:
        res=run()
        exitcode=0
    except Exception as e:
        res={
            "schema":"neon.macro.genus_firstnight_reencounter_source.v1",
            "status":"STOP_GENUS_FIRSTNIGHT_SOURCE_RECONSTRUCTION_OR_INVARIANT",
            "error_class":type(e).__name__,
            "no_nextnight_genus_reencounter_outcome_computed":True,
            "no_private_original_identifiers_exported":True,
        }
        exitcode=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(res,indent=2,sort_keys=True))
    return exitcode

if __name__=="__main__":
    raise SystemExit(main())
