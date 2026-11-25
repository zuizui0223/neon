// V20: arithmetic on published cohort summaries, no raw-data fit.
const fs=require('node:fs');
function calculate(d){
 const check=(x,m)=>{if(!x)throw Error(m)};
 const avg=(x,y)=>(x+y)/2;
 const o=d.cohorts.map(c=>{
 check(c.stations_each_year*c.seeds_per_station===c.released_each_year,"release design");
 const n=c.released_each_year;
 const partition=[0,1].map(i=>c.removed_pct[i]+c.at_station_rodent_eaten_pct[i]+c.at_station_ant_eaten_pct[i]+c.at_station_rotten_pct[i]+c.at_station_established_pct[i]);
 check(partition.every(x=>Math.abs(x-100)<=.21),"at-station rounded partition");
 const r=c.removed_pct.map(x=>x/100),a=c.at_station_established_pct.map(x=>x/100),b=c.post_removal_established_exact_counts.map(x=>x/n);
 const p=a.map((x,i)=>x/(1-r[i])),q=b.map((x,i)=>x/r[i]),total=a.map((x,i)=>x+b[i]);
 check(p.every(x=>x>=0&&x<=1)&&q.every(x=>x>=0&&x<=1),"nested pathway");
 const alloc=(r[1]-r[0])*(avg(q[0],q[1])-avg(p[0],p[1]));
 const site=(1-avg(...r))*(p[1]-p[0]),moved=avg(...r)*(q[1]-q[0]);
 check(Math.abs(alloc+site+moved-(total[1]-total[0]))<1e-12,"exact symmetric decomposition");
 // Rounding-only sensitivity: use half unit of last displayed decimal; no distribution.
 // 21% printed with no decimal, conservative ±0.5 pp. Zero in station is explicit in prose.
 const dr=c.removed_pct.map(x=>Number.isInteger(x)?.005:.0005);
 const da=c.at_station_established_pct.map(x=>x===0?0:.0005);
 const results=[];
 for(const bits of [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]){
  const rr=r.map((v,i)=>v+(bits&(1<<i)?1:-1)*dr[i]),aa=a.map((v,i)=>v+(bits&(1<<(i+2))?1:-1)*da[i]);
  const pp=aa.map((x,i)=>x/(1-rr[i])),qq=b.map((x,i)=>x/rr[i]);
  const tt=aa.map((x,i)=>x+b[i]);
  results.push({allocation:(rr[1]-rr[0])*(avg(...qq)-avg(...pp)),station:(1-avg(...rr))*(pp[1]-pp[0]),after:avg(...rr)*(qq[1]-qq[0]),total_change:tt[1]-tt[0]});
 }
 const bounds=Object.fromEntries(Object.keys(results[0]).map(k=>[k,[Math.min(...results.map(x=>x[k])),Math.max(...results.map(x=>x[k]))]]));
 // Maximal *unresolved* post-removal scenario: every removed seed not recorded
 // as established might have established; deliberately includes known consumed seeds,
 // because complete count absent. Not a sharp missing-fate bound.
 const broad=total.map((x,i)=>[x,a[i]+r[i]]);
 return {species:c.species,N_each_year:n,removed:r,recorded_establishment_at_station:a,recorded_establishment_after_removal:b,recorded_total_establishment:total,post_removal_fraction_among_recorded_establishment:total.map((x,i)=>x?b[i]/x:null),conditional_recorded_station_establishment_given_not_removed:p,conditional_recorded_after_removal_establishment:q,delta_recorded_total:total[1]-total[0],symmetric_descriptive_components:{removal_allocation:alloc,within_nonremoved_route:site,within_removed_route:moved},rounding_endpoint_corner_sensitivity:bounds,at_station_partition_sum_pct:partition,primary_cache_per_release_pct:c.primary_cache_pct,broad_unknown_removed_ceiling:broad,broad_total_change_ceiling:[broad[1][0]-broad[0][1],broad[1][1]-broad[0][0]],net_additional_unrecorded_low_minus_high_fraction_to_tie:total[1]-total[0],station_gain_over_recorded_post_removal_loss:b[0]>b[1]?(a[1]-a[0])/(b[0]-b[1]):null}
 });
 const x=d.resource;
 check(x.rodent_species_counts&&Object.values(x.rodent_species_counts).reduce((s,v)=>s+v[0],0)===27&&Object.values(x.rodent_species_counts).reduce((s,v)=>s+v[1],0)===7,"capture tally");
 return {status:"PUBLISHED_AGGREGATE_ESTABLISHMENT_ROUTE_ACCOUNTING",source:d.source,resource_summary:{seed_rain_ratio:x.community_seed_rain_per_m2[1]/x.community_seed_rain_per_m2[0],capture_count_ratio:x.rodent_reported_individual_count[1]/x.rodent_reported_individual_count[0],relative_seed_rain_to_capture_index_ratio:(x.community_seed_rain_per_m2[1]/x.community_seed_rain_per_m2[0])/(x.rodent_reported_individual_count[1]/x.rodent_reported_individual_count[0]),camellia_sampled_plant_crop_ratio:x.camellia_crop_per_sampled_plant[1]/x.camellia_crop_per_sampled_plant[0]},cohorts:o,boundary:d.boundary,rounding_scope:"Corner calculations reflect printed rounding only, not SE or sampling CI; exact post-removal counts held fixed. Not bounds on latent unobserved establishment. Broad ceiling permits every removed seed to establish and is intentionally loose."}
}
console.log(JSON.stringify(calculate(JSON.parse(fs.readFileSync("data/neon_cao2017_establishment_routes_v20_20261126.json",'utf8'))),null,2));
