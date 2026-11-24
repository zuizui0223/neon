"""Partial-identification contrasts for a paired seed-release experiment.

Four mutually exclusive categories at the same documented follow-up:
known intact cache, known embryo-damaged cache, known noncache, and unknown
fate. If a cache is confirmed but embryo status unknown, preserve it as
a fifth category. Unknowns are never automatically predation or dispersal.
"""
from fractions import Fraction
from statistics import mean

CATEGORIES=("intact","damaged","noncache","unknown","cache_embryo_unknown")
def metrics(n,counts):
    if type(n) is not int or n<=0 or set(counts)!=set(CATEGORIES):
        raise ValueError("INVALID_DENOMINATOR_OR_CATEGORY_SET")
    if any(type(v) is not int or v<0 for v in counts.values()) or sum(counts.values())!=n:
        raise ValueError("COUNTS_NOT_EXHAUSTIVE")
    i,d,u,e=(counts[k] for k in ("intact","damaged","unknown","cache_embryo_unknown"))
    def bounds(a,b):return (Fraction(a,n),Fraction(b,n))
    return {"cache":bounds(i+d+e,i+d+e+u),
            "intact":bounds(i,i+e+u),
            "damage":bounds(d,d+e+u),
            "known_cache":Fraction(i+d+e,n),"known_intact":Fraction(i,n),
            "known_damage":Fraction(d,n)}

def paired(mixed,mono):
    # Cumulative cache and intact-cache risks per ALL originally released seeds.
    a,b=metrics(30,mixed),metrics(60,mono)
    out={}
    for key in ("cache","intact","damage"):
        alo,ahi=a[key];blo,bhi=b[key]
        out[key+"_difference_bounds"]=(alo-bhi,ahi-blo)
        out[key+"_known_difference"]=a["known_"+key]-b["known_"+key]
    # At the latent complete-data level:
    # delta(cache)-delta(intact)=delta(damaged), including unknown assignments.
    # Bounding damage directly is tighter than subtracting marginal intervals.
    out["attenuation_difference_bounds"]=out["damage_difference_bounds"]
    return out

def summarize(stations):
    # Input only after source ontology confirms original 3 sites x 3 stations.
    if len(stations)!=3 or any(len(block)!=3 for block in stations):
        raise ValueError("ORIGINAL_3_BY_3_BLOCK_DESIGN_REQUIRED")
    groups=[[paired(mixed,mono) for mixed,mono in block] for block in stations]
    keys=list(groups[0][0])
    def av(xs):
        return mean(xs)
    site=[]
    for block in groups:
        site.append({k:tuple(av([s[k][j] for s in block]) for j in (0,1)) if k.endswith("bounds") else av([s[k] for s in block]) for k in keys})
    pooled={k:tuple(av([s[k][j] for s in site]) for j in (0,1)) if k.endswith("bounds") else av([s[k] for s in site]) for k in keys}
    # These are identification bounds, not confidence intervals or p values.
    robust=(pooled["cache_difference_bounds"][0]>0 and pooled["attenuation_difference_bounds"][0]>0
            and all(s["damage_known_difference"]>0 for s in site))
    def numeric(x):
        return [float(v) for v in x] if isinstance(x,tuple) else float(x)
    return {"status":"DESCRIPTIVE_CACHE_GAIN_AND_ATTENUATION_ROBUST_TO_UNKNOWN_FATE" if robust else "ROBUST_ATTENUATION_NOT_ESTABLISHED",
            "sites":3,"stations":9,"equal_site_weighted":{k:numeric(v) for k,v in pooled.items()},
            "sites_positive_known_damage_difference":sum(s["damage_known_difference"]>0 for s in site),
            "bounds_not_confidence_intervals":True,
            "intact_cache_not_germination_or_net_recruitment":True}
