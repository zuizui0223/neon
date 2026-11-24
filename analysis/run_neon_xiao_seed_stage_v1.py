"""Xiao 2016 full-release stage contrast, with unresolved-fate bounds.

The 18 unretrieved acorns are published externally, not fitted. If the workbook
cannot locate them, all 18 may be in the adverse treatment arm. No guessing
species/response codes, no unrecorded seeds turned into known noncache.
"""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from fractions import Fraction
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import json,re
from analysis.audit_neon_seasonal_seed_role_source_v1 import verified_file
from analysis.neon_seed_stage_attenuation_bounds_v1 import summarize
from analysis.audit_neon_direct_seed_fate_stage_sources_v1 import audit
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_xiao_seed_stage_2016_20261124.json"
SHA="71d1de98d6ea7af0620eda71610af35415fa2b2a0fb32e8fe8d30bd3121b5953"
HEADER=["site","treatment","species","station","harvest","Removal","hoard","dispersal","distance"]
def req(x,code):
    if not x:raise ValueError(code)
def token(v):
    if v is None:return ""
    if isinstance(v,float) and v.is_integer():return str(int(v))
    return str(v).strip()
def canon(v):
    return re.sub(r"[^a-z]","",token(v).lower())
def species(v):
    a=canon(v)
    if a in {"qv","quercusvariabilis","qvariabilis","acorn","acorns","quercus"}:return "oak"
    if a in {"ch","castaneahenryi","chenryi","chestnut","chestnuts","castanea"}:return "chestnut"
    return None
def binary(v):
    s=token(v).lower()
    if s in {"1","yes","true"}:return 1
    if s in {"0","no","false"}:return 0
    if s in {"","na","n/a","nan","not applicable","."}:return None
    raise ValueError("UNVERIFIED_STAGE_LITERAL")
def note_confirms_binary(note):
    # Require an explicit author definition of numeric 1 and 0, not just
    # the observation that a column happens to contain two numeric values.
    s=" ".join(note).lower()
    one=bool(re.search(r"\b1\s*[:=–—-]?\s*(?:for\s+|means\s+|represents\s+|indicates\s+)?(?:yes|success|positive|true|harvested|removed|hoarded|dispersed|occurred)\b",s))
    zero=bool(re.search(r"\b0\s*[:=–—-]?\s*(?:for\s+|means\s+|represents\s+|indicates\s+)?(?:no|failure|negative|false|not\b)",s))
    return one and zero

def coarse_bounds(mono,mixed,missing=18):
    # Nine stations each have 60 mono and 30 mixed oak seeds. Equal station
    # and site weighting thus equals these fixed pooled denominators.
    req(mono["released"]==540 and mixed["released"]==270,"RELEASE_DENOMINATOR_DRIFT")
    res={}
    for key in ("cache","intact","damage"):
        a,b=mixed[key],mono[key]
        known=Fraction(a,270)-Fraction(b,540)
        # Unknown embryo caches are only possible additional intact/damaged
        # outcomes, not additional caches. Unretrieved seeds may be in either arm.
        ea=mixed["embryo_unknown"] if key!="cache" else 0
        eb=mono["embryo_unknown"] if key!="cache" else 0
        # Missing seeds cannot already be known cached. The published total
        # is a global budget; these conservative marginal extrema need not
        # be simultaneously attained across outcomes.
        up_a=min(270-a,missing+ea);up_b=min(540-b,missing+eb)
        lo=known-Fraction(up_b,540);hi=known+Fraction(up_a,270)
        res[key]={"known_risk_difference":float(known),"conservative_bounds":[float(lo),float(hi)]}
    res["attenuation"]=dict(res["damage"])
    return res

