from __future__ import annotations

import argparse
import csv
import json
import random
import re
from collections import Counter, defaultdict
from datetime import datetime

BINS = ("early", "middle", "late")
SPECIES = ("CHFA", "DKR", "LAPM", "PEMA", "PEER", "SKR")
STATES = ("EMPTY",) + SPECIES
TRAPS = tuple(f"{letter}{number}" for letter in "ABCDEFG" for number in range(1, 8))
DOM = {"DKR", "SKR"}
POCKET = {"CHFA", "LAPM"}
INVALID = {"AMBIG", "OTHER"}
EMPTY = ("EMPTY", "")
REPS = 499
SEED = 20261008


def date_of(s):
    for fmt in ("%m/%d/%y", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except (ValueError, AttributeError):
            continue
    return None


def species_of(r):
    x = r["species"].strip().upper()
    return x if x in SPECIES else "OTHER"


def individual_id(r):
    x = r.get("unique_ID", "").strip().upper().replace(" ", "")
    bad = ("", "MISSING", "NONE", "NA", "N/A", "UNKNOWN", "MISSINGMISSING")
    return x if x not in bad and not x.startswith("MISSING") else ""


def value(a, b):
    p, q = a[0], b[0]
    if p in INVALID or q in INVALID:
        return None
    return (
        int(p in SPECIES and p == q),
        int(p in DOM and q in POCKET),
        int(p == "SKR" and q == "CHFA"),
        int(p in SPECIES and q in SPECIES and p != q),
    )


def count_pairs(pairs):
    sums = [0, 0, 0, 0]
    n = 0
    for a, b in pairs:
        v = value(a, b)
        if v is None:
            continue
        n += 1
        for j in range(4):
            sums[j] += v[j]
    return n, sums


def quantile(a, p):
    if not a:
        return None
    xs = sorted(a)
    h = (len(xs) - 1) * p
    lo = int(h)
    hi = min(len(xs) - 1, lo + 1)
    return xs[lo] + (h - lo) * (xs[hi] - xs[lo])


def summarize(obs, null):
    if not null:
        return None
    return {
        "observed": obs,
        "null_median": quantile(null, .5),
        "null_q025": quantile(null, .025),
        "null_q975": quantile(null, .975),
        "upper_tail_fraction": sum(x >= obs for x in null) / len(null),
        "lower_tail_fraction": sum(x <= obs for x in null) / len(null),
        "two_sided_monte_carlo_p": min(
            1.0, 2.0 * min((sum(x >= obs for x in null)+1)/(len(null)+1),
                           (sum(x <= obs for x in null)+1)/(len(null)+1))
        ),
        "n_replicates": len(null),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    with open(args.input, encoding="utf-8-sig", newline="") as handle:
        raw = list(csv.DictReader(handle))

    raw_cells = defaultdict(list)
    nights = defaultdict(set)
    all_dates = defaultdict(set)
    invalid_trap_rows = 0
    for r in raw:
        g = r["grid"].strip()
        d = date_of(r["date"])
        b = r["time_bin"].strip().lower()
        flag = r["flag"].strip().upper()
        if d is None or not g.isdigit() or int(g) not in range(1,9) or b not in BINS:
            continue
        all_dates[g].add(d)
        nights[(g, d)].add(b)
        if flag not in TRAPS:
            invalid_trap_rows += 1
            continue
        raw_cells[(g,d,flag,b)].append((species_of(r), individual_id(r)))

    dates_to_bout = {}
    for g, ds in all_dates.items():
        last = None
        bout = 0
        for d in sorted(ds):
            if last is None or (d-last).days > 7:
                bout += 1
            dates_to_bout[(g,d)] = bout
            last = d

    complete = sorted((g,d) for (g,d),bs in nights.items() if set(BINS) <= bs)
    ambiguous = Counter()
    cell_states = {}
    for (g,d,flag,b), records in raw_cells.items():
        if len(records) == 1:
            cell_states[(g,d,flag,b)] = records[0]
        else:
            cell_states[(g,d,flag,b)] = ("AMBIG", "")
            ambiguous["all_duplicate_cells"] += 1
            if len({x[0] for x in records}) > 1:
                ambiguous["mixed_species_duplicate_cells"] += 1
            else:
                ambiguous["same_species_duplicate_cells"] += 1

    days = {}
    for g,d in complete:
        bins = {}
        for b in BINS:
            bins[b] = [cell_states.get((g,d,f,b), EMPTY) for f in TRAPS]
        days[(g,d)] = bins

    keys = ("same_species", "kangaroo_to_pocket", "SKR_to_CHFA", "heterospecific")
    groups = []
    matrix = Counter()
    identity = Counter()
    pair_count = 0
    excluded = Counter()
    prev_species = Counter()
    next_species = Counter()
    for (g,d),bins in days.items():
        for b1,b2 in zip(BINS, BINS[1:]):
            pairs = list(zip(bins[b1], bins[b2]))
            groups.append((g,d,b1,b2,pairs))
            for a,b in pairs:
                pair_count += 1
                p,q = a[0],b[0]
                if p in INVALID or q in INVALID:
                    excluded["ambiguous_or_other_state"] += 1
                    continue
                matrix[(p,q)] += 1
                prev_species[p] += 1
                next_species[q] += 1
                if p in SPECIES and p == q:
                    if a[1] and b[1]:
                        if a[1] == b[1]:
                            identity["same_individual_identified"] += 1
                        else:
                            identity["same_species_distinct_individuals"] += 1
                    else:
                        identity["same_species_identity_unresolved"] += 1

    observed_n, observed = count_pairs(
        (p for _g,_d,_a,_b,pairs in groups for p in pairs)
    )
    rng = random.Random(SEED)
    permutation_values = [[] for _ in keys]
    for _ in range(REPS):
        stat = [0] * len(keys)
        for _g,_d,_a,_b,pairs in groups:
            prev = [x[0] for x in pairs]
            curr = [x[1] for x in pairs]
            rng.shuffle(curr)
            for a,b in zip(prev,curr):
                v = value(a,b)
                if v is not None:
                    for j in range(len(keys)):
                        stat[j] += v[j]
        for j in range(len(keys)):
            permutation_values[j].append(stat[j])

    by_bout = defaultdict(list)
    for (g,d),bins in days.items():
        by_bout[(g,dates_to_bout[(g,d)])].append((d,bins))
    supported = [(k,sorted(v)) for k,v in by_bout.items() if len(v) >= 2]
    within_bout_observed = [0] * len(keys)
    within_bout_valid = 0
    for key,v in supported:
        for d,bins in v:
            for b1,b2 in zip(BINS,BINS[1:]):
                n,vals = count_pairs(zip(bins[b1], bins[b2]))
                within_bout_valid += n
                for j in range(len(keys)):
                    within_bout_observed[j] += vals[j]

    shift_values = [[] for _ in keys]
    shift_valid = []
    for _ in range(REPS):
        totals = [0]*len(keys)
        valid_total = 0
        for key,v in supported:
            n_dates = len(v)
            perm = list(range(n_dates))
            while any(perm[i] == i for i in range(n_dates)):
                rng.shuffle(perm)
            for i,(_d,prevbins) in enumerate(v):
                nextbins = v[perm[i]][1]
                for b1,b2 in zip(BINS,BINS[1:]):
                    valid, vals = count_pairs(zip(prevbins[b1],nextbins[b2]))
                    valid_total += valid
                    for j in range(len(keys)):
                        totals[j] += vals[j]
        shift_valid.append(valid_total)
        for j in range(len(keys)):
            shift_values[j].append(totals[j])

    result = {
        "schema": "neon.san_jacinto_previous_occupant_transition.v1",
        "status": "post_prior_work_exploratory_before_outcome_inspection",
        "source_rows": len(raw),
        "sampling_scope": {
            "grid_dates_with_any_capture": len(nights),
            "grid_dates_with_all_early_middle_late_capture_bins": len(complete),
            "nominal_traps_per_grid": 49,
            "check_intervals_per_complete_grid_date": 3,
            "possible_adjacent_transitions": pair_count,
            "evaluable_adjacent_transitions": observed_n,
            "excluded_pairs": dict(excluded),
            "invalid_trap_rows": invalid_trap_rows,
            "ambiguous_trap_check_cells_all_dates": dict(ambiguous),
            "complete_grid_dates_per_grid": dict(Counter(g for g,d in complete)),
        },
        "state_counts_before_transition": dict(prev_species),
        "state_counts_after_transition": dict(next_species),
        "transition_matrix": {
            p: {q: matrix[(p,q)] for q in STATES}
            for p in STATES
        },
        "same_species_identity_breakdown": dict(identity),
        "contrast_names": list(keys),
        "observed_contrasts": dict(zip(keys,observed)),
        "within_grid_date_bin_shuffle": {
            k:summarize(observed[j],permutation_values[j])
            for j,k in enumerate(keys)
        },
        "within_grid_bout_cross_night_same_trap_null": {
            "supported_grid_bouts": len(supported),
            "grid_dates_in_supported_bouts": sum(len(v) for k,v in supported),
            "observed_valid_trap_transitions": within_bout_valid,
            "null_valid_transitions_range": [min(shift_valid),max(shift_valid)],
            "metrics": {
                k:summarize(within_bout_observed[j],shift_values[j])
                for j,k in enumerate(keys)
            },
        },
        "claim_boundary": {
            "causal_occupant_effect_identified": False,
            "trap_scent_effect_identified": False,
            "competition_identified": False,
            "selection_condition": "Only grid-dates with a captured animal recorded in all 3 check bins; not an effort-complete census.",
            "empty_cell_assumption": "An unrecorded capture at a trap/check is treated as no recorded capture, provided the grid-date has all three check bins observed somewhere.",
            "duplicate_rule": "Exclude adjacent comparisons touching a multiple-record or non-target-species trap/check cell.",
            "bin_shuffle_null": "Shuffle next-check capture states among traps within the same grid/date/bin transition; controls total abundance but not persistent trap affinity.",
            "cross_night_null": "Derange the next-check nights within grid and monthly bout, holding trap location and check pair fixed; controls stable trap suitability but not all time-varying factors.",
            "identification_note": "Same-individual classifications rely on non-missing tags and may be subject to recording error.",
        },
    }
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result,handle,indent=2,sort_keys=True)
        handle.write("\n")
    print(json.dumps({
        "scope": result["sampling_scope"],
        "observed_contrasts": result["observed_contrasts"],
        "identity": result["same_species_identity_breakdown"],
        "bin_null": result["within_grid_date_bin_shuffle"],
        "bout_null": result["within_grid_bout_cross_night_same_trap_null"],
    },indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
