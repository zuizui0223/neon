"""Pure aggregate, ecological-effect-blind NEON CHM five-anchor source audit.

Every source namedLocation is a *literal* NEON station anchor; E5 is NOT
used to synthesize A1/A10/J1/J10. Even complete five-point coverage does
not prove that all 100 mammal trap stations were mapped or that the
latest aerial raster represents the historic trapping season.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from math import isfinite
from statistics import median

ANCHORS=("A1","A10","J1","J10","E5")
VALID="VALID_REFERENCE_PIXEL"


def _distribution(xs: list[float]) -> dict:
    return {
        "minimum":min(xs) if xs else None,
        "median":float(median(xs)) if xs else None,
        "maximum":max(xs) if xs else None,
    }


def aggregate_five_anchor_height_support(
    rows: list[dict], *, expected_plots: int=30
) -> dict:
    """Return ONLY counts/ranges: no geographic coordinates, raw heights
    by plot, site codes, genus capture recurrence or animal identities.
    """
    if isinstance(expected_plots,bool) or not isinstance(expected_plots,int) or expected_plots<1:
        raise ValueError("positive, fixed source original plot count required")
    by_plot=defaultdict(dict)
    states=Counter()
    known=0
    unknown=0
    zero=0
    negative=0
    valid=0
    for item in rows:
        if not isinstance(item,dict):
            raise ValueError("Original source must provide structured anchor status")
        plot=item.get("plot_key")
        anchor=item.get("anchor")
        if not isinstance(plot,(str,tuple)) or not plot or anchor not in ANCHORS:
            raise ValueError("Unknown source plot or noncanonical named anchor")
        if anchor in by_plot[plot]:
            raise ValueError("duplicate original source named station anchor")
        state=item.get("status")
        if not isinstance(state,str) or not state:
            raise ValueError("Missing original raster validity status")
        h=item.get("height_m")
        if state==VALID:
            if isinstance(h,bool) or not isinstance(h,(float,int)) or not isfinite(h):
                raise ValueError("Valid source height must be finite")
            valid+=1
            zero+=h==0
            negative+=h<0
        elif h is not None:
            raise ValueError("Masked or unavailable raster values must be missing")
        u=item.get("uncertainty_known")
        if not isinstance(u,bool):
            raise ValueError("Coordinate uncertainty known/unknown must be explicit")
        known+=u
        unknown+=not u
        flag=item.get("historically_flagged_grid")
        if not isinstance(flag,bool):
            raise ValueError("Published geolocation-issue membership must be explicit")
        states[state]+=1
        by_plot[plot][anchor]=item

    if len(by_plot)!=expected_plots:
        raise ValueError("Frozen source original plot denominator changed")
    if any(set(group)!=set(ANCHORS) for group in by_plot.values()):
        raise ValueError("Every plot must include the five original anchors")
    if len(rows)!=5*expected_plots:
        raise ValueError("Frozen original source five anchor denominator changed")

    ranges=[]
    plots_two=0
    plots_five=0
    plots_diff=0
    e5_valid=0
    e5_zero=0
    e5_zero_other_positive=0
    flagged_plots=0
    all_five_all_zero=0
    for group in by_plot.values():
        heights=[float(x["height_m"]) for x in group.values() if x["status"]==VALID]
        if len(heights)>=2:
            plots_two+=1
            range_m=max(heights)-min(heights)
            ranges.append(range_m)
            if range_m>1e-9:
                plots_diff+=1
        if len(heights)==5:
            plots_five+=1
            if all(x==0 for x in heights):
                all_five_all_zero+=1
        e5=group["E5"]
        if e5["status"]==VALID:
            e5_valid+=1
            if e5["height_m"]==0:
                e5_zero+=1
                if any(
                    x["status"]==VALID and x["height_m"]>0
                    for key,x in group.items() if key!="E5"
                ):
                    e5_zero_other_positive+=1
        flagged_plots+=any(x["historically_flagged_grid"] for x in group.values())

    return {
        "schema":"neon.chm.five_named_anchors.aggregates_only.v1",
        "original_plots":expected_plots,
        "original_anchor_attempts":5*expected_plots,
        "valid_anchors":valid,
        "masked_or_unavailable_anchors":5*expected_plots-valid,
        "valid_zero_canopy_anchors":zero,
        "valid_negative_canopy_anchors_flagged":negative,
        "valid_E5_reference_anchors":e5_valid,
        "zero_E5_reference_heights":e5_zero,
        "plots_with_two_or_more_valid_anchors":plots_two,
        "plots_with_all_five_valid_anchors":plots_five,
        "plots_with_nonzero_five_anchor_canopy_range":plots_diff,
        "plots_with_all_five_valid_and_zero_canopy":all_five_all_zero,
        "plots_E5_zero_other_anchor_positive":e5_zero_other_positive,
        "five_anchor_range_m_summary":_distribution(ranges),
        "plots_with_published_geolocation_issue":flagged_plots,
        "anchors_with_known_coordinate_uncertainty":known,
        "anchors_with_unknown_coordinate_uncertainty":unknown,
        "raster_point_status_counts":dict(sorted(states.items())),
        "unknown_coordinate_uncertainty_was_treated_as_zero":False,
        "no_source_site_plot_coordinate_or_plot_height_values_exported":True,
        "all_100_trap_station_habitat_verified":False,
        "historical_capture_date_alignment_proven":False,
        "ecological_genus_habitat_effect_computed":False,
        "CHM_zero_means_no_understory":False,
        "original_density_W_B_claim_reclassified":False,
        "MOSA_W_B_effects":"SEALED",
    }
