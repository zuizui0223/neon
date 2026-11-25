// V23: exact vertex extrema on published outer sets, no dependencies.
const fs=require('node:fs');
const paths={
  "li": "results/neon_seasonal_intact_routes_v21_20261126.json",
  "lang": "results/neon_lang_wang2016_seasonal_route_bounds_v22_20261126.json",
  "cao": "results/neon_cao2017_establishment_routes_v20_20261126.json",
  "beech": "results/neon_sachser_downstream_fate_v11_20261125.json",
  "v16": "results/neon_sachser_joint_context_v16_20261126.json",
  "liRaw": "data/neon_li2021_seasonal_published_fates_20261124.json"
};
function calculate(d) {
 const eps=1e-10;
 const need=(x,m)=>{if(!x)throw Error(m)};
 const rng=a=>[Math.min(...a),Math.max(...a)];
 const near=(a,b)=>Math.abs(a-b)<eps;
 // Each source's feasible (A,B) outcome states: exact vertices of a convex
 // OUTER SET, not probability draws. A and B share the same released cohort.
 function poly(al,ah,bl,bh,cap){
   need(al>=0&&bl>=0&&al<=ah+eps&&bl<=bh+eps&&al+bl<=cap+eps,"invalid input constraints");
   const lines=[[1,0,al],[1,0,ah],[0,1,bl],[0,1,bh],[1,1,cap]];
   const out=[];
   for(let i=0;i<lines.length;i++)for(let j=i+1;j<lines.length;j++){
     const [a,b,c]=lines[i], [e,f,g]=lines[j],den=a*f-b*e;
     if(Math.abs(den)<eps)continue;
     const x=(c*f-b*g)/den,y=(a*g-c*e)/den;
     if(x>=al-eps&&x<=ah+eps&&y>=bl-eps&&y<=bh+eps&&x+y<=cap+eps&&!out.some(p=>near(p[0],x)&&near(p[1],y)))out.push([Math.max(0,x),Math.max(0,y)]);
   }
   need(out.length>0,"empty outcome set");
   return out;
 }
 function phase(v,N,label,detail,unit="seeds"){
   const A=rng(v.map(x=>x[0])),B=rng(v.map(x=>x[1])),T=rng(v.map(x=>x[0]+x[1]));
   return {label,N,denominator_unit:unit,vertices:v,source:A,moved:B,total:T,detail};
 }
 const rows=[];
 function compare(study,group,endpoint,contrast,sp,a,b,point,scope,context,eligible){
   const vertices=a.vertices.flatMap(x=>b.vertices.map(y=>[y[0]-x[0],y[1]-x[1]]));
   const A=rng(vertices.map(x=>x[0])),B=rng(vertices.map(x=>x[1])),T=rng(vertices.map(x=>x[0]+x[1]));
   const sign=z=>z[0]>eps?"increase":z[1]<-eps?"decrease":Math.abs(z[0])+Math.abs(z[1])<eps?"zero":"unresolved";
   const capLoss=A[1]<-eps&&T[1]<-eps;
   const uncoupledCeiling=A[1]+B[1];
   const pointStatus=point?((point[0]>eps&&point[1]<-eps&&point[0]+point[1]>=-eps)?"source_gain_offsets_moved_loss":(point[0]<-eps&&point[1]>eps&&point[0]+point[1]>=-eps)?"moved_gain_offsets_source_loss":(point[0]<-eps&&point[1]>eps)?"moved_gain_partially_offsets_source_loss":"no_observed_opposing_gain_loss_or_incomplete"):"not_available";
   const row={study,landscape_cluster:group,endpoint,contrast,species:sp,phase0:a,phase1:b,context,scope,formal_meta_eligible:eligible,confirmed_point_delta:point?{source:point[0],moved:point[1],total:point[0]+point[1],classification:pointStatus}:null,delta:{source:A,moved:B,total:T},directions:{source:sign(A),moved:sign(B),total:sign(T)},source_loss_min_if_identified:A[1]<-eps?-A[1]:null,moved_gain_max:B[1],full_moved_compensation_of_source_loss_impossible:capLoss,min_total_loss_if_identified:T[1]<-eps?-T[1]:null,uncoupled_total_upper:uncoupledCeiling,joint_ceiling_tightening:uncoupledCeiling-T[1],robust_source_compensates_moved_loss:A[0]>eps&&B[1]<-eps&&T[0]>=-eps,robust_moved_compensates_source_loss:A[1]<-eps&&B[0]>eps&&T[0]>=-eps};
   need(row.joint_ceiling_tightening>=-eps,"joint bound larger than independent");
   rows.push(row);
 }
 // Match season orientation autumn -> spring, irrespective of calendar order.
 // Li uses rounded percentages only. Source end-state is fixed as printed;
 // M unknown is after removal. No exact count invented.
 const li=d.li.cohorts;
 function liPhase(s){
   const x=li.find(v=>v.season===s);
   const n=d.liRaw.release_design_reported[s].seeds;
   const A=x.source_intact/10000,B=x.removed_intact/10000,M=x.missing_after_removal/10000;
   return phase(poly(A,A,B,B+M,A+B+M),n,s,"Printed aggregate fractions, not reconstructed individual counts; all unknowns after removal.");
 }
 const la=liPhase("autumn"),lb=liPhase("spring");
 compare("Li et al. 2021","northeast_china_li2021","intact/unconsumed recorded state","autumn→spring","four species pooled",la,lb,[lb.source[0]-la.source[0],lb.moved[0]-la.moved[0]],"Two reported seasons; exact calendar year and terminal horizon unresolved; unequal stations, pooled species. Scheduled 60 days; no latent viability.","No independent resource measurement for this comparison used",false);
 need(near(rows[0].delta.total[1],-d.li.unrestricted_missing_fate_envelopes.total_intact_delta[0]),"Li reproduction");
 // Lang published subgroup lower bounds, all other outcomes freely assigned.
 // A>=ignored; A<=1-Emin-Rmin; B>=0; B<=1-Emin-A; preserve inconsistencies.
 const lsp=[...new Set(d.lang.cohorts.map(x=>x.species))];
 for(const sp of lsp){
   function get(s){
     const x=d.lang.cohorts.find(c=>c.species===sp&&c.season===s);
     const [al,ah]=x.source_intact_outer_bounds,[bl,bh]=x.moved_intact_outer_bounds,cap=x.any_intact_outer_bounds[1];
     return phase(poly(al,ah,bl,bh,cap),x.N,s,"Conditional broad outer set from narrative ignored lower and minimally inferred subgroup eaten/removed; no exact cache partition.");
   }
   compare("Lang & Wang 2016","ailaoshan","intact/unconsumed recorded state","autumn→spring",sp,get("autumn"),get("spring"),null,"2013 autumn vs 2014 spring, scheduled 36 days; tree pairing unresolved; subgroup/narrative discrepancies in two species; no visual figure confirmation; conditional source validity.","Nominal trap effort 343 each; capture counts 7→32; qualitative resource context only",false);
   const old=d.lang.contrasts.find(c=>c.species===sp);
   need(near(rows.at(-1).delta.total[0],old.total_intact_change_outer[0])&&near(rows.at(-1).delta.total[1],old.total_intact_change_outer[1]),"Lang reproduction");
 }
 // Cao: recorded established at source plus exact reported after-removal count.
 // Source rates rounded; broad unknown post-removal ceiling allows all removed
 // seeds to establish. Treat source rates within printed precision; no true
 // post-removal fate completeness.
 for(const c of d.cao.cohorts){
   function get(i){
     const a=c.recorded_establishment_at_station[i],b=c.recorded_establishment_after_removal[i],R=c.removed[i];
     const da=a===0?0:.0005, dr=Number.isInteger(R*100+eps)?0.005:0.0005;
     // use 0.5 percentage point for all R upper bounds, conservative w.r.t.
     // mixed printed precision (integer 21% and one-decimal values).
     const rhi=Math.min(1,R+.005),alo=Math.max(0,a-da),ahi=Math.min(1,a+da);
     return phase(poly(alo,ahi,b,rhi,1),c.N_each_year,String(2007+i),"Broad post-removal ceiling; source rounded ±0.05pp (explicit zero fixed), removal upper +0.5pp conservative; not actual missing-count bound.");
   }
   compare("Cao et al. 2017","xishuangbanna_cao","recorded seedling establishment","2007→2008",c.species,get(0),get(1),[c.recorded_establishment_at_station[1]-c.recorded_establishment_at_station[0],c.recorded_establishment_after_removal[1]-c.recorded_establishment_after_removal[0]],"Annual resource contrast, same late-Aug/early-Sep release window; terminal horizon unresolved; no complete missing fates; published percentages, actual source report text only.","Community seed rain 0.85→10/m²; captured rodents 27→7 per nominal 600 trap nights; same landscape",false);
 }
 // Sachser: location (not necessarily a movement history). The missing
 // seeds can contribute to A or B or neither, never both.
 for(const endpoint of ["documented germination by location","intact or germinated by location"]){
   function get(k){
     const x=d.beech.cohorts[k],c=x.reported_position_counts;
     need(x.N===180&&x.unresolved===c.in.missing+c.ex.missing,"beech source");
     const plus=endpoint==="intact or germinated by location";
     const A=(c.in.germinated+(plus?c.in.intact:0))/x.N,B=(c.ex.germinated+(plus?c.ex.intact:0))/x.N,M=x.unresolved/x.N;
     return phase(poly(A,A+M,B,B+M,A+B+M),x.N,k,"Shared missing-fate budget across locations: A+B extra <= M. In/ex situ is recorded final position, not proven never-moved/moved route.");
   }
   const a=get("2018/19"),b=get("2020/21");
   compare("Sachser et al. 2025","rothwald",endpoint,"2018/19→2020/21","Fagus sylvatica",a,b,[b.source[0]-a.source[0],b.moved[0]-a.moved[0]],"Two local seed lots, separate annual cohorts; location only, not complete movement history; separate germination/early state endpoints, not two independent studies.","Beech rain 59.2→543/m²; 44→59 August capture counts per nominal 500 trap nights; no source-level causal inference",false);
   const ref=d.v16.contrast_2020_vs_2018[endpoint.startsWith("documented")?"field_germination_change_bounds":"field_intact_or_germinated_change_bounds"];
   need(rows.at(-1).delta.total.every((x,i)=>near(x,ref[i])),"beech shared budget reproduction");
 }
 need(rows.length===8&&new Set(rows.map(x=>x.landscape_cluster)).size===4,"roster drift");
 // Source validity stress for L. hancei, independent of unknown moved fate:
 // with the printed autumn ignored lower fixed, count of confirmed spring
 // in-situ eaten needed to ensure spring total < autumn lower.
 const h=d.lang.cohorts.find(x=>x.species==="Lithocarpus hancei"&&x.season==="spring");
 const h0=d.lang.cohorts.find(x=>x.species==="Lithocarpus hancei"&&x.season==="autumn");
 const threshold=(1-h0.source_intact_outer_bounds[0])*h.N;
 const minInt=Math.floor(threshold+eps)+1;
 const E=Math.min(...h.possible_in_situ_eaten_counts_from_rounded_subset_pct);
 need(E===54&&minInt===18,"source stress");
 const stress={species:"Lithocarpus hancei",spring_released:h.N,autumn_ignored_lower:h0.source_intact_outer_bounds[0],spring_reported_subset_implied_eaten_min:E,spring_confirmed_in_situ_eaten_count_strict_decline_min:minInt,max_implied_eaten_count_removed_from_lower_bound_still_decline:E-minInt,source_validity_boundary:"Arithmetic sensitivity only: if at least 18 of 600 spring seeds are reliably confirmed eaten in situ, total spring intact < autumn ignored lower. Does NOT establish that 54 counts or ignored rate are correct; disagreement in subgroup denominator remains. With no usable predation information, total decline unidentifiable."};
 const seasonal=rows.filter(x=>x.contrast==="autumn→spring"),ann=rows.filter(x=>x.contrast!=="autumn→spring");
 return {status:"CROSS_SOURCE_PARTIAL_IDENTIFICATION_REGISTER_NOT_META_ANALYSIS",method:"A=recorded source or in-situ successful-state fraction; B=recorded moved or ex-situ successful-state fraction; T=A+B. Per-released-seed fractions within source. Source-specific convex outer sets respect shared fate budget where available. Compute all endpoint extrema over differences of vertices; no probability assigned to uncertainty scenarios. Distinguish early intact-state, seedling establishment, germination and final position. No across-endpoint effect pooling. Source loss robust and T upper<0 means full moved-route compensation impossible under source assumptions, NOT proof actual compensatory gain occurred. Actual recorded compensation requires opposite signs of observed components and total nonnegative. These are different claims.",rows,summary:{rows:rows.length,landscape_clusters:4,seasonal_intact_rows:seasonal.length,seasonal_clusters:new Set(seasonal.map(x=>x.landscape_cluster)).size,seasonal_source_loss_identified:seasonal.filter(x=>x.directions.source==="decrease").length,seasonal_full_moved_compensation_impossible:seasonal.filter(x=>x.full_moved_compensation_of_source_loss_impossible).length,seasonal_clusters_with_conditional_impossibility:new Set(seasonal.filter(x=>x.full_moved_compensation_of_source_loss_impossible).map(x=>x.landscape_cluster)).size,seasonal_robust_actual_full_compensation:seasonal.filter(x=>x.robust_moved_compensates_source_loss||x.robust_source_compensates_moved_loss).length,annual_rows:ann.length,annual_clusters:new Set(ann.map(x=>x.landscape_cluster)).size,annual_confirmed_point_source_compensation:ann.filter(x=>x.confirmed_point_delta?.classification==="source_gain_offsets_moved_loss").length,strict_formal_meta_eligible:rows.filter(x=>x.formal_meta_eligible).length},lang_source_stress:stress,boundary:"Exploratory bounded register, not systematic literature search, no inference of prevalence, prediction validation, p values, random-effects pooling or cross-landscape mechanism. Source conditions and omissions differ; Lang source integrity caveat particularly important. All earlier STOPs preserved."};
}
const inputs=Object.fromEntries(Object.entries(paths).map(([k,p])=>[k,JSON.parse(fs.readFileSync(p,'utf8'))]));
console.log(JSON.stringify(calculate(inputs),null,2));
