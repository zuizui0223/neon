#!/usr/bin/env python3
"""Post-result direct fixed-fixed null propagation to independent NEON sites.

Directly samples each original source unit's recorded fixed-fixed null
overlaps (standardized with the original unit mean/SD). It does not assume
that site-level Z statistics are sign-symmetric under that null.

Two transparent coupling assumptions are reported: independently sampled
unit marginal nulls, and a comonotone within-physical-site coupling of
unit marginal null ranks. Neither is a full generative ecological model,
and neither changes the already archived original 14-site signflip test.

No raw source tags, seasons, trap positions, site IDs or null vectors are
included in returned JSON. Null draw arrays are in-memory only.
"""
from __future__ import annotations

from collections import defaultdict
from math import sqrt, isfinite
from random import Random
from statistics import mean, stdev


def _empirical_quantiles(values: list[float]) -> dict:
    if len(values)<2:
        raise ValueError("At least two calibrated null replicates required")
    x=sorted(values)
    def at(p:float)->float:
        position=p*(len(x)-1)
        lo=int(position)
        hi=min(len(x)-1,lo+1)
        weight=position-lo
        return x[lo]*(1-weight)+x[hi]*weight
    return {
        "q025":float(at(.025)),
        "q50":float(at(.5)),
        "q975":float(at(.975)),
        "q995":float(at(.995)),
    }


def _draw_summary(
    values: list[float], observed: float, *,
    n_sites:int,n_units:int,mode:str
)->dict:
    exceed=sum(v>=observed-1e-12 for v in values)
    b=len(values)
    p=(1+exceed)/(b+1)
    return {
        "null_coupling":mode,
        "sites":n_sites,
        "units":n_units,
        "null_meta_replicates":b,
        "extreme_null_meta_replicates":exceed,
        "one_sided_p":p,
        "mc_standard_error_approx":sqrt(p*(1-p)/(b+1)),
        "observed_equal_site_weighted_grand_mean_Z":float(observed),
        "null_mean_of_site_grand_statistic":float(mean(values)),
        "null_sd_of_site_grand_statistic":float(stdev(values)),
        "null_quantiles":_empirical_quantiles(values),
        "no_sign_symmetry_assumption_invoked":True,
        "not_independent_new_ecological_observations":True,
    }


def direct_site_null_calibration(
    units: list[dict],*,seed:int=2026101929,n_replicates:int=20000
) -> dict:
    """Calibrate original frozen site mean Z under two null couplings.

    units: source-internal records with:
      site (physical NEON site, never emitted)
      observed_unit_z (original unit Z)
      null_unit_z_draws (exact 2000 stored standardized fixed-fixed null
                         overlap draws, transient in RAM only)
    Standardized null draws must be based on each unit's ORIGINAL
    randomized overlap mean and sample SD, never a new selected null.
    """
    if not isinstance(seed,int) or not isinstance(n_replicates,int):
        raise ValueError("Null meta seed and replicate count must be integer")
    if n_replicates<100 or n_replicates>1000000:
        raise ValueError("Unexpected meta-null replicate count")
    if not units:
        raise ValueError("No original physical-site unit null draws available")

    by_site=defaultdict(list)
    n_draws=None
    for u in units:
        if not isinstance(u,dict):
            raise ValueError("Malformed private unit null record")
        site=u.get("site")
        obs=u.get("observed_unit_z")
        draws=u.get("null_unit_z_draws")
        if not isinstance(site,str) or not site or not isinstance(draws,list):
            raise ValueError("Null needs confidential physical site and private draw vector")
        if not isinstance(obs,(int,float)) or not isfinite(obs):
            raise ValueError("Observed unit Z must be finite")
        if len(draws)<5 or any(
            not isinstance(x,(int,float)) or isinstance(x,bool) or
            not isfinite(x) for x in draws
        ):
            raise ValueError("Unit marginal null draws must all be finite")
        if n_draws is None:
            n_draws=len(draws)
        if len(draws)!=n_draws:
            raise ValueError("Every original unit requires equal null draw count")
        by_site[site].append((float(obs),draws,sorted(draws)))

    sites=sorted(by_site)
    site_n=len(sites)
    units_n=sum(len(v) for v in by_site.values())
    observed=mean([mean([u[0] for u in by_site[site]]) for site in sites])
    rng_ind=Random(seed)
    rng_comono=Random(seed+1)
    independent=[]
    dependent=[]
    for _ in range(n_replicates):
        grand_ind=0.0
        grand_comono=0.0
        for site in sites:
            source_units=by_site[site]
            # Draw an independent null for each seasonal comparison,
            # conditionally on its frozen genus/trap marginal counts.
            total_ind=0.0
            for _obs,draws,_sorted in source_units:
                total_ind+=draws[rng_ind.randrange(n_draws)]
            grand_ind+=total_ind/len(source_units)
            # Worst-tail within-site stress: one quantile shared among
            # all source units at this site (strong marginal dependence).
            q=rng_comono.randrange(n_draws)
            grand_comono+=sum(v[2][q] for v in source_units)/len(source_units)
        independent.append(grand_ind/site_n)
        dependent.append(grand_comono/site_n)

    ind=_draw_summary(
        independent,observed,n_sites=site_n,n_units=units_n,
        mode="INDEPENDENT_UNIT_MARGINALS_CONDITIONAL_ON_FROZEN_SEASON_B_MARGINS",
    )
    coupled=_draw_summary(
        dependent,observed,n_sites=site_n,n_units=units_n,
        mode="COMONOTONE_SITEWISE_UNIT_NULL_QUANTILES_STRESS_TEST",
    )
    return {
        "schema":"neon.crossseason_direct_nested_fixedfixed_site_null.v1",
        "status":"POST_RESULT_DIRECT_SITE_NULL_CALIBRATED_NO_NEW_ECOLOGICAL_HYPOTHESIS",
        "random_seed_independent_unit_marginals":seed,
        "random_seed_comonotone_site_stress":seed+1,
        "source_independent_physical_sites":site_n,
        "source_original_seasonal_units":units_n,
        "original_unit_null_draws_per_unit":n_draws,
        "observed_equal_site_weighted_mean_Z":float(observed),
        "independent_unit_marginal_null":ind,
        "comonotone_within_site_marginal_null":coupled,
        "calibration_robust_at_0_05_under_both_couplings":(
            ind["one_sided_p"]<0.05 and coupled["one_sided_p"]<0.05
        ),
        "original_signflip_not_assumed_for_new_tests":True,
        "source_seasonal_unit_marginals_preserved":True,
        "within_site_dependence_not_ecologically_identified":True,
        "comonotone_is_not_a_proven_upper_bound_on_all_joint_ecological_nulls":True,
        "post_result_statistical_validation_not_a_second_independent_ecological_dataset":True,
        "raw_Neon_unit_samples_exported":False,
        "original_density_W_B_reestimated":False,
        "causal_habitat_filtering_or_competition_established":False,
    }
