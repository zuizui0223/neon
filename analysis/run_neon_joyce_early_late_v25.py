"""V25: Joyce 2024 matched early retention and later establishment.
Public source verification and fixed leave-site-out prediction; no causal
mammal-specific or seasonal interpretation. Source DOI 10.5061/dryad.05qfttfb9.
"""
from collections import Counter,defaultdict
from statistics import mean
from html.parser import HTMLParser
import csv,io,hashlib,json,math,pathlib,urllib.request,urllib.parse
BASE='https://datadryad.org'
DOI='10.5061/dryad.05qfttfb9'
LAND=BASE+'/dataset/doi:'+DOI
FILES=['seed_removal.csv','seedling_establishment.csv','seed_predator_detections.csv']
CAP=2_000_000
SPECIES={'OCO_PUB','OTO_NOV','PSE_MOL','QUE_BEN'}
def require(x,m):
    if not x:raise ValueError(m)
def read(url,accept='*/*'):
    require(urllib.parse.urlparse(url).scheme=='https','non_https')
    r=urllib.request.Request(url,headers={'User-Agent':'NEON research source verification/1.0','Accept':accept})
    with urllib.request.urlopen(r,timeout=30) as f:b=f.read(CAP+1);mime=f.headers.get('Content-Type','')
    require(len(b)<=CAP,'byte_cap')
    return b,mime
class Links(HTMLParser):
    def __init__(self):super().__init__();self.a=None;self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':self.a=(dict(attrs),[])
    def handle_data(self,d):
        if self.a:self.a[1].append(d)
    def handle_endtag(self,tag):
        if tag=='a' and self.a:
            self.links.append((self.a[0],''.join(self.a[1]).strip()));self.a=None
def source(out):
    u=BASE+'/api/v2/datasets/'+urllib.parse.quote('doi:'+DOI,safe='')
    x=json.loads(read(u,'application/json')[0])
    require(x.get('identifier','').lower()=='doi:'+DOI,'dataset_identity')
    v=json.loads(read(urllib.parse.urljoin(BASE,x['_links']['stash:version']['href']),'application/json')[0])
    fs=json.loads(read(urllib.parse.urljoin(BASE,v['_links']['stash:files']['href']),'application/json')[0])['_embedded']['stash:files']
    out['title']=x.get('title');out['version']=v.get('versionNumber')
    out['provider_files']=[{k:f.get(k) for k in ('path','size','digest','digestType')} for f in fs]
    require(all(sum(f.get('path')==n for f in fs)==1 for n in FILES),'file_roster')
    html,mime=read(LAND,'text/html')
    require('html' in mime.lower(),'landing_content_type')
    p=Links();p.feed(html.decode('utf8','replace'))
    result={};out['downloads']={}
    for name in FILES:
        receipt={};out['downloads'][name]=receipt
        try:
            f=next(f for f in fs if f['path']==name)
            urls=set()
            for a,t in p.links:
                href=a.get('href','');label=t+' '+a.get('title','')+' '+a.get('download','')
                if name.lower() in label.lower() and 'download' in href.lower():
                    url=urllib.parse.urljoin(BASE,href)
                    if urllib.parse.urlparse(url).hostname=='datadryad.org':urls.add(url)
            require(len(urls)==1,'public_download_link_not_unique')
            url=next(iter(urls));receipt['url']=url
            b,mime=read(url)
            receipt.update(bytes=len(b),mime=mime,sha256=hashlib.sha256(b).hexdigest())
            algo=str(f['digestType']).lower().replace('-','')
            require(algo in ('md5','sha1','sha256','sha512'),'unrecognized_digest')
            require(len(b)==int(f['size']) and hashlib.new(algo,b).hexdigest()==f['digest'],'provider_checksum_mismatch')
            rr=csv.DictReader(io.StringIO(b.decode('utf-8-sig'),newline=''))
            h=rr.fieldnames
            require(h and len(h)==len(set(h)),'csv_header')
            rows=list(rr)
            require(all(None not in r and all(z is not None for z in r.values()) for r in rows),'csv_width')
            receipt.update(status='VERIFIED',header=h,rows=len(rows))
            result[name]=rows
        except Exception as e:receipt.update(status='STOP',reason=type(e).__name__+': '+str(e)[:200])
    return result
def number(v):
    z=float(v);require(math.isfinite(z) and z==int(z) and z>=0,'noninteger_count');return int(z)
def paired(rows,final=False):
    y='seeds_established' if final else 'seeds_remaining'
    z='seeds_failed' if final else 'seeds_missing'
    expected=352 if final else 368
    require(len(rows)==expected,'published_row_count')
    fields={'species','site','trt','station','exclosure','seeds_total',y,z}
    require(fields<=set(rows[0]),'missing documented key or outcome field')
    out={}
    for r in rows:
        site=r['site'].strip();sp=r['species'].strip();hab=r['trt'].strip();st=number(r['station']);arm=r['exclosure'].strip()
        require(site and sp in SPECIES and hab in ('Restored','Remnant') and st in range(1,5) and arm in ('caged','exposed'),'unexpected literal key')
        k=(site,sp,hab,st,arm)
        N,a,b=(number(r[x]) for x in ('seeds_total',y,z))
        require(N in (7,8,11) and a+b==N and k not in out,'count partition or key duplication')
        out[k]=(N,a)
    require(sum(v[0] for v in out.values())==(2880 if final else 3024),'published denominator drift')
    return out
