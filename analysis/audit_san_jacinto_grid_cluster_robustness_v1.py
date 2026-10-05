from __future__ import annotations
import argparse, itertools, json, math
from collections import defaultdict
from pathlib import Path

def grid_means(rows, value_key):
    by=defaultdict(list)
    for r in rows:
        v=r.get(value_key)
        if isinstance(v,(int,float)) and math.isfinite(float(v)):
            by[str(r["grid"])].append(float(v))
    return {g: sum(v)/len(v) for g,v in sorted(by.items()) if v}

def exact_signflip(values):
    vals=list(values)
    obs=sum(vals)/len(vals)
    stats=[]
    for signs in itertools.product((-1.0,1.0), repeat=len(vals)):
        stats.append(sum(s*v for s,v in zip(signs,vals))/len(vals))
    ge=sum(x>=obs-1e-15 for x in stats)
    return {
        "observed_mean_grid_cluster_statistic":obs,
        "exact_one_sided_p_upper":ge/len(stats),
        "sign_patterns":len(stats),
        "positive_grid_clusters":sum(v>0 for v in vals),
        "negative_grid_clusters":sum(v<0 for v in vals),
        "zero_grid_clusters":sum(v==0 for v in vals),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--footprint",type=Path,required=True)
    ap.add_argument("--persistence",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    footprint=json.loads(args.footprint.read_text())
    persistence=json.loads(args.persistence.read_text())

    fp_means=grid_means(footprint["grid_seasons"],"z_observed")
    ps_means=grid_means(persistence["units"],"z")

    result={
      "schema":"neon.san_jacinto_grid_cluster_robustness.v1",
      "status":"post_result_non_rescuing_cluster_robustness",
      "purpose":"Check whether positive temporal-persistence and individual-footprint signals survive equal weighting at the physical-grid level rather than treating repeated seasons as independent replicates.",
      "method":"Within each analysis, average standardized unit effects within physical grid, then enumerate all 2^G joint sign flips of the G grid-level means. Upper-tail p is the exact fraction of sign patterns with mean at least the observed mean.",
      "footprint_assortativity":{
        "grid_means":fp_means,
        **exact_signflip(list(fp_means.values()))
      },
      "temporal_persistence":{
        "grid_means":ps_means,
        **exact_signflip(list(ps_means.values()))
      },
      "claim_boundary":{
        "confirmatory":False,
        "can_rescue_failed_route":False,
        "species_pair_decomposition_opened":False,
        "new_ecological_endpoint_opened":False,
        "assumption":"The exact sign-flip audit treats the grid-level null contrast as sign-symmetric around zero; it is a conservative cluster-level robustness diagnostic rather than the primary permutation test."
      }
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
