from __future__ import annotations

import argparse, json, math
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path

import numpy as np

from analysis import inventory_neon_footprint_validation_v1 as source

MIN_NIGHTS=2
MIN_INDIVIDUALS_PER_SPECIES=3
MIN_SPECIES_PER_UNIT=3
MIN_INFORMATIVE_SITES=6
PERMUTATIONS=10_000
SEED=2026100511

def jaccard(a:frozenset[str],b:frozenset[str])->float:
    u=len(a|b)
    return 0.0 if u==0 else len(a&b)/u

def exact_signflip_p(site_means:list[float])->float|None:
    vals=[float(x) for x in site_means if math.isfinite(float(x))]
    if not vals: return None
    obs=sum(vals)/len(vals)
    ge=0
    total=1<<len(vals)
    for mask in range(total):
        s=0.0
        for i,v in enumerate(vals):
            s += v if ((mask>>i)&1) else -v
        if s/len(vals) >= obs-1e-15: ge+=1
    return ge/total

def permute_labels_within_sizes(labels:np.ndarray,sizes:np.ndarray,rng:np.random.Generator)->np.ndarray:
    out=labels.copy()
    for s in np.unique(sizes):
        idx=np.flatnonzero(sizes==s)
        if len(idx)>1: out[idx]=rng.permutation(out[idx])
    return out

def contrast(labels:np.ndarray,ii:np.ndarray,jj:np.ndarray,sims:np.ndarray)->tuple[float,float,float]:
    same=labels[ii]==labels[jj]
    if not np.any(same) or np.all(same): return math.nan,math.nan,math.nan
    con=float(np.mean(sims[same])); het=float(np.mean(sims[~same]))
    return con-het,con,het

def build_footprints(token:str)->tuple[list[dict],dict]:
    payload=source.post_query(token)
    files=source.inventory(payload)
    night={}
    file_bytes=0
    for f in [x for x in files if x["table"]=="mam_perplotnight"]:
        raw=source.download(f,token); file_bytes+=len(raw)
        _,rr=source.rows(raw)
        for r in rr:
            uid=source.clean(r.get("nightuid"))
            if not uid: continue
            meta={
              "site":f["site"],
              "plotID":source.clean(r.get("plotID")),
              "collectDate":source.clean(r.get("collectDate")),
              "eventID":source.clean(r.get("eventID")),
              "samplingMethod":source.clean(r.get("mammalGridSamplingMethod")),
            }
            if uid in night and night[uid]!=meta: raise RuntimeError(f"nightuid conflict {uid}")
            night[uid]=meta

    hist=defaultdict(list)
    counts=Counter()
    for f in [x for x in files if x["table"]=="mam_pertrapnight"]:
        raw=source.download(f,token); file_bytes+=len(raw)
        _,rr=source.rows(raw)
        for r in rr:
            if not source.is_capture(r.get("trapStatus","")): continue
            tag=source.clean(r.get("tagID")); tax=source.clean(r.get("taxonID"))
            rank=source.clean(r.get("taxonRank")).lower()
            coord=source.clean(r.get("trapCoordinate")); nuid=source.clean(r.get("nightuid"))
            if not tag or not tax or rank!="species" or not coord or "X" in coord.upper(): continue
            meta=night.get(nuid)
            if meta is None or not meta["eventID"] or not meta["plotID"] or not meta["collectDate"]: continue
            key=(f["site"],meta["plotID"],meta["eventID"],tag)
            hist[key].append({
              "date":meta["collectDate"],"coord":coord,"taxon":tax,
              "samplingMethod":meta["samplingMethod"],
            })
            counts["eligible_species_rank_capture_rows"]+=1

    footprints=[]
    inconsistent=0
    for (site,plot,event,tag),rr in sorted(hist.items()):
        taxa={x["taxon"] for x in rr}
        if len(taxa)!=1:
            inconsistent+=1; continue
        dates={x["date"] for x in rr}
        if len(dates)<MIN_NIGHTS: continue
        methods={x["samplingMethod"] for x in rr if x["samplingMethod"]}
        footprints.append({
          "site":site,"plotID":plot,"eventID":event,"tagID":tag,
          "taxonID":next(iter(taxa)),"night_count":len(dates),
          "footprint":frozenset(x["coord"] for x in rr),
          "samplingMethod":next(iter(methods)) if len(methods)==1 else None,
        })
    support={
      "downloaded_verified_bytes":file_bytes,
      "species_rank_capture_rows":counts["eligible_species_rank_capture_rows"],
      "multi_night_footprints_before_unit_filter":len(footprints),
      "taxonomically_inconsistent_tag_units_excluded":inconsistent,
    }
    return footprints,support

