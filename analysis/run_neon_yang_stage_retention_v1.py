"""Yang et al 2020: pre-outcome recorded stage risk contrasts on the exact
published pair/year/patch design. No causal net dispersal or seasonal fit.
"""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from fractions import Fraction
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from statistics import mean
import json,re
from analysis.audit_neon_seasonal_seed_role_source_v1 import verified_file
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_yang_stage_retention_20261124.json"
SHA="c1c00e8b261e82fddd0b4dd3657f3b14d35cd45f8f8f996b46c54819d1fdb13e"
HEADER=["year","patch_code","seed_station","treatment","seed_species","seed_removal","scatter-hoarding","overwinter_survival"]
RAIN=["year","month","patch_code","seed_trap_code","seed_species","seed_crops"]
# Table 1 of doi:10.1111/ele.13405, not outcome-selected.
DESIGN={
 1:(("QV","CO"),(2015,2016,2017,2018),("B12","F","H")),
 2:(("QS","CG"),(2017,2018),("B21","K","M")),
 3:(("QV","QS"),(2016,2017,2018),("B11","D","A")),
 4:(("CO","CG"),(2016,2017,2018),("B22","L","C")),
 5:(("CO","QS"),(2015,),("B11","L","A")),
 6:(("CA","CF"),(2015,2018),("B22","D","M")),
}
EXPECTED={(g,y,p) for g,(_,ys,ps) in DESIGN.items() for y in ys for p in ps}
PHYSICAL={(y,p) for g,y,p in EXPECTED}
# At shared physical patch-years, the Table 1 pairs contain disjoint species.
# Assign by exact species identity and Table 1, never by outcome or station number.
PAIR_LOOKUP=defaultdict(list)
for g,y,p in sorted(EXPECTED):
    for sp in DESIGN[g][0]:PAIR_LOOKUP[y,p,sp].append(g)

def resolve_pair(y,p,sp):
    options=PAIR_LOOKUP.get((y,p,sp),[])
    if len(options)!=1:raise ValueError('PAIR_IDENTITY_NOT_UNIQUE')
    return options[0]
PUBLISHED=(13870,3806,407)

def req(x,code):
    if not x:raise ValueError(code)
def token(v):
    if v is None:return ""
    if isinstance(v,float) and v.is_integer():return str(int(v))
    return str(v).strip()
def norm(v):return re.sub("[^a-z0-9]","",token(v).lower())
def species(v):
    aliases={"qv":"QV","quercusvariabilis":"QV","qvariabilis":"QV",
        "qs":"QS","quercusserrata":"QS","qserrata":"QS",
        "co":"CO","camelliaoleifera":"CO","camelliaoleigera":"CO","coleifera":"CO",
        "cg":"CG","cyclobalanopsisglauca":"CG","quercusglauca":"CG","cglauca":"CG",
        "ca":"CA","choerospondiasaxillaris":"CA","caxillaris":"CA",
        "cf":"CF","castanopsisfargesii":"CF","cfargesii":"CF"}
    return aliases.get(norm(v))
def treatment(v):
    a=norm(v)
    if a in {"mono","monospecific","monospecificstation","monospecificstations","one","single"}:return "mono"
    if a in {"mixed","mix","mixedstation","mixedstations"}:return "mixed"
    return None
def flag(v):
    a=token(v).lower()
    if a in {"0","1"}:return int(a)
    if a in {"","na","nan","n/a","."}:return None
    raise ValueError("UNVERIFIED_STAGE_VALUE")

