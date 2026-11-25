"""Diagnose incomplete station-night keys, source counts only. Do not open seasonal fate rates."""
import collections as C,json,pathlib
from audit_neon_merz_support_v7 import fetch,keys,present
from neon_merz_matched_stage_v7 import integer,SK
def main():
    out={'status':'SOURCE_DIAGNOSTIC_ONLY','effect_opened':False}
    try:
        a,s=fetch('all'),fetch('station')
        f=['WP.seeds.set','WP.seeds.left','RO.seeds.set','RO.seeds.left']
        valid=[]; invalid=[]
        for i,r in enumerate(s,2):
            k=keys(r,SK)
            if all(present(v) for v in k):
                valid.append(r)
            else:
                invalid.append({'csv_line':i,'nonempty_fields':{k:v for k,v in r.items() if present(v)},'n_present_key_fields':sum(present(v) for v in k)})
        out['invalid_rows']=invalid
        counts=C.Counter(keys(r,SK) for r in valid)
        out['valid_key_rows']=len(valid)
        out['valid_distinct_keys']=len(counts)
        out['duplicate_valid_keys']=sum(x-1 for x in counts.values())
        out['all_camera_rows_matching_valid_keys']=sum(keys(r,SK) in counts for r in a)
        out['valid_field_sums']={k:sum(integer(r[k]) or 0 for r in valid) for k in f}
        out['valid_missing_counts']={k:sum(integer(r[k]) is None for r in valid) for k in f}
        out['published_reconciliation']={'station_nights':len(valid)==288,
          'offered_WP':out['valid_field_sums'][f[0]]==4280,'offered_RO':out['valid_field_sums'][f[2]]==955,
          'disappeared_WP':out['valid_field_sums'][f[0]]-out['valid_field_sums'][f[1]]==2231,
          'disappeared_RO':out['valid_field_sums'][f[2]]-out['valid_field_sums'][f[3]]==350}
    except (OSError,ValueError,KeyError,TypeError) as e: out.update(status='STOP_DIAGNOSTIC',reason=str(e))
    pathlib.Path('merz_station_key_diagnosis.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__': main()
