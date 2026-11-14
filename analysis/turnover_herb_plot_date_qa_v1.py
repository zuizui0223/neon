#!/usr/bin/env python3
"""Turnover source support: NEON RELEASE-2026 shared months, actual plot/date joins.
Credential never leaves the existing repository runner. No raw records or signed
URLs exported. No biomass–diversity effect, trait value or model is computed.
"""
from __future__ import annotations
import argparse,csv,io,os,json,hashlib,math,time
import urllib.request,urllib.error
from urllib.parse import urlsplit
from pathlib import Path
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import date,timedelta
RELEASE='RELEASE-2026';BASE='https://data.neonscience.org/api/v0'
PRODS=('DP1.10023.001','DP1.10058.001')
TABLES=('hbp_perbout','hbp_massdata','div_1m2data')
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        raise urllib.error.HTTPError(req.full_url,code,'credential redirect blocked',headers,fp)
def number(v):
    try:n=float(v)
    except (TypeError,ValueError):return None
    return n if math.isfinite(n) and n>=0 else None
def day(v):
    try:return date.fromisoformat(str(v or '')[:10])
    except ValueError:return None
def nearest(d,candidates,max_days=30):
    gaps=sorted((abs((x-d).days),x) for x in set(candidates))
    if not gaps or gaps[0][0]>max_days:return None
    if len(gaps)>1 and gaps[0][0]==gaps[1][0]:return None
    return gaps[0][1],gaps[0][0]
def api(path,token=None,body=None):
    headers={'Accept':'application/json','User-Agent':'turnover-herb-plot-date-qa/1.0'}
    if token:headers['X-API-TOKEN']=token
    if body is not None:headers['Content-Type']='application/json'
    request=urllib.request.Request(BASE+path,headers=headers,data=json.dumps(body).encode() if body is not None else None)
    with urllib.request.build_opener(NoRedirect).open(request,timeout=100) as r:raw=r.read(80000001)
    if len(raw)>80000000:raise ValueError('Metadata size limit')
    return json.loads(raw)['data'],hashlib.sha256(raw).hexdigest()
def source_files(token):
    months={};digests={}
    for prod in PRODS:
        obj,digest=api('/products/'+prod+'?release='+RELEASE)
        months[prod]={}
        for s in obj['siteCodes']:
            rel=[x for x in s.get('availableReleases',[]) if x.get('release')==RELEASE]
            if len(rel)==1:months[prod][s['siteCode']]=set(rel[0]['availableMonths'])
        digests[prod]={'product_json_sha256':digest}
    shared={s:months[PRODS[0]][s]&months[PRODS[1]][s] for s in set(months[PRODS[0]])&set(months[PRODS[1]])}
    shared={s:m for s,m in shared.items() if m};allowed={(s,m) for s,v in shared.items() for m in v}
    if len(shared)!=47 or len(allowed)!=424:raise ValueError('Frozen 47-site 424-month population changed')
    cells=defaultdict(dict);domains={}
    for prod in PRODS:
        obj,digest=api('/data/query',token,{'productCode':prod,'siteCodes':sorted(shared),
            'startDateMonth':min(m for _,m in allowed),'endDateMonth':max(m for _,m in allowed),
            'release':RELEASE,'package':'basic','includeProvisional':False})
        digests[prod]['query_json_sha256']=digest
        rel=[x for x in obj.get('releases',[]) if x.get('release')==RELEASE]
        if len(rel)!=1:raise ValueError('Pinned release absent')
        for p in rel[0].get('packages',[]):
            key=(p['siteCode'],p['month'])
            if p.get('packageType')!='basic' or key not in allowed:continue
            domains[key[0]]=p['domainCode']
            for f in p.get('files',[]):
                n=f['name'].lower()
                for t in TABLES:
                    if t in n and '.basic.' in n and n.endswith('.csv'):
                        if t in cells[key] and cells[key][t]['name']!=f['name']:raise ValueError('Ambiguous basic table')
                        cells[key][t]=f
    complete={k:v for k,v in cells.items() if set(TABLES)<=set(v)}
    if len(complete)!=397:raise ValueError('Frozen all-table month count changed')
    jobs=[(site,month,t,f) for (site,month),files in sorted(complete.items()) for t,f in files.items()]
    return jobs,domains,digests

