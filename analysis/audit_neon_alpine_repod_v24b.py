"""V24b: official author deposits at RePOD, not an OSF access workaround.
Separate public data citations from the original paper; no outcome fit.
"""
import csv,hashlib,io,json,pathlib,re,urllib.request,urllib.parse
BASE='https://repod.icm.edu.pl'
TARGETS={'tracking':'doi:10.18150/OPN782','capture':'doi:10.18150/N2LI79'}
CAP=8_000_000
def read(url,cap=CAP):
    if urllib.parse.urlparse(url).scheme!='https':raise ValueError('non HTTPS')
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'NEON research source inventory/1.0','Accept':'*/*'}),timeout=25) as r:b=r.read(cap+1)
    if len(b)>cap:raise ValueError('size limit')
    return b
def api(url):return json.loads(read(url))
def dataset(doi):
    u=BASE+'/api/datasets/:persistentId/?'+urllib.parse.urlencode({'persistentId':doi})
    d=api(u)['data']
    v=d['latestVersion']
    if d['persistentUrl'].lower().split('doi.org/')[-1]!=doi[4:].lower():raise ValueError('DOI mismatch')
    return v
def inspect(role,doi):
    out={'doi':doi,'status':'STOP_SOURCE','effect_opened':False}
    try:
        v=dataset(doi)
        out['version']=[v['versionNumber'],v['versionMinorNumber']]
        citation=v['metadataBlocks']['citation']['fields']
        out['title']=next(x['value'] for x in citation if x['typeName']=='title')
        out['files']=[]
        for f in v['files']:
            d=f['dataFile']
            z={k:d.get(k) for k in ('id','filename','filesize','contentType','checksum','originalFileName','originalFileFormat','originalFileSize')}
            z['restricted']=f.get('restricted',False);out['files'].append(z)
        # Dataverse converted tabular data has provider-defined .tab and
        # may offer an original CSV download. Check downloaded bytes against
        # metadata for the stored representation; never guess a checksum.
        candidates=[f for f in out['files'] if f['filename'].endswith('_1.tab') and not f['restricted']]
        if len(candidates)!=1:raise ValueError('public csv-derived table identity not unique')
        f=candidates[0];u=BASE+'/api/access/datafile/'+str(f['id'])
        b=read(u)
        alg=f['checksum']['type'].lower().replace('-','')
        actual=hashlib.new(alg,b).hexdigest()
        if len(b)!=f['filesize'] or actual!=f['checksum']['value']:raise ValueError('table representation checksum or size mismatch')
        rr=list(csv.reader(io.StringIO(b.decode('utf-8-sig'),newline=''),delimiter='\t'))
        h=[x.strip() for x in rr[0]]
        if len(set(h))!=len(h) or not all(len(x)==len(h) for x in rr[1:]):raise ValueError('tabular schema')
        out.update(status='VERIFIED_TABLE_SCHEMA',sha256=hashlib.sha256(b).hexdigest(),table_file=f['filename'],header=h,rows=len(rr)-1)
        if len(rr)-1!={'tracking':2400,'capture':1118}[role]:raise ValueError('row count differs from advertised')
        # No outcome counts opened. Report literal context keys only.
        out['context']=[{'name':k,'distinct':len(vals),'labels':sorted(vals) if len(vals)<=30 else None} for i,k in enumerate(h) if re.fullmatch(r'year|site|altitude|elevation|date|day|month|session|plot|transect|species',k,re.I) for vals in [{x[i] for x in rr[1:]}]]
    except Exception as e:out.update(status='STOP_SOURCE_OR_SCHEMA',reason=type(e).__name__+': '+str(e)[:250])
    return out
def main():
    out={'status':'SOURCE_GATE_ONLY','sources':{k:inspect(k,d) for k,d in TARGETS.items()},'early_to_emergence_prediction':'NOT_OPENED_NO_VERIFIED_EMERGENCE_SOURCE','boundary':'Original public author deposits, no individual match to separately measured emergence. Prior OSF 500 preserved. No further download retry on representation mismatch.'}
    p=pathlib.Path('build/neon_alpine_repod_v24b.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(json.dumps(out,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