def analyze(rows,note):
    groups=defaultdict(list)
    for row in rows:
        groups[(token(row[0]),token(row[3]),token(row[1]),token(row[2]))].append(row)
    diag={"rows":len(rows),"site_count":len({k[0] for k in groups}),
          "site_station_count":len({k[:2] for k in groups}),
          "literal_treatment_species_group_sizes":[{"treatment":t,"species":sp,"group_size_histogram":dict(Counter(len(v) for k,v in groups.items() if k[2:]==(t,sp)))} for t,sp in sorted({k[2:] for k in groups})],
          "stage_literal_counts":{HEADER[j]:dict(Counter(token(x[j]) for x in rows)) for j in (4,5,6,7)},
          "author_note":note,"author_note_confirms_binary":note_confirms_binary(note)}
    out={"source_diagnostics":diag,"effect":None}
    if not note_confirms_binary(note):
        return {**out,"status":"STOP_BINARY_CODE_NOT_EXPLICITLY_DOCUMENTED"}
    if any(species(k[3]) is None for k in groups):
        return {**out,"status":"STOP_SPECIES_CODE_NOT_IDENTIFIED"}
    req(len(rows)==1620 and diag["site_count"]==3 and diag["site_station_count"]==9,"ORIGINAL_RELEASE_DESIGN_DRIFT")
    sites=defaultdict(set)
    for s,t,_,_ in groups:sites[s].add(t)
    req(all(len(x)==3 for x in sites.values()),"SITE_STATION_DESIGN_DRIFT")
    # Mixed vs mono is determined by the original balanced release design,
    # not by outcome. Require one 60 and one 30 group for each species per station.
    panel=defaultdict(dict)
    treat_labels=defaultdict(set)
    for (s,station,tr,sp),g in groups.items():
        role={30:"mixed",60:"mono"}.get(len(g));name=species(sp)
        req(role is not None and (name,role) not in panel[(s,station)],"RELEASE_CELL_DRIFT")
        panel[(s,station)][name,role]=g;treat_labels[role].add(tr)
    req(all(set(x)=={(s,t) for s in ("oak","chestnut") for t in ("mono","mixed")} for x in panel.values()),"INCOMPLETE_ORIGINAL_RELEASE_CELLS")
    req(treat_labels["mixed"].isdisjoint(treat_labels["mono"]),"TREATMENT_LABEL_CONFLICT")
    # Only the original oak endpoint. A positive hoard denotes a recorded cache.
    # A positive dispersal is a cache with intact embryo (paper definitions).
    # No assumption that negative hoard alone distinguishes eaten from missing.
    sums={k:Counter() for k in ("mono","mixed")};station_counts=defaultdict(dict)
    for (s,station),cells in sorted(panel.items()):
        for role in ("mono","mixed"):
            cnt=Counter(released=len(cells["oak",role]))
            cats=Counter()
            for x in cells["oak",role]:
                h,rem,cache,intact=map(binary,x[4:8])
                if rem==1:req(h==1,"NON_NESTED_HARVEST")
                if cache==1:req(rem==1 and h==1,"NON_NESTED_CACHE")
                if intact==1:req(cache==1,"NON_NESTED_INTACT")
                if cache==1:
                    cnt["cache"]+=1
                    if intact==1:cnt["intact"]+=1;cats["intact"]+=1
                    elif intact==0:cnt["damage"]+=1;cats["damaged"]+=1
                    else:cnt["embryo_unknown"]+=1;cats["cache_embryo_unknown"]+=1
                elif rem==1 and cache is None:cats["unknown"]+=1
                else:cats["noncache"]+=1
            sums[role].update(cnt);station_counts[s,station][role]=(cnt,cats)
    # Exact unresolved rows are usable only if they reconcile to all
    # 18 published missing oak seeds. Else use external global-budget bounds,
    # never the falsely exhaustive "noncache" labels for the exact estimator.
    total_unknown=sum(v[t][1]["unknown"] for v in station_counts.values() for t in ("mono","mixed"))
    out["published_unretrieved_oaks"]=18
    out["explicit_unresolved_after_removal_rows"]=total_unknown
    req(total_unknown<=18,"UNRESOLVED_CODE_EXCEEDS_PUBLISHED_TOTAL")
    # All 810 oak releases are retained; known cache tallies unaffected by
    # unknown seed locations. Require no unexplained removed seed with
    # missing harvest or no documented removal/harvest.
    if total_unknown==18:
        bysite=defaultdict(list)
        from analysis.neon_seed_stage_attenuation_bounds_v1 import CATEGORIES
        for (s,station),v in sorted(station_counts.items()):
            bysite[s].append(tuple({k:v[t][1][k] for k in CATEGORIES} for t in ("mixed","mono")))
        result=summarize([bysite[s] for s in sorted(bysite)])
        out.update(status=result["status"],effect=result,unresolved_fate_mode="rowwise_reconciled_to_published_total")
    else:
        b=coarse_bounds(sums["mono"],sums["mixed"])
        site=defaultdict(lambda:Counter())
        for (s,station),v in station_counts.items():
            site[s]["mixed"]+=v["mixed"][0]["damage"];site[s]["mono"]+=v["mono"][0]["damage"]
        pos=sum(2*v["mixed"]>v["mono"] for v in site.values())
        supported=b["cache"]["conservative_bounds"][0]>0 and b["damage"]["conservative_bounds"][0]>0 and pos==3
        out.update(status="COARSE_PUBLISHED_MISSING_BUDGET_ATTENUATION_SUPPORTED" if supported else "COARSE_PUBLISHED_MISSING_BUDGET_ATTENUATION_NOT_ESTABLISHED",
                   effect={"known_counts_by_treatment":{k:dict(v) for k,v in sums.items()},"equal_site_weighted":b,
                           "sites_positive_known_damage_difference":pos,"bounds_not_confidence_intervals":True,
                           "intact_cache_not_recruitment":True},unresolved_fate_mode="global_18_missing_budget_no_fate_allocation")
    return out
def primary():
    from openpyxl import load_workbook
    raw=verified_file(3189775,1,4993375,70432,"37f045d36dc897bf390b1dac4cc9a2bd",SHA)
    b=load_workbook(BytesIO(raw),read_only=True,data_only=True)
    try:
        n=[token(x) for row in b["note"].values for x in row if x is not None and token(x)]
        it=b["seedfatedata"].values
        req(list(next(it))==HEADER,"WORKBOOK_HEADER_DRIFT")
        rows=list(it);req(len(rows)==1620,"WORKBOOK_ROW_COUNT_DRIFT")
        return analyze(rows,n)
    finally:b.close()
def main():
    out={"schema":"neon.xiao2016.seed_stage_bound_and_synchrony_source.v1","submission_hold":True,"Holt_closed":True}
    try:out["primary"]=primary()
    except Exception as e:out["primary"]={"status":"STOP_ORIGINAL_STAGE_ONTOLOGY","effect":None,"error_class":type(e).__name__,"reason":str(e) if type(e) is ValueError and re.fullmatch("[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR"}
    try:out["synchrony_source"]=audit(9896078,{"version":None,"keywords":(),"paper":"Yang et al Ecology Letters 2020; PMC6916184","role":"source_inventory_only_paper_linked_doi"})
    except Exception as e:out["synchrony_source"]={"status":"SOURCE_STOP","error_class":type(e).__name__}
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0
if __name__=="__main__":raise SystemExit(main())
