"""Matched reproductive seasonality across species, independent of litter data.

No inference of reproductive onset, competition, coexistence or resource
mechanism. Fixed calendar windows and shared observed plots. Outcome is
captured adult females with literal pregnant/not status.
"""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from itertools import combinations
from fractions import Fraction
from statistics import mean
import argparse,json,os,re
from pathlib import Path
from analysis.audit_neon_seedfall_mammal_breeding_support_v1 import ROOT,TOKEN_ENV,batch,rows,d,t,known,req
from analysis.audit_neon_seedfall_mammal_breeding_sharded_v2 import source,expected,manifest_pin_digest,merge_numeric
from analysis.audit_neon_crossseason_genus_support_v1 import _events,_normal_coord,_normal_tag
from analysis.audit_multiscale_density_mnka_variation_v1 import _taxonomy
BUILD=ROOT/"build"
SHARD="neon.matched_species_pregnancy_season.shard.v1"
SCHEMA="neon.matched_species_pregnancy_season.v1"
CAPTURE={"5 - capture","4 - more than 1 capture in one trap"}
NO_REPLACE={"","NA","N/A","NULL","NONE","NAN","N","NO","FALSE","0"}
MIN_KNOWN=5
PHASES=("early","late")
def phase(day):
    return "early" if day.month in (5,6) else "late" if day.month in (8,9) else None
def sign(x):return (x>0)-(x<0)

def collect(files,token,targets,names):
    pp=[];captures=defaultdict(list);effort=defaultdict(set)
    identity=defaultdict(set);replaced=defaultdict(set);issues=Counter()
    for meta,raw in batch(files,token):
        _,it=rows(raw);s=meta["site"]
        if meta["table"]=="mam_perplotnight":
            for x in it:
                req(t(x.get("siteID"))==s,"PLOT_SITE_MISMATCH")
                day=d(x.get("collectDate"))
                if not day or phase(day) is None:continue
                pp.append({"_site":s,"siteID":s,"plotID":t(x.get("plotID")),
                    "eventID":t(x.get("eventID")),"nightuid":t(x.get("nightuid")),
                    "collectDate":day.isoformat(),"gridCompletion":t(x.get("gridCompletion"))})
            continue
        for x in it:
            req(t(x.get("siteID"))==s,"TRAP_SITE_MISMATCH")
            day=d(x.get("collectDate"));pl=t(x.get("plotID"));night=t(x.get("nightuid"))
            if not day or not pl or not night:issues["invalid_capture_context"]+=1;continue
            k=(s,pl,night);coord=_normal_coord(x.get("trapCoordinate"))
            if phase(day) and coord:effort[k].add(coord)
            if t(x.get("trapStatus")).lower() not in CAPTURE:continue
            tag=_normal_tag(x.get("tagID"))
            if not tag:issues["capture_without_tag"]+=1;continue
            tax=t(x.get("taxonID"));sx=t(x.get("sex")).upper()
            rp=t(x.get("replacedTag"))
            if rp.upper() not in NO_REPLACE:
                replaced[s,day.year].add(tag)
                if _normal_tag(rp):replaced[s,day.year].add(rp)
            # Identity conflicts are checked across all downloaded dates
            # in the site-year, not just the response window.
            if known(tax) and sx in {"F","M"}:identity[s,day.year,tag].add((tax,sx))
            if phase(day) is None or tax not in targets or sx!="F" or t(x.get("lifeStage")).lower()!="adult":continue
            name=t(x.get("scientificName"));canonical=names.get(tax)
            if t(x.get("taxonRank")).lower()!="species" or name!=canonical or not re.fullmatch(r"[A-Z][a-z]+ [a-z][a-z-]+",name):
                issues["not_exact_target_binomial"]+=1;continue
            if not coord:issues["capture_noncanonical_trap"]+=1;continue
            pr=t(x.get("pregnancyStatus")).lower()
            captures[k].append((day,tag,tax,name,pr if pr in {"pregnant","not"} else "unknown"))
    _,rej,approved=_events(pp);issues.update({"event_"+k:v for k,v in rej.items()})
    candidates=defaultdict(list)
    for (s,pl,e),v in approved.items():
        phases={phase(a) for a in v["dates"]}
        if len(phases)!=1 or None in phases:continue
        if not all(len(effort[s,pl,n])>=90 for n in v["nights"]):
            issues["low_effort_event"]+=1;continue
        ph=next(iter(phases));y=v["first"].year
        candidates[s,y,pl,ph].append(v)
    selected={}
    for k,events in candidates.items():
        s,y,pl,ph=k
        v=min(events,key=lambda z:(z["first"],z["event"]))
        obs=[]
        for n in v["nights"]:
            for rec in captures[s,pl,n]:
                day,tag,tax,name,pr=rec
                if day not in v["dates"]:
                    issues["capture_event_date_mismatch"]+=1;continue
                if len(identity[s,y,tag])!=1 or tag in replaced[s,y]:
                    issues["ambiguous_or_replaced_tag"]+=1;continue
                obs.append(rec)
        selected[k]=obs
    return selected,dict(issues)

