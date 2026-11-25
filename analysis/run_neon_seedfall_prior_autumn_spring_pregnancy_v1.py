"""Prospective exploratory prior-autumn deposition vs next-spring pregnancy.

Not the original joint spring/autumn support estimand. No causal inference.
All sites retained; adjacent-year, fixed trap and near-calendar plot contrasts.
"""
from collections import Counter, defaultdict
from datetime import date,datetime,timezone
from statistics import mean
from pathlib import Path
import argparse,json,os,re,math
from analysis.audit_neon_seedfall_mammal_breeding_support_v1 import (
    ROOT, TOKEN_ENV, batch, rows, d, t, known, req
)
from analysis.audit_neon_seedfall_mammal_breeding_sharded_v2 import (
    source, expected, manifest_pin_digest, merge_numeric
)
from analysis.audit_neon_crossseason_genus_support_v1 import _events,_normal_coord,_normal_tag
BUILD=ROOT/"build"
SHARD_SCHEMA="neon.seedfall.prior_autumn.spring_pregnancy.shard.v1"
SCHEMA="neon.seedfall.prior_autumn.spring_pregnancy.v1"
CAPTURE={"5 - capture","4 - more than 1 capture in one trap"}
NO_REPLACE={"","NA","N/A","NULL","NONE","NAN","N","NO","FALSE","0"}
def fnum(x):
    try:v=float(t(x))
    except ValueError:return None
    return v if math.isfinite(v) and v>=0 else None
def status(x):return t(x.get("trapCondition")).split(" - ")[0]
def sign(x):return (x>0)-(x<0)

def litter(lf,token):
    trap=defaultdict(set);field=defaultdict(set);parents=defaultdict(set)
    mass=defaultdict(set);issues=Counter()
    for meta,raw in batch(lf,token):
        h,it=rows(raw);site=meta["site"];tab=meta["table"]
        for x in it:
            if t(x.get("siteID"))!=site:
                issues["site_mismatch"]+=1;continue
            tr=t(x.get("trapID"));pl=t(x.get("plotID"));key=t(x.get("fieldSampleID"))
            if not tr or not pl:
                issues["missing_trap_or_plot"]+=1;continue
            if tab=="ltr_pertrap":
                typ=t(x.get("trapType"))
                if typ:trap[site,tr].add((pl,typ,t(x.get("namedLocation")),t(x.get("trapSize"))))
                continue
            a,b=d(x.get("setDate")),d(x.get("collectDate"))
            if a is None or b is None:
                issues["missing_interval_dates"]+=1;continue
            if tab=="ltr_fielddata":
                v=(pl,a,b,key,status(x),t(x.get("trappingDays")))
                field[site,tr,b].add(v)
                if known(key):parents[site,key].add((tr,pl,a,b))
            elif known(key):
                # All rows, including QA duplicates, retained for reconciliation.
                mass[site,key].add((tr,pl,a,b,t(x.get("functionalGroup")),
                    t(x.get("massSampleID")),t(x.get("qaDryMass")),t(x.get("dryMass"))))
    by=defaultdict(list)
    for (s,tr,b),vals in field.items():
        if b.month not in (9,10,11,12):continue
        if len(vals)!=1:
            issues["conflicting_field_key"]+=1;continue
        pl,a,b,key,cond,nd=next(iter(vals))
        if not date(b.year,9,1)<=a<b<=date(b.year,12,1):continue
        n=(b-a).days
        if fnum(nd)!=n:
            issues["trapping_days_mismatch"]+=1;continue
        tv=trap.get((s,tr),set())
        if len(tv)!=1 or next(iter(tv))[0]!=pl or next(iter(tv))[1]!="Elevated":
            issues["not_unique_elevated_trap"]+=1;continue
        ident=next(iter(tv))
        if cond=="TE":
            # Explicit empty-trap status, no mass records: a measured zero,
            # never an imputed absent seed functional group.
            if known(key) and mass.get((s,key)):
                issues["empty_trap_has_mass_records"]+=1;continue
            w=0.0
            issues["explicit_empty_interval"]+=1
        elif cond=="OK":
            if not known(key) or parents.get((s,key))!={(tr,pl,a,b)}:
                issues["parent_identity_unresolved"]+=1;continue
            mm=mass.get((s,key),set())
            if not mm or any(v[:4]!=(tr,pl,a,b) for v in mm):
                issues["mass_parent_interval_mismatch"]+=1;continue
            gg=defaultdict(set)
            for v in mm:gg[v[4]].add((v[5],v[6],v[7]))
            def original(g):
                vv=gg.get(g,set())
                ids={v[0] for v in vv}
                orig={v[2] for v in vv if v[1]=="N"}
                if len(ids)!=1 or not all(known(x) for x in ids) or len(orig)!=1:return None
                if any(v[1] not in {"Y","N"} for v in vv):return None
                return fnum(next(iter(orig)))
            # No inferred zero when a seed group is absent, including
            # 2018-19 unsorted samples. Mixed positive or unresolved => STOP.
            if "Mixed" in gg and original("Mixed")!=0:
                issues["mixed_mass_positive_or_unresolved"]+=1;continue
            w=original("Seeds")
            if w is None:
                issues["explicit_seed_original_mass_unresolved"]+=1;continue
            issues["explicit_seed_mass_interval"]+=1
        else:
            issues["non_OK_nonempty_trap"]+=1;continue
        # Day-of-season masks permit only whole-interval matched coverage,
        # no prorating a sample across unobserved dates.
        start=(a-date(a.year,9,1)).days;stop=start+n
        by[s,b.year,tr].append((start,stop,w,ident))
    good={}
    for k,v in by.items():
        v=sorted(v,key=lambda z:(z[0],z[1]))
        if any(x[1]>y[0] for x,y in zip(v,v[1:])):
            issues["overlap_trap_autumn_excluded"]+=1;continue
        if len({x[3] for x in v})!=1:
            issues["trap_metadata_inconsistent"]+=1;continue
        days=set().union(*(set(range(a,b)) for a,b,w,z in v))
        good[k]=(days,sum(x[2] for x in v)/len(days),v[0][3])
    return good,issues

