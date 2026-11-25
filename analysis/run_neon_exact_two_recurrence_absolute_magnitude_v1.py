"""Translate the already-opened exact-two NEON recurrence to absolute units.

No new effect test, subgroup search, p-value, or biological inference.
Preserve original 150 informative units and established sensitivity sets.
Report all 158 source pairs, including null-degenerate pairs, separately.
"""
from collections import defaultdict
from datetime import datetime,timezone
from fractions import Fraction
from statistics import mean
from pathlib import Path
import json,math,re
from analysis.run_neon_two_genus_source_v1 import original_sources_for_two_genus
from analysis.run_neon_exact_two_genus_ecology_v1 import reuse_physical_sites
from analysis.neon_exact_two_row_fixedmargin_v1 import two_row_exact_marginal,observed_exact_unit

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_exact_two_recurrence_absolute_magnitude_20261125.json"
def req(ok,msg):
    if not ok:raise ValueError(msg)
def row(u):
    a,b=u["A"],u["B"]
    mar=two_row_exact_marginal(a,b)
    den=sum(len(v) for v in b.values())
    obs=sum(len(a[g]&b[g]) for g in a)
    mass=mar["_private_mass"];total=mar["total_uniform_fixed_margin_matrices"]
    mu=Fraction(sum(k*n for k,n in mass.items()),total)
    req(total>0 and sum(mass.values())==total and 0<=mu<=den and 0<=obs<=den,"EXACT_MARGIN_INVALID")
    req(abs(float(mu)-mar["null_mean"])<1e-12,"ORIGINAL_NULL_MEAN_DRIFT")
    informative=mar["status"]=="EXACT_NONDEGENERATE"
    if informative:
        z=observed_exact_unit(a,b,mar)["z"]
    else:
        req(mu==obs,"DEGENERATE_NULL_NOT_EQUAL_OBSERVED")
        z=None
    return {"site":u["site"],"den":den,"obs":obs,"mu":mu,"z":z}

def summarize(rows):
    req(bool(rows),"NO_SOURCE_ROWS")
    by=defaultdict(list)
    for x in rows:by[x["site"]].append(x)
    # Match original physical-site weighting: fraction per pair, mean
    # within site, then mean across sites. Not ratio of pooled counts.
    def of(x):return Fraction(x["obs"],x["den"])
    def nf(x):return x["mu"]/x["den"]
    os=[mean(of(x) for x in v) for v in by.values()]
    ns=[mean(nf(x) for x in v) for v in by.values()]
    es=[o-n for o,n in zip(os,ns)]
    ob=mean(os);nu=mean(ns);ex=mean(es)
    req(ob-nu==ex,"SITE_EQUAL_ARITHMETIC")
    den=sum(x["den"] for x in rows);obs=sum(x["obs"] for x in rows);expected=sum((x["mu"] for x in rows),Fraction(0))
    zi=[mean(x["z"] for x in v if x["z"] is not None) for v in by.values() if any(x["z"] is not None for x in v)]
    informative=sum(x["z"] is not None for x in rows)
    out={"pairs":len(rows),"physical_sites":len(by),"informative_pairs":informative,
         "null_degenerate_pairs":len(rows)-informative,
         "equal_site_observed_fraction":float(ob),"equal_site_null_expected_fraction":float(nu),
         "equal_site_excess_fraction":float(ex),
         "equal_site_observed_to_expected_ratio":float(ob/nu) if nu>0 else None,
         "positive_excess_site_count":sum(v>0 for v in es),
         "equal_site_mean_Z_informative_only":mean(zi) if zi else None,
         "all_pair_cell_counts_descriptive":{"later_genus_station_cells":den,"observed_same_genus_matches":obs,
            "null_expected_matches":float(expected),"excess_matches":float(obs-expected),
            "pooled_cell_observed_fraction":obs/den,"pooled_cell_null_expected_fraction":float(expected/den),
            "not_independent_cell_trials":True},
         "site_excess_fraction_range":[float(min(es)),float(max(es))],
         "no_new_p_value_or_individual_recurrence_probability":True}
    if len(es)>1:
        loo=[mean(v for j,v in enumerate(es) if i!=j) for i in range(len(es))]
        out["leave_one_site_out_excess_fraction_range"]=[float(min(loo)),float(max(loo))]
    return out

def run():
    strict,exact,source=original_sources_for_two_genus()
    req(len(strict)==58 and len(exact)==158 and len({u["site"] for u in exact})==30,"ORIGINAL_SOURCE_DRIFT")
    reused=reuse_physical_sites(exact);orig={u["site"] for u in strict}
    req(len(reused)==13 and sum(u["site"] not in reused for u in exact)==52,"ORIGINAL_REUSE_ROSTER_DRIFT")
    vals=[row(u) for u in exact];informative=[x for x in vals if x["z"] is not None]
    clean=[x for x in informative if x["site"] not in reused]
    new=[x for x in informative if x["site"] not in orig]
    req(len(informative)==150 and len(clean)==48 and len(new)==71,"ORIGINAL_INFORMATIVE_ROSTER_DRIFT")
    a,b,c=(summarize(v) for v in (informative,clean,new))
    for x,n,s,z in [(a,150,30,.6147113767599713),(b,48,17,.6983519175917221),(c,71,17,.7600592308705587)]:
        req(x["pairs"]==n and x["physical_sites"]==s and abs(x["equal_site_mean_Z_informative_only"]-z)<1e-10,"ARCHIVED_SITE_MEAN_Z_DRIFT")
    req(a["positive_excess_site_count"]>=0,"SOURCE_SANITY")
    return {"status":"EXISTING_EFFECT_MAGNITUDE_TRANSLATED","source":source,
        "original_informative_main":a,"original_whole_site_reuse_exclusion":b,"original_geographic_nonoverlap":c,
        "all_158_source_pairs_raw_descriptive_including_degenerate":summarize(vals),
        "archived_Z_reconciled":True,"same_release_not_independent_replication":True,
        "no_metric_distance_habitat_or_causal_claim":True}

def main():
    out={"schema":"neon.exact_two.recurrence.absolute_magnitude.v1","submission_hold":True,
         "translation_of_already_opened_effects_only":True,"no_new_hypothesis_or_p_value":True}
    try:out.update(run())
    except Exception as e:out.update(status="STOP_SOURCE_OR_ARITHMETIC",error_class=type(e).__name__,reason=str(e) if type(e) is ValueError and re.fullmatch("[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR")
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True));return 3 if out["status"]=="STOP_SOURCE_OR_ARITHMETIC" else 0
if __name__=="__main__":raise SystemExit(main())
