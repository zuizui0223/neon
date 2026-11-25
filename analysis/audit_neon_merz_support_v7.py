"""Merz v2 support audit. No seasonal fate rates or decomposition opened.
Read source labels, dates, identity support and join keys; do not execute author code.
"""
import csv, io, json, hashlib, math, pathlib, urllib.request, collections as C, datetime as dt, re

FILES={
 'all':(51682217,792575,'5f823a01c8751bd360dab723f3d49faa',3243),
 'station':(51682220,35432,'1cc4f0c66043c9a96955bed1c66408e3',291),
 'mouse':(51682229,278572,'63adc6b8f232e423fefc2d802d25904d',883),
 'vole':(51682232,313588,'e05cb082df82286672f49a39df4585b2',951),
 'capture':(51682214,1224945,'d9b8cd69378a98c520b10172b80f2c23',11614),
 'r':(51823913,68819,'b5f99bfd6b800cdecb435dfb23f6e6b9',None),
}
MISS={'','na','nan','n/a','null','none'}
def n(v): return str(v).strip().casefold()
def present(v): return n(v) not in MISS
def fetch(k):
    fid,size,md5,count=FILES[k]
    with urllib.request.urlopen('https://api.figshare.com/v2/file/download/'+str(fid),timeout=25) as r: b=r.read(size+1)
    if len(b)!=size or hashlib.md5(b).hexdigest()!=md5: raise ValueError('checksum '+k)
    s=b.decode('utf-8-sig')
    if count is None: return s
    rows=list(csv.DictReader(io.StringIO(s)))
    if len(rows)!=count: raise ValueError('count '+k)
    return rows
def date(v):
    v=v.strip()
    if not present(v): return None
    for f in ('%Y-%m-%d','%m/%d/%Y','%m/%d/%y','%Y/%m/%d','%d-%b-%Y','%d-%b-%y','%Y-%m-%d %H:%M:%S','%m/%d/%Y %H:%M:%S'):
        try: return dt.datetime.strptime(v,f).date()
        except ValueError: pass
    return None
def keys(r,fields): return tuple(r.get(k,'').strip() for k in fields)
def levels(rows,fields):
    return {f:sorted(set(r.get(f,'') for r in rows))[:50] for f in fields}
def main():
    out={'status':'SUPPORT_ONLY','seasonal_fate_effect_opened':False,'source':'10.6084/m9.figshare.28207769.v2'}
    try:
        data={k:fetch(k) for k in FILES}
        fields=['Session','Seed.SPP','Seed.Found..Y.N.','Eat..disperse..reject..or.move','Species','Treatment.x']
        out['literal_levels']={k:levels(data[k],fields) for k in ('all','mouse','vole')}
        out['station_levels']=levels(data['station'],['Session','Treatment','Grid_Month','Visitors?'])
        out['capture_levels']=levels(data['capture'],['YEAR','SESSION','SPP2'])
        sk=['Grid','Site','Session','Night']
        out['station_join']={}
        stat=C.Counter(keys(r,sk) for r in data['station'])
        out['station_keys']={'rows':len(data['station']),'distinct':len(stat),'duplicate_excess':sum(x-1 for x in stat.values())}
        for k in ('all','mouse','vole'):
            a=data[k]; ds=[date(r.get('Date','')) for r in a]
            out['station_join'][k]={'rows':len(a),'unmatched':sum(keys(r,sk) not in stat for r in a),'unparsed_date_nonblank':sum(d is None and present(r.get('Date','')) for d,r in zip(ds,a)),
              'calendar_months':sorted(set(d.strftime('%Y-%m') for d in ds if d is not None))}
            out['station_join'][k]['session_to_calendar']={s:sorted(set(d.strftime('%Y-%m') for r,d in zip(a,ds) if r['Session']==s and d is not None)) for s in sorted({r['Session'] for r in a})}
            # Effect-blind support for every found flag category (not conditional on fate).
            tab={}
            for flag in sorted({r['Seed.Found..Y.N.'] for r in a}):
                found=[r for r in a if r['Seed.Found..Y.N.']==flag and present(r['PIT'])]
                ids=C.defaultdict(set); grids=C.defaultdict(set)
                for r in found: ids[r['Session']].add(r['PIT']); grids[r['Session']].add(r['Grid'])
                tab[flag]={'known_PIT_rows':len(found),'unique_PIT':len({r['PIT'] for r in found}),
                   'by_session':{s:{'rows':sum(r['Session']==s for r in found),'unique_PIT':len(v),'grids':len(grids[s])} for s,v in ids.items()},
                   'pairwise_shared_PIT':{a+'|'+b:len(ids[a]&ids[b]) for a in sorted(ids) for b in sorted(ids) if a<b}}
            out.setdefault('known_actor_support_by_found_flag',{})[k]=tab
        # Compare raw and curated event identities, independent of fate.
        ev=sk+['Visit.ID','Video','PIT','Seed.SPP','Seed.ID','Timestamp.found']
        base=C.Counter(keys(r,ev) for r in data['all'])
        for k in ('mouse','vole'):
            sub=C.Counter(keys(r,ev) for r in data[k])
            out.setdefault('raw_curated_key_check',{})[k]={'distinct':len(sub),'excess_curated_rows':sum((sub-base).values()),'duplicate_excess':sum(x-1 for x in sub.values())}
        # Read code as text only, output small selection of literal filter statements relevant to seed labels.
        pattern=re.compile(r'(Seed\.SPP|Seed\.Found|Eat\.\.disperse|dispers.*==|filter\(|WP\.seeds\.set)',re.I)
        out['author_code_filter_lines']=[line.strip()[:300] for line in data['r'].splitlines() if pattern.search(line) and not line.strip().startswith('#')][:65]
    except (OSError,ValueError,KeyError,TypeError) as e: out.update(status='STOP_SOURCE',reason=str(e)[:300])
    pathlib.Path('merz_support.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