def resource_pair(g,s,y):
    a=y-2;b=y-1
    ids={tr for ss,yy,tr in g if ss==s and yy==a}&{tr for ss,yy,tr in g if ss==s and yy==b}
    changes=[];plots=set()
    for tr in sorted(ids):
        da,xa,ia=g[s,a,tr];db,xb,ib=g[s,b,tr]
        if ia!=ib or len(da&db)<45 or len(da^db)>14:continue
        changes.append(xb-xa);plots.add(ia[0])
    return (mean(changes),len(changes)) if len(changes)>=3 and len(plots)>=3 else None

def mammals(mf,token):
    pp=[];captures=defaultdict(list);effort=defaultdict(set);issues=Counter()
    identities=defaultdict(set);replacements=defaultdict(set)
    for meta,raw in batch(mf,token):
        h,it=rows(raw);s=meta["site"]
        if meta["table"]=="mam_perplotnight":
            for x in it:
                day=d(x.get("collectDate"))
                if day and day.month in (3,4,5):
                    pp.append({"_site":s,"siteID":t(x.get("siteID")),"plotID":t(x.get("plotID")),
                        "eventID":t(x.get("eventID")),"nightuid":t(x.get("nightuid")),
                        "collectDate":day.isoformat(),"gridCompletion":t(x.get("gridCompletion"))})
            continue
        for x in it:
            day=d(x.get("collectDate"));pl=t(x.get("plotID"));n=t(x.get("nightuid"))
            if not day or day.month not in (3,4,5) or not pl or not n or t(x.get("siteID"))!=s:continue
            k=(s,pl,n);coord=_normal_coord(x.get("trapCoordinate"))
            if coord:effort[k].add(coord)
            if t(x.get("trapStatus")).lower() not in CAPTURE:continue
            tag=_normal_tag(x.get("tagID"))
            if not tag:continue
            sp=t(x.get("taxonID"));sx=t(x.get("sex")).upper();rank=t(x.get("taxonRank")).lower()
            name=t(x.get("scientificName"))
            rep=t(x.get("replacedTag"))
            if rep.upper() not in NO_REPLACE:
                replacements[s,day.year].add(tag)
                if _normal_tag(rep):replacements[s,day.year].add(rep)
            if known(sp) and sx in {"F","M"}:
                identities[s,day.year,tag].add((sp,sx))
            # Require explicit species identity; no species groups.
            if rank!="species" or not re.fullmatch(r"[A-Z][a-z]+ [a-z][a-z-]+",name) or not known(sp):continue
            if sx!="F" or t(x.get("lifeStage")).lower()!="adult":continue
            pr=t(x.get("pregnancyStatus")).lower()
            captures[k].append((day,tag,sp,pr))
    chosen,rej,approved=_events(pp)
    issues.update({"event_reject_"+k:v for k,v in rej.items()})
    # Select the first qualifying completed three-night bout per plot/spring,
    # before opening pregnancy values. Same choice as inherited _events.
    obs={}
    for (s,pl,e),v in chosen.items():
        y=v["first"].year
        if not all(len(effort[s,pl,n])>=90 for n in v["nights"]):
            issues["low_trap_effort_bout"]+=1;continue
        out=[]
        for n in v["nights"]:
            for rec in captures[s,pl,n]:
                day,tag,sp,pr=rec
                if len(identities[s,y,tag])!=1 or tag in replacements[s,y]:
                    issues["identity_or_replacement_excluded"]+=1;continue
                out.append(rec)
        obs[s,y,pl]=(v["first"],out)
    return obs,issues