def prepare_units(footprints:list[dict])->list[dict]:
    by=defaultdict(list)
    for x in footprints:
        by[(x["site"],x["plotID"],x["eventID"])].append(x)
    out=[]
    for (site,plot,event),rr in sorted(by.items()):
        c=Counter(x["taxonID"] for x in rr)
        species=tuple(sorted(sp for sp,n in c.items() if n>=MIN_INDIVIDUALS_PER_SPECIES))
        if len(species)<MIN_SPECIES_PER_UNIT: continue
        kept=[x for x in rr if x["taxonID"] in species]
        index={sp:i for i,sp in enumerate(species)}
        labels=np.asarray([index[x["taxonID"]] for x in kept],dtype=np.int16)
        sizes=np.asarray([len(x["footprint"]) for x in kept],dtype=np.int16)
        fps=[x["footprint"] for x in kept]
        ii,jj=np.triu_indices(len(kept),1)
        sims=np.asarray([jaccard(fps[i],fps[j]) for i,j in zip(ii,jj)],dtype=float)
        methods={x["samplingMethod"] for x in kept if x["samplingMethod"]}
        out.append({
          "id":f"{site}|{plot}|{event}","site":site,"plotID":plot,"eventID":event,
          "species":species,"rows":kept,"labels":labels,"sizes":sizes,
          "ii":ii,"jj":jj,"sims":sims,
          "samplingMethod":next(iter(methods)) if len(methods)==1 else None,
        })
    return out

