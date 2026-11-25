"""V10 support-only: link independently recorded captures to foraging sessions.
No September action counts or predictive scores opened.
"""
import collections as C, json, pathlib, re
from audit_neon_merz_support_v7 import fetch, keys, present, date
from neon_merz_matched_stage_v7 import SK,integer
def main():
    out={'status':'SOURCE_SUPPORT_ONLY','heldout_september_actions_opened':False,'source':'10.6084/m9.figshare.28207769.v2'}
    try:
        a,s,c,code=[fetch(k) for k in ('all','station','capture','r')]
        st={keys(r,SK):r for r in s if all(present(v) for v in keys(r,SK))}
        assert len(st)==288
        valid={k:r for k,r in st.items() if r['Treatment'] in ('high density','low density') and 0<=integer(r['WP.seeds.left'])<=integer(r['WP.seeds.set']) and integer(r['WP.seeds.set'])>0}
        cells=C.defaultdict(list)
        for k,r in valid.items(): cells[k[0],r['Treatment'],k[2]].append(k)
        shared=sorted({(g,t) for g,t,p in cells if all(len(cells.get((g,t,m),[]))>=2 for m in ('3','5'))})
        grids=sorted({g for g,t in shared})
        assert len(shared)==8 and len(grids)==4 and sum(len(cells[g,t,p]) for g,t in shared for p in ('3','5'))==159
        cap=[r for r in c if r['YEAR']=='23' and r['SESSION'] in ('3','4','5') and r['GRID'] in grids]
        out['capture_source_levels']={'grid':sorted({r['GRID'] for r in c if r['YEAR']=='23'}),'year23_dates_parsed':sum(date(r['DATE']) is not None for r in c if r['YEAR']=='23'),'year23_dates_rows':sum(r['YEAR']=='23' for r in c),'unparsed_date_literals':sorted({r['DATE'] for r in cap if date(r['DATE']) is None})[:15]}
        out['station_date_fields']={f:{'parsed':sum(date(r[f]) is not None for r in st.values()),'nonempty':sum(present(r[f]) for r in st.values()),'unparsed_literals':sorted({r[f] for r in st.values() if present(r[f]) and date(r[f]) is None})[:6]} for f in ('Date','Night.set','Morning.check')}
        cmap=C.defaultdict(set)
        for r in a:
            d=date(r['Date'])
            if d is not None: cmap[keys(r,SK)].add(d)
        ids=C.defaultdict(set); hist=C.defaultdict(set); dates=C.defaultdict(set)
        for r in cap:
            g,p=r['GRID'],r['SESSION']; d=date(r['DATE'])
            if d is not None: dates[g,p].add(d)
            if r['SPP2'] in ('PM','MG') and present(r['PIT']):
                ids[g,p,r['SPP2']].add(r['PIT']); hist[r['PIT']].add(r['SPP2'])
        out['focal_PIT_species_conflicts']=sum(len(v)>1 for v in hist.values())
        rows=[]
        for g in grids:
            for p in ('3','4','5'):
                ks=[k for t in ('low density','high density') for k in cells.get((g,t,p),[])]
                d0=[date(st[k]['Date']) for k in ks]
                camdates=[d for k in ks for d in cmap[k]]
                ds=dates[g,p]
                rows.append({'grid':g,'session':p,'capture_counts':{x:len(ids[g,p,x]) for x in ('PM','MG')},
                    'focal_capture_rows_missing_PIT':sum(r['GRID']==g and r['SESSION']==p and r['SPP2'] in ('PM','MG') and not present(r['PIT']) for r in cap),
                    'capture_date_min':str(min(ds)) if ds else None,'capture_date_max':str(max(ds)) if ds else None,
                    'capture_distinct_dates':len(ds),'capture_calendar_months':sorted({d.strftime('%Y-%m') for d in ds}),
                    'station_nights_by_density':{t:len(cells.get((g,t,p),[])) for t in ('low density','high density')},
                    'station_date_parsed':sum(x is not None for x in d0),'station_date_min':str(min(x for x in d0 if x is not None)) if any(x is not None for x in d0) else None,
                    'camera_date_min':str(min(camdates)) if camdates else None,
                    'all_capture_before_first_station_date':bool(ds and d0 and all(x is not None for x in d0) and max(ds)<=min(d0)),
                    'all_capture_before_first_camera_date':bool(ds and camdates and max(ds)<=min(camdates))})
        out['grid_session_support']=rows
        out['author_capture_code_excerpt']=[f'{i+1}: {x[:250]}' for i,x in enumerate(code.splitlines()[:55]) if x.strip()][:48]
        out['limitations']='Counts of unique captured IDs, not population density estimates; source lacks trap-night operability. Same capture session for both species; chronological date gate and original 3-night protocol required for prediction.'
    except (OSError,ValueError,KeyError,TypeError,AssertionError) as e: out.update(status='STOP_SOURCE',reason=type(e).__name__+': '+str(e)[:200])
    pathlib.Path('merz_capture_support_v10.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
