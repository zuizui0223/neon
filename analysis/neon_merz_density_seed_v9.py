"""V9: density-stratified extension of opened V8, no independent replication.
Matched original 159 WP nights; both seed taxa field disappearance common endpoint.
For WP, enumerate original five ambiguous groups and verify original pooled H/Y.
No selection of direction or preferred scenario. RO D vs rejection is not WP D vs E.
"""
import collections as C,itertools,json,math,pathlib
from audit_neon_merz_support_v7 import fetch,keys,present
from neon_merz_matched_stage_v7 import SK,FATE,integer,split,G,PERIODS
from neon_merz_ambiguity_envelope_v8 import envelope
DENSITIES=('low density','high density')
ROOT=pathlib.Path(__file__).resolve().parents[1]
def status_sign(lo,hi):
    return 'POSITIVE' if lo>1e-10 else ('NEGATIVE' if hi< -1e-10 else 'UNRESOLVED')
def main():
    out={'status':'STOP','source':'10.6084/m9.figshare.28207769.v2',
         'analysis_status':'POST_V8_EXPLORATORY_MATCHED_COHORT_STRATIFICATION',
         'primary':'Compare high minus low density difference in Aug-Oct carriage change; positive means more positive change at high density. No directional prediction chosen from subgroup outcomes.',
         'secondary':'Compare red oak versus white pine fraction of offered seeds disappearing, on identical nights with both taxa offered. Disappearance is not confirmed carriage or consumption.',
         'density_semantics':'High/low treatment changes both offered seed species together; no independent natural resource or consumer density manipulation; no causal density effect inferred.'}
    try:
        a,s=fetch('all'),fetch('station')
        fs=['WP.seeds.set','WP.seeds.left','RO.seeds.set','RO.seeds.left']
        footer=[{k:v for k,v in r.items() if present(v)} for r in s if not all(present(v) for v in keys(r,SK))]
        assert footer==[{'WP.seeds.set':'4280','WP.seeds.left':'2049','RO.seeds.set':'955','RO.seeds.left':'605'},{'WP.seeds.set':'2231','RO.seeds.set':'350'},{'WP.seeds.set':'0.521261682','RO.seeds.set':'0.366492147'}]
        stations={keys(r,SK):r for r in s if all(present(v) for v in keys(r,SK))}
        assert len(stations)==288 and all(keys(r,SK) in stations for r in a)
        assert [sum(integer(r[k]) for r in stations.values()) for k in fs]==[4280,2049,955,605]
        valid={k:r for k,r in stations.items() if r['Treatment'] in DENSITIES and 0<=integer(r['WP.seeds.left'])<=integer(r['WP.seeds.set']) and integer(r['WP.seeds.set'])>0}
        cells=C.defaultdict(list)
        for k,r in valid.items(): cells[k[0],r['Treatment'],k[2]].append(k)
        shared=sorted({(g,t) for g,t,p in cells if all(len(cells.get((g,t,m),[]))>=2 for m in PERIODS)})
        grids=sorted({g for g,t in shared})
        target={k for g,t in shared for p in PERIODS for k in cells[g,t,p]}
        assert len(valid)==287 and len(grids)==4 and len(shared)==8 and len(target)==159
        assert all((g,t) in shared for g in grids for t in DENSITIES)
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
        cap={k:integer(valid[k]['WP.seeds.set'])-integer(valid[k]['WP.seeds.left']) for k in target}
        base=C.Counter(k for k,_ in fixed)
        assert all(base[k]<=cap[k] for k in target)
        weight={k:1/len(grids)/len(cells[g,t,p]) for g,t in shared for p in PERIODS for k in cells[g,t,p]}
        treatment={k:valid[k]['Treatment'] for k in target}
        assert all(math.isclose(sum(weight[k] for k in target if k[2]==p and treatment[k]==t),1) for p in PERIODS for t in DENSITIES)
        options=[[[],[(k,rr[0])],[(k,rr[1])],[(k,rr[0]),(k,rr[1])]] for k,rr in ambiguous]
        values=C.defaultdict(list); joint=C.defaultdict(list); pooled=C.defaultdict(list); rejected=0
        grid_signs=C.defaultdict(list)
        for choice in itertools.product(*options):
            extra=[item for group in choice for item in group]
            counts=base+C.Counter(k for k,_ in extra)
            if any(counts[k]>cap[k] for k in target): rejected+=1; continue
            rates={t:{p:{g:[0.,0.] for g in G} for p in PERIODS} for t in DENSITIES}
            by_grid={t:{p:{g:{actor:[0.,0.] for actor in G} for g in grids} for p in PERIODS} for t in DENSITIES}
            for k,(actor,f) in fixed+extra:
                if actor not in G: continue
                t=treatment[k]; p=k[2]; j=0 if f=='D' else 1
                rates[t][p][actor][j]+=weight[k]
                by_grid[t][p][k[0]][actor][j]+=weight[k]*len(grids)
            z={}
            for t in DENSITIES:
                v=split(rates[t]['3'],rates[t]['5'])
                if v['status']!='DESCRIPTIVE': raise ValueError('undefined density-specific allocation')
                h0,h1=v['handling_rates']; y0,y1=v['carriage_rates']; q0,q1=v['carriage_share']
                z[t]={'H0':h0,'H1':h1,'Y0':y0,'Y1':y1,'q0':q0,'q1':q1,'delta_H':h1-h0,'delta_Y':y1-y0,'delta_q':q1-q0,
                   'H_ratio':h1/h0 if h0 else None,'Y_ratio':y1/y0 if y0 else None,
                   'intensity':v['intensity_component'],'allocation':v['allocation_component'],
                   'composition_lo':v['composition_component_bounds'][0],'composition_hi':v['composition_component_bounds'][1],
                   'within_lo':v['within_taxon_component_bounds'][0],'within_hi':v['within_taxon_component_bounds'][1]}
                for k,x in z[t].items(): values[t,k].append(x)
            lo,hi=(z[t] for t in DENSITIES)
            for k in ('delta_H','delta_Y','delta_q','intensity','allocation','H_ratio','Y_ratio'):
                joint[k].append(hi[k]-lo[k] if hi[k] is not None and lo[k] is not None else None)
            joint['composition_min'].append(hi['composition_lo']-lo['composition_hi'])
            joint['composition_max'].append(hi['composition_hi']-lo['composition_lo'])
            joint['within_min'].append(hi['within_lo']-lo['within_hi'])
            joint['within_max'].append(hi['within_hi']-lo['within_lo'])
            for i,p in enumerate(PERIODS):
                pooled['H'+str(i)].append((lo['H'+str(i)]+hi['H'+str(i)])/2)
                pooled['Y'+str(i)].append((lo['Y'+str(i)]+hi['Y'+str(i)])/2)
            for g in grids:
                def y(t,p): return sum(v[0] for v in by_grid[t][p][g].values())
                x=(y('high density','5')-y('high density','3'))-(y('low density','5')-y('low density','3'))
                grid_signs[g].append(x)
        assert rejected==0 and len(joint['delta_Y'])==1024
        old=json.loads((ROOT/'results/neon_merz_ambiguity_envelope_v8_20261125.json').read_text())['metric_ranges']
        for k,x in pooled.items():
            assert all(math.isclose(i,j,abs_tol=1e-10) for i,j in zip(envelope(x),old[k]))
        out['V8_reproduction']='all four pooled H/Y endpoint ranges match to 1e-10'
        out['scenario_count']=1024
        out['night_counts']={t:{p:sum(len(cells[g,t,p]) for g in grids) for p in PERIODS} for t in DENSITIES}
        out['WP_by_density']={t:{k:envelope(x) for (tt,k),x in values.items() if t==tt} for t in DENSITIES}
        out['high_minus_low_change']={k:envelope(x) for k,x in joint.items()}
        out['grid_direction_support']={'positive_all_scenarios':sum(min(v)>1e-10 for v in grid_signs.values()),'negative_all_scenarios':sum(max(v)<-1e-10 for v in grid_signs.values()),'grids':len(grids)}
        # Separate common-denominator two-seed endpoint. Require exact same original
        # night cohort; no exclusion or rematching if red oak missing/not offered.
        if not all(0<=integer(valid[k]['RO.seeds.left'])<=integer(valid[k]['RO.seeds.set']) and integer(valid[k]['RO.seeds.set'])>0 for k in target):
            out['two_seed_field_endpoint']={'status':'STOP_NOT_BOTH_OFFERED_ON_ALL_ORIGINAL_NIGHTS'}
        else:
            f={}
            for t in DENSITIES:
                f[t]={}
                for p in PERIODS:
                    ks=[k for k in target if treatment[k]==t and k[2]==p]
                    f[t][p]={}
                    for seed in ('WP','RO'):
                        offered=sum(integer(valid[k][seed+'.seeds.set'])*weight[k] for k in ks)
                        lost=sum((integer(valid[k][seed+'.seeds.set'])-integer(valid[k][seed+'.seeds.left']))*weight[k] for k in ks)
                        f[t][p][seed]={'offered':offered,'disappeared':lost,'fraction':lost/offered}
            changes={t:{seed:f[t]['5'][seed]['fraction']-f[t]['3'][seed]['fraction'] for seed in ('WP','RO')} for t in DENSITIES}
            out['two_seed_field_endpoint']={'status':'DESCRIPTIVE','by_density_month':f,'changes':changes,
                'RO_minus_WP_change':{t:changes[t]['RO']-changes[t]['WP'] for t in DENSITIES},
                'equal_grid_weighting':'weighted disappearance divided by weighted offered, not mean nightly fraction'}
        out['decision']={'high_minus_low_carriage_change_sign':status_sign(*out['high_minus_low_change']['delta_Y']),
                         'claim_ceiling':'Descriptive context interaction under fixed V8 observation and ambiguity assumptions; no sampling CI, independent replication, natural resource causation or true dispersal.'}
        out['status']='V9_DESCRIPTIVE_COMPLETE'
    except (OSError,ValueError,KeyError,TypeError,AssertionError) as e: out.update(status='STOP_SOURCE_OR_SUPPORT',reason=type(e).__name__+': '+str(e)[:200])
    pathlib.Path('merz_density_seed_v9.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
