"""V19b: terminal recorded seed fate, separate from stopped common-30d AGE endpoint.
Locked after support-only audit and before counts. Do not infer event times.
"""
import collections as C,hashlib,io,json,math,pathlib
from statistics import mean
import openpyxl
from audit_neon_pillay_source_v19 import get,parse,date,n,key
EXPECTED_SHA='25caef9e57be78484d5dd50d4021aca66eaae3256b274c93dbc90037cd9c5e14'
FIELDS=['FTYPE','TREE.ID','TRANSECT','PLOT','DISTANCE','SEED.ID','DENS.TRT','TRT','START','STOP','STAGE','SURV','AGE']
def metric(rows):
    counts=C.Counter((str(r['STAGE']).strip(),n(r['SURV'])) for r in rows)
    return {'N':len(rows),'terminal_alive':sum(v for (stage,s),v in counts.items() if s==0),
        'terminal_alive_seedling':counts['seedling',0],
        'ever_seedling_recorded':sum(v for (stage,s),v in counts.items() if stage=='seedling'),
        'stage_by_surv':{stage:{str(s):counts[stage,s] for s in (0,1)} for stage in ('germinated','intact','seedling','ungerminated')}}
def average(plots,endpoint):
    return mean(p[endpoint] for p in plots)
def main():
    out={'status':'STOP','source_doi':'10.5281/zenodo.2020340',
         'scope':'Terminal recorded fate only, not 30-day survival, actual recruitment to adulthood or direct mammal dispersal. Density 5 vs 50 perfectly confounded with distance 2 vs 32 m. One 2014 mast event.',
         'locked_primary':'All 56 plots; terminal alive seedling = SURV 0 and STAGE seedling, separately terminal alive (any stage). Use complete original seeds. Pair at source tree × distance/density × start-date block, equal replicate plots each arm. Source tree grouping rather than guessed transect pair. Equal tree-weighted contrast, no p-value. Verify terminal censor dates within block, deaths no later than censor date where known. Do not infer exact death time from STOP or AGE. Cross-density contrast only where all four arms have same start and censor date within tree where known. Require all blocks, no outcome-based removal.'}
    try:
        b=get()
        if hashlib.sha256(b).hexdigest()!=EXPECTED_SHA:raise ValueError('source byte drift')
        w=openpyxl.load_workbook(io.BytesIO(b),read_only=True,data_only=True)
        rows,_=parse(w['ExclosureSingleRec-Seed'],FIELDS,1540)
        g=C.defaultdict(list)
        for r in rows:g[key(r)].append(r)
        if len(g)!=56:raise ValueError('plot support drift')
        plots=[];blocks=C.defaultdict(lambda:C.defaultdict(list)); trees=C.defaultdict(lambda:C.defaultdict(list))
        # First gate: source rows and complete nominal input denominators only.
        for k,rr in sorted(g.items()):
            forest,tree,transect,plot,distance,trt,density=k
            expected={'Logged':{'logged-ctrl':'open','logged-excl':'exclosure'},'Unlogged':{'primary-ctrl':'open','primary-excl':'exclosure'}}
            arm=expected.get(forest,{}).get(trt);d=int(density)
            if not arm or (d,int(distance)) not in ((5,2),(50,32)) or len(rr)!=d or len({str(r['SEED.ID']) for r in rr})!=d:raise ValueError('plot denominator or context drift')
            starts={date(r['START']) for r in rr}
            if len(starts)!=1 or None in starts or any(date(r['STOP']) is None or date(r['STOP'])<next(iter(starts)) for r in rr):raise ValueError('plot dates drift')
            start=next(iter(starts))
            p={'forest':forest,'tree':tree,'plot':plot,'density':d,'distance':int(distance),'arm':arm,'start':str(start),'rows':rr}
            plots.append(p);blocks[forest,tree,d,str(start)][arm].append(p);trees[forest,tree][d,arm].append(p)
        if len({p['plot'] for p in plots})!=56:raise ValueError('plot identity reused')
        if any(len(v['open'])!=len(v['exclosure']) or not v['open'] for v in blocks.values()):raise ValueError('unbalanced source-tree density start blocks')
        if any(set(v)!={(d,a) for d in (5,50) for a in ('open','exclosure')} for v in trees.values()):raise ValueError('incomplete four-arm source tree')
        # Terminal codes are checked after the structural gate. No time-to-event fit.
        for p in plots:
            rr=p.pop('rows')
            if any(n(r['SURV']) not in (0,1) or str(r['STAGE']).strip() not in ('germinated','intact','seedling','ungerminated') for r in rr):raise ValueError('terminal fate code invalid')
            p.update(metric(rr))
            p['censor_dates']=sorted({str(date(r['STOP'])) for r in rr if n(r['SURV'])==0})
            p['last_death_date']=max((str(date(r['STOP'])) for r in rr if n(r['SURV'])==1),default=None)
        # Full accounting by forest, density-distance and treatment, no selected plots.
        contexts=[]
        for forest in ('Logged','Unlogged'):
            for d in (5,50):
                for arm in ('open','exclosure'):
                    ps=[p for p in plots if (p['forest'],p['density'],p['arm'])==(forest,d,arm)]
                    if len(ps)!=7:raise ValueError('context replicate count drift')
                    c={'forest':forest,'density':d,'distance':2 if d==5 else 32,'arm':arm,'plots':len(ps),'N':sum(p['N'] for p in ps),
                        'terminal_alive':sum(p['terminal_alive'] for p in ps),'terminal_alive_seedling':sum(p['terminal_alive_seedling'] for p in ps),
                        'ever_seedling_recorded':sum(p['ever_seedling_recorded'] for p in ps),
                        'censor_dates':sorted({x for p in ps for x in p['censor_dates']})}
                    c['alive_fraction']=c['terminal_alive']/c['N'];c['alive_seedling_fraction']=c['terminal_alive_seedling']/c['N']
                    c['alive_per_m2']=c['terminal_alive']/c['plots'];c['alive_seedling_per_m2']=c['terminal_alive_seedling']/c['plots']
                    contexts.append(c)
        assert sum(c['N'] for c in contexts)==1540
        out['all_context_terminal_counts']=contexts
        # Match final census within each pair block. A block with no survivors
        # has no source final-censor date; do not invent that date.
        time_issues=C.Counter();spans=[]
        for k,v in blocks.items():
            ps=v['open']+v['exclosure'];dates={x for p in ps for x in p['censor_dates']}
            if len(dates)!=1:
                time_issues['block_final_censor_date_not_unique_or_absent']+=1;continue
            end=next(iter(dates))
            if any(p['last_death_date'] and p['last_death_date']>end for p in ps):time_issues['death_after_block_censor_date']+=1;continue
            spans.append((date(end)-date(k[3])).days)
        out['paired_block_support']={'source_tree_blocks':len(blocks),'time_matched_blocks':len(spans),'time_issues':dict(time_issues),'matched_duration_range':[min(spans),max(spans)] if spans else None,'source_trees':len(trees)}
        if time_issues:
            out['status']='TERMINAL_COUNTS_ONLY_PAIRED_TIMING_STOP'
        else:
            # Tree-level summary, all blocks, equal tree weights per forest.
            contrasts=[]
            for forest in ('Logged','Unlogged'):
                ts=[v for (f,t),v in trees.items() if f==forest]
                for d in (5,50):
                    for endpoint in ('terminal_alive','terminal_alive_seedling'):
                        diffs=[average(v[d,'exclosure'],endpoint)-average(v[d,'open'],endpoint) for v in ts]
                        contrasts.append({'forest':forest,'density':d,'endpoint':endpoint,'trees':len(ts),'mean_exclosure_minus_open_per_m2':mean(diffs),'mean_exclosure_minus_open_fraction':mean(diffs)/d,'trees_positive':sum(x>0 for x in diffs),'trees_negative':sum(x<0 for x in diffs),'trees_tied':sum(x==0 for x in diffs)})
            out['within_context_exclosure_contrasts']=contrasts
            # No density causal effect: only compare contexts with the same
            # source-tree start and terminal dates across all four arms.
            crossissues=0
            for v in trees.values():
                ps=[p for q in v.values() for p in q]
                if len({p['start'] for p in ps})!=1 or len({d for p in ps for d in p['censor_dates']})!=1:crossissues+=1
            out['cross_context_time_mismatch_trees']=crossissues
            if not crossissues:
                cross=[]
                for forest in ('Logged','Unlogged'):
                    ts=[v for (f,t),v in trees.items() if f==forest]
                    for arm in ('open','exclosure'):
                        for endpoint in ('terminal_alive','terminal_alive_seedling'):
                            low=[average(v[5,arm],endpoint) for v in ts];high=[average(v[50,arm],endpoint) for v in ts]
                            a,b=mean(low),mean(high)
                            cross.append({'forest':forest,'arm':arm,'endpoint':endpoint,'trees':len(ts),'low_context_count_per_m2':a,'high_context_count_per_m2':b,'low_fraction':a/5,'high_fraction':b/50,'count_difference':b-a,'fraction_difference':b/50-a/5,'trees_count_up_rate_down':sum(y>x and y/50<x/5 for x,y in zip(low,high))})
                out['density_distance_context_comparison']=cross
            out['status']='TERMINAL_PAIRED_CONTEXT_DESCRIPTIVE'
        out['strict_30d_status']='STOP_AGE_DATE_MISMATCH_UNRESOLVED'
        out['interpretation']='Treatment comparisons within matched contexts concern recorded terminal fate and exclusion of vertebrates (and potential cage effects), not taxon-specific predation or dispersal. No causal density-distance contrast. No cross-season or geographic inference.'
    except Exception as e:out.update(status='STOP_SOURCE_OR_SUPPORT',reason=type(e).__name__+': '+str(e)[:300])
    pathlib.Path('pillay_terminal_v19b.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
