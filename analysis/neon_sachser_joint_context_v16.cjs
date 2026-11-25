// V16: source aggregate calculations, run from repo root.
const fs=require('node:fs');
function calculate(d){
 const assert=(v,m)=>{if(!v)throw Error(m)};
 const sum=a=>a.reduce((x,y)=>x+y,0);
 const mean=a=>sum(a)/a.length;
 assert(d.seed_rain.length===12&&d.captures.length===71&&d.lab.length===12,"source row support");
 const labs={};let trial="";
 for(const r of d.lab){if(r[0])trial=r[0];assert(["2018/19","2020/21"].includes(trial),"lab cohort");const z=r.slice(2).map(Number);assert(z[0]+z[1]+z[2]===z[3]&&z[3]>=0&&z[3]<=100,"lab partition");(labs[trial]??=[]).push(z[3]);}
 assert(labs["2018/19"].length===4&&labs["2020/21"].length===8,"lab sample size");
 const cohorts={};
 for(const [k,f] of Object.entries(d.fates)){
  const y=+k.slice(0,4),rain=d.seed_rain.filter(r=>r.year===y);
  assert(rain.length===3&&new Set(rain.map(r=>r.taxon)).size===3,"rain roster");
  const r=Object.fromEntries(rain.map(x=>[x.taxon,x.mean]));
  const rows=d.captures.filter(x=>x.trial===k);
  assert(rows.every(x=>x.date.startsWith(y+"-08-")&&Number.isInteger(x.count)&&x.count>0),"capture month or count");
  assert(new Set(rows.map(x=>[x.site,x.date,x.family].join("|"))).size===rows.length,"duplicate capture summary key");
  const families=Object.fromEntries(["cricetidae","muridae","gliridae"].map(x=>[x,sum(rows.filter(z=>z.family===x).map(z=>z.count))]));
  const by_site={};for(const site of ["basin","slope"]){const z=rows.filter(x=>x.site===site),n=new Set(z.map(x=>x.date)).size;assert(n===(y===2012?3:5),"night coverage");by_site[site]={reported_date_count:n,count:sum(z.map(x=>x.count)),families:Object.fromEntries(Object.keys(families).map(g=>[g,sum(z.filter(x=>x.family===g).map(x=>x.count))]))};}
  const n=sum(Object.values(families)),nominal_effort=50*sum(Object.values(by_site).map(z=>z.reported_date_count));assert(n===sum(Object.values(by_site).map(z=>z.count)),"capture reconciliation");
  const all=f.reported_position_counts,counts=Object.fromEntries(["germinated","intact","predated","missing"].map(z=>[z,all.in[z]+all.ex[z]]));
  assert(sum(Object.values(counts))===f.N&&counts.missing===f.unresolved,"fate reconciliation");
  const bound=x=>[x/f.N,(x+counts.missing)/f.N];
  cohorts[k]={rain_beech_per_m2:r.B,rain_other_two_per_m2:r.S+r.F,rain_three_species_per_m2:sum(Object.values(r)),beech_fraction_of_three:sum(Object.values(r))?r.B/sum(Object.values(r)):null,
     capture_counts:n,nominal_trap_nights:nominal_effort,captures_per_100_nominal_trap_nights:n/nominal_effort*100,capture_family_counts:families,capture_family_shares:Object.fromEntries(Object.entries(families).map(([k,v])=>[k,v/n])),by_site,
     lab_germination_mean:labs[k]?mean(labs[k])/100:null,lab_batch_n:labs[k]?.length??0,
     field_assessed:f.N,field_fate_counts:counts,field_germination_bounds:bound(counts.germinated),field_intact_or_germinated_bounds:bound(counts.intact+counts.germinated),field_predation_bounds:bound(counts.predated),recorded_ex_situ_location_bounds:bound(f.located_ex_situ)};
 }
 const x=cohorts["2018/19"],y=cohorts["2020/21"];assert(x.nominal_trap_nights===500&&y.nominal_trap_nights===500,"equal nominal effort");
 const ratio=(k)=>y[k]/x[k];const change=(k)=>[y[k][0]-x[k][1],y[k][1]-x[k][0]];
 return {status:"JOINT_ANNUAL_CONTEXT_DESCRIPTIVE",cohorts,contrast_2020_vs_2018:{beech_rain_ratio:ratio("rain_beech_per_m2"),three_species_rain_ratio:ratio("rain_three_species_per_m2"),capture_rate_ratio:ratio("captures_per_100_nominal_trap_nights"),beech_rain_to_capture_index_ratio:ratio("rain_beech_per_m2")/ratio("captures_per_100_nominal_trap_nights"),three_species_rain_to_capture_index_ratio:ratio("rain_three_species_per_m2")/ratio("captures_per_100_nominal_trap_nights"),beech_seed_rain_fraction_change:y.beech_fraction_of_three-x.beech_fraction_of_three,gliridae_capture_share_change:y.capture_family_shares.gliridae-x.capture_family_shares.gliridae,cricetidae_capture_share_change:y.capture_family_shares.cricetidae-x.capture_family_shares.cricetidae,lab_germination_change:y.lab_germination_mean-x.lab_germination_mean,field_germination_change_bounds:change("field_germination_bounds"),field_intact_or_germinated_change_bounds:change("field_intact_or_germinated_bounds"),field_predation_change_bounds:change("field_predation_bounds"),ex_situ_location_change_bounds:change("recorded_ex_situ_location_bounds")},boundary:"Two comparable local-seed years, one landscape; August recorded capture counts per nominal effort may include repeated individuals; annual seed rain per area and capture index are different units, not food per animal or causal resource pressure. Diet/accessibility not known; family composition not seed handling actor attribution. Lab batches are separate from field seeds and not an experimental counterfactual. Fate uncertainty ranges allocate all missing freely, not sampling CIs. Intact may remain viable or fail later; no recruitment or seasonal replication."};
}
console.log(JSON.stringify(calculate(JSON.parse(fs.readFileSync("data/neon_sachser_joint_context_v16_20261126.json",'utf8'))),null,2));
