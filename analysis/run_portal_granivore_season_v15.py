"""V15: Portal native monthly granivore seasonal composition forecast.
Post-NEON support STOP. One independent landscape, previously used source.
No claim of seed movement, actual diet or population abundance.
"""
import collections as C,json,math,pathlib
from statistics import mean
from analysis.portal_external_id_niche_source_v1 import SOURCE_COMMIT,get_source,csv_rows,i,stake
ROOT=pathlib.Path(__file__).resolve().parents[1]
FILES=['Rodents/Portal_rodent.csv','Rodents/Portal_rodent_trapping.csv','Rodents/Portal_rodent_species.csv','SiteandMethods/Portal_plots.csv']
MONTHS=(5,6,8,9)
PHASES=((5,6),(8,9))
TRAIN=range(1996,2020)
TEST=range(2020,2026)
def prob(x):
    n=sum(x.values());return {k:v/n for k,v in x.items()} if n else {}
def tv(a,b):
    return .5*sum(abs(a.get(k,0)-b.get(k,0)) for k in set(a)|set(b))
def pred(a,delta):
    return prob({k:max(0,a.get(k,0)+delta.get(k,0)) for k in set(a)|set(delta)})
def avg(xs):
    return {k:mean(x.get(k,0) for x in xs) for k in set().union(*xs)}
