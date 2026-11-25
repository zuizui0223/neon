// V12: run node analysis/neon_seed_stage_synthesis_v12.cjs from repository root. No dependencies.
// The numerical core was executed directly before committing.
const fs=require('node:fs');
const paths={
  "lu": "data/neon_lu2004_published_seasonal_release_counts_20261124.json",
  "li": "data/neon_li2021_seasonal_published_fates_20261124.json",
  "ny": "docs/NEON_VAVRA_ACTOR_SEASONAL_V5_20261125.md",
  "amazon": "docs/NEON_AMAZON_SEASONAL_STAGE_V4_20261125.md",
  "maine": "results/neon_merz_ambiguity_envelope_v8_20261125.json",
  "density": "results/neon_merz_density_seed_v9_20261125.json",
  "beech": "results/neon_sachser_downstream_fate_v11_20261125.json"
};
function calculate(d){
 const near=(a,b)=>Math.abs(a-b)<1e-9;
 const assert=(x,m)=>{if(!x)throw Error(m)};
 const rows=[];
 const interval=x=>Array.isArray(x)?x:[x,x];
 const div=(a,b)=>{a=interval(a);b=interval(b);assert(b[0]>0,"nonpositive denominator");return [a[0]/b[1],a[1]/b[0]]};
 const direction=r=>r[0]>1+1e-10?"increase":r[1]<1-1e-10?"decrease":"unresolved_or_flat";
 const push=(study,context,time,up,down,u0,u1,y0,y1,scope,q0=null,q1=null)=>{
   const ur=div(u1,u0),yr=div(y1,y0),qr=div(q1===null?div(y1,u1):q1,q0===null?div(y0,u0):q0);
   assert(interval(y0)[1]<=interval(u0)[1]+1e-9&&interval(y1)[1]<=interval(u1)[1]+1e-9,"non-nested");
   if([...ur,...yr,...qr].every(Number.isFinite) && ur[0]===ur[1]&&yr[0]===yr[1])assert(near(ur[0]*qr[0],yr[0]),"product identity");
   const ud=direction(ur),yd=direction(yr),qd=direction(qr);
   let propagation="unresolved_or_flat";
   if(ud!=="unresolved_or_flat"&&yd!=="unresolved_or_flat"){
     if(ud!==yd)propagation="reversal";
     else if(qd!=="unresolved_or_flat")propagation=qd===ud?"amplification":"attenuation";
   }
   rows.push({study,context,contrast:time,upstream:up,downstream:down,upstream_ratio:ur,downstream_ratio:yr,conversion_ratio:qr,log2_conversion_ratio:qr.map(Math.log2),observed_propagation:propagation,scope})
 };
 const lu=d.lu;assert(lu.followup_days===16&&lu.rows.length===6,"lu source");
 for(const habitat of ["low","high"]){
   const a=lu.rows.find(r=>r[0]===habitat&&r[1]==="summer"),b=lu.rows.find(r=>r[0]===habitat&&r[1]==="autumn");
   assert(a[2]===600&&b[2]===600,"lu denominator");
   push("Lu & Zhang 2004",habitat,"summer→autumn","removed","recorded hoarded",a[3]/a[2],b[3]/b[2],a[5]/a[2],b[5]/b[2],"published counts; some other fate columns inconsistent; unknown caching not identified");
 }
 const l=d.li.fates;
 function stages(f){assert(Object.values(f).reduce((a,b)=>a+b,0)===10000,"li fate partition");return [(10000-f.IS)/10000,(f.PR+f.IR+f.HR+f.MR)/10000,f.HR/10000]}
 const a=stages(l.spring),b=stages(l.autumn);
 push("Li et al. 2021","four seed species pooled","spring→autumn","removed or eaten in situ","removed",a[0],b[0],a[1],b[1],"rounded published proportions; unequal stations and unknown mixture; handling definition is recorded removal or on-site eating");
 push("Li et al. 2021","four seed species pooled","spring→autumn","removed","recorded hoarded",a[1],b[1],a[2],b[2],"rounded published proportions; true hoarding direction unresolved with missing fates");
 assert(d.ny.includes("| Dec | (30,2) | (1,0) | (0,2) | 35 | 4 |")&&d.ny.includes("| Jan | (1,0) | (0,0) | (0,5) | 6 | 5 |"),"NY verified summary");
 push("Vavra & Guiden 2025","maple, all recorded actors","Dec→Jan","handled","carried whole",35,6,4,5,"verified original data; one forest, January six seeds; not equivalence or annual inference");
 assert(d.amazon.includes("| Primary buried after removal | 637 | 244 |")&&d.amazon.includes("| Relocated from primary burial | 38 | 3 |")&&d.amazon.includes("| Still there at original primary burial site | 3 | 2 |"),"Amazon summary");
 push("Haugaasen et al. 2010","Brazil nut","dry→wet","recorded primary burial","recorded relocation",244,637,3,38,"published aggregate; relocation and persistence are separate outcomes; latent primary burial direction unresolved");
 push("Haugaasen et al. 2010","Brazil nut","dry→wet","recorded primary burial","original cache persistence",244,637,2,3,"published aggregate; rare recorded persistence, not total survival or establishment");
 const v=d.maine.metric_ranges;
 const m=(context,z)=>push("Merz et al. 2026",context,"Aug→Oct","recorded focal D/E handling","recorded focal D carriage",z.H0,z.H1,z.Y0,z.Y1,"V8 ambiguity scenarios, singleton assumption; equal matched effort weights; not all animals or true carriage",z.q0,z.q1);
 assert(d.maine.feasible===1024&&d.density.scenario_count===1024,"scenario support");m("pooled density",v);
 for(const t of ["low density","high density"])m(t,d.density.WP_by_density[t]);
 const a11=d.beech.cohorts["2018/19"],b11=d.beech.cohorts["2020/21"];
 const endpoints=z=>{assert(z.N===180&&z.observed_ex_situ_germinated===0,"beech source");const loc=[],germ=[];for(let x=0;x<=z.unresolved;x++){for(let y=0;y<=z.unresolved;y++){loc.push((z.located_ex_situ+x)/z.N);germ.push((z.observed_in_situ_germinated+z.observed_ex_situ_germinated+y)/z.N)}}return {ex_situ_fraction:[Math.min(...loc),Math.max(...loc)],total_germination_fraction:[Math.min(...germ),Math.max(...germ)]}};
 const z0=endpoints(a11),z1=endpoints(b11);
 const delta=(a,b)=>[b[0]-a[1],b[1]-a[0]];
 const beech={contrast:"2018/19→2020/21",first:z0,second:z1,ex_situ_change:delta(z0.ex_situ_fraction,z1.ex_situ_fraction),total_germination_change:delta(z0.total_germination_fraction,z1.total_germination_fraction),scope:"separate year contrast; ex-situ location and total germination not nested; no causal or seasonal inference; worst-case missing assignments only"};
 assert(beech.ex_situ_change[0]>0&&beech.total_germination_change[1]<0,"beech direction");
 return {status:"DESCRIPTIVE_STAGE_SYNTHESIS_NOT_META_ANALYSIS",definition:"Conversion ratio = (downstream1/upstream1)/(downstream0/upstream0); distinct nested observation endpoints, no across-stage pooling or universal direction; intervals are conservative marginal envelopes, not CIs.",rows,beech};
}
const inputs=Object.fromEntries(Object.entries(paths).map(([k,p])=>[k, ['ny','amazon'].includes(k)?fs.readFileSync(p,'utf8'):JSON.parse(fs.readFileSync(p,'utf8'))]));
console.log(JSON.stringify(calculate(inputs),null,2));
