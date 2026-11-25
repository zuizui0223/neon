"""V11. Author-linked beech seed fate supplement. Inventory only; no outcomes extracted.
Use public Figshare article ID confirmed by research output DOI, verify provider bytes.
"""
import csv,hashlib,io,json,pathlib,urllib.request,zipfile,xml.etree.ElementTree as ET
ARTICLE=28054287
LIMIT=25_000_000
def read(url,limit):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'NEON-source-audit/1.0'}),timeout=30) as r:
        b=r.read(limit+1)
    if len(b)>limit:raise ValueError('bounded size exceeded')
    return b
def schema(name,b):
    if name.lower().endswith('.csv'):
        r=csv.reader(io.StringIO(b.decode('utf-8-sig'))); h=next(r); return {'columns':h,'rows':sum(1 for x in r if x)}
    if name.lower().endswith('.xlsx'):
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            w=ET.fromstring(z.read('xl/workbook.xml'))
            return {'sheets':[x.attrib.get('name') for x in w.findall('.//s:sheet',ns)]}
    if name.lower().endswith('.docx'):
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            d=ET.fromstring(z.read('word/document.xml'))
            return {'tables':[{'n_rows':len(t.findall('w:tr',ns)),'header':[''.join(x.text or '' for x in cell.findall('.//w:t',ns)) for cell in t.findall('w:tr',ns)[0].findall('w:tc',ns)]} for t in d.findall('.//w:tbl',ns) if t.findall('w:tr',ns)]}
    if name.lower().endswith('.zip'):
        with zipfile.ZipFile(io.BytesIO(b)) as z:return {'members':[{'name':i.filename,'size':i.file_size} for i in z.infolist()[:200]]}
    return {'format':name.rsplit('.',1)[-1],'not_interpreted':True}
def main():
    out={'status':'STOP','source_doi':'10.6084/m9.figshare.28054287','paper_doi':'10.1098/rsbl.2024.0586','effect_opened':False,'files':[]}
    try:
        a=json.loads(read(f'https://api.figshare.com/v2/articles/{ARTICLE}',LIMIT))
        if a.get('id')!=ARTICLE or 'Tracking individual seed fate' not in a.get('title',''): raise ValueError('article identity')
        out.update(title=a['title'],version=a.get('version'),license=a.get('license'))
        for f in a['files']:
            r={k:f.get(k) for k in ('id','name','size','computed_md5','supplied_md5')};out['files'].append(r)
            try:
                if not 0<int(f['size'])<=LIMIT: raise ValueError('size gate')
                b=read(f"https://api.figshare.com/v2/file/download/{f['id']}",LIMIT)
                if len(b)!=int(f['size']) or hashlib.md5(b).hexdigest()!=f['computed_md5']:raise ValueError('provider checksum mismatch')
                r.update(status='VERIFIED',bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),schema=schema(f['name'],b))
            except (OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile,ET.ParseError) as e:r.update(status='STOP',reason=str(e)[:200])
        out['status']='VERIFIED_SOURCE_INVENTORY' if out['files'] and all(x['status']=='VERIFIED' for x in out['files']) else 'STOP_INCOMPLETE_SOURCE'
    except (OSError,ValueError,KeyError,TypeError) as e:out.update(status='STOP_SOURCE',reason=str(e)[:200])
    pathlib.Path('sachser_source_v11.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(out,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
