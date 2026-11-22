"""Corrected lazy proposal-clock fixed-margin null; old results stay archived.

Randomly choose a row pair once per step. A rejected proposal is a step,
not something to resample until it moves. One-half laziness guarantees
aperiodicity. The row-pair swap probability is symmetric: the exclusive
set sizes are unchanged in the reverse move. Thus uniform fixed margins
is stationary. Finite running time still requires convergence diagnostics.
"""
from collections import defaultdict
from fractions import Fraction
from itertools import combinations, product
from math import sqrt
from random import Random
from statistics import mean, variance, stdev

TRAPS=tuple(f'{chr(65+i)}{j}' for i in range(10) for j in range(1,11))
INDEX={v:i for i,v in enumerate(TRAPS)}


def _bit(mask,rng):
    for _ in range(rng.randrange(mask.bit_count())):
        mask &= mask-1
    return mask & -mask


def proposal_step(rows,rng):
    """ONE lazy proposal, including holds/rejections; never retry to success."""
    if len(rows)<2:
        return False
    if rng.random()<0.5:
        return False
    i=rng.randrange(len(rows))
    j=rng.randrange(len(rows)-1)
    if j>=i:
        j+=1
    a=rows[i] & ~rows[j]
    b=rows[j] & ~rows[i]
    if not a or not b:
        return False
    bits=_bit(a,rng) | _bit(b,rng)
    rows[i] ^= bits
    rows[j] ^= bits
    return True


def exact_kernel(state,*,lazy=True):
    """Exact rational one-step kernel, for finite state validation only."""
    state=tuple(state)
    g=len(state)
    if g<2:
        return {state:Fraction(1)}
    out=defaultdict(Fraction)
    half=Fraction(1,2) if lazy else Fraction(1)
    out[state]+=1-half
    for i,j in combinations(range(g),2):
        a=state[i] & ~state[j]
        b=state[j] & ~state[i]
        mass=half/Fraction(g*(g-1),2)
        if not a or not b:
            out[state]+=mass
            continue
        aa=[1<<k for k in range(a.bit_length()) if a & (1<<k)]
        bb=[1<<k for k in range(b.bit_length()) if b & (1<<k)]
        for x,y in product(aa,bb):
            s=list(state)
            s[i] ^= x|y
            s[j] ^= x|y
            out[tuple(s)]+=mass/(len(aa)*len(bb))
    return dict(out)


def _rhat(chains):
    parts=[]
    for xs in chains:
        n=len(xs)//2
        parts.extend((xs[:n],xs[-n:]))
    n=len(parts[0])
    W=mean(variance(x) for x in parts)
    if W<=0:
        return None
    B=n*variance(mean(x) for x in parts)
    return sqrt(((n-1)/n*W+B/n)/W)


def _ess(xs):
    n=len(xs)
    v=variance(xs)
    if v<=0:
        return 0.
    b=max(10,int(sqrt(n)))
    k=n//b
    batches=[mean(xs[i*b:(i+1)*b]) for i in range(k)]
    asym=b*variance(batches)
    return float(min(n,n*v/asym)) if asym>0 else float(n)


def corrected_unit(A,B,*,seed,n_draws=2000,burn=10000,thin=100,min_ess=200,draws_out=None):
    """Two seeded chains; every hold counts. No source identifiers exported."""
    if not isinstance(A,dict) or set(A)!=set(B) or len(A)<3:
        raise ValueError('Need same >=3 genus rows')
    if any(not isinstance(x,int) or isinstance(x,bool) for x in (seed,n_draws,burn,thin,min_ess)):
        raise ValueError('Integer sampler settings required')
    if n_draws<20 or burn<0 or thin<1 or min_ess<1:
        raise ValueError('Invalid settings')
    labels=sorted(A)
    def bits(vals):
        if any(v not in INDEX for v in vals):
            raise ValueError('Noncanonical trap')
        return sum(1<<INDEX[v] for v in set(vals))
    left=[bits(A[g]) for g in labels]
    right=[bits(B[g]) for g in labels]
    if any(len(A[g])<2 or len(B[g])<2 for g in labels):
        raise ValueError('Original support fails')
    obs=sum((a&b).bit_count() for a,b in zip(left,right))
    chains=[]
    moves=0
    for c in range(2):
        rng=Random(seed+1_000_003*c)
        current=right.copy()
        for _ in range(burn):
            moves+=proposal_step(current,rng)
        xs=[]
        for _ in range(n_draws):
            for _ in range(thin):
                moves+=proposal_step(current,rng)
            xs.append(sum((a&b).bit_count() for a,b in zip(left,current)))
        assert [x.bit_count() for x in current]==[x.bit_count() for x in right]
        assert [sum(bool(x & (1<<j)) for x in current) for j in range(100)]==[sum(bool(x & (1<<j)) for x in right) for j in range(100)]
        chains.append(xs)
    flat=chains[0]+chains[1]
    sd=stdev(flat)
    mu=mean(flat)
    ess=[_ess(x) for x in chains]
    rh=_rhat(chains)
    good=sd>0 and rh is not None and rh<1.05 and min(ess)>=min_ess
    if draws_out is not None:
        draws_out.extend(flat)
    return {
        'schema':'neon.uniform_proposal_clock_unit.v2',
        'observed_overlap':obs,'source_genera':len(labels),
        'null_mean':float(mu),'null_sd':float(sd),
        'z':float((obs-mu)/sd) if sd>0 else None,
        'quality_pass':good,'split_Rhat':rh,
        'batch_means_ESS_per_chain':ess,
        'chains':2,'draws_per_chain':n_draws,
        'burn_proposals_per_chain':burn,'spacing_proposals':thin,
        'attempts_counted':2*(burn+n_draws*thin),'accepted_moves':moves,
        'all_rejected_proposals_and_lazy_holds_counted':True,
        'uniform_stationary_target_proven_by_symmetric_kernel':True,
        'finite_MCMC_output_not_exact_independent_uniform_draws':True,
        'no_source_identifiers_exported':True,
    }