def aggregate(rows):
    stations=defaultdict(list)
    totals=Counter();cross=Counter()
    for x in rows:
        y=int(token(x[0]));p=token(x[1]).upper();s=token(x[2])
        t=treatment(x[3]);sp=species(x[4])
        req(s and t is not None and sp is not None,"TABLE1_ROW_IDENTITY_MISMATCH")
        g=resolve_pair(y,p,sp)
        z=tuple(flag(v) for v in x[5:8])
        stations[g,y,p,s].append((t,sp,z))
        for j,v in enumerate(z):
            totals[j]+=int(v==1)
        cross[z]+=1
    req(tuple(totals[j] for j in range(3))==PUBLISHED,"PUBLISHED_POSITIVE_TOTAL_MISMATCH")
    # SH and SDE are cumulative recorded outcomes per released seed.
    # Test strict nesting separately; if not nested, no within-cache survival claim.
    req(all(z[1]!=1 or z[0]==1 for z in cross),"CACHE_WITHOUT_CONFIRMED_REMOVAL")
    req(all(z[2]!=1 or z[0]==1 for z in cross),"SURVIVAL_WITHOUT_CONFIRMED_REMOVAL")
    survival_without_cache=sum(n for z,n in cross.items() if z[2]==1 and z[1]!=1)
    blocks=defaultdict(dict);station_kinds=defaultdict(Counter)
    for (g,y,p,s),v in stations.items():
        req(len(v)==40,"STATION_RELEASE_COUNT_MISMATCH")
        kinds={t for t,sp,z in v};req(len(kinds)==1,"STATION_TREATMENT_MIXED")
        t=next(iter(kinds));by=Counter(sp for _,sp,_ in v)
        pair=DESIGN[g][0]
        if t=="mixed":req(by==Counter({pair[0]:20,pair[1]:20}),"MIXED_COMPOSITION_MISMATCH")
        else:req(len(by)==1 and next(iter(by.values()))==40,"MONO_COMPOSITION_MISMATCH")
        station_kinds[g,y,p][(t,tuple(sorted(by)))]+=1
        for sp,n in by.items():
            k=(g,y,p,sp)
            if t not in blocks[k]:blocks[k][t]=Counter()
            cnt=blocks[k][t];cnt["released"]+=n
            for _,sp2,z in v:
                if sp2!=sp:continue
                for j,name in ((0,"removed"),(1,"cache"),(2,"winter")):
                    cnt[name]+=int(z[j]==1);cnt[name+"_NA"]+=int(z[j] is None)
    req(set(station_kinds)==set(EXPECTED),"PATCH_YEAR_ROSTER_MISMATCH")
    for (g,y,p),d in station_kinds.items():
        a,b=DESIGN[g][0]
        req(d==Counter({("mono",(a,)):3,("mono",(b,)):3,("mixed",tuple(sorted((a,b)))):6}),"TABLE1_STATION_ROSTER_MISMATCH")
    req(len(stations)==540 and len(blocks)==90,"TOTAL_STATION_BLOCK_MISMATCH")
    for x in blocks.values():req(set(x)=={"mono","mixed"} and all(v["released"]==120 for v in x.values()),"SPECIES_ARM_RELEASE_COUNT_MISMATCH")
    return blocks,{"published_positive_totals_verified":list(PUBLISHED),"station_count":len(stations),"pair_patch_year_count":len(EXPECTED),"physical_patch_year_count":len(PHYSICAL),
        "species_patch_year_count":len(blocks),"positive_winter_without_positive_cache":survival_without_cache,
        "joint_stage_flag_counts":{"/".join("NA" if v is None else str(v) for v in k):n for k,n in sorted(cross.items(),key=lambda v:str(v[0]))}}

def bounds(x,stage):
    a,b=x["mixed"],x["mono"]
    na,nb=a["released"],b["released"]
    d=Fraction(a[stage],na)-Fraction(b[stage],nb)
    return d,d-Fraction(b[stage+"_NA"],nb),d+Fraction(a[stage+"_NA"],na)
def average_triplet(a):
    return tuple(mean(v[j] for v in a) for j in range(3))
def sign(x):
    return 1 if x>0 else -1 if x<0 else 0
def interval_sign(x):
    return 1 if x[1]>0 else -1 if x[2]<0 else 0
def summarize(blocks):
    edges=[]
    for g,(spp,years,patches) in DESIGN.items():
        for sp in spp:
            byyear={y:{stage:average_triplet([bounds(blocks[g,y,p,sp],stage) for p in patches]) for stage in ("removed","cache","winter")} for y in years}
            totals={stage:average_triplet([v[stage] for v in byyear.values()]) for stage in ("removed","cache","winter")}
            sc,sw=sign(totals["cache"][0]),sign(totals["winter"][0])
            bsc,bsw=interval_sign(totals["cache"]),interval_sign(totals["winter"])
            classification=("REVERSED" if sc*sw==-1 else "RETAINED" if sc*sw==1 else "ZERO_AT_ONE_OR_BOTH_STAGES")
            # A strict descriptive reversal requires nonzero opposite signs
            # after removing any observed year, and explicit-NA marginal bounds.
            loo=[]
            if len(years)>=2:
                for omitted in years:
                    a=average_triplet([byyear[y]["cache"] for y in years if y!=omitted])
                    b=average_triplet([byyear[y]["winter"] for y in years if y!=omitted])
                    loo.append((interval_sign(a),interval_sign(b)))
            robust=(bsc*bsw==-1 and len(years)>=2 and all(a==bsc and b==bsw for a,b in loo))
            edges.append({"pair":g,"focal_species":sp,"neighbor_species":next(x for x in spp if x!=sp),"years":list(years),
                "pair_patch_years":len(years)*3,
                "stage_effects":{k:{"recorded_risk_difference":float(v[0]),"explicit_NA_only_bounds":[float(v[1]),float(v[2])]} for k,v in totals.items()},
                "classification":classification,"robust_opposite_signs_under_explicit_NA_and_leave_one_year":robust,
                "leave_one_year_checks":len(loo)})
    return {"directed_pair_edges":edges,"classification_counts":dict(Counter(e["classification"] for e in edges)),
        "strict_reversal_edges":sum(e["robust_opposite_signs_under_explicit_NA_and_leave_one_year"] for e in edges),
        "edges_with_multiple_years":sum(len(e["years"])>=2 for e in edges),
        "interpretation":"recorded cumulative outcomes; NA-only bounds do not address unlabelled missing seeds coded 0",
        "not_confidence_intervals_or_causal_net_benefit":True}

