"""Frozen source feasibility for seasonal seed-rodent interactions; no effect fitting."""
from collections import Counter
from datetime import date, datetime, timezone
from hashlib import md5, sha256
from io import BytesIO, StringIO
from pathlib import Path
from zipfile import ZipFile
import csv
import json
import re

from analysis.audit_neon_direct_resource_groundcover_source_v1 import bounded, require

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_seasonal_seed_role_source_20261124.json"
RECEIPT=ROOT/"results/neon_direct_resource_groundcover_source_inventory_20261124.json"
DRI_SHA="0c4dcc8cebbc968c768e7d30fd8bb4cf66207bb026659c7c0dd0aa42c827f29a"
GU_SHA="9424cc40bab0ad1d498abb91c0a961ff6aa81a1a04946d1515a14b4d6baadfcb"
GU_MD5="d6fca6133f60fdd0971557f8ab4c9b7e"

def verified_file(article,version,fid,size,expected_md5,expected_sha):
    meta=json.loads(bounded(f"https://api.figshare.com/v2/articles/{article}/versions/{version}",2_000_000))
    require(meta.get("id")==article and meta.get("version")==version,"VERSION_ID_MISMATCH")
    found=[f for f in meta["files"] if f["id"]==fid]
    require(len(found)==1,"FILE_ID_MISMATCH")
    f=found[0]
    require(f["size"]==size and (f.get("computed_md5") or f.get("supplied_md5")).lower()==expected_md5,"FILE_METADATA_DRIFT")
    raw=bounded(f["download_url"],size)
    require(len(raw)==size and md5(raw).hexdigest()==expected_md5 and sha256(raw).hexdigest()==expected_sha,"ORIGINAL_BYTES_DRIFT")
    return raw

def year_field(name):
    return re.sub(r"[^a-z]","",name.lower()) in {"year","yr","captureyear","seedyear","collectionyear"}

def csv_schema(raw):
    rdr=csv.reader(StringIO(raw.decode("utf-8-sig"),newline=""))
    header=next(rdr)
    require(0<len(header)<=5000 and all(len(x)<=160 for x in header),"INVALID_HEADER")
    # Header strings are source variable names, not biological rows.
    counts=Counter()
    ys={i:Counter() for i,h in enumerate(header) if year_field(h)}
    missing=[0]*len(header)
    for row in rdr:
        counts[len(row)]+=1
        if len(row)!=len(header):
            continue
        for i,x in enumerate(row):
            if not x.strip() or x.strip().lower() in {"na","nan","null"}:
                missing[i]+=1
            if i in ys:
                v=x.strip()
                k=v if re.fullmatch(r"(19|20)\d{2}",v) else "missing_or_not_literal_four_digit_year"
                ys[i][k]+=1
    return {"header":header,"rows":sum(counts.values()),"width_histogram":dict(counts),
            "blank_or_na_counts_by_column_index":missing,
            "literal_year_counts_by_column_index":{str(i):dict(sorted(c.items())) for i,c in ys.items()}}

def dri():
    inv=json.loads(RECEIPT.read_text())["original_stdout_json"]["source_results"]["15029247"]["schema_receipts"][0]
    raw=verified_file(15029247,1,36110309,2277102,"5f5263ba55a2d72c886d170ec5d38c43",DRI_SHA)
    with ZipFile(BytesIO(raw)) as z:
        expected={x["name"]:x["uncompressed_bytes"] for x in inv["members"]}
        observed={x.filename:x.file_size for x in z.infolist()}
        require(len(z.infolist())==len(observed) and observed==expected,"ARCHIVE_MEMBER_DRIFT")
        out={}
        for name in sorted(observed):
            if name.lower().endswith(".csv"):
                out[name]=csv_schema(z.read(name))
        # README only: author documentation, no raw animal or seed rows.
        readme=z.read("Data_and_code/Read_me.txt").decode("utf-8-sig",errors="replace")
        # R source code ontology: collect references to input files and selected
        # chronology operators, not evaluated R or fitted outcomes.
        code={}
        for name in sorted(observed):
            if name.lower().endswith(".r"):
                s=z.read(name).decode("utf-8",errors="replace")
                refs=sorted(set(re.findall(r"""['"]([^'"]+\.csv)['"]""",s,flags=re.I)))
                code[name]={"literal_csv_references":refs,
                    "year_lag_line_count":sum(bool(re.search(r"\blag\s*\(|\blead\s*\(|year\s*[+-]\s*1",x,re.I)) for x in s.splitlines())}
        return {"status":"ARCHIVE_SCHEMA_GO_NO_PATCH_JOIN_YET","archive_sha256":DRI_SHA,
                "csv_schemas":out,"author_readme":readme,"author_code_input_inventory":code}

