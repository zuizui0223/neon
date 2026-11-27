// Independent replay on derived V27 context records; no source acquisition.
const fs=require('node:fs');
function score(data,raw){
const mean=a=>a.reduce((s,x)=>s+x,0)/a.length;
const sites=[...new Set(data.map(r=>r.site))].sort();
const d=data.map(r=>{const m=r.mammal*(raw?1:100/r.nights),b=r.bird*(raw?1:100/r.nights);return {...r,duration:Math.log(r.nights),intensity:Math.log1p(m+b),balance:Math.log1p(m)-Math.log1p(b)}});
const models={M0:["duration"],M1:["duration","early"],M2:["duration","intensity","balance"],M3:["duration","early","intensity"],M4:["duration","early","intensity","balance"]};
const dot=(x,y)=>x.reduce((a,v,i)=>a+v*y[i],0);
function solve(a,b){a=a.map((r,i)=>[...r,b[i]]);const n=b.length;for(let i=0;i<n;i++){let p=i;for(let j=i+1;j<n;j++)if(Math.abs(a[j][i])>Math.abs(a[p][i]))p=j;[a[i],a[p]]=[a[p],a[i]];const q=a[i][i];if(Math.abs(q)<1e-12)throw Error("singular");a[i]=a[i].map(x=>x/q);for(let j=0;j<n;j++)if(j!==i){const z=a[j][i];a[j]=a[j].map((x,k)=>x-z*a[i][k]);}}return a.map(r=>r[n]);}
const clip=x=>Math.min(1,Math.max(-1,x));
const folds=sites.map(site=>{
const tr=d.filter(r=>r.site!==site),te=d.filter(r=>r.site===site),key=r=>r.species+"|"+r.forest,groups={};
for(const r of tr)(groups[key(r)]??=[]).push(r);
if(te.some(r=>new Set(groups[key(r)].map(q=>q.site)).size<2))throw Error("support");
const mu=Object.fromEntries(Object.entries(groups).map(([k,v])=>[k,Object.fromEntries(["duration","early","late","intensity","balance"].map(f=>[f,mean(v.map(r=>r[f]))]))]));
const center=(r,f)=>r[f]-mu[key(r)][f], y=tr.map(r=>center(r,"late")), mse={},coef={};
for(const [name,fs] of Object.entries(models)){
const cols=fs.map(f=>tr.map(r=>center(r,f))),sd=cols.map(c=>Math.sqrt(mean(c.map(x=>x*x))));
if(sd.some(x=>x<=1e-12))throw Error("constant");
const X=cols.map((c,i)=>c.map(x=>x/sd[i]));
const beta=solve(X.map((c,i)=>X.map((z,j)=>dot(c,z)+(i===j?1:0))),X.map(c=>dot(c,y)));
coef[name]=Object.fromEntries(fs.map((f,i)=>[f,beta[i]/sd[i]]));
mse[name]=mean(te.map(r=>(r.late-clip(mu[key(r)].late+dot(beta,fs.map((f,i)=>center(r,f)/sd[i]))))**2));
}
const x=tr.map(r=>center(r,"early")),b=dot(x,y)/dot(x,x);
mse.V26_reference=mean(te.map(r=>(r.late-clip(mu[key(r)].late+b*center(r,"early")))**2));
mse.unchanged_early=mean(te.map(r=>(r.late-r.early)**2));
return {site,n:te.length,mse,coef};
});
const rm=Object.fromEntries(Object.keys(folds[0].mse).map(k=>[k,Math.sqrt(mean(folds.map(f=>f.mse[k])))]));
const contrasts={};for(const [a,b] of [["M4","M1"],["M4","M3"],["M2","M0"]]){const win=folds.filter(f=>f.mse[a]<f.mse[b]).length;contrasts[a+"_vs_"+b]={rmse_gain:rm[b]-rm[a],relative_rmse_gain:1-rm[a]/rm[b],sites_improved:win,meets_descriptive_gate:rm[a]<rm[b]&&win>=6};}
return {equal_site_RMSE:rm,contrasts,site_folds:folds};
}
const d=JSON.parse(fs.readFileSync('results/neon_joyce_camera_increment_v27_20261127.json','utf8'));console.log(JSON.stringify({primary:score(d.context_records,false),raw_count_sensitivity:score(d.context_records,true)},null,2));
