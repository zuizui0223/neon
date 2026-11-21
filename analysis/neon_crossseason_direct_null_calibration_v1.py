#!/usr/bin/env python3
"""Post-result conditional product-null calibration of 14-site NEON statistic.

Uses private in-memory frozen-chain *standardized* null overlap values, not
W/B, density, taxon-vs-habitat regression or the sign-flip null. Keeps
original physical-site membership and EQUAL site weights.

IMPORTANT inferential limitation: randomising each season-B in different
units independently does not preserve covariance across pairs that share
a real seasonal observation. This is a transparent conditional product
null calibration, NOT an exact source-level joint null and NOT new
pre-registered confirmation of the 2026-10-19 positive ecological result.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from math import isfinite, sqrt
from random import Random
from statistics import mean, stdev


def _percentile(ordered: list[float], q: float) -> float:
    n=len(ordered)
    if n==1:
        return float(ordered[0])
    loc=(n-1)*q
    i=int(loc)
    alpha=loc-i
    return float(ordered[i]*(1-alpha)+ordered[min(i+1,n-1)]*alpha)


def season_sharing_diagnostic(units: list[dict]) -> dict:
    """Count reused season sources across pair roles without exporting IDs."""
    season_to_pairs=defaultdict(set)
    for idx,unit in enumerate(units):
        site=str(unit.get("site") or "")
        site_plot=unit.get("site_plot")
        season=unit.get("season_ordinal")
        if not site or not isinstance(site_plot,(list,tuple)) or len(site_plot)!=2:
            raise ValueError("private source site/plot identifiers are missing")
        if not isinstance(season,int):
            raise ValueError("original seasonal ordinal is missing")
        if str(site_plot[0])!=site:
            raise ValueError("site_plot must refer to original physical site")
        for ordinal in (season,season+1):
            season_to_pairs[(tuple(site_plot),ordinal)].add(idx)
    reused={key:members for key,members in season_to_pairs.items() if len(members)>1}
    involved_sites={key[0][0] for key in reused}
    return {
        "number_seasonal_units":len(units),
        "distinct_site_plot_season_keys":len(season_to_pairs),
        "season_keys_used_in_multiple_pair_roles":len(reused),
        "source_pair_roles_at_reused_seasons":sum(len(items) for items in reused.values()),
        "physical_sites_with_any_adjacent_pair_season_reuse":len(involved_sites),
        "joint_shared_season_covariance_not_preserved":True,
        "raw_site_plot_and_season_identifiers_exported":False,
    }


def reused_physical_site_ids_from_source_units(units: list[dict]) -> set[str]:
    """PRIVATE set of physical sites whose adjacent pairs reuse a season.

    Exclusively original source site×plot×season multiplicity is consulted.
    No observed Z, shuffled null effect or taxon outcome participates.
    Callers MUST output only its count, not source geographic identifiers.
    """
    source_key_counts=Counter()
    for item in units:
        site=str(item.get("site") or "")
        site_plot=item.get("site_plot")
        q=item.get("season_ordinal")
        if not site or not isinstance(site_plot,(tuple,list)) or len(site_plot)!=2:
            raise ValueError("No original source site/plot in reused-season guard")
        if not isinstance(q,int) or site_plot[0]!=site:
            raise ValueError("Site/season source mismatch in reused-season guard")
        original_plot=tuple(site_plot)
        source_key_counts[(original_plot,q)]+=1
        source_key_counts[(original_plot,q+1)]+=1
    return {
        site_plot[0]
        for (site_plot,_ordinal),uses in source_key_counts.items()
        if uses>1
    }


def direct_site_weighted_product_null(
    units: list[dict], *, seed: int=2026101902, n_replicates: int=100_000
) -> dict:
    """Draw independent unit null overlaps; average within then across sites.

    Expected input rows: {
      unit_index: immutable original sorted source index,
      site: private source physical site,
      observed_z: original frozen standardized overlap effect,
      null_z_draws: ephemeral same-chain overlap draws standardized by the
                    original frozen null mean & SD
    }
    Returns scalar distribution summaries only. No site IDs, original
    null vectors or biological labels are ever serialized.
    """
    if isinstance(seed,bool) or not isinstance(seed,int):
        raise ValueError("product-null random seed must be integer")
    if isinstance(n_replicates,bool) or not isinstance(n_replicates,int) or not (100<=n_replicates<=500000):
        raise ValueError("product-null Monte Carlo replicate count must be 100..500000")
    if not units:
        raise ValueError("at least one original matched-seasonal unit required")

    # Sorting by the source-stable numeric unit index makes the sampling
    # deterministic under records returned in any order; this index is
    # deliberately omitted from the result.
    ids=[]
    by_site=defaultdict(list)
    for unit in units:
        idx=unit.get("unit_index")
        site=unit.get("site")
        z=unit.get("observed_z")
        draws=unit.get("null_z_draws")
        if isinstance(idx,bool) or not isinstance(idx,int) or idx<0:
            raise ValueError("unit_index must be the original nonnegative source index")
        if not isinstance(site,str) or not site.strip():
            raise ValueError("source physical site required")
        if isinstance(z,bool) or not isinstance(z,(int,float)) or not isfinite(z):
            raise ValueError("finite original unit Z needed")
        if not isinstance(draws,(tuple,list)) or len(draws)<2:
            raise ValueError("at least two original null-chain draws needed")
        if any(isinstance(x,bool) or not isinstance(x,(float,int)) or not isfinite(x)
               for x in draws):
            raise ValueError("original null-chain draws must be finite")
        ids.append(idx)
        by_site[site].append(unit)
    if len(ids)!=len(set(ids)):
        raise ValueError("duplicate original source unit_index")

    n_sites=len(by_site)
    per_site_obs={}
    for site,items in by_site.items():
        per_site_obs[site]=mean(float(x["observed_z"]) for x in items)
    observed=float(mean(per_site_obs.values()))

    # Precompute unit weights once so every physical site has weight 1/S,
    # irrespective of whether it contributed 1 or 20 seasonal comparisons.
    weighted=[]
    for site in sorted(by_site):
        group=sorted(by_site[site],key=lambda x:x["unit_index"])
        weight=1.0/(n_sites*len(group))
        for item in group:
            weighted.append((item["null_z_draws"],weight))
    rng=Random(seed)
    scores=[]
    count_exceed=0
    for _rep in range(n_replicates):
        statistic=0.0
        for draws,w in weighted:
            statistic+=float(draws[rng.randrange(len(draws))])*w
        scores.append(statistic)
        if statistic>=observed-1e-12:
            count_exceed+=1
    sorted_scores=sorted(scores)
    p_plus_one=(count_exceed+1)/(n_replicates+1)
    # Binomial SE for the finite empirical-sample exceedance probability;
    # excludes dependence/mixing error in the underlying unit null chains.
    mc_se=sqrt(p_plus_one*(1-p_plus_one)/(n_replicates+1))
    return {
        "schema":"neon.crossseason.direct_site_weighted_product_null.v1",
        "status":"SECONDARY_CONDITIONAL_PRODUCT_NULL_CALIBRATED_NOT_INDEPENDENT_CONFIRMATION",
        "physical_sites":n_sites,
        "seasonal_units":len(units),
        "observed_equal_site_weighted_mean_z":observed,
        "one_sided_p_with_plus_one":float(p_plus_one),
        "upper_tail_exceedances":count_exceed,
        "monte_carlo_replicates":n_replicates,
        "monte_carlo_seed":seed,
        "monte_carlo_binomial_se_conditional":float(mc_se),
        "null_T_mean":float(mean(scores)),
        "null_T_sd":float(stdev(scores)),
        "null_T_quantile_025":_percentile(sorted_scores,0.025),
        "null_T_quantile_50":_percentile(sorted_scores,0.5),
        "null_T_quantile_95":_percentile(sorted_scores,0.95),
        "null_T_quantile_975":_percentile(sorted_scores,0.975),
        "site_means_weighted_equally":True,
        "unit_null_chain_vectors_retained_only_in_memory":True,
        "product_null_disallows_signflip_symmetry_assumption":True,
        "conditional_product_assumes_independent_unit_B_randomization":True,
        "overlapping_season_pair_covariance_not_preserved":True,
        "post_result_calibration_not_new_confirmatory_test":True,
        "genus_specific_detection_bias_excluded":False,
        "competition_or_habitat_mechanism_proven":False,
        "raw_source_labels_or_null_draw_arrays_exported":False,
        "original_preregistered_signflip_result_unchanged":True,
        "prior_density_W_B_effects_refitted":False,
    }
