"""V13b: source-semantic correction of V13; original V13 zero retained.
 repeatability of seasonal captured small-mammal composition.
NEON RELEASE-2026, previously pinned 32-site common-product roster.
Observed taxon composition, not abundance, seed handling, or function.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from statistics import mean,median
from pathlib import Path
from hashlib import sha256
import argparse,json,os,re,math
from analysis.audit_neon_seedfall_mammal_breeding_support_v1 import ROOT,TOKEN_ENV,batch,rows,d,t,known,req
from analysis.audit_neon_seedfall_mammal_breeding_sharded_v2 import source,expected,manifest_pin_digest,merge_numeric
from analysis.audit_neon_crossseason_genus_support_v1 import _events,_normal_coord,_normal_tag
from analysis.audit_multiscale_density_mnka_variation_v1 import _taxonomy
from analysis.run_neon_matched_species_pregnancy_season_v1 import NO_REPLACE,phase
from analysis.neon_macro_6night_operable_trap_status_v1 import published_trap_status
BUILD=ROOT/'build'
SCHEMA='neon.capture.composition.season.v13b'
PHASES=('early','late')
TRAIN=range(2017,2022)
TEST=range(2022,2026)
# Source eligibility does not depend on the sign of taxonomic change.
MIN_TAGS=20
MIN_COMMON=90
MIN_TRAIN=2
MIN_TEST=1

def sample(files,token,genus):
    pp=[];eff=defaultdict(set); status_by_station={}; obs=defaultdict(list); ident=defaultdict(set); replaced=defaultdict(set); issues=Counter()
    for meta,raw in batch(files,token):
        _,it=rows(raw);s=meta['site']
        for x in it:
            req(t(x.get('siteID'))==s,'SITE_MISMATCH')
            day=d(x.get('collectDate'));pl=t(x.get('plotID'));night=t(x.get('nightuid'))
            if not day or not pl or not night:
                issues['invalid_context']+=1;continue
            if day.year not in range(2017,2026):continue
            if meta['table']=='mam_perplotnight':
                if phase(day):pp.append({'_site':s,'siteID':s,'plotID':pl,'nightuid':night,'eventID':t(x.get('eventID')),'collectDate':day.isoformat(),'gridCompletion':t(x.get('gridCompletion'))})
                continue
            k=(s,pl,night);coord=_normal_coord(x.get('trapCoordinate'));status=t(x.get('trapStatus')).lower()
            code,ok=published_trap_status(x.get('trapStatus'))
            if phase(day) and coord:
                issues['trap_status_'+code]+=1
                z=(k,coord)
                status_by_station[z]=status_by_station.get(z,True) and ok
            if code not in ('4','5') or not ok:continue
            tag=_normal_tag(x.get('tagID')); tax=t(x.get('taxonID'));g=genus.get(tax)
            if tag and g:ident[s,day.year,tag].add(g)
            rp=t(x.get('replacedTag'))
            if tag and rp.upper() not in NO_REPLACE:
                replaced[s,day.year].add(tag)
                if _normal_tag(rp):replaced[s,day.year].add(rp)
            if not phase(day):continue
            if not coord:issues['noncanonical_capture']+=1;continue
            obs[k].append((day,coord,tag,g,tax))
    for (k,coord),ok in status_by_station.items():
        if ok:eff[k].add(coord)
    _,reject,approved=_events(pp)
    issues['approved_events_before_effort']=len(approved)
    issues.update({'event_'+k:v for k,v in reject.items()})
    cand=defaultdict(list)
    for (s,pl,e),v in approved.items():
        ph={phase(x) for x in v['dates']}
        if len(ph)!=1 or None in ph:continue
        if not all(len(eff[s,pl,n])>=MIN_COMMON for n in v['nights']):
            issues['events_below_nightly_effort']+=1;continue
        cand[s,v['first'].year,pl,next(iter(ph))].append(v)
    chosen={k:min(v,key=lambda x:(x['first'],x['event'])) for k,v in cand.items()}
    issues['selected_bouts']=len(chosen)
    grouped=defaultdict(lambda:defaultdict(set))
    for s,y,pl,p in chosen:grouped[s,y][p].add(pl)
    # Same plot and >=90 shared explicitly capture/no-capture stations on all six nights.
    # Per site-year use all paired plots, unique tags across these plots, separately by phase.
    out=defaultdict(list)
    for (s,y),ph in sorted(grouped.items()):
        common=sorted(ph['early']&ph['late'])
        issues['paired_plots_before_six_night_effort']+=len(common)
        tags={p:defaultdict(set) for p in PHASES}; invalid=Counter(); captures=Counter(); paired=0
        for pl in common:
            ev={p:chosen[s,y,pl,p] for p in PHASES}
            sets=[eff[s,pl,n] for p in PHASES for n in ev[p]['nights']]
            coords=set.intersection(*sets)
            issues['common_status456_stations_hist_'+str(len(coords))]+=1
            if len(coords)<MIN_COMMON:
                issues['paired_plots_below_common90']+=1;continue
            paired+=1
            issues['paired_plots_common90']+=1
            for p in PHASES:
                for n in ev[p]['nights']:
                    for day,co,tag,g,tax in obs[s,pl,n]:
                        if day not in ev[p]['dates'] or co not in coords:continue
                        captures[p]+=1
                        if not tag or not g or len(ident[s,y,tag])!=1 or tag in replaced[s,y]:
                            invalid[p]+=1;continue
                        tags[p][tag].add(g)
        if not paired:continue
        issues['paired_site_years_effort']+=1
        c={p:Counter() for p in PHASES}
        for p in PHASES:
            for tag,gs in tags[p].items():
                if len(gs)==1:c[p][next(iter(gs))]+=1
                else:invalid[p]+=1
        if any(sum(c[p].values())<MIN_TAGS for p in PHASES):
            issues['site_year_low_tag_support']+=1;continue
        if any(invalid[p]>0.1*captures[p] for p in PHASES):
            issues['site_year_invalid_capture_over_10pct']+=1;continue
        # Count bounds for focal genera allow every invalid capture record to
        # represent another individual of either genus (overconservative).
        focal={}
        for p in PHASES:
            a,b=c[p]['Peromyscus'],c[p]['Myodes']+c[p]['Clethrionomys']
            focal[p]={'PM':a,'MG_group':b,'unresolved_records':invalid[p]}
        out[s].append({'year':y,'paired_plots':paired,'counts':{p:dict(c[p]) for p in PHASES},
                       'unresolved_records':dict(invalid),'capture_rows':dict(captures),'focal':focal})
    return out,dict(issues)

def prob(c):
    n=sum(c.values());return {g:v/n for g,v in c.items()}
def distance(a,b):
    return 0.5*sum(abs(a.get(g,0)-b.get(g,0)) for g in set(a)|set(b))
def predict(a,delta):
    # Fixed clipping and normalization, no fit to test.
    raw={g:max(0.,a.get(g,0)+delta.get(g,0)) for g in set(a)|set(delta)}
    total=sum(raw.values());return {g:v/total for g,v in raw.items()} if total else dict(a)
def site_result(rr):
    train=[r for r in rr if r['year'] in TRAIN]
    test=[r for r in rr if r['year'] in TEST]
    if len(train)<MIN_TRAIN or len(test)<MIN_TEST:return None
    ds=[]
    for r in train:
        a,b=[prob(r['counts'][p]) for p in PHASES]
        ds.append({g:b.get(g,0)-a.get(g,0) for g in set(a)|set(b)})
    delta={g:mean(x.get(g,0) for x in ds) for g in set().union(*ds)}
    out=[]
    for r in test:
        a,b=[prob(r['counts'][p]) for p in PHASES]
        base=distance(a,b);model=distance(predict(a,delta),b)
        out.append((base,model,base-model))
    return {'train_years':len(train),'test_years':len(test),'baseline_TV':mean(x[0] for x in out),'forecast_TV':mean(x[1] for x in out),'gain':mean(x[2] for x in out)}
def focal_result(rr):
    # Same genera directly implicated in Merz, but do not equate all congener
    # species' seed behavior. Exact focal group names, no outcome-based selection.
    train=[];test=[]
    for r in rr:
        v=[]
        for p in PHASES:
            z=r['focal'][p];a,b,u=z['PM'],z['MG_group'],z['unresolved_records']
            if a+b<10:break
            v.append((b/(a+b),b/(a+b+u),(b+u)/(a+b+u)))
        if len(v)!=2:continue
        z=(v[1][0]-v[0][0],v[1][1]-v[0][2],v[1][2]-v[0][1])
        (train if r['year'] in TRAIN else test).append(z)
    if len(train)<MIN_TRAIN or len(test)<MIN_TEST:return None
    pred=mean(x[0] for x in train)
    return {'train_years':len(train),'test_years':len(test),'train_delta':pred,
      'test_delta':mean(x[0] for x in test),'test_bounds':[mean(x[1] for x in test),mean(x[2] for x in test)],
      'mse_gain':mean(x[0]**2-(x[0]-pred)**2 for x in test)}
def shard(index):
    token=os.environ.get(TOKEN_ENV,'').strip();req(token,'NEON_TOKEN_UNAVAILABLE')
    parts,_,mf,pin=source(token);sites=parts[index]
    # Retain all pinned mammal months for within-site-year identity checks,
    # exactly the same original manifest as prior work.
    files=[x for x in mf if x['site'] in sites]
    _,genus,_=_taxonomy()
    obs,issues=sample(files,token,genus)
    return {'status':'SHARD_COMPLETE','index':index,'site_count':len(sites),'manifest_pin':manifest_pin_digest(pin),
      'partition_sha256':sha256(json.dumps(sorted(sites)).encode()).hexdigest(),'verified_files':len(files),
      'issues':issues,'site_results':[{'eligible_years':len(obs[s]),'main':site_result(obs[s]),'focal':focal_result(obs[s])} for s in sorted(sites)]}
def combine(directory):
    a=[json.loads(f.read_text()) for f in sorted(directory.rglob('neon_composition_v13b_shard_*.json'))]
    req(len(a)==4 and {x.get('index') for x in a}==set(range(4)),'INCOMPLETE_SHARDS')
    req(all(x.get('schema')==SCHEMA and x.get('status')=='SHARD_COMPLETE' and x.get('manifest_pin')==manifest_pin_digest(expected()) and x.get('site_count')==8 and len(x.get('site_results',[]))==8 for x in a),'SHARD_STOP_OR_PIN_DRIFT')
    req(len({x['partition_sha256'] for x in a})==4 and sum(x['verified_files'] for x in a)==1760,'SOURCE_ROSTER_DRIFT')
    rr=[r for x in a for r in x['site_results']]
    main=[r['main'] for r in rr if r['main'] is not None]
    focal=[r['focal'] for r in rr if r['focal'] is not None]
    out={'status':'STOP_NO_ELIGIBLE_SITE_YEAR' if not any(r['eligible_years'] for r in rr) else 'STOP_TOO_FEW_REPEAT_SITES','verified_files':1760,'roster_sites':32,
      'eligible_site_years':sum(r['eligible_years'] for r in rr),'sites_any_eligible':sum(r['eligible_years']>0 for r in rr),
      'issues':merge_numeric([x['issues'] for x in a]),'primary_sites':len(main),'focal_sites':len(focal),
      'primary':None,'focal':None}
    if main:
        out['primary']={'train_site_years':sum(x['train_years'] for x in main),'test_site_years':sum(x['test_years'] for x in main),
         'equal_site_baseline_TV':mean(x['baseline_TV'] for x in main),'equal_site_forecast_TV':mean(x['forecast_TV'] for x in main),
         'equal_site_gain':mean(x['gain'] for x in main),'sites_positive_gain':sum(x['gain']>0 for x in main)}
        if len(main)>=8:
            out['status']='TEMPORAL_FORECAST_DESCRIPTIVE_SUPPORT' if out['primary']['equal_site_gain']>0 and out['primary']['sites_positive_gain']>=0.75*len(main) else 'TEMPORAL_FORECAST_CRITERION_NOT_MET'
    if focal:
        out['focal']={'train_site_years':sum(x['train_years'] for x in focal),'test_site_years':sum(x['test_years'] for x in focal),
         'equal_site_test_delta':mean(x['test_delta'] for x in focal),'equal_site_test_bounds':[mean(x['test_bounds'][i] for x in focal) for i in (0,1)],
         'equal_site_mse_gain':mean(x['mse_gain'] for x in focal),'sites_same_sign':sum(x['train_delta']*x['test_delta']>0 for x in focal),
         'minimum_8_sites_met':len(focal)>=8}
    return out
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='mode',required=True)
    sp=sub.add_parser('shard');sp.add_argument('index',type=int,choices=range(4))
    cp=sub.add_parser('combine');cp.add_argument('directory',type=Path);a=p.parse_args()
    out={'schema':SCHEMA,'scope':'Captured target genus composition in matched recorded trap opportunities; not true abundance, diet, seed dispersal or recruitment. Same-site temporal transfer only. Prior resource-link and seed prediction stops unchanged.'}
    path=BUILD/(f'neon_composition_v13b_shard_{a.index}.json' if a.mode=='shard' else 'neon_composition_v13b.json')
    try:out.update(shard(a.index) if a.mode=='shard' else combine(a.directory))
    except Exception as e:out.update(status='STOP_SOURCE_OR_ANALYSIS',error_class=type(e).__name__,reason=str(e) if type(e) is ValueError and re.fullmatch('[A-Z0-9_]+',str(e)) else 'UNEXPORTED_ERROR')
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    # Shard outputs include anonymous site summaries; no tags, plots, coordinates or dates.
    print(json.dumps({k:v for k,v in out.items() if k!='site_results'},indent=2,sort_keys=True))
    return 2 if out['status']=='STOP_SOURCE_OR_ANALYSIS' else 0
if __name__=='__main__':raise SystemExit(main())
