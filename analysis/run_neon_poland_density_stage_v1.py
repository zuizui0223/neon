"""Pinned OSF CSV dialect and ecological stage contrast.

Run original-byte and source code semantics checks before any grouped effect.
Stage decomposition targets documented cache per offered seed; it cannot identify
germination or causal density effects. No fitted seasonal effect.
"""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from fractions import Fraction
from hashlib import md5,sha256
from io import StringIO
from pathlib import Path
from statistics import mean
import csv,json,re
from analysis.audit_neon_consumer_pressure_source_v1 import api,get,req,pages,OSF
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_poland_density_stage_20261125.json"
MANIFEST=[{"file_id":"65c22b0f435c45096dda7403","name":"dispersal & abundance data.csv","size":777522,"sha256":"b9ce41fdbb32c5f2e03267583e731a9c00a86e2868cee832ceb5c5f00f3eb5db","md5":"10c60e03edcb1b53f1cc70d4a87c6072"},{"file_id":"65c22c481a30ef0a01c3477a","name":"Seedlings - all.csv","size":7751,"sha256":"ebf19226feb1efbb1de61f4d54aaf9659e416ca430cfab6c7d7c059965f840f8","md5":"93b192260015f9fd9f94af8ce76cf297"},{"file_id":"65c22c8e435c450972da7454","name":"abundances and interactions 25.12.2023.csv","size":7316,"sha256":"72c64305695978a7324dea138ad8fe9ec38864246946d1e261f96cd65f9ed057","md5":"3d7cbcad0a7105954599f5656d08449c"}]
# Source header vocabulary from paper 2.3 and 2.5. Fail closed on unknown
# or duplicate semantic columns; report actual labels for later interpretation.
ROLE_ALIASES={
 "year":{"year","rok"},
 "site":{"site","siteid","plot","plotid","grid","gridid","location","studyarea","area","powierzchnia"},
 "session":{"session","sessionid","trappingsession","trappingperiod","sessionnumber","sessionno","sesja"},
 "day":{"day","dayofexperiment","dayofyear","date","doy","julianday"},
 "abundance":{"abundance","mouseabundance","miceabundance","apodemusabundance","afabundance","af","numberofmice","mice","nind","afnumber","nummice","mousecount","rodentabundance"},
 "actor":{"species","rodentspecies","consumerspecies","remover","removerspecies","animal","animalsp","disperser","disperserspecies","sp"},
 "removed":{"removal","removed","seedremoval","isremoved"},
 "recovered":{"recovery","recovered","found","seedrecovery","isfound"},
 "fate":{"fate","seedfate","seedstatus","status","seedcondition","condition","seedstate","postdispersalstate","dispersalstatus"},
 "cache":{"cache","cached","caching","hoarded","hoarding"},
 "consumed":{"consumed","consumption","eaten","predation"},
 "surface":{"surface","leftonsurface","onsurface","leftsurface"},
}
def norm(x):return re.sub(r"[^a-z0-9]","",str(x).strip().lower())
def parse(data):
    try:txt=data.decode("utf-8-sig")
    except UnicodeDecodeError:txt=data.decode("latin1")
    choices=[]
    for sep in (";",",","\t"):
        rows=list(csv.reader(StringIO(txt,newline=""),delimiter=sep))
        if not rows:continue
        # Excel exports may start with a blank index-header column.
        header=[x.strip() for x in rows[0]]
        rest=rows[1:]
        if len(header)>=2 and len(set(header))==len(header) and all(len(x)<=200 for x in header) and all(len(r)==len(header) for r in rest):
            choices.append((sep,header,rest))
    req(len(choices)==1,"CSV_DIALECT_NOT_UNIQUE")
    sep,h,rows=choices[0]
    return sep,h,rows
def roles(h):
    out={}
    for name,aliases in ROLE_ALIASES.items():
        k=[i for i,v in enumerate(h) if norm(v) in aliases]
        if len(k)==1:out[name]=k[0]
    return out
def diagnostics(sep,h,rows):
    res={"delimiter":repr(sep),"header":h,"data_rows":len(rows),"unambiguous_candidate_roles":{k:h[i] for k,i in roles(h).items()},"column_profiles":[]}
    for i,name in enumerate(h):
        c=Counter(str(x[i]).strip() for x in rows)
        # Only low-cardinality documented source category/flag fields are
        # exported as literals, not tag IDs, distances or other raw values.
        label=norm(name);allowed=set().union(*(ROLE_ALIASES[k] for k in ("year","session","actor","removed","recovered","fate","cache","consumed","surface")))
        v={"column":name,"distinct_literal_count":len(c),"blank_count":c.get("",0)}
        if label in allowed and len(c)<=35:v["category_counts"]=dict(c)
        res["column_profiles"].append(v)
    return res

