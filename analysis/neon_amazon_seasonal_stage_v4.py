"""Haugaasen et al. (2010), doi:10.1017/S0266467410000027, Tables 1–2.
Published-aggregate descriptive calculations, not an individual data fit.
Initial burial refers only to recorded burial after movement from release station.
"""
import json
from math import isclose

N = 900
ROWS = {
    'wet': dict(table1=[637,38,14,12,32,7,77,11,28], total=856,
                primary_followup=[38,125,78,431,3], mean_days=38.7,
                monkey_percent=4.8),
    'dry': dict(table1=[244,75,37,4,68,77,53,0,81], total=639,
                primary_followup=[3,99,34,109,2], mean_days=11.3,
                monkey_percent=27.5),
}
# Table 2 relocated counts are not mutually exclusive with later fates:
# eaten, marker-only, unknown, still there sum to the primary cache count.

def calculate():
    by_season={}
    for s,r in ROWS.items():
        t=r['table1']; b=t[0]; second,eaten,marker,unknown,still=r['primary_followup']
        assert sum(t)==r['total'] and sum([eaten,marker,unknown,still])==b
        assert second<=b and N>=r['total']
        u=sum(t[4:7])+N-r['total']
        by_season[s]={'released':N,'table1_total':r['total'],'unlisted':N-r['total'],
          'unresolved_first_fate_upper_count':u,'recorded_primary_burial':b,
          'recorded_relocated_from_primary_burial':second,'primary_still_there':still,
          'confirmed_primary_burial_fraction':b/N,'primary_burial_bounds':[b/N,(b+u)/N],
          'recorded_relocation_per_release':second/N,'recorded_relocation_per_primary':second/b,
          'still_there_per_release':still/N,'still_there_per_primary':still/b,
          'mean_primary_cache_days_reported':r['mean_days'],'monkey_share_reported_pct':r['monkey_percent']}
    w,d=by_season['wet'],by_season['dry']
    bw,bd=w['recorded_primary_burial'],d['recorded_primary_burial']
    uw,ud=w['unresolved_first_fate_upper_count'],d['unresolved_first_fate_upper_count']
    gap=bw-bd
    sr=w['recorded_relocated_from_primary_burial']/d['recorded_relocated_from_primary_burial']
    pr=bw/bd
    cr=w['recorded_relocation_per_primary']/d['recorded_relocation_per_primary']
    assert isclose(sr,pr*cr)
    # If q_w=q_d, range across common q in [0,1]; no missing-at-random assumption claimed.
    eq=sorted([gap/N,(gap+uw-ud)/N])
    out={'status':'PUBLISHED_AGGREGATE_SENSITIVITY_ONLY','season':by_season,
      'primary_wet_minus_dry_unrestricted_bounds':[(gap-ud)/N,(gap+uw)/N],
      'primary_wet_minus_dry_equal_unknown_fraction_bounds':eq,
      'dry_unknown_fraction_to_tie_if_wet_unknown_zero':gap/ud,
      'wet_unknown_fraction_to_tie_if_all_dry_unknown_buried':(ud-gap)/uw,
      'primary_burial_wet_dry_ratio':pr,'recorded_relocation_wet_dry_ratio':sr,
      'conditional_recorded_relocation_wet_dry_ratio':cr,
      'recorded_relocation_wet_minus_dry':(w['recorded_relocated_from_primary_burial']-d['recorded_relocated_from_primary_burial'])/N,
      'primary_still_there_wet_dry_ratio':w['primary_still_there']/d['primary_still_there'],
      'monkey_share_dry_minus_wet_pp':d['monkey_share_reported_pct']-w['monkey_share_reported_pct']}
    assert isclose(out['primary_wet_minus_dry_unrestricted_bounds'][0],-66/900)
    assert isclose(eq[0],94/900)
    return out

if __name__=='__main__':
    print(json.dumps(calculate(), indent=2, sort_keys=True))
