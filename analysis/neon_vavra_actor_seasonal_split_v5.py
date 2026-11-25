"""Actor-resolved seasonal handling of A. saccharum, Vavra & Guiden 2025.
Frozen after source-only inventory, before seasonal counts opened. Descriptive
Dec-to-Jan contrast in one forest, preselected from published winter result;
no new independent confirmation. Strict recorded-count reconciliation.
"""
import csv, datetime as dt, hashlib, io, itertools, json, math, pathlib, re, urllib.request
from collections import Counter, defaultdict

FILES={
 'camera':(45697716,48101,'f22346a9936b3a927f35777b4bd25845',754),
 'actor':(45697752,18768,'61fce3d952efc8d575ad119de0cbbb0f',504),
 'tray':(45697746,4080,'23f47c340da04be6364a4528df3a8a6c',168),
}
MISSING={'','na','nan','n/a'}
def read(k):
    fid,size,md5,n=FILES[k]
    with urllib.request.urlopen(f'https://api.figshare.com/v2/file/download/{fid}',timeout=25) as r:
        b=r.read(size+1)
    if len(b)!=size or hashlib.md5(b).hexdigest()!=md5: raise ValueError(k+' source mismatch')
    a=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))))
    if len(a)!=n: raise ValueError(k+' row count mismatch')
    return a
def norm(v): return str(v).strip().casefold()
def num(v):
    if norm(v) in MISSING: return None
    f=float(v)
    if not math.isfinite(f) or f<0 or not f.is_integer(): raise ValueError('noninteger or negative count')
    return int(f)
def calendar_date(s):
    s=s.strip()
    if norm(s) in MISSING: return None
    for fmt in ('%m/%d/%y','%m/%d/%Y','%Y-%m-%d','%Y/%m/%d','%m-%d-%Y','%m-%d-%y','%d-%b-%y','%d-%b-%Y','%d %b %Y','%Y-%m-%d %H:%M:%S','%m/%d/%Y %H:%M:%S'):
        try:
            d=dt.datetime.strptime(s,fmt).date()
            if 2022<=d.year<=2023: return d
        except ValueError: pass
    raise ValueError('unparsed camera calendar date: '+s)
def calendar_map(cam):
    windows={10:('2022-10-23','2022-10-30'),12:('2022-11-27','2022-12-05'),
             1:('2023-01-22','2023-01-30'),4:('2023-04-15','2023-04-23')}
    found=defaultdict(set); dates=defaultdict(set)
    for r in cam:
        d=calendar_date(r['Date'])
        if d is None: continue
        matches=[m for m,(lo,hi) in windows.items() if dt.date.fromisoformat(lo)<=d<=dt.date.fromisoformat(hi)]
        if len(matches)!=1: raise ValueError('camera date outside paper session: '+str(d))
        code=r['Collection.date'].strip()
        found[code].add(matches[0]); dates[code].add(str(d))
    if set(found)!={'0','2','3','6'} or any(len(v)!=1 for v in found.values()): raise ValueError('calendar code ambiguity')
    mapping={k:next(iter(v)) for k,v in found.items()}
    if set(mapping.values())!=set(windows): raise ValueError('calendar map not one-to-one')
    return mapping,{k:{'first':min(v),'last':max(v),'n_dates':len(v)} for k,v in dates.items()}
def maple(v): return norm(v) in {'acsa','acer saccharum','a. saccharum','sugar maple'}
def key(r): return (r['Collection.date'].strip(),r['Site'].strip(),norm(r['Species']))
def decomposition(a,b):
    # a,b actor -> [consumed, carried]. Unknown actor-specific rates if no handling.
    aa=sum(sum(v) for v in a.values()); bb=sum(sum(v) for v in b.values())
    if not aa or not bb: return {'status':'STOP_NO_HANDLED_SEEDS_IN_ONE_MONTH'}
    taxa=sorted(set(a)|set(b))
    w0={g:sum(a.get(g,[0,0]))/aa for g in taxa}
    w1={g:sum(b.get(g,[0,0]))/bb for g in taxa}
    p0={g:a[g][1]/sum(a[g]) if g in a and sum(a[g]) else None for g in taxa}
    p1={g:b[g][1]/sum(b[g]) if g in b and sum(b[g]) else None for g in taxa}
    delta=sum(v[1] for v in b.values())/bb-sum(v[1] for v in a.values())/aa
    unknown=[(i,g) for i,p in enumerate([p0,p1]) for g in taxa if p[g] is None and (w0[g]+w1[g])>0]
    components=[]
    for corner in itertools.product([0.,1.], repeat=len(unknown)):
        pp=[dict(p0),dict(p1)]
        for (i,g),v in zip(unknown,corner): pp[i][g]=v
        active=[g for g in taxa if w0[g]+w1[g]>0]
        c=sum((w1[g]-w0[g])*(pp[0][g]+pp[1][g])/2 for g in active)
        h=sum((w1[g]+w0[g])*(pp[1][g]-pp[0][g])/2 for g in active)
        assert math.isclose(c+h,delta,abs_tol=1e-12)
        components.append((c,h))
    return {'status':'PARTIAL_IDENTIFICATION' if unknown else 'OBSERVED_DESCRIPTIVE_EXACT_SPLIT',
            'delta_carried_fraction_among_handled':delta,
            'actor_composition_component_bounds':[min(v[0] for v in components),max(v[0] for v in components)],
            'within_actor_component_bounds':[min(v[1] for v in components),max(v[1] for v in components)],
            'unobserved_actor_month_rates':[list(x) for x in unknown],
            'actor_weights_dec':w0,'actor_weights_jan':w1,'actor_carried_rates_dec':p0,'actor_carried_rates_jan':p1}
