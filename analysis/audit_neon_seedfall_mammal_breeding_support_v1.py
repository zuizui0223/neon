"""Direct NEON seed deposition × mammal breeding source support.

Both products fixed to RELEASE-2026; no resource/response associations
computed. Source audit counts calendar/record support, not edible seeds.
No private identifiers, exact capture dates, tag histories, seed masses,
or pregnancy outcomes exported by site/year.
"""
from collections import Counter, defaultdict
from datetime import date,datetime,timezone
from hashlib import sha256
from pathlib import Path
import csv,io,json,os,re
from analysis.run_multiscale_density_estimability_release2026_v3 import (
    RELEASE,QUERY_URL,TOKEN_ENV,_request_json,_site_codes,_download_many,
)
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_seedfall_mammal_breeding_support_20261125.json"
LITTER="DP1.10033.001"
MAMMAL="DP1.10072.001"
START="2017-01"
END="2025-12"
LITTER_TABLES=("ltr_pertrap","ltr_fielddata","ltr_massdata")
MAMMAL_TABLES=("mam_perplotnight","mam_pertrapnight")
MISSING={"","NA","N/A","NULL","NONE","NAN"}
MONTHS={3,4,5,9,10,11}
LIMIT=500_000_000

def req(x,code):
    if not x:raise ValueError(code)
def t(x):return str(x or "").strip()
def known(x):return t(x).upper() not in MISSING
def d(x):
    try:return date.fromisoformat(t(x)[:10])
    except (TypeError,ValueError):return None
def rows(raw):
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    h=reader.fieldnames or []
    req(h and len(h)==len(set(h)),"CSV_HEADER_INVALID")
    return tuple(h),reader
def inventory(product,sites,tables,token):
    payload=_request_json(QUERY_URL,token=token,body={
        "productCode":product,"siteCodes":sites,"startDateMonth":START,
        "endDateMonth":END,"release":RELEASE,"package":"basic","includeProvisional":False})
    releases=[x for x in payload["data"].get("releases",[]) if x.get("release")==RELEASE]
    req(len(releases)==1,"RELEASE_BLOCK_MISSING")
    found={}
    for p in releases[0].get("packages",[]):
        if p.get("packageType")!="basic":continue
        site,month=t(p.get("siteCode")),t(p.get("month"))
        req(site in sites and re.fullmatch(r"\d{4}-\d{2}",month),"PACKAGE_KEY_INVALID")
        for f in p.get("files",[]):
            name=t(f.get("name"))
            matches=[table for table in tables if table in name.lower() and name.lower().endswith(".csv")]
            if not matches:continue
            req(len(matches)==1,"TABLE_NAME_AMBIGUOUS")
            size=f.get("size");digest=t(f.get("md5")).lower();url=t(f.get("url"))
            req(type(size) is int and size>=0 and re.fullmatch(r"[a-f0-9]{32}",digest) and url.startswith("https://"),"INVENTORY_FILE_METADATA_INVALID")
            obj={"site":site,"month":month,"name":name,"table":matches[0],"size":size,"md5":digest,"url":url}
            k=(site,month,name)
            req(k not in found or found[k]==obj,"CONFLICTING_FILE_METADATA")
            found[k]=obj
    return [found[k] for k in sorted(found)]
def batch(items,token):
    for j in range(0,len(items),36):
        part=items[j:j+36]
        for m,b in zip(part,_download_many(part,token,max_workers=6)):
            yield m,b
def manifest_info(items):
    return {"files":len(items),"bytes":sum(x["size"] for x in items),
        "files_by_table":dict(Counter(x["table"] for x in items)),
        "site_count":len({x["site"] for x in items}),
        "site_months":len({(x["site"],x["month"]) for x in items}),
        "md5_manifest_sha256":sha256(json.dumps([(x["site"],x["month"],x["name"],x["size"],x["md5"]) for x in items],separators=(",",":")).encode()).hexdigest()}
def schema_counts(seen):
    return {k:[{"header":list(h),"files":n} for h,n in v.items()] for k,v in seen.items()}
def add_header(seen,table,h):
    seen[table][h]+=1
def phase(day):
    if day.month in (3,4,5):return "spring"
    if day.month in (9,10,11):return "autumn"
    return None
