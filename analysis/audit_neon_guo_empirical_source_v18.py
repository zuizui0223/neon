"""V18: public source retrieval only. No seed fate counts opened.
Use Dryad's published landing page and advertised individual file link,
never invent a download URL or evade authentication.
"""
import hashlib,io,json,pathlib,re,urllib.request,urllib.parse,zipfile,xml.etree.ElementTree as ET
from html.parser import HTMLParser
DOI='10.5061/dryad.g79cnp64s'
BASE='https://datadryad.org'
LAND=BASE+'/dataset/doi:'+DOI
LIMIT=5_000_000
def read(url,accept):
    p=urllib.parse.urlparse(url)
    if p.scheme!='https':raise ValueError('non HTTPS source')
    r=urllib.request.Request(url,headers={'User-Agent':'NEON research source verification/1.0','Accept':accept})
    with urllib.request.urlopen(r,timeout=30) as f:
        b=f.read(LIMIT+1); mime=f.headers.get('Content-Type','')
    if len(b)>LIMIT:raise ValueError('source exceeds bounded size')
    return b,mime
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.cur=None
    def handle_starttag(self,tag,attrs):
        if tag=='a':
            self.cur=[dict(attrs),[]]
    def handle_data(self,d):
        if self.cur:self.cur[1].append(d)
    def handle_endtag(self,tag):
        if tag=='a' and self.cur:
            self.links.append((self.cur[0],''.join(self.cur[1]).strip()));self.cur=None
def schema(b):
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            sr=ET.fromstring(z.read('xl/sharedStrings.xml'))
            strings=[''.join(t.text or '' for t in a.findall('.//m:t',ns)) for a in sr.findall('m:si',ns)]
        wb=ET.fromstring(z.read('xl/workbook.xml'))
        out={'sheets':[e.attrib.get('name') for e in wb.findall('.//m:sheet',ns)],'tables':[]}
        for p in sorted(x for x in z.namelist() if re.fullmatch(r'xl/worksheets/sheet\d+\.xml',x)):
            rows=ET.fromstring(z.read(p)).findall('.//m:sheetData/m:row',ns)
            h=[]
            if rows:
                for c in rows[0].findall('m:c',ns):
                    v=c.findtext('m:v',default='',namespaces=ns)
                    if c.attrib.get('t')=='s':v=strings[int(v)]
                    elif c.attrib.get('t')=='inlineStr':v=''.join(e.text or '' for e in c.findall('.//m:t',ns))
                    h.append({'cell':c.attrib.get('r'),'header':v[:100]})
            out['tables'].append({'member':p,'rows':len(rows),'first_row':h})
    return out
def main():
    out={'status':'STOP','doi':DOI,'effect_opened':False}
    try:
        u=BASE+'/api/v2/datasets/'+urllib.parse.quote('doi:'+DOI,safe='')
        x=json.loads(read(u,'application/json')[0])
        if x.get('identifier','').lower()!='doi:'+DOI:raise ValueError('dataset identity')
        out['title']=x.get('title')
        v=json.loads(read(urllib.parse.urljoin(BASE,x['_links']['stash:version']['href']),'application/json')[0])
        fs=json.loads(read(urllib.parse.urljoin(BASE,v['_links']['stash:files']['href']),'application/json')[0])['_embedded']['stash:files']
        out['version']=v.get('versionNumber')
        out['files']=[{k:f.get(k) for k in ('path','size','digest','digestType')} for f in fs]
        candidates=[f for f in fs if f.get('path','').lower()=='data.xlsx']
        if len(candidates)!=1:raise ValueError('workbook identity')
        f=candidates[0]
        # The file API requires authentication; use the normal public UI only.
        html,mime=read(LAND,'text/html')
        if 'html' not in mime.lower():raise ValueError('not a public landing page')
        parser=Links();parser.feed(html.decode('utf-8','replace'))
        links=[]
        for attrs,label in parser.links:
            href=attrs.get('href','')
            if href and ('data.xlsx' in (label+' '+attrs.get('title','')+' '+attrs.get('download','')).lower()) and 'download' in href.lower():
                u=urllib.parse.urljoin(BASE,href)
                if urllib.parse.urlparse(u).hostname=='datadryad.org':links.append(u)
        links=sorted(set(links));out['public_workbook_links']=links
        if len(links)!=1:raise ValueError('no unique advertised workbook download link; do not guess')
        b,mime=read(links[0],'application/octet-stream, */*')
        if not b.startswith(b'PK'):raise ValueError('download not workbook: '+mime)
        algo=f['digestType'].lower().replace('-','')
        if len(b)!=int(f['size']) or hashlib.new(algo,b).hexdigest()!=f['digest']:raise ValueError('provider checksum mismatch')
        out.update(status='VERIFIED_PUBLIC_WORKBOOK',bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),schema=schema(b))
        pathlib.Path('guo_source_v18.xlsx').write_bytes(b)
    except Exception as e:out.update(status='STOP_SOURCE',reason=type(e).__name__+': '+str(e)[:250])
    pathlib.Path('guo_source_v18.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
