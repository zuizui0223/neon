"""NEON trapStatus 4/5/6 operability-source sensitivity (NO ecological effects).

Official NEON controlled codes:
  4: >1 capture in one trap; 5: capture; 6: trap set and empty
  0: no data; 1: not set or captures not processed;
  2: trap disturbed/door closed empty; 3: door open with spoor.
An original row for a named trap station is NOT proof it was functional:
the category is required. All SIX original consecutive trap nights must
record source code 4/5/6 for that same station, with no contradictory row.

Source only: returns aggregate source QC and ephemeral same-genus matrices
restricted to fully coded statuses; never computes A×B exact same-trap
recurrence, fixed-fixed null, movement, density or climate effects.
"""
from __future__ import annotations
from collections import defaultdict,Counter
from statistics import mean,median
import re
from analysis.audit_neon_crossseason_genus_support_v1 import _events,_normal_coord

CODE=re.compile(r"^([0-6])(?:\s*-\s*(.*))?$")


def published_trap_status(raw:object)->tuple[str,bool]:
    """Return safe category string and evidence of operational 4/5/6.

    Numeric controlled code must be leading digit. When a description is
    present, it must match the documented official code semantics for
    treated-as-operable states; contradictory source text => UNKNOWN.
    """
    text=str(raw if raw is not None else "").strip()
    m=CODE.fullmatch(text)
    if m is None:return "UNKNOWN",False
    c=m.group(1)
    tail=(m.group(2) or "").strip().lower()
    good=c in ("4","5","6")
    if good and tail:
        if c=="4":
            good=("capture" in tail and
                  ("more than 1" in tail or ">1" in tail or "multiple" in tail))
        elif c=="5":
            good=("capture" in tail and "no capture" not in tail)
        elif c=="6":
            good=("set" in tail and "empty" in tail and
                  "not set" not in tail and "capture" not in tail)
    return (c,good) if good or c in ("0","1","2","3") else ("UNKNOWN",False)