def fetch_csv(job):
    site,month,table,f=job;url=f['url'];host=urlsplit(url).hostname or ''
    if urlsplit(url).scheme!='https' or not (host=='storage.googleapis.com' or host.endswith('.storage.googleapis.com')):
        raise ValueError('Unapproved storage host; no token forwarded')
    for attempt in range(2):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'turnover-herb-source-record-qa/1.0'})
            with urllib.request.urlopen(req,timeout=70) as r:raw=r.read(25000001)
            break
        except (TimeoutError,urllib.error.URLError):
            if attempt:raise
            time.sleep(1)
    if len(raw)>25000000:raise ValueError('CSV size limit')
    if f.get('md5') and hashlib.md5(raw).hexdigest()!=f['md5'].lower():raise ValueError('NEON MD5 changed')
    reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')));rows=list(reader)
    required={'plotID','collectDate','sampleID','clipArea'} if table=='hbp_perbout' else {'sampleID','dryMass','herbGroup','plotID'} if table=='hbp_massdata' else {'plotID','endDate','taxonID','taxonRank','percentCover','otherVariables'}
    if not required<=set(reader.fieldnames or []):raise ValueError('Required source fields absent: '+table)
    return site,month,table,rows,{'name':f['name'],'sha256':hashlib.sha256(raw).hexdigest(),'row_count':len(rows),'table':table}

