"""Independent Merz 2023 Aug-Oct observational stage comparison, V7.
Frozen after support-only run, before month-specific action counts.
One forest; no inference about annual seasonality or repeated individual plasticity.
"""
import collections as C, itertools, json, math, pathlib
from audit_neon_merz_support_v7 import fetch, keys, present

SK=['Grid','Site','Session','Night']
G=('PM','MG')
PERIODS=('3','5')
FATE='Eat..disperse..reject..or.move'
def integer(v):
    if not present(v): return None
    x=float(v)
    if not math.isfinite(x) or x<0 or int(x)!=x: raise ValueError('noninteger field count')
    return int(x)
def mean(x):
    x=list(x); return sum(x)/len(x)
def summarize(a):
    H=sum(sum(v) for v in a.values()); Y=sum(v[0] for v in a.values())
    return H,Y,Y/H if H else None
def split(a,b):
    h0,y0,p0=summarize(a); h1,y1,p1=summarize(b)
    if not h0 or not h1: return {'status':'STOP_NO_HANDLING'}
    intensity=(h1-h0)*(p0+p1)/2; allocation=(h0+h1)*(p1-p0)/2
    assert math.isclose(intensity+allocation,y1-y0,abs_tol=1e-10)
    ws=[{g:sum(x[g])/h for g in G} for x,h in [(a,h0),(b,h1)]]
    ps=[{g:x[g][0]/sum(x[g]) if sum(x[g]) else None for g in G} for x in (a,b)]
    missing=[(i,g) for i in (0,1) for g in G if ps[i][g] is None and ws[0][g]+ws[1][g]>0]
    active=[g for g in G if ws[0][g]+ws[1][g]>0]
    pairs=[]
    for corner in itertools.product([0.,1.],repeat=len(missing)):
        q=[dict(p) for p in ps]
        for (i,g),v in zip(missing,corner): q[i][g]=v
        c=sum((ws[1][g]-ws[0][g])*(q[0][g]+q[1][g])/2 for g in active)
        b=sum((ws[0][g]+ws[1][g])*(q[1][g]-q[0][g])/2 for g in active)
        assert math.isclose(c+b,p1-p0,abs_tol=1e-10)
        pairs.append((c*(h0+h1)/2,b*(h0+h1)/2))
    return {'status':'DESCRIPTIVE','handling_rates':[h0,h1],'carriage_rates':[y0,y1],
      'carriage_share':[p0,p1],'delta_carriage_rate':y1-y0,'intensity_component':intensity,
      'allocation_component':allocation,'composition_component_bounds':[min(x[0] for x in pairs),max(x[0] for x in pairs)],
      'within_taxon_component_bounds':[min(x[1] for x in pairs),max(x[1] for x in pairs)],
      'missing_taxon_month_rates':missing,'actor_weights':ws,'actor_rates':ps}
