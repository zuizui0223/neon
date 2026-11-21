"""NEON original RELEASE-2026 first-night fate/disposition SOURCE-ONLY audit.

A 2026 original mam_pertrapnight fate column exists but previous analytic
loader discarded it; source availability can separate known non-release from
subsequent reencounter observation. No new day2/3 matching performed here.

STRICT, pre-original-fate inspection (28 October 2026) category treatment:
raw blank/unknown is MISSING, NEVER interpreted as confirmed release.
Official old NEON manuals report that fate may be left blank for marked-
and-released animals; therefore a strong missingness/strict eligibility
STOP is expected/acceptable. Do not change after seeing the new result.
"""
from __future__ import annotations
from collections import Counter,defaultdict

from analysis.audit_neon_crossseason_genus_support_v1 import _normal_tag,_normal_coord
from analysis.neon_macro_6night_operable_trap_status_v1 import published_trap_status

MISSING={"", "na", "n/a", "nan", "none", "null", "unknown", "unk", "not reported"}
# Conservative codes; current-year categorical Codes documentation may
# warrant a SOURCE-only update after verifying published dictionary, but
# it must not be rewritten after looking at day2/3 outcomes.
RELEASED_EXPLICIT={"released", "released alive", "release", "marked and released"}
DEAD_EXPLICIT={"dead", "mortality", "died"}
ESCAPE_EXPLICIT={"escaped", "escape"}
NON_TARGET={"nontarget", "non-target", "non target"}
NO_RELEASE_OTHER={"voucher", "vouchered", "retained", "euthanized", "euthanasia"}

def category(raw:object, column_present:bool)->str:
    if not column_present:return "COLUMN_ABSENT"
    s=" ".join(str(raw if raw is not None else "").strip().lower().split())
    if s in MISSING:return "BLANK_OR_UNKNOWN"
    if s in RELEASED_EXPLICIT:return "RELEASED_EXPLICIT"
    if s in DEAD_EXPLICIT:return "DEAD_EXPLICIT"
    if s in ESCAPE_EXPLICIT:return "ESCAPED_EXPLICIT"
    if s in NON_TARGET:return "NONTARGET_EXPLICIT"
    if s in NO_RELEASE_OTHER:return "OTHER_NONRELEASE_EXPLICIT"
    if len(s)<=72 and "releas" in s and "not" not in s and "dead" not in s:
        return "RELEASE_TERM_UNMAPPED"
    if "dead" in s or "died" in s or "mortal" in s:
        return "DEATH_TERM_UNMAPPED"
    if "escap" in s:return "ESCAPE_TERM_UNMAPPED"
    if s.isdigit():return "NUMERIC_FATE_UNMAPPED"
    return "OTHER_UNMAPPED"

