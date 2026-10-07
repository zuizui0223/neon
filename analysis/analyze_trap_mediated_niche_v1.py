from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

SPECIES=("CHFA","DKR","LAPM","PEER","PEMA","SKR")
SPECIES_SET=set(SPECIES)
BINS=("EARLY","MIDDLE","LATE")
BIN_INDEX={x:i for i,x in enumerate(BINS)}
CHECK_PAIRS=(("EARLY","MIDDLE"),("MIDDLE","LATE"))
ALL_PAIRS=(("EARLY","MIDDLE"),("MIDDLE","LATE"),("EARLY","LATE"))
FLAGS=tuple(f"{r}{c}" for r in "ABCDEFG" for c in range(1,8))
KR={"DKR","SKR"}

def clean(x):
    return "" if x is None else str(x).strip().upper()

def parse_date(x):
    for fmt in ("%m/%d/%y","%m/%d/%Y","%Y-%m-%d"):
        try: return datetime.strptime(str(x).strip(),fmt).date()
        except ValueError: pass
    raise ValueError(f"bad date {x!r}")

def valid_id(x):
    x=clean(x)
    if not x or x=="NONE" or "MISSING" in x: return ""
    return x

def median(xs):
    return statistics.median(xs) if xs else None

def trap_xy(flag):
    f=clean(flag)
    return ("ABCDEFG".index(f[0]),int(f[1:])-1)

def ring_flags(flag,distance):
    x,y=trap_xy(flag)
    return [f for f in FLAGS if sum(abs(a-b) for a,b in zip((x,y),trap_xy(f)))==distance]

def normal_two_sided(z):
    return math.erfc(abs(z)/math.sqrt(2.0))

def percentile(xs,p):
    z=sorted(xs)
    h=(len(z)-1)*p
    lo=int(math.floor(h)); hi=int(math.ceil(h)); g=h-lo
    return z[lo]*(1-g)+z[hi]*g

def bh(rows):
    valid=sorted([r for r in rows if r.get("p_approx") is not None],key=lambda r:r["p_approx"])
    prev=1.0
    for i in range(len(valid)-1,-1,-1):
        q=min(prev,valid[i]["p_approx"]*len(valid)/(i+1))
        valid[i]["q_bh"]=q; prev=q

def unique_permutations3(v):
    return sorted(set(itertools.permutations(v,3)))

def cz(a,b):
    sa=sum(a); sb=sum(b)
    if sa<=0 or sb<=0: return None
    return 1.0 - 0.5*sum(abs(a[i]/sa-b[i]/sb) for i in range(3))

def community_overlap(sm):
    spp=sorted(sm)
    vals=[]
    for i,a in enumerate(spp):
        for b in spp[i+1:]:
            z=cz(sm[a],sm[b])
            if z is not None: vals.append(z)
    return sum(vals)/len(vals) if vals else None