def tally(records):
    bytag=defaultdict(list)
    for day,tag,tax,name,pr in records:bytag[tag].append((day,tax,name,pr))
    out=defaultdict(Counter)
    for v in bytag.values():
        ids={(x[1],x[2]) for x in v}
        if len(ids)!=1:continue
        tax,name=next(iter(ids));first=min(x[0] for x in v)
        st={x[3] for x in v if x[0]==first}
        out[(tax,name)][next(iter(st)) if len(st)==1 else "unknown"]+=1
    return out

def risk(v):
    a=v["pregnant"];n=a+v["not"];u=v["unknown"]
    if n<MIN_KNOWN:return None
    return (Fraction(a,n),Fraction(a,n+u),Fraction(a+u,n+u))

def contrasts(selected,sites):
    sy=defaultdict(set)
    for s,y,pl,ph in selected:sy[s,y].add(pl)
    diagnostics=Counter();by_site=defaultdict(lambda:defaultdict(list))
    for (s,y),plots in sorted(sy.items()):
        common=[pl for pl in sorted(plots) if all((s,y,pl,ph) in selected for ph in PHASES)]
        diagnostics["site_years_with_paired_plot_windows"]+=int(bool(common))
        diagnostics["paired_plot_years"]+=len(common)
        pairplots=defaultdict(list)
        for pl in common:
            spp=[]
            for ph in PHASES:
                # Require an observed tagged adult female for each taxon
                # in both selected bouts, not inferred absence or breeding zero.
                spp.append({(x[2],x[3]) for x in selected[s,y,pl,ph]})
            for pair in combinations(sorted(spp[0]&spp[1]),2):
                pairplots[pair].append(pl)
        for pair,ps in sorted(pairplots.items()):
            counts={ph:tally([rec for pl in ps for rec in selected[s,y,pl,ph]]) for ph in PHASES}
            a,b=pair
            ae,al,be,bl=(risk(counts[ph].get(sp,Counter())) for sp,ph in ((a,"early"),(a,"late"),(b,"early"),(b,"late")))
            diagnostics["observed_pair_site_years"]+=1
            if any(v is None for v in (ae,al,be,bl)):
                diagnostics["insufficient_known_status"]+=1;continue
            val=al[0]-ae[0]-bl[0]+be[0]
            lo=al[1]-ae[2]-bl[2]+be[1];hi=al[2]-ae[1]-bl[1]+be[2]
            req(lo<=val<=hi,"UNKNOWN_STATUS_BOUND_INVARIANT")
            pairkey=(a,b)
            by_site[s][pairkey].append((val,lo,hi))
            diagnostics["eligible_pair_site_years"]+=1
    out=[]
    for site in sorted(sites):
        pairs=[]
        for (a,b),v in sorted(by_site[site].items()):
            avg=[mean(z[j] for z in v) for j in range(3)]
            pairs.append({"species_a":[*a],"species_b":[*b],"years":len(v),
                "mean_D":float(avg[0]),"unknown_lo":float(avg[1]),"unknown_hi":float(avg[2]),
                "positive_years":sum(z[0]>0 for z in v),"negative_years":sum(z[0]<0 for z in v)})
        out.append({"pairs":pairs})
    return out,dict(diagnostics)

