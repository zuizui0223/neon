#!/usr/bin/env python3
"""Fixed-fixed null for seasonal genus×trap recurrence after animal turnover.

Ecological primary endpoint, distinct from all past density/W/B hypotheses.
The original San Jacinto study suggested the *direction* but NEON data have
not been used to tune this direction or the frozen sampling criteria.

Input is a PRIVATE in-memory pair of genus→nominal-trap sets with shared
animals already excluded. Output contains ONLY aggregate statistics, never
animal IDs, site codes, genus names, or trap positions.
"""
from __future__ import annotations

from itertools import product
from math import sqrt
from random import Random
from statistics import mean, stdev

TRAPS=tuple(f"{chr(65+i)}{j}" for i in range(10) for j in range(1,11))
TRAP_INDEX={label:i for i,label in enumerate(TRAPS)}
ALL_BITS=(1<<len(TRAPS))-1


def _choose_bit(mask: int, rng: Random) -> int:
    """Choose one set bit uniformly without a 100-element allocation."""
    k=rng.randrange(mask.bit_count())
    for _ in range(k):
        mask&=mask-1
    return mask & -mask


def _single_swap(rows: list[int], rng: Random) -> bool:
    if len(rows)<2:
        return False
    i=rng.randrange(len(rows))
    j=rng.randrange(len(rows)-1)
    if j>=i:
        j+=1
    a,b=rows[i],rows[j]
    only_a=a & (ALL_BITS^b)
    only_b=b & (ALL_BITS^a)
    if only_a==0 or only_b==0:
        return False
    bit_a=_choose_bit(only_a,rng)
    bit_b=_choose_bit(only_b,rng)
    switch=bit_a|bit_b
    rows[i]^=switch
    rows[j]^=switch
    return True


def swap_fixed_margins(rows: list[int], rng: Random, *, max_proposals: int=30) -> int:
    """One accepted 2×2 swap, or zero if unavailable under capped proposals."""
    if max_proposals<1:
        raise ValueError("max_proposals must be positive")
    for _ in range(max_proposals):
        if _single_swap(rows,rng):
            return 1
    return 0


def _bits(labels: set[str]) -> int:
    bits=0
    for label in labels:
        if label not in TRAP_INDEX:
            raise ValueError("Genus occupancy contains noncanonical 10×10 trap")
        bits|=1<<TRAP_INDEX[label]
    return bits


def _overlap(left: list[int],right: list[int]) -> int:
    return sum((a&b).bit_count() for a,b in zip(left,right))


def _lag1(xs: list[int]) -> float:
    if len(xs)<4:
        return 0.
    avg=mean(xs)
    variance=sum((x-avg)**2 for x in xs)
    if variance<=0:
        return 0.
    return sum((x-avg)*(y-avg) for x,y in zip(xs[:-1],xs[1:]))/variance


def fixed_fixed_null_for_unit(
    A: dict[str,set[str]],
    B: dict[str,set[str]],
    *,
    seed: int,
    n_draws: int=2000,
    burn_in: int=1000,
    swaps_per_draw: int=40,
    min_effective_draws: int=200,
) -> dict:
    """Fixed margins: every genus row sum and individual trap column sum."""
    if not isinstance(A,dict) or not isinstance(B,dict) or set(A)!=set(B):
        raise ValueError("Same source genera required in both seasons")
    labels=sorted(A)
    if len(labels)<3:
        raise ValueError("Primary null requires >=3 genera")
    if any(len(A[g])<2 or len(B[g])<2 for g in labels):
        raise ValueError("Source unit fails frozen distinct trap-position support")
    if any(isinstance(z,bool) or not isinstance(z,int) for z in
           (seed,n_draws,burn_in,swaps_per_draw,min_effective_draws)):
        raise ValueError("MCMC configuration must contain integer inputs")
    if n_draws<5 or burn_in<0 or swaps_per_draw<1 or min_effective_draws<1:
        raise ValueError("Invalid fixed-fixed MCMC settings")
    original=[_bits(B[g]) for g in labels]
    fixed=[_bits(A[g]) for g in labels]
    current=original.copy()
    rng=Random(seed)
    accepted=0
    proposals=0
    # Capped accepted-swap process; never infinite-loop on a fixed matrix.
    def advance(nswaps):
        nonlocal accepted,proposals
        for _ in range(nswaps):
            success=False
            for _p in range(10000):
                proposals+=1
                if _single_swap(current,rng):
                    accepted+=1
                    success=True
                    break
            if not success:
                return False
        return True

    base={
        "schema":"neon.crossseason.fixedfixed_unit.v1",
        "source_genera":len(labels),
        "season_A_observed_genus_trap_cells":sum(z.bit_count() for z in fixed),
        "season_B_observed_genus_trap_cells":sum(z.bit_count() for z in original),
        "genus_and_trap_occupancy_margins_preserved":True,
        "site_independence_not_claimed":True,
        "original_animal_identifiers_and_trap_locations_exported":False,
    }
    observed=_overlap(fixed,original)
    if not advance(burn_in):
        return {
            **base,"status":"UNINFORMATIVE_NO_FIXED_FIXED_SWAPS",
            "observed_same_genus_same_trap_overlap":observed,
            "null_draws_requested":n_draws,
            "accepted_null_swaps":accepted,
            "swap_proposals":proposals,
            "z":None,
        }
    draws=[]
    for _ in range(n_draws):
        if not advance(swaps_per_draw):
            return {**base,"status":"UNINFORMATIVE_SWAP_PROCESS_STOP",
                    "observed_same_genus_same_trap_overlap":observed,
                    "null_draws_requested":n_draws,"accepted_null_swaps":accepted,
                    "swap_proposals":proposals,"z":None}
        draws.append(_overlap(fixed,current))
    sd=stdev(draws)
    avg=mean(draws)
    rho=_lag1(draws)
    rho_positive=max(0.,min(0.9999,rho))
    approx_ess=n_draws*(1-rho_positive)/(1+rho_positive)
    unit={
        **base,
        "observed_same_genus_same_trap_overlap":observed,
        "null_draws_requested":n_draws,
        "null_mean":float(avg),
        "null_sd":float(sd),
        "accepted_null_swaps":accepted,
        "swap_proposals":proposals,
        "swap_acceptance_rate":accepted/proposals if proposals else 0.,
        "lag1_overlap_autocorrelation":float(rho),
        "approx_effective_null_draws_lag1":float(approx_ess),
        "minimum_eligible_effective_draws":min_effective_draws,
    }
    if sd<=1e-12:
        return {**unit,"status":"UNINFORMATIVE_ZERO_NULL_VARIANCE","z":None}
    if approx_ess<min_effective_draws:
        return {**unit,"status":"UNINFORMATIVE_PERSISTENT_NULL_AUTOCORRELATION","z":None}
    return {
        **unit,
        "status":"INFORMATIVE_FIXED_FIXED_NULL",
        "z":float((observed-avg)/sd),
    }


