"""Diagnose exact S1 source keys and independent annual capture support.

No biological association, count response model, missing-species imputation,
or date inference. No original biological rows, animal IDs or plot coordinates
exported. All original mismatches counted; source-only nominal valid-key join.
"""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from hashlib import sha256
from io import BytesIO,StringIO
from pathlib import Path
from zipfile import ZipFile
import csv,json,re
from analysis.audit_neon_holt_plant_sources_v1 import SOURCES,download_version
from analysis.audit_neon_seasonal_seed_role_source_v1 import verified_file,DRI_SHA
from analysis.run_neon_holt_acorn_preceding_upcoming_v1 import read_csv,CAPTURE_YEARS
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_holt_annual_bridge_source_20261124.json"
PLANT_SHA={"seedfall":"64d8cab3e85bafe321b6a43543b04fec877fe9f2244ab54421301e6ddd63a2f4",
           "seedling":"a1f1939184446348dcbe9641f061fd6dba11f0b5dce27bfec73fa4f55bacbd5f"}
CAP_SHA="ca47ac53e0f5b91fedaad3d7a6c3ba0be3efc918cbe280729c06818e35c768e5"
YEARS=tuple(range(1988,2014))
def req(ok,label):
    if not ok:raise ValueError(label)

def key_diagnosis(rows,kind):
    bad=Counter();bad_tokens=Counter();valid=set();valid_species=set();dup=Counter()
    byyear=Counter();year_plots=defaultdict(set);year_non_species_marker=Counter()
    species_per_key=defaultdict(set);effort=Counter();layout=Counter()
    orig_n=0
    for row in rows:
        orig_n+=1
        y0=row["YEAR"].strip();l=row["LINE"].strip();p0=row["PLOT"].strip()
        causes=[]
        if not re.fullmatch(r"(19|20)\d{2}",y0):causes.append("YEAR_NOT_FOUR_DIGIT")
        if l not in {"N","S"}:causes.append("LINE_NOT_N_S")
        if not re.fullmatch(r"[+-]?\d+",p0):causes.append("PLOT_NOT_INTEGER")
        elif not 1<=int(p0)<=600:causes.append("PLOT_OUTSIDE_1_600")
        if causes:
            for c in causes:bad[c]+=1
            # These are environmental station codes, not capture identities.
            # Limit token disclosure to short source code shapes/plot values.
            if "PLOT_OUTSIDE_1_600" in causes:bad_tokens["out_of_range_plot:"+str(int(p0))]+=1
            if "LINE_NOT_N_S" in causes:bad_tokens["line:"+repr(l)[:24]]+=1
            if "PLOT_NOT_INTEGER" in causes:bad_tokens["plot_literal_shape:"+re.sub(r"\d+","D",p0)[:20]]+=1
            bad["rows_with_any_invalid_key"]+=1
            continue
        y=int(y0);p=int(p0);k=(y,l,p)
        valid.add(k);year_plots[y].add((l,p));byyear[y]+=1
        layout[str(p%10)]+=1
        sp=row["FIASP"].strip()
        # Distinguish literal code/explicit zero-marker from absent species.
        is_marker=sp in {"","0","000","NA","N/A"} or row.get("SPEC","").strip() in {"0","0.0"}
        if is_marker:
            year_non_species_marker[y]+=1
        else:
            valid_species.add((*k,sp));species_per_key[k].add(sp)
        dup[(*k,sp,row.get("SPEC","").strip())]+=1
        fields=["COUNT"] if kind=="seedfall" else ["HT1","HT2","HT3","HT4"]
        for f in fields:
            v=row[f].strip()
            if v=="0":effort[f+"_explicit_zero"]+=1
            elif not v:effort[f+"_blank"]+=1
            elif not re.fullmatch(r"\d+",v):effort[f+"_noninteger_literal"]+=1
    return {"original_rows":orig_n,"invalid_key_reason_counts":dict(bad),
        "invalid_key_token_counts":dict(bad_tokens),"valid_nominal_plot_year_keys":len(valid),
        "valid_distinct_nominal_plots":len({(l,p) for y,l,p in valid}),
        "rows_by_year":dict(sorted(byyear.items())),
        "observed_plots_by_year":{str(y):len(s) for y,s in sorted(year_plots.items())},
        "plot_number_mod10_counts":dict(layout),
        "literal_non_species_marker_rows_by_year":dict(sorted(year_non_species_marker.items())),
        "duplicate_full_year_line_plot_FIASP_SPEC_excess":sum(n-1 for n in dup.values() if n>1),
        "explicit_zero_blank_noninteger_field_counts":dict(effort),
        "observed_species_keys":len(valid_species),"not_complete_effort_or_species_absence":True},valid,valid_species

def pair_support(seed,seedling,seedsp,seedlingsp):
    o={}
    for lag in (0,1):
        # lag=0 is same collection-year label, not proven crop-year chronology.
        matched={k for k in seed if (k[0]+lag,k[1],k[2]) in seedling}
        spmat={k for k in seedsp if (k[0]+lag,*k[1:]) in seedlingsp}
        o[str(lag)]={"matched_plot_year_keys":len(matched),
            "matched_years":sorted({k[0] for k in matched}),
            "matched_plots":len({k[1:] for k in matched}),
            "matched_species_plot_year_keys":len(spmat),
            "red_oak_FIASP_833_shared_keys":sum(k[-1]=="833" for k in spmat),
            "matched_plot_keys_by_seed_label_year":dict(sorted(Counter(k[0] for k in matched).items()))}
    return o

