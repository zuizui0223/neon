"""Separate marginal-flag source audit: no nested biological transition.

Keep v2 STOP, source-block partition and original outcome denominators.
A row whose flag pattern violates any intended stage ordering is unknown
for all three outcomes in the conservative sensitivity calculation.
"""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from fractions import Fraction
from io import BytesIO
from statistics import mean
import json,re
from analysis.run_neon_yang_stage_retention_v2 import structure,req,token,flag,verified_file,HEADER,SHA,ROOT,DESIGN,PUBLISHED
OUT=ROOT/"build/neon_yang_marginal_flag_audit_20261124.json"
STAGES=("removed","cache","winter")

def inconsistent(z):
    r,c,w=z
    return any(x is None for x in z) or (c==1 and r!=1) or (w==1 and (r!=1 or c!=1))

def counts(rows,assignments):
    raw=defaultdict(dict);joint=Counter();bad=Counter();total=Counter()
    for (g,y,p,s,t),v in assignments.items():
        for sp,j in v:
            z=tuple(flag(x) for x in rows[j][5:8])
            joint[z]+=1
            invalid=inconsistent(z)
            if invalid:bad[z]+=1
            k=(g,y,p,sp)
            a=raw[k].setdefault(t,Counter())
            a["released"]+=1;a["uncertain"]+=int(invalid)
            for key,val in zip(STAGES,z):
                total[key]+=int(val==1);a[key]+=int(val==1)
                a[key+"_verified_positive"]+=int(val==1 and not invalid)
    req(tuple(total[s] for s in STAGES)==PUBLISHED,"ORIGINAL_FLAG_TOTAL_DRIFT")
    req(len(raw)==90 and all(set(v)=={"mono","mixed"} and all(a["released"]==120 for a in v.values()) for v in raw.values()),"ARM_DENOMINATOR_DRIFT")
    def show(c):return {"/".join("NA" if x is None else str(x) for x in k):n for k,n in sorted(c.items(),key=lambda item:str(item[0]))}
    diag={"joint_flag_counts":show(joint),"non_nested_or_NA_row_patterns":show(bad),"non_nested_or_NA_rows":sum(bad.values()),"total_rows":sum(joint.values()),"marginal_positive_totals":dict(total)}
    return raw,diag

def contrast(a,stage):
    m,n=a["mixed"],a["mono"]
    x,y=m["released"],n["released"]
    d=Fraction(m[stage],x)-Fraction(n[stage],y)
    # All flagged rows are uncertain, including their recorded positive values.
    lo=Fraction(m[stage+"_verified_positive"],x)-Fraction(n[stage+"_verified_positive"]+n["uncertain"],y)
    hi=Fraction(m[stage+"_verified_positive"]+m["uncertain"],x)-Fraction(n[stage+"_verified_positive"],y)
    req(lo<=d<=hi,"RECORDED_CONTRAST_OUTSIDE_BOUNDS")
    return (d,lo,hi)

def average(v):
    return tuple(mean(x[j] for x in v) for j in range(3))
def sign(x):return 1 if x>0 else -1 if x<0 else 0
def robust(v):return 1 if v[1]>0 else -1 if v[2]<0 else 0
def show(v):return {"recorded_RD":float(v[0]),"anomaly_only_bounds":[float(v[1]),float(v[2])]}

def summarize(raw,bypair):
    edges=[]
    for g,(spp,ys,_) in DESIGN.items():
        for sp in spp:
            annual={y:{s:average([contrast(raw[g,y,p,sp],s) for p in sorted(bypair[g,y])]) for s in STAGES} for y in ys}
            avg={s:average([annual[y][s] for y in ys]) for s in STAGES}
            c,w=sign(avg["cache"][0]),sign(avg["winter"][0]);bc,bw=robust(avg["cache"]),robust(avg["winter"])
            loo=[(robust(average([annual[y]["cache"] for y in ys if y!=omit])),robust(average([annual[y]["winter"] for y in ys if y!=omit]))) for omit in ys] if len(ys)>1 else []
            strict=bc*bw==-1 and bool(loo) and all(v==(bc,bw) for v in loo)
            cls="opposite_recorded_signs" if c*w==-1 else "same_nonzero_recorded_sign" if c*w==1 else "zero_at_one_or_both"
            edges.append({"pair":g,"focal_species":sp,"years":list(ys),"stages":{s:show(avg[s]) for s in STAGES},"annual":{str(y):{s:show(v) for s,v in a.items()} for y,a in annual.items()},"classification":cls,"strict_anomaly_bounded_reversal":strict})
    return {"edges":edges,"classification_counts":dict(Counter(e["classification"] for e in edges)),"strict_anomaly_bounded_reversal_edges":sum(e["strict_anomaly_bounded_reversal"] for e in edges),"multiyear_edges":sum(len(e["years"])>1 for e in edges),"bounds_only_cover_explicit_NA_or_nonnested_rows_not_unlabelled_missing_fates":True,"no_transition_or_significance_claim":True}

def run():
    from openpyxl import load_workbook
    data=verified_file(9896078,1,17783663,10021976,"0512754403790273d877b07bf2ae7537",SHA)
    book=load_workbook(BytesIO(data),read_only=True,data_only=True)
    try:
        it=book["Seed_fate_data"].values
        req(list(next(it))==HEADER,"FATE_HEADER_DRIFT")
        rows=list(it);req(len(rows)==21600,"RELEASE_COUNT_DRIFT")
        notes=[token(x) for row in book["Note"].values for x in row if token(x)]
        req(any("1 for success" in x.lower() and "0 for failure" in x.lower() for x in notes),"BINARY_DEFINITION_DRIFT")
        a,b,diag=structure(rows)
        raw,flags=counts(rows,a)
        req(flags["non_nested_or_NA_rows"]>0,"ORIGINAL_STOP_NOT_REPRODUCED")
        return {"status":"MARGINAL_ARCHIVE_FLAG_AUDIT_ONLY","structure":diag,"joint_flags":flags,"marginal_audit":summarize(raw,b)}
    finally:book.close()
def main():
    out={"schema":"neon.yang.marginal_flag_audit.v1","submission_hold":True,"v2_transition_stop_preserved":True,"no_geographic_crosswalk_or_seasonal_model":True}
    try:out.update(run())
    except Exception as e:out.update(status="STOP_SOURCE_OR_DIAGNOSTIC",error_class=type(e).__name__,reason=str(e) if type(e) is ValueError and re.fullmatch("[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR")
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