def signflip_site_mean_test(site_means:list[float],*,seed:int=2026101901)->dict:
    """Physical-site sign-flip (exact <=18); not individual-season test."""
    if not site_means or not all(abs(x)<1e8 for x in site_means):
        raise ValueError("Need finite physical-site means")
    n=len(site_means)
    observed=mean(site_means)
    if n<=18:
        values=(sum(x*s for x,s in zip(site_means,signs))/n
                for signs in product((-1.,1.),repeat=n))
        extreme=sum(v>=observed-1e-12 for v in values)
        nsamples=2**n
        exact=True
        p=extreme/nsamples
    else:
        rng=Random(seed)
        nsamples=20000
        extreme=0
        for _ in range(nsamples):
            score=sum(x*(1 if rng.randrange(2) else -1)
                      for x in site_means)/n
            extreme+=score>=observed-1e-12
        exact=False
        p=(1+extreme)/(1+nsamples)
    return {
        "physical_sites":n,
        "site_mean_Z_mean":float(observed),
        "site_mean_Z_median":float(sorted(site_means)[n//2] if n%2 else
                                    (sorted(site_means)[n//2-1]+sorted(site_means)[n//2])/2),
        "positive_site_means":sum(x>0. for x in site_means),
        "one_sided_site_signflip_p":float(p),
        "signflip_samples":nsamples,
        "signflip_exact_given_site_statistics":exact,
    }


def crossseason_template_inference(
    site_z:dict[str,list[float]],
    *,
    seed:int=2026101901,
)->dict:
    """Aggregate only independent physical-site mean Z; redact site codes."""
    means=[]
    n_units=0
    for site,z in sorted(site_z.items()):
        if not z:
            continue
        if any(not isinstance(x,(int,float)) for x in z):
            raise ValueError("Only numeric site means are allowed")
        n_units+=len(z)
        means.append(float(mean(z)))
    if not means:
        return {
            "schema":"neon.crossseason_site_block_primary_test.v1",
            "status":"STOP_NO_INFORMATIVE_PHYSICAL_SITES",
            "physical_sites":0,"informative_seasonal_units":0,
            "ecological_site_level_criterion_passed":False,
            "site_names_exported":False,
        }
    test=signflip_site_mean_test(means,seed=seed)
    qualified=(len(means)>=8 and test["site_mean_Z_mean"]>0
               and test["one_sided_site_signflip_p"]<0.05)
    state=("SUPPORT_MULTI_SITE_GENUS_TEMPLATE_REASSEMBLY"
           if qualified else
           ("STOP_FEWER_THAN_8_INFORMATIVE_PHYSICAL_SITES"
            if len(means)<8 else "NOT_SUPPORTED_BY_FROZEN_SITE_TEST"))
    return {
        "schema":"neon.crossseason_site_block_primary_test.v1",
        "status":state,
        **test,
        "informative_seasonal_units":n_units,
        "site_Z_means_sorted_ascending":sorted(means),
        "site_names_exported":False,
        "site_level_inference_not_season_pair_pseudoreplication":True,
        "ecological_site_level_criterion_passed":qualified,
    }