def fate(book):
    it=book["Seed_fate_data"].values
    req(list(next(it))==HEADER,"FATE_HEADER_DRIFT")
    rows=list(it)
    req(len(rows)==21600 and all(len(r)==8 for r in rows),"FATE_ROW_COUNT_DRIFT")
    notes=[token(x) for row in book["Note"].values for x in row if token(x)]
    diag={"note":notes,"row_count":len(rows),"literal_year_counts":dict(Counter(token(x[0]) for x in rows)),
        "literal_treatment_counts":dict(Counter(token(x[3]) for x in rows)),
        "literal_species_counts":dict(Counter(token(x[4]) for x in rows)),
        "literal_stage_counts":{HEADER[j]:dict(Counter(token(x[j]) for x in rows)) for j in (5,6,7)},
        "literal_patch_count":len({token(x[1]) for x in rows})}
    try:
        blocks,check=aggregate(rows)
        return {"status":"RECORDED_STAGE_CONTRAST_COMPUTED","source_diagnostics":diag,"design_checks":check,"effect":summarize(blocks)}
    except ValueError as e:
        return {"status":"STOP_FATE_ONTOLOGY_OR_DESIGN","reason":str(e) if re.fullmatch("[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR","source_diagnostics":diag,"effect":None}

def rain(book):
    # Do not confuse Excel's sheet extent with actual observation rows.
    s=book["Seed_rain"];it=s.values;req(list(next(it))==RAIN,"RAIN_HEADER_DRIFT")
    counts=Counter();months=Counter();species_count=Counter();keys=Counter();key_complete=0
    for row in it:
        counts["sheet_rows_iterated"]+=1
        vals=[token(x) for x in row]
        if not any(vals):counts["entirely_blank_rows"]+=1;continue
        counts["nonblank_rows"]+=1
        if not all(vals[:5]):counts["incomplete_key_rows"]+=1;continue
        counts["complete_key_rows"]+=1
        year,month,patch,trap,sp=vals[:5]
        if not re.fullmatch(r"20\d{2}",year):counts["year_literal_unresolved"]+=1;continue
        months[year+"/"+month]+=1;species_count[sp]+=1
        # Distinct observation key count, not sums of seed abundance.
        keys[(year,month,patch,trap,sp)]+=1
        if not vals[5]:counts["blank_crop_values"]+=1
    return {"worksheet_extent_rows_including_header":s.max_row,"source_row_counts":dict(counts),
        "rows_by_literal_year_month":dict(sorted(months.items())),"rows_by_literal_seed_species":dict(sorted(species_count.items())),
        "distinct_observation_keys":len(keys),"repeated_key_excess":sum(n-1 for n in keys.values()),
        "unique_trap_keys":len({(k[2],k[3]) for k in keys}),"no_crop_values_aggregated":True}

def run():
    from openpyxl import load_workbook
    raw=verified_file(9896078,1,17783663,10021976,"0512754403790273d877b07bf2ae7537",SHA)
    book=load_workbook(BytesIO(raw),read_only=True,data_only=True)
    try:
        result=fate(book)
        try:rain_result=rain(book)
        except Exception as e:rain_result={"status":"STOP_RAIN_SCHEMA","error_class":type(e).__name__}
        return {"fate":result,"rain_source":rain_result,"source_sha256":SHA}
    finally:book.close()

def main():
    out={"schema":"neon.yang.stage_retention.v1","submission_hold":True,"Xiao_source_stop_preserved":True,"no_new_seasonal_model":True}
    try:out.update(run())
    except Exception as e:out.update(status="STOP_SOURCE",error_class=type(e).__name__)
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0
if __name__=="__main__":raise SystemExit(main())
