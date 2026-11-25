"""Exploratory published-aggregate stage contrasts, 2026-11-25.
Run from repository root: python analysis/neon_seed_fate_stage_context_v2.py
No new fit, sampling CI, pooled meta-analysis, or causal inference.
"""
import json
from pathlib import Path
from math import isclose
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]

def split(n, r0, k0, r1, k1):
    assert 0 <= k0 <= r0 <= n and 0 <= k1 <= r1 <= n and min(r0, r1) > 0
    a, b, c, d = r0/n, r1/n, k0/r0, k1/r1
    movement = (b-a)*(c+d)/2
    conditional = (d-c)*(a+b)/2
    delta = (k1-k0)/n
    assert isclose(movement+conditional, delta, abs_tol=1e-12)
    return {k:100*v for k,v in {
        'removal_change_pp':b-a, 'conditional_recorded_cache_change_pp':d-c,
        'recorded_cache_change_pp':delta, 'removal_component_pp':movement,
        'conditional_component_pp':conditional}.items()}

def main():
    raw = json.loads((ROOT/'data/neon_lu2004_published_seasonal_release_counts_20261124.json').read_text())
    rows = {(r[0], r[1]): r[2:5] for r in raw['rows']}
    lu = {}
    for habitat in ('low','high'):
        n,r0,k0 = rows[habitat,'summer']
        n1,r1,k1 = rows[habitat,'autumn']
        # Source columns are released, removed, surface, hoarded: use index 5, not 4.
        a = next(r for r in raw['rows'] if r[:2]==[habitat,'summer'])
        b = next(r for r in raw['rows'] if r[:2]==[habitat,'autumn'])
        assert n==n1==600
        lu[habitat] = split(n,r0,a[5],r1,b[5])
    lu['pooled'] = split(1200,62,15,978,209)
    assert isclose(lu['low']['conditional_recorded_cache_change_pp'],-12.731021279729033)
    assert isclose(lu['high']['conditional_recorded_cache_change_pp'],6.105263157894736)
    # Suzuki & Kajimura 2023 Table 1, percentages of seed MASS disappearance.
    # Each row: Summer-I, Summer-II, Fall-I, Fall-II; all table values retained.
    # Camera failure flags affect behavioral opportunity; mass loss is a separate endpoint.
    japan = {'BF_IN':[100,100,59.45,25.27],'BF_OUT':[100,100,.99,25.46],
             'CF_IN':[100,100,99.68,100],'CF_OUT':[100,100,100,100]}
    changes = {p:mean(v[2:])-mean(v[:2]) for p,v in japan.items()}
    bf = mean([changes['BF_IN'],changes['BF_OUT']])
    cf = mean([changes['CF_IN'],changes['CF_OUT']])
    contrast = cf-bf
    out_only = changes['CF_OUT']-changes['BF_OUT']
    assert isclose(contrast,72.1275) and isclose(out_only,86.775)
    result={'status':'EXPLORATORY_AGGREGATE_ONLY',
        'lu2004':lu,
        'suzuki2023':{'doi':'10.3389/fevo.2023.1124393','table1_mass_loss_pct':japan,
                       'BF_change_pp':bf,'CF_change_pp':cf,'difference_of_changes_pp':contrast,
                       'OUT_only_complete_camera_contrast_pp':out_only,
                       'n_independent_landscapes':1,'n_forest_plots':2,
                       'data_access':'author-linked Figshare download HTTP403'},
        'forget1996':{'doi':'10.1017/S0266467400009998','march_may_removal_pct':[23,96],
                       'cached_among_removed_pct':[28,48],'eaten_among_removed_pct':[43,9],
                       'restriction':'published abstract means; no joint denominator or matched horizon verified; no multiplication'},
        'fleury2014':{'doi':'10.1371/journal.pone.0090060','total_released':1440,
                      'reported_dispersed':2,'unlocated':11,
                      'observed_plus_all_unlocated_fraction_ceiling_pct':100*13/1440,
                      'restriction':'30-day endpoint; ceiling for these reported categories, not lifetime dispersal; no seasonal missing counts; author distance inconsistency; mixed predators'},
        'claim_ceiling':'Observed stage-specific associations and context heterogeneity; no latent allocation, causal resource predictor, or new independent test.'}
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__ == '__main__':
    main()
