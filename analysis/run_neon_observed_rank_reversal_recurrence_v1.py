"""Post-result exploratory recurrence conditional on observed tag-count rank reversal.
Original 158 pairs and exact null unchanged; never an estimate of true density.
"""
from collections import Counter,defaultdict
from statistics import mean
from pathlib import Path
from math import ceil
import json,re
from analysis.run_neon_two_genus_source_v1 import original_sources_for_two_genus
from analysis.audit_multiscale_density_mnka_variation_v1 import _taxonomy
from analysis.audit_neon_crossseason_genus_support_v1 import _events,_normal_coord,_normal_tag,_is_capture,MIN_TRAPS_PER_NIGHT
from analysis.run_neon_exact_two_genus_ecology_v1 import reuse_physical_sites
from analysis.neon_exact_two_row_fixedmargin_v1 import two_row_exact_marginal,observed_exact_unit,meta_exact_site_null
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_observed_rank_reversal_recurrence_20261125.json"
def req(v,msg):
    if not v:raise ValueError(msg)
def rank(a,b):return (a>b)-(a<b)
def category(fa,fb,da,db):
    a,b,c,d=rank(*fa),rank(*fb),rank(*da),rank(*db)
    if a*b==-1 and (a,b)==(c,d):return "strict_reversal"
    if a==b!=0 and (a,b)==(c,d):return "strict_retained_rank"
    return "tie_or_disagreement"

def count_context(pp,tt,genus):
    # Independently mirror original event/tag eligibility, then verify
    # exact A/B matrices for every source unit before opening overlap.
    chosen,_,approved=_events(pp)
    night={}
    for k,x in approved.items():
        for n in x["nights"]:
            req(n not in night or night[n]==k,"NIGHT_UID_CONFLICT")
            night[n]=k
    gtags=defaultdict(set);effort=defaultdict(set);captured=defaultdict(set)
    for x in tt:
        s=str(x.get("_site") or "").strip();p=str(x.get("plotID") or "").strip()
        n=str(x.get("nightuid") or "").strip();k=night.get(n)
        if k is None or k[:2]!=(s,p):continue
        c=_normal_coord(x.get("trapCoordinate"))
        if k in chosen and c:effort[k,n].add(c)
        if not _is_capture(x.get("trapStatus")):continue
        g=genus.get(str(x.get("taxonID") or "").strip());tag=_normal_tag(x.get("tagID"))
        if not tag or not g:continue
        gtags[s,p,tag].add(g)
        if k in chosen and c:captured[k,n,tag].add(c)
    ambiguous={(k,tag) for (k,n,tag),c in captured.items() if len(c)>1}
    valid={k:x for k,x in chosen.items() if all(len(effort[k,n])>=MIN_TRAPS_PER_NIGHT for n in x["nights"])}
    periods={(x["site"],x["plot"],x["season"]):k for k,x in valid.items()}
    tags=defaultdict(lambda:defaultdict(set));coords=defaultdict(set)
    for (k,n,tag),c in captured.items():
        if k not in valid or (k,tag) in ambiguous:continue
        gg=gtags.get((k[0],k[1],tag),set())
        if len(gg)!=1:continue
        g=next(iter(gg));tags[k][g].add(tag);coords[k,g,tag].update(c)
    return periods,tags,coords

def verify_unit(u,ctx):
    periods,tags,coords=ctx;s,p=u["site_plot"];q=u["season_ordinal"]
    a,b=periods[s,p,q],periods[s,p,q+1]
    gl=sorted(u["A"])
    req(len(gl)==2 and gl==sorted(u["B"]),"NOT_EXACT_TWO")
    req(all(g in tags[a] and g in tags[b] for g in gl),"TAG_ROSTER_DRIFT")
    shared=set().union(*tags[a].values())&set().union(*tags[b].values())
    def side(k,mat):
        full=tuple(len(tags[k][g]) for g in gl)
        ex={g:tags[k][g]-shared for g in gl}
        c={g:set().union(*(coords[k,g,t] for t in ex[g])) for g in gl}
        req(c==mat and all(len(ex[g])>=2 for g in gl),"ORIGINAL_MATRIX_RECONCILIATION_FAILED")
        return full,tuple(len(ex[g]) for g in gl)
    fa,da=side(a,u["A"]);fb,db=side(b,u["B"])
    return category(fa,fb,da,db)

