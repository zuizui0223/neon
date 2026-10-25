#!/usr/bin/env python3
"""Exact uniform fixed-margin conditional null for exactly TWO taxon rows.

All season-B matrices with given row totals and trap-column richness have
probability 1/C(m,a), where m is the number of singleton-genus trap columns
and a of them belong to the first taxon. Exact multivariate hypergeometric
overlap distribution, no MCMC approximation and NO old accepted-swap chain.

No private site/taxon/animal/station identifier is emitted by summaries.
"""
from __future__ import annotations
from collections import defaultdict
from math import comb, sqrt
from bisect import bisect_left
from random import Random
from statistics import mean,stdev
from typing import Callable

TRAPS={f"{chr(65+i)}{j}" for i in range(10) for j in range(1,11)}


def _check(A:dict[str,set[str]],B:dict[str,set[str]])->tuple[list[str],dict,dict]:
    if not isinstance(A,dict) or not isinstance(B,dict) or len(A)!=2 or set(A)!=set(B):
        raise ValueError("Exactly two identical taxon row identities required")
    labels=sorted(A)
    if any(not isinstance(A[g],set) or not isinstance(B[g],set)
           or len(A[g])<2 or len(B[g])<2
           or not A[g].issubset(TRAPS) or not B[g].issubset(TRAPS)
           for g in labels):
        raise ValueError("Original source trap and taxon support invalid")
    return labels,A,B


def two_row_exact_marginal(A:dict[str,set[str]],B:dict[str,set[str]])->dict:
    """No observed season-A×B overlap is calculated; variance first."""
    labels,A,B=_check(A,B)
    g1,g2=labels
    both=B[g1]&B[g2]
    singleton=B[g1]^B[g2]
    m=len(singleton)
    a=len(B[g1]-B[g2])
    if not 0<=a<=m:raise AssertionError("Fixed-margin row total invalid")
    npos=sum(int(t in A[g1]) - int(t in A[g2])==1 for t in singleton)
    nneg=sum(int(t in A[g1]) - int(t in A[g2])==-1 for t in singleton)
    nzero=m-npos-nneg
    base=sum(int(t in A[g1])+int(t in A[g2]) for t in both)
    base+=sum(t in A[g2] for t in singleton)
    mass=defaultdict(int)
    total=comb(m,a)
    for x in range(npos+1):
        for y in range(nneg+1):
            z=a-x-y
            if not 0<=z<=nzero:continue
            outcomes=comb(npos,x)*comb(nneg,y)*comb(nzero,z)
            if outcomes:
                mass[base+x-y]+=outcomes
    if sum(mass.values())!=total or not mass:
        raise AssertionError("Enumerated two-row hypergeometric mass invalid")
    keys=sorted(mass)
    mu=sum(k*mass[k] for k in keys)/total
    variance=sum((k-mu)**2*mass[k] for k in keys)/total
    sd=sqrt(max(0.0,variance))
    return {
        "status":("EXACT_NONDEGENERATE" if sd>1e-12 else "EXACT_ZERO_VARIANCE"),
        "n_singleton_columns":m,
        "n_forced_double_columns":len(both),
        "genus1_singleton_count":a,
        "n_singleton_weights_positive":npos,
        "n_singleton_weights_negative":nneg,
        "n_singleton_weights_zero":nzero,
        "total_uniform_fixed_margin_matrices":total,
        "null_mean":float(mu),
        "null_sd":float(sd),
        # Confidential raw marginal distribution stays in RAM and cannot
        # be persisted as per-site/taxon source-labelled tables.
        "_private_mass":dict(sorted(mass.items())),
        "exact_uniform_target_no_mcmc":True,
    }


def observed_exact_unit(
    A:dict[str,set[str]],B:dict[str,set[str]],marginal:dict
)->dict:
    """Must be called only after original source-wide variance support GO."""
    labels,_,_=_check(A,B)
    obs=sum(len(A[g]&B[g]) for g in labels)
    mass=marginal["_private_mass"]
    total=marginal["total_uniform_fixed_margin_matrices"]
    if not min(mass)<=obs<=max(mass):
        raise AssertionError("Observed source overlap outside exact null support")
    sd=marginal["null_sd"]
    if sd<=1e-12:
        return {"status":"EXACT_ZERO_VARIANCE","z":None,
                "exact_unit_tail_p":None}
    p=sum(count for k,count in mass.items() if k>=obs)/total
    return {
        "status":"EXACT_NONDEGENERATE",
        "z":(obs-marginal["null_mean"])/sd,
        "exact_unit_tail_p":p,
        "null_marginal_points":len(mass),
        "exact_uniform_target_no_mcmc":True,
    }


