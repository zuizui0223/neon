// V14 trait source QA only, no capture outcomes. Run from repo root.
const fs=require('node:fs');
function audit(raw){
 const lines=raw.trim().split(/\r?\n/),h=lines[0].split(",");if(lines.some(l=>l.split(",").length!==h.length))throw Error("unexpected CSV quoting or width");
 const rs=lines.slice(1).map(l=>Object.fromEntries(l.split(",").map((v,i)=>[h[i],v])));
 if(rs.length!==132||new Set(rs.map(r=>r.taxon_id)).size!==132)throw Error("roster mismatch");
 const cols=["det_inv","det_vend","det_vect","det_vfish","det_vunk","det_scav","det_fruit","det_nect","det_seed","det_plantother"];
 const g={};let known=0,complete=0,non100=0;
 for(const r of rs){
  const genus=r.species_name.split(" ")[0];
  const z=g[genus]??={n:0,reported:0,seed:[],fullvectors:[],missing:[]};z.n++;
  if(r.det_seed_provenance==="reported"){const v=Number(r.det_seed);if(r.det_seed===""||!Number.isFinite(v)||v<0||v>100)throw Error("bad seed value");known++;z.reported++;z.seed.push(v)}
  else z.missing.push(r.species_name);
  if(cols.every(c=>r[c+"_provenance"]==="reported"&&r[c]!==""&&Number.isFinite(Number(r[c])))){
   const vec=cols.map(c=>Number(r[c]));if(vec.some(v=>v<0||v>100))throw Error("bad diet vector");complete++;if(Math.abs(vec.reduce((a,b)=>a+b,0)-100)>1e-9)non100++;z.fullvectors.push(vec.join(","))
  }
 }
 const summary=Object.entries(g).sort(([a],[b])=>a.localeCompare(b)).map(([genus,z])=>({genus,target_species:z.n,reported_seed_species:z.reported,unique_reported_seed_values:[...new Set(z.seed)].sort((a,b)=>a-b),complete_diet_vectors:z.fullvectors.length,distinct_complete_diet_vectors:new Set(z.fullvectors).size,missing_species:z.missing}));
 const multi=summary.filter(z=>z.reported_seed_species>=2);
 if(known!==111||multi.length!==18||multi.some(z=>z.unique_reported_seed_values.length!==1))throw Error("unexpected reported coverage");
 return {status:"TRAIT_SOURCE_AUDIT_ONLY",n_species:rs.length,reported_seed:known,missing_seed:rs.length-known,genus_count:summary.length,genus_with_any_seed:summary.filter(z=>z.reported_seed_species>0).length,multispecies_reported_genus:multi.length,multispecies_same_seed_value:multi.filter(z=>z.unique_reported_seed_values.length===1).length,complete_reported_diet_vectors:complete,non100_diet_vectors:non100,multispecies_complete_vector_genus:summary.filter(z=>z.complete_diet_vectors>=2).length,multispecies_identical_full_vector_genus:summary.filter(z=>z.complete_diet_vectors>=2&&z.distinct_complete_diet_vectors===1).length,genus_summaries:summary};
}
console.log(JSON.stringify(audit(fs.readFileSync("data/derived/combine_target_pool_traits_v1.csv",'utf8')),null,2));
