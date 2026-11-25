"""V8b: explicit ambiguity-envelope sensitivity; does not reverse V7 strict STOP.
Same 159 station-nights, WP, Aug/Oct, PM/MG, same grid x density weights.
No seasonal estimates seen before this design. Enumerate zero/one/both of five
ambiguous two-row groups; require observed physical disappearance cap.
All results conditional on accuracy of singleton terminal IDs and action labels.
"""
import collections as C,itertools,json,math,pathlib
from audit_neon_merz_support_v7 import fetch,keys,present
from neon_merz_matched_stage_v7 import SK,FATE,integer,split,G,PERIODS

def envelope(xs):
    xs=list(xs)
    if not xs or any(x is None for x in xs): return None
    return [min(xs),max(xs)]

def main():
    out={'status':'STOP','estimand':'SENSITIVITY_ONLY; recorded PM/MG WP terminal carriage and consumption per station-night',
         'frozen_V7_strict_status':'STOP_UNCHANGED','source_doi':'10.6084/m9.figshare.28207769.v2',
         'assumption':'Singleton terminal label/action records correctly identify distinct physical seeds. Every ambiguous group can contribute neither, either, or both records; no choice based on effects. Bounds address five identified groups, not arbitrary misclassification.',
         'decision_rule':'complete compensation if H1<H0 and Y1>=Y0 for every feasible scenario; partial if 0<Y1/Y0<1 and H1/H0<Y1/Y0 across every scenario; positive composition term only if its lower endpoint >0. No equivalence, CI, or causal test.'}
    try:
        a,s=fetch('all'),fetch('station')
        fs=['WP.seeds.set','WP.seeds.left','RO.seeds.set','RO.seeds.left']
        footer=[{k:v for k,v in r.items() if present(v)} for r in s if not all(present(v) for v in keys(r,SK))]
        assert footer==[{'WP.seeds.set':'4280','WP.seeds.left':'2049','RO.seeds.set':'955','RO.seeds.left':'605'},{'WP.seeds.set':'2231','RO.seeds.set':'350'},{'WP.seeds.set':'0.521261682','RO.seeds.set':'0.366492147'}]
        stations={keys(r,SK):r for r in s if all(present(v) for v in keys(r,SK))}
        assert len(stations)==288 and all(keys(r,SK) in stations for r in a)
        assert [sum(integer(r[k]) for r in stations.values()) for k in fs]==[4280,2049,955,605]
        valid={k:r for k,r in stations.items() if r['Treatment'] in ('high density','low density') and 0<=integer(r['WP.seeds.left'])<=integer(r['WP.seeds.set']) and integer(r['WP.seeds.set'])>0}
        cells=C.defaultdict(list)
        for k,r in valid.items(): cells[k[0],r['Treatment'],k[2]].append(k)
        shared=sorted({(g,t) for g,t,p in cells if all(len(cells.get((g,t,m),[]))>=2 for m in PERIODS)})
        grids=sorted({g for g,t in shared})
        target={k for g,t in shared for p in PERIODS for k in cells[g,t,p]}
        assert len(valid)==287 and len(grids)==4 and len(shared)==8 and len(target)==159
        assert {p:sum(k[2]==p for k in target) for p in PERIODS}=={'3':63,'5':96}
        groups=C.defaultdict(list)
        for r in a:
            k=keys(r,SK)
            if k in target and r['Seed.SPP']=='WP' and r['Seed.Found..Y.N.']=='Y' and r[FATE] in ('D','E'):
                assert present(r['Seed.ID'])
                groups[k+(r['Seed.ID'].strip(),)].append((r['Species'],r[FATE]))
        fixed=[(k[:-1],rr[0]) for k,rr in groups.items() if len(rr)==1]
        ambiguous=[(k[:-1],rr) for k,rr in groups.items() if len(rr)>1]
        assert len(groups)==557 and len(fixed)==552 and len(ambiguous)==5 and all(len(rr)==2 for k,rr in ambiguous)
        # Per-station-night physical cap is applied to all taxa, not only PM/MG.
        cap={k:integer(valid[k]['WP.seeds.set'])-integer(valid[k]['WP.seeds.left']) for k in target}
        base_counts=C.Counter(k for k,_ in fixed)
        assert all(base_counts[k]<=cap[k] for k in target)
        # Equal grid and equal matched density strata within grid. Include zero-event nights.
        weight={k:1/len(grids)/sum(gg==g for gg,tt in shared)/len(cells[g,t,p])
                for g,t in shared for p in PERIODS for k in cells[g,t,p]}
        assert all(math.isclose(sum(weight[k] for k in target if k[2]==p),1) for p in PERIODS)
        field={p:sum(cap[k]*weight[k] for k in target if k[2]==p) for p in PERIODS}
        offered={p:sum(integer(valid[k]['WP.seeds.set'])*weight[k] for k in target if k[2]==p) for p in PERIODS}
        options=[]
        for k,rr in ambiguous:
            options.append([[],[(k,rr[0])],[(k,rr[1])],[(k,rr[0]),(k,rr[1])]])
        scenarios=[]; rejected=0
        for choice in itertools.product(*options):
            extra=[item for group in choice for item in group]
            counts=base_counts+C.Counter(k for k,_ in extra)
            if any(counts[k]>cap[k] for k in target): rejected+=1; continue
            rates={p:{g:[0.,0.] for g in G} for p in PERIODS}
            raw={p:{g:[0,0] for g in G} for p in PERIODS}
            gr={p:{g:{a:[0.,0.] for a in G} for g in grids} for p in PERIODS}
            for k,(actor,f) in fixed+extra:
                if actor not in G: continue
                p=k[2]; j=0 if f=='D' else 1
                rates[p][actor][j]+=weight[k]; raw[p][actor][j]+=1
                gr[p][k[0]][actor][j]+=weight[k]*len(grids)
            z=split(rates['3'],rates['5'])
            if z['status']!='DESCRIPTIVE': raise ValueError('undefined focal allocation')
            h0,h1=z['handling_rates']; y0,y1=z['carriage_rates']; q0,q1=z['carriage_share']
            bounds={p:[z['carriage_rates'][i]/field[p],(z['carriage_rates'][i]+field[p]-z['handling_rates'][i])/field[p]] for i,p in enumerate(PERIODS)}
            assert all(-1e-10<=lo<=hi+1e-10<=1+1e-9 for lo,hi in bounds.values())
            metrics={'H0':h0,'H1':h1,'Y0':y0,'Y1':y1,'q0':q0,'q1':q1,'delta_H':h1-h0,'delta_Y':y1-y0,'delta_q':q1-q0,
               'H_ratio':h1/h0 if h0 else None,'Y_ratio':y1/y0 if y0 else None,
               'relative_attenuation_ratio_difference':y1/y0-h1/h0 if y0 and h0 else None,
               'intensity':z['intensity_component'],'allocation':z['allocation_component'],
               'composition_lo':z['composition_component_bounds'][0],'composition_hi':z['composition_component_bounds'][1],
               'within_lo':z['within_taxon_component_bounds'][0],'within_hi':z['within_taxon_component_bounds'][1],
               'all_disappearance_carriage_delta_lo':bounds['5'][0]-bounds['3'][1],
               'all_disappearance_carriage_delta_hi':bounds['5'][1]-bounds['3'][0],
               'Y_per_offer0':y0/offered['3'],'Y_per_offer1':y1/offered['5']}
            for p in PERIODS:
                for g in G:
                    for j,nm in enumerate(('D','E')):
                        metrics[f'raw_{p}_{g}_{nm}']=raw[p][g][j]
                        metrics[f'rate_{p}_{g}_{nm}']=rates[p][g][j]
            for g in grids:
                H=[sum(sum(v) for v in gr[p][g].values()) for p in PERIODS]
                Y=[sum(v[0] for v in gr[p][g].values()) for p in PERIODS]
                metrics['grid_H_decrease_'+g]=int(H[1]<H[0]-1e-12)
                metrics['grid_Y_non_decrease_'+g]=int(Y[1]>=Y[0]-1e-12)
            scenarios.append(metrics)
        assert len(scenarios)+rejected==1024 and scenarios
        env={k:envelope(x[k] for x in scenarios) for k in scenarios[0] if not k.startswith('grid_')}
        out.update(status='DESCRIPTIVE_AMBIGUITY_ENVELOPE',matched_nights={'3':63,'5':96},matched_grids=4,matched_cells=8,
          singleton_groups=len(fixed),ambiguous_groups=len(ambiguous),enumerated=1024,feasible=len(scenarios),rejected_cap=rejected,
          weighted_field_disappearance=field,weighted_offered=offered,metric_ranges=env,
          grid_direction_counts={k:envelope(sum(x[f'{k}_{g}'] for g in grids) for x in scenarios) for k in ('grid_H_decrease','grid_Y_non_decrease')})
        out['decision']={'complete_compensation_all':all(x['delta_H']<0 and x['delta_Y']>=-1e-12 for x in scenarios),
          'partial_attenuation_all':all(x['H_ratio'] is not None and x['Y_ratio'] is not None and x['H_ratio']<x['Y_ratio']<1 for x in scenarios),
          'composition_positive_all':all(x['composition_lo']>0 for x in scenarios),
          'composition_negative_all':all(x['composition_hi']<0 for x in scenarios),
          'all_disappearance_carriage_fraction_direction_identified':env['all_disappearance_carriage_delta_lo'][0]>0 or env['all_disappearance_carriage_delta_hi'][1]<0}
    except (OSError,ValueError,KeyError,TypeError,AssertionError) as e:
        out.update(status='STOP_SOURCE_OR_SUPPORT',reason=type(e).__name__+': '+str(e)[:200])
    pathlib.Path('merz_ambiguity_envelope.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
