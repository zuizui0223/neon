#!/usr/bin/env python3
"""Independent UK trap-check data feasibility audit; no new outcome tests."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter,defaultdict
from pathlib import Path

def norm(x):
    return (x or "").strip()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    args=ap.parse_args()

    data=args.input.read_bytes()
    # Some journal endpoints serve an HTML interstitial instead of the CSV.
    prefix=data[:500].lower()
    if b"<html" in prefix or b"<!doctype html" in prefix:
        raise RuntimeError("PLOS data endpoint returned HTML rather than supplemental CSV")

    with args.input.open(newline="",encoding="utf-8-sig") as f:
        rd=csv.DictReader(f)
        cols=list(rd.fieldnames or [])
        records=list(rd)
    expected={"SessionID","TrapID","Seq","AsCaught","MaCaught","MgCaught","Prev"}
    if not expected.issubset(cols):
        raise RuntimeError(f"Unexpected schema; missing {sorted(expected-set(cols))}, saw {cols}")

    def dist(col):
        return dict(Counter(norm(r.get(col)) for r in records).most_common(20))
    dup=Counter((norm(r.get("SessionID")),norm(r.get("TrapID")),norm(r.get("Seq"))) for r in records)
    ses=Counter(norm(r.get("SessionID")) for r in records)
    traps=defaultdict(set)
    seq_by_session=defaultdict(set)
    time_by_session=defaultdict(set)
    for r in records:
        sid=norm(r.get("SessionID"))
        traps[sid].add(norm(r.get("TrapID")))
        seq_by_session[sid].add(norm(r.get("Seq")))
        time_by_session[sid].add(norm(r.get("Time")))
    def captured(x):
        x=norm(x).lower()
        return x not in ("","0","0.0","false","f","na","nan","no","n")
    capture_counts={c:sum(captured(r.get(c)) for r in records)
                    for c in ("AsCaught","MaCaught","MgCaught")}

    out={
      "schema":"neon.uk_previous_occupant_data_feasibility.v1",
      "status":"external_dataset_schema_audit_only",
      "source":"Brouard et al. 2015 PLOS ONE DOI 10.1371/journal.pone.0145006 S1 Data",
      "bytes":len(data),"rows":len(records),
      "columns":cols,
      "session_count":len(ses),
      "trap_check_key_duplicates":sum(n>1 for n in dup.values()),
      "max_rows_per_key":max(dup.values()) if dup else 0,
      "sample_session_trap_and_seq_counts":[{
        "session":sid,
        "rows":ses[sid],
        "traps":len(traps[sid]),
        "check_numbers":len(seq_by_session[sid]),
        "time_labels":sorted(time_by_session[sid])
       } for sid in sorted(ses)[:15]],
      "sequence_distribution":dist("Seq"),
      "time_distribution":dist("Time"),
      "prev_distribution":dist("Prev"),
      "step_distribution":dist("Step"),
      "habitat_distribution":dist("Habitat"),
      "capture_counts":capture_counts,
      "claim_boundary":{
        "independent_empirical_validation_completed":False,
        "new_previous_occupant_effect_discovered":False,
        "interpretation":"This audit verifies whether a previously published independent UK live-trap check dataset can support a separate directional sequence-network comparison. Prior publication already established previous-occupant effects."
      }
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":
    main()