def ra3_exact(sm):
    spp=sorted(sm)
    choices=[unique_permutations3(sm[s]) for s in spp]
    obs=community_overlap(sm)
    vals=[]
    cur={}
    def rec(i):
        if i==len(spp):
            vals.append(community_overlap(cur)); return
        s=spp[i]
        for p in choices[i]:
            cur[s]=p; rec(i+1)
    rec(0)
    vals.sort()
    mu=sum(vals)/len(vals)
    sd=statistics.stdev(vals) if len(vals)>1 else 0.0
    q025=percentile(vals,.025); q975=percentile(vals,.975)
    status="segregated" if obs<q025 else "aggregated" if obs>q975 else "null"
    return dict(observed=obs,null_mean=mu,null_sd=sd,q025=q025,q975=q975,
                ses=(obs-mu)/sd if sd else None,n_null=len(vals),classification=status)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    with args.input.open(newline="",encoding="utf-8-sig") as f:
        raw=list(csv.DictReader(f))
    for i,r in enumerate(raw):
        r["_row"]=i
        r["_grid"]=clean(r.get("grid"))
        r["_date"]=str(r.get("date","")).strip()
        r["_bin"]=clean(r.get("time_bin"))
        r["_flag"]=clean(r.get("flag"))
        r["_species"]=clean(r.get("species"))
        r["_id"]=valid_id(r.get("unique_ID"))

    # Bout IDs from >7-day gaps, matching the existing San Jacinto reconstruction.
    dates_by_grid=defaultdict(set)
    for r in raw:
        if r["_grid"] and r["_date"]: dates_by_grid[r["_grid"]].add(r["_date"])
    bout={}
    bout_size={}
    for g,ds0 in dates_by_grid.items():
        ds=sorted(ds0,key=parse_date); b=1; last=None; cur=[]
        for d in ds:
            if last is not None and (parse_date(d)-parse_date(last)).days>7:
                bout_size[(g,b)]=len(cur); b+=1; cur=[]
            bout[(g,d)]=b; cur.append(d); last=d
        bout_size[(g,b)]=len(cur)

    # Collapse capture rows to trap x check state.
    cell_rows=defaultdict(list)
    for r in raw:
        if r["_flag"] in FLAGS and r["_bin"] in BINS:
            cell_rows[(r["_grid"],r["_date"],r["_flag"],r["_bin"])].append(r)

    duplicate_cells=sum(len(v)>1 for v in cell_rows.values())
    multi_species_cells=0
    for v in cell_rows.values():
        s={x["_species"] for x in v if x["_species"]}
        if len(s)>1: multi_species_cells+=1

    def state(g,d,flag,bin_):
        arr=cell_rows.get((g,d,flag,bin_),[])
        if not arr: return {"species":"EMPTY","id":"","ambiguous":False}
        s={x["_species"] for x in arr if x["_species"]}
        if len(s)!=1 or "P" in s: return {"species":"AMBIG","id":"","ambiguous":True}
        sp=next(iter(s))
        if sp not in SPECIES_SET: sp="OTHER"
        ids={x["_id"] for x in arr if x["_id"]}
        return {"species":sp,"id":next(iter(ids)) if len(ids)==1 else "","ambiguous":False}

    transitions=[]
    for g,ds in dates_by_grid.items():
        for d in ds:
            b=bout[(g,d)]; bs=bout_size[(g,b)]
            for flag in FLAGS:
                for a,z in CHECK_PAIRS:
                    p=state(g,d,flag,a); n=state(g,d,flag,z)
                    if p["ambiguous"] or n["ambiguous"]: continue
                    transitions.append(dict(grid=g,date=d,flag=flag,bout=b,bout_size=bs,
                                            pair=f"{a}-{z}",prev=p["species"],next=n["species"],
                                            prev_id=p["id"],next_id=n["id"]))

    def grouped_metric(records,pred_prev,pred_next):
        groups=defaultdict(list)
        for r in records: groups[(r["grid"],r["flag"],r["bout"],r["pair"])].append(r)
        obs=exp=var=0.0; n=ng=0
        for arr in groups.values():
            if len(arr)<2: continue
            ng+=1; n+=len(arr)
            A=sum(bool(pred_prev(r)) for r in arr)
            B=sum(bool(pred_next(r)) for r in arr)
            O=sum(bool(pred_prev(r) and pred_next(r)) for r in arr)
            obs+=O; exp+=A*B/len(arr)
            var+=A*B*(len(arr)-A)*(len(arr)-B)/(len(arr)**2*(len(arr)-1))
        z=(obs-exp)/math.sqrt(var) if var else None
        return dict(observed=int(obs),expected=exp,observed_expected=obs/exp if exp else None,
                    z=z,p_approx=normal_two_sided(z) if z is not None else None,n=n,groups=ng)

    # Same-species detector succession.
    same_species={}
    same_species_exact3={}
    for sp in SPECIES:
        same_species[sp]=grouped_metric(transitions,lambda r,s=sp:r["prev"]==s,
                                       lambda r,s=sp:r["next"]==s)
        z=[r for r in transitions if r["bout_size"]==3]
        same_species_exact3[sp]=grouped_metric(z,lambda r,s=sp:r["prev"]==s,
                                              lambda r,s=sp:r["next"]==s)

    # Identity decomposition: expected count under random pairing of next-date records inside group.
    def identity_metric(sp,kind,only_exact3=False):
        groups=defaultdict(list)
        for r in transitions:
            if only_exact3 and r["bout_size"]!=3: continue
            groups[(r["grid"],r["flag"],r["bout"],r["pair"])].append(r)
        obs=exp=0.0
        for arr in groups.values():
            n=len(arr)
            if n<2: continue
            def good(p,q):
                if p["prev"]!=sp or q["next"]!=sp or not p["prev_id"] or not q["next_id"]: return False
                return (p["prev_id"]==q["next_id"]) if kind=="same_id" else (p["prev_id"]!=q["next_id"])
            obs+=sum(good(r,r) for r in arr)
            exp+=sum(good(p,q) for p in arr for q in arr)/n
        return dict(observed=int(obs),expected=exp,observed_expected=obs/exp if exp else None)

    identity={}
    for sp in SPECIES:
        identity[sp]={
            "same_id":identity_metric(sp,"same_id"),
            "different_known_id":identity_metric(sp,"different_id"),
            "same_id_exact3":identity_metric(sp,"same_id",True),
            "different_known_id_exact3":identity_metric(sp,"different_id",True),
        }

    # Dominance-motivated focal contrasts.
    kr=lambda s:s in KR
    same_trap_forward=grouped_metric(transitions,lambda r:kr(r["prev"]),lambda r:r["next"]=="LAPM")
    same_trap_reverse=grouped_metric(transitions,lambda r:r["prev"]=="LAPM",lambda r:kr(r["next"]))
    exact3=[r for r in transitions if r["bout_size"]==3]
    same_trap_forward_exact3=grouped_metric(exact3,lambda r:kr(r["prev"]),lambda r:r["next"]=="LAPM")
    same_trap_reverse_exact3=grouped_metric(exact3,lambda r:r["prev"]=="LAPM",lambda r:kr(r["next"]))

    # Spatial decay: focal KR at one trap, next-check LAPM in Manhattan rings.
    def ring_outcome(g,d,flag,bin_,dist):
        fs=[flag] if dist==0 else ring_flags(flag,dist)
        amb=False
        for f in fs:
            s=state(g,d,f,bin_)
            if s["ambiguous"]: amb=True
            elif s["species"]=="LAPM": return True
        return None if amb else False

    spatial_decay={}
    for label,only3 in (("all",False),("exact3",True)):
        spatial_decay[label]={}
        for dist in (0,1,2):
            rec=[]
            for g,ds in dates_by_grid.items():
                for d in ds:
                    b=bout[(g,d)]; bs=bout_size[(g,b)]
                    if only3 and bs!=3: continue
                    for flag in FLAGS:
                        for a,z in CHECK_PAIRS:
                            ps=state(g,d,flag,a)
                            if ps["ambiguous"]: continue
                            y=ring_outcome(g,d,flag,z,dist)
                            if y is None: continue
                            rec.append(dict(grid=g,date=d,flag=flag,bout=b,bout_size=bs,
                                            pair=f"{a}-{z}",p=ps["species"] in KR,y=y))
            spatial_decay[label][f"manhattan_{dist}"]=grouped_metric(
                rec,lambda r:r["p"],lambda r:r["y"])

    # Temporal decay at the same detector.
    temporal_decay={}
    for label,only3 in (("all",False),("exact3",True)):
        temporal_decay[label]={}
        for a,z in ALL_PAIRS:
            rec=[]
            for g,ds in dates_by_grid.items():
                for d in ds:
                    b=bout[(g,d)]; bs=bout_size[(g,b)]
                    if only3 and bs!=3: continue
                    for flag in FLAGS:
                        p=state(g,d,flag,a); q=state(g,d,flag,z)
                        if p["ambiguous"] or q["ambiguous"]: continue
                        rec.append(dict(grid=g,date=d,flag=flag,bout=b,bout_size=bs,
                                        pair=f"{a}-{z}",prev=p["species"],next=q["species"]))
            temporal_decay[label][f"{a}_{z}"]={
                "KR_to_LAPM":grouped_metric(rec,lambda r:r["prev"] in KR,lambda r:r["next"]=="LAPM"),
                "LAPM_to_KR":grouped_metric(rec,lambda r:r["prev"]=="LAPM",lambda r:r["next"] in KR),
            }

    # Grid leave-one-out.
    grid_loo={}
    for g in map(str,range(1,9)):
        z=[r for r in transitions if r["grid"]!=g]
        grid_loo[f"omit_{g}"]={
            "KR_to_LAPM":grouped_metric(z,lambda r:r["prev"] in KR,lambda r:r["next"]=="LAPM"),
            "LAPM_to_KR":grouped_metric(z,lambda r:r["prev"]=="LAPM",lambda r:r["next"] in KR),
        }

    # Block bootstrap using grid x bout contributions.
    def block_contrib(pred_prev,pred_next):
        groups=defaultdict(list)
        for r in transitions: groups[(r["grid"],r["flag"],r["bout"],r["pair"])].append(r)
        blocks=defaultdict(lambda:[0.0,0.0])
        for arr in groups.values():
            if len(arr)<2: continue
            A=sum(pred_prev(r) for r in arr); B=sum(pred_next(r) for r in arr)
            O=sum(pred_prev(r) and pred_next(r) for r in arr); E=A*B/len(arr)
            k=(arr[0]["grid"],arr[0]["bout"])
            blocks[k][0]+=O; blocks[k][1]+=E
        return blocks
    fw=block_contrib(lambda r:r["prev"] in KR,lambda r:r["next"]=="LAPM")
    rv=block_contrib(lambda r:r["prev"]=="LAPM",lambda r:r["next"] in KR)
    block_keys=sorted(set(fw)|set(rv))
    blocks=[(fw.get(k,[0,0]),rv.get(k,[0,0])) for k in block_keys]
    rng=random.Random(20261007); nboot=20000
    boot_fw=[]; boot_rv=[]; boot_asym=[]
    for _ in range(nboot):
        OF=EF=OR=ER=0.0
        for __ in range(len(blocks)):
            f,r=blocks[rng.randrange(len(blocks))]
            OF+=f[0];EF+=f[1];OR+=r[0];ER+=r[1]
        a=OF/EF; b=OR/ER
        boot_fw.append(a);boot_rv.append(b);boot_asym.append(math.log(a/b))
    point_fw=same_trap_forward["observed_expected"];point_rv=same_trap_reverse["observed_expected"]
    bootstrap={
        "unit":"grid_x_trapping_bout","n_blocks":len(blocks),"replicates":nboot,"seed":20261007,
        "KR_to_LAPM_oe_point":point_fw,
        "KR_to_LAPM_oe_ci":[percentile(boot_fw,.025),percentile(boot_fw,.975)],
        "LAPM_to_KR_oe_point":point_rv,
        "LAPM_to_KR_oe_ci":[percentile(boot_rv,.025),percentile(boot_rv,.975)],
        "oe_ratio_point":point_fw/point_rv,
        "oe_ratio_ci":[math.exp(percentile(boot_asym,.025)),math.exp(percentile(boot_asym,.975))],
        "fraction_KR_to_LAPM_oe_ge_1":sum(x>=1 for x in boot_fw)/nboot,
        "fraction_asymmetry_ge_0":sum(x>=0 for x in boot_asym)/nboot,
    }

    # All directed heterospecific pairs + approximate BH audit.
    directed=[]
    for a in SPECIES:
        for b in SPECIES:
            if a==b: continue
            m=grouped_metric(transitions,lambda r,a=a:r["prev"]==a,lambda r,b=b:r["next"]==b)
            directed.append(dict(source=a,target=b,**m))
    bh(directed)

    # Body mass and direction alignment.
    weights={s:[] for s in SPECIES}
    for r in raw:
        s=r["_species"]
        try: w=float(str(r.get("weight_g","")).strip())
        except ValueError: continue
        if s in SPECIES_SET and 0<w<300: weights[s].append(w)
    masses={s:dict(n=len(weights[s]),median_g=statistics.median(weights[s]),
                   mean_g=sum(weights[s])/len(weights[s])) for s in SPECIES}
    dmap={(r["source"],r["target"]):r for r in directed}
    dyads=[]
    for i,a in enumerate(SPECIES):
        for b in SPECIES[i+1:]:
            heavy,light=(a,b) if masses[a]["median_g"]>=masses[b]["median_g"] else (b,a)
            hl=dmap[(heavy,light)]["observed_expected"]; lh=dmap[(light,heavy)]["observed_expected"]
            if hl and lh:
                dyads.append(dict(heavy=heavy,light=light,
                                  log_mass_ratio=math.log(masses[heavy]["median_g"]/masses[light]["median_g"]),
                                  heavy_to_light_oe=hl,light_to_heavy_oe=lh,
                                  log_direction_ratio=math.log(hl/lh)))
    observed_concordant=sum(d["log_direction_ratio"]<0 for d in dyads)
    mass_values=[masses[s]["median_g"] for s in SPECIES]
    perm_counts=[]
    for vals in itertools.permutations(mass_values):
        mm=dict(zip(SPECIES,vals)); c=0
        for i,a in enumerate(SPECIES):
            for b in SPECIES[i+1:]:
                heavy,light=(a,b) if mm[a]>=mm[b] else (b,a)
                hl=dmap[(heavy,light)]["observed_expected"]; lh=dmap[(light,heavy)]["observed_expected"]
                if hl and lh and hl<lh: c+=1
        perm_counts.append(c)
    # Summarize the directed O/E network as an ordering problem.
    # A is ranked above B when A->B O/E is lower than B->A O/E.
    def hierarchy_score(order):
        pos={sp:i for i,sp in enumerate(order)}
        score=0
        for i,a in enumerate(SPECIES):
            for b in SPECIES[i+1:]:
                upper,lower=(a,b) if pos[a]<pos[b] else (b,a)
                if dmap[(upper,lower)]["observed_expected"] < dmap[(lower,upper)]["observed_expected"]:
                    score+=1
        return score
    species_orders=list(itertools.permutations(SPECIES))
    hierarchy_scores=[hierarchy_score(o) for o in species_orders]
    hierarchy_max=max(hierarchy_scores)
    hierarchy_optimal=[list(o) for o,v in zip(species_orders,hierarchy_scores) if v==hierarchy_max]
    mass_order=tuple(sorted(SPECIES,key=lambda sp:masses[sp]["median_g"],reverse=True))
    mass_order_score=hierarchy_score(mass_order)

    dominance_alignment={
        "species_mass":masses,
        "dyads":dyads,
        "concordant_heavy_to_light_deficit":observed_concordant,
        "n_dyads":len(dyads),
        "mass_rank_permutations":len(perm_counts),
        "exact_upper_tail_fraction":sum(x>=observed_concordant for x in perm_counts)/len(perm_counts),
        "hierarchy":{
            "edge_definition":"A ranks above B when A->B observed/expected is lower than B->A observed/expected",
            "maximum_pairwise_score":hierarchy_max,
            "n_optimal_orders":len(hierarchy_optimal),
            "optimal_orders":hierarchy_optimal,
            "mass_order":list(mass_order),
            "mass_order_score":mass_order_score,
            "exact_fraction_orders_score_at_least_mass":sum(v>=mass_order_score for v in hierarchy_scores)/len(hierarchy_scores),
        },
        "status":"post_result_exploratory_guild_level_pattern",
    }

    def hierarchy_from_records(records):
        local=[]
        for a in SPECIES:
            for b in SPECIES:
                if a==b: continue
                mm=grouped_metric(records,lambda r,a=a:r["prev"]==a,lambda r,b=b:r["next"]==b)
                local.append(dict(source=a,target=b,**mm))
        lm={(r["source"],r["target"]):r for r in local}
        def sc(order):
            pos={sp:i for i,sp in enumerate(order)}
            total=0
            for i,a in enumerate(SPECIES):
                for b in SPECIES[i+1:]:
                    upper,lower=(a,b) if pos[a]<pos[b] else (b,a)
                    u=lm[(upper,lower)]["observed_expected"]
                    v=lm[(lower,upper)]["observed_expected"]
                    if u is not None and v is not None and u<v: total+=1
            return total
        vals=[sc(o) for o in species_orders]
        mx=max(vals)
        opt=[list(o) for o,v in zip(species_orders,vals) if v==mx]
        ms=sc(mass_order)
        return {
            "maximum_pairwise_score":mx,
            "n_optimal_orders":len(opt),
            "optimal_orders":opt,
            "mass_order_score":ms,
            "exact_fraction_orders_score_at_least_mass":sum(v>=ms for v in vals)/len(vals),
        }
    dominance_alignment["interval_hierarchy"]={
        pair:hierarchy_from_records([r for r in transitions if r["pair"]==pair])
        for pair in ("EARLY-MIDDLE","MIDDLE-LATE")
    }

    # Spatial replication of the date-shuffle hierarchy.
    full_optimal_order=dominance_alignment["hierarchy"]["optimal_orders"][0]
    hierarchy_grid_loo={}
    for gdrop in sorted({r["grid"] for r in transitions}):
        h=hierarchy_from_records([r for r in transitions if r["grid"]!=gdrop])
        h["omitted_grid"]=gdrop
        h["full_data_optimal_order_remains_optimal"]=full_optimal_order in h["optimal_orders"]
        hierarchy_grid_loo[f"omit_grid_{gdrop}"]=h
    dominance_alignment["hierarchy"]["leave_one_grid_out_date_shuffle"]=hierarchy_grid_loo
    dominance_alignment["hierarchy"]["leave_one_grid_out_date_shuffle_summary"]={
        "full_data_optimal_order":full_optimal_order,
        "full_data_optimal_order_remains_optimal_in":sum(
            x["full_data_optimal_order_remains_optimal"] for x in hierarchy_grid_loo.values()
        ),
        "n_grid_omissions":len(hierarchy_grid_loo),
        "maximum_pairwise_scores":[x["maximum_pairwise_score"] for x in hierarchy_grid_loo.values()],
        "mass_order_scores":[x["mass_order_score"] for x in hierarchy_grid_loo.values()],
    }

    # Community temporal overlap sensitivity: all captures vs first known capture per individual-night,
    # retaining unknown-ID rows in primary sensitivity.
    focal=[r for r in raw if r["_species"] in SPECIES_SET and r["_bin"] in BINS]
    def nocturnal_time(x):
        try: h,m=map(int,str(x).strip().split(":"))
        except Exception: return 99.0
        if 7<=h<=11: h+=12
        elif h==12: h=24
        elif 0<=h<=6: h+=24
        return h+m/60
    first={}
    for r in focal:
        if not r["_id"]: continue
        k=(r["_grid"],r["_date"],r["_id"])
        score=(BIN_INDEX[r["_bin"]],nocturnal_time(r.get("time")),r["_row"])
        if k not in first or score<first[k][0]: first[k]=(score,r["_row"])
    first_rows={x[1] for x in first.values()}
    first_repr=[r for r in focal if not r["_id"] or r["_row"] in first_rows]

    def season(d):
        m=parse_date(d).month
        if m in (8,9,10): return "FALL"
        if m in (11,12,1): return "WINTER"
        if m in (2,3,4): return "SPRING"
        return "SUMMER"
    def temporal_maps(arr):
        gs=defaultdict(lambda:defaultdict(lambda:[0,0,0]))
        for r in arr: gs[(r["_grid"],season(r["_date"]))][r["_species"]][BIN_INDEX[r["_bin"]]]+=1
        return gs
    ta=temporal_maps(focal); tf=temporal_maps(first_repr)
    raw_deltas=[]; ra3_all=Counter(); ra3_first=Counter(); class_changes=Counter(); ses_delta=[]
    for k in sorted(set(ta)&set(tf)):
        oa=community_overlap(ta[k]); of=community_overlap(tf[k])
        raw_deltas.append(of-oa)
        a=ra3_exact(ta[k]); f=ra3_exact(tf[k])
        ra3_all[a["classification"]]+=1;ra3_first[f["classification"]]+=1
        class_changes[f'{a["classification"]}->{f["classification"]}']+=1
        ses_delta.append(f["ses"]-a["ses"])
    removed=len(focal)-len(first_repr)
    community_sensitivity={
        "all_capture_rows":len(focal),"first_capture_keep_unknown_rows":len(first_repr),
        "removed_identifiable_post_first_rows":removed,
        "raw_czekanowski_delta_first_minus_all":{
            "mean":sum(raw_deltas)/len(raw_deltas),"median":statistics.median(raw_deltas),
            "negative":sum(x<0 for x in raw_deltas),"positive":sum(x>0 for x in raw_deltas),
            "min":min(raw_deltas),"max":max(raw_deltas),
        },
        "ra3_style_exact_enumeration":{
            "all_capture_class_counts":dict(ra3_all),
            "first_capture_class_counts":dict(ra3_first),
            "class_changes":dict(class_changes),
            "ses_delta_mean":sum(ses_delta)/len(ses_delta),
            "ses_delta_median":statistics.median(ses_delta),
            "published_all_capture_reference":"Chock et al. reported temporal aggregation in 7/32 grid-seasons and temporal segregation in 0/32; this exact-enumeration reimplementation is a sensitivity and must disclose any count mismatch.",
        },
    }

    out={
        "schema":"neon.trap_mediated_niche_sequence.v1",
        "status":"post_result_exploratory_ecological_discovery_with_frozen_robustness_protocol",
        "source_sha256_expected":"ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301",
        "data_qc":{
            "rows":len(raw),"duplicate_trap_check_cells":duplicate_cells,
            "multi_species_trap_check_cells":multi_species_cells,
            "valid_same_trap_consecutive_transition_opportunities":len(transitions),
        },
        "same_species_succession":same_species,
        "same_species_succession_exact3":same_species_exact3,
        "identity_decomposition":identity,
        "dominance_focal":{
            "same_trap_KR_to_LAPM":same_trap_forward,
            "same_trap_LAPM_to_KR":same_trap_reverse,
            "same_trap_KR_to_LAPM_exact3":same_trap_forward_exact3,
            "same_trap_LAPM_to_KR_exact3":same_trap_reverse_exact3,
            "spatial_decay":spatial_decay,
            "temporal_decay":temporal_decay,
            "grid_leave_one_out":grid_loo,
            "block_bootstrap":bootstrap,
        },
        "directed_heterospecific_pairs":directed,
        "body_size_direction_alignment":dominance_alignment,
        "community_temporal_overlap_sensitivity":community_sensitivity,
        "claim_boundary":{
            "causal_competition_identified":False,
            "residual_scent_identified":False,
            "natural_encounter_avoidance_identified":False,
            "confirmatory_effect":False,
            "interpretation":"Fine-scale trap-mediated sequence structure is consistent with short-term local avoidance by subordinate LAPM after kangaroo-rat occupancy, but capture/release, odour, bait state, local activity and natural interactions are not separable in these observational data."
        }
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "data_qc":out["data_qc"],
        "same_trap_KR_to_LAPM":same_trap_forward,
        "same_trap_LAPM_to_KR":same_trap_reverse,
        "block_bootstrap":bootstrap,
        "body_size_direction_alignment":{k:v for k,v in dominance_alignment.items() if k!="dyads"},
        "community_temporal_overlap_sensitivity":community_sensitivity,
    },indent=2,sort_keys=True))

if __name__=="__main__":
    main()
