"""Gu v2 source support only. No fate distributions or effect estimates.
Read verified workbook note and date/identity support. Do not run author code.
"""
import collections as C, datetime as dt, hashlib, io, json, pathlib, re, urllib.request, zipfile
import xml.etree.ElementTree as ET
FILES={'workbook':(56869019,51056,'d6fca6133f60fdd0971557f8ab4c9b7e'),'readme':(57701638,1413,'da65fb22331ee45f1bb7d50feec1002b')}
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def fetch(k):
    fid,n,d=FILES[k]
    with urllib.request.urlopen('https://api.figshare.com/v2/file/download/'+str(fid),timeout=20) as r:
        b=r.read(n+1)
    if len(b)!=n or hashlib.md5(b).hexdigest()!=d: raise ValueError(k+' checksum mismatch')
    return b
def worksheets(b):
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        ss=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            ss=[''.join(x.text or '' for x in r.findall('.//m:t',NS)) for r in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS)]
        result=[]
        for i in (1,2,3):
            rows=[]
            for r in ET.fromstring(z.read('xl/worksheets/sheet%d.xml'%i)).findall('.//m:sheetData/m:row',NS):
                row={}
                for c in r.findall('m:c',NS):
                    v=c.findtext('m:v',default='',namespaces=NS)
                    typ=c.attrib.get('t')
                    if typ=='s': v=ss[int(v)]
                    elif typ=='inlineStr': v=''.join(t.text or '' for t in c.findall('.//m:t',NS))
                    row[re.match('[A-Z]+',c.attrib['r']).group()]=v.strip()
                rows.append(row)
            result.append(rows)
        return result
def date(v):
    if not v or v.strip().lower() in {'na','nan','-','/','none','null'}: return None
    try:
        x=float(v)
        if 42000<=x<=46000:
            return (dt.datetime(1899,12,30)+dt.timedelta(days=x)).date()
    except ValueError: pass
    for f in ('%Y-%m-%d','%Y/%m/%d','%m/%d/%Y','%Y.%m.%d','%Y-%m-%d %H:%M:%S','%m/%d/%y'):
        try: return dt.datetime.strptime(v,f).date()
        except ValueError: pass
    return None
def main():
    out={'status':'SOURCE_SUPPORT_ONLY','effect_opened':False,
         'source_doi':'10.6084/m9.figshare.29815622.v2'}
    try:
        b=fetch('workbook'); readme=fetch('readme').decode('utf-8-sig',errors='replace')
        a,s,n=worksheets(b)
        out['readme']=readme
        out['note_rows']=n
        out['header']=a[0]
        assert a[0].get('A')=='Code' and a[0].get('D')=='Date of first dispersal' and a[0].get('G')=='Dispersers'
        rows=[r for r in a[1:] if r.get('A') and r.get('B')]
        out['candidate_seed_rows']=len(rows)
        out['unique_seed_codes']=len({r['A'] for r in rows})
        out['plant_taxon_levels']=dict(C.Counter(r['B'] for r in rows))
        for c,key in [('D','first_event'),('E','second_event')]:
            vals=[r.get(c,'') for r in rows]
            ds=[date(v) for v in vals]
            out[key+'_date_support']={'nonempty':sum(bool(v) for v in vals),'parsed':sum(d is not None for d in ds),
                 'unparsed_nonempty':sum(bool(v) and d is None for v,d in zip(vals,ds)),
                 'by_month':dict(C.Counter(d.strftime('%Y-%m') for d in ds if d is not None))}
        both=[(date(r.get('D','')),date(r.get('E',''))) for r in rows]
        out['paired_date_support']={'both_parsed':sum(a is not None and b is not None for a,b in both),
          'reverse_chronology':sum(a is not None and b is not None and b<a for a,b in both)}
        # Identifier shape only, no individual labels or fate outcomes.
        g=[r.get('G','') for r in rows]
        out['disperser_field_support']={'nonempty':sum(bool(v) for v in g),'unique_nonempty_strings':len({v for v in g if v}),
          'contains_dash':sum('-' in v for v in g),'contains_semicolon':sum(';' in v for v in g),
          'contains_slash':sum('/' in v for v in g),'contains_comma':sum(',' in v or '，' in v for v in g)}
        out['rodent_survey_rows']=len([r for r in s[1:] if r.get('A') and r.get('B')])
        out['release_date_header_present']=any('release' in v.lower() or 'placement date' in v.lower() for v in a[0].values())
        out['seasonal_release_contrast']='STOP_NO_RELEASE_DATE_COLUMN' if not out['release_date_header_present'] else 'REQUIRES_CODEBOOK'
    except (OSError,ValueError,KeyError,AssertionError,zipfile.BadZipFile) as e: out.update(status='STOP_SOURCE',reason=str(e)[:300])
    pathlib.Path('gu_source_support.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(out,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
