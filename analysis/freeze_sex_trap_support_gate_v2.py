from __future__ import annotations

import argparse
import json
from pathlib import Path


def qualifying_species(inv: dict, *, unit: str) -> dict[str,dict]:
    out={}
    for species,row in (inv.get("species") or {}).items():
        sessions=int(row.get("support_paired_n3_sessions",0) or 0)
        units=int(row.get(unit,0) or 0)
        if sessions>=10 and units>=2:
            out[species]={
                "support_paired_n3_sessions":sessions,
                unit:units,
                "count_only_paired_n3_sessions":int(
                    row.get("count_only_paired_n3_sessions",0) or 0
                ),
                "trap_support_invalid_sessions":int(
                    row.get("trap_support_invalid_sessions",0) or 0
                ),
            }
    return out


def freeze_gate(portal: dict, neon: dict) -> dict:
    portal_q=qualifying_species(portal,unit="independent_plots")
    neon_q=qualifying_species(neon,unit="independent_sites")
    shared=sorted(
        species for species in set(portal_q)&set(neon_q)
        if portal_q[species]["support_paired_n3_sessions"]>=10
        and neon_q[species]["support_paired_n3_sessions"]>=10
    )
    portal_pass=len(portal_q)>=3
    neon_pass=len(neon_q)>=3
    cross_pass=bool(shared)
    passed=portal_pass and neon_pass and cross_pass
    return {
        "schema":"neon.public_mammal_sex_packing.primary_support_estimability_gate.v2",
        "frozen_date":"2026-09-29",
        "decision":(
            "authorize_effect_extraction"
            if passed else
            "stop_trap_support_estimability_failed"
        ),
        "primary_sex_count_threshold":3,
        "trap_support_rule":"all retained individual trap locations valid and unique within candidate session",
        "portal_family_gate":{
            "passed":portal_pass,
            "qualifying_species":sorted(portal_q),
            "counts":portal_q,
        },
        "neon_family_gate":{
            "passed":neon_pass,
            "qualifying_species":sorted(neon_q),
            "counts":neon_q,
        },
        "cross_source_gate":{
            "passed":cross_pass,
            "shared_species":shared,
        },
        "portal_summary":{
            key:portal.get(key)
            for key in (
                "session_count",
                "count_only_paired_n3_sessions",
                "support_paired_n3_sessions",
                "support_paired_n5_sessions",
                "trap_support_invalid_sessions",
                "duplicate_location_sessions",
                "missing_or_invalid_location_sessions",
            )
        },
        "neon_summary":{
            key:neon.get(key)
            for key in (
                "session_count",
                "count_only_paired_n3_sessions",
                "support_paired_n3_sessions",
                "support_paired_n5_sessions",
                "trap_support_invalid_sessions",
                "duplicate_location_sessions",
                "missing_or_invalid_location_sessions",
                "processed_site_count",
                "site_stops",
            )
        },
        "ecological_effects_inspected":False,
        "ecological_model_fits":0,
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--portal",type=Path,required=True)
    parser.add_argument("--neon",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    portal=json.loads(args.portal.read_text())
    neon=json.loads(args.neon.read_text())
    out=freeze_gate(portal,neon)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
