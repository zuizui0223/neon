#!/usr/bin/env python3
"""Only source-coded firstnight NEON fate label frequencies, after API codebook STOP.

No day2/3 reencounters or prior spatial effects are computed or read.
615 original selected night1 tags in seven SOURCE-selected physical sites;
391 records with unrecognised revised-era fate strings remain unclassified.
Safely show a small set of frequently recurring controlled-looking labels
for future *official codebook* reconciliation, NEVER infer live release.
"""
from __future__ import annotations
import os,re,json
from collections import Counter,defaultdict
from pathlib import Path

from analysis.run_neon_two_genus_source_v1 import original_sources_for_two_genus
from analysis.audit_multiscale_density_mnka_variation_v1 import _taxonomy
from analysis.neon_macro_firstnight_reencounter_source_v1 import source_first_night_cohort
from analysis.neon_macro_firstnight_fate_source_v1 import (
    initial_fate_source,category,
)
from analysis.audit_neon_crossseason_genus_support_v1 import _normal_tag
from analysis.neon_macro_6night_operable_trap_status_v1 import published_trap_status
from analysis.run_multiscale_density_estimability_release2026_v3 import TOKEN_ENV

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_original_fate_unmapped_controlled_labels_20261028.json"
PRIOR=ROOT/"results/neon_firstnight_original_fate_source_20261028.json"
LIMIT=12
MIN_COUNT=5
LABEL=re.compile(r"^[A-Za-z][A-Za-z0-9, .()/-]{0,48}$")
BLOCK=("site","plot","tag","nightuid","person","email","http",
       "microtus","peromyscus")

def safe_label(v:object)->str|None:
    x=" ".join(str(v if v is not None else "").strip().split())
    lower=x.lower()
    if not LABEL.fullmatch(x) or re.search(r"\d{3,}",x):
        return None
    if any(k in lower for k in BLOCK):return None
    # Source categorization/semantic meaning remains UNMAPPED even if
    # the token reads like "released": official versioned codebook needed.
    return x

def tally_unmapped(labels:list[str],*,expected:int|None=None)->dict:
    """All recorded counts retained without exposing rare raw values."""
    if expected is not None and len(labels)!=expected:
        raise ValueError("Unmapped source labels source-count drift")
    frequencies=Counter(" ".join(x.split()) for x in labels)
    selected=[(raw,num) for raw,num in frequencies.items()
              if num>=MIN_COUNT and safe_label(raw) is not None]
    selected.sort(key=lambda z:(-z[1],z[0]))
    keep=selected[:LIMIT]
    exposed=sum(n for k,n in keep)
    return {
        "n_original_unmapped_source_values":len(labels),
        "n_distinct_raw_unmapped_labels_private":len(frequencies),
        "frequent_safe_original_raw_token_forms":[
            {"normalized_controlled_looking_source_token":safe_label(token),
             "n_firstnight_marked_captures":count,
             "no_release_interpretation_assigned":True}
            for token,count in keep
        ],
        "n_original_unmapped_records_in_displayed_token_forms":exposed,
        "n_original_unmapped_records_with_literal_suppressed":len(labels)-exposed,
        "no_unknown_or_rare_original_tokens_exported":True,
        "raw_fate_labels_are_not_official_release_semantics":True,
    }

def need(value:bool,what:str)->None:
    if not value:raise RuntimeError("ORIGINAL_FATE_UNMAPPED_LABEL_SOURCE_STOP: "+what)

