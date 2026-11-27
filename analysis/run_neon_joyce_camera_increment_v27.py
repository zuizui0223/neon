"""V27: locked camera increment; local original Dryad archive only."""
import argparse, csv, hashlib, io, json, math, pathlib, zipfile
from collections import defaultdict, Counter
from statistics import mean
import numpy as np

SOURCE = {
    'seed_removal.csv': (13364, '0a9fe6484953b591bb03fca3d0a20cfbf2fff553cbed28f4c12dfeb4a8be15c2'),
    'seedling_establishment.csv': (12754, 'a1b34061fb5703fe32b31bff15e0b165dcde28943c5e036a8f86d736c3cee183'),
    'seed_predator_detections.csv': (12967, '9306def6d93b620a54d815ad5589d4688d54c46d38212359230d25077a079302'),
    'README.md': (7483, 'c5eec604c20449c697da6674acd5dd674ea32a9922faf2d4d5bdbf756bb1a7c5'),
}
ZIP_SHA = '334a72b18767888ae339504777837f8c04ed53301ae9fa9703c5747ae9702b03'
MAMMALS = ('unidentified mouse/rat', 'Sciurus granatensis', 'Dasyprocta punctata', 'Dicotyles tajacu')
BIRDS = ('Odontophorus gujanensis', 'Tinamus major')
ROSTER = set(MAMMALS + BIRDS)
MODELS = {
    'M0': ['duration'],
    'M1': ['duration', 'early'],
    'M2': ['duration', 'intensity', 'balance'],
    'M3': ['duration', 'early', 'intensity'],
    'M4': ['duration', 'early', 'intensity', 'balance'],
}

def require(ok, why):
    if not ok:
        raise ValueError(why)

def load(p):
    require(hashlib.sha256(p.read_bytes()).hexdigest() == ZIP_SHA, 'original archive mismatch')
    out = {}
    with zipfile.ZipFile(p) as z:
        for name, (n, h) in SOURCE.items():
            members = [m for m in z.infolist() if m.filename == name]
            require(len(members) == 1 and members[0].file_size == n, 'source roster/size drift ' + name)
            b = z.read(members[0])
            require(hashlib.sha256(b).hexdigest() == h, 'source hash drift ' + name)
            if name.endswith('.csv'):
                reader = csv.DictReader(io.StringIO(b.decode('utf-8-sig'), newline=''))
                rows = list(reader)
                require(len(set(reader.fieldnames)) == len(reader.fieldnames) and all(None not in r and all(v is not None for v in r.values()) for r in rows), 'CSV shape')
                out[name] = rows
    return out

def stage(rows, late):
    out = {}
    for r in rows:
        k = (r['site'], r['species'], r['trt'], int(r['station']), r['exc' if late else 'exclosure'])
        n = int(r['seeds_total'])
        a = int(r['seeds_established' if late else 'seeds_remaining'])
        b = int(r['seeds_failed' if late else 'seeds_missing'])
        require(k not in out and k[-1] in ('caged', 'exposed') and n in (7, 8, 9, 11) and a >= 0 and b >= 0 and a+b == n, 'source stage invalid')
        out[k] = (n, a)
    require(len(out) == (352 if late else 368) and sum(v[0] for v in out.values()) == (2879 if late else 3024), 'stage support drift')
    return out

def contexts(raw):
    e, l = stage(raw['seed_removal.csv'], False), stage(raw['seedling_establishment.csv'], True)
    require(set(l) <= set(e) and len(set(e)-set(l)) == 16 and {k[0] for k in set(e)-set(l)} == {'HB'}, 'final key drift')
    groups = defaultdict(list)
    for k in sorted(l):
        if k[-1] != 'caged': continue
        b = k[:-1] + ('exposed',)
        require(b in l, 'pair missing')
        groups[k[:3]].append((k[3], e[k][1]/e[k][0]-e[b][1]/e[b][0], l[k][1]/l[k][0]-l[b][1]/l[b][0]))
    require(len(groups)==44 and all(sorted(x[0] for x in v)==[1,2,3,4] for v in groups.values()), 'V26 roster drift')
    return {k: {'site': k[0], 'species': k[1], 'forest': k[2], 'early':mean(x[1] for x in v), 'late':mean(x[2] for x in v)} for k,v in groups.items()}

