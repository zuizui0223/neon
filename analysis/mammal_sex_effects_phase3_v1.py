from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def _load_exact():
    path=ROOT/"analysis"/"mammal_spatial_packing_exact_v2.py"
    spec=importlib.util.spec_from_file_location("packing_exact_v2",path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PACKING=_load_exact()


def sex_packing_effect(
    active_traps_xy: np.ndarray,
    male_xy: np.ndarray,
    female_xy: np.ndarray,
) -> dict[str,Any]:
    active=np.asarray(active_traps_xy,dtype=float)
    male=np.asarray(male_xy,dtype=float)
    female=np.asarray(female_xy,dtype=float)

    if len(male)<2 or len(female)<2:
        return {
            "estimable":False,
            "non_estimable_reason":"fewer_than_two_per_sex",
        }

    combined=np.vstack([male,female])
    if len(np.unique(combined,axis=0)) != len(combined):
        return {
            "estimable":False,
            "non_estimable_reason":"duplicate_retained_trap_location",
        }

    male_score=PACKING.packing_score_exact(male,active)
    female_score=PACKING.packing_score_exact(female,active)
    if not male_score["estimable"] or not female_score["estimable"]:
        reason=(
            male_score.get("non_estimable_reason")
            if not male_score["estimable"]
            else female_score.get("non_estimable_reason")
        )
        return {
            "estimable":False,
            "non_estimable_reason":reason,
            "male":male_score,
            "female":female_score,
        }

    return {
        "estimable":True,
        "non_estimable_reason":None,
        "n_male":len(male),
        "n_female":len(female),
        "packing_z_male":float(male_score["packing_z"]),
        "packing_z_female":float(female_score["packing_z"]),
        "delta_sex_packing":float(
            male_score["packing_z"]-female_score["packing_z"]
        ),
        "male_mpd_observed":male_score["mpd_observed"],
        "female_mpd_observed":female_score["mpd_observed"],
        "male_null_mean":male_score["mpd_null_mean"],
        "female_null_mean":female_score["mpd_null_mean"],
        "male_null_sd":male_score["mpd_null_sd"],
        "female_null_sd":female_score["mpd_null_sd"],
        "null_mode":"exact_finite_population_moments",
    }


def threshold_flags(n_male: int, n_female: int) -> dict[str,bool]:
    return {
        "paired_n2_eligible":n_male>=2 and n_female>=2,
        "paired_n3_eligible":n_male>=3 and n_female>=3,
        "paired_n5_eligible":n_male>=5 and n_female>=5,
    }