def main():
    out={'status':'STOP','source_commit':SOURCE_COMMIT,'design':'Portal source-defined granivorous census-target rodents, control plots, 1996-2019 training, 2020-2025 heldout calendar years. Same plots with exactly one sampled QC 48/49-trap positive-period session in each of May, June, August, September; each phase counts unique tagged individuals per session, weighted 49/effort; repeat capture in different months is a separate animal-session. No annual population estimates. At least 3 matched control plots, 20 valid target animal-sessions per phase, <=10% unresolved target capture rows. Fixed seasonal additive composition shift, compare with persistence and mean historical late composition; >=8 train years and >=4 test years. Mean equal-year TV gain and majority-year improvement. Previously used source, retrospective holdout, one desert landscape, no confirmatory evidence.'}
    try:
        raw={p:get_source(p) for p in FILES}
        ro,_=csv_rows(raw[FILES[0]],('plot','year','month','period','day','stake','species','id'))
        ef,_=csv_rows(raw[FILES[1]],('plot','year','month','period','day','sampled','effort','qcflag'))
        tx,_=csv_rows(raw[FILES[2]],('speciescode','scientificname','rodent','granivore','censustarget','unidentified'))
        tr,_=csv_rows(raw[FILES[3]],('plot','year','month','treatment','resourcetreatment','anttreatment'))
        taxa={}
        for r in tx:
            k=r['speciescode'].strip()
            if k in taxa:raise ValueError('duplicate taxon')
            taxa[k]=r
        target={k for k,r in taxa.items() if r['rodent']=='1' and r['granivore']=='1' and r['censustarget']=='1' and r['unidentified']=='0'}
        assert {'DM','PP'}<=target
        treatments={}
        for r in tr:
            k=tuple(i(r[x]) for x in ('plot','year','month'))
            if k in treatments:raise ValueError('duplicate plot treatment')
            treatments[k]=(r['treatment'].strip().lower(),r['resourcetreatment'],r['anttreatment'])
        sessions={}; monthly=C.defaultdict(list)
        for r in ef:
            p,y,m,period,day=(i(r[x]) for x in ('plot','year','month','period','day'))
            if None in (p,y,m,period,day) or y not in range(1996,2026) or m not in MONTHS or period<=0:continue
            t=treatments.get((p,y,m))
            if not t or t[0]!='control' or r['sampled']!='1' or r['qcflag']!='1' or i(r['effort']) not in (48,49):continue
            k=(p,y,m,period)
            if k in sessions:raise ValueError('duplicate effort key')
            sessions[k]=(day,i(r['effort']),t)
            monthly[p,y,m].append(k)
        pairs=C.defaultdict(list)
        for p,y,m in monthly:
            if m!=5:continue
            keys=[monthly.get((p,y,j),[]) for j in MONTHS]
            if not all(len(k)==1 for k in keys):continue
            ks=[k[0] for k in keys]
            # No within-year switches in recorded rodent/resource/ant treatment.
            if len({sessions[k][2] for k in ks})!=1:continue
            pairs[y].append(ks)
        needed={k for v in pairs.values() for ks in v for k in ks}
        obs=C.defaultdict(lambda:C.defaultdict(set)); bad=C.Counter(); total=C.Counter(); issues=C.Counter()
        for r in ro:
            k=tuple(i(r[x]) for x in ('plot','year','month','period'))
            if k not in needed:continue
            code=r['species'].strip()
            if code not in target:
                # Unidentified rodent records remain unresolved, not automatically target.
                if code not in taxa or (taxa[code]['rodent']=='1' and taxa[code]['unidentified']=='1'):
                    total[k]+=1;bad[k]+=1
                continue
            total[k]+=1
            tag=r['id'].strip();st=stake(r['stake'])
            if tag.lower() in ('','na','nan','null') or st is None or i(r['day'])!=sessions[k][0]:
                bad[k]+=1;continue
            obs[k][tag].add((code,st))
        counts=C.defaultdict(C.Counter)
        for k,ids in obs.items():
            for v in ids.values():
                if len(v)!=1:bad[k]+=len(v);continue
                code,st=next(iter(v));counts[k][code]+=1
        out['support']={'qualified_monthly_sessions':len(sessions),'candidate_matched_plot_years':sum(map(len,pairs.values())),
            'candidate_years':len(pairs),'source_target_granivore_species':len(target),'candidate_sessions':len(needed)}
        yr={}
        for y,plots in sorted(pairs.items()):
            if len(plots)<3:issues['too_few_matched_plots']+=1;continue
            totals=[]
            for js in ((0,1),(2,3)):
                ks=[p[j] for p in plots for j in js]
                n=sum(sum(counts[k].values()) for k in ks)
                u=sum(bad[k] for k in ks);raw_n=sum(total[k] for k in ks)
                if n<20 or u>.1*raw_n:break
                weighted=C.Counter()
                for k in ks:
                    for sp,v in counts[k].items():weighted[sp]+=v*49/sessions[k][1]
                totals.append((weighted,n,u))
            if len(totals)!=2:issues['low_count_or_unresolved']+=1;continue
            yr[y]={'early':prob(totals[0][0]),'late':prob(totals[1][0]),'plots':len(plots),'n':[z[1] for z in totals],'unresolved':[z[2] for z in totals]}
        trn=[y for y in TRAIN if y in yr];tst=[y for y in TEST if y in yr]
        out['support'].update(eligible_train_years=trn,eligible_test_years=tst,excluded_years=dict(issues),eligible_matched_plot_years=sum(v['plots'] for v in yr.values()))
        if len(trn)<8 or len(tst)<4:
            out['status']='STOP_TOO_FEW_YEARS'
        else:
            ds=[]
            for y in trn:
                a,b=yr[y]['early'],yr[y]['late']
                ds.append({k:b.get(k,0)-a.get(k,0) for k in set(a)|set(b)})
            delta=avg(ds);clim=avg([yr[y]['late'] for y in trn]);records=[]
            for y in tst:
                a,b=yr[y]['early'],yr[y]['late'];p=pred(a,delta)
                assert math.isclose(sum(p.values()),1,abs_tol=1e-10)
                rec={'year':y,'matched_plots':yr[y]['plots'],'tagged_animal_sessions':yr[y]['n'],'unresolved_capture_rows':yr[y]['unresolved'],'persistence_TV':tv(a,b),'seasonal_TV':tv(p,b),'historical_late_climatology_TV':tv(clim,b)}
                rec['gain_vs_persistence']=rec['persistence_TV']-rec['seasonal_TV']
                rec['gain_vs_climatology']=rec['historical_late_climatology_TV']-rec['seasonal_TV']
                records.append(rec)
            scores={k:mean(r[k] for r in records) for k in ('persistence_TV','seasonal_TV','historical_late_climatology_TV','gain_vs_persistence','gain_vs_climatology')}
            win=sum(r['gain_vs_persistence']>0 and r['gain_vs_climatology']>0 for r in records)
            out.update(status='DESCRIPTIVE_TEMPORAL_FORECAST',scores=scores,years=records,years_improving_both=win,
               meets_fixed_criterion=scores['gain_vs_persistence']>0 and scores['gain_vs_climatology']>0 and win>len(records)/2,
               historical_species_share_changes={taxa[k]['scientificname']:v for k,v in sorted(delta.items())})
        out['boundary']='No sampling CI, causal mechanism or independent geographic replication. One Portal landscape. Same-source earlier work means heldout years are not virgin source data. No seed fate or seed availability measured in this analysis. Changing plot membership across years is a limitation; same four sessions within year are matched. Invalid captures excluded not corrected; source-defined granivore label is not measured seed use.'
    except Exception as e:out.update(status='STOP_SOURCE_OR_ANALYSIS',reason=type(e).__name__+': '+str(e)[:250])
    path=ROOT/'build/portal_granivore_season_v15.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
