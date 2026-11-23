from __future__ import annotations

import statistics
from collections import defaultdict
from typing import Iterable

HETEROMYID_GENERA={"Chaetodipus","Dipodomys","Perognathus","Microdipodops"}


def is_heteromyid(scientific_name: str) -> bool:
    parts=str(scientific_name or "").strip().split()
    if len(parts) < 2:
        return False
    genus=parts[0]
    species=parts[1].lower()
    if genus not in HETEROMYID_GENERA:
        return False
    if species in {"sp.","sp","spp.","spp"}:
        return False
    return True


def normalize_sex(value: object) -> str | None:
    if value is None:
        return None
    text=str(value).strip().lower()
    if not text:
        return None
    if text in {"m","male","1 - male","1-male","1_male"}:
        return "M"
    if text in {"f","female","2 - female","2-female","2_female"}:
        return "F"
    return None


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"1","true","t","yes","y"}


def sex_count_record(
    rows: Iterable[dict],
    *,
    id_field: str,
    pit_field: str | None=None,
    sex_field: str="sex",
) -> dict:
    by_id={}
    for raw in rows:
        row=dict(raw)
        ident=str(row.get(id_field,"")).strip()
        if not ident:
            continue
        by_id.setdefault(ident,row)

    retained=list(by_id.values())
    n_total=len(retained)
    known=[normalize_sex(row.get(sex_field)) for row in retained]
    n_male=sum(value=="M" for value in known)
    n_female=sum(value=="F" for value in known)
    n_known=n_male+n_female

    pit_fraction=None
    if pit_field is not None:
        pit_fraction=(
            sum(_truthy(row.get(pit_field)) for row in retained)/n_total
            if n_total else None
        )

    return {
        "n_total":n_total,
        "n_known_sex":n_known,
        "n_male":n_male,
        "n_female":n_female,
        "n_unknown_sex":n_total-n_known,
        "known_sex_fraction":(n_known/n_total if n_total else None),
        "pit_reliable_fraction":pit_fraction,
        "paired_n2_eligible":n_male>=2 and n_female>=2,
        "paired_n3_eligible":n_male>=3 and n_female>=3,
        "paired_n5_eligible":n_male>=5 and n_female>=5,
    }


def summarize_sex_estimability(
    session_rows: Iterable[dict],
    *,
    source: str,
) -> dict:
    rows=[dict(row) for row in session_rows]
    by_species=defaultdict(list)
    for row in rows:
        species=str(row.get("species","")).strip()
        if species:
            by_species[species].append(row)

    species_summary={}
    for species,srows in sorted(by_species.items()):
        primary=[row for row in srows if bool(row.get("paired_n3_eligible"))]
        plots={
            str(row.get("plot_id","")).strip()
            for row in primary
            if str(row.get("plot_id","")).strip()
        }
        sites={
            str(row.get("site","")).strip()
            for row in primary
            if str(row.get("site","")).strip()
        }
        years={
            str(row.get("year","")).strip()
            for row in primary
            if str(row.get("year","")).strip()
        }
        species_summary[species]={
            "session_count":len(srows),
            "paired_n2_sessions":sum(bool(row.get("paired_n2_eligible")) for row in srows),
            "paired_n3_sessions":len(primary),
            "paired_n5_sessions":sum(bool(row.get("paired_n5_eligible")) for row in srows),
            "independent_plots":len(plots),
            "independent_sites":len(sites),
            "years":len(years),
        }

    known=[
        float(row["known_sex_fraction"])
        for row in rows
        if row.get("known_sex_fraction") not in (None,"")
    ]

    return {
        "source":source,
        "session_count":len(rows),
        "species_count":len(species_summary),
        "paired_n2_sessions":sum(bool(row.get("paired_n2_eligible")) for row in rows),
        "paired_n3_sessions":sum(bool(row.get("paired_n3_eligible")) for row in rows),
        "paired_n5_sessions":sum(bool(row.get("paired_n5_eligible")) for row in rows),
        "median_known_sex_fraction":statistics.median(known) if known else None,
        "species":species_summary,
        "ecological_effects_inspected":False,
    }
