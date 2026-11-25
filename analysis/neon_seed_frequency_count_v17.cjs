// V17: reproduce published-coefficient implications; no third-party dependencies.
const fs=require('node:fs');
function calculate(d,v){
 const assert=(x,m)=>{if(!x)throw Error(m)};
 const [f0,f1]=d.frequency_endpoints,delta=f1-f0,d2=f1*f1-f0*f0,nratio=f1/f0,logn=Math.log(nratio),z=1.96;
 assert(d.fixed_patch_seed_count===80&&d.rows.length===6&&f0===.1&&f1===.9,"source design");
 const B=x=>[Math.min(0,x),Math.max(0,x)], scale=(a,b)=>[nratio*Math.exp(a),nratio*Math.exp(b)];
 const add=(a,b)=>[a[0]+b[0],a[1]+b[1]];
 const lim=(a,u)=>[Math.min(0,a-u),Math.max(0,a+u)];
 const logistic=x=>1/(1+Math.exp(-x));
 const rows=d.rows.map(([target,neighbor,br,sr,bc,sc,gc,sg])=>{
 const r=br*delta,c=bc*delta+gc*d2,ur=z*sr*delta,uc=z*(sc*delta+sg*d2);
 const rb=B(r),cb=B(c),er=lim(r,ur),ec=lim(c,uc);
 const R=scale(...rb),C=scale(...cb),RC=scale(...add(rb,cb));
 // Numerical verification of bounds over a wide range of unknown intercepts;
 // analytic proof is independent of this finite grid.
 for(let x=-24;x<=24;x+=.5){
   const rr=logistic(x+r)/logistic(x);
   assert(rr>=Math.exp(rb[0])-1e-10&&rr<=Math.exp(rb[1])+1e-10,"logit risk bound");
   for(const y of [-24,-12,-4,0,4,12,24]){
    const cc=logistic(y+c)/logistic(y),rc=nratio*rr*cc;
    assert(rc>=RC[0]-1e-9&&rc<=RC[1]+1e-9,"product bound");
   }
 }
 return {target,neighbor,removal_logit_shift:r,cache_logit_shift:c,removal_odds_ratio:Math.exp(r),cache_odds_ratio:Math.exp(c),removal_count_factor_point_model:R,removal_count_factor_normal_sensitivity:scale(...er),cache_count_factor_unconditional_point_model:C,cache_count_factor_conditional_point_model:RC,cache_count_factor_unconditional_normal_sensitivity:scale(...ec),cache_count_factor_conditional_normal_sensitivity:scale(...add(er,ec))};
 });
 const a=v.cohorts["2018/19"],b=v.cohorts["2020/21"];const total=b.rain_three_species_per_m2/a.rain_three_species_per_m2,comp=b.beech_fraction_of_three/a.beech_fraction_of_three,focal=b.rain_beech_per_m2/a.rain_beech_per_m2;
 assert(Math.abs(total*comp-focal)<1e-10,"resource identity");
 return {status:"PUBLISHED_COEFFICIENT_MODEL_IMPLICATIONS_ONLY",source_doi:d.paper_doi,frequency_from:f0,frequency_to:f1,focal_count_from:d.fixed_patch_seed_count*f0,focal_count_to:d.fixed_patch_seed_count*f1,threshold_linear_logit_slope:-logn/delta,rows,
 all_six_removal_point_lower_above_one:rows.every(x=>x.removal_count_factor_point_model[0]>1),
 all_six_removal_marginal_normal_lower_above_one:rows.every(x=>x.removal_count_factor_normal_sensitivity[0]>1),
 min_removal_point_lower:Math.min(...rows.map(x=>x.removal_count_factor_point_model[0])),
 min_removal_marginal_normal_lower:Math.min(...rows.map(x=>x.removal_count_factor_normal_sensitivity[0])),
 cache_both_interpretations_point_lower_above_one:rows.filter(x=>x.cache_count_factor_unconditional_point_model[0]>1&&x.cache_count_factor_conditional_point_model[0]>1).length,
 cache_both_interpretations_marginal_normal_lower_above_one:rows.filter(x=>x.cache_count_factor_unconditional_normal_sensitivity[0]>1&&x.cache_count_factor_conditional_normal_sensitivity[0]>1).length,
 beech_resource_decomposition:{total,comp,focal,log_total_share:Math.log(total)/Math.log(focal),log_composition_share:Math.log(comp)/Math.log(focal)},limitations:d.limitations,uncertainty:"Individual coefficient estimate ±1.96 marginal SE; for a quadratic combination use sum of absolute weighted SE as conservative envelope, then rectangular combination across stages. Not a simultaneous or calibrated 95% CI, no covariance, no new test or observed model validation."};
}
const x=JSON.parse(fs.readFileSync("data/neon_guo2026_size_frequency_coefficients_v17.json",'utf8'));
const y=JSON.parse(fs.readFileSync("results/neon_sachser_joint_context_v16_20261126.json",'utf8'));
console.log(JSON.stringify(calculate(x,y),null,2));