def possible_alignment(litter,breeding):
    """Calendar support only; never read resource mass or response status."""
    full=[]
    for s,y in sorted({(s,y) for s,y,g,ph in breeding}):
        # Three complete autumn months cannot be inferred from date
        # presence alone. This is a necessary, not sufficient, condition.
        previous=litter.get((s,y-1),set());current=litter.get((s,y),set())
        if not previous or not current:continue
        gset={g for ss,yy,g,ph in breeding if (ss,yy)==(s,y)}
        for g in gset:
            a=len(breeding.get((s,y,g,"spring"),set()))
            b=len(breeding.get((s,y,g,"autumn"),set()))
            if min(a,b)>=10:
                full.append((s,y,g,len(previous),len(current)))
    sy={(s,y) for s,y,g,p,c in full}
    bysite=Counter(s for s,y in sy)
    return {"candidate_site_year_taxon_cells":len(full),"candidate_site_years":len(sy),
        "candidate_sites":len(bysite),"site_year_support_histogram":dict(Counter(bysite.values())),
        "sites_with_at_least_four_candidate_years":sum(n>=4 for n in bysite.values()),
        "candidate_cells_with_at_least_two_collection_dates_each_autumn":sum(p>=2 and c>=2 for s,y,g,p,c in full),
        "necessary_only_no_complete_litter_interval_or_same_plot_claim":True}

def audit(lfiles,mfiles,token):
    headers=defaultdict(Counter);lrow=Counter();lbad=Counter();mrow=Counter();mbad=Counter()
    groups=Counter();traptypes=Counter();conditions=Counter();qa=Counter()
    field_index=defaultdict(set);mass_index=defaultdict(set);trap_index=defaultdict(set)
    seed_explicit=set();field_dates=defaultdict(set)
    # Count candidate field/mass/trap linkage, retaining ambiguous keys.
    # Never sum mass, infer a missing functional group means zero, or
    # assume collection dates represent start dates.
    for meta,raw in batch(lfiles,token):
        h,reader=rows(raw);tab=meta["table"];site=meta["site"];add_header(headers,tab,h)
        for x in reader:
            lrow[tab]+=1
            if known(x.get("siteID")) and t(x["siteID"])!=site:
                lbad["site_mismatch"]+=1;continue
            if tab=="ltr_pertrap":
                trap=t(x.get("trapID"))
                typ=t(x.get("trapType"))
                if trap and typ:trap_index[site,trap].add(typ);traptypes[typ]+=1
                else:lbad["trap_identity_or_type_missing"]+=1
            elif tab=="ltr_fielddata":
                trap=t(x.get("trapID"));key=t(x.get("fieldSampleID"));day=d(x.get("collectDate"))
                condition=t(x.get("trapCondition"));conditions[condition]+=1
                if trap and day:
                    if key:field_index[site,key].add((trap,day,condition))
                    if phase(day)=="autumn":field_dates[site,day.year].add(day)
                else:lbad["field_trap_or_calendar_missing"]+=1
            elif tab=="ltr_massdata":
                key=t(x.get("fieldSampleID"));fg=t(x.get("functionalGroup"));m=t(x.get("massSampleID"));qa0=t(x.get("qaDryMass"))
                groups[fg]+=1;qa[qa0]+=1
                if not key or not fg or not m:lbad["mass_key_or_group_missing"]+=1;continue
                mass_index[site,key].add((fg,m,qa0))
                if fg.lower() in {"seed","seeds"}:seed_explicit.add((site,key))
    fkeys=set(field_index);mkeys=set(mass_index)
    unique_seed_keys={k for k in seed_explicit if len(field_index.get(k,set()))==1}
    elevated_candidate=0;seed_ambiguous_group=0
    for k in unique_seed_keys:
        trap,day,cond=next(iter(field_index[k]))
        ty=trap_index.get((k[0],trap),set())
        if len(ty)==1 and "elevated" in next(iter(ty)).lower():elevated_candidate+=1
        massid={v[1] for v in mass_index[k] if v[0].lower() in {"seed","seeds"}}
        if len(massid)!=1:seed_ambiguous_group+=1
    ldiag={"rows_by_table":dict(lrow),"literal_functional_group_counts":dict(groups),"literal_trap_type_counts":dict(traptypes),
        "literal_trap_condition_counts":dict(conditions),"literal_qaDryMass_counts":dict(qa),"field_sample_keys":len(fkeys),
        "mass_sample_parent_keys":len(mkeys),"mass_keys_without_field_parent":len(mkeys-fkeys),
        "field_keys_with_multiple_distinct_records":sum(len(v)>1 for v in field_index.values()),
        "explicit_seed_group_field_keys":len(seed_explicit),"explicit_seed_keys_unique_field_join":len(unique_seed_keys),
        "explicit_seed_keys_unique_elevated_trap_candidate":elevated_candidate,
        "explicit_seed_keys_multiple_mass_ids":seed_ambiguous_group,
        "candidate_site_autumn_years_any_field_dates":len(field_dates),"issues":dict(lbad),
        "no_mass_values_opened":True}
    # Mammal: count support of capture records with explicit recorded sex,
    # life stage, tag and nonblank pregnancy field. No pregnancy value
    # is used as a positive or negative endpoint here.
    breeding=defaultdict(set);capture_days=defaultdict(set);sex=Counter();age=Counter();preg_labels=Counter()
    event_keys=set()
    for meta,raw in batch(mfiles,token):
        h,reader=rows(raw);tab=meta["table"];site=meta["site"];add_header(headers,tab,h)
        if tab=="mam_perplotnight":
            for x in reader:
                mrow[tab]+=1
                n=t(x.get("nightuid") or x.get("nightUID"));p=t(x.get("plotID"));e=t(x.get("eventID"));day=d(x.get("collectDate"))
                if n and p and e and day:event_keys.add((site,n,p))
                else:mbad["plot_event_identity_missing"]+=1
            continue
        for x in reader:
            mrow[tab]+=1
            if known(x.get("siteID")) and t(x["siteID"])!=site:
                mbad["site_mismatch"]+=1;continue
            n=t(x.get("nightuid") or x.get("nightUID"));p=t(x.get("plotID"))
            day=d(x.get("collectDate"))
            if not n or not p or not day:
                mbad["capture_key_or_date_missing"]+=1;continue
            stat=t(x.get("trapStatus")).lower()
            if "capture" not in stat or "no capture" in stat:continue
            mrow["literal_capture_status"]+=1
            a=t(x.get("lifeStage"));sx=t(x.get("sex"));pr=t(x.get("pregnancyStatus"))
            sex[sx]+=1;age[a]+=1
            # Pregnancy labels exported globally only, not by exposure.
            if sx.lower() in {"female","f"} and a.lower() in {"adult","a"}:
                preg_labels[pr]+=1
                ph=phase(day)
                tag=t(x.get("tagID"));tax=t(x.get("taxonID"))
                if ph and known(tag) and known(tax) and known(pr):
                    breeding[site,day.year,tax,ph].add(tag)
                    capture_days[site,day.year,tax,ph].add(day)
    mdiag={"rows_by_table_or_capture_status":dict(mrow),"plot_event_night_keys":len(event_keys),
        "literal_capture_sex_counts":dict(sex),"literal_capture_life_stage_counts":dict(age),
        "adult_female_global_pregnancy_label_counts":dict(preg_labels),
        "adult_female_tagged_known_pregnancy_field_site_year_taxon_phase_cells":len(breeding),
        "cells_with_at_least_ten_unique_literal_tags":sum(len(v)>=10 for v in breeding.values()),
        "issues":dict(mbad),"no_endpoint_mapping_no_demographic_effect":True}
    return {"litter_source":ldiag,"mammal_source":mdiag,"headers":schema_counts(headers),
       "necessary_calendar_support":possible_alignment(field_dates,breeding),
       "complete_resource_intervals_verified":False,"individual_identity_history_verified":False,"ecological_effect":None}