def plant():
    from playwright.sync_api import sync_playwright
    out={};keys={};sp={}
    with sync_playwright() as pw:
        browser=pw.chromium.launch()
        for name,(url,n,fields) in SOURCES.items():
            page=browser.new_page(accept_downloads=True)
            try:
                raw=download_version(page,url)
                req(sha256(raw).hexdigest()==PLANT_SHA[name],"ORIGINAL_PLANT_SHA256_DRIFT")
                req(not raw.startswith(b"PK"),"EXPECTED_ORIGINAL_CSV_BYTES")
                try:txt=raw.decode("utf-8-sig")
                except UnicodeError:txt=raw.decode("latin1")
                reader=csv.DictReader(StringIO(txt,newline=""))
                req(reader.fieldnames and fields<=set(reader.fieldnames),"ORIGINAL_FIELDS_DRIFT")
                rows=list(reader);req(len(rows)==n,"ORIGINAL_ROW_COUNT_DRIFT")
                report,ks,ss=key_diagnosis(rows,name)
                report["original_sha256"]=PLANT_SHA[name]
                out[name]=report;keys[name]=ks;sp[name]=ss
            except Exception as e:out[name]={"status":"STOP_REPLAY_OR_SCHEMA","error_class":type(e).__name__}
            finally:page.close()
        browser.close()
    if set(keys)==set(SOURCES):
        out["observed_nominal_keys_only"]=pair_support(keys["seedfall"],keys["seedling"],sp["seedfall"],sp["seedling"])
    return out

def explicit_august(s):
    return str(s).strip().lower() in {"8","08","aug","august"}

def annual_capture(cap,summary,old):
    hist=defaultdict(set);months=Counter();ids=defaultdict(set);rows_year=Counter();bad=Counter()
    for x in cap:
        y=int(x["year"]);idv=x["id_new"].strip();m=x["month"].strip()
        months[m]+=1;rows_year[y]+=1
        if not idv:bad["blank_capture_id"]+=1
        else:ids[y].add(idv)
        key=(y,idv,x["STRAPSTAT"].strip(),x["date"].strip())
        hist[key].add(m)
    ann={};duplicate=0
    for x in summary:
        y=int(x["year"])
        if y in ann:duplicate+=1
        ann[y]=x
    cmp=Counter()
    for y,x in ann.items():
        if not explicit_august(x["month"]):cmp["summary_nonaugust"]+=1
        try:n=int(x["nind"])
        except ValueError:cmp["summary_nind_unresolved"]+=1;continue
        cmp["summary_equals_unique_ID" if n==len(ids.get(y,set())) else "summary_differs_unique_ID"]+=1
    match=Counter();byyear=defaultdict(Counter)
    for x in old:
        y=int(x["year"])
        if y not in CAPTURE_YEARS or x["used"].strip()!="1":continue
        k=(y,x["id_new"].strip(),x["STRAPSTAT"].strip(),x["date"].strip())
        options=hist.get(k,set())
        status=("exact_match_all_explicit_august" if options and all(explicit_august(m) for m in options)
                else "exact_match_nonaugust_or_ambiguous" if options else "no_exact_match")
        match[status]+=1;byyear[y][status]+=1
    return {"capture_rows":len(cap),"capture_years":sorted(rows_year),
            "literal_month_counts":dict(months),"identity_quality_counts":dict(bad),
            "summary_rows":len(summary),"duplicate_summary_years":duplicate,
            "summary_years":sorted(ann),"annual_nind_crosscheck_counts":dict(cmp),
            "old_2022_target_used_exact_crosswalk":dict(match),
            "old_crosswalk_counts_by_year":{str(y):dict(c) for y,c in sorted(byyear.items())},
            "no_new_date_decoding_or_effect":True}

def capture():
    raw=verified_file(27152484,2,50529696,131218,"750f8d669a890e3450c4a61a2794c223",CAP_SHA)
    oldraw=verified_file(15029247,1,36110309,2277102,"5f5263ba55a2d72c886d170ec5d38c43",DRI_SHA)
    def read(z,name,n):
        r=csv.DictReader(StringIO(z.read("Data and code/Data/"+name).decode("utf-8-sig"),newline=""))
        data=list(r);req(len(data)==n,"SOURCE_ROW_COUNT_DRIFT");return data
    with ZipFile(BytesIO(raw)) as z,ZipFile(BytesIO(oldraw)) as oldz:
        cap=read(z,"mice83_21_tr_aug.csv",11549)
        summary=read(z,"mice83_21_tr_bm_aug.csv",39)
        old=read_csv(oldz,"peroUS_AV_AG.csv",6351)
        ans=annual_capture(cap,summary,old)
        # Extract author code lines describing temporal and count definitions, not outcomes.
        hits={}
        for name in ("Data and code/1_DataOrg.R","Data and code/2_DataAnalysis.R"):
            s=z.read(name).decode("utf-8",errors="replace")
            selected=[]
            for line in s.splitlines():
                if re.search(r"\blag\s*\(|\blead\s*\(|\bn_distinct\s*\(|year\s*[+-]\s*1|\bnind\s*=|\bmonth\s*==|\btrap.?night|\bseeds83_20_year_sp_wide2",line,re.I):
                    selected.append(line.strip()[:240])
            hits[name]=selected[:40]
        ans["author_code_selected_time_and_count_lines"]=hits
    return ans

def main():
    import sys
    part=sys.argv[1] if len(sys.argv)>1 else "capture"
    req(part in {"plant","capture"},"UNKNOWN_PART")
    out={"schema":"neon.holt.annual_bridge_source.v1","part":part,"no_effect_fitted":True,"submission_hold":True}
    try:out["result"]=plant() if part=="plant" else capture()
    except Exception as e:out.update(status="SOURCE_STOP",error_class=type(e).__name__)
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    path=OUT.with_name(OUT.stem+"_"+part+".json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0
if __name__=="__main__":raise SystemExit(main())