def initial_fate_source(
    original_source_private:dict,
    traps:list[dict],
    plots:list[dict],
    genus_by_taxon:dict[str,str],
    *,
    selected_genera:tuple[str,str]=("Microtus","Peromyscus"),
    selected_sites:set[str]|None=None,
    expected_sites:int=7,
    min_released_microtus:int=90,
    min_released_peromyscus:int=220,
    min_shared_sites:int=6,
    min_per_genus_site:int=5,
    min_known_fate_fraction:float=.8,
)->tuple[dict,dict]:
    """Original night1 fate only; NEVER accesses later-night capture outcomes.

    selected_sites are fixed by the previous source-only 26-Oct design
    and not chosen using fate/recapture observations. Return aggregate
    public receipt and ephemeral private original tag classifications.
    """
    if selected_genera!=("Microtus","Peromyscus"):
        raise ValueError("Previously source-selected genus identities changed")
    if selected_sites is None or len(selected_sites)!=expected_sites:
        raise ValueError("Previously source-selected physical sites changed")
    firstnight=original_source_private["event_source_dates"]
    nights=original_source_private["event_source_night_index"]
    originals=original_source_private["original_firstnight_tagged_animal_genus_by_event"]
    # exact firstnight keyed cohort, before any future return outcomes
    candidate={
        (ev,tag):genus for (ev,tag),genus in originals.items()
        if ev[0] in selected_sites and genus in selected_genera
    }
    if not candidate:
        raise ValueError("Prior source-only night1 cohort unavailable")
    first_year_by_night={}
    for row in plots:
        night=str(row.get("nightuid") or "").strip()
        if night not in nights:continue
        period=str(row.get("collectDate") or "").strip()[:4]
        if not period.isdigit():continue
        if night in first_year_by_night and first_year_by_night[night]!=period:
            raise ValueError("Original firstnight year conflict")
        first_year_by_night[night]=period

    fate_entries=defaultdict(set)
    site_genus=defaultdict(Counter)
    era=defaultdict(Counter)
    all_selected=Counter()
    fate_rows_read=0
    for row in traps:
        n=str(row.get("nightuid") or "").strip()
        ev=nights.get(n)
        if ev is None or ev[0] not in selected_sites or n!=firstnight.get(ev):
            continue # do not inspect any day2/3 outcome
        if (str(row.get("_site") or "").strip(),
            str(row.get("plotID") or "").strip())!=ev[:2]:
            raise ValueError("Raw original night1 trap site/plot mismatched")
        c,valid=published_trap_status(row.get("trapStatus"))
        if not(valid and c in ("4","5")):continue
        tag=_normal_tag(row.get("tagID"))
        key=(ev,tag)
        if tag is None or key not in candidate:continue
        genus=genus_by_taxon.get(str(row.get("taxonID") or "").strip())
        if genus!=candidate[key]:
            raise ValueError("Previously source-qualified firstnight genus drifted")
        if _normal_coord(row.get("trapCoordinate")) is None:
            raise ValueError("Previously qualified firstnight station drifted")
        fate_rows_read+=1
        fate_entries[key].add(category(row.get("fate"),bool(row.get("_fate_column_present",False))))

    published_genera=defaultdict(Counter)
    selected_period_counts=defaultdict(Counter)
    private={}
    sites_released=defaultdict(Counter)
    missing_source_marked=0
    ambiguous=0
    for key,genus in candidate.items():
        ev,tag=key
        categories=fate_entries.get(key,set())
        if not categories:
            classification="NO_MATCHING_NIGHT1_FATE_ROW"
            missing_source_marked+=1
        elif len(categories)>1:
            classification="CONFLICTING_OR_DUPLICATED_DISPOSITION"
            ambiguous+=1
        else:
            classification=next(iter(categories))
        # Source identifier stays private.
        private[key]=classification
        published_genera[genus][classification]+=1
        all_selected[classification]+=1
        site_genus[ev[0]][genus]+=1
        if classification=="RELEASED_EXPLICIT":
            sites_released[ev[0]][genus]+=1
        night=firstnight[ev]
        year=first_year_by_night.get(night)
        era_label="2017_PLUS" if year is not None and int(year)>=2017 else "PRE_2017_OR_UNKNOWN"
        selected_period_counts[era_label][classification]+=1

    if sum(all_selected.values())!=len(candidate):
        raise AssertionError("Source fate classifications do not account for marked firstnight tags")
    first,second=selected_genera
    released_sites=sorted(s for s in selected_sites
        if sites_released[s][first]>=min_per_genus_site
        and sites_released[s][second]>=min_per_genus_site)
    known={"RELEASED_EXPLICIT","DEAD_EXPLICIT","ESCAPED_EXPLICIT","NONTARGET_EXPLICIT","OTHER_NONRELEASE_EXPLICIT"}
    known_n=sum(v for k,v in all_selected.items() if k in known)
    released_n={g:sum(sites_released[s][g] for s in released_sites) for g in selected_genera}
    pass_gate=(
        len(released_sites)>=min_shared_sites
        and released_n[first]>=min_released_microtus
        and released_n[second]>=min_released_peromyscus
        and known_n/len(candidate)>=min_known_fate_fraction
    )
    return {
        "schema":"neon.macro.original_marked_firstnight_fate_source.v1",
        "status":("SOURCE_EXPLICIT_RELEASE_GATED_REENCOUNTER_GO"
                  if pass_gate else "STOP_EXPLICIT_RELEASE_FATE_SOURCE_SUPPORT"),
        "original_frozen_genus_pair":list(selected_genera),
        "original_frozen_matched_physical_sites":len(selected_sites),
        "original_pre_reencounter_firstnight_tag_cohort":len(candidate),
        "source_firstnight_capture_rows_matched":fate_rows_read,
        "source_firstnight_marked_rows_without_fate_record":missing_source_marked,
        "conflicting_original_firstnight_fates":ambiguous,
        "fate_categorical_counts_by_original_genus":{
            g:dict(sorted(published_genera[g].items())) for g in selected_genera},
        "fate_categorical_counts_overall":dict(sorted(all_selected.items())),
        "fate_categories_by_year_group":{
            e:dict(sorted(v.items())) for e,v in sorted(selected_period_counts.items())},
        "observed_genus_source_firstnight_totals":{
            g:sum(site_genus[s][g] for s in selected_sites) for g in selected_genera
        },
        "source_firstnight_unambiguous_documented_fate_fraction":known_n/len(candidate),
        "source_explicit_release_matched_sites":len(released_sites),
        "released_individuals_in_source_qualified_sites_by_genus":released_n,
        "new_post_result_source_thresholds":{
            "minimum_original_matched_sites_with_five_released_per_genus":min_shared_sites,
            "minimum_released_microtus":min_released_microtus,
            "minimum_released_peromyscus":min_released_peromyscus,
            "minimum_per_genus_per_site":min_per_genus_site,
            "minimum_documented_fate_fraction":min_known_fate_fraction,
            "passed":pass_gate,
        },
        "boundaries":{
            "source_disposition_metadata_is_not_true_survival_after_release":True,
            "empty_original_fate_value_is_not_assumed_released":True,
            "unrecognized_raw_fate_values_not_mapped_ad_hoc":True,
            "original_fate_column_may_be_unavailable_or_blank_before_2017":True,
            "original_7_source_sites_selected_before_any_fate_data":True,
            "day2_or3_tag_matching_or_return_outcome_opened":False,
            "no_new_genus_detection_p_or_habitat_cause_inferred":True,
            "original_same_release_historical_reencounter_results_unchanged":True,
            "no_original_individual_site_plot_station_dates_or_raw_unknown_text_exported":True,
        },
    },{
        "original_firstnight_fate_classes":private,
        "original_preselected_sites_with_five_released_each":released_sites,
    }
