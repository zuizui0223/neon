#!/usr/bin/env python3
"""MOSA pre-effect stress test: discard ALL codes bearing observed identity warnings.

Pure, repeatable and effect blind. Receives only already-authenticated author
retained records and the fixed conservative original strict-month support
cohort. Computes neither positions/distances/centroids nor W/B or spatial
slopes. Outputs *aggregate counts only* and never returns raw codes or dates.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime

from analysis.audit_mosa_effect_blind_structure_v1 import published_field_map

UNKNOWN = {"", "NA", "N/A", "UNKNOWN"}
KNOWN_SEX = {"M", "F"}
Y = set("ABCDEFGHIJ")


def conservative_warning_exclusion_support(
    rows: list[dict],
    fields: list[str],
    author_mn: set[str],
    excluded_whitespace_codes: set[str],
    strict_months: list[dict],
    *,
    min_repeat: int = 5,
    min_months: int = 60,
    min_varying_years: int = 10,
) -> dict:
    """Hold all strict-month identifiers fixed; REMOVE warnings only in sensitivity.

    Case definitions mirror the prior independent source audit: full-history
    distinct-station same-day MN conflicts, two known SX values for MN and
    two distinct known species for an author-first-MN code.
    """
    f = published_field_map(fields)
    sexes = [h for h in fields if str(h).upper().strip() == "SX"]
    if len(sexes) != 1:
        raise ValueError("Original verified SX field required exactly once")
    sx = sexes[0]
    roster = set(author_mn)
    excluded = set(excluded_whitespace_codes)
    if not roster or not excluded.issubset(roster):
        raise ValueError("Authenticated roster/excluded whitespace subset required")
    if not strict_months:
        raise ValueError("Frozen strict cohort cannot be empty")
    month_info = {s["year_month"]: s for s in strict_months}
    if len(month_info) != len(strict_months):
        raise ValueError("Duplicate frozen strict month")
    nights: dict[str, dict[str, set]] = defaultdict(lambda: defaultdict(set))
    known_species: dict[str, set] = defaultdict(set)
    known_sex: dict[str, set] = defaultdict(set)
    stations: dict[tuple[str, object], set] = defaultdict(set)
    for r in rows:
        tag = str(r.get(f["tag"]) or "").strip()
        if tag not in roster or tag in excluded:
            continue
        d = datetime.strptime(str(r.get(f["date"]) or "").strip(), "%d/%m/%Y").date()
        mo = f"{d.year:04d}-{d.month:02d}"
        sp = str(r.get(f["species"]) or "").strip().upper()
        if sp not in UNKNOWN:
            known_species[tag].add(sp)
        if sp != "MN":
            continue
        if str(r.get(f["grid"]) or "").strip().upper() != "MOSA":
            raise ValueError("Unexpected published grid in first-MN history")
        sex = str(r.get(sx) or "").strip().upper()
        if sex in KNOWN_SEX:
            known_sex[tag].add(sex)
        try:
            xx = int(str(r.get(f["x"]) or "").strip())
            yy = str(r.get(f["y"]) or "").strip().upper()
            valid = 1 <= xx <= 30 and len(yy) == 1 and yy in Y
        except (TypeError, ValueError):
            valid = False
        if not valid:
            continue
        stations[(tag, d)].add((xx, yy))
        if mo in month_info:
            nights[mo][tag].add(d)
    station_warning = {t for (t, _d), st in stations.items() if len(st) > 1}
    sex_warning = {t for t, vals in known_sex.items() if len(vals) > 1}
    species_warning = {t for t, vals in known_species.items() if len(vals) > 1}
    union = station_warning | sex_warning | species_warning

    drops = []
    support_remaining = []
    original_pair_count = 0
    suspect_pair_count = 0
    supported_all_original = 0
    affected_months = 0
    original_m_hist = Counter()
    new_m_hist = Counter()
    for month, entry in month_info.items():
        by_tag = nights.get(month, {})
        repeated = {tag for tag, days in by_tag.items() if len(days) >= 2}
        original_m = len(repeated)
        if original_m != int(entry["m"]):
            raise ValueError("Frozen within-month m support drift (fail closed)")
        if original_m < min_repeat:
            raise ValueError("Originally frozen m support no longer >= threshold")
        original_m_hist[original_m] += 1
        original_pair_count += original_m
        bad = repeated & union
        suspect_pair_count += len(bad)
        affected_months += bool(bad)
        m_kept = original_m - len(bad)
        drops.append(len(bad))
        new_m_hist[m_kept] += 1
        supported_all_original += int(m_kept >= min_repeat)
        if m_kept >= min_repeat:
            support_remaining.append((int(entry["year"]), int(entry["MNA"])))
    by_year = defaultdict(set)
    n_by_year = Counter()
    for year, mna in support_remaining:
        by_year[year].add(mna)
        n_by_year[year] += 1
    varying = {year for year, mna in by_year.items()
               if len(mna) >= 2 and n_by_year[year] >= 2}
    months_in_varying = sum(n_by_year[year] for year in varying)
    passed = (supported_all_original >= min_months and
              len(varying) >= min_varying_years and
              months_in_varying >= min_months)
    return {
        "schema": "neon.mosa.warning_exclusion_support.v1",
        "status": ("OBSERVATION_SUPPORT_STRESS_PASS_ECOLOGY_STILL_HOLD"
                   if passed else "STOP_WARNING_REMOVAL_INSUFFICIENT_SUPPORT"),
        "original_frozen_months": len(strict_months),
        "original_repeat_supported_code_month_pairs": original_pair_count,
        "station_warning_codes": len(station_warning),
        "sex_warning_codes": len(sex_warning),
        "species_warning_codes": len(species_warning),
        "union_warning_codes": len(union),
        "warning_affected_original_months": affected_months,
        "warning_affected_original_repeat_code_month_pairs": suspect_pair_count,
        "months_m_ge5_after_worst_case_code_removal": supported_all_original,
        "months_newly_below_m5": len(strict_months) - supported_all_original,
        "years_with_any_supported_month_after_removal": len(by_year),
        "years_with_ge2_distinct_FROZEN_MNA_levels_after_removal": len(varying),
        "retained_months_in_FROZEN_MNA_varying_years": months_in_varying,
        "min_original_m": min(original_m_hist),
        "min_after_removal_m": min(new_m_hist),
        "max_m_reduction_in_one_month": max(drops),
        "months_with_any_m_decrease": sum(n > 0 for n in drops),
        "months_by_m_reduction": dict(sorted(Counter(drops).items())),
        "m_after_removal_aggregated_histogram": dict(sorted(new_m_hist.items())),
        "uses_only_original_frozen_MNA_predictor": True,
        "new_MNA_predictor_or_spatial_response_recomputed": False,
        "full_153_month_original_eligibility_unchanged": True,
        "known_warning_exclusion_is_NOT_all_possible_identity_errors": True,
        "original_TOE_values_dates_and_station_positions_exported": False,
        "ecological_effects_opened": False,
        "biological_individual_ID_proven": False,
        "published_19850_MN_animal_identification_reconciled": False,
        "authoritative_source_ID_release": "HOLD",
        "scope": "Stress-test only: one Tanzanian grid; cannot revise failed NEON multigenus replication.",
    }
