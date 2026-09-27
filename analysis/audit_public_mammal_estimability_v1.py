from __future__ import annotations

import importlib.util
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
            "unmapped_nlcd_classes":sorted(unmapped_nlcd),
            "pathogen_species_with_estimable_recapture":int(
                neon_secondary.get("pathogen_species_with_estimable_recapture",0) or 0
            ),
        },
        "shared_species_meeting_source_specific_estimability":shared,
        "non_estimable_reasons":reasons,
        "ecological_model_fits":0,
    }
