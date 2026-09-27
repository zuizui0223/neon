from __future__ import annotations

import json
import random
import statistics
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"results"/"carrier_prevalence_response_v1.json"
OUT=ROOT/"results"/"carrier_turnover_vs_species_pool_fresh11_v1.json"


def jaccard(a, b) -> float:
    left=set(a)
    right=set(b)
    union=left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def mean_pairwise_jaccard(sets: list[list[str]]) -> float:
    values=[]
    for i in range(len(sets)):
        for j in range(i+1,len(sets)):
            values.append(jaccard(sets[i],sets[j]))
    return statistics.mean(values) if values else 0.0


def simulate_mean_carrier_jaccard(
    sites: list[dict[str, object]],
    *,
    replicates: int,
    seed: int,
) -> list[float]:
    rng=random.Random(seed)
    values=[]
    for _ in range(replicates):
        sampled=[]
        for site in sites:
            pool=list(site["pool"])
            k=int(site["carrier_count"])
            sampled.append(rng.sample(pool,k))
        values.append(mean_pairwise_jaccard(sampled))
    return values


def quantile(values: list[float], q: float) -> float:
    ordered=sorted(values)
    if not ordered:
        raise ValueError("values must be non-empty")
    index=int(q*(len(ordered)-1))
    return ordered[index]


def rank_average(values: list[float]) -> list[float]:
    order=sorted(range(len(values)),key=lambda i:values[i])
    ranks=[0.0]*len(values)
    i=0
    while i<len(order):
        j=i+1
        while j<len(order) and values[order[j]]==values[order[i]]:
            j+=1
        rank=(i+1+j)/2.0
        for k in range(i,j):
            ranks[order[k]]=rank
        i=j
    return ranks


def pearson(x: list[float], y: list[float]) -> float | None:
    if len(x)<3 or len(x)!=len(y):
        return None
    mx=statistics.mean(x)
    my=statistics.mean(y)
    dx=sum((v-mx)**2 for v in x) ** 0.5
    dy=sum((v-my)**2 for v in y) ** 0.5
    if dx==0 or dy==0:
        return None
    return sum((a-mx)*(b-my) for a,b in zip(x,y)) / (dx*dy)


def spearman(x: list[float], y: list[float]) -> float | None:
    return pearson(rank_average(x),rank_average(y))


def main() -> None:
    payload=json.loads(SOURCE.read_text(encoding="utf-8"))
    sites=[]
    for site in payload["site_results"]:
        pool=[
            row["scientific_name"]
            for row in site["species_results"]
        ]
        carriers=[
            row["scientific_name"]
            for row in site["species_results"]
            if int(row["observed_carrier"])==1
        ]
        sites.append({
            "site":site["site_code"],
            "pool":pool,
            "carriers":carriers,
            "carrier_count":len(carriers),
        })

    pair_rows=[]
    pool_values=[]
    carrier_values=[]
    differences=[]
    for i in range(len(sites)):
        for j in range(i+1,len(sites)):
            pool_j=jaccard(sites[i]["pool"],sites[j]["pool"])
            carrier_j=jaccard(sites[i]["carriers"],sites[j]["carriers"])
            diff=carrier_j-pool_j
            pool_values.append(pool_j)
            carrier_values.append(carrier_j)
            differences.append(diff)
            pair_rows.append({
                "site_a":sites[i]["site"],
                "site_b":sites[j]["site"],
                "species_pool_jaccard":pool_j,
                "carrier_jaccard":carrier_j,
                "carrier_minus_pool_jaccard":diff,
            })

    observed_mean=statistics.mean(carrier_values)
    simulations=simulate_mean_carrier_jaccard(
        sites,
        replicates=20000,
        seed=20260927,
    )
    null_mean=statistics.mean(simulations)
    p_lower=sum(v<=observed_mean+1e-15 for v in simulations)/len(simulations)
    p_higher=sum(v>=observed_mean-1e-15 for v in simulations)/len(simulations)

    out={
        "schema":"neon.carrier_turnover_vs_species_pool.fresh11.v1",
        "status":"posthoc_frozen-response_validity_audit",
        "scope":{
            "sites":len(sites),
            "site_pairs":len(pair_rows),
            "species_pool_definition":"eligible species already present in frozen fresh response (>=2 positive non-X trap nodes)",
            "carrier_definition":"observed_carrier == 1 in frozen fresh response",
            "new_biological_response_access":False,
        },
        "site_summary":[
            {
                "site_code":site["site"],
                "eligible_species_pool_size":len(site["pool"]),
                "carrier_count":site["carrier_count"],
            }
            for site in sites
        ],
        "pairwise_summary":{
            "species_pool_jaccard_median":statistics.median(pool_values),
            "species_pool_jaccard_mean":statistics.mean(pool_values),
            "species_pool_jaccard_zero_pairs":sum(v==0 for v in pool_values),
            "carrier_jaccard_median":statistics.median(carrier_values),
            "carrier_jaccard_mean":observed_mean,
            "carrier_jaccard_zero_pairs":sum(v==0 for v in carrier_values),
            "carrier_minus_pool_jaccard_median":statistics.median(differences),
            "carrier_minus_pool_jaccard_mean":statistics.mean(differences),
            "carrier_minus_pool_negative_pairs":sum(v<0 for v in differences),
            "carrier_minus_pool_zero_pairs":sum(v==0 for v in differences),
            "carrier_minus_pool_positive_pairs":sum(v>0 for v in differences),
            "spearman_species_pool_vs_carrier_jaccard":spearman(pool_values,carrier_values),
        },
        "pool_conditioned_null":{
            "replicates":len(simulations),
            "seed":20260927,
            "randomization":"within each site, sample the observed number of carriers uniformly from the frozen eligible species pool",
            "observed_mean_pairwise_carrier_jaccard":observed_mean,
            "null_mean":null_mean,
            "null_median":statistics.median(simulations),
            "null_q025":quantile(simulations,0.025),
            "null_q975":quantile(simulations,0.975),
            "one_sided_p_observed_overlap_lower_than_pool_conditioned_null":p_lower,
            "one_sided_p_observed_overlap_higher_than_pool_conditioned_null":p_higher,
        },
        "pairwise":pair_rows,
        "interpretation":{
            "supported":"Fresh-panel carrier turnover is not lower than expected after conditioning on biogeographic species-pool overlap and the observed number of carriers per site.",
            "not_supported":"Raw carrier-set Jaccard near zero is evidence of carrier-specific taxonomic replacement beyond ordinary species-pool turnover.",
            "boundary":"This audit directly covers the independent fresh 11-site panel. The original 16-site frozen result did not retain complete species identities in the repository summary, so extending this conditional comparison to those 16 sites would require reopening or reconstructing biological response and is not done here.",
        },
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out["pairwise_summary"],sort_keys=True))
    print(json.dumps(out["pool_conditioned_null"],sort_keys=True))


if __name__=="__main__":
    main()
