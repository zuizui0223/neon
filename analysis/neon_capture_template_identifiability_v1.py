#!/usr/bin/env python3
"""Source-free exact two-genus capture-template identifiability counterexample.

Synthetic algebra ONLY; no NEON ecological response is loaded or re-scored.
With each trap containing one observed genus in both seasons and with fixed
genus totals, stable genus-by-trap observation affinity may yield positive
conditional recurrence even when the two seasons' states are independent.
"""
from __future__ import annotations

import json
from math import exp, isfinite, lgamma, sqrt


def _logchoose(n: int, k: int) -> float:
    if k < 0 or k > n:
        return float("-inf")
    return lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)


def observation_only_counterexample(
    *, stations: int, genus1_stations: int, high_preference_stations: int,
    high_to_low_log_relative_odds: float,
) -> dict:
    """Exact expectation of two independent observed seasons, fixed margins.

    Within a season the observed genus-1 label subset S has fixed size a and
    Pr(S) proportional to exp(beta * number of high-affinity traps in S).
    Across seasons S_A and S_B are independent. beta is a synthetic persistent
    genus-by-station recording affinity, NOT empirical NEON detection p.
    """
    m, a, h, beta = stations, genus1_stations, high_preference_stations, high_to_low_log_relative_odds
    if any(type(x) is not int for x in (m, a, h)) or not (4 <= m <= 1000 and 1 <= a < m and 1 <= h < m):
        raise ValueError("Require 4<=stations<=1000, 1<=genus1_stations<stations and 1<=high<stations")
    if not isinstance(beta, (int, float)) or not isfinite(beta) or abs(beta) > 20:
        raise ValueError("Finite |log relative odds| <=20 required")
    low = m - h
    # K=number of high-affinity stations with observed genus-1 label.
    # This is the exact Fisher noncentral hypergeometric conditional law.
    logmass = [
        (k, _logchoose(h, k) + _logchoose(low, a - k) + beta * k)
        for k in range(max(0, a - low), min(a, h) + 1)
    ]
    largest = max(lv for _, lv in logmass)
    weights = [(k, exp(lv - largest)) for k, lv in logmass]
    denom = sum(w for _, w in weights)
    mean_high = sum(k * w for k, w in weights) / denom
    p_high = mean_high / h
    p_low = (a - mean_high) / low
    p_mean = a / m

    # Different seasons are independent GIVEN the persistent station affinity.
    # Both seasons have singleton observed genus richness at each station.
    expected_overlap = h * (p_high**2 + (1 - p_high)**2) + low * (p_low**2 + (1 - p_low)**2)
    uniform_null_mean = m - 2 * a + 2 * a * a / m
    # Under uniform fixed margins, overlap=m-2a+2K and K~Hypergeom(m,a,a).
    null_variance = 4 * a * (a / m) * (1 - a / m) * (m - a) / (m - 1)
    excess = expected_overlap - uniform_null_mean
    identity = 2 * (h * (p_high - p_mean)**2 + low * (p_low - p_mean)**2)
    if abs(excess - identity) > 1e-8:
        raise AssertionError("Station-affinity variance identity failed")
    return {
        "status": "SYNTHETIC_OBSERVATION_ONLY_COUNTEREXAMPLE_NOT_NEON_EFFECT",
        "singleton_stations": m,
        "genus1_stations_in_each_season": a,
        "high_preference_stations": h,
        "high_to_low_log_relative_odds": float(beta),
        "high_to_low_relative_odds": exp(beta),
        "genus1_record_probability_high": p_high,
        "genus1_record_probability_low": p_low,
        "uniform_fixed_margin_overlap_mean": uniform_null_mean,
        "uniform_fixed_margin_overlap_sd": sqrt(null_variance),
        "observation_only_expected_overlap": expected_overlap,
        "observation_only_expected_excess_overlap": excess,
        "observation_only_expected_z": excess / sqrt(null_variance),
        "between_season_true_use_memory_introduced": False,
        "between_season_observed_label_independent_given_station_affinity": True,
        "genus_detection_probability_estimated": False,
        "neon_capture_rows_read": 0,
    }


def reference_sweep() -> dict:
    """Illustrative source-free values, not fitted to any historical Z."""
    return {
        "scientific_decision": "OBSERVATION_ONLY_TEMPLATE_CAN_CREATE_POSITIVE_FIXED_MARGIN_Z",
        "hypothesis_boundary": "Does NOT show this mechanism caused NEON recurrence",
        "source": "SYNTHETIC_NO_SOURCE",
        "no_real_neon_response_opened": True,
        "illustrations": [
            observation_only_counterexample(
                stations=100, genus1_stations=50, high_preference_stations=50,
                high_to_low_log_relative_odds=beta,
            )
            for beta in (0.0, 0.5, 1.0, 1.5)
        ],
    }


if __name__ == "__main__":
    print(json.dumps(reference_sweep(), indent=2, sort_keys=True))
