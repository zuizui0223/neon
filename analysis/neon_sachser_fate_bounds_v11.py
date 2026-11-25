"""V11: exact S5 year/fate/position count analysis after source-only inventory.
No individual seed history inferred. Exclude 2012 (aggregate endpoint) and 2019
(sterilized commercial seeds) from primary viable-seed cohort contrast.
"""
import collections as C, hashlib,io,itertools,json,math,pathlib,re,zipfile
import xml.etree.ElementTree as ET
from audit_neon_sachser_source_v11 import read,LIMIT
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
PIN={2:(51278310,18660,'639f323576320fd7b2f273435f4154c5'),
     3:(51278301,24307,'1f5ea0b8dbe58ff07cac90e3799d1d25'),
     4:(51278316,16132,'bd9ea9761993da045fd935e0c8960582'),
     5:(51278298,20710,'1b87c72edf9784097218c59b2816e7c4'),
     7:(51278304,16970,'e459a0d544a074ca0e95d87ab5f66d27'),
     9:(51278289,14377,'59dba39430ace93777d37b1171473fcd')}
def document(k):
    f,n,d=PIN[k];b=read(f'https://api.figshare.com/v2/file/download/{f}',LIMIT)
    if len(b)!=n or hashlib.md5(b).hexdigest()!=d:raise ValueError('source mismatch S'+str(k))
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        root=ET.fromstring(z.read('word/document.xml'))
    def txt(e):return ''.join(t.text or '' for t in e.findall('.//w:t',NS)).strip()
    paras=[txt(p) for p in root.findall('w:body/w:p',NS) if txt(p)]
    tables=[[[txt(c) for c in r.findall('w:tc',NS)] for r in t.findall('w:tr',NS)] for t in root.findall('.//w:tbl',NS)]
    return paras,tables
def norm(s):return re.sub(r'[^a-z]','',s.casefold())
def calculate(n,d,i,gd,gi,m):
    assert d+i+m==n and 0<=gd<=d and 0<=gi<=i
    # Assign every unresolved final fate to either location category, then any germination status.
    # These are worst-case arithmetic bounds for the stated documented categories, not sampling CIs.
    rdiff=[]; cdiff=[]
    for x in range(m+1):
        if d+x and i+m-x:
            rdiff.extend([(gd)/(d+x)-(gi+m-x)/(i+m-x),(gd+x)/(d+x)-gi/(i+m-x)])
        cdiff.extend([(gd-gi-(m-x))/n,(gd+x-gi)/n])
    return {'N':n,'located_ex_situ':d,'located_in_situ':i,'unresolved':m,
       'observed_ex_situ_germinated':gd,'observed_in_situ_germinated':gi,
       'ex_situ_germination_per_release_bound':[gd/n,(gd+m)/n],
       'in_situ_germination_per_release_bound':[gi/n,(gi+m)/n],
       'ex_minus_in_germination_per_release_bound':[min(cdiff),max(cdiff)],
       'ex_minus_in_conditional_germination_bound':[min(rdiff),max(rdiff)] if rdiff else None,
       'unresolved_ex_situ_germinants_needed_to_equal_observed_in_situ':max(0,gi-gd),
       'cannot_equal_observed_in_situ_even_if_all_missing_germinated_ex_situ':gd+m<gi}
def main():
    out={'status':'STOP','source':'10.6084/m9.figshare.28054281.v1',
         'scope':'published aggregate year x location x fate counts, not newly retrieved individual records; no causal or seasonal replication',
         'primary':'2018/19 and 2020/21 separate viable field-collected seed trials; 2012 and 2019 retained only for aggregate provenance.',
         'assumptions':'Every missing fate may belong to either location and germinate or not. Observed nonmissing location and fate labels treated as valid. In situ is documented position, not proof of never moved. No statistical intervals.'}
    try:
        docs={k:document(k) for k in PIN}
        out['S5_codebook']=docs[5][0]
        out['S4_seed_source_excerpt']=docs[4][0]
        out['S9_legacy_excerpt']=docs[9][0]
        t=docs[5][1][0];assert t[0]==['TRIAL','FATE','INEXSITU','NTOTAL','N']
        out['literal_levels']={k:sorted({r[j] for r in t[1:]}) for j,k in enumerate(t[0][:3])}
        # Explicitly match meanings only from labels. Stop if unexpected, no inferred counts.
        fates={'predated':'predated','missing':'missing','intact':'intact','germinated':'germinated'}
        locs={'in':'in','ex':'ex'} # Literal source S5 labels verified by first parser stop
        rows=C.defaultdict(dict);nt={}
        for r in t[1:]:
            if len(r)!=5:raise ValueError('row width')
            trial,f,l,total,n=r
            if norm(f) not in fates or norm(l) not in locs:raise ValueError('unexpected source labels '+str((f,l)))
            k=(fates[norm(f)],locs[norm(l)])
            if k in rows[trial]:raise ValueError('duplicate year/fate/position key')
            if trial in nt and nt[trial]!=int(total):raise ValueError('release count mismatch')
            nt[trial]=int(total);rows[trial][k]=int(n)
        assert len(rows)==4 and all(len(v)==8 for v in rows.values())
        assert all(sum(v.values())==nt[t] for t,v in rows.items()) and sum(nt.values())==639
        assert sum(v['missing','in']+v['missing','ex'] for v in rows.values())==103
        out['cohorts']={}
        for trial,v in rows.items():
            n=nt[trial];d=sum(v[f,'ex'] for f in fates if f!='missing');i=sum(v[f,'in'] for f in fates if f!='missing')
            gd=v['germinated','ex'];gi=v['germinated','in'];m=n-d-i
            assert gd==0
            q=calculate(n,d,i,gd,gi,m)
            q.update(recorded_ex_situ_including_missing=sum(v[f,'ex'] for f in fates),
                reported_position_counts={l:{f:v[f,l] for f in fates} for l in ('in','ex')})
            out['cohorts'][trial]=q
        primary=[v for t,v in out['cohorts'].items() if re.search(r'2018|2020',t)]
        if len(primary)!=2:raise ValueError('primary trial labels not recognized')
        out['primary_total_descriptive']=calculate(*[sum(v[k] for v in primary) for k in ('N','located_ex_situ','located_in_situ','observed_ex_situ_germinated','observed_in_situ_germinated','unresolved')])
        out['primary_total_descriptive']['warning']='Cohort counts added only for accounting; no independent sample pooling or rate inference.'
        out['resource_source_support']={'S2_summary_rows':len(docs[2][1][0])-1,'S3_capture_rows':len(docs[3][1][0])-1,'S7_germination_test_rows':len(docs[7][1][0])-1,'joined_seed_level_data':False}
        out['status']='V11_AGGREGATE_MISSING_FATE_BOUNDS'
    except Exception as e:out.update(status='STOP_SOURCE_OR_SUPPORT',reason=type(e).__name__+': '+str(e)[:300])
    pathlib.Path('sachser_fate_v11.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
