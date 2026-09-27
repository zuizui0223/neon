from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

ROOT=Path(__file__).resolve().parents[1]


def _load_context():
    path=ROOT/"analysis"/"public_mammal_context_v1.py"
    spec=importlib.util.spec_from_file_location("public_mammal_context_v1",path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONTEXT=_load_context()


def _flag(row: dict, key: str) -> bool:
    value=row.get(key,False)
    if isinstance(value,bool):
        return value
    return str(value).strip().lower() in {"1","true","yes"}


def _threshold_counts(rows: list[dict]) -> dict[str,int]:
    return {
        "eligible_n3_sessions":sum(_flag(row,"sensitivity_n3_eligible") for row in rows),
        "eligible_n5_sessions":sum(_flag(row,"primary_n5_eligible") for row in rows),
        "eligible_n8_sessions":sum(_flag(row,"sensitivity_n8_eligible") for row in rows),
    }


def audit_estimability(
    portal_rows: Iterable[dict],
    neon_rows: Iterable[dict],
    *,
    neon_secondary: dict,
) -> dict:
    portal=[dict(row) for row in portal_rows]
    neon=[dict(row) for row in neon_rows]

    portal_context_counts: dict[str,Counter]=defaultdict(Counter)
    portal_plot_counts: dict[str,dict[str,set[str]]]=defaultdict(lambda:defaultdict(set))
    for row in portal:
        if not _flag(row,"primary_n5_eligible"):
            continue
        context=CONTEXT.portal_competition_context(str(row.get("treatment","")))
        if context is None:
            continue
        species=str(row.get("species","")).strip()
        if not species:
            continue
        portal_context_counts[species][context]+=1
        plot=str(row.get("plot_id","")).strip()
        if plot:
            portal_plot_counts[species][context].add(plot)

    portal_both=sorted(
        species
        for species,counts in portal_context_counts.items()
        if counts["control"]>=5 and counts["kangaroo_rat_exclosure"]>=5
    )

    neon_habitat_counts: dict[str,Counter]=defaultdict(Counter)
    neon_site_sets: dict[str,set[str]]=defaultdict(set)
    neon_site_counts: dict[str,Counter]=defaultdict(Counter)
    neon_site_habitat_counts: dict[str,dict[str,Counter]]=defaultdict(lambda:defaultdict(Counter))
    unmapped_nlcd=set()
    for row in neon:
        if not _flag(row,"primary_n5_eligible"):
            continue
        species=str(row.get("species","")).strip()
        if not species:
            continue
        raw=str(row.get("nlcd_class","")).strip()
        try:
            habitat=CONTEXT.map_neon_nlcd(raw)
        except KeyError:
            unmapped_nlcd.add(raw)
            continue
        neon_habitat_counts[species][habitat]+=1
        site=str(row.get("site","")).strip()
        if site:
            neon_site_sets[species].add(site)
            neon_site_counts[species][site]+=1
            neon_site_habitat_counts[species][site][habitat]+=1

    neon_multi_habitat=sorted(
        species
        for species,counts in neon_habitat_counts.items()
        if sum(count>=5 for count in counts.values())>=2
    )
    neon_multi_site=sorted(
        species
        for species,sites in neon_site_sets.items()
        if len(sites)>=2
    )
    neon_strict_multi_site=sorted(
        species
        for species,counts in neon_site_counts.items()
        if sum(count>=5 for count in counts.values())>=2
    )

    within_site_habitat_species=[]
    cross_site_habitat_species=[]
    for species,site_map in neon_site_habitat_counts.items():
        within_site=any(
            sum(count>=5 for count in habitat_counts.values())>=2
            for habitat_counts in site_map.values()
        )
        habitat_site_replication: dict[str,set[str]]=defaultdict(set)
        for site,habitat_counts in site_map.items():
            for habitat,count in habitat_counts.items():
                if count>=3:
                    habitat_site_replication[habitat].add(site)
        cross_site=sum(
            len(sites)>=2
            for sites in habitat_site_replication.values()
        )>=2
        if within_site:
            within_site_habitat_species.append(species)
        if cross_site:
            cross_site_habitat_species.append(species)

    within_site_habitat_species=sorted(within_site_habitat_species)
    cross_site_habitat_species=sorted(cross_site_habitat_species)
    primary_habitat_identifiable=sorted(
        set(within_site_habitat_species) | set(cross_site_habitat_species)
    )

    shared=sorted(set(portal_both)&set(neon_multi_habitat))

    portal_thresholds=_threshold_counts(portal)
    neon_thresholds=_threshold_counts(neon)

    reasons=[]
    if portal_thresholds["eligible_n5_sessions"]==0:
        reasons.append("no_portal_n5_sessions")
    if neon_thresholds["eligible_n5_sessions"]==0:
        reasons.append("no_neon_n5_sessions")
    if not portal_both:
        reasons.append("no_portal_species_with_n5_ge5_sessions_both_contexts")
    if not neon_multi_habitat:
        reasons.append("no_neon_species_with_n5_ge5_sessions_in_ge2_habitats")
    if not primary_habitat_identifiable:
        reasons.append("no_neon_species_with_primary_habitat_identifiability")
    if not shared:
        reasons.append("no_shared_species_meeting_source_specific_estimability")
    if unmapped_nlcd:
        reasons.append("unmapped_neon_nlcd_classes")

    return {
        "schema":"neon.public_mammal_space_use.estimability.v1",
        "portal":{
            "session_count":len(portal),
            **portal_thresholds,
            "species_count":len({str(row.get("species","")).strip() for row in portal if str(row.get("species","")).strip()}),
            "n5_species_context_session_counts":{
                species:dict(sorted(counts.items()))
                for species,counts in sorted(portal_context_counts.items())
            },
            "n5_species_context_plot_counts":{
                species:{
                    context:len(plots)
                    for context,plots in sorted(contexts.items())
                }
                for species,contexts in sorted(portal_plot_counts.items())
            },
            "species_with_n5_ge5_sessions_both_contexts":portal_both,
        },
        "neon":{
            "session_count":len(neon),
            **neon_thresholds,
            "species_count":len({str(row.get("species","")).strip() for row in neon if str(row.get("species","")).strip()}),
            "site_count":len({str(row.get("site","")).strip() for row in neon if str(row.get("site","")).strip()}),
            "n5_species_habitat_session_counts":{
                species:dict(sorted(counts.items()))
                for species,counts in sorted(neon_habitat_counts.items())
            },
            "species_with_n5_ge5_sessions_in_ge2_habitats":neon_multi_habitat,
            "species_with_n5_sessions_in_ge2_sites":neon_multi_site,
            "species_with_n5_ge5_sessions_in_ge2_sites":neon_strict_multi_site,
            "species_with_within_site_habitat_contrast":within_site_habitat_species,
            "species_with_cross_site_habitat_replication":cross_site_habitat_species,
            "species_with_primary_habitat_identifiability":primary_habitat_identifiable,
            "unmapped_nlcd_classes":sorted(unmapped_nlcd),
            "pathogen_species_with_estimable_recapture":int(
                neon_secondary.get("pathogen_species_with_estimable_recapture",0) or 0
            ),
        },
        "shared_species_meeting_source_specific_estimability":shared,
        "non_estimable_reasons":reasons,
        "ecological_model_fits":0,
    }


def session_inventory_rows(
    portal_rows: Iterable[dict],
    neon_rows: Iterable[dict],
) -> list[dict]:
    grouped: dict[tuple[str,str,str],Counter]=defaultdict(Counter)

    for raw in portal_rows:
        row=dict(raw)
        species=str(row.get("species","")).strip()
        context=CONTEXT.portal_competition_context(str(row.get("treatment","")))
        if not species or context is None:
            continue
        key=("Portal",species,context)
        grouped[key]["session_count"]+=1
        grouped[key]["eligible_n3"]+=int(_flag(row,"sensitivity_n3_eligible"))
        grouped[key]["eligible_n5"]+=int(_flag(row,"primary_n5_eligible"))
        grouped[key]["eligible_n8"]+=int(_flag(row,"sensitivity_n8_eligible"))

    for raw in neon_rows:
        row=dict(raw)
        species=str(row.get("species","")).strip()
        if not species:
            continue
        raw_nlcd=str(row.get("nlcd_class","")).strip()
        try:
            context=CONTEXT.map_neon_nlcd(raw_nlcd)
        except KeyError:
            context=f"UNMAPPED:{raw_nlcd}"
        key=("NEON",species,context)
        grouped[key]["session_count"]+=1
        grouped[key]["eligible_n3"]+=int(_flag(row,"sensitivity_n3_eligible"))
        grouped[key]["eligible_n5"]+=int(_flag(row,"primary_n5_eligible"))
        grouped[key]["eligible_n8"]+=int(_flag(row,"sensitivity_n8_eligible"))

    return [
        {
            "source":source,
            "species":species,
            "context":context,
            "session_count":counts["session_count"],
            "eligible_n3":counts["eligible_n3"],
            "eligible_n5":counts["eligible_n5"],
            "eligible_n8":counts["eligible_n8"],
        }
        for (source,species,context),counts in sorted(grouped.items())
    ]


def render_estimability_memo(report: dict) -> str:
    portal=report["portal"]
    neon=report["neon"]
    shared=report["shared_species_meeting_source_specific_estimability"]
    reasons=report["non_estimable_reasons"]
    lines=[
        "# Public mammal Phase-1 estimability — V1",
        "",
        "## Status",
        "",
        "**No ecological models were fit in this phase.**",
        "",
        "This memo reports only whether the prespecified Portal and NEON contrasts have enough repeated public-data sessions to proceed to a separately frozen modeling phase.",
        "",
        "## Portal",
        "",
        f"- sessions: {portal['session_count']}",
        f"- eligible N>=3: {portal['eligible_n3_sessions']}",
        f"- eligible N>=5: {portal['eligible_n5_sessions']}",
        f"- eligible N>=8: {portal['eligible_n8_sessions']}",
        f"- species with >=5 N>=5 sessions in both control and kangaroo-rat exclosure: {', '.join(portal['species_with_n5_ge5_sessions_both_contexts']) or 'none'}",
        "",
        "## NEON",
        "",
        f"- sessions: {neon['session_count']}",
        f"- eligible N>=3: {neon['eligible_n3_sessions']}",
        f"- eligible N>=5: {neon['eligible_n5_sessions']}",
        f"- eligible N>=8: {neon['eligible_n8_sessions']}",
        f"- species with >=5 N>=5 sessions in >=2 habitat groups: {', '.join(neon['species_with_n5_ge5_sessions_in_ge2_habitats']) or 'none'}",
        f"- species with N>=5 sessions at >=2 sites: {', '.join(neon['species_with_n5_sessions_in_ge2_sites']) or 'none'}",
        f"- pathogen-grid species meeting the frozen recapture validation gate: {neon['pathogen_species_with_estimable_recapture']}",
        "",
        "## Cross-dataset",
        "",
        f"- shared species meeting the source-specific Portal and NEON estimability rules: {', '.join(shared) or 'none'}",
        "",
        "## Design issues before Phase 2",
        "",
    ]
    if reasons:
        lines.extend(f"- {reason}" for reason in reasons)
    else:
        lines.append("- none detected by the frozen estimability rules")
    lines += [
        "",
        "Phase 2 may proceed only after the estimability gate is explicitly frozen. This document contains no ecological coefficient, effect direction, significance test or model-selection result.",
        "",
    ]
    return "\n".join(lines)


def _read_csv(path: Path) -> list[dict]:
    with path.open(newline="",encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def _write_inventory(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    fields=["source","species","context","session_count","eligible_n3","eligible_n5","eligible_n8"]
    with path.open("w",newline="",encoding="utf-8") as fh:
        writer=csv.DictWriter(fh,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--portal-sessions",type=Path,required=True)
    parser.add_argument("--neon-sessions",type=Path,required=True)
    parser.add_argument("--neon-inventory",type=Path,required=True)
    parser.add_argument("--output-json",type=Path,default=ROOT/"results"/"public_mammal_estimability_v1.json")
    parser.add_argument("--output-csv",type=Path,default=ROOT/"data"/"derived"/"public_mammal_session_inventory_v1.csv")
    parser.add_argument("--output-md",type=Path,default=ROOT/"docs"/"PUBLIC_MAMMAL_ESTIMABILITY_V1.md")
    args=parser.parse_args()

    portal=_read_csv(args.portal_sessions)
    neon=_read_csv(args.neon_sessions)
    neon_inventory=json.loads(args.neon_inventory.read_text(encoding="utf-8"))
    report=audit_estimability(
        portal,
        neon,
        neon_secondary={
            "pathogen_species_with_estimable_recapture":
                neon_inventory.get("pathogen_species_with_estimable_recapture",0)
        },
    )
    inventory=session_inventory_rows(portal,neon)

    args.output_json.parent.mkdir(parents=True,exist_ok=True)
    args.output_json.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    _write_inventory(args.output_csv,inventory)
    args.output_md.parent.mkdir(parents=True,exist_ok=True)
    args.output_md.write_text(render_estimability_memo(report),encoding="utf-8")
    print(json.dumps({
        "portal_n5":report["portal"]["eligible_n5_sessions"],
        "neon_n5":report["neon"]["eligible_n5_sessions"],
        "portal_both_context_species":report["portal"]["species_with_n5_ge5_sessions_both_contexts"],
        "neon_multi_habitat_species":report["neon"]["species_with_n5_ge5_sessions_in_ge2_habitats"],
        "shared_species":report["shared_species_meeting_source_specific_estimability"],
        "non_estimable_reasons":report["non_estimable_reasons"],
        "ecological_model_fits":report["ecological_model_fits"],
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