def run_test(footprints:list[dict],support:dict,permutations:int=PERMUTATIONS,seed:int=SEED)->dict:
    if permutations<100: raise ValueError("permutations must be >=100")
    units=prepare_units(footprints)
    rng=np.random.default_rng(seed)
    summaries=[]; nulls=[]; informative=[]
    for ui,u in enumerate(units):
        obs,con,het=contrast(u["labels"],u["ii"],u["jj"],u["sims"])
        vals=np.empty(permutations,dtype=float)
        for b in range(permutations):
            lab=permute_labels_within_sizes(u["labels"],u["sizes"],rng)
            vals[b]=contrast(lab,u["ii"],u["jj"],u["sims"])[0]
        finite=vals[np.isfinite(vals)]
        mu=float(np.mean(finite)) if finite.size else math.nan
        sd=float(np.std(finite,ddof=0)) if finite.size else math.nan
        z=(obs-mu)/sd if math.isfinite(obs) and math.isfinite(sd) and sd>0 else None
        if z is not None: informative.append(ui)
        nulls.append(vals)
        summaries.append({
          "id":u["id"],"site":u["site"],"plotID":u["plotID"],"eventID":u["eventID"],
          "eligible_species":list(u["species"]),"multi_night_individuals":len(u["rows"]),
          "individuals_by_species":dict(sorted(Counter(x["taxonID"] for x in u["rows"]).items())),
          "footprint_size_distribution":{str(k):v for k,v in sorted(Counter(int(x) for x in u["sizes"]).items())},
          "sampling_method":u["samplingMethod"],
          "observed_mean_conspecific_jaccard":con,
          "observed_mean_heterospecific_jaccard":het,
          "observed_difference":obs,"null_mean_difference":mu,"null_sd_difference":sd,
          "z_observed":z,
        })

    site_units=defaultdict(list)
    for i in informative: site_units[units[i]["site"]].append(i)
    informative_sites=sorted(site_units)
    site_means={}
    for s in informative_sites:
        site_means[s]=float(np.mean([
          summaries[i]["z_observed"] for i in site_units[s]
        ]))
    t_obs=float(np.mean(list(site_means.values()))) if site_means else None

    if site_means:
        mus={}; sds={}
        for i in informative:
            finite=nulls[i][np.isfinite(nulls[i])]
            mus[i]=float(np.mean(finite)); sds[i]=float(np.std(finite,ddof=0))
        t_null=np.empty(permutations,dtype=float)
        for b in range(permutations):
            sm=[]
            for s in informative_sites:
                zvals=[]
                for i in site_units[s]:
                    v=nulls[i][b]
                    if math.isfinite(v): zvals.append((v-mus[i])/sds[i])
                if zvals: sm.append(float(np.mean(zvals)))
            t_null[b]=float(np.mean(sm)) if sm else math.nan
        ft=t_null[np.isfinite(t_null)]
        p=(int(np.sum(ft>=t_obs-1e-15))+1)/(len(ft)+1)
        null_mean=float(np.mean(ft)); null_sd=float(np.std(ft,ddof=0))
    else:
        p=null_mean=null_sd=None

    signflip=exact_signflip_p(list(site_means.values()))
    primary_pass=(
      len(informative_sites)>=MIN_INFORMATIVE_SITES and t_obs is not None and t_obs>0
      and p is not None and p<0.05
    )
    robust=primary_pass and signflip is not None and signflip<0.05
    decision=(
      "strong_independent_replication_species_specific_multinight_footprints" if robust
      else "unit_level_signal_without_site_robustness" if primary_pass
      else "stop_no_independent_footprint_replication"
    )
    fpdist=Counter(len(x["footprint"]) for x in footprints)
    eligible_ids={x["id"] for x in summaries}
    eligible_n=sum(len(units[i]["rows"]) for i in range(len(units)))
    unit_z=[summaries[i]["z_observed"] for i in informative]
    return {
      "schema":"neon.independent_footprint_assortativity.v1",
      "status":"stage1_frozen_replication_complete",
      "source":{"product":source.PRODUCT,"release":source.RELEASE,"fixed_sites":list(source.SITES)},
      "frozen_design":"docs/NEON_INDEPENDENT_FOOTPRINT_VALIDATION_V1.md",
      "design":{
        "unit":"site x plotID x eventID",
        "minimum_distinct_nights":MIN_NIGHTS,
        "taxon_rank":"species only",
        "minimum_multinight_individuals_per_species_unit":MIN_INDIVIDUALS_PER_SPECIES,
        "minimum_species_per_unit":MIN_SPECIES_PER_UNIT,
        "pair_similarity":"Jaccard",
        "unit_statistic":"mean conspecific Jaccard minus mean heterospecific Jaccard",
        "null":"shuffle species labels within exact individual footprint-size strata inside unit",
        "permutations":permutations,"seed":seed,
        "global_weighting":"equal physical site after averaging standardized unit effects",
      },
      "support":{
        **support,
        "eligible_units":len(units),
        "informative_units_nonzero_null_sd":len(informative),
        "informative_sites":len(informative_sites),
        "eligible_multinight_individual_rows":eligible_n,
        "footprint_size_distribution_before_unit_filter":{str(k):v for k,v in sorted(fpdist.items())},
      },
      "primary":{
        "equal_site_mean_standardized_footprint_assortativity":t_obs,
        "null_global_mean":null_mean,"null_global_sd":null_sd,
        "one_sided_monte_carlo_p_upper":p,
        "minimum_informative_sites":MIN_INFORMATIVE_SITES,
        "site_mean_z":site_means,
        "exact_one_sided_site_signflip_p":signflip,
        "unit_weighted_mean_z_descriptive":float(np.mean(unit_z)) if unit_z else None,
        "positive_raw_difference_units":sum(
          s["observed_difference"] is not None and s["observed_difference"]>0 for s in summaries
        ),
        "decision":decision,
      },
      "units":summaries,
      "claim_boundary":{
        "species_pair_decomposition_opened":False,
        "habitat_split_opened":False,
        "alternative_overlap_metric_opened":False,
        "alternative_thresholds_opened":False,
        "interpretation_if_strong_replication":(
          "Across an independent standardized North American small-mammal network, "
          "same-species individuals repeatedly use more similar multi-night trap-use footprints "
          "than different-species individuals after exact control for footprint size."
        )
      }
    }

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--permutations",type=int,default=PERMUTATIONS)
    ap.add_argument("--seed",type=int,default=SEED)
    args=ap.parse_args()
    token=__import__("os").environ.get(source.TOKEN_ENV,"").strip()
    if not token: raise RuntimeError("NEON_API_TOKEN missing")
    fp,support=build_footprints(token)
    result=run_test(fp,support,args.permutations,args.seed)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"support":result["support"],"primary":result["primary"]},indent=2,sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
