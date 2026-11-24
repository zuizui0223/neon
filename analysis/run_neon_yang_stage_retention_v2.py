"""Source-only structural crosswalk and same frozen Yang stage contrasts.

v1 original Table 1 literal patch crosswalk remains an explicit gate.
If source patch labels differ, a separate recorded-block descriptive
contrast is admissible only on complete original pair-year release
architecture identified without stage outcomes. Never infer geographic
patch identity across years, or count the latter as independent sites.
"""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from io import BytesIO
import json,re
from analysis.run_neon_yang_stage_retention_v1 import (
    ROOT,SHA,HEADER,RAIN,DESIGN,EXPECTED,PHYSICAL,PUBLISHED,token,species,flag,
    req,verified_file,average_triplet,bounds,sign,interval_sign,
)
from statistics import mean
OUT=ROOT/"build/neon_yang_stage_retention_v2_20261124.json"
PAIR_SPECIES={frozenset(spp):g for g,(spp,_,_) in DESIGN.items()}

def treatment(v):
    v=token(v).lower()
    return {"mixed":"mixed","monspecific":"mono","monospecific":"mono"}.get(v)

def structure(rows):
    # Only metadata columns; no stage response consulted for any grouping.
    # At a shared source patch-year, station may be reused across pairs.
    source=defaultdict(list)
    for j,x in enumerate(rows):
        y=int(token(x[0]));p=token(x[1]).upper();s=token(x[2])
        t=treatment(x[3]);sp=species(x[4])
        req(y in {2015,2016,2017,2018} and p and s and t and sp,"UNVERIFIED_ORIGINAL_KEY")
        source[y,p,s,t].append((sp,j))
    # Mixed station composition first determines the candidate pair.
    # A reused station label in a shared patch may have four species:
    # partition by uniquely documented pair membership in that year.
    mixed=defaultdict(list)
    for (y,p,s,t),v in source.items():
        if t!="mixed":continue
        sp_counts=Counter(sp for sp,j in v)
        possible=[g for g,(spp,ys,_) in DESIGN.items()
                  if y in ys and all(sp_counts[z]>=20 for z in spp)]
        if len(v)==40:
            req(len(sp_counts)==2 and all(n==20 for n in sp_counts.values()),"MIXED_STATION_COMPOSITION")
            g=PAIR_SPECIES.get(frozenset(sp_counts))
            req(g in possible,"MIXED_PAIR_NOT_IN_TABLE1_YEAR")
            mixed[y,p,g].append((s,v))
        else:
            # No arbitrary partition: require pairwise disjoint candidate
            # species, each appearing exactly 20 times, covering every row.
            req(possible and len(possible)*40==len(v),"MIXED_STATION_REUSE_UNRESOLVED")
            seen=set()
            for g in possible:
                spp=set(DESIGN[g][0])
                req(not seen&spp and all(sp_counts[z]==20 for z in spp),"AMBIGUOUS_SHARED_STATION_PAIR")
                seen|=spp
                mixed[y,p,g].append((s,[(sp,j) for sp,j in v if sp in spp]))
            req(seen==set(sp_counts),"MIXED_STATION_NOT_EXHAUSTIVE")
    bypair=defaultdict(set)
    for y,p,g in mixed:bypair[g,y].add(p)
    req(set(bypair)=={(g,y) for g,(_,ys,_) in DESIGN.items() for y in ys},"PAIR_YEAR_ROSTER_MISMATCH")
    req(all(len(ps)==3 for ps in bypair.values()),"NOT_THREE_SOURCE_PATCH_LABELS_PER_PAIR_YEAR")
    assignments=defaultdict(list)
    for (y,p,g),ss in mixed.items():
        req(len(ss)==6 and len({s for s,v in ss})==6,"MIXED_STATION_ROSTER_MISMATCH")
        for s,v in ss:assignments[g,y,p,s,"mixed"].extend(v)
    for (y,p,s,t),v in source.items():
        if t!="mono":continue
        bysp=defaultdict(list)
        for sp,j in v:bysp[sp].append((sp,j))
        for sp,rr in bysp.items():
            req(len(rr)==40,"MONO_STATION_COMPOSITION_MISMATCH")
            options=[g for yy,pp,g in mixed if yy==y and pp==p and sp in DESIGN[g][0]]
            req(len(options)==1,"MONO_PAIR_IDENTITY_NOT_UNIQUE")
            assignments[options[0],y,p,s,"mono"].extend(rr)
    roster=defaultdict(Counter);ids=[]
    for (g,y,p,s,t),v in assignments.items():
        req(len(v)==40,"FINAL_STATION_COUNT_MISMATCH")
        spp=tuple(sorted({sp for sp,j in v}))
        roster[g,y,p][(t,spp)]+=1
        ids.extend(j for sp,j in v)
    req(len(ids)==21600 and len(set(ids))==21600 and set(ids)==set(range(len(rows))),"RELEASE_ROW_PARTITION_MISMATCH")
    req(len(assignments)==540 and len(roster)==45,"TOTAL_STATION_OR_PAIR_PATCH_MISMATCH")
    # No station ID may denote both treatments within an inferred pair block.
    station_keys={(g,y,p,s) for g,y,p,s,t in assignments}
    req(len(station_keys)==540,"STATION_TREATMENT_IDENTITY_COLLISION")
    for (g,y,p),v in roster.items():
        a,b=DESIGN[g][0]
        req(v==Counter({("mono",(a,)):3,("mono",(b,)):3,("mixed",tuple(sorted((a,b)))):6}),"TABLE1_RELEASE_ARCHITECTURE_MISMATCH")
    literal_match=set(roster)==EXPECTED
    diag={"source_patch_labels":sorted({p for y,p,s,t in source}),
          "source_physical_patch_year_labels":len({(y,p) for g,y,p in roster}),
          "pair_patch_year_blocks":len(roster),"station_blocks":len(assignments),
          "literal_table1_patch_roster_match":literal_match,
          "pair_year_source_patch_labels":[{"pair":g,"year":y,"source_labels":sorted(ps),
            "table1_labels":sorted(DESIGN[g][2])} for (g,y),ps in sorted(bypair.items())],
          "geographic_identity_not_inferred_from_label":True}
    return assignments,bypair,diag