def run()->dict:
    need(bool(os.environ.get(TOKEN_ENV,"").strip()),
         "original NEON token unavailable")
    old=json.loads(PRIOR.read_text(encoding="utf-8"))
    need(old["status"]=="STOP_EXPLICIT_RELEASE_FATE_SOURCE_SUPPORT"
         and old["original_pre_reencounter_firstnight_tag_cohort"]==615
         and (old["fate_categorical_counts_by_original_genus"]["Microtus"]["OTHER_UNMAPPED"],
              old["fate_categorical_counts_by_original_genus"]["Peromyscus"]["OTHER_UNMAPPED"])==(111,280),
         "original immutable seven-site source fate receipt changed")
    strict,two,provenance,plots,traps=original_sources_for_two_genus(
        include_private_source_rows=True,include_capture_fate=True
    )
    need((len(strict),len(two))==(58,158),"source 58+158 original cohort drift")
    _,bytaxon,_=_taxonomy()
    source,private=source_first_night_cohort(two,plots,traps,bytaxon)
    chosen=private["source_selected_genus_pair"]
    need(chosen is not None and tuple(chosen[:2])==("Microtus","Peromyscus")
         and len(chosen[2])==7,"original firstnight seven-site pair drift")
    prior,controls=initial_fate_source(private,traps,plots,bytaxon,
        selected_sites=set(chosen[2]))
    need(prior["original_pre_reencounter_firstnight_tag_cohort"]==615
         and prior["fate_categorical_counts_by_original_genus"]==
             old["fate_categorical_counts_by_original_genus"]
         and prior["status"]=="STOP_EXPLICIT_RELEASE_FATE_SOURCE_SUPPORT",
         "original categorized fate source-reconstruction drift")

    firstnight=private["event_source_dates"]
    night_index=private["event_source_night_index"]
    selected=private["original_firstnight_tagged_animal_genus_by_event"]
    picked={(ev,tag):genus for (ev,tag),genus in selected.items()
            if ev[0] in chosen[2] and genus in chosen[:2]}
    seen=defaultdict(list)
    for row in traps:
        night=str(row.get("nightuid") or "").strip()
        ev=night_index.get(night)
        if ev is None or ev[0] not in chosen[2] or night!=firstnight.get(ev):
            continue
        code,valid=published_trap_status(row.get("trapStatus"))
        if not valid or code not in ("4","5"):continue
        tag=_normal_tag(row.get("tagID"))
        if tag is None or (ev,tag) not in picked:continue
        need((str(row.get("_site") or "").strip(),
              str(row.get("plotID") or "").strip())==ev[:2],
             "original firstnight site/plot drift")
        raw=str(row.get("fate") or "")
        present=bool(row.get("_fate_column_present"))
        seen[(ev,tag)].append((raw,category(raw,present)))
    unmapped=[]
    byera=Counter()
    for key,genus in picked.items():
        if controls["original_firstnight_fate_classes"][key]!="OTHER_UNMAPPED":
            continue
        # Never arbitrarily select among conflicting original fate rows.
        labels=seen.get(key,[])
        need(len(labels)==1 and labels[0][1]=="OTHER_UNMAPPED",
             "original unmapped tag fate is ambiguous")
        unmapped.append(labels[0][0])
        byera[genus]+=1
    need(len(unmapped)==391 and (byera["Microtus"],byera["Peromyscus"])==(111,280),
         "original unmapped firstnight fate cannot be reproduced")
    return {
        "schema":"neon.macro.firstnight_original_post2017_fate_labels_source_only.v1",
        "status":"UNMAPPED_FATE_SOURCE_LABEL_FORMS_AUDITED_NO_SEMANTIC_RECLASSIFICATION",
        "original_source_recapture_genus_comparison":"Microtus vs Peromyscus, seven original source selected sites",
        "original_Neon_release":"RELEASE-2026",
        "original_firstnight_tagged_cohort":615,
        "original_unmapped_genus_counts":{"Microtus":111,"Peromyscus":280},
        "other_unmapped_status_original_2017plus_only":True,
        "safe_frequency_audit":tally_unmapped(unmapped,expected=391),
        "official_categorical_dictionary_still_not_retrieved":True,
        "source_metadata_query_incomplete_not_evidence_dictionary_absent":True,
        "claim_boundaries":{
            "original_explicit_release_6_site_source_gate_still_STOP":True,
            "no_laternight_reencounter_outcomes_accessed":True,
            "no_true_genus_specific_capture_detection_p_inferred":True,
            "cannot_change_original_23_5point_observed_genus_contrast":True,
            "no_raw_id_site_plot_trap_date_source_filename_or_rare_token_export":True,
        },
    }

def main()->int:
    try:
        v=run();code=0
    except Exception as e:
        v={
            "schema":"neon.macro.firstnight_original_post2017_fate_labels_source_only.v1",
            "status":"STOP_ORIGINAL_FATE_UNMAPPED_LABEL_SOURCE_OR_QC",
            "error_class":type(e).__name__,
            "original_genus_reencounter_effect_unchanged":True,
            "no_source_ids_or_raw_values_exported":True,
        };code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(v,indent=2,sort_keys=True))
    return code
if __name__=="__main__":
    raise SystemExit(main())
