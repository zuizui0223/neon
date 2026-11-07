#!/usr/bin/env python3
"""Effect-blind compare Zenodo MOSA author encounter matrix TOE/SPECIES to raw.

The article reports 19,850 MN individuals, original checksum-verified raw
capture file contains 19,818 distinct stripped TOE values, and the author
encounter matrices together have 19,850 rows. A row is NOT assumed to
correspond to one animal until its actual SPECIES/TOE columns are checked.

Neither MNA, animal space use, W/B nor density associations are computed.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

from analysis.audit_mosa_zenodo_source_schema_v1 import (
    API,RECORD_ID,select_datafile,validate_source_bytes,
    _get,PublishedSourceError
)
from analysis.audit_mosa_encounter_matrix_schema_v1 import FILES

OUT=Path("build/mosa_raw_to_author_TOE_identity_roster_v1.json")
EXPECTED_SOURCE_N=49216
EXPECTED_SOURCE_MN=45433
EXPECTED_MATRIX_ROWS=19850


def compare_tag_identity_rosters(raw_mn_toes:set[str],
                                  matrix_rows:list[tuple[str,str]]) -> dict:
    MN=[tag.strip() for species,tag in matrix_rows
        if str(species).strip().upper()=="MN"]
    values=Counter(v for v in MN if v)
    nonMN=Counter(str(species).strip().upper() for species,_ in matrix_rows
                  if str(species).strip().upper()!="MN")
    tagset=set(values)
    # The archived encounter matrix contains records whose SPECIES is NA.
    # Their TOE may coincide with raw MN identifiers, but an unknown species
    # is NOT automatically a Mastomys individual. Summarize overlaps only.
    unknown_labels={"", "NA", "N/A", "UNKNOWN"}
    unknown=[
        str(tag).strip() for species,tag in matrix_rows
        if str(species).strip().upper() in unknown_labels
    ]
    unknown_ids={tag for tag in unknown if tag}
    raw_missing=raw_mn_toes-tagset
    return {
        "matrix_unknown_species_rows":len(unknown),
        "matrix_unknown_species_blank_TOE_rows":sum(not tag for tag in unknown),
        "matrix_unknown_species_distinct_nonblank_TOE":len(unknown_ids),
        "unknown_species_TOE_matching_raw_MN_missing_from_MN_matrix":
            len(unknown_ids & raw_missing),
        "unknown_species_TOE_already_in_MN_matrix":len(unknown_ids & tagset),
        "unknown_species_TOE_absent_from_raw_MN":len(unknown_ids-raw_mn_toes),
        "raw_MN_TOE_missing_from_MN_and_unknown_species_rows":
            len(raw_mn_toes-(tagset|unknown_ids)),
        "unknown_species_rows_prove_MN_identity":False,
        "matrix_total_rows":len(matrix_rows),
        "matrix_MN_rows":len(MN),
        "matrix_MN_distinct_TOE":len(tagset),
        "matrix_MN_duplicate_TOE_rows":sum(k-1 for k in values.values()),
        "matrix_MN_blank_TOE_rows":sum(not v for v in MN),
        "matrix_nonMN_rows":sum(nonMN.values()),
        "matrix_nonMN_species":dict(sorted(nonMN.items())),
        "raw_MN_distinct_TOE":len(raw_mn_toes),
        "raw_MN_tags_not_in_author_matrix":len(raw_mn_toes-tagset),
        "author_matrix_MN_tags_not_in_raw":len(tagset-raw_mn_toes),
        "raw_and_matrix_identity_rosters_match":tagset==raw_mn_toes,
        "publication_MN_individuals":19850,
        "no_individual_identity_reassignment":True,
        "MNA_or_spatial_density_effects_opened":False,
    }


def _validated_download(f):
    raw=_get(str((f.get("links") or {}).get("self") or ""))
    if len(raw)!=f.get("size"):
        raise PublishedSourceError("author published source length differs")
    checksum=str(f.get("checksum") or "").lower()
    if ":" not in checksum:
        raise PublishedSourceError("published author matrix lacks digest")
    alg,want=checksum.split(":",1)
    if alg not in ("md5","sha256") or hashlib.new(alg,raw).hexdigest()!=want:
        raise PublishedSourceError("published author matrix digest mismatch")
    return raw


def raw_mn_identifiers(meta):
    f=select_datafile(meta)
    raw=_validated_download(f)
    valid=validate_source_bytes(raw,f)
    delim={"SEMICOLON":";","TAB":"\t","COMMA":","}[valid["delimiter_type"]]
    rows=csv.DictReader(io.StringIO(raw.decode(valid["text_encoding"])),
                        delimiter=delim)
    raw_tags=set()
    total=0;mn=0
    for r in rows:
        total+=1
        if str(r.get("SPECIES") or "").upper().strip()!="MN":
            continue
        mn+=1
        tag=str(r.get("TOE") or "").strip()
        if not tag:
            raise PublishedSourceError("published original MN capture with blank TOE")
        raw_tags.add(tag)
    if total!=EXPECTED_SOURCE_N or mn!=EXPECTED_SOURCE_MN:
        raise PublishedSourceError("original MOSA capture/target row count drift")
    return raw_tags,valid


def author_matrix_species_tags(meta):
    by_name={str(f.get("key") or ""):f for f in meta.get("files",[])}
    output=[]
    per_file=[]
    for filename in FILES:
        f=by_name.get(filename)
        if f is None:
            raise PublishedSourceError("MOSA published encounter source missing")
        raw=_validated_download(f)
        try:text=raw.decode("utf-8-sig")
        except UnicodeDecodeError:text=raw.decode("cp1252")
        reader=csv.reader(io.StringIO(text),delimiter=";")
        header=next(reader,[])
        if not {"SPECIES","TOE"}.issubset(set(header)):
            raise PublishedSourceError("missing SPECIES or TOE column in published author encounter matrix")
        a,b=header.index("SPECIES"),header.index("TOE")
        n=0
        for line in reader:
            if len(line)!=len(header):
                raise PublishedSourceError("MOSA encounter source has ragged capture matrix row")
            output.append((line[a],line[b]))
            n+=1
        per_file.append({"file":filename,"rows":n,"MD5":f.get("checksum"),
                         "published_bytes":len(raw)})
    if len(output)!=EXPECTED_MATRIX_ROWS:
        raise PublishedSourceError("MOSA authored total encounter-matrix row count drift")
    return output,per_file


def run():
    meta=json.loads(_get(API).decode("utf-8"))
    if int(meta.get("id",-1))!=RECORD_ID:
        raise PublishedSourceError("Zenodo MOSA record identity mismatch")
    raw_tags,source=raw_mn_identifiers(meta)
    matrix_rows,parts=author_matrix_species_tags(meta)
    comp=compare_tag_identity_rosters(raw_tags,matrix_rows)
    return {
        "schema":"neon.MOSA_raw_to_author_encounter_identity.v1",
        "status":"AUTHOR_ENCOUNTER_TOE_COMPARE_COMPLETE_IDENTITY_GUARD_UNDECIDED",
        "comparison":comp,
        "source_original_csv_md5":source["verified_checksum"],
        "encounter_original_matrix_parts":parts,
        "raw_TOE_individual_level_inference_authorized":False,
        "provisional_MOSA_MNA_computation_unsealed":False,
        "MOSA_W_B_or_density_slopes_unsealed":False,
        "ecological_claim_boundary":"Matrix rows are not automatically unique animals. Compare its target species and TOE values exactly with original raw capture histories; do not amend fixed biological hypotheses based on any identity discrepancy.",
    }


if __name__=="__main__":
    try:r=run()
    except (PublishedSourceError,RuntimeError,ValueError,OSError) as e:
        r={"schema":"neon.MOSA_raw_to_author_encounter_identity.v1",
           "status":"STOP_AUTHOR_IDENTITY_SOURCE_UNVERIFIED",
           "error":str(e)[:400],
           "MOSA_W_B_or_density_slopes_unsealed":False}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps(r,indent=2,sort_keys=True))
    if r["status"]!="AUTHOR_ENCOUNTER_TOE_COMPARE_COMPLETE_IDENTITY_GUARD_UNDECIDED":
        raise SystemExit(3)