def spring_pair(obs,s,y):
    ps={p for ss,yy,p in obs if ss==s and yy==y-1}&{p for ss,yy,p in obs if ss==s and yy==y}
    good=[]
    for p in sorted(ps):
        a,b=obs[s,y-1,p][0],obs[s,y,p][0]
        # Month/day converted to fixed leap-free calendar; March-May only.
        if abs((date(2001,b.month,b.day)-date(2001,a.month,a.day)).days)<=14:good.append(p)
    if not good:return {},0
    by={}
    for yy in (y-1,y):
        first=defaultdict(list)
        for p in good:
            for day,tag,sp,pr in obs[s,yy,p][1]:first[tag].append((day,sp,pr))
        count=defaultdict(Counter)
        for tag,v in first.items():
            if len({x[1] for x in v})!=1:continue
            day=min(x[0] for x in v);ss={x[2] for x in v if x[0]==day};sp=v[0][1]
            # Earliest observation only; ambiguity remains unknown.
            label=next(iter(ss)) if len(ss)==1 else "unknown"
            count[sp][label if label in {"pregnant","not"} else "unknown"]+=1
        by[yy]=count
    result={}
    for sp in set(by[y-1])&set(by[y]):
        a,b=by[y-1][sp],by[y][sp]
        def risk(v):
            n=v["pregnant"]+v["not"];u=v["unknown"]
            if n<10:return None
            return (v["pregnant"]/n,v["pregnant"]/(n+u),(v["pregnant"]+u)/(n+u))
        ra,rb=risk(a),risk(b)
        if ra and rb:result[sp]=(rb[0]-ra[0],rb[1]-ra[2],rb[2]-ra[1])
    return result,len(good)

def site_effects(g,obs,ss):
    counts=Counter();out=[]
    for s in sorted(ss):
        vals=[];year_pairs=set()
        for y in range(2019,2026):
            rr=resource_pair(g,s,y)
            if rr is None:continue
            counts["matched_resource_year_pairs"]+=1
            delta,traps=rr
            sp,np=spring_pair(obs,s,y)
            if not np:continue
            counts["matched_resource_and_spring_plot_year_pairs"]+=1
            if delta==0:
                counts["zero_resource_change_year_pairs"]+=1;continue
            for a,lo,hi in sp.values():
                if delta>0:v=(a,lo,hi)
                else:v=(-a,-hi,-lo)
                vals.append(v);year_pairs.add(y)
        if vals:
            out.append({"n":len(vals),"year_pairs":len(year_pairs),
                "aligned_RD":mean(v[0] for v in vals),
                "unknown_status_lower":mean(v[1] for v in vals),
                "unknown_status_upper":mean(v[2] for v in vals),
                "n_positive":sum(v[0]>0 for v in vals),"n_zero":sum(v[0]==0 for v in vals)})
    return out,dict(counts)

