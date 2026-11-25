"""V10: locked August-calibrated prediction of previously uninspected September D/E.
Same forest, previously used August/October source; temporal holdout only.
Source gate before terminal event grouping. No tuning on September.
"""
import collections as C,itertools,json,math,pathlib
from audit_neon_merz_support_v7 import fetch,keys,present,date
from neon_merz_matched_stage_v7 import SK,FATE,integer
DENS=('low density','high density')
G=('PM','MG')
def rng(x): return [min(x),max(x)]
def frac(n,d): return n/d
def combine(a,b): return tuple(x+y for x,y in zip(a,b))
ZERO=(0,0,0,0) # PM D,E; MG D,E
def states_by_cell(rows,stations,target,cellmap):
    groups=C.defaultdict(list)
    for r in rows:
        k=keys(r,SK)
        if k in target and r['Seed.SPP']=='WP' and r['Seed.Found..Y.N.']=='Y' and r[FATE] in ('D','E'):
            if not present(r['Seed.ID']): raise ValueError('missing terminal seed label')
            groups[k,r['Seed.ID'].strip()].append((r['Species'],r[FATE]))
    bynight=C.defaultdict(list)
    for (k,sid),rs in groups.items(): bynight[k].append(rs)
    cellstates={cell:{ZERO} for cell in set(cellmap.values())}
    support=C.Counter()
    for k in sorted(target):
        cap=integer(stations[k]['WP.seeds.set'])-integer(stations[k]['WP.seeds.left'])
        state={(0,ZERO)}
        for rs in bynight[k]:
            if len(rs)>8: raise ValueError('ambiguous label group too large for prespecified enumeration')
            opts=set()
            # Same assumption as V8: unique singleton retained, multirow group any subset.
            sel=[rs] if len(rs)==1 else [list(v for v,on in zip(rs,bits) if on) for bits in itertools.product((0,1),repeat=len(rs))]
            if len(rs)>1: support['ambiguous_groups']+=1
            else: support['singleton_groups']+=1
            for rr in sel:
                x=[0]*4
                for actor,fate in rr:
                    if actor in G: x[2*G.index(actor)+(fate=='E')]+=1
                opts.add((len(rr),tuple(x)))
            state={(n+m,combine(x,y)) for n,x in state for m,y in opts if n+m<=cap}
            if not state: raise ValueError('no feasible terminal assignment')
        ns={x for n,x in state}
        cell=cellmap[k]
        cellstates[cell]={combine(x,y) for x in cellstates[cell] for y in ns}
        if len(cellstates[cell])>100000: raise ValueError('cell enumeration exceeds fixed limit')
    return cellstates,dict(support)