def main():
    out={'status':'STOP','source_doi':'10.6084/m9.figshare.25620519.v2',
         'primary':'December 2022 to January 2023; descriptive, after prior published winter decline; one forest',
         'interpretation':'Observed in-situ consumption versus whole removal. Not cache, recruitment, animal abundance, or individual behavior.'}
    try:
        cam,actor,tray=[read(k) for k in ['camera','actor','tray']]
        out['source_levels']={'collection_date':sorted({r['Collection.date'] for r in actor}),
            'seed':sorted({r['Seed'] for r in actor}),
            'actor_species':sorted({r['Species'] for r in actor}),
            'camera_species':sorted({r['Species'] for r in cam})}
        a=[r for r in actor if maple(r['Seed'])]
        t=[r for r in tray if maple(r['Seed'])]
        if len(a)!=168 or len(t)!=56: raise ValueError('maple cohort size mismatch')
        known={}
        for r in a:
            k=key(r); v=num(r['tot.seeds'])
            if k in known or v is None: raise ValueError('nonunique/missing actor total')
            known[k]=v
        totals=defaultdict(lambda:[0,0])
        missing=Counter()
        unmatched_positive=0
        for r in cam:
            k=key(r)
            vals=[num(r['ACSA.eaten']),num(r['ACSA.removed'])]
            for i,v in enumerate(vals):
                if v is None: missing[i]+=1
            if k not in known:
                if any(v for v in vals): unmatched_positive+=1
                continue
            for i,v in enumerate(vals):
                if v is not None: totals[k][i]+=v
        out['camera_missing_count_cells']={'eaten':missing[0],'carried':missing[1]}
        mismatches=[(known[k],sum(totals[k])) for k in known if known[k]!=sum(totals[k])]
        out['actor_crosswalk']={'keys':len(known),'mismatches':len(mismatches),'unmatched_positive_camera_rows':unmatched_positive,'total_actor_counts':sum(known.values()),'total_camera_known_counts':sum(sum(v) for v in totals.values())}
        if mismatches or unmatched_positive: raise ValueError('camera to actor count reconciliation failed')
        # Explicit counts sum to independently published actor table for every key.
        # Blank fields are not assigned latent behavior; estimand is recorded counts only.
        tk={}
        for r in t:
            k=(r['Collection.date'].strip(),r['Site'].strip())
            v=num(r['Seeds.removed'])
            if k in tk or v is None: raise ValueError('nonunique/missing tray count')
            tk[k]=v
        rk=defaultdict(int)
        for k,v in known.items(): rk[k[:2]]+=v
        if set(tk)!=set(rk): raise ValueError('tray/actor key mismatch')
        deficit=[tk[k]-rk[k] for k in tk]
        out['tray_crosswalk']={'keys':len(tk),'negative_deficits':sum(d<0 for d in deficit),'positive_deficits':sum(d>0 for d in deficit),'unattributed_counts':sum(d for d in deficit if d>0)}
        if any(d<0 for d in deficit): raise ValueError('actor count exceeds tray disappearance')
        mapping,date_support=calendar_map(cam)
        out['calendar_code_verified_from_camera_dates']=mapping
        out['calendar_date_support']=date_support
        season=defaultdict(lambda:defaultdict(lambda:[0,0]))
        support=defaultdict(set)
        site_by_month=defaultdict(set)
        unresolved=Counter()
        for k,v in tk.items():
            m=mapping[k[0]]; site_by_month[m].add(k[1]); unresolved[m]+=v-rk[k]
        if set(site_by_month)!={10,12,1,4} or any(len(x)!=14 for x in site_by_month.values()): raise ValueError('unexpected month/site support')
        for k,v in totals.items():
            m=mapping[k[0]]
            for i in (0,1): season[m][k[2]][i]+=v[i]
            if sum(v): support[m,k[2]].add(k[1])
        out['status']='DESCRIPTIVE_ACTOR_RESOLVED'
        out['months']={}
        for m in (10,12,1,4):
            vals=season[m]; n=sum(sum(v) for v in vals.values()); c=sum(v[1] for v in vals.values()); u=unresolved[m]
            out['months'][m]={'actors':{g:{'in_situ':v[0],'carried':v[1],'sites_with_handling':len(support[m,g])} for g,v in vals.items()},
                'identified_handled':n,'carried':c,'unattributed_tray_disappearance':u,
                'carried_fraction_identified':c/n if n else None,
                'carried_fraction_all_disappearance_bounds':[c/(n+u),(c+u)/(n+u)] if n+u else None}
        out['winter_split']=decomposition(season[12],season[1])
        out['matched_active_sites_dec_jan']={g:len(support[12,g]&support[1,g]) for g in set(season[12])|set(season[1])}
        out['pooled_actor_counts']={g:[sum(season[m].get(g,[0,0])[i] for m in (10,12,1,4)) for i in (0,1)] for g in {g for s in season.values() for g in s}}
        out['limitation']='No p-value or equivalence test. Within-actor term can include population composition, selection of sites or individuals, not identified individual plasticity.'
    except (OSError,ValueError,KeyError,TypeError) as e:
        out.update(status='STOP_SOURCE_OR_SUPPORT',reason=str(e)[:300])
    pathlib.Path('vavra_seasonal_result.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
