#!/usr/bin/env python3
"""Literal source-only matched same-N, same-U focal-versus-congener comparisons.

No NEON W/B, coordinates, animal identities, habitat-effect fit or slopes.
Only count whether original source events actually exhibit matched neighbour
composition at the same observed genus total, same uncertain-animal index,
and in the same focal population and calendar month-of-year.

This is a descriptive OVERLAP diagnostic, NOT a causal natural experiment.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from statistics import median

from analysis.audit_neon_u_adjusted_fixed_total_support_v1 import _analysis_cohort


def _summarize_groups(groups: dict[tuple, list[dict]], *, n_total: int) -> dict:
    qualifying=0
    event_pairs=0
    site_set=set()
    series_set=set()
    session_set=set()
    all_diffs=[]
    for _key, rows in groups.items():
        if len(rows)<2:
            continue
        freq=Counter(int(r["F"]) for r in rows)
        if len(freq)<2:
            continue
        qualifying+=1
        n=len(rows)
        event_pairs+=(n*(n-1)-sum(q*(q-1) for q in freq.values()))//2
        site_set.add(rows[0]["site"])
        series_set.add(rows[0]["series_id"])
        for r in rows:
            session_set.add((
                r["taxon"],r["site"],r["plot_id"],r["event_id"],
            ))
        counts=sorted(freq.items())
        for i,(f,ni) in enumerate(counts):
            for other,nj in counts[i+1:]:
                all_diffs.extend([abs(other-f)]*(ni*nj))
    if event_pairs!=len(all_diffs):
        raise AssertionError("Literal fixed-total pair counts and F contrasts disagree")
    return {
        "qualifying_contexts":qualifying,
        "distinct_event_pairs":event_pairs,
        "physical_sites_with_pairs":len(site_set),
        "supported_focal_series_with_pairs":len(series_set),
        "sessions_in_matched_contexts":len(session_set),
        "fraction_of_eligible_focal_sessions_in_matched_contexts":(
            len(session_set)/n_total if n_total else None
        ),
        "absolute_F_change_min":min(all_diffs) if all_diffs else None,
        "absolute_F_change_median":float(median(all_diffs)) if all_diffs else None,
        "absolute_F_change_max":max(all_diffs) if all_diffs else None,
    }


def observed_fixed_total_pairs(
    rows: list[dict], *,
    genus: str,
    previous_frozen_support: dict,
) -> dict:
    """Count only matched original event-level abundance compositions.

    Primary groups: focal species×site×plot, calendar month-of-year, N,U.
    Secondary groups: focal species×site×plot, N,U regardless of season.
    No favorable site, season or species selection permitted.
    """
    cohort=_analysis_cohort(rows,genus,previous_frozen_support)
    same_month=defaultdict(list)
    broad=defaultdict(list)
    for r in cohort:
        split=str(r["site_month"]).rsplit("|",1)
        if len(split)!=2 or split[0]!=r["site"] or not split[1].isdigit() or not 1<=int(split[1])<=12:
            raise ValueError("Original site×calendar-month nuisance encoding drifted")
        key=(r["series_id"],int(r["N"]),int(r["U"]))
        broad[key].append(r)
        same_month[(key,split[1])].append(r)
    strict=_summarize_groups(same_month,n_total=len(cohort))
    broad_sum=_summarize_groups(broad,n_total=len(cohort))
    if broad_sum["distinct_event_pairs"]<strict["distinct_event_pairs"]:
        raise AssertionError("Broader matched-pair count cannot be smaller")
    return {
        "schema":"neon.fixed_total.observed_N_U_matched_pair_support.v1",
        "genus":genus,
        "original_frozen_3plus_series_sessions":len(cohort),
        "original_physical_sites":len({r["site"] for r in cohort}),
        "original_focal_series":len({r["series_id"] for r in cohort}),
        "primary_same_calendar_month":{
            **strict,
            "matched_context":"focal species × site × plot × month-of-year × genus-N × unresolved-U",
            "inference_scope":"Exact arithmetic support only, potentially cross-year",
            "seasonally_not_equivalent_to_primary":False,
        },
        "broader_within_series_any_season":{
            **broad_sum,
            "matched_context":"focal species × site × plot × genus-N × unresolved-U, arbitrary month",
            "inference_scope":"Seasonally non-equivalent, never primary matched evidence",
            "seasonally_not_equivalent_to_primary":True,
        },
        "additional_cross_season_pairs":(
            broad_sum["distinct_event_pairs"]-strict["distinct_event_pairs"]
        ),
        "no_literal_same_season_fixed_total_pair":strict["distinct_event_pairs"]==0,
        "literal_pairs_do_not_prove_causal_species_interaction":True,
        "rank_two_without_literal_pair_is_model_based_extrapolation":True,
        "original_genus_N_and_U_never_relaxed_to_force_matches":True,
        "no_original_site_or_event_ids_exported":True,
        "ecological_W_B_effects_opened":False,
        "past_cross_genus_generality_status":"FAILED_5_OF_8",
        "MOSA_spatial_effects":"SEALED",
    }
