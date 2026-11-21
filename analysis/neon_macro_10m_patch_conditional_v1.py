"""10 m patch-scale genus recurrence beyond fixed exact trap recurrence.

Mathematically exact *conditional* uniform two-row fixed-margin marginal
moments; direct IID exact-target samples for neighbor-score site calibration.
Condition on (i) season-B each genus station prevalence, (ii) each trap's
season-B genus richness, AND (iii) the actually observed same-genus
same-trap overlap. No old accepted-swap MCMC and no source IDs exported.

PRIMARY distance: 10 m rook (same column adjacent letter, or same letter
adjacent number); NO diagonal, no 20 m threshold fishing. NEON standard
10x10 10m nominal trap spacing documented in official mammal protocol.
"""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from math import comb,sqrt,isfinite
from random import Random

TRAPS=tuple(f"{chr(65+i)}{j}" for i in range(10) for j in range(1,11))
NEIGHBOR={}
for i in range(10):
    for j in range(1,11):
        t=f"{chr(65+i)}{j}"
        v=set()
        if i>0:v.add(f"{chr(65+i-1)}{j}")
        if i<9:v.add(f"{chr(65+i+1)}{j}")
        if j>1:v.add(f"{chr(65+i)}{j-1}")
        if j<10:v.add(f"{chr(65+i)}{j+1}")
        NEIGHBOR[t]=frozenset(v)


def _must(cond:bool,why:str):
    if not cond:raise ValueError("EXACT_10M_CONDITIONAL_PATCH_SOURCE_STOP: "+why)


def conditional_patch_profile(
    A:dict[str,set[str]],B:dict[str,set[str]]
)->dict:
    """Compute exact conditional S mean/variance WITHOUT observed patch S.

    Original fixed-station overlap O was already observed in the old
    exact-two 30-site analysis. Conditioning on O is intentionally
    response-informed relative to the OLD hypothesis, never claimed
    to be an independent pre-existing exposure.
    """
    _must(isinstance(A,dict) and isinstance(B,dict) and len(A)==2
          and set(A)==set(B),"Need exact same TWO genus rows")
    labels=sorted(A)
    _must(all(isinstance(A[g],set) and isinstance(B[g],set)
              and len(A[g])>=2 and len(B[g])>=2
              and A[g].issubset(TRAPS) and B[g].issubset(TRAPS)
              for g in labels),"Original genus station support invalid")
    g1,g2=labels
    b1,b2=B[g1],B[g2]
    both=b1&b2
    single=b1^b2
    a=len(b1-both)
    K1={t:int(bool(NEIGHBOR[t]&A[g1])) for t in TRAPS}
    K2={t:int(bool(NEIGHBOR[t]&A[g2])) for t in TRAPS}
    original_O=sum(len(A[g]&B[g]) for g in labels)
    overlap_fixed=sum(int(t in A[g1])+int(t in A[g2]) for t in both)
    overlap_fixed+=sum(int(t in A[g2]) for t in single)
    observed_weight=original_O-overlap_fixed
    patch_fixed=sum(K1[t]+K2[t] for t in both)
    patch_fixed+=sum(K2[t] for t in single)

    groups={w:[] for w in (-1,0,1)}
    for t in sorted(single):
        w=int(t in A[g1])-int(t in A[g2])
        v=K1[t]-K2[t]
        groups[w].append(v)
    n={w:len(groups[w]) for w in groups}
    configurations=[]
    total=0
    moment1=Fraction(0)
    moment2=Fraction(0)
    for km in range(n[-1]+1):
        for kp in range(n[1]+1):
            k0=a-km-kp
            if not 0<=k0<=n[0] or kp-km!=observed_weight:
                continue
            counts={-1:km,0:k0,1:kp}
            weight=comb(n[-1],km)*comb(n[0],k0)*comb(n[1],kp)
            if weight==0:continue
            expected=Fraction(patch_fixed)
            varwithin=Fraction(0)
            for w,values in groups.items():
                nn=len(values);kk=counts[w]
                if nn==0:
                    _must(kk==0,"No columns in null stratum")
                    continue
                totalv=sum(values)
                totalv2=sum(v*v for v in values)
                expected+=Fraction(kk*totalv,nn)
                if nn>=2 and kk:
                    varwithin+=(
                        Fraction(kk*(nn-kk),nn*(nn-1)) *
                        (totalv2-Fraction(totalv*totalv,nn))
                    )
            configurations.append((counts,weight))
            total+=weight
            moment1+=weight*expected
            moment2+=weight*(expected**2+varwithin)

    if not configurations or total<=0:
        raise ValueError("Exact observed original overlap outside conditioned margins")
    # Cross-check probability normalization by brute combinatorics;
    # conditional support must be a nonempty subset of C(m,a).
    _must(total<=comb(len(single),a),"Impossible conditional fixed-margin cardinality")
    mu=moment1/total
    var=moment2/total-mu*mu
    _must(var>=0,"Exact conditional patch variance negative")
    sd=sqrt(float(var))
    return {
        "schema":"neon.exact_two_genus_10m_patch_given_exact_station_overlap.v1",
        "status":"EXACT_CONDITIONAL_NEIGHBOR_VARIANCE_POSITIVE" if var>0 else "EXACT_CONDITIONAL_NEIGHBOR_VARIANCE_ZERO",
        "exact_conditioning_on_original_same_trap_overlap":True,
        "conditioned_fixed_original_overlap":original_O,
        "fixed_B_genus_and_station_richness_margins":True,
        "nominal_10m_rook_neighbor_excludes_self":True,
        "uniform_conditional_matrices":total,
        "nontrivial_conditional_selection_triples":len(configurations),
        "null_mean":float(mu),
        "null_sd":sd,
        "_private_groups":groups,
        "_private_configs":configurations,
        "_private_total":total,
        "_private_patch_fixed":patch_fixed,
    }