def quantile_sampler(marginal:dict)->Callable[[float],float]:
    """Exact marginal mass, floating threshold only for meta MC draws."""
    if marginal.get("status")!="EXACT_NONDEGENERATE":
        raise ValueError("Source null has zero variance")
    mu=marginal["null_mean"]
    sd=marginal["null_sd"]
    n=marginal["total_uniform_fixed_margin_matrices"]
    mass=marginal["_private_mass"]
    points=[]
    cut=[]
    cum=0
    for overlap,count in sorted(mass.items()):
        cum+=count
        points.append((overlap-mu)/sd)
        cut.append(cum/n)
    cut[-1]=1.0
    def sampler(q:float)->float:
        if not 0<=q<1:raise ValueError("Need finite unit interval")
        idx=bisect_left(cut,q)
        return points[min(idx,len(points)-1)]
    return sampler


def _summary_draws(values:list[float],obs:float)->dict:
    n=len(values)
    ordered=sorted(values)
    extreme=sum(v>=obs-1e-12 for v in values)
    def pct(q):
        pos=q*(n-1)
        lo=int(pos)
        hi=min(lo+1,n-1)
        w=pos-lo
        return ordered[lo]*(1-w)+ordered[hi]*w
    return {
        "draws":n,"exceedances":extreme,
        "one_sided_plus_one_p":(extreme+1)/(n+1),
        "null_mean":mean(values),
        "null_sd":stdev(values),
        "null_q025":pct(.025),
        "null_q975":pct(.975),
        "null_value_is_conditional_not_universal_site_dependence_bound":True,
        "monte_carlo_p_is_post_result_exploratory_not_independent_replication":True,
    }


def meta_exact_site_null(
    private:list[dict],*,seed:int=2026102501,n_replicates:int=20000
)->dict:
    """Site-weighted product and within-site rank-coupled fixed-margin meta null.

    private dicts: site, observed_z, exact_marginal. Never outputs site IDs.
    """
    if not isinstance(seed,int) or not isinstance(n_replicates,int) or n_replicates<200:
        raise ValueError("Explicit seed and adequate nested draws required")
    bysite=defaultdict(list)
    for unit in private:
        if not isinstance(unit.get("site"),str) or not unit["site"]:
            raise ValueError("Missing original physical-site block")
        obs=unit.get("observed_z")
        mar=unit.get("exact_marginal")
        if not isinstance(obs,(float,int)) or not isinstance(mar,dict):
            raise ValueError("Missing finite observed Z or exact private marginal")
        sample=quantile_sampler(mar)
        bysite[unit["site"]].append((obs,sample))
    if not bysite:raise ValueError("No informative original fixed-margin units")
    sites=sorted(bysite)
    observed=mean([mean(z for z,f in bysite[s]) for s in sites])
    ind=[];com=[]
    rng1=Random(seed)
    rng2=Random(seed+1)
    for _ in range(n_replicates):
        ind_t=com_t=0.0
        for s in sites:
            group=bysite[s]
            ind_t+=mean(f(rng1.random()) for z,f in group)
            common_q=rng2.random()
            com_t+=mean(f(common_q) for z,f in group)
        ind.append(ind_t/len(sites))
        com.append(com_t/len(sites))
    return {
        "sites":len(sites),"seasonal_pairs":len(private),
        "observed_equal_site_mean_z":observed,
        "independent_unit_exact_marginal_null":_summary_draws(ind,observed),
        "rank_comonotone_within_site_exact_marginal_stress":_summary_draws(com,observed),
        "site_ids_or_genus_names_exported":False,
        "not_an_actual_joint_site_ecological_null":True,
        "comonotone_not_a_proven_worst_case_bound":True,
        "two_row_unit_nulls_mathematically_exact":True,
    }