def fetch_all():
    root=api(f"https://api.osf.io/v2/nodes/{OSF}/")["data"]
    req(root["id"]==OSF and root["attributes"].get("public") is True,"OSF_IDENTITY")
    found={}
    for f in pages(f"https://api.osf.io/v2/nodes/{OSF}/files/osfstorage/"):
        a=f["attributes"]
        if a["kind"]=="file":found[f["id"]]=f
    out={}
    for m in MANIFEST:
        f=found.get(m["file_id"]);req(f is not None,"ORIGINAL_OSF_FILE_MISSING")
        a=f["attributes"]
        req(a["name"]==m["name"] and a["size"]==m["size"],"ORIGINAL_OSF_FILE_ROSTER_DRIFT")
        raw,_=get(f["links"]["download"],m["size"])
        req(len(raw)==m["size"] and sha256(raw).hexdigest()==m["sha256"] and md5(raw).hexdigest()==m["md5"],"OSF_PINNED_SOURCE_DRIFT")
        out[m["name"]]=parse(raw)
    return out
def boolean(v):
    s=norm(v)
    if s in {"0","no","false"}:return 0
    if s in {"1","yes","true"}:return 1
    if s in {"","na","nan"}:return None
    raise ValueError("UNVERIFIED_BINARY_FLAG")
def actor(v):
    a=norm(v)
    if a in {"af","apodemusflavicollis","yellowneckedmouse","yellowneckedmice","aflavicollis"}:return "mouse"
    if a in {"mg","myodesglareolus","clethrionomysglareolus","bankvole","mglareolus"}:return "vole"
    if a in {"","na","nan","none","0","notremoved"}:return None
    raise ValueError("UNVERIFIED_REMOVER_LITERAL")
def fate(v):
    a=norm(v)
    for category,opts in {"cache":{"cache","cached","hoarded","hoarding","buried"},
        "consumed":{"consumed","eaten","fullyeaten","completelyeaten"},
        "surface":{"surface","leftonsurface","onsurface","leftsurface"},
        "missing":{"missing","notfound","unrecovered","lost"},
        "station":{"notremoved","unremoved","intactatstation","leftatstation","notaken","nottaken"}}.items():
        if a in opts:return category
    if a in {"","na","nan"}:return None
    raise ValueError("UNVERIFIED_FATE_LITERAL")
def number(v):
    # Decimal comma is a legitimate regional CSV convention. No guessing
    # thousands separators; integer abundance required.
    s=str(v).strip().replace(",",".")
    req(bool(re.fullmatch(r"[0-9]+(?:\.0+)?",s)),"NONINTEGER_ABUNDANCE")
    return int(float(s))
def observations(h,rows):
    rm=roles(h)
    req(len(rows)==7054,"PUBLISHED_RELEASE_ROW_COUNT_MISMATCH")
    needed={"year","site","abundance","actor","removed","fate"}
    req(needed<=set(rm) and ("session" in rm or "day" in rm),"SOURCE_ROLE_UNRESOLVED")
    grouping="session" if "session" in rm else "day"
    groups=defaultdict(Counter);ab=defaultdict(set);tot=Counter()
    for row in rows:
        v=lambda k:row[rm[k]]
        year=number(v("year"));site=v("site").strip();t=v(grouping).strip()
        req(year in {2020,2021,2022} and site and t,"INVALID_CONTEXT_KEY")
        key=(year,site,t);a=number(v("abundance"))
        ab[key].add(a);g=groups[key];g["offered"]+=1
        rem=boolean(v("removed"));who=actor(v("actor"));f=fate(v("fate"))
        req(rem is not None,"UNKNOWN_REMOVAL_FLAG")
        tot["offered"]+=1;tot["removed"]+=rem
        if rem==0:
            req(f in {None,"station"} and who is None,"NONREMOVAL_FATE_CONFLICT")
            continue
        req(who in {"mouse","vole"} and f not in {None,"station"},"REMOVAL_FATE_OR_ACTOR_UNRESOLVED")
        if who=="vole":tot["vole"]+=1;g["vole"]+=1;continue
        g["mouse_removed"]+=1;g[f]+=1;tot["mouse_removed"]+=1;tot[f]+=1
        if "recovered" in rm:req(boolean(v("recovered"))==int(f!="missing"),"RECOVERY_FATE_CONFLICT")
    for k,n in {"offered":7054,"removed":2999,"vole":13,"mouse_removed":2986,"cache":559,"consumed":894,"surface":290,"missing":1243}.items():
        req(tot[k]==n,"PUBLISHED_"+k.upper()+"_TOTAL_MISMATCH")
    req(all(len(x)==1 for x in ab.values()),"AMBIGUOUS_CONTEXT_ABUNDANCE")
    # Day may identify a session only if the observed archive independently
    # reproduces exactly five unique contexts per original site-year.
    roster=Counter((y,s) for y,s,t in groups)
    req(len({s for y,s,t in groups})==6 and len(roster)==18 and all(n==5 for n in roster.values()) and len(groups)==90,"ORIGINAL_90_SITE_SESSION_YEAR_ROSTER_REQUIRED")
    return groups,{k:next(iter(v)) for k,v in ab.items()},grouping,dict(tot)

def pool(rows):
    out=Counter()
    for row in rows:out.update(row)
    return out