def main():
    out={'status':'STOP','source':'10.6084/m9.figshare.28207769.v2',
         'contrast':'Aug vs Oct, WP, observed PM/MG unambiguous terminal carriage D vs consumption E; all PIT states',
         'frozen_rule':'valid station-night keys, identical duplicates only, >=2 positive offered station nights per period per shared grid x density; >=3 grids and >=4 cells; equal grid and within-grid density weights; strict unique terminal seed-night and reconciliation gates',
         'individual_seasonal_gate':'STOP: upper bound 3 shared PIT across Aug/Oct all seed finding; do not fit individual plasticity'}
    try:
        a,s=fetch('all'),fetch('station')
        stations={}; blank=0; identical=0
        for r in s:
            k=keys(r,SK)
            if not all(present(x) for x in k):
                if any(present(r.get(f,'')) for f in ('WP.seeds.set','WP.seeds.left','RO.seeds.set','RO.seeds.left')): raise ValueError('invalid key with seed data')
                blank+=1; continue
            v=(r['Treatment'].strip(),integer(r['WP.seeds.set']),integer(r['WP.seeds.left']))
            if k in stations:
                if stations[k]!=v: raise ValueError('conflicting station-night seed/density')
                identical+=1; continue
            stations[k]=v
        valid={k:v for k,v in stations.items() if v[0] in ('high density','low density') and v[1] is not None and v[2] is not None and 0<=v[2]<=v[1] and v[1]>0}
        cells=C.defaultdict(list)
        for k,v in valid.items(): cells[(k[0],v[0],k[2])].append(k)
        shared=sorted({(g,t) for g,t,m in cells if all(len(cells.get((g,t,p),[]))>=2 for p in PERIODS)})
        grids=sorted({g for g,t in shared})
        out['station_support']={'source_rows':len(s),'blank_key_rows':blank,'identical_station_key_duplicates':identical,'distinct_valid_offer_nights':len(valid),'matched_cells':len(shared),'matched_grids':len(grids),
            'matched_nights_by_period':{p:sum(len(cells[g,t,p]) for g,t in shared) for p in PERIODS}}
        if len(grids)<3 or len(shared)<4: raise ValueError('insufficient matched effort')
        target={k for g,t in shared for p in PERIODS for k in cells[g,t,p]}
        # Validate unique terminal seed identities across all documented actors in matched nights.
        terminal={}; dup=0; unknown=0; absent=0
        for r in a:
            k=keys(r,SK)
            if k not in target or r['Seed.SPP']!='WP' or r['Seed.Found..Y.N.']!='Y': continue
            f=r[FATE]; actor=r['Species']
            if f not in ('D','E'):
                if f not in ('R',): unknown+=1
                continue
            sid=r['Seed.ID'].strip()
            if not present(sid): absent+=1; continue
            ek=k+(sid,)
            sig=keys(r,['Species','PIT','Visit.ID','Timestamp.found',FATE])
            if ek in terminal:
                if terminal[ek]!=sig: raise ValueError('conflicting terminal seed-night records')
                dup+=1
            else: terminal[ek]=sig
        out['source_gate']={'terminal_seed_night_records':len(terminal),'identical_terminal_duplicates':dup,'terminal_without_seed_id':absent,'other_ambiguous_WP_event_rows':unknown}
        if absent: raise ValueError('terminal event has missing seed ID')
        per=C.defaultdict(lambda:{g:[0,0] for g in G})
        counted=C.Counter()
        for ek,sig in terminal.items():
            k=ek[:-1]; actor=sig[0]; f=sig[-1]; counted[k]+=1
            if actor in G: per[k][actor][0 if f=='D' else 1]+=1
        bad=sum(counted[k]>valid[k][1]-valid[k][2] for k in target)
        out['source_gate']['station_nights_terminal_count_exceeds_field_disappearance']=bad
        if bad: raise ValueError('terminal count exceeds field disappearance')
        # All matched valid station nights, including no visits/zero focal actor outcomes.
        estimates={}; by_grid={}
        for p in PERIODS:
            pg={}
            for g in grids:
                gg=[t for gg,t in shared if gg==g]
                rates=[]
                for t in gg:
                    ks=cells[g,t,p]; n=len(ks)
                    rates.append({'actor':{actor:[sum(per[k][actor][j] for k in ks)/n for j in (0,1)] for actor in G},
                                  'field_disappearance':sum(valid[k][1]-valid[k][2] for k in ks)/n,
                                  'offered':sum(valid[k][1] for k in ks)/n})
                pg[g]={'actor':{actor:[mean(r['actor'][actor][j] for r in rates) for j in (0,1)] for actor in G},
                      'field_disappearance':mean(r['field_disappearance'] for r in rates),'offered':mean(r['offered'] for r in rates)}
            by_grid[p]=pg
            aa={actor:[mean(pg[g]['actor'][actor][j] for g in grids) for j in (0,1)] for actor in G}
            h,y,q=summarize(aa); field=mean(pg[g]['field_disappearance'] for g in grids)
            estimates[p]={'actor_rates':aa,'field_disappearance_rate':field,'offered_rate':mean(pg[g]['offered'] for g in grids),
               'known_focal_handling_rate':h,'known_focal_carriage_rate':y,'known_focal_carriage_share':q,
               'all_disappearance_carriage_bounds':[y/field,(y+field-h)/field] if field else None}
        out.update(status='DESCRIPTIVE_MATCHED_GRID_DENSITY',monthly=estimates,split=split(estimates['3']['actor_rates'],estimates['5']['actor_rates']))
        out['grid_direction_summary']=[{ 'grid':i+1,'focal_H':[summarize(by_grid[p][g]['actor'])[0] for p in PERIODS],
          'focal_Y':[summarize(by_grid[p][g]['actor'])[1] for p in PERIODS]} for i,g in enumerate(grids)]
        out['boundary']='Rates per sampled station-night under matched grids and offered density; stations moved adaptively, unidentified actors and ambiguous fates remain. Within-taxon term does not identify repeated-individual plasticity. No annual generalization, causal effect, p-value or equivalence.'
    except (OSError,ValueError,KeyError,TypeError) as e: out.update(status='STOP_SOURCE_OR_SUPPORT',reason=str(e)[:300])
    pathlib.Path('merz_matched_stage.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