def run():
    token=os.environ.get(TOKEN_ENV,"").strip()
    req(token,"NEON_TOKEN_UNAVAILABLE")
    req(RELEASE=="RELEASE-2026","RELEASE_DRIFT")
    def sites(product):
        return set(_site_codes(_request_json("https://data.neonscience.org/api/v0/products/"+product+"?release="+RELEASE)))
    a,b=sites(LITTER),sites(MAMMAL)
    common=sorted(a&b);req(common,"NO_COMMON_PRODUCT_SITE")
    lf=inventory(LITTER,common,LITTER_TABLES,token)
    mf0=inventory(MAMMAL,common,MAMMAL_TABLES,token)
    # Use all litter months, only spring/autumn mammal package months
    # plus adjacent boundary months to avoid a collection crossing a
    # package boundary. Actual collectDate determines season later.
    mf=[v for v in mf0 if int(v["month"][-2:]) in {2,3,4,5,6,8,9,10,11,12}]
    mf.sort(key=lambda v:(v["table"]!="mam_perplotnight",v["site"],v["month"],v["name"]))
    out={"release":RELEASE,"window":[START,END],"litter_product_site_count":len(a),
        "mammal_product_site_count":len(b),"common_product_site_count":len(common),
        "litter_manifest":manifest_info(lf),"mammal_manifest_all":manifest_info(mf0),
        "mammal_manifest_selected":manifest_info(mf)}
    if not lf or not mf or sum(x["size"] for x in lf+mf)>LIMIT:
        return {**out,"status":"STOP_SOURCE_FILE_BUDGET_OR_EMPTY","ecological_effect":None}
    out.update(audit(lf,mf,token));out["status"]="SOURCE_SUPPORT_ONLY_NO_EFFECT"
    return out
def main():
    out={"schema":"neon.seedfall.mammal.breeding.support.v1","submission_hold":True,
        "poland_holt_yang_closed":True,"no_new_ecological_effect":True}
    try:out.update(run())
    except Exception as e:out.update(status="STOP_SOURCE_OR_SCHEMA",ecological_effect=None,error_class=type(e).__name__,
        reason=str(e) if type(e) is ValueError and re.fullmatch("[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR")
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
