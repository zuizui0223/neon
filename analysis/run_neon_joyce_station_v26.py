"""V26 source-native station-paired recorded fraction contrast.
V25 exact same-denominator design remains STOP. No source outcomes examined
when this alternative measurement estimand was specified.
"""
import argparse,csv,hashlib,io,json,math,pathlib,zipfile
from collections import defaultdict,Counter
from statistics import mean
from analysis.run_neon_joyce_early_late_v25 import fit_score
from analysis.run_neon_joyce_local_v25 import MANIFEST,parse_verified

def require(x,m):
    if not x:raise ValueError(m)
def parse(blob,name):
    rows=parse_verified(blob,name,MANIFEST[name])
    late=name=="seedling_establishment.csv"
    arm="exc" if late else "exclosure"
    y="seeds_established" if late else "seeds_remaining"
    z="seeds_failed" if late else "seeds_missing"
    out={}
    for r in rows:
        k=(r["site"],r["species"],r["trt"],int(r["station"]),r[arm])
        require(k[0] and k[1] in ("OCO_PUB","OTO_NOV","PSE_MOL","QUE_BEN") and k[2] in ("Restored","Remnant") and k[3] in (1,2,3,4) and k[4] in ("caged","exposed"),"invalid context")
        v=[int(r[x]) for x in ("seeds_total",y,z)]
        require(v[0] in (7,8,9,11) and min(v)>=0 and v[1]+v[2]==v[0] and k not in out,"invalid source count partition/key")
        out[k]=tuple(v)
    require(len(out)==(352 if late else 368) and sum(v[0] for v in out.values())==(2879 if late else 3024),"actual input support drift")
    return out
def analyze(e,l):
    require(set(l)<=set(e) and len(set(e)-set(l))==16 and {k[0] for k in set(e)-set(l)}=={"HB"},"unexpected final attrition")
    drift={k for k in l if e[k][0]!=l[k][0]}
    require(len(drift)==7,"known denominator discrepancy changed")
    contexts=defaultdict(list)
    for k in l:
        if k[-1]!="caged":continue
        q=k[:-1];a=q+("caged",);b=q+("exposed",)
        require(b in l,"unpaired station")
        rec={"station":q[3],"early":e[a][1]/e[a][0]-e[b][1]/e[b][0],"late":l[a][1]/l[a][0]-l[b][1]/l[b][0],
             "denom_drift":a in drift or b in drift}
        contexts[q[:3]].append(rec)
    require(sum(map(len,contexts.values()))==176 and len(contexts)==44 and len({k[0] for k in contexts})==8,"actual matched context drift")
    require(all(sorted(r["station"] for r in v)==[1,2,3,4] for v in contexts.values()),"incomplete four-station groups")
    # Equal station weights. Different denominators are explicit in each
    # observed rate; no attempt to reconstruct common cohorts.
    def recs(drop=False):
        r=[]
        for k,rr in sorted(contexts.items()):
            v=[q for q in rr if not(drop and q["denom_drift"])]
            require(len(v)>=3,"sensitivity has <3 paired stations in a group")
            r.append({"site":k[0],"stratum":(k[1],k[2]),"early":mean(q["early"] for q in v),"late":mean(q["late"] for q in v),"stations":len(v)})
        return r
    primary=recs()
    out={"status":"DESCRIPTIVE_PREDICTION_COMPLETE","strict_v25_status":"STOP_SOURCE_DENOMINATOR_DRIFT",
        "support":{"early_rows":len(e),"final_rows":len(l),"early_seeds_total":sum(v[0] for v in e.values()),"late_seeds_total":sum(v[0] for v in l.values()),"denominator_changed_rows":len(drift),"denominator_changed_station_pairs":sum(r["denom_drift"] for v in contexts.values() for r in v),"paired_stations":176,"site_species_forest_contexts":44,"physical_sites":8},
        "denominator_discrepancies":[{"key":list(k),"early_n":e[k][0],"late_n":l[k][0]} for k in sorted(drift)],
        "primary":fit_score(primary,False),"context_records":primary}
    try:
        sensitivity=recs(True)
        out["denom_matched_only_sensitivity"]={"status":"COMPLETE","station_pairs":sum(r["stations"] for r in sensitivity),"scores":fit_score(sensitivity,False)}
    except ValueError as ex:out["denom_matched_only_sensitivity"]={"status":"STOP","reason":str(ex)}
    out["boundary"]="Observed stage-specific caged-minus-exposed rate contrasts; same station keys, not necessarily same denominator or individual cohorts. Not confirmed irreversible loss, natural recruitment, season effect, or mammal-specific causal effect. Species/forest baseline only. One landscape, retrospective leave-site-out; no external temporal validation or p-values. Drop-mismatch sensitivity is not a rescue of V25."
    return out

def run(p):
    try:
        with zipfile.ZipFile(p) as z:
            files={}
            for name in MANIFEST:
                matches=[m for m in z.infolist() if not m.is_dir() and pathlib.PurePosixPath(m.filename).name==name]
                require(len(matches)==1 and matches[0].file_size==MANIFEST[name][0],"archive roster/size")
                with z.open(matches[0]) as f:files[name]=parse(f.read(MANIFEST[name][0]+1),name)
        out=analyze(files["seed_removal.csv"],files["seedling_establishment.csv"])
    except (ValueError,KeyError,OSError,zipfile.BadZipFile) as e:out={"status":"STOP","reason":str(e)}
    out["source_doi"]="10.5061/dryad.05qfttfb9"
    return out
def main():
    p=argparse.ArgumentParser();p.add_argument("--input",required=True);p.add_argument("--out",required=True)
    a=p.parse_args();out=run(a.input)
    pathlib.Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0 if out["status"]=="DESCRIPTIVE_PREDICTION_COMPLETE" else 2
if __name__=="__main__":raise SystemExit(main())
