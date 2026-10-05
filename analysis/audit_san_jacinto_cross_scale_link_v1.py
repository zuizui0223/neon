from __future__ import annotations
import argparse, itertools, json, math
from collections import defaultdict
from pathlib import Path
import numpy as np

SEED=2026100506
WITHIN_PERMUTATIONS=200000

def pearson(x,y):
    x=np.asarray(x,float); y=np.asarray(y,float)
    if len(x)<3 or np.std(x)==0 or np.std(y)==0: return None
    return float(np.corrcoef(x,y)[0,1])

def matched_rows(footprint, stage4):
    ses={x["id"]:x.get("ses") for x in stage4["night_first"] if x.get("analyzable") and isinstance(x.get("ses"),(int,float))}
    ref=set(stage4["primary"]["all_reference_segregated_ids"])
    out=[]
    for x in footprint["grid_seasons"]:
        z=x.get("z_observed")
        if isinstance(z,(int,float)) and x["id"] in ses:
            out.append({"id":x["id"],"grid":str(x["grid"]),"season":x["season"],"footprint_z":float(z),"community_ses":float(ses[x["id"]]),"stage4_reference":x["id"] in ref})
    return out

def grid_means(rows):
    g=defaultdict(list)
    for r in rows:g[r["grid"]].append(r)
    out=[]
    for grid,rr in sorted(g.items()):
        out.append({"grid":grid,"n_seasons":len(rr),
                    "mean_footprint_z":sum(x["footprint_z"] for x in rr)/len(rr),
                    "mean_community_ses":sum(x["community_ses"] for x in rr)/len(rr)})
    return out

def exact_between_grid_permutation(gm):
    x=np.array([r["mean_footprint_z"] for r in gm],float)
    y=np.array([r["mean_community_ses"] for r in gm],float)
    obs=pearson(x,y)
    vals=[]
    for p in itertools.permutations(y.tolist()):
        vals.append(pearson(x,p))
    vals=np.asarray(vals,float)
    return {"r":obs,"exact_one_sided_p_upper":float(np.mean(vals>=obs-1e-15)),"permutations":len(vals)}

def within_grid_center(rows):
    g=defaultdict(list)
    for r in rows:g[r["grid"]].append(r)
    out=[]
    for grid,rr in g.items():
        mx=sum(x["footprint_z"] for x in rr)/len(rr); my=sum(x["community_ses"] for x in rr)/len(rr)
        for x in rr: out.append({"grid":grid,"x":x["footprint_z"]-mx,"y":x["community_ses"]-my})
    return out,g

def within_grid_permutation(rows, nperm=WITHIN_PERMUTATIONS, seed=SEED):
    centered,groups=within_grid_center(rows)
    obs=pearson([r["x"] for r in centered],[r["y"] for r in centered])
    rng=np.random.default_rng(seed)
    x=[]; groups_idx=[]; y=[]
    offset=0
    for grid,rr in sorted(groups.items()):
        xv=np.array([r["footprint_z"] for r in rr],float); yv=np.array([r["community_ses"] for r in rr],float)
        xv=xv-xv.mean(); yv=yv-yv.mean()
        x.extend(xv.tolist()); y.extend(yv.tolist()); groups_idx.append(np.arange(offset,offset+len(rr))); offset+=len(rr)
    x=np.asarray(x); y=np.asarray(y)
    ge=0
    for _ in range(nperm):
        yp=y.copy()
        for idx in groups_idx:
            if len(idx)>1: yp[idx]=rng.permutation(yp[idx])
        r=pearson(x,yp)
        if r is not None and r>=obs-1e-15: ge+=1
    return {"r":obs,"monte_carlo_one_sided_p_upper":(ge+1)/(nperm+1),"permutations":nperm,"seed":seed}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--footprint",type=Path,required=True)
    ap.add_argument("--stage4",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    fp=json.loads(args.footprint.read_text()); s4=json.loads(args.stage4.read_text())
    rows=matched_rows(fp,s4); gm=grid_means(rows)
    ref=[r["footprint_z"] for r in rows if r["stage4_reference"]]
    non=[r["footprint_z"] for r in rows if not r["stage4_reference"]]
    result={
      "schema":"neon.san_jacinto_cross_scale_link_audit.v1",
      "status":"post_result_exploratory_non_rescuing",
      "matched_grid_seasons":len(rows),
      "overall":{"r":pearson([r["footprint_z"] for r in rows],[r["community_ses"] for r in rows])},
      "between_grid":{"grid_means":gm,**exact_between_grid_permutation(gm)},
      "within_grid_seasonal":within_grid_permutation(rows),
      "reference_contrast":{
        "reference_units_n":len(ref),"nonreference_units_n":len(non),
        "mean_footprint_z_reference":sum(ref)/len(ref),
        "mean_footprint_z_nonreference":sum(non)/len(non),
        "difference":sum(ref)/len(ref)-sum(non)/len(non)
      },
      "interpretation_boundary":"A strong between-grid link can arise from persistent habitat, species composition, competitor presence, or other grid-scale context. This audit does not identify the causal driver and does not convert the already-opened descriptive correlation into a confirmatory endpoint.",
      "claim_boundary":{"confirmatory":False,"causal":False,"species_pair_decomposition_opened":False,"new_threshold_search":False}
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__": main()
