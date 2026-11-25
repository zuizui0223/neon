"""V19: verified Pillay source inventory and locked 30-day fate analysis.
Source: 10.5281/zenodo.2020340 (CC BY 4.0), DOI 10.1002/ece3.4352.
No new seed-trap-to-natural-recruit linkage inferred. No seasonal contrast.
"""
import collections as C,datetime as dt,hashlib,io,json,math,pathlib,urllib.request,urllib.parse
import openpyxl
RECORD=2020340
NAME='Pillay_R_et_al_Dryobalanops_lanceolata_AllData.xlsx'
MD5='4f5b6f4c58b43f488f43aab675562d9c'
LIMIT=2_000_000
OUT=pathlib.Path('pillay_source_v19.json')
def read(url):
    if urllib.parse.urlparse(url).scheme!='https':raise ValueError('invalid source URL')
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'NEON seed fate research/1.0'}),timeout=35) as r:b=r.read(LIMIT+1)
    if len(b)>LIMIT:raise ValueError('size limit')
    return b
def get():
    m=json.loads(read(f'https://zenodo.org/api/records/{RECORD}'))
    if m.get('id')!=RECORD or m.get('doi')!='10.5281/zenodo.2020340':raise ValueError('record identity')
    fs=[x for x in m['files'] if x.get('key')==NAME]
    if len(fs)!=1:raise ValueError('workbook identity')
    f=fs[0]
    if f.get('checksum')!='md5:'+MD5:raise ValueError('provider checksum metadata drift')
    b=read(f['links']['self'])
    if len(b)!=f['size'] or hashlib.md5(b).hexdigest()!=MD5:raise ValueError('workbook checksum mismatch')
    return b
def norm(v):
    return str(v or '').strip().casefold()
def parse(sheet,fields,expected):
    rows=list(sheet.values)
    hits=[i for i,r in enumerate(rows[:30]) if set(fields)<=set(str(v).strip() for v in r if v is not None)]
    if len(hits)!=1:raise ValueError('header not unique '+sheet.title)
    j=hits[0];h=[str(v).strip() if v is not None else '' for v in rows[j]]
    inds=[k for k,v in enumerate(h) if v]
    if len(set(h[k] for k in inds))!=len(inds):raise ValueError('duplicate header '+sheet.title)
    rr=[{h[k]:r[k] for k in inds} for r in rows[j+1:] if any(v is not None for v in r)]
    if len(rr)!=expected:raise ValueError('row count '+sheet.title+' '+str(len(rr)))
    return rr,h
def date(v):
    if isinstance(v,dt.datetime):return v.date()
    if isinstance(v,dt.date):return v
    if isinstance(v,str):
        for fmt in ('%Y-%m-%d','%d/%m/%Y','%d-%b-%Y'):
            try:return dt.datetime.strptime(v.strip(),fmt).date()
            except ValueError:pass
    return None
def n(v):
    if isinstance(v,bool):return None
    try:
        f=float(v);return int(f) if math.isfinite(f) and f==int(f) else None
    except (TypeError,ValueError,OverflowError):return None
def key(r):
    return tuple(str(r[k]).strip() for k in ('FTYPE','TREE.ID','TRANSECT','PLOT','DISTANCE','TRT','DENS.TRT'))
def main():
    out={'status':'STOP','source_doi':'10.5281/zenodo.2020340','effect_opened':False,'scope':'source-only support; no biological fate counts or treatment estimates'}
    try:
        b=get();out.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),provider_md5=MD5)
        w=openpyxl.load_workbook(io.BytesIO(b),read_only=True,data_only=True)
        out['sheets']=[{'name':z.title,'max_row':z.max_row,'max_column':z.max_column} for z in w.worksheets]
        specs=[
            ('TreeSize',['ftype','tree.id','Species'],13),
            ('SeedfallTrapByDist',['ftype','tree.id','transect','trap','distance','seeds'],312),
            ('NaturalPlotsSingleRec-Seed',['FTYPE','TREE.ID','TRANSECT','PLOT','DISTANCE','SEED.ID.ANALYSES','START','STOP','STAGE','SURV','AGE','GERM'],2069),
            ('ExclosureSingleRec-Seed',['FTYPE','TREE.ID','TRANSECT','PLOT','DISTANCE','SEED.ID','DENS.TRT','TRT','START','STOP','STAGE','SURV','AGE'],1540)]
        data={}
        out['tables']={}
        for sheet,fields,count in specs:
            r,h=parse(w[sheet],fields,count);data[sheet]=r;out['tables'][sheet]={'rows':len(r),'headers':h}
        e=data['ExclosureSingleRec-Seed'];a=data['NaturalPlotsSingleRec-Seed']
        out['exclosure_source_labels']={k:sorted({str(x[k]) for x in e}) for k in ('FTYPE','TRT','DENS.TRT','DISTANCE','STAGE','SURV')}
        out['natural_source_labels']={k:sorted({str(x[k]) for x in a}) for k in ('FTYPE','DISTANCE','STAGE','SURV','GERM')}
        # Labels above are only category vocabulary, not counts by fate.
        groups=C.defaultdict(list)
        for r in e:groups[key(r)].append(r)
        out['exclosure_group_support']=[{'forest':k[0],'tree':k[1],'transect':k[2],'plot':k[3],'distance':k[4],'treatment':k[5],'density':k[6],
            'rows':len(v),'unique_nonblank_seed_IDs':len({str(r['SEED.ID']).strip() for r in v if r['SEED.ID'] is not None and str(r['SEED.ID']).strip()}),
            'start_date_labels':sorted({str(date(r['START'])) for r in v})} for k,v in sorted(groups.items())]
        for label,rr in [('natural',a),('exclosure',e)]:
            both=[(date(x['START']),date(x['STOP']),n(x['AGE'])) for x in rr]
            out[label+'_chronology_support']={'start_unparsed':sum(x is None for x,y,z in both),'stop_unparsed':sum(y is None for x,y,z in both),'age_noninteger':sum(z is None for x,y,z in both),
                'negative_dates':sum(x is not None and y is not None and y<x for x,y,z in both),
                'age_disagrees_elapsed':sum(x is not None and y is not None and z is not None and z!=(y-x).days for x,y,z in both),
                'start_range':[min(x for x in (str(r[0]) for r in both) if x!='None'),max(x for x in (str(r[0]) for r in both) if x!='None')]}
        out['natural_plot_keys']=len({tuple(str(r[k]) for k in ('FTYPE','TREE.ID','TRANSECT','PLOT','DISTANCE')) for r in a})
        out['natural_unique_analysis_seed_IDs']=len({str(r['SEED.ID.ANALYSES']) for r in a})
        out['status']='VERIFIED_SOURCE_SUPPORT_ONLY'
    except Exception as e:out.update(status='STOP_SOURCE_OR_SCHEMA',reason=type(e).__name__+': '+str(e)[:300])
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
