"""V11: inventory source collection, pin files S2/S3/S4/S5/S7/S9.
Only schema and source provenance; no biological outcomes.
"""
import hashlib,json,pathlib,re
from audit_neon_sachser_source_v11 import read,schema,LIMIT
CID=7590246
def main():
    out={'status':'STOP','collection_doi':'10.6084/m9.figshare.c.7590246','effect_opened':False,'items':[]}
    try:
        m=json.loads(read(f'https://api.figshare.com/v2/collections/{CID}',LIMIT))
        assert m.get('id')==CID and 'Tracking individual seed fate' in m.get('title','')
        out['title']=m['title']
        aa=json.loads(read(f'https://api.figshare.com/v2/collections/{CID}/articles?page_size=100',LIMIT))
        assert isinstance(aa,list) and 0<len(aa)<100
        for a in aa:
            x=json.loads(read(f"https://api.figshare.com/v2/articles/{a['id']}",LIMIT))
            assert x['id']==a['id']
            rec={'id':x['id'],'doi':x.get('doi'),'version':x.get('version'),'files':[]};out['items'].append(rec)
            for f in x['files']:
                r={k:f.get(k) for k in ('id','name','size','computed_md5')};rec['files'].append(r)
                match=re.search(r'si_0*(\d+)\.',f['name'],re.I)
                if not match or int(match[1]) not in (2,3,4,5,7,9):continue
                try:
                    assert 0<int(f['size'])<=LIMIT
                    b=read(f"https://api.figshare.com/v2/file/download/{f['id']}",LIMIT)
                    assert len(b)==int(f['size']) and hashlib.md5(b).hexdigest()==f['computed_md5']
                    r.update(status='VERIFIED',supplement=int(match[1]),sha256=hashlib.sha256(b).hexdigest(),schema=schema(f['name'],b))
                except Exception as e:r.update(status='STOP',reason=str(e)[:200])
        out['verified_supplements']=sorted(r['supplement'] for x in out['items'] for r in x['files'] if r.get('status')=='VERIFIED')
        out['status']='S5_VERIFIED' if 5 in out['verified_supplements'] else 'STOP_NO_VERIFIED_S5'
    except Exception as e:out.update(status='STOP_COLLECTION',reason=type(e).__name__+': '+str(e)[:200])
    pathlib.Path('sachser_collection_v11.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