def cameras(raw, ctx):
    rows=raw['seed_predator_detections.csv']
    require(len(rows)==275, 'camera row drift')
    groups=defaultdict(list); blank=0
    for r in rows:
        k=(r['site'],r['focal_species'],r['trt'])
        if any(x in ('','NA') for x in k):
            require(all(x in ('','NA') for x in k), 'partial context key')
            blank+=1;continue
        groups[k].append(r)
    require(blank==1 and len(groups)==41 and len(set(groups)&set(ctx))==39, 'camera key drift')
    no_camera=[list(k) for k in sorted(set(ctx)-set(groups))]
    invalid=[]; valid={}
    for k,rr in sorted(groups.items()):
        if k not in ctx: continue
        taxa=[x['binomial_name'] for x in rr]
        nights={int(x['nights_elapsed']) for x in rr}
        reasons=[]
        if len(set(taxa))!=len(taxa): reasons.append('duplicate_taxon')
        if len(nights)!=1 or min(nights)<=0: reasons.append('inconsistent_effort')
        if not ROSTER<=set(taxa): reasons.append('incomplete_six_taxa')
        if any(int(x['presence']) not in (0,1) or int(x['independent_observations'])<0 or bool(int(x['presence']))!=(int(x['independent_observations'])>0) for x in rr): reasons.append('invalid_presence_count')
        if reasons:
            invalid.append({'key':list(k),'reasons':reasons});continue
        n=next(iter(nights));c={x['binomial_name']:int(x['independent_observations']) for x in rr}
        m=sum(c[t] for t in MAMMALS); b=sum(c[t] for t in BIRDS)
        valid[k]={'nights':n,'mammal':m,'bird':b,'taxon_counts':{t:c[t] for t in sorted(ROSTER)}}
    require(len(valid)==35, 'camera valid support drift')
    ss=defaultdict(set)
    for k in valid:ss[k[1:]].add(k[0])
    unsupported=[list(k) for k in valid if len(ss[k[1:]])<3]
    data=[]
    for k,v in sorted(valid.items()):
        if len(ss[k[1:]])<3:continue
        r={**ctx[k],**v}; n,m,b=r['nights'],r['mammal'],r['bird']
        r.update(duration=math.log(n),intensity=math.log1p(100*(m+b)/n),balance=math.log1p(100*m/n)-math.log1p(100*b/n))
        data.append(r)
    require(len(data)==33 and len({r['site'] for r in data})==8, 'locked common support drift')
    return data,{'camera_rows':275,'blank_key_rows':blank,'camera_contexts':41,'camera_final_key_overlap':39,'no_camera':no_camera,'invalid_camera':invalid,'valid_camera_contexts':35,'unsupported_training_stratum':unsupported,'final_contexts':33,'sites':8}

def cv(data, raw_counts=False):
    # Fit only on training sites: stratum intercepts and centering, then ridge.
    # Standardization of centered training predictors is fit independently per fold.
    dd=[dict(r) for r in data]
    if raw_counts:
        for r in dd:
            r['intensity']=math.log1p(r['mammal']+r['bird'])
            r['balance']=math.log1p(r['mammal'])-math.log1p(r['bird'])
    sites=sorted({r['site'] for r in dd});result={};folds=[]
    for site in sites:
        tr=[r for r in dd if r['site']!=site];te=[r for r in dd if r['site']==site]
        group=defaultdict(list)
        for r in tr:group[r['species'],r['forest']].append(r)
        fields=['early','late','duration','intensity','balance']
        mu={k:{f:mean(r[f] for r in v) for f in fields} for k,v in group.items()}
        require(all(len({q['site'] for q in group[r['species'],r['forest']]})>=2 for r in te), 'training stratum unsupported')
        m=lambda r:mu[r['species'],r['forest']]
        yc=np.array([r['late']-m(r)['late'] for r in tr]);obs=np.array([r['late'] for r in te]); row={'site':site,'n':len(te),'mse':{},'coef':{}}
        for name,fs in MODELS.items():
            x=np.array([[r[f]-m(r)[f] for f in fs] for r in tr]);sd=np.sqrt(np.mean(x*x,axis=0));require(np.all(sd>1e-12), 'constant predictor in '+site+name)
            x=x/sd; beta=np.linalg.solve(x.T@x+np.eye(len(fs)),x.T@yc)
            z=np.array([[r[f]-m(r)[f] for f in fs] for r in te])/sd
            pred=np.clip(np.array([m(r)['late'] for r in te])+z@beta,-1,1)
            row['mse'][name]=float(np.mean((obs-pred)**2));row['coef'][name]=dict(zip(fs,map(float,beta/sd)))
        # Exact original V26 scoring as a reference, not a candidate rescue.
        x=np.array([r['early']-m(r)['early'] for r in tr]);require(x@x>1e-12,'no early variance')
        pred=np.clip(np.array([m(r)['late']+(x@yc)/(x@x)*(r['early']-m(r)['early']) for r in te]),-1,1)
        row['mse']['V26_reference']=float(np.mean((obs-pred)**2))
        row['mse']['unchanged_early']=float(np.mean((obs-np.array([r['early'] for r in te]))**2))
        folds.append(row)
    rm={k:math.sqrt(mean(x['mse'][k] for x in folds)) for k in folds[0]['mse']}
    for a,b in [('M4','M1'),('M4','M3'),('M2','M0')]:
        win=sum(f['mse'][a]<f['mse'][b] for f in folds)
        result[a+'_vs_'+b]={'rmse_gain':rm[b]-rm[a],'relative_rmse_gain':1-rm[a]/rm[b],'sites_improved':win,'meets_descriptive_gate':rm[a]<rm[b] and win>=6}
    return {'equal_site_RMSE':rm,'contrasts':result,'site_folds':folds}

def run(p):
    raw=load(p);ctx=contexts(raw);data,support=cameras(raw,ctx)
    return {'status':'V27_CAMERA_INCREMENT_EVALUATED','support':support,'source_doi':'10.5061/dryad.05qfttfb9','archive_sha256':ZIP_SHA,'source_manifest':SOURCE,'lock_commit':'9870dda5634ad7eb3db3e5c9b319ba6c367f3a7c','primary':cv(data),'raw_count_sensitivity':cv(data,True),'context_records':data,'original_v26_context_records':[ctx[k] for k in sorted(ctx)],'boundary':'Observed encounters at seed quadrats; camera stopping can depend on seed depletion. Not abundance, exogenous pressure, or direct predation attribution. No independent landscape/time/season validation. Exploratory same response data; V25/V26 stops unchanged.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',required=True,type=pathlib.Path);p.add_argument('--out',required=True,type=pathlib.Path);a=p.parse_args()
    out=run(a.input);a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:out[k] for k in ['status','support']},indent=2));print(json.dumps({k:{'equal_site_RMSE':out[k]['equal_site_RMSE'],'contrasts':out[k]['contrasts']} for k in ['primary','raw_count_sensitivity']},indent=2))