def all_six_operable_source(
    source_two:list[dict],
    plots:list[dict],
    traps:list[dict],
    domains:dict[str,str],
    *,
    expected_pairs:int=158,
    expected_sites:int=30,
    minimum_six_operable_stations:int=90,
    minimum_pairs:int=80,
    minimum_sites:int=18,
    minimum_domains:int=10,
)->tuple[dict,list[dict]]:
    """Source-only exact source event and canonical trap-status audit."""
    if len(source_two)!=expected_pairs or len({x["site"] for x in source_two})!=expected_sites:
        raise ValueError("Original two-genus source size changed")
    chosen,_,_=_events(plots)
    dateidx={}
    for key,info in chosen.items():
        ref=(key[0],key[1],info["dates"])
        if ref in dateidx:
            raise ValueError("Original site plot date keys duplicated")
        dateidx[ref]=key
    source_units=[]
    relevant_events={}
    for u in source_two:
        site,plot=tuple(u["site_plot"])
        if site!=u["site"] or site not in domains:
            raise ValueError("Original source site and domain mismatch")
        a=dateidx.get((site,plot,tuple(u["capture_dates_A"])))
        b=dateidx.get((site,plot,tuple(u["capture_dates_B"])))
        if a is None or b is None or a==b:
            raise ValueError("Exact original six-night site/plot/season events missing")
        if set(u["A"])!=set(u["B"]) or len(u["A"])!=2:
            raise ValueError("Source genus rows no longer exactly two")
        relevant_events[a]=chosen[a];relevant_events[b]=chosen[b]
        source_units.append((u,a,b))
    nights={}
    for event,meta in relevant_events.items():
        if len(meta["nights"])!=3:
            raise ValueError("Original source bout missing three nights")
        for n in meta["nights"]:
            if n in nights and nights[n]!=event:
                raise ValueError("Night reused across different original bouts")
            nights[n]=event

    # Duplicate source rows for a trap/night are normal for trapStatus=4,
    # but ANY unknown/nonoperative row excludes that trap/night.
    operational=defaultdict(lambda:True)
    entries=set()
    bad=Counter()
    parsed_counts=Counter()
    canonical=0
    row_status_total=0
    for r in traps:
        night=str(r.get("nightuid") or "").strip()
        event=nights.get(night)
        if event is None:continue
        if (str(r.get("_site") or "").strip(),
            str(r.get("plotID") or "").strip())!=event[:2]:
            raise ValueError("Pertrapnight row site/plot conflicts with frozen selected bout")
        coord=_normal_coord(r.get("trapCoordinate"))
        if coord is None:
            bad["noncanonical_original_source_station"]+=1
            continue
        canonical+=1
        code,ok=published_trap_status(r.get("trapStatus"))
        parsed_counts[code]+=1
        key=(night,coord)
        if key not in entries:
            entries.add(key)
            operational[key]=ok
        else:
            operational[key]=operational[key] and ok
            bad["duplicate_original_station_night_row"]+=1
        row_status_total+=1

    bynight=defaultdict(set)
    for (night,coord),status in operational.items():
        if status:bynight[night].add(coord)
    common_counts=[]
    bydomain=defaultdict(lambda:{"original_pairs":0,"source_qualifying_pairs":0})
    byyear=Counter()
    failures=Counter()
    qualifying=[]
    for u,a,b in source_units:
        original_nights=tuple(sorted(relevant_events[a]["nights"]))+tuple(
            sorted(relevant_events[b]["nights"]))
        if len(original_nights)!=6 or len(set(original_nights))!=6:
            raise ValueError("Original six-night pairing has overlapping or missing nights")
        common=set.intersection(*(bynight[n] for n in original_nights))
        common_counts.append(len(common))
        dom=domains[u["site"]]
        bydomain[dom]["original_pairs"]+=1
        byyear[str(u["season_ordinal"]//4)]+=1
        sufficient=len(common)>=minimum_six_operable_stations
        matA={g:st & common for g,st in u["A"].items()}
        matB={g:st & common for g,st in u["B"].items()}
        genus_supported=all(len(matA[g])>=2 and len(matB[g])>=2 for g in matA)
        if not sufficient:
            failures["fewer_than_90_all_six_operability_coded_stations"]+=1
        elif not genus_supported:
            failures["genus_two_occupied_station_support_lost"]+=1
        else:
            qualifying.append({
                "site":u["site"],"site_plot":tuple(u["site_plot"]),
                "season_ordinal":u["season_ordinal"],
                "A":matA,"B":matB,
            })
            bydomain[dom]["source_qualifying_pairs"]+=1
            failures["all_six_code456_and_genus_station_support"]+=1
    if len(common_counts)!=len(source_two) or sum(failures.values())!=len(source_two):
        raise AssertionError("Source six-night categorization not exhaustive")
    eligible_sites={u["site"] for u in qualifying}
    eligible_domains={domains[u["site"]] for u in qualifying}
    passed=(len(qualifying)>=minimum_pairs and len(eligible_sites)>=minimum_sites
            and len(eligible_domains)>=minimum_domains)
    return {
        "schema":"neon.macro.six_night_neon_operable_456_source_v1",
        "status":("SOURCE_SIX_NIGHT_OPERABLE_456_GO" if passed
                  else "STOP_OPERABLE_456_SIX_NIGHT_SOURCE_SUPPORT"),
        "source_two_genus_original_pairs":len(source_two),
        "source_original_physical_sites":len({u["site"] for u in source_two}),
        "source_original_three_night_events":len(relevant_events),
        "original_canonical_trap_status_rows":canonical,
        "source_canonical_station_night_keys":len(entries),
        "source_status_code_row_counts":dict(sorted(parsed_counts.items())),
        "source_status_duplicates_and_unknown_location":dict(sorted(bad.items())),
        "unclassified_numeric_or_semantic_status_rows":parsed_counts["UNKNOWN"],
        "source_4_5_6_explicit_operability_evidence":True,
        "source_0_1_2_3_including_disturbed_or_not_set_excluded":True,
        "all_six_verified_status_456_stations":{
            "minimum":min(common_counts),
            "median":median(common_counts),
            "mean":mean(common_counts),
            "maximum":max(common_counts),
        },
        "pair_genus_station_retention_reason_counts":dict(sorted(failures.items())),
        "retained_pairs":len(qualifying),
        "retained_physical_sites":len(eligible_sites),
        "retained_NEON_domains":len(eligible_domains),
        "source_region_counts":dict(sorted(bydomain.items())),
        "source_year_counts":dict(sorted(byyear.items())),
        "original_source_rule":{
            "minimum_all_six_status456_stations":minimum_six_operable_stations,
            "minimum_retained_pairs":minimum_pairs,
            "minimum_physical_sites":minimum_sites,
            "minimum_domains":minimum_domains,
            "passed":passed,
            "new_post_result_feasibility_gate_not_prior_14site_preregistration":True,
        },
        "inference_limits":{
            "all_operable_status_categories_from_NEON_code4_5_6":True,
            "source_station_operability_is_not_capture_detection_probability":True,
            "source_six_night_recorded_presence_alone_not_enough":True,
            "no_original_genus_exact_trap_overlap_opened":True,
            "no_mammal_Z_or_density_habitat_or_10m_patch_effect_computed":True,
            "missing_or_uncoded_status_never_imputed":True,
            "source_identifiers_station_genus_animal_and_dates_not_exported":True,
        },
    },qualifying
