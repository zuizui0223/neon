"""Source-only nearby NEON base-plot plant cover date support.

Same plotID denotes planned site association, NOT co-located trap ground
cover: mammal grids are usually 150 +/- 50 m offset from plant base plots.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import date
import csv,io

def parse_1m2_source(raw):
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    fields=reader.fieldnames or []
    if len(fields)!=len(set(fields)) or not {"plotID","endDate","eventID","divDataType","percentCover"}<=set(fields):
        raise ValueError("Required source 1m2 field names missing")
    out=[];count=0
    for row in reader:
        count+=1
        if None in row or any(v is None for v in row.values()):
            raise ValueError("Ragged plant cover source")
        plot=str(row.get("plotID") or "").strip()
        value=str(row.get("endDate") or "").strip()
        if not plot or len(value)<10:
            continue
        try: day=date.fromisoformat(value[:10])
        except ValueError: continue
        cover=str(row.get("percentCover") or "").strip()
        try: valid=(0<=float(cover)<=100)
        except (ValueError,TypeError): valid=False
        impractical=str(row.get("samplingImpractical") or "").strip()
        if impractical and impractical.upper() not in ("OK","NA","N/A","NULL","NONE"):
            valid=False
        out.append((plot,day,str(row.get("eventID") or "").strip(),valid,
                    str(row.get("divDataType") or "").strip()))
    return out,count

def plant_source_events(files,original_plot_keys):
    byplot=defaultdict(dict);stats=Counter()
    for site,rows,total in files:
        stats["original_plant_rows"]+=total
        for plot,day,event,numeric,kind in rows:
            stats["plant_rows_with_plot_and_date"]+=1
            key=(site,plot)
            if key not in original_plot_keys: continue
            stats["rows_at_shared_plotID"]+=1
            stem=(day,event)
            byplot[key][stem]=bool(byplot[key].get(stem,False) or numeric)
            stats["matched_rows_with_numeric_cover"]+=numeric
    return byplot,dict(stats)

def _matching(events,trap_days,days,require_numeric):
    return {
        key for key,numeric in events.items()
        if (not require_numeric or numeric) and
        min(abs((key[0]-d).days) for d in trap_days)<=days
    }

def summarize_nearby_plant_bouts(units,byplot,*,expected_pairs=58,
                                 expected_plots=30,expected_sites=14):
    if len(units)!=expected_pairs:raise ValueError("Original 58 comparisons drifted")
    plots=set();sites=set();counts=Counter();blocks=defaultdict(set);plots_ok=defaultdict(set)
    for u in units:
        plot=tuple(u["site_plot"]);site=u["site"]
        A=tuple(u["capture_dates_A"]);B=tuple(u["capture_dates_B"])
        if len(A)!=3 or len(B)!=3 or len(set(A+B))!=6 or plot[0]!=site:
            raise ValueError("Original mammal six-night source changed")
        sites.add(site);plots.add(plot)
        events=byplot.get(plot,{})
        for numeric in (False,True):
            for days in (90,365):
                label=("numeric" if numeric else "event")+"_"+str(days)
                aa=_matching(events,A,days,numeric)
                bb=_matching(events,B,days,numeric)
                distinct=bool(aa and bb and any(a!=b for a in aa for b in bb))
                counts[label+"_A"]+=bool(aa)
                counts[label+"_B"]+=bool(bb)
                counts[label+"_both"]+=bool(aa and bb)
                counts[label+"_distinct"]+=distinct
                if distinct:
                    blocks[label].add(site);plots_ok[label].add(plot)
    if len(plots)!=expected_plots or len(sites)!=expected_sites:
        raise ValueError("Independent mammal geographic universe changed")
    classes=("event_90","event_365","numeric_90","numeric_365")
    for label in classes:
        for suffix in ("A","B","both","distinct"):
            counts.setdefault(label+"_"+suffix,0)
    good=counts["numeric_365_distinct"]>=20 and len(blocks["numeric_365"])>=8 and len(plots_ok["numeric_365"])>=12
    return {
        "original_pair_count":len(units),
        "original_mammal_plots":len(plots),
        "original_mammal_physical_sites":len(sites),
        "plots_with_exact_ID_matched_base_plant_survey":sum(bool(byplot.get(p)) for p in plots),
        "source_period_support_counts":dict(sorted(counts.items())),
        "independent_sites_with_distinct_plant_events":{k:len(blocks[k]) for k in classes},
        "original_plots_with_distinct_plant_events":{k:len(plots_ok[k]) for k in classes},
        "source_min_pairs":20,"source_min_sites":8,"source_min_plots":12,
        "nearby_base_plot_numeric_cover_source_GO":good,
        "same_plotID_not_same_100_trap_locations":True,
        "original_rodent_Z_or_detection_never_opened":True,
        "no_plotIDs_dates_percentCover_or_animal_tags_exported":True,
    }
