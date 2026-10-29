"""Correctness reanalysis, not a new hypothesis or independent dataset.

Keep all original 58 pairs, margins and 14 sites; correct only the biased
accepted-only MCMC clock. Compare both full and already-declared 12-site
source-overlap exclusion. Original numbers remain archived, not rewritten.
No raw identities, species, trap labels, W/B, or habitat outcomes exported.
"""
from collections import defaultdict
import json
from pathlib import Path
from statistics import mean

from analysis.run_neon_crossseason_direct_site_null_calibration_v1 import _original_source_units
from analysis.neon_crossseason_template_null_v1 import crossseason_template_inference
from analysis.neon_crossseason_direct_site_null_v1 import direct_site_null_calibration
from analysis.neon_crossseason_direct_null_calibration_v1 import (
    direct_site_weighted_product_null,
    reused_physical_site_ids_from_source_units,
    season_sharing_diagnostic,
)
from analysis.neon_proposal_clock_v2 import corrected_unit

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/neon_uniform_null_correction_v2.json'


def require(ok,message):
    if not ok:
        raise RuntimeError(message)


def aggregate(private,seed):
    bysite=defaultdict(list)
    for u in private:
        bysite[u['site']].append(u['observed_z'])
    site=crossseason_template_inference(bysite,seed=seed)
    product=direct_site_weighted_product_null(private,seed=seed+1,n_replicates=100000)
    linked=direct_site_null_calibration([
        {'site':u['site'],'observed_unit_z':u['observed_z'],
         'null_unit_z_draws':u['null_z_draws']} for u in private
    ],seed=seed+2,n_replicates=20000)
    coupled=linked['comonotone_within_site_marginal_null']
    return {
        'physical_sites':len(bysite),'seasonal_pairs':len(private),
        'site_mean_Z':site['site_mean_Z_mean'],
        'positive_site_means':site['positive_site_means'],
        'sorted_site_means':site['site_Z_means_sorted_ascending'],
        'signflip_p_descriptive_only':site['one_sided_site_signflip_p'],
        'independent_unit_null':product,
        'within_site_comonotone_stress':coupled,
        'support_under_both_conditional_couplings':(
            len(bysite)>=8 and site['site_mean_Z_mean']>0
            and product['one_sided_p_with_plus_one']<.05
            and coupled['one_sided_p']<.05),
        'not_new_independent_confirmation':True,
        'within_site_coupling_not_a_bound_over_all_joint_nulls':True,
    }


