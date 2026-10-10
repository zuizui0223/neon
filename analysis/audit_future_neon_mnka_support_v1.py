"""Effect-blind future-only genus MNKA support.

Known-alive intervals built from provisional observations only are truncated at
RELEASE-2026 boundary. This is a support diagnostic, NOT a final held-out
predictor or ecological response analysis.
"""
from collections import defaultdict
from analysis.audit_multiscale_density_estimability_v1 import (
    _capture_row,_genus_from_scientific_name,
)

MODE_GENERA=("Chaetodipus","Myodes","Peromyscus","Dipodomys","Sigmodon")
FROZEN_TAXA=("CHHI","PEBO","PEGO","PELE","PEMA","DIOR","SIHI")


def future_only_mnka_support(trap_rows, selected, sessions, target_ids):
    events=selected["events"]
    night_to_event=selected["nights"]
    by_plot=defaultdict(list)
    for key,meta in events.items():
        by_plot[(key[0],key[1])].append((meta["date"],key))
    event_index={}
    for values in by_plot.values():
        for i,(_date,key) in enumerate(sorted(values,key=lambda v:(v[0],v[1][2]))):
            event_index[key]=i

    tag_genus=defaultdict(set)
    tag_events=defaultdict(set)
    for row in trap_rows:
        if not _capture_row(row,"trapStatus","tagID"):
            continue
        taxon=str(row.get("taxonID") or "").strip()
        tag=str(row.get("tagID") or "").strip()
        genus=_genus_from_scientific_name(row.get("scientificName",""))
        event=night_to_event.get(row.get("nightuid",""))
        if event is None or taxon not in target_ids or not tag or not genus:
            continue
        site,plot,_=event
        key=(site,plot,tag)
        tag_genus[key].add(genus)
        tag_events[key].add(event)

    intervals=defaultdict(list)
    ambiguous=0
    for tag,gs in tag_genus.items():
        if len(gs)!=1:
            ambiguous+=1
            continue
        known=sorted({event_index[e] for e in tag_events[tag]})
        if known:
            intervals[(tag[0],tag[1],next(iter(gs)))].append((known[0],known[-1]))

    intervals_by_plot=defaultdict(dict)
    for (s,p,g),hist in intervals.items():
        intervals_by_plot[(s,p)][g]=hist

    mnka={}
    for (site,plot,event),i in event_index.items():
        for genus,hs in intervals_by_plot.get((site,plot),{}).items():
            mnka[(site,plot,event,genus)]=sum(a<=i<=b for a,b in hs)

    series=defaultdict(list)
    eligible=0
    unpaired=0
    for s in sessions:
        if not s.get("primary_complete_session") or s.get("taxon") not in target_ids:
            continue
        if int(s.get("n_repeat_coordinate_supported_tagged_individuals",0))<5:
            continue
        if float(s.get("all_capture_trap_night_fraction_of_observed",1.0))>0.30:
            continue
        if len(s.get("site_ids",[]))!=1 or len(s.get("genus_labels",[]))!=1:
            continue
        eligible+=1
        site=s["site_ids"][0];genus=s["genus_labels"][0]
        index=(site,s["plot_id"],s["event_id"],genus)
        n=mnka.get(index)
        if n is None:
            unpaired+=1
            continue
        series[(s["taxon"],site,s["plot_id"],genus)].append(n)

    def summarize(filterfun):
        supported=[
            (key,values) for key,values in series.items()
            if filterfun(key) and len(values)>=3 and len(set(values))>=2
        ]
        return {
            "series_with_ge3_events_ge2_distinct_future_only_MNKA":len(supported),
            "sessions_in_those_series":sum(len(values) for _,values in supported),
            "sites":len({key[1] for key,_ in supported}),
        }
    return {
        "state":"FUTURE_ONLY_MNKA_SUPPORT_NOT_FINAL_ABUNDANCE_INDEX",
        "candidate_sessions":eligible,
        "unpaired_sessions":unpaired,
        "ambiguous_cross_genus_history_count":ambiguous,
        "mode_genera":{g:summarize(lambda k,g=g:k[3]==g) for g in MODE_GENERA},
        "frozen_taxa":{t:summarize(lambda k,t=t:k[0]==t) for t in FROZEN_TAXA},
        "final_MNKA_support_authorized":False,
        "left_censoring_caveat":"Historic known-alive tags from RELEASE-2026 have not yet been included. Final prospective MNKA must use the continuous frozen+future tag history (without old W/B response reuse).",
        "future_W_B_response_opened":False,
    }
