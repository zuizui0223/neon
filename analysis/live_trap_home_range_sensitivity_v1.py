from __future__ import annotations
import argparse,csv,hashlib,importlib.util,json,math,statistics,urllib.request
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def load_support():
    p=ROOT/"analysis"/"live_trap_home_range_support_v1.py"
    spec=importlib.util.spec_from_file_location("support",p)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
SUPPORT=load_support()
Z95=1.959963984540054

def convex_hull(points):
    pts=sorted(set((float(x),float(y)) for x,y in points))
    if len(pts)<3: raise ValueError("need >=3 unique points")
    def cross(o,a,b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lower=[]
    for p in pts:
        while len(lower)>=2 and cross(lower[-2],lower[-1],p)<=0: lower.pop()
        lower.append(p)
    upper=[]
    for p in reversed(pts):
        while len(upper)>=2 and cross(upper[-2],upper[-1],p)<=0: upper.pop()
        upper.append(p)
    hull=lower[:-1]+upper[:-1]
    if len(hull)<3: raise ValueError("degenerate hull")
    return hull

def polygon_area(points):
    hull=convex_hull(points)
    return abs(sum(
        hull[i][0]*hull[(i+1)%len(hull)][1]-hull[(i+1)%len(hull)][0]*hull[i][1]
        for i in range(len(hull))
    ))/2.0

def rms_radius(points):
    pts=[(float(x),float(y)) for x,y in points]
    cx=statistics.mean(x for x,y in pts); cy=statistics.mean(y for x,y in pts)
    return math.sqrt(statistics.mean((x-cx)**2+(y-cy)**2 for x,y in pts))

def wilson(k,n,z=Z95):
    p=k/n; z2=z*z; den=1+z2/n
    center=(p+z2/(2*n))/den
    half=z*math.sqrt((p*(1-p)+z2/(4*n))/n)/den
    return max(0,center-half),min(1,center+half)

def download():
    req=urllib.request.Request(SUPPORT.URL,headers={"User-Agent":"live-trap-home-range-effect/1.0"})
    with urllib.request.urlopen(req,timeout=180) as r: raw=r.read()
    if hashlib.sha256(raw).hexdigest()!=SUPPORT.SHA256: raise RuntimeError("source checksum mismatch")
    return list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))

def eligible_detail(rows,estim_lock):
    support=SUPPORT.count_support(rows,estim_lock)
    first,last=SUPPORT.nightly_representations(rows)
    eligible={
        (sp,d["grid"],d["unique_ID"])
        for sp,details in support["species_details"].items()
        for d in details if d["eligible"]
    }
    return support,first,last,eligible

def individual_results(rows,estim_lock):
    support,first,last,eligible=eligible_detail(rows,estim_lock)
    if not support["programme_gate"]["passed"]:
        raise RuntimeError("frozen home-range support gate failed")
    out=[]
    for sp,grid,uid in sorted(eligible):
        keys=sorted(k for k in first if k[:3]==(sp,grid,uid))
        fpts=[SUPPORT.XY[first[k]] for k in keys]
        lpts=[SUPPORT.XY[last[k]] for k in keys]
        af=polygon_area(fpts); al=polygon_area(lpts)
        if af<=0 or al<=0: raise RuntimeError("eligible individual has zero MCP area")
        rf=rms_radius(fpts); rl=rms_radius(lpts)
        ratio=max(af,al)/min(af,al)
        rratio=max(rf,rl)/min(rf,rl) if min(rf,rl)>0 else None
        out.append({
          "species":sp,"grid":grid,"unique_ID":uid,"capture_nights":len(keys),
          "mcp_first_m2":af,"mcp_last_m2":al,
          "area_ratio":ratio,"signed_log_area_ratio":math.log(al/af),
          "material_area_change":ratio>=1.25-1e-12,
          "rms_first_m":rf,"rms_last_m":rl,"rms_ratio":rratio
        })
    return support,out

def species_summary(individuals,sp):
    rows=[r for r in individuals if r["species"]==sp]
    n=len(rows); k=sum(r["material_area_change"] for r in rows)
    lo,hi=wilson(k,n)
    ratios=[r["area_ratio"] for r in rows]
    signed=[r["signed_log_area_ratio"] for r in rows]
    grid_results={}
    for g in sorted({r["grid"] for r in rows}):
        gr=[r for r in rows if r["grid"]==g]
        grid_results[g]={
          "eligible_individuals":len(gr),
          "material_change_count":sum(r["material_area_change"] for r in gr),
          "material_change_fraction":sum(r["material_area_change"] for r in gr)/len(gr),
          "median_area_ratio":statistics.median(r["area_ratio"] for r in gr)
        }
    passed=(lo>0.25 and statistics.median(ratios)>=1.25)
    return {
      "eligible_individuals":n,"material_change_count":k,
      "material_change_fraction":k/n,"wilson95_low":lo,"wilson95_high":hi,
      "median_area_ratio":statistics.median(ratios),
      "q90_area_ratio":statistics.quantiles(ratios,n=10,method="inclusive")[8],
      "median_signed_log_area_ratio":statistics.median(signed),
      "median_mcp_first_m2":statistics.median(r["mcp_first_m2"] for r in rows),
      "median_mcp_last_m2":statistics.median(r["mcp_last_m2"] for r in rows),
      "median_rms_ratio":statistics.median(r["rms_ratio"] for r in rows if r["rms_ratio"] is not None),
      "grid_results":grid_results,"species_gate_passed":passed
    }

def analyze(rows,estim_lock,effect_lock):
    support,individuals=individual_results(rows,estim_lock)
    species={sp:species_summary(individuals,sp) for sp in ("PEMA","PEER")}
    passed=all(species[sp]["species_gate_passed"] for sp in species)
    return {
      "schema":"neon.live_trap_aliasing.downstream_home_range_effect.v1",
      "support_gate":support["programme_gate"],"species":species,
      "programme_gate":{"passed":passed,"decision":effect_lock["pass_decision"] if passed else effect_lock["fail_decision"]},
      "mcp_areas_inspected":True,"mcp_area_ratios_inspected":True,
      "rms_radius_differences_inspected":True,"ecological_model_fits":0
    },individuals

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--estim-lock",type=Path,required=True); ap.add_argument("--effect-lock",type=Path,required=True)
    ap.add_argument("--output-json",type=Path,required=True); ap.add_argument("--output-csv",type=Path,required=True)
    a=ap.parse_args()
    estim=json.loads(a.estim_lock.read_text()); effect=json.loads(a.effect_lock.read_text())
    if effect["state"]!="frozen_before_home_range_effects": raise RuntimeError("effect lock not frozen")
    result,rows=analyze(download(),estim,effect)
    a.output_json.parent.mkdir(parents=True,exist_ok=True)
    a.output_json.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    with a.output_csv.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__": main()