def aggregate(site):
    if not site:return {"status":"NO_ELIGIBLE_PAIRED_COMPARISON","effect":None,"eligible_sites":0}
    n=len(site);m=mean(x["aligned_RD"] for x in site);npos=sum(x["aligned_RD"]>0 for x in site)
    reps=sum(x["year_pairs"]>=2 for x in site);pairs=sum(x["n"] for x in site)
    enough=n>=8 and pairs>=20 and reps>=4
    consistent=enough and m>0 and npos>=math.ceil(.75*n) and min(mean(x["aligned_RD"] for j,x in enumerate(site) if j!=i) for i in range(n))>0
    return {"status":"EXPLORATORY_DIRECTION_SUPPORTED" if consistent else "EXPLORATORY_DIRECTION_NOT_SUPPORTED" if enough else "DESCRIPTIVE_ONLY_THIN_SUPPORT",
        "eligible_sites":n,"eligible_taxon_year_pairs":pairs,"sites_two_or_more_year_pairs":reps,"positive_sites":npos,
        "effect":{"equal_site_aligned_pregnancy_RD":m,
            "unknown_status_bounds":[mean(x["unknown_status_lower"] for x in site),mean(x["unknown_status_upper"] for x in site)],
            "positive_taxon_year_pairs":sum(x["n_positive"] for x in site),"zero_taxon_year_pairs":sum(x["n_zero"] for x in site),
            "no_sampling_CI_or_causal_effect":True,"no_climate_adjustment":True}}
def shard(i):
    token=os.environ.get(TOKEN_ENV,"").strip();req(token,"NEON_TOKEN_UNAVAILABLE")
    parts,lf,mf,pin=source(token);ss=parts[i]
    a=[x for x in lf if x["site"] in ss];b=[x for x in mf if x["site"] in ss]
    g,li=litter(a,token);obs,mi=mammals(b,token)
    eff,q=site_effects(g,obs,ss)
    return {"status":"SHARD_COMPLETE","index":i,"source_pin_sha256":manifest_pin_digest(pin),
        "verified_files":len(a)+len(b),"litter_issues":dict(li),"mammal_issues":dict(mi),
        "trap_autumn_records":len(g),"spring_bouts":len(obs),"comparison_support":q,"anonymous_site_summaries":eff}
def combine(directory):
    a=[json.loads(f.read_text()) for f in sorted(directory.rglob("neon_seedfall_pregnancy_shard_*.json"))]
    req(len(a)==4 and {v.get("index") for v in a}==set(range(4)),"INCOMPLETE_SHARDS")
    req(all(v.get("schema")==SHARD_SCHEMA and v.get("status")=="SHARD_COMPLETE" and v.get("source_pin_sha256")==manifest_pin_digest(expected()) for v in a),"SHARD_STOP_OR_PIN_DRIFT")
    req(sum(v["verified_files"] for v in a)==7009,"SOURCE_FILE_TOTAL_DRIFT")
    out=aggregate([x for v in a for x in v["anonymous_site_summaries"]])
    out.update(verified_files=7009,trap_autumn_records=sum(v["trap_autumn_records"] for v in a),
        spring_bouts=sum(v["spring_bouts"] for v in a),litter_issues=merge_numeric([v["litter_issues"] for v in a]),
        mammal_issues=merge_numeric([v["mammal_issues"] for v in a]),
        comparison_support=merge_numeric([v["comparison_support"] for v in a]))
    return out
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="mode",required=True)
    s=sub.add_parser("shard");s.add_argument("index",type=int,choices=range(4))
    c=sub.add_parser("combine");c.add_argument("directory",type=Path);a=p.parse_args()
    out={"schema":SHARD_SCHEMA if a.mode=="shard" else SCHEMA,"submission_hold":True,
        "exploratory_spring_only_not_original_joint_phase":True,"no_causal_cache_or_coexistence_claim":True}
    path=BUILD/(f"neon_seedfall_pregnancy_shard_{a.index}.json" if a.mode=="shard" else "neon_seedfall_prior_autumn_spring_pregnancy_20261125.json")
    if a.mode=="shard":out["index"]=a.index
    try:out.update(shard(a.index) if a.mode=="shard" else combine(a.directory))
    except Exception as e:out.update(status="STOP_SOURCE_OR_ANALYSIS",effect=None,error_class=type(e).__name__,reason=str(e) if type(e) is ValueError and re.fullmatch("[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR")
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 2 if out["status"]=="STOP_SOURCE_OR_ANALYSIS" else 0
if __name__=="__main__":raise SystemExit(main())
