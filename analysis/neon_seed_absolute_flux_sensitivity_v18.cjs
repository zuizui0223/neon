// V18b: conditional flow projections; run from repository root.
const fs=require('node:fs');
function calculate(v){
 const need=(x,m)=>{if(!x)throw Error(m)};
 need(v.status==="JOINT_ANNUAL_CONTEXT_DESCRIPTIVE","V16 source");
 const a=v.cohorts["2018/19"],b=v.cohorts["2020/21"];
 for(const x of [a,b])need(x.field_assessed===180&&Object.values(x.field_fate_counts).reduce((s,n)=>s+n,0)===180,"fate counts");
 const E=[
  ["documented_germination","field_germination_bounds",x=>x.field_fate_counts.germinated],
  ["documented_ex_situ_location","recorded_ex_situ_location_bounds",x=>Math.round(x.recorded_ex_situ_location_bounds[0]*x.field_assessed)],
  ["intact_or_germinated","field_intact_or_germinated_bounds",x=>x.field_fate_counts.intact+x.field_fate_counts.germinated],
  ["predated","field_predation_bounds",x=>x.field_fate_counts.predated]
 ];
 const supply=[a.rain_beech_per_m2,b.rain_beech_per_m2],R=supply[1]/supply[0];
 const rows=E.map(([endpoint,field,count])=>{
  const n=[count(a),count(b)],m=[a.field_fate_counts.missing,b.field_fate_counts.missing],N=[a.field_assessed,b.field_assessed];
  const probs=n.map((x,i)=>[x/N[i],(x+m[i])/N[i]]);
  need(probs.every((z,i)=>z.every((q,k)=>Math.abs(q-[a,b][i][field][k])<1e-10)),"reconcile "+endpoint);
  const proj=probs.map((z,i)=>z.map(p=>p*supply[i]));
  const rate_ratio=[probs[1][0]/probs[0][1],probs[1][1]/probs[0][0]];
  const flux_ratio=[proj[1][0]/proj[0][1],proj[1][1]/proj[0][0]];
  const thresh=[1/rate_ratio[1],1/rate_ratio[0]];
  // Exhaustively verify extrema across integer missing-outcome assignments.
  let lo=Infinity,hi=-Infinity;
  for(let i=0;i<=m[0];i++)for(let j=0;j<=m[1];j++){
   const q=supply[1]*(n[1]+j)/N[1]/(supply[0]*(n[0]+i)/N[0]);
   lo=Math.min(lo,q);hi=Math.max(hi,q);
  }
  need(Math.abs(lo-flux_ratio[0])<1e-10&&Math.abs(hi-flux_ratio[1])<1e-10,"enumeration");
  return {endpoint,observed_n:n,missing_n:m,per_assessed_seed_fraction:probs,conditional_area_projection_per_m2:proj,
     projected_ratio_using_confirmed_counts_only:proj[1][0]/proj[0][0],
     per_seed_rate_ratio_bounds:rate_ratio,area_projection_ratio_bounds:flux_ratio,
     supply_ratio_required_for_equal_projection_bounds:thresh,
     projection_difference_bounds:[proj[1][0]-proj[0][1],proj[1][1]-proj[0][0]],
     projection_direction:lo>1?"increase_all_missing_assignments":hi<1?"decrease_all_missing_assignments":"unresolved"};
 });
 // Missing germinants required for nondecrease in projected field germination.
 const g=rows[0];const minBy2018=[];
 for(let x=0;x<=a.field_fate_counts.missing;x++){
  let j=null;
  for(let k=0;k<=b.field_fate_counts.missing;k++){
    if(supply[1]*(g.observed_n[1]+k)/180>=supply[0]*(g.observed_n[0]+x)/180){j=k;break}
  }
  minBy2018.push({additional_2018_germinated:x,min_additional_2020_germinated_for_nondecrease:j});
 }
 return {status:"CONDITIONAL_FLUX_SCENARIO_NOT_OBSERVED_AREA_FLUX",source_doi:"10.1098/rsbl.2024.0586",cohort_years:["2018/19","2020/21"],seed_rain_per_m2:supply,supply_ratio:R,rows,missing_germination_thresholds:minBy2018,assumptions:["Treat experimental assessed seed fate fractions as hypothetical transferable probabilities for all natural beech seed rain in the same year; this is not established.","Missing seeds may have any endpoint state; reported nonmissing fate labels held fixed. Separate endpoint bounds are marginal, not joint distributions.","Do not use projected ex-situ location as actual transport, intact-or-germinated as viability, or germination as recruitment. Natural seed rain may include unviable seeds; tagged field seeds and natural seeds differ in sampling, handling, density, and location.","One forest, two years; no causal inference, statistical confidence interval, validated absolute flux, or seasonal replication."]};
}
console.log(JSON.stringify(calculate(JSON.parse(fs.readFileSync("results/neon_sachser_joint_context_v16_20261126.json",'utf8'))),null,2));