def stages(rows,assignments):
    totals=Counter();cross=Counter();blocks=defaultdict(dict)
    for (g,y,p,s,t),v in assignments.items():
        for sp,j in v:
            z=tuple(flag(x) for x in rows[j][5:8])
            for k,val in enumerate(z):totals[k]+=int(val==1)
            cross[z]+=1
            k=(g,y,p,sp)
            cnt=blocks[k].setdefault(t,Counter())
            cnt["released"]+=1
            for name,val in zip(("removed","cache","winter"),z):
                cnt[name]+=int(val==1);cnt[name+"_NA"]+=int(val is None)
    req(tuple(totals[j] for j in range(3))==PUBLISHED,"PUBLISHED_STAGE_TOTAL_MISMATCH")
    req(all(z[1]!=1 or z[0]==1 for z in cross),"CACHE_WITHOUT_CONFIRMED_REMOVAL")
    req(all(z[2]!=1 or z[0]==1 for z in cross),"SURVIVAL_WITHOUT_CONFIRMED_REMOVAL")
    req(len(blocks)==90 and all(set(v)=={"mono","mixed"} and all(c["released"]==120 for c in v.values()) for v in blocks.values()),"SPECIES_RELEASE_DENOMINATOR_MISMATCH")
    return blocks,{"joint_stage_flag_counts":{"/".join("NA" if x is None else str(x) for x in k):n for k,n in sorted(cross.items(),key=lambda item:str(item[0]))},
        "published_positive_totals":list(PUBLISHED),"species_arm_comparisons":len(blocks),
        "positive_winter_without_positive_cache":sum(n for z,n in cross.items() if z[2]==1 and z[1]!=1)}

def summarize(blocks,bypair):
    edges=[]
    for g,(spp,years,_) in DESIGN.items():
        for sp in spp:
            peryear={y:{stage:average_triplet([bounds(blocks[g,y,p,sp],stage) for p in sorted(bypair[g,y])]) for stage in ("removed","cache","winter")} for y in years}
            totals={stage:average_triplet([v[stage] for v in peryear.values()]) for stage in ("removed","cache","winter")}
            sc,sw=sign(totals["cache"][0]),sign(totals["winter"][0])
            bc,bw=interval_sign(totals["cache"]),interval_sign(totals["winter"])
            cls="REVERSED" if sc*sw==-1 else "RETAINED" if sc*sw==1 else "ZERO_AT_ONE_OR_BOTH_STAGES"
            loo=[]
            for omitted in years if len(years)>1 else ():
                a=average_triplet([peryear[y]["cache"] for y in years if y!=omitted])
                b=average_triplet([peryear[y]["winter"] for y in years if y!=omitted])
                loo.append((interval_sign(a),interval_sign(b)))
            strict=bc*bw==-1 and len(years)>=2 and all(a==bc and b==bw for a,b in loo)
            def show(v):return {"recorded_risk_difference":float(v[0]),"explicit_NA_only_bounds":[float(v[1]),float(v[2])]}
            edges.append({"pair":g,"focal_species":sp,"neighbor_species":next(x for x in spp if x!=sp),
                "years":list(years),"classification":cls,"strict_reversal":strict,
                "stage_effects":{k:show(v) for k,v in totals.items()},
                "annual_stage_effects":{str(y):{k:show(v) for k,v in stages.items()} for y,stages in peryear.items()}})
    return {"edges":edges,"classification_counts":dict(Counter(e["classification"] for e in edges)),
        "strict_reversal_edges":sum(e["strict_reversal"] for e in edges),
        "edges_with_multiple_years":sum(len(e["years"])>=2 for e in edges),
        "recorded_flags_not_unknown_fate_corrected":True,"not_net_recruitment_or_statistical_significance":True}

