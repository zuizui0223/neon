"""V8: source identity diagnosis, no calendar-specific outcome counts.
Read published code as text; audit raw and curated source keys. No guessed corrections.
"""
import collections as C, json, pathlib, re
from audit_neon_merz_support_v7 import fetch, keys, present
from neon_merz_matched_stage_v7 import SK,FATE,integer
def main():
    a,s,m,v,code=[fetch(k) for k in ('all','station','mouse','vole','r')]
    stations={keys(r,SK):r for r in s if all(present(x) for x in keys(r,SK))}
    assert len(stations)==288 and len(a)==3243
    valid={k:r for k,r in stations.items() if r['Treatment'] in ('high density','low density') and integer(r['WP.seeds.set'])>0}
    cells=C.defaultdict(list)
    for k,r in valid.items(): cells[k[0],r['Treatment'],k[2]].append(k)
    shared=sorted({(g,t) for g,t,p in cells if all(len(cells.get((g,t,m),[]))>=2 for m in ('3','5'))})
    target={k for g,t in shared for p in ('3','5') for k in cells[g,t,p]}
    assert len(target)==159
    rows=[r for r in a if keys(r,SK) in target and r['Seed.SPP']=='WP' and r['Seed.Found..Y.N.']=='Y' and r[FATE] in ('D','E')]
    grouped=C.defaultdict(list)
    for r in rows:
        if present(r['Seed.ID']): grouped[keys(r,SK+['Seed.ID'])].append(r)
    multi=[rr for rr in grouped.values() if len(rr)>1]
    sig=['Species','PIT','Visit.ID','Timestamp.found',FATE]
    conflicts=[rr for rr in multi if len({keys(r,sig) for r in rr})>1]
    def count_changes(cols): return sum(len({keys(r,cols) for r in rr})>1 for rr in conflicts)
    out={'status':'SOURCE_IDENTITY_DIAGNOSTIC_ONLY','season_specific_effect_opened':False,'original_matched_nights':len(target),
       'terminal_rows':len(rows),'terminal_without_seed_id':sum(not present(r['Seed.ID']) for r in rows),
       'unique_seed_night_labels':len(grouped),'multirow_keys':len(multi),'conflicting_keys':len(conflicts),
       'conflicting_rows':sum(len(rr) for rr in conflicts),
       'conflicts_differing_in':{c:count_changes([c]) for c in ['Species','PIT','Visit.ID','Timestamp.found',FATE,'Date','Video','Cam','Time.start']},
       'conflicts_same_actor_and_fate':sum(len({keys(r,['Species',FATE]) for r in rr})==1 for rr in conflicts),
       'conflicting_id_shape_counts':dict(C.Counter('numeric' if re.fullmatch(r'\d+(\.\d+)?',rr[0]['Seed.ID']) else 'other' for rr in conflicts))}
    # Compare candidate accounting units to known physical disappearance, pooled across months.
    for add in ([],['Cam'],['Video'],['Visit.ID'],['Timestamp.found'],['Date','Cam']):
        counts=C.defaultdict(set)
        for r in rows:
            if present(r['Seed.ID']): counts[keys(r,SK)].add(keys(r,['Seed.ID']+add))
        out.setdefault('candidate_keys',[]).append({'additional':add,'unique_groups':sum(map(len,counts.values())),
            'nights_exceeding_field_disappearance':sum(len(counts[k])>integer(valid[k]['WP.seeds.set'])-integer(valid[k]['WP.seeds.left']) for k in target)})
    # Include recorded notes patterns (counts only) and author code context.
    out['conflicting_groups_note_flags']={p:sum(any(re.search(p,r.get('Notes',''),re.I) for r in rr) for rr in conflicts) for p in ['same','already','duplicate','different','camera','unknown','seed']}
    lines=code.splitlines()
    pat=re.compile(r'Seed_INFO|duplicat|distinct\(|unique\(|Visit.ID|Seed.ID|Timestamp.found',re.I)
    inds=set()
    for i,l in enumerate(lines):
        if pat.search(l):
            inds.update(range(max(0,i-1),min(len(lines),i+2)))
    out['author_code_excerpt']=[f'{i+1}: {lines[i][:250]}' for i in sorted(inds)][:100]
    # Count within-camera duplicates vs time-near paired records; no individual or raw row export.
    out['conflict_group_sizes']=dict(C.Counter(map(len,conflicts)))
    pathlib.Path('merz_seed_identity_diagnosis.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