def observed_patch(A:dict[str,set[str]],B:dict[str,set[str]],profile:dict)->dict:
    """New neighborhood response is computed only AFTER cohort variance GO."""
    _must(profile["status"]=="EXACT_CONDITIONAL_NEIGHBOR_VARIANCE_POSITIVE",
          "No exact conditional patch variance")
    labels=sorted(A)
    stat=sum(
        sum(int(bool(NEIGHBOR[t]&A[g])) for t in B[g])
        for g in labels
    )
    z=(stat-profile["null_mean"])/profile["null_sd"]
    _must(isfinite(z),"Nonfinite exact conditioned neighborhood score")
    return {
        "observed_nearest_neighbor_10m_score":stat,
        "Z_patch_given_exact_station_overlap":z,
        "conditional_null_score_variance_positive":True,
    }


def iid_conditional_patch_null(
    profile:dict,*,seed:int,n_draws:int=2000
)->list[float]:
    """Direct IID conditional-uniform two-row assignments (no MCMC)."""
    _must(profile["status"]=="EXACT_CONDITIONAL_NEIGHBOR_VARIANCE_POSITIVE",
          "Cannot sample degenerate exact conditioned null")
    _must(isinstance(seed,int) and isinstance(n_draws,int) and n_draws>=100,
          "Fixed original seed/draw count required")
    rng=Random(seed)
    rows=profile["_private_configs"]
    mass=profile["_private_total"]
    groups=profile["_private_groups"]
    mu=profile["null_mean"]
    sd=profile["null_sd"]
    cumulative=[]
    n=0
    for counts,weight in rows:
        n+=weight
        cumulative.append((n,counts))
    _must(n==mass,"Exact conditional combinatorial weights drifted")
    out=[]
    for _ in range(n_draws):
        q=rng.randrange(mass)
        counts=next(counts for upto,counts in cumulative if q<upto)
        chosen_delta=0
        for w in (-1,0,1):
            k=counts[w]
            if k:
                chosen_delta+=sum(rng.sample(groups[w],k))
        score=profile["_private_patch_fixed"]+chosen_delta
        out.append((score-mu)/sd)
    return out


def geometry_coverage()->dict:
    """Source-independent physical structure (not any biological outcome)."""
    return {
        "station_count":len(TRAPS),
        "grid_neighbor_count_corner":len(NEIGHBOR["A1"]),
        "grid_neighbor_count_edge":len(NEIGHBOR["A5"]),
        "grid_neighbor_count_interior":len(NEIGHBOR["E5"]),
        "self_neighbor_count":sum(t in NEIGHBOR[t] for t in TRAPS),
        "all_rook_edges_undirected":sum(len(v) for v in NEIGHBOR.values())//2,
        "nominal_spacing_m":10,
    }