def fit_score(recs,extra):
    # Fixed strata-specific means baseline. Estimate a single within-stratum
    # centered slope from training sites only. For extra=2 add camera index
    # separately via fixed ridge in standardized residual units.
    sites=sorted({r['site'] for r in recs});scores=[]
    require(len(sites)>=6,'too_few_sites')
    for site in sites:
        train=[r for r in recs if r['site']!=site];test=[r for r in recs if r['site']==site]
        group=defaultdict(list)
        for r in train:group[r['stratum']].append(r)
        require(all(r['stratum'] in group and len({q['site'] for q in group[r['stratum']]})>=2 for r in test),'training stratum not supported')
        mus={k:{f:mean(r[f] for r in v) for f in ('early','late')} for k,v in group.items()}
        rx=[r['early']-mus[r['stratum']]['early'] for r in train];ry=[r['late']-mus[r['stratum']]['late'] for r in train]
        ss=sum(x*x for x in rx);require(ss>1e-12,'no residual early variation')
        beta=sum(x*y for x,y in zip(rx,ry))/ss
        errors=[]
        for r in test:
            m=mus[r['stratum']]
            p0=m['late'];p1=max(-1,min(1,p0+beta*(r['early']-m['early'])))
            errors.append(((r['late']-p0)**2,(r['late']-p1)**2,(r['late']-r['early'])**2))
        scores.append({'site':site,'n':len(test),'baseline_mse':mean(x[0] for x in errors),'early_augmented_mse':mean(x[1] for x in errors),'unchanged_early_mse':mean(x[2] for x in errors),'train_slope':beta})
    rm={k:math.sqrt(mean(s[k] for s in scores)) for k in ('baseline_mse','early_augmented_mse','unchanged_early_mse')}
    return {'site_equal_RMSE':rm,'site_count':len(sites),'sites_improved_over_baseline':sum(s['early_augmented_mse']<s['baseline_mse'] for s in scores),'site_scores':scores,'meets_descriptive_gate':rm['early_augmented_mse']<min(rm['baseline_mse'],rm['unchanged_early_mse']) and sum(s['early_augmented_mse']<s['baseline_mse'] for s in scores)>=.75*len(sites)}
def analyze(raw,out):
    E=paired(raw[FILES[0]]);L=paired(raw[FILES[1]],True)
    require(set(L)<=set(E),'final not subset of early')
    dropped=set(E)-set(L)
    require(len(dropped)==16 and {k[0] for k in dropped}=={'HB'},'documented loss mismatch')
    require(all(E[k][0]==L[k][0] for k in L),'denominator mismatch between stages')
    groups=defaultdict(list)
    for k in L:
        if k[-1]!='caged':continue
        x=k[:-1];a=x+('caged',);b=x+('exposed',)
        require(b in L and E[a][0]==E[b][0],'unmatched treatment denominators')
        groups[x[:3]].append((a,b))
    require(sum(map(len,groups.values()))*2==len(L),'unmatched stations')
    recs=[]
    for k,v in sorted(groups.items()):
        require(len(v)==4 and {a[3] for a,b in v}==set(range(1,5)),'not four stations')
        n=sum(E[a][0] for a,b in v);require(n==sum(E[b][0] for a,b in v),'unbalanced effort')
        e=(sum(E[a][1]-E[b][1] for a,b in v))/n
        l=(sum(L[a][1]-L[b][1] for a,b in v))/n
        recs.append({'site':k[0],'stratum':(k[1],k[2]),'N_per_arm':n,'early':e,'late':l})
    out['support']={'early_rows':len(E),'final_rows':len(L),'missing_final_rows':len(dropped),'matched_site_species_habitat_units':len(recs),'physical_sites':len({r['site'] for r in recs}),'species':sorted({r['stratum'][0] for r in recs})}
    # No individual fate joint distribution inferred even though the same
    # quadrats are matched. Late established counts may exceed early observed
    # retained counts owing to imperfect observation or early germination.
    out['prediction']=fit_score(recs,False)
    out['status']='DESCRIPTIVE_PREDICTION_COMPLETE'
def main():
    out={'status':'STOP_SOURCE_OR_SUPPORT','doi':DOI,'paper':'10.1111/btp.13381','outcome_opened':False,
      'boundary':'Same sowing quadrats, not individual seed histories. Species and sowing season confounded; one landscape. Early retention deficit not confirmed mortality. Vertebrate exclusion includes birds and cage effects. Species/forest baseline only, not resource or independent consumer baseline. No causal or seasonal inference.'}
    try:
        raw=source(out)
        require(all(k in raw for k in FILES[:2]),'required original tables not verified')
        out['outcome_opened']=True
        analyze(raw,out)
    except Exception as e:out['reason']=type(e).__name__+': '+str(e)[:250]
    p=pathlib.Path('build/neon_joyce_early_late_v25.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