def main():
    token=os.environ.get('NEON_API_TOKEN')
    if not token:raise ValueError('Existing NEON credential absent')
    jobs,domains,queries=source_files(token)
    bouts={};bout_conflicts=set();mass=defaultdict(set);bad_mass=set();cover=defaultdict(set)
    counts=Counter();flags=defaultdict(Counter);manifests=[];failures=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(fetch_csv,j):j for j in jobs}
        for future in as_completed(futures):
            job=futures[future]
            try:site,month,table,rows,manifest=future.result()
            except Exception as e:
                failures.append({'site':job[0],'month':job[1],'table':job[2],'error_class':type(e).__name__});continue
            manifests.append(manifest);counts[table+'_rows']+=len(rows)
            for r in rows:
                if r.get('siteID') and r['siteID']!=site:raise ValueError('Source row site identity mismatch')
                for field in ('samplingImpractical','dataQF','sampleCondition','exclosure','plotManagement'):
                    if field in r:flags[table+'.'+field][str(r.get(field) or '(blank)')]+=1
                if table=='hbp_perbout':
                    sid=str(r.get('sampleID') or '').strip();plot=str(r.get('plotID') or '').strip()
                    dt=day(r.get('collectDate'));area=number(r.get('clipArea'))
                    if not sid or not plot or dt is None or area is None or area<=0:
                        counts['bout_missing_id_date_or_positive_area']+=1;continue
                    state=(site,plot,dt,area)
                    if sid in bouts and bouts[sid]!=state:bout_conflicts.add(sid)
                    else:bouts[sid]=state
                elif table=='hbp_massdata':
                    sid=str(r.get('sampleID') or '').strip();group=str(r.get('herbGroup') or '').strip();v=number(r.get('dryMass'))
                    if not sid:counts['mass_missing_sample_id']+=1;continue
                    if v is None or not group:bad_mass.add(sid);counts['mass_missing_or_invalid_dry_mass_or_group']+=1;continue
                    mass[(sid,group)].add(v)
                else:
                    plot=str(r.get('plotID') or '').strip();dt=day(r.get('endDate'));tax=str(r.get('taxonID') or '').strip()
                    v=number(r.get('percentCover'));rank=str(r.get('taxonRank') or '').strip().casefold()
                    if r.get('otherVariables') or not tax or rank!='species':counts['cover_non_species_or_ground_cover_rows']+=1;continue
                    if not plot or dt is None or v is None or v<=0 or v>100:counts['cover_missing_or_invalid_positive_cover']+=1;continue
                    cover[(site,plot,dt)].add(tax)
            if len(manifests)%150==0:print('SOURCE_FILES_VERIFIED',len(manifests),flush=True)
    mass_conflicts={sid for (sid,g),v in mass.items() if len(v)!=1}
    mass_valid={sid for (sid,g),v in mass.items() if len(v)==1}-bad_mass-mass_conflicts
    dates=defaultdict(set)
    for site,plot,dt in cover:dates[(site,plot)].add(dt)
    events={};matched_samples=0;gaps=Counter();source_samples=0
    for sid,(site,plot,dt,area) in bouts.items():
        if sid in bout_conflicts or sid not in mass_valid:continue
        source_samples+=1
        match=nearest(dt,dates.get((site,plot),set()))
        if match is None:continue
        cvdate,gap=match;matched_samples+=1;gaps[gap]+=1
        key=(site,plot,dt)
        events[key]={'cover_date':cvdate,'species_count':len(cover[(site,plot,cvdate)])}
    site_summary={}
    for site in sorted(domains):
        es=[(k,v) for k,v in events.items() if k[0]==site]
        site_summary[site]={'domain':domains[site],'matched_plot_harvest_dates':len(es),
            'unique_matched_plots':len({k[1] for k,v in es}),
            'events_with_at_least_three_species':sum(v['species_count']>=3 for k,v in es)}
    sites={s for s,v in site_summary.items() if v['matched_plot_harvest_dates']}
    five={s for s,v in site_summary.items() if v['unique_matched_plots']>=5}
    good_domains={domains[s] for s in sites};five_domains={domains[s] for s in five}
    ok=len(sites)>=12 and len(good_domains)>=4 and len(events)>=100 and not failures
    return {'status':'NEON_STRUCTURAL_PLOT_DATE_AUDIT_COMPLETE','release':RELEASE,
      'credential_source':'Existing zuizui0223/neon secret, not copied/exported',
      'catalog_sites':47,'catalog_site_months':424,'all_table_site_months':397,
      'source_files_expected':len(jobs),'source_files_verified':len(manifests),'source_file_failures':failures,
      'row_counts':dict(counts),'sample_ids_with_valid_date_area_and_mass':source_samples,
      'matched_strip_samples':matched_samples,'matched_plot_harvest_dates':len(events),
      'matched_sites':len(sites),'matched_domains':len(good_domains),
      'sites_with_at_least_five_distinct_matched_plots':len(five),'domains_in_five_plot_sites':len(five_domains),
      'events_in_five_plot_sites':sum(v['matched_plot_harvest_dates'] for s,v in site_summary.items() if s in five),
      'structural_12_site_4_domain_100_event_thresholds_met':ok,
      'harvest_to_cover_day_gap_histogram':dict(sorted(gaps.items())),
      'ambiguous_bout_sample_ids':len(bout_conflicts),'conflicting_mass_sample_ids':len(mass_conflicts),
      'source_quality_flag_distributions':{k:dict(v) for k,v in flags.items()},
      'site_summary':site_summary,'source_file_manifest':sorted(manifests,key=lambda x:x['name']),'queries':queries,
      'raw_records_exported':False,'token_or_signed_urls_exported':False,'ecological_effects_estimated':False,
      'eligible_for_ecological_analysis':False,
      'remaining':['Interpret source QA flags/exclosures and management codes.','Verify dryMass and clipArea units from source metadata.','Confirm trait definitions, source provenance and trait coverage.','Distinct cover quadrats and harvest strips: co-location is only at plot level.'],
      'matching_rule':'same plotID, exact release, unique nearest species-cover endDate within 30 calendar days of collectDate; ties excluded; clips collapsed to plot-harvest-date'}

def tests():
    d=date(2020,5,1)
    assert nearest(d,{d+timedelta(days=30)})==(d+timedelta(days=30),30)
    assert nearest(d,{d+timedelta(days=31)}) is None
    assert nearest(d,{d-timedelta(days=2),d+timedelta(days=2)}) is None
    assert nearest(d,{d,d+timedelta(days=5)})==(d,0)
    assert number('-9999') is None and number('0')==0 and number('NaN') is None
    return {'status':'SOURCE_JOIN_FIXTURES_PASS','tests':5}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out');p.add_argument('--self-test',action='store_true');a=p.parse_args()
    if a.self_test:print(json.dumps(tests()))
    else:
        if not a.out:p.error('--out required')
        result=main();out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print('NEON_PLOT_DATE_RESULT',json.dumps({k:v for k,v in result.items() if k!='source_file_manifest'},sort_keys=True))