def run():
    units,old,source=_original_source_units()
    units.sort(key=lambda u:(u['site'],u['site_plot'],u['season_ordinal']))
    require(len(units)==58 and len({u['site'] for u in units})==14,
            'Original 58-pair 14-site cohort changed')
    excludes=reused_physical_site_ids_from_source_units(units)
    require(len(excludes)==2,'Source-defined two-site exclusion changed')
    clean_source=[u for u in units if u['site'] not in excludes]
    require(len(clean_source)==46 and len({u['site'] for u in clean_source})==12,
            'Original 46-pair 12-site sensitivity changed')
    require(season_sharing_diagnostic(clean_source)['season_keys_used_in_multiple_pair_roles']==0,
            'Excluded cohort still reuses original season keys')
    previous=old['informative_unit_source_geometry_summary']['unlabelled_unit_diagnostics']
    require(len(previous)==58,'Original aggregate receipt does not match')
    private=[]
    diagnostics=[]
    for i,(u,past) in enumerate(zip(units,previous)):
        require(len(u['A'])==past['source_genera'] and
                sum(map(len,u['A'].values()))==past['observed_genus_trap_cells_season_A'] and
                sum(map(len,u['B'].values()))==past['observed_genus_trap_cells_season_B'],
                'Original pair genus or occupancy margins changed')
        draws=[]
        r=corrected_unit(u['A'],u['B'],seed=2026102001+i,
                         n_draws=2000,burn=10000,thin=100,min_ess=200,
                         draws_out=draws)
        diagnostics.append({
            'quality_pass':r['quality_pass'],
            'split_Rhat':r['split_Rhat'],
            'ESS':r['batch_means_ESS_per_chain'],
            'original_accepted_clock_Z':past['z'],
            'corrected_proposal_clock_Z':r['z'],
            'observed_overlap':r['observed_overlap'],
            'null_mean':r['null_mean'],'null_sd':r['null_sd'],
            'accepted_fraction':r['accepted_moves']/r['attempts_counted'],
        })
        if r['quality_pass']:
            private.append({
                'unit_index':i,'site':u['site'],'observed_z':r['z'],
                'null_z_draws':[(x-r['null_mean'])/r['null_sd'] for x in draws],
            })
    base={
        'schema':'neon.corrected_uniform_fixedmargin_recurrence.v2',
        'record_date':'2026-10-20',
        'source':source,
        'method':'lazy symmetric row-pair swap; all proposals counted including rejected and held states',
        'proof_and_plan':'docs/NEON_NULL_PROPOSAL_CLOCK_CORRECTION_20261020.md',
        'source_cohort_and_margins_unchanged':True,
        'old_accepted_only_clock_not_uniform_in_general':True,
        'old_p_values_retained_as_historical_not_uniform_null_validation':True,
        'two_chains_per_unit':True,
        'retained_draws_per_chain':2000,
        'burn_proposals_per_chain':10000,
        'spacing_in_proposals':100,
        'sampler_seed_base':2026102001,
        'second_chain_seed_offset':1000003,
        'all_units_quality_pass':len(private)==58,
        'unit_diagnostics':diagnostics,
        'uniform_stationarity_proof_not_finite_time_exact_sampling':True,
        'post_result_correction_not_preregistered_independent_confirmation':True,
        'old_density_W_B_status':'FAILED_5_OF_8',
        'MOSA_W_B':'SEALED',
        'causal_competition_or_habitat_filtering_established':False,
        'genus_specific_detection_bias_excluded':False,
        'raw_source_ids_or_null_draws_exported':False,
    }
    if len(private)!=58:
        return {**base,'status':'HOLD_CORRECTED_SAMPLER_CHAIN_QUALITY',
                'failed_units':58-len(private),
                'no_failed_unit_removed_to_create_significance':True}
    full=aggregate(private,2026102021)
    clean=aggregate([u for u in private if u['site'] not in excludes],2026102031)
    okay=(full['support_under_both_conditional_couplings'] and
          clean['support_under_both_conditional_couplings'])
    return {
        **base,
        'status':('CORRECTED_UNIFORM_NULL_SUPPORTS_RECURRENCE_CONDITIONALLY'
                  if okay else 'CORRECTED_UNIFORM_NULL_WEAKENS_PREVIOUS_CLAIM'),
        'full_14site':full,'source_disjoint_12site':clean,
        'no_reused_season_keys_in_12site_cohort':True,
        'max_split_Rhat':max(x['split_Rhat'] for x in diagnostics),
        'minimum_batch_means_ESS':min(min(x['ESS']) for x in diagnostics),
        'mean_absolute_unit_Z_change':mean(abs(x['original_accepted_clock_Z']-x['corrected_proposal_clock_Z']) for x in diagnostics),
        'maximum_absolute_unit_Z_change':max(abs(x['original_accepted_clock_Z']-x['corrected_proposal_clock_Z']) for x in diagnostics),
        'claim':'Conditional genus-associated trap recurrence; not verified demographic replacement, competition, or habitat mechanism',
    }


def main():
    try:
        result=run()
    except Exception as e:
        result={'schema':'neon.corrected_uniform_fixedmargin_recurrence.v2',
                'status':'STOP_SOURCE_OR_CORRECTED_SAMPLER',
                'error_class':type(e).__name__,
                'original_p_values_not_reinstated':True}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,sort_keys=True))
    return 3 if result['status'].startswith(('STOP','HOLD')) else 0


if __name__=='__main__':
    raise SystemExit(main())
