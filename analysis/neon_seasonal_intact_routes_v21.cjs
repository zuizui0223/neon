// V21: reproduce partial-identification arithmetic, node from repo root.
const fs=require('node:fs');
function calculate(d){
 const need=(x,m)=>{if(!x)throw Error(m)};
 const u=10000,phase=["spring","autumn"];
 const a=phase.map(s=>{
  const f=d.fates[s];need(Object.values(f).reduce((x,y)=>x+y,0)===u,"partition");
  const A=f.IS,B=f.IR+f.HR,M=f.MR,R=f.PR+B+M,N=f.IS+f.PS;
  need(R+N===u,"route partition");
  return {season:s,source_intact:A,removed_intact:B,missing_after_removal:M,removed:R,not_removed:N,confirmed_total_intact:A+B,conditional_source_intact:A/N,conditional_moved_intact_bounds:[B/R,(B+M)/R],total_intact_state_bounds:[(A+B)/u,(A+B+M)/u],moved_share_of_total_intact_bounds:[B/(A+B),(B+M)/(A+B+M)]};
 });
 const [x,y]=a;
 const point=(v,m)=>({A:v.source_intact/u,B:(v.removed_intact+m*v.missing_after_removal)/u,R:v.removed/u,p:v.conditional_source_intact,q:(v.removed_intact+m*v.missing_after_removal)/v.removed});
 const contrast=(m0,m1)=>{
  const z0=point(x,m0),z1=point(y,m1),mean=(a,b)=>(a+b)/2;
  const moved=z1.B-z0.B,source=z1.A-z0.A,total=source+moved;
  const alloc=(z1.R-z0.R)*(mean(z0.q,z1.q)-mean(z0.p,z1.p)),non=(1-mean(z0.R,z1.R))*(z1.p-z0.p),mov=mean(z0.R,z1.R)*(z1.q-z0.q);
  need(Math.abs(alloc+non+mov-total)<1e-12,"accounting identity");
  return {source_route_delta:source,moved_route_delta:moved,total_intact_delta:total,conditional_nonremoved_delta:z1.p-z0.p,conditional_removed_delta:z1.q-z0.q,change_in_conditional_removed_minus_nonremoved:(z1.q-z1.p)-(z0.q-z0.p),allocation_component:alloc,within_nonremoved_component:non,within_removed_component:mov};
 };
 const corners=[[0,0],[0,1],[1,0],[1,1]],envelope=ps=>Object.fromEntries(Object.keys(ps[0]).map(k=>[k,[Math.min(...ps.map(x=>x[k])),Math.max(...ps.map(x=>x[k]))]]));
 const un=envelope(corners.map(([m0,m1])=>contrast(m0,m1))),eq=envelope([contrast(0,0),contrast(1,1)]);
 const k=v=>((v.source_intact/v.not_removed)*v.removed-v.removed_intact)/v.missing_after_removal;
 const tie=a.map(k);
 const comparison=a.map(v=>({season:v.season,conditional_removed_minus_nonremoved_bounds:v.conditional_moved_intact_bounds.map(q=>q-v.conditional_source_intact),missing_intact_fraction_for_tie:k(v)}));
 need(un.total_intact_delta[0]>0&&un.moved_route_delta[0]<0&&un.source_route_delta[0]>-un.moved_route_delta[0],"compensation envelope");
 return {status:"SEASONAL_RECORDED_INTACT_ROUTE_PARTIAL_IDENTIFICATION",source_doi:d.source.doi,cohorts:a,confirmed_only_contrast:contrast(0,0),unrestricted_missing_fate_envelopes:un,equal_unknown_intact_fraction_sensitivity: minMax(eq),conditional_route_comparison:comparison,worst_case_source_gain_to_moved_loss_ratio:un.source_route_delta[0]/(-un.moved_route_delta[0]),unknown_fraction_note:"m_s is fraction of missing-after-removal seeds hypothetically in the intact/unconsumed state. m0,m1 vary freely [0,1] in unrestricted bounds. Equal fractions are sensitivity only, not missing-at-random or an estimate. All contrasts affine in missing fractions; corner extrema exact for reported rounded values.",limits:["Published spring/autumn pooled percentages, four species, 15 vs 9 release stations (same 20 seeds/species/station), scheduled 60-day follow-up. Original calendar year not independently verified in this run; source text includes later spring re-observation. No claim of paired station or exact common terminal date beyond reported fate categories.","Intact state is operational: intact at station plus reported intact surface/buried after removal, not proof of viability, survival to germination, or recruitment. Missing may have other fates; binary scenarios treat intact state as 0/1. Observed categories assumed valid. Bounds conditional on printed rates, not uncertainty in classification or sampling.","Source and moved route groups are observational, not randomized. No causal movement effect or independent site replication. No reconstructing seed-level counts from rounded percentages. No pooling with V20 establishment outcomes."]};
 function minMax(x){return x}
}
console.log(JSON.stringify(calculate(JSON.parse(fs.readFileSync("data/neon_li2021_seasonal_published_fates_20261124.json",'utf8'))),null,2));
