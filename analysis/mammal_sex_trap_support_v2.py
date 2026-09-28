from __future__ import annotations

import statistics
from collections import Counter, defaultdict
from typing import Iterable

from analysis.mammal_sex_packing_estimability_v1 import normalize_sex


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"1","true","t","yes","y"}


def trap_support_record(
    rows: Iterable[dict],
    *,
    id_field: str,
    location_field: str,
    sex_field: str="sex",
    pit_field: str | None=None,
) -> dict:
    """Effect-blind retained-individual and trap-support audit.

    Input ordering is authoritative: the first record for an individual is
    retained, matching the frozen v1 deterministic-deduplication contract.
    """
    by_id={}
    for raw in rows:
        row=dict(raw)
        ident=str(row.get(id_field,"")).strip()
        if not ident:
            continue
        by_id.setdefault(ident,row)

    retained=list(by_id.values())
    sexes=[normalize_sex(row.get(sex_field)) for row in retained]
    locations=[
        str(row.get(location_field,"")).strip()
        for row in retained
    ]
    nonempty=[value for value in locations if value]
    counts=Counter(nonempty)
    duplicate_locations=sorted(
        value for value,count in counts.items() if count>1
    )
    duplicate_excess=sum(count-1 for count in counts.values() if count>1)
    missing_locations=sum(not value for value in locations)

    n_total=len(retained)
    n_male=sum(value=="M" for value in sexes)
    n_female=sum(value=="F" for value in sexes)
    n_known=n_male+n_female
    support_valid=(missing_locations==0 and duplicate_excess==0)

    pit_fraction=None
    if pit_field is not None:
        pit_fraction=(
            sum(_truthy(row.get(pit_field)) for row in retained)/n_total
            if n_total else None
        )

    reason=None
    if missing_locations:
        reason="missing_or_invalid_retained_trap_location"
    elif duplicate_excess:
        reason="duplicate_retained_trap_location"

    return {
        "n_total":n_total,
        "n_known_sex":n_known,
        "n_male":n_male,
        "n_female":n_female,
        "n_unknown_sex":n_total-n_known,
        "known_sex_fraction":(n_known/n_total if n_total else None),
        "pit_reliable_fraction":pit_fraction,
        "retained_location_count":len(nonempty),
        "missing_or_invalid_location_count":missing_locations,
        "duplicate_location_excess_count":duplicate_excess,
        "duplicate_locations":";".join(duplicate_locations),
        "trap_support_valid":support_valid,
        "trap_support_non_estimable_reason":reason,
        "count_only_paired_n2_eligible":n_male>=2 and n_female>=2,
        "count_only_paired_n3_eligible":n_male>=3 and n_female>=3,
        "count_only_paired_n5_eligible":n_male>=5 and n_female>=5,
        "support_paired_n2_eligible":support_valid and n_male>=2 and n_female>=2,
        "support_paired_n3_eligible":support_valid and n_male>=3 and n_female>=3,
        "support_paired_n5_eligible":support_valid and n_male>=5 and n_female>=5,
    }


def summarize_support_sessions(
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
        primary=[
            row for row in srows
            if bool(row.get("support_paired_n3_eligible"))
        ]
        species_summary[species]={
            "session_count":len(srows),
            "count_only_paired_n3_sessions":sum(
                bool(row.get("count_only_paired_n3_eligible")) for row in srows
            ),
            "support_paired_n2_sessions":sum(
                bool(row.get("support_paired_n2_eligible")) for row in srows
            ),
            "support_paired_n3_sessions":len(primary),
            "support_paired_n5_sessions":sum(
                bool(row.get("support_paired_n5_eligible")) for row in srows
            ),
            "trap_support_invalid_sessions":sum(
                not bool(row.get("trap_support_valid")) for row in srows
            ),
            "independent_plots":len({
                str(row.get("plot_id","")).strip()
                for row in primary
                if str(row.get("plot_id","")).strip()
            }),
            "independent_sites":len({
                str(row.get("site","")).strip()
                for row in primary
                if str(row.get("site","")).strip()
            }),
            "years":len({
                str(row.get("year","")).strip()
                for row in primary
                if str(row.get("year","")).strip()
            }),
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
        "count_only_paired_n3_sessions":sum(
            bool(row.get("count_only_paired_n3_eligible")) for row in rows
        ),
        "support_paired_n2_sessions":sum(
            bool(row.get("support_paired_n2_eligible")) for row in rows
        ),
        "support_paired_n3_sessions":sum(
            bool(row.get("support_paired_n3_eligible")) for row in rows
        ),
        "support_paired_n5_sessions":sum(
            bool(row.get("support_paired_n5_eligible")) for row in rows
        ),
        "trap_support_invalid_sessions":sum(
            not bool(row.get("trap_support_valid")) for row in rows
        ),
        "duplicate_location_sessions":sum(
            int(row.get("duplicate_location_excess_count",0) or 0)>0
            for row in rows
        ),
        "missing_or_invalid_location_sessions":sum(
            int(row.get("missing_or_invalid_location_count",0) or 0)>0
            for row in rows
        ),
        "median_known_sex_fraction":statistics.median(known) if known else None,
        "species":species_summary,
        "ecological_effects_inspected":False,
        "ecological_model_fits":0,
    }