def main():
    out={'status':'STOP','source':'10.6084/m9.figshare.28207769.v2',
         'design':'Aug (session 3) calibration; Sep (4) temporal evaluation; Oct excluded from behavioral prediction. Frozen original 4 V8 grids x 2 densities; no response-driven cell selection.',
         'model':'MG interaction share q. Baseline p=(MG handled+0.5)/(total focal handled+1) in Aug same grid-density. Adjusted odds p/(1-p) multiplied by Sept/Aug capture odds ratio (unique MG+0.5)/(unique PM+0.5) from prior monthly capture. Capture-only diagnostic p from Sep counts. Primary error: equal-cell squared share error, improvement baseline minus adjusted; positive across all feasible scenarios means descriptive support. Secondary conditional carriage share from same Aug species-specific smoothed D/(D+E) applied to baseline/adjusted MG shares. No tuning, no p-values.',
         'gate':'All four original grids, both densities, >=2 valid offer-nights in each of Aug and Sep. Each grid-month >=2 identified focal captures in total, no missing focal PIT or conflicting species tags, capture dates parsed and before/equal earliest corresponding observed camera date with published after-trapping order, all dates in correct month. Same camera effort not guaranteed. Strict terminal singleton assumption plus V8 ambiguity bounds. If any cell has zero focal handling under a feasible state, STOP share comparison. No use of Sept outcomes before gate.'}
    try:
        a,s,c=[fetch(k) for k in ('all','station','capture')]
        st={keys(r,SK):r for r in s if all(present(v) for v in keys(r,SK))}
        fs=['WP.seeds.set','WP.seeds.left','RO.seeds.set','RO.seeds.left']
        assert len(st)==288 and [sum(integer(r[k]) for r in st.values()) for k in fs]==[4280,2049,955,605] and all(keys(r,SK) in st for r in a)
        valid={k:r for k,r in st.items() if r['Treatment'] in DENS and 0<=integer(r['WP.seeds.left'])<=integer(r['WP.seeds.set']) and integer(r['WP.seeds.set'])>0}
        cells=C.defaultdict(list)
        for k,r in valid.items(): cells[k[0],r['Treatment'],k[2]].append(k)
        shared=sorted({(g,t) for g,t,p in cells if all(len(cells.get((g,t,m),[]))>=2 for m in ('3','5'))})
        grids=sorted({g for g,t in shared})
        assert len(grids)==4 and len(shared)==8 and sum(len(cells[g,t,p]) for g,t in shared for p in ('3','5'))==159
        if any(len(cells.get((g,t,p),[]))<2 for g,t in shared for p in ('3','4')): raise ValueError('insufficient Aug/Sep matched offer nights')
        target={k for g,t in shared for p in ('3','4') for k in cells[g,t,p]}
        cellmap={k:(g,t,p) for g,t in shared for p in ('3','4') for k in cells[g,t,p]}
        rows=[r for r in c if r['YEAR']=='23' and r['SESSION'] in ('3','4') and r['GRID'] in grids]
        ids=C.defaultdict(set); tagsp=C.defaultdict(set); cd=C.defaultdict(list)
        for r in rows:
            g,p=r['GRID'],r['SESSION']; d=date(r['DATE'])
            if d is None or d.year!=2023 or d.month!=int(p)+5: raise ValueError('capture date not parsed/matched calendar')
            cd[g,p].append(d)
            if r['SPP2'] in G:
                if not present(r['PIT']): raise ValueError('missing focal capture identity')
                ids[g,p,r['SPP2']].add(r['PIT']); tagsp[r['PIT']].add(r['SPP2'])
        if any(len(v)>1 for v in tagsp.values()): raise ValueError('conflicting focal capture species')
        camdates=C.defaultdict(list)
        for r in a:
            k=keys(r,SK)
            if k in target:
                d=date(r['Date']); p=k[2]
                if d is None or d.year!=2023 or d.month!=int(p)+5: raise ValueError('camera date not parsed/matched calendar')
                camdates[k[0],p].append(d)
        # Explicitly require capture survey preceding first observed video in each grid-month.
        support=[]
        for g in grids:
            for p in ('3','4'):
                n={x:len(ids[g,p,x]) for x in G}
                if sum(n.values())<2 or not cd[g,p] or not camdates[g,p] or max(cd[g,p])>min(camdates[g,p]): raise ValueError('capture coverage or chronology gate')
                support.append({'grid':g,'session':p,'counts':n,'capture_last':str(max(cd[g,p])),'first_camera':str(min(camdates[g,p])),
                                'nights':{t:len(cells[g,t,p]) for t in DENS}})
        out['source_gate']={'status':'GO','grid_months':support,'matched_cells':len(shared),'target_nights':len(target)}
        # No held-out action counts were accessed before this point.
        cs,ambiguity=states_by_cell(a,st,target,cellmap)
        out['ambiguity_support']=ambiguity
        cellsout=[]; metricdiffs=C.defaultdict(list)
        for g,t in shared:
            a0=cs[g,t,'3']; a1=cs[g,t,'4']
            if any(sum(x)==0 for x in a0|a1): raise ValueError('zero handling in a feasible cell-period scenario')
            cap0=(len(ids[g,'3','MG'])+.5)/(len(ids[g,'3','PM'])+.5)
            cap1=(len(ids[g,'4','MG'])+.5)/(len(ids[g,'4','PM'])+.5)
            r=cap1/cap0
            m=C.defaultdict(list)
            for x,y in itertools.product(a0,a1):
                p=(sum(x[2:])+.5)/(sum(x)+1)
                pred=(p*r)/(1-p+p*r)
                obs=sum(y[2:])/sum(y)
                pm=(x[0]+.5)/(sum(x[:2])+1)
                mg=(x[2]+.5)/(sum(x[2:])+1)
                pc0=(1-p)*pm+p*mg
                pc1=(1-pred)*pm+pred*mg
                oc=(y[0]+y[2])/sum(y)
                cprior=cap1/(1+cap1)
                z={'baseline_share':p,'adjusted_share':pred,'observed_share':obs,'capture_only_share':cprior,
                   'baseline_sqerr':(p-obs)**2,'adjusted_sqerr':(pred-obs)**2,
                   'share_gain':(p-obs)**2-(pred-obs)**2,
                   'capture_only_gain':(p-obs)**2-(cprior-obs)**2,
                   'baseline_carriage_share':pc0,'adjusted_carriage_share':pc1,'observed_carriage_share':oc,
                   'carriage_gain':(pc0-oc)**2-(pc1-oc)**2,
                   'aug_handled':sum(x),'sep_handled':sum(y)}
                for k,v in z.items():m[k].append(v)
            rr={k:rng(v) for k,v in m.items()}
            cellsout.append({'grid':g,'density':t,'aug_feasible_count_states':len(a0),'sep_feasible_count_states':len(a1),'capture_odds_ratio_change':r,'ranges':rr})
            for k in ('share_gain','capture_only_gain','carriage_gain','baseline_sqerr','adjusted_sqerr'):
                metricdiffs[k].append(rr[k])
        out['cells']=cellsout
        # Cell-wise ambiguity options do not share seed-night keys, so extrema additive.
        out['equal_cell_score_ranges']={k:[sum(x[i] for x in v)/len(v) for i in (0,1)] for k,v in metricdiffs.items()}
        out['decision']={'share_gain_positive_all':out['equal_cell_score_ranges']['share_gain'][0]>0,
                         'share_gain_negative_all':out['equal_cell_score_ranges']['share_gain'][1]<0,
                         'carriage_gain_positive_all':out['equal_cell_score_ranges']['carriage_gain'][0]>0,
                         'cells_positive_share_gain_all':sum(z['ranges']['share_gain'][0]>0 for z in cellsout)}
        out['status']='V10_TEMPORAL_DESCRIPTIVE_EVALUATION'
        out['boundary']='Relative captured-tag index, not true abundance/detection. Same region, only one year, previously used August and October, no independent geographic confirmation. Prior capture counts and observed interaction shares are separate observation streams, not causal drivers. Equal-cell share errors are not population risk estimates or CIs.'
    except (OSError,ValueError,KeyError,TypeError,AssertionError) as e: out.update(status='STOP_SOURCE_OR_SUPPORT',reason=type(e).__name__+': '+str(e)[:200])
    pathlib.Path('merz_capture_prediction_v10.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