def rain_audit(book):
    s=book["Seed_rain"];it=s.values
    req(list(next(it))==RAIN,"RAIN_HEADER_DRIFT")
    data=defaultdict(list);months=defaultdict(set);patchyears=defaultdict(set)
    n=Counter();labels=defaultdict(set)
    for row in it:
        v=[token(x) for x in row]
        if not any(v):continue
        n["nonblank"]+=1
        if len(v)!=6 or not all(v):n["incomplete"]+=1;continue
        y,m,p,t,sp,c=v
        if not re.fullmatch(r"20\d{2}",y) or m not in {"8","9","10","11","12"} or species(sp) is None:
            n["invalid_key"]+=1;continue
        try:
            x=float(c)
            if x<0 or not x.is_integer():raise ValueError()
        except (ValueError,OverflowError):n["invalid_crop_value"]+=1;continue
        # Audit multiplicities and identical/different values. Neither dedup
        # nor sum rows: unknown collection-round identities and zeros.
        k=(int(y),int(m),p.upper(),t,species(sp))
        data[k].append(x);months[k[0],k[2],k[4]].add(k[1]);patchyears[k[0],k[2]].add(k[4])
    n["distinct_keys"]=len(data)
    n["repeated_key_excess"]=sum(len(v)-1 for v in data.values())
    n["repeated_keys_all_equal"]=sum(len(v)>1 and len(set(v))==1 for v in data.values())
    n["repeated_keys_different_values"]=sum(len(set(v))>1 for v in data.values())
    n["explicit_zero_rows"]=sum(x==0 for v in data.values() for x in v)
    return {"counts":dict(n),"multiplicity_histogram":dict(Counter(len(v) for v in data.values())),
        "month_coverage_histogram_by_patch_year_species":dict(Counter(len(v) for v in months.values())),
        "species_coverage_by_patch_year":[{"year":y,"patch_label":p,"species":sorted(v)} for (y,p),v in sorted(patchyears.items())],
        "no_deduplication_no_sums_no_missing_month_imputation":True}

def run():
    from openpyxl import load_workbook
    raw=verified_file(9896078,1,17783663,10021976,"0512754403790273d877b07bf2ae7537",SHA)
    book=load_workbook(BytesIO(raw),read_only=True,data_only=True)
    out={"effect":None,"source_sha256":SHA}
    try:
        it=book["Seed_fate_data"].values;req(list(next(it))==HEADER,"FATE_HEADER_DRIFT")
        rows=list(it);req(len(rows)==21600 and all(len(r)==8 for r in rows),"FATE_ROW_COUNT_DRIFT")
        notes=[token(x) for row in book["Note"].values for x in row if token(x)]
        req(any("1 for success" in x.lower() and "0 for failure" in x.lower() for x in notes),"AUTHOR_BINARY_DEFINITION_MISSING")
        # Publish source-label grouping even when the full architecture fails.
        out["source_label_support"]=[{"year":y,"patch":p,"species_counts":dict(c)} for (y,p),c in sorted(_label_counts(rows).items())]
        try:
            assignments,bypair,diag=structure(rows);out["structure"]=diag
            blocks,check=stages(rows,assignments);out["stage_checks"]=check
            out["status"]="EXACT_TABLE1_RECORDED_STAGE_CONTRAST" if diag["literal_table1_patch_roster_match"] else "ARCHIVE_BLOCK_DESCRIPTIVE_CONTRAST_ONLY_TABLE1_LABEL_STOP"
            out["effect"]=summarize(blocks,bypair)
        except ValueError as e:out.update(status="STOP_RELEASE_ARCHITECTURE",reason=str(e) if re.fullmatch("[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR")
        try:out["rain_source"]=rain_audit(book)
        except Exception as e:out["rain_source"]={"status":"STOP_RAIN_SOURCE","error_class":type(e).__name__}
    finally:book.close()
    return out
def _label_counts(rows):
    ans=defaultdict(Counter)
    for x in rows:ans[int(token(x[0])),token(x[1]).upper()][token(x[4])]+=1
    return ans
def main():
    out={"schema":"neon.yang.stage_retention.v2","submission_hold":True,"original_v1_stop_preserved":True,
         "no_new_seasonal_effect":True}
    try:out.update(run())
    except Exception as e:out.update(status="STOP_SOURCE_OR_ONTOLOGY",effect=None,error_class=type(e).__name__,reason=str(e) if type(e) is ValueError and re.fullmatch("[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR")
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0
if __name__=="__main__":raise SystemExit(main())
