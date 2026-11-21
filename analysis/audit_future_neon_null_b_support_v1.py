"""Effect-blind null-B reference support on MNKA-varying future taxon×plot series.

The denominator is the exact future Peromyscus analysis cohort, NOT every
m>=5 capture-supported Peromyscus session. Counts are structural upper bounds:
the final scored-centroid comparison may lose individuals or entire sessions.
"""
from collections import Counter, defaultdict

def null_b_screen_on_varying_series(sessions, target_ids, continuous_mnka):
    series = defaultdict(list)
    for s in sessions:
        if not s.get("primary_complete_session") or s.get("taxon") not in target_ids:
            continue
        m = int(s.get("n_repeat_coordinate_supported_tagged_individuals",0))
        if m < 5:continue
        if float(s.get("all_capture_trap_night_fraction_of_observed",1.0))>.30:
            continue
        if len(s.get("site_ids",[]))!=1 or len(s.get("genus_labels",[]))!=1:
            continue
        site=s["site_ids"][0];genus=s["genus_labels"][0]
        n=continuous_mnka.get((site,s["plot_id"],s["event_id"],genus))
        if n is None:continue
        key=(s["taxon"],site,s["plot_id"],genus)
        series[key].append({"N":int(n),"m":m,"event":s["event_id"]})
    by_genus=defaultdict(list)
    eligible_group={}
    for key,rows in series.items():
        if len({r["event"] for r in rows}) != len(rows):
            raise RuntimeError("duplicate response event in fixed future taxon-plot series")
        if len(rows)<3 or len({r["N"] for r in rows})<2:
            continue
        total=sum(r["m"] for r in rows)
        for row in rows:
            by_genus[key[3]].append({
                "taxon":key[0],"site":key[1],"plot":key[2],
                "reference_available":total-row["m"] >= row["m"],
            })
    per={}
    for genus in sorted(by_genus):
        arr=by_genus[genus]
        avail=sum(r["reference_available"] for r in arr)
        per[genus]={
            "varying_series_sessions":len(arr),
            "series":len({(r["taxon"],r["site"],r["plot"]) for r in arr}),
            "sites":len({r["site"] for r in arr}),
            "other_event_reference_opportunity_count":avail,
            "structural_upper_bound_coverage":avail/len(arr),
            "observed_centroid_null_coverage_unopened":True,
        }
    p=per.get("Peromyscus",{})
    base={
        "min_future_sessions":80,
        "min_sites":10,
        "min_taxon_plot_series":20,
        "min_varying_series":15,
        "min_dual_null_complete_fraction":.90,
    }
    base_status={
        "sessions_ge80":p.get("varying_series_sessions",0)>=80,
        "sites_ge10":p.get("sites",0)>=10,
        "series_ge20":p.get("series",0)>=20,
        "varying_series_ge15":p.get("series",0)>=15,
        "nullB_structural_upper_bound_ge90pct":
            p.get("structural_upper_bound_coverage",0)>=.9,
    }
    return {
        "schema":"neon.future_mammal_null_b_structural_screen.v1",
        "source":"continuous known-alive MNKA support; spatial coordinates unopened",
        "per_genus":per,
        "peromyscus_original_future_contract_thresholds":base,
        "peromyscus_structural_screen":base_status,
        "all_structural_upper_bounds_met":all(base_status.values()),
        "can_claim_independent_ecological_confirmation":False,
        "future_W_B_opened":False,
        "inferential_boundary":"A passed structural upper-bound is NOT the prespecified actual centroid null coverage; if it fails, original 90% criterion is impossible for this cohort without forbidden filtering.",
    }