def date_value(x):
    if isinstance(x,datetime):
        return x.date()
    if isinstance(x,date):
        return x
    if isinstance(x,str):
        # Deliberately refuse ambiguous month/day and yearless dates.
        m=re.fullmatch(r"(19\d{2}|20\d{2})[-/](\d{1,2})[-/](\d{1,2})(?: 00:00:00)?",x.strip())
        if m:
            try:return date(*map(int,m.groups()))
            except ValueError:return None
    return None

def date_coverage(rows,i,j):
    counts=Counter();first=Counter();second=Counter();both=Counter()
    for row in rows:
        a,b=row[i],row[j]
        x,y=date_value(a),date_value(b)
        for v,d,months,label in ((a,x,first,"first"),(b,y,second,"second")):
            counts[label+"_blank" if v is None or v=="" else label+"_parseable" if d else label+"_unresolved"]+=1
            if d: months[d.strftime("%Y-%m")]+=1
        if x and y:
            counts["both_parseable"]+=1
            counts["chronological" if y>=x else "reversed"]+=1
            if y>=x:
                delta=(y-x).days
                both["same_day" if delta==0 else "1_7d" if delta<=7 else "8_30d" if delta<=30 else "31_90d" if delta<=90 else "over_90d"]+=1
    return {"date_status_counts":dict(counts),"first_month_row_counts":dict(sorted(first.items())),
            "second_month_row_counts":dict(sorted(second.items())),
            "nonnegative_interval_counts":dict(both)}

def gu():
    from openpyxl import load_workbook
    raw=verified_file(29815622,2,56869019,51056,GU_MD5,GU_SHA)
    book=load_workbook(BytesIO(raw),read_only=True,data_only=True)
    try:
        it=book["Dispersal"].values
        header=list(next(it))
        i=header.index("Date of first dispersal");j=header.index("Date of second dispersal")
        rows=list(it)
        require(len(rows)==738 and len({row[header.index("Code")] for row in rows})==735,"ARCHIVE_ROW_ONTOLOGY_DRIFT")
        g=date_coverage(rows,i,j)
        sv=book["Rodent survey"].values
        h=list(next(sv));k=h.index("Date");v=Counter();unresolved=0
        for row in sv:
            d=date_value(row[k])
            if d:v[d.strftime("%Y-%m")]+=1
            else:unresolved+=1
        return {"status":"ARCHIVE_EVENT_DATE_SUPPORT_ONLY","archive_sha256":GU_SHA,
                "seed_archive_rows":738,"distinct_seed_codes":735,"dispersal_header":header,
                "date_coverage":g,"rodent_survey_month_row_counts":dict(sorted(v.items())),
                "rodent_survey_unresolved_dates":unresolved,
                "seed_release_date_column_present":any("release" in str(h).lower() or "placement date" in str(h).lower() for h in header),
                "seed_final_fate_date_column_present":any("fate date" in str(h).lower() for h in header),
                "seed_actor_individual_PIT_column_present":any("pit" in str(h).lower() for h in header),
                "no_seasonal_fate_effect_fitted":True}
    finally:book.close()

def main():
    out={"schema":"neon.seasonal_seed_role.source_feasibility.v1",
         "retrieved_utc":datetime.now(timezone.utc).isoformat(),
         "no_biological_response_effect_fitted":True,"submission_hold":True}
    for label,fn in (("Dri_primary_resource_space",dri),("Gu_seed_event_chronology",gu)):
        try:out[label]=fn()
        except Exception as exc:out[label]={"status":"SOURCE_STOP","error_class":type(exc).__name__}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":raise SystemExit(main())