def aggregate(sites):
    support=defaultdict(list);n_year=0
    for i,s in enumerate(sites):
        seen=set()
        for x in s["pairs"]:
            a,b=tuple(x["species_a"]),tuple(x["species_b"]);k=(a,b)
            req(a<b and k not in seen and x["years"]>=1,"PAIR_ROSTER_INVALID")
            seen.add(k);n_year+=x["years"]
            if x["years"]>=2:support[k].append((i,x))
    repeated={k:v for k,v in support.items() if len(v)>=3}
    by_site=defaultdict(list);pairresults=[]
    for (a,b),v in sorted(repeated.items()):
        outcomes=[]
        for idx,x in v:
            pred=mean(z["mean_D"] for j,z in v if j!=idx)
            obs=x["mean_D"]
            # Ties are included as non-agreements, not filtered out.
            agree=int(sign(pred)!=0 and sign(pred)==sign(obs))
            sq=(pred-obs)**2;base=obs**2
            robust=int((pred>0 and x["unknown_lo"]>0) or (pred<0 and x["unknown_hi"]<0))
            by_site[idx].append((agree,sq,base,robust))
            outcomes.append((agree,sq,base,robust))
        pairresults.append({"species_a":a[1],"species_b":b[1],"sites":len(v),"years_total":sum(x["years"] for i,x in v),
            "equal_site_mean_D":mean(x["mean_D"] for i,x in v),
            "unknown_status_bounds":[mean(x["unknown_lo"] for i,x in v),mean(x["unknown_hi"] for i,x in v)],
            "heldout_site_sign_agreement":mean(x[0] for x in outcomes)})
    out={"sites_with_any_eligible_pair":sum(bool(s["pairs"]) for s in sites),"eligible_pair_site_years":n_year,
        "repeated_site_pair_count":sum(len(v) for v in support.values()),
        "species_pairs_with_at_least_three_repeated_sites":len(repeated),
        "heldout_evaluable_sites":len(by_site),"heldout_site_pair_count":sum(map(len,by_site.values())),"effect":None}
    if not by_site:return {**out,"status":"NO_CROSS_SITE_REPEAT_SUPPORT"}
    siteavg=[tuple(mean(x[j] for x in v) for j in range(4)) for v in by_site.values()]
    agree,mse,base,robust=(mean(x[j] for x in siteavg) for j in range(4))
    sufficient=len(by_site)>=8 and len(repeated)>=3
    supported=sufficient and agree>=.70 and mse<base and sum(v[0]>.5 for v in siteavg)>=.75*len(siteavg)
    return {**out,"status":"EXPLORATORY_REPRODUCTIVE_CONTRAST_TRANSFER_SUPPORTED" if supported else "EXPLORATORY_TRANSFER_NOT_SUPPORTED" if sufficient else "DESCRIPTIVE_ONLY_THIN_SUPPORT",
        "effect":{"equal_site_sign_agreement":agree,"equal_site_unknown_bound_agreement":robust,
            "equal_site_mse":mse,"zero_contrast_baseline_mse":base,"sites_majority_correct":sum(v[0]>.5 for v in siteavg),
            "repeated_pairs":pairresults,"descriptive_not_independent_test_or_causal":True}}
def shard(index):
    token=os.environ.get(TOKEN_ENV,"").strip();req(token,"NEON_TOKEN_UNAVAILABLE")
    parts,_,mf,pin=source(token);ss=parts[index]
    selected=[v for v in mf if v["site"] in ss]
    target,_,names=_taxonomy()
    obs,issues=collect(selected,token,target,names)
    summaries,diag=contrasts(obs,ss)
    return {"status":"SHARD_COMPLETE","index":index,"source_pin_sha256":manifest_pin_digest(pin),
        "verified_mammal_files":len(selected),"site_count":len(ss),"selected_bouts":len(obs),
        "issues":issues,"support":diag,"anonymous_site_summaries":summaries}
def combine(directory):
    a=[json.loads(f.read_text()) for f in sorted(directory.rglob("neon_repro_season_shard_*.json"))]
    req(len(a)==4 and {x.get("index") for x in a}==set(range(4)),"INCOMPLETE_SHARDS")
    req(all(x.get("schema")==SHARD and x.get("status")=="SHARD_COMPLETE" and x.get("source_pin_sha256")==manifest_pin_digest(expected()) and x.get("site_count")==8 and len(x.get("anonymous_site_summaries",[]))==8 for x in a),"SHARD_STOP_OR_PIN_DRIFT")
    req(sum(x["verified_mammal_files"] for x in a)==1760,"MAMMAL_FILE_TOTAL_DRIFT")
    out=aggregate([s for x in a for s in x["anonymous_site_summaries"]])
    out.update(verified_mammal_files=1760,selected_bouts=sum(x["selected_bouts"] for x in a),
        issues=merge_numeric([x["issues"] for x in a]),support=merge_numeric([x["support"] for x in a]))
    return out
def main():
    p=argparse.ArgumentParser();sp=p.add_subparsers(dest="mode",required=True)
    s=sp.add_parser("shard");s.add_argument("index",type=int,choices=range(4))
    c=sp.add_parser("combine");c.add_argument("directory",type=Path);a=p.parse_args()
    out={"schema":SHARD if a.mode=="shard" else SCHEMA,"submission_hold":True,
        "prior_seedfall_effect_lane_closed":True,"no_resource_or_coexistence_mechanism_estimated":True}
    path=BUILD/(f"neon_repro_season_shard_{a.index}.json" if a.mode=="shard" else "neon_matched_species_pregnancy_season_20261125.json")
    if a.mode=="shard":out["index"]=a.index
    try:out.update(shard(a.index) if a.mode=="shard" else combine(a.directory))
    except Exception as e:out.update(status="STOP_SOURCE_OR_ANALYSIS",effect=None,error_class=type(e).__name__,reason=str(e) if type(e) is ValueError and re.fullmatch("[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR")
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True));return 2 if out["status"]=="STOP_SOURCE_OR_ANALYSIS" else 0
if __name__=="__main__":raise SystemExit(main())
