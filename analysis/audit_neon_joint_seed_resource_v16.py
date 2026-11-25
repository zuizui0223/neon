"""V16 source gate: no new fate model. Audit original linked resource and capture measurements."""
import collections as C,hashlib,io,json,pathlib,re,urllib.request,urllib.parse,zipfile,xml.etree.ElementTree as ET
from neon_sachser_fate_bounds_v11 import document
ROOT=pathlib.Path(__file__).resolve().parents[1]
DOI='10.5061/dryad.c030b'
LIMIT=20_000_000
def read(url):
    if not url.startswith('https://'):raise ValueError('non-HTTPS source')
    req=urllib.request.Request(url,headers={'User-Agent':'NEON seed resource source audit','Accept':'application/json, application/octet-stream, */*'})
    with urllib.request.urlopen(req,timeout=25) as r:
        b=r.read(LIMIT+1);mime=r.headers.get('Content-Type','')
    if len(b)>LIMIT:raise ValueError('size limit')
    return b,mime
def dryad():
    out={'doi':DOI,'status':'STOP','effect_opened':False}
    try:
        u='https://datadryad.org/api/v2/datasets/'+urllib.parse.quote('doi:'+DOI,safe='')
        x=json.loads(read(u)[0])
        if x.get('identifier','').lower()!='doi:'+DOI:raise ValueError('DOI mismatch')
        out['title']=x.get('title')
        rel=x['_links']['stash:version']['href']
        base='https://datadryad.org'
        v=json.loads(read(urllib.parse.urljoin(base,rel))[0])
        out['version']=v.get('versionNumber')
        fs=json.loads(read(urllib.parse.urljoin(base,v['_links']['stash:files']['href']))[0])
        files=fs['_embedded']['stash:files']
        out['files']=[{k:f.get(k) for k in ('path','size','digest','digestType')} for f in files]
        f=[f for f in files if str(f.get('path','')).lower().endswith('data.xlsx')]
        if len(f)!=1:raise ValueError('workbook identity ambiguous')
        f=f[0]
        link=urllib.parse.urljoin(base,f['_links']['stash:download']['href'])
        b,mime=read(link)
        if not b.startswith(b'PK'):raise ValueError('non-XLSX response '+mime)
        if int(f['size'])!=len(b):raise ValueError('size mismatch')
        algo=str(f['digestType']).lower().replace('-','')
        if algo not in ('md5','sha1','sha256','sha512'):raise ValueError('unknown checksum algorithm')
        if hashlib.new(algo,b).hexdigest()!=f['digest']:raise ValueError('provider checksum mismatch')
        ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            strings=[]
            if 'xl/sharedStrings.xml' in z.namelist():
                sr=ET.fromstring(z.read('xl/sharedStrings.xml'))
                strings=[''.join(t.text or '' for t in a.findall('.//m:t',ns)) for a in sr.findall('m:si',ns)]
            wb=ET.fromstring(z.read('xl/workbook.xml'))
            sheets=[e.attrib.get('name') for e in wb.findall('.//m:sheet',ns)]
            out['sheet_names']=sheets;out['schema']=[]
            for p in sorted(x for x in z.namelist() if re.fullmatch(r'xl/worksheets/sheet\d+\.xml',x)):
                rs=ET.fromstring(z.read(p)).findall('.//m:sheetData/m:row',ns)
                h=[]
                if rs:
                    for c in rs[0].findall('m:c',ns):
                        v=c.findtext('m:v',default='',namespaces=ns)
                        if c.attrib.get('t')=='s':v=strings[int(v)]
                        elif c.attrib.get('t')=='inlineStr':v=''.join(e.text or '' for e in c.findall('.//m:t',ns))
                        h.append({'cell':c.attrib.get('r'),'header':v[:150]})
                out['schema'].append({'member':p,'rows':len(rs),'first_row':h})
        out.update(status='WORKBOOK_VERIFIED',bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
    except Exception as e:out.update(status='STOP_SOURCE',reason=type(e).__name__+': '+str(e)[:250])
    return out
def sachser():
    out={'source':'10.6084/m9.figshare.c.7590246','status':'STOP','effect_opened':False}
    try:
        # Existing V11 document() validates pinned size+MD5 for each supplement.
        for k in (2,3,7):
            paras,tables=document(k)
            out['S'+str(k)]={'description':paras,'tables':tables}
        out['status']='RESOURCE_CAPTURE_SUMMARY_VERIFIED'
    except Exception as e:out.update(status='STOP_SOURCE',reason=type(e).__name__+': '+str(e)[:250])
    return out
def main():
    out={'schema':'neon.joint_seed_resource_source.v16','sachser':sachser(),'sunyer':dryad(),'no_new_fate_model':True}
    p=ROOT/'build/neon_joint_seed_resource_source_v16.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(out,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