def stage(c):
    n=c["offered"];h=c["mouse_removed"];k=c["cache"];u=c["missing"]
    req(n>0 and 0<=k<=h<=n and 0<=u<=h-k,"INVALID_STAGE_COUNTS")
    return {"harvest":Fraction(h,n),"conditional_cache":Fraction(k,h) if h else None,
            "cache":Fraction(k,n),"cache_upper":Fraction(k+u,n),
            "conditional_cache_upper":Fraction(k+u,h) if h else None}
def pair(lo,hi):
    a,b=stage(lo),stage(hi)
    req(a["conditional_cache"] is not None and b["conditional_cache"] is not None,"ZERO_MOUSE_HARVEST_IN_EXTREME")
    d=b["cache"]-a["cache"]
    encounter=(b["harvest"]-a["harvest"])*(b["conditional_cache"]+a["conditional_cache"])/2
    allocation=(b["conditional_cache"]-a["conditional_cache"])*(b["harvest"]+a["harvest"])/2
    req(d==encounter+allocation,"DECOMPOSITION_IDENTITY")
    return {"harvest_RD":b["harvest"]-a["harvest"],
            "conditional_recorded_cache_RD":b["conditional_cache"]-a["conditional_cache"],
            "recorded_cache_per_offered_RD":d,"harvest_component":encounter,"post_harvest_component":allocation,
            "cache_RD_lower":b["cache"]-a["cache_upper"],"cache_RD_upper":b["cache_upper"]-a["cache"],
            "conditional_RD_lower":b["conditional_cache"]-a["conditional_cache_upper"],
            "conditional_RD_upper":b["conditional_cache_upper"]-a["conditional_cache"]}
def compare(groups,ab):
    sy=defaultdict(list)
    for k,c in groups.items():sy[k[:2]].append(k)
    results=[];stops=Counter()
    for (y,s),keys in sorted(sy.items()):
        low=min(ab[k] for k in keys);high=max(ab[k] for k in keys)
        if low==high:stops["constant_abundance"]+=1;continue
        a=pool(groups[k] for k in keys if ab[k]==low);b=pool(groups[k] for k in keys if ab[k]==high)
        if not a["mouse_removed"] or not b["mouse_removed"]:stops["zero_harvest"]+=1;continue
        results.append((y,s,pair(a,b)))
    # Same-site-year description, not an abundance intervention or seasonal
    # adjustment. Require support in all six sites and three years.
    out={"eligible_site_years":len(results),"excluded_context_counts":dict(stops),"effect":None}
    if len(results)<12 or len({s for y,s,v in results})!=6 or len({y for y,s,v in results})!=3:
        return {**out,"status":"STOP_INSUFFICIENT_EXTREME_PAIR_SUPPORT"}
    keys=list(results[0][2]);aver={k:mean(v[k] for y,s,v in results) for k in keys}
    site={s:{k:mean(v[k] for y,t,v in results if t==s) for k in keys} for s in sorted({s for y,s,v in results})}
    balanced={k:mean(v[k] for v in site.values()) for k in keys}
    support=balanced["harvest_component"]>0 and balanced["post_harvest_component"]<0 and sum(v["harvest_component"]>0 and v["post_harvest_component"]<0 for v in site.values())>=5
    return {**out,"status":"DESCRIPTIVE_OFFSET_SUPPORTED" if support else "DESCRIPTIVE_OFFSET_NOT_SUPPORTED",
            "effect":{"equal_site_mean":{k:float(v) for k,v in balanced.items()},
                      "equal_site_year_mean":{k:float(v) for k,v in aver.items()},
                      "sites_opposite_components":sum(v["harvest_component"]>0 and v["post_harvest_component"]<0 for v in site.values()),
                      "cache_direction_identified_under_missing_fate":balanced["cache_RD_lower"]>0 or balanced["cache_RD_upper"]<0,
                      "conditional_direction_identified_under_missing_fate":balanced["conditional_RD_lower"]>0 or balanced["conditional_RD_upper"]<0,
                      "not_causal_density_or_true_germination":True,"day_and_density_can_covary":True}}
def run():
    files=fetch_all();out={"source_schema":{name:diagnostics(*parts) for name,parts in files.items()}}
    sep,h,rows=files["dispersal & abundance data.csv"]
    try:
        g,ab,group,tot=observations(h,rows)
        out["context_grouping"]=group;out["published_count_reconciliation"]=tot
        out.update(compare(g,ab))
    except ValueError as e:
        out.update(status="STOP_SOURCE_SEMANTICS_OR_DESIGN",reason=str(e) if re.fullmatch("[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR",effect=None)
    return out
def main():
    out={"schema":"neon.poland.density_stage_decomposition.v1","submission_hold":True,
         "new_stage_model_not_original_published_effect":True,"qinling_source_stop_preserved":True}
    try:out.update(run())
    except Exception as e:out.update(status="STOP_SOURCE_REPLAY",error_class=type(e).__name__,reason=str(e) if type(e) is ValueError and re.fullmatch("[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR",effect=None)
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