def evaluate(rows,seed,minn,mins):
    info=[(u,m) for u,m in rows if m["status"]=="EXACT_NONDEGENERATE"]
    sites={u["site"] for u,m in info}
    out={"informative_pairs":len(info),"sites":len(sites),"minimum_pairs":minn,"minimum_sites":mins}
    if len(info)<minn or len(sites)<mins:return {**out,"status":"STOP_SUBGROUP_SUPPORT","effect":None}
    private=[];by=defaultdict(list)
    for u,m in info:
        z=observed_exact_unit(u["A"],u["B"],m)["z"]
        obs=sum(len(u["A"][g]&u["B"][g]) for g in u["A"])
        den=sum(len(v) for v in u["B"].values())
        by[u["site"]].append((z,(obs-m["null_mean"])/den))
        private.append({"site":u["site"],"observed_z":z,"exact_marginal":m})
    n=meta_exact_site_null(private,seed=seed,n_replicates=20000)
    zz=[mean(x[0] for x in v) for v in by.values()]
    pos=sum(x>0 for x in zz)
    ok=mean(zz)>0 and pos>=ceil(.75*len(zz)) and n["rank_comonotone_within_site_exact_marginal_stress"]["one_sided_plus_one_p"]<.05
    return {**out,"status":"DESCRIPTIVE_RECURRENCE_SUPPORTED" if ok else "DESCRIPTIVE_RECURRENCE_NOT_SUPPORTED",
        "effect":{"equal_site_mean_Z":mean(zz),"positive_sites":pos,
            "equal_site_excess_same_genus_station_fraction":mean(mean(x[1] for x in v) for v in by.values()),
            "conditional_null":n}}
def run():
    strict,exact,source,pp,tt=original_sources_for_two_genus(include_private_source_rows=True)
    req(len(strict)==58 and len(exact)==158 and len({u["site"] for u in exact})==30,"SOURCE_COHORT_DRIFT")
    _,genus,_=_taxonomy()
    ctx=count_context(pp,tt,genus);reused=reuse_physical_sites(exact)
    req(len(reused)==13 and sum(u["site"] not in reused for u in exact)==52,"SOURCE_REUSE_DRIFT")
    labels=[verify_unit(u,ctx) for u in exact]
    del pp,tt,ctx
    margins=[two_row_exact_marginal(u["A"],u["B"]) for u in exact]
    req(sum(m["status"]=="EXACT_NONDEGENERATE" for m in margins)==150,"NULL_VARIANCE_DRIFT")
    allrows=list(zip(exact,margins,labels))
    def choose(k,clean=False):
        return [(u,m) for u,m,c in allrows if c==k and (not clean or u["site"] not in reused)]
    full=evaluate(choose("strict_reversal"),2026112507,20,8)
    clean=evaluate(choose("strict_reversal",True),2026112508,12,6)
    retained=evaluate(choose("strict_retained_rank"),2026112509,20,8)
    return {"status":"EXPLORATORY_REVERSAL_RECURRENCE_SUPPORTED_BOTH" if full["status"]==clean["status"]=="DESCRIPTIVE_RECURRENCE_SUPPORTED" else "REVERSAL_RECURRENCE_NOT_ESTABLISHED",
        "source":source,"original_matrices_reconciled":158,"original_informative_units":150,
        "observed_rank_categories":dict(Counter(labels)),
        "informative_rank_categories":dict(Counter(c for u,m,c in allrows if m["status"]=="EXACT_NONDEGENERATE")),
        "whole_site_no_reuse_rank_categories":dict(Counter(c for u,m,c in allrows if u["site"] not in reused)),
        "strict_rank_reversal":full,"strict_rank_reversal_no_reused_season_sites":clean,"retained_rank_context_only":retained,
        "original_full_cohort_effect_unchanged":True,"no_direct_between_group_test":True,
        "not_true_density_dominance_or_ecological_mechanism":True}
def main():
    out={"schema":"neon.observed_rank_reversal.recurrence.v1","submission_hold":True,"post_result_exploratory":True,"pregnancy_lane_closed":True,"no_new_independent_replication":True}
    try:out.update(run())
    except Exception as e:
        out.update(status="STOP_SOURCE_OR_ANALYSIS",error_class=type(e).__name__,reason=str(e) if type(e) is ValueError and re.fullmatch("[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR")
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True));return 3 if out["status"]=="STOP_SOURCE_OR_ANALYSIS" else 0
if __name__=="__main__":raise SystemExit(main())
