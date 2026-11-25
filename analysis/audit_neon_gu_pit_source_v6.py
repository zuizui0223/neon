"""One source inventory for Gu et al. (2025), Figshare 29815622 v2.
No effect estimates, row values, private data, or execution of deposited code.
"""
import csv, hashlib, io, json, pathlib, sys, urllib.request, urllib.error, zipfile
import xml.etree.ElementTree as ET
from pathlib import PurePosixPath

ARTICLE = 29815622
LIMIT = 20_000_000
def get(url, limit):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'NEON-seed-fate-source-audit/1.0'}), timeout=20) as r:
        b=r.read(limit+1)
    if len(b)>limit: raise ValueError('size limit')
    return b
def inspect(name, b):
    suffix=PurePosixPath(name).suffix.lower()
    if suffix in ('.csv','.tsv'):
        rows=csv.reader(io.StringIO(b.decode('utf-8-sig')), delimiter='\t' if suffix=='.tsv' else ',')
        header=next(rows,[])
        n=0; irregular=0
        for row in rows:
            if not row: continue
            n+=1; irregular+=len(row)!=len(header)
        return {'columns':header,'rows':n,'irregular_width':irregular}
    if suffix=='.zip':
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            return {'archive_members':[{'name':x.filename,'size':x.file_size} for x in z.infolist()[:200]]}
    if suffix=='.xlsx':
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            ss=[]
            if 'xl/sharedStrings.xml' in z.namelist():
                ss=[''.join(t.text or '' for t in si.findall('.//m:t',ns)) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)]
            sheets=[]
            wb=ET.fromstring(z.read('xl/workbook.xml'))
            names=[s.attrib.get('name') for s in wb.findall('.//m:sheet',ns)]
            for i,member in enumerate(sorted(x for x in z.namelist() if x.startswith('xl/worksheets/sheet') and x.endswith('.xml'))):
                rows=ET.fromstring(z.read(member)).findall('.//m:sheetData/m:row',ns)
                cols=[]
                for cell in rows[0].findall('m:c',ns) if rows else []:
                    v=cell.findtext('m:v',default='',namespaces=ns)
                    if cell.attrib.get('t')=='s': v=ss[int(v)]
                    elif cell.attrib.get('t')=='inlineStr': v=''.join(t.text or '' for t in cell.findall('.//m:t',ns))
                    cols.append({'cell':cell.attrib.get('r'),'header':v[:180]})
                sheets.append({'member':member,'header_cells':cols,'rows':len(rows)})
            return {'sheet_names':names,'sheets':sheets}
    return {'not_interpreted':True}
def main():
    receipt={'article':ARTICLE,'doi':'10.6084/m9.figshare.29815622','effect_opened':False,'files':[]}
    try:
        m=json.loads(get('https://api.figshare.com/v2/articles/'+str(ARTICLE)+'/versions/2',LIMIT))
        if m.get('id')!=ARTICLE or m.get('version')!=2: raise ValueError('article identity mismatch')
        receipt.update(title=m.get('title'),version=m.get('version'),license=m.get('license'),metadata_files=len(m.get('files',[])))
        if not m.get('files'): raise ValueError('no public files')
        for f in m['files']:
            info={k:f.get(k) for k in ('id','name','size','computed_md5','supplied_md5')}
            receipt['files'].append(info)
            if not (0<int(f['size'])<=LIMIT):
                info['status']='SKIP_SIZE'; continue
            try:
                b=get('https://api.figshare.com/v2/file/download/'+str(int(f['id'])),LIMIT)
                md5=hashlib.md5(b).hexdigest()
                info.update(bytes=len(b),observed_md5=md5,sha256=hashlib.sha256(b).hexdigest())
                if len(b)!=int(f['size']) or md5!=f.get('computed_md5'): raise ValueError('size or provider checksum mismatch')
                info.update(status='VERIFIED',schema=inspect(f['name'],b))
            except (OSError,ValueError,KeyError,UnicodeError,zipfile.BadZipFile) as e:
                info.update(status='STOP',error=str(e)[:250])
        receipt['status']='SOURCE_INVENTORY_ONLY' if any(f.get('status')=='VERIFIED' for f in receipt['files']) else 'STOP_NO_VERIFIED_FILES'
    except (OSError,ValueError,KeyError) as e:
        receipt.update(status='STOP_SOURCE_ACCESS',error=str(e)[:250])
    pathlib.Path('gu_source_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__': main()
