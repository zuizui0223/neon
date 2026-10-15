#!/usr/bin/env python3
"""Effect-blind MOSA identity conflict counts for the frozen conservative cohort.

Only observed tag/date/station *categories*, sex labels and species labels.
No distances, individual centroids, W/B, MNA-space joins or density slopes.
Output contains aggregate counts ONLY: no TOE codes, sex-specific locations,
calendar dates, raw capture rows, or location summaries.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from analysis.audit_mosa_effect_blind_structure_v1 import published_field_map

VALID_SEX = {"M", "F"}
UNKNOWN_SPECIES = {"", "NA", "N/A", "UNKNOWN"}
GRID_Y = set("ABCDEFGHIJ")


def audit_identity_conflicts(
    rows: list[dict], fields: list[str], author_mn: set[str],
    excluded_codes: set[str], eligible_months: set[str],
    *, expected_support_m: dict[str, int] | None = None,
) -> dict:
    """Count anomalies without treating duplicate capture rows as animals.

    An observed multi-station same-night key is *ambiguous*, not proof of TOE
    reuse: the handling/trapping process could produce successive captures.
    Suspect-code intersection with the repeat-supported cohort is an UPPER
    BOUND on potentially affected W/B months, not a measured effect.
    """
    f = published_field_map(fields)
    sex_fields = [col for col in fields if str(col).strip().upper() == "SX"]
    if len(sex_fields) != 1:
        raise ValueError("MOSA source must contain its one verified SX sex column")
    sx = sex_fields[0]
    flag_fields = [col for col in fields if str(col).strip().upper() == "FLAGS"]
    if len(flag_fields) != 1:
        raise ValueError("MOSA original must have one FLAGS correction-history column")
    flag_col = flag_fields[0]
    roster = set(author_mn)
    excluded = set(excluded_codes)
    eligible = set(eligible_months)
    if not roster or not excluded.issubset(roster):
        raise ValueError("Nonempty author MN roster and valid exclusion subset required")
    if not eligible or any(
        len(m) != 7 or m[4] != "-" or not m[:4].isdigit() or not m[5:].isdigit()
        or not 1 <= int(m[5:]) <= 12 for m in eligible
    ):
        raise ValueError("Frozen eligible months required in YYYY-MM format")
    if expected_support_m is not None and set(expected_support_m) != eligible:
        raise ValueError("Frozen m-support keys must match all eligible months")

    # Identity warnings across the complete *author-retained* capture history.
    # A suspect code anywhere may undermine a repeat observation in a later
    # eligible cohort month; a direct-concurrent ambiguity is reported apart.
    by_tag_day: dict[tuple[str, object], dict] = defaultdict(
        lambda: {"stations": set(), "n_records": 0, "n_flagged": 0}
    )
    by_tag_species = defaultdict(set)
    by_tag_sex = defaultdict(set)
    repeat_nights = defaultdict(set)
    bad_lattice = 0
    seen_known_sex = 0
    seen_unknown_sex = 0
    author_mn_rows = 0
    excluded_rows = 0
    flagged_MN_records = 0
    codes_with_any_flagged_MN_record = set()

    for row in rows:
        tag = str(row.get(f["tag"]) or "").strip()
        if tag not in roster:
            continue
        if tag in excluded:
            excluded_rows += 1
            continue
        date_text = str(row.get(f["date"]) or "").strip()
        day = datetime.strptime(date_text, "%d/%m/%Y").date()
        month = day.strftime("%Y-%m")
        species = str(row.get(f["species"]) or "").strip().upper()
        if species not in UNKNOWN_SPECIES:
            by_tag_species[tag].add(species)
        if species != "MN":
            # Do not relabel non-MN captures as Mastomys.
            continue
        author_mn_rows += 1
        raw_flag = str(row.get(flag_col) or "").strip()
        has_flag = raw_flag.upper() not in {"", "NA", "N/A"}
        if has_flag:
            flagged_MN_records += 1
            codes_with_any_flagged_MN_record.add(tag)
        if str(row.get(f["grid"]) or "").strip().upper() != "MOSA":
            raise ValueError("Author-retained MN code on an unexpected grid")
        sex = str(row.get(sx) or "").strip().upper()
        if sex in VALID_SEX:
            by_tag_sex[tag].add(sex)
            seen_known_sex += 1
        else:
            seen_unknown_sex += 1
        try:
            x = int(str(row.get(f["x"]) or "").strip())
            y = str(row.get(f["y"]) or "").strip().upper()
            if not (1 <= x <= 30 and len(y) == 1 and y in GRID_Y):
                raise ValueError("invalid trap coordinate")
        except (ValueError, TypeError):
            bad_lattice += 1
            continue
        key = (tag, day)
        by_tag_day[key]["stations"].add((x, y))
        by_tag_day[key]["n_records"] += 1
        if has_flag:
            by_tag_day[key]["n_flagged"] += 1
        if month in eligible:
            repeat_nights[(tag, month)].add(day)

    multi_station_keys = {
        k for k, v in by_tag_day.items() if len(v["stations"]) > 1
    }
    same_station_duplicate_keys = {
        k for k, v in by_tag_day.items()
        if v["n_records"] > 1 and len(v["stations"]) == 1
    }
    station_suspect = {tag for tag, _day in multi_station_keys}
    sex_suspect = {tag for tag, vals in by_tag_sex.items() if len(vals) > 1}
    species_suspect = {
        tag for tag, vals in by_tag_species.items() if len(vals) > 1
    }

    repeat_by_month = defaultdict(set)
    for (tag, month), nights in repeat_nights.items():
        if len(nights) >= 2:
            repeat_by_month[month].add(tag)
    if set(repeat_by_month) != eligible:
        raise ValueError("Recomputed repeat-supported months drifted from frozen cohort")
    if expected_support_m is not None:
        mismatches = sum(
            len(repeat_by_month[month]) != expected_support_m[month]
            for month in eligible
        )
        if mismatches:
            raise ValueError("Frozen repeat-supported m counts differ from identity audit")

    repeat_tag_months = {
        (tag, month) for month, tags in repeat_by_month.items() for tag in tags
    }
    repeat_tags = {tag for tag, _month in repeat_tag_months}
    direct_stations = {
        tag for tag, day in multi_station_keys
        if day.strftime("%Y-%m") in eligible
    }
    union_suspect = station_suspect | sex_suspect | species_suspect
    affected_pairs = {
        (tag, month) for tag, month in repeat_tag_months
        if tag in union_suspect
    }
    affected_months = {month for _tag, month in affected_pairs}
    direct_affected_months = {
        month for tag, month in repeat_tag_months if tag in direct_stations
    }
    label_affected_months = {
        month for tag, month in repeat_tag_months
        if tag in (sex_suspect | species_suspect)
    }

    return {
        "schema": "neon.mosa.effect_blind_identity_conflict_summary.v2",
        "status": "EFFECT_BLIND_IDENTITY_COUNTS_ECOLOGY_HOLD",
        "author_first_MN_codes": len(roster),
        "excluded_collision_codes": len(excluded),
        "noncolliding_codes": len(roster - excluded),
        "frozen_eligible_months": len(eligible),
        "repeat_supported_code_month_pairs": len(repeat_tag_months),
        "repeat_supported_distinct_codes": len(repeat_tags),
        "repeat_supported_months_scored": len(repeat_by_month),
        "author_first_MN_retained_MN_capture_rows": author_mn_rows,
        "excluded_collision_capture_rows_all_species": excluded_rows,
        "known_M_or_F_SX_MN_capture_rows": seen_known_sex,
        "unknown_or_other_SX_MN_capture_rows": seen_unknown_sex,
        "MN_capture_rows_with_nonblank_FLAGS": flagged_MN_records,
        "same_day_multiple_station_keys_with_any_FLAG": sum(
            by_tag_day[k]["n_flagged"] > 0 for k in multi_station_keys
        ),
        "station_warning_codes_with_any_FLAG_in_history": len(
            station_suspect & codes_with_any_flagged_MN_record
        ),
        "suspect_repeat_codes_with_any_FLAG_in_history": len(
            repeat_tags & union_suspect & codes_with_any_flagged_MN_record
        ),
        "potentially_affected_months_with_a_flagged_suspect_code": len({
            month for tag, month in affected_pairs
            if tag in codes_with_any_flagged_MN_record
        }),
        "repeat_cohort_codes_with_explicit_series_prefix": sum(
            "/" in tag for tag in repeat_tags
        ),
        "repeat_cohort_codes_with_B_suffix": sum(
            tag.upper().endswith(" B") for tag in repeat_tags
        ),
        "station_warning_codes_with_explicit_series_prefix": sum(
            "/" in tag for tag in station_suspect
        ),
        "station_warning_codes_with_B_suffix": sum(
            tag.upper().endswith(" B") for tag in station_suspect
        ),
        "nonblank_FLAG_proves_identity_reconciled": False,
        "distinct_valid_tag_date_keys_full_history": len(by_tag_day),
        "same_day_multiple_station_keys_full_history": len(multi_station_keys),
        "same_day_duplicate_same_station_keys_full_history": len(same_station_duplicate_keys),
        "same_day_multiple_station_keys_in_frozen_months": sum(
            day.strftime("%Y-%m") in eligible for _tag, day in multi_station_keys
        ),
        "cross_species_codes_full_history": len(species_suspect),
        "cross_sex_SX_codes_full_history": len(sex_suspect),
        "station_conflict_codes_full_history": len(station_suspect),
        "station_conflict_codes_in_frozen_months": len(direct_stations),
        "union_suspect_codes_full_history": len(union_suspect),
        "suspect_codes_in_repeat_supported_cohort": len(repeat_tags & union_suspect),
        "potentially_affected_repeat_code_month_pairs": len(affected_pairs),
        "potentially_affected_months_upper_bound": len(affected_months),
        "potentially_affected_years_upper_bound": len({m[:4] for m in affected_months}),
        "months_with_direct_station_conflict_in_cohort_codes": len(direct_affected_months),
        "months_with_sex_or_species_warning_in_cohort_codes": len(label_affected_months),
        "MN_retained_rows_without_valid_lattice_station": bad_lattice,
        "same_day_station_change_proves_code_reuse": False,
        "unknown_sex_treated_as_change": False,
        "absence_of_conflicts_proves_biological_ID": False,
        "potential_affected_months_is_bias_estimate": False,
        "published_19850_biological_individuals_reconciled": False,
        "raw_TOE_values_or_calendar_dates_exported": False,
        "W_B_centroids_or_density_associations_opened": False,
        "ecological_effects_opened": False,
        "decision": "HOLD_BIOLOGICAL_IDENTITY_REQUIRES_AUTHOR_CLARIFICATION",
    }
