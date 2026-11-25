// V22: conservative bounds from printed subgroup counts, run from repository root.
const fs=require('node:fs');
function calc(d){
 const need=(x,m)=>{if(!x)throw Error(m)};
 const tol=.05/100; // one decimal place, percentage proportion
 function roundedCandidates(n,p){let out=[];for(let k=0;k<=n;k++)if(Math.abs(k/n-p/100)<=tol+1e-12)out.push(k);return out;}
 const rows=d.rows.map(([species,season,N,H,r,e,ig])=>{
  const rs=roundedCandidates(H,r),es=roundedCandidates(H,e);
  need(rs.length&&es.length,"empty rounding set");
  const combos=rs.flatMap(R=>es.filter(E=>R+E<=H).map(E=>[R,E]));
  need(combos.length,"invalid reported subset");
  const rmin=Math.min(...combos.map(z=>z[0]))/N,emin=Math.min(...combos.map(z=>z[1]))/N;
  // Ignored lower is the only source-retention lower bound. No residual
  // from N-H treated as a known cache or intact count.
  const igLo=ig===null?0:Math.max(0,ig/100-tol);
  const igHi=ig===null?1:Math.min(1,ig/100+tol);
  const il=ig===0?0:igLo,ih=ig===0?0:igHi;
  need(il+rmin+emin<=1+1e-12,"incompatible lower bounds");
  const narrativeH=ig===null?null:[N*(1-ih),N*(1-il)];
  return {species,season,N,reported_subset_n:H,possible_removed_counts_from_rounded_subset_pct:rs,possible_in_situ_eaten_counts_from_rounded_subset_pct:es,reported_subset_removed_per_release_min:rmin,reported_subset_eaten_in_situ_per_release_min:emin,ignored_narrative_bounds:ig===null?null:[il,ih],narrative_harvest_count_interval:narrativeH,subset_n_inside_narrative_harvest_interval:narrativeH?H>=narrativeH[0]-1e-9&&H<=narrativeH[1]+1e-9:null,source_intact_outer_bounds:[il,1-rmin-emin],moved_intact_outer_bounds:[0,1-il-emin],any_intact_outer_bounds:[il,1-emin],removal_outer_bounds:[rmin,1-il-emin]};
 });
 const contrasts=[];
 for(const sp of [...new Set(rows.map(x=>x.species))]){
  const a=rows.find(x=>x.species===sp&&x.season==="autumn"),b=rows.find(x=>x.species===sp&&x.season==="spring");
  need(a&&b,"missing common species");
  const delta=(k)=>[b[k][0]-a[k][1],b[k][1]-a[k][0]];
  const s=delta("source_intact_outer_bounds"),m=delta("moved_intact_outer_bounds"),t=delta("any_intact_outer_bounds"),r=delta("removal_outer_bounds");
  contrasts.push({species:sp,source_intact_change_outer:s,moved_intact_change_outer:m,total_intact_change_outer:t,removal_change_outer:r,
     source_decline_identified:s[1]<0,total_decline_even_if_all_eligible_moved_survive:t[1]<0,removal_increase_identified:r[0]>0,
     minimum_uncompensated_loss_pp:t[1]<0?-100*t[1]:0,
     scenario_why_total_bound:"autumn lower = narrative ignored; spring upper = all released except minimally documented in-situ eaten; permits all other seeds intact including all removed and unknown, so no cache counts needed"});
 }
 return {status:"EXPLORATORY_SEASONAL_OUTER_BOUNDS_FROM_PUBLISHED_SUBGROUPS",source:d.source,design:d.design,cohorts:rows,contrasts,capture_ratio:d.design.reported_captures[1]/d.design.reported_captures[0],limits:d.boundary,uncertainty:"Integer candidates derived solely from rounding-compatible printed subgroup percentages, not retrieved seed histories. Unknown category assignments maximize feasible intact fractions; broad outer bounds, not sharp bounds or statistical CIs. Conditional on denominators and reported ignored/eaten/removed categories being valid. For inconsistent narrative H and subgroup n no forced partition or imputation. These are recorded seed-fate states, not survival to germination."};
}
console.log(JSON.stringify(calc(JSON.parse(fs.readFileSync("data/neon_lang_wang2016_seasonal_source_v22.json",'utf8'))),null,2));
