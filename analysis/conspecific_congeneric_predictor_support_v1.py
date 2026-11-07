#!/usr/bin/env python3
"""Pure, outcome-BLIND analysis of NEON known-alive species/congener predictors.

This is a NEW hypothesis generated after the unsuccessful original generality
and heldout tests. It is NOT a response model, never computes W/B/distance,
never joins spatial outcomes and must not rescue historical NEON results.
Original taxon-level and genus-level identifiers are kept distinct.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Iterable

import numpy as np

from analysis.multiscale_density_fixed_effects_v1 import _design

GROUP_TAXON_IDS = frozenset({"DIORDIMI", "PEGOPELE", "PEKEPEMA", "PELEPEMA"})
MIN_SESSIONS = 60
MIN_SITES = 6
MIN_SERIES = 8
MIN_JOINT_VARYING_SERIES = 5
MAX_CONDITION_NUMBER = 30.0


def classify_history(
    taxon_ids: Iterable[str],
    genus_by_taxon: dict[str, str],
    resolved_species_ids: set[str],
    *,
    qualifier_warning: bool = False,
) -> tuple[str, str | None, str | None]:
    """Return (state, one_genus_or_none, one_resolved_taxon_or_none)."""
    ids = {str(t).strip() for t in taxon_ids}
    if not ids:
        return ("EMPTY", None, None)
    if not ids.issubset(genus_by_taxon):
        raise ValueError("A source history includes an unknown target taxon")
    genera = {genus_by_taxon[t] for t in ids}
    if len(genera) != 1:
        return ("CROSS_GENUS", None, None)
    genus = next(iter(genera))
    if len(ids) == 1 and next(iter(ids)) in resolved_species_ids and not qualifier_warning:
        return ("RESOLVED_SPECIES", genus, next(iter(ids)))
    return ("UNRESOLVED_IN_GENUS", genus, None)


def event_predictors(
    *,
    ordered_events: dict[tuple[str, str], list[str]],
    histories: Iterable[dict],
    genus_by_taxon: dict[str, str],
    resolved_species_ids: set[str],
    respect_qualifier_warning: bool = False,
) -> tuple[dict[tuple[str, str, str, str], dict], dict]:
    """Construct genus N=F+C+U known-alive decomposition per plot event.

    histories include only captured target animals in original complete
    3-night standard-grid events. Records are {site,plot_id,taxon_ids,
    event_ids}. No raw TOE code or animal coordinate is needed here.
    """
    index = {}
    for key, ordered in ordered_events.items():
        if not ordered or len(set(ordered)) != len(ordered):
            raise ValueError("Duplicate/empty completed original events")
        for i, event_id in enumerate(ordered):
            index[(key[0], key[1], event_id)] = i

    bounds = defaultdict(list)
    summary = Counter()
    for h in histories:
        state, genus, species = classify_history(
            h["taxon_ids"], genus_by_taxon, resolved_species_ids,
            qualifier_warning=(
                bool(h.get("qualifier_warning", False))
                if respect_qualifier_warning else False
            ),
        )
        summary[state] += 1
        if state in {"EMPTY", "CROSS_GENUS"}:
            continue
        site, plot = str(h["site"]), str(h["plot_id"])
        event_ids = {str(e) for e in h["event_ids"]}
        if not event_ids or not (site, plot) in ordered_events:
            raise ValueError("Target animal has no eligible plot-event")
        if not event_ids.issubset(set(ordered_events[(site, plot)])):
            raise ValueError("Target animal captures not contained in complete event order")
        indices = [index[(site, plot, e)] for e in event_ids]
        lo, hi = min(indices), max(indices)
        bounds[(site, plot, genus)].append((lo, hi, species))

    out = {}
    for (site, plot, genus), intervals in bounds.items():
        event_ids = ordered_events[(site, plot)]
        for i, event_id in enumerate(event_ids):
            active = [sp for lo, hi, sp in intervals if lo <= i <= hi]
            counts = Counter(sp for sp in active if sp is not None)
            unresolved = sum(sp is None for sp in active)
            N = len(active)
            if N != sum(counts.values()) + unresolved:
                raise AssertionError("Unresolved known alive identity")
            out[(site, plot, event_id, genus)] = {
                "N": N,
                "resolved_species_counts": dict(sorted(counts.items())),
                "unresolved": unresolved,
            }
    return out, dict(summary)


def response_predictor_rows(
    sessions: list[dict],
    predictor_map: dict[tuple[str, str, str, str], dict],
    *,
    resolved_species_ids: set[str],
) -> tuple[list[dict], dict]:
    """Join ONLY abundance predictors to existing structural response IDs."""
    out = []
    species_groups = 0
    for session in sessions:
        taxon = str(session["taxon"])
        key = (str(session["site"]), str(session["plot_id"]),
               str(session["event_id"]), str(session["genus"]))
        z = predictor_map.get(key)
        if z is None:
            raise ValueError("Frozen structural session has no genus MNKA")
        n = int(z["N"])
        species_counts = z["resolved_species_counts"]
        unresolved = int(z["unresolved"])
        total_resolved = sum(species_counts.values())
        if n != total_resolved + unresolved:
            raise AssertionError("N is not decomposed exactly")
        is_species = taxon in resolved_species_ids
        focal = int(species_counts.get(taxon, 0)) if is_species else None
        congener = (total_resolved - focal) if is_species else None
        if not is_species:
            species_groups += 1
        if is_species and n != focal + congener + unresolved:
            raise AssertionError("Focal+other+unresolved does not equal genus MNKA")
        out.append({
            "taxon": taxon, "genus": str(session["genus"]),
            "site": str(session["site"]), "plot_id": str(session["plot_id"]),
            "event_id": str(session["event_id"]),
            "year": str(session["year"]),
            "site_month": f'{session["site"]}|{session["month"]}',
            "series_id": f'{taxon}|{session["site"]}|{session["plot_id"]}',
            "N": n, "F": focal, "C": congener, "U": unresolved,
            "strictly_resolved_response_taxon": is_species,
        })
    return out, {
        "target_structural_sessions": len(sessions),
        "species_group_response_sessions": species_groups,
        "strict_species_response_sessions": len(out) - species_groups,
    }


def _fwl_predictors(rows: list[dict]) -> dict:
    """Single-genus rank/collinearity after original nuisance FE; no outcomes."""
    if len(rows) < 3:
        return {"state": "NO_SAMPLES"}
    X = np.asarray([[float(r["F"]),float(r["C"])] for r in rows],dtype=float)
    if not np.all(np.isfinite(X)):
        raise ValueError("Non-finite species/congener predictor")
    Z = _design(rows, ("series_id", "site_month", "year"))
    coef, *_ = np.linalg.lstsq(Z, X, rcond=None)
    resid = X - Z @ coef
    sxx = resid.T @ resid
    rank = int(np.linalg.matrix_rank(resid, tol=1e-8))
    singular = np.linalg.svd(resid, compute_uv=False)
    condition = float(singular[0]/singular[1]) if len(singular)>1 and singular[1]>1e-8 else None
    s_f = float(sxx[0,0])
    s_c = float(sxx[1,1])
    rho = float(sxx[0,1]/np.sqrt(s_f*s_c)) if s_f>1e-10 and s_c>1e-10 else None
    return {
        "state": "RANK_TWO" if rank==2 else "INSUFFICIENT_RANK",
        "nuisance_rank": int(np.linalg.matrix_rank(Z)),
        "predictor_rank_after_FE": rank,
        "focal_residual_SS": s_f,
        "congener_residual_SS": s_c,
        "residual_F_C_correlation": rho,
        "predictor_condition_number": condition,
    }


def genus_support(rows: list[dict], *, all_genera: Iterable[str]) -> dict:
    """Aggregate taxonomic/covariate SUPPORT only. No W/B responses passed."""
    by_genus = defaultdict(list)
    for r in rows:
        if r["strictly_resolved_response_taxon"]:
            by_genus[r["genus"]].append(r)
    results = {}
    for g in sorted(set(all_genera)):
        rr = by_genus.get(g, [])
        by_series = defaultdict(list)
        for x in rr:
            by_series[x["series_id"]].append(x)
        retained = [
            x for key,vals in by_series.items() if len(vals)>=3
            for x in vals
        ]
        supported_series={k:v for k,v in by_series.items() if len(v)>=3}
        joint_varying = sum(
            len({x["F"] for x in vals})>=2 and len({x["C"] for x in vals})>=2
            for vals in supported_series.values()
        )
        fwl = _fwl_predictors(retained)
        sites = len({r["site"] for r in retained})
        n_series = len(supported_series)
        n_sess = len(retained)
        candidate = (
            n_sess>=MIN_SESSIONS and sites>=MIN_SITES
            and n_series>=MIN_SERIES and joint_varying>=MIN_JOINT_VARYING_SERIES
            and fwl.get("predictor_rank_after_FE")==2
            and fwl.get("predictor_condition_number") is not None
            and fwl["predictor_condition_number"] <= MAX_CONDITION_NUMBER
        )
        results[g] = {
            "state": "PREDICTOR_ONLY_POTENTIALLY_IDENTIFIABLE" if candidate
                     else "PREDICTOR_ONLY_STRUCTURAL_LIMIT",
            "species_sessions_all": len(rr),
            "species_sessions_in_3plus_series": n_sess,
            "sites_in_3plus_series": sites,
            "species_series_with_3plus_sessions": n_series,
            "series_varying_focal_F": sum(
                len({r["F"] for r in vals})>=2 for vals in supported_series.values()
            ),
            "series_varying_other_congener_C": sum(
                len({r["C"] for r in vals})>=2 for vals in supported_series.values()
            ),
            "series_joint_F_C_variation": joint_varying,
            "event_sessions_with_resolved_other_congener_C": sum(r["C"]>0 for r in rr),
            "event_sessions_with_unresolved_genus_U": sum(r["U"]>0 for r in rr),
            "unresolved_abundance_sum": sum(r["U"] for r in rr),
            "genus_abundance_sum": sum(r["N"] for r in rr),
            "fraction_of_genus_N_unresolved": (
                sum(r["U"] for r in rr) / sum(r["N"] for r in rr)
                if sum(r["N"] for r in rr)>0 else None
            ),
            "fixed_effects_predictor_geometry": fwl,
            "no_spatial_effect_or_W_B_opened": True,
        }
    return results
