"""Synthetic-only tests for prior-art roe deer resource closure state table."""
from __future__ import annotations
import unittest
from analysis.reproduce_ranc_2021_resource_closure_state_use_v1 import (
    phase_source_report,source_blob_sha
)

def synthetic(n=2,unknown=False):
    rows=[]
    ids=[str(i+1) for i in range(n)]
    init=[{"exp_id":x} for x in ids]
    for i,animal in enumerate(ids):
        for access,states in (
            ("1",["1"]*24+["2"]*12+["3"]*12),
            ("0",["2"]*24+["3"]*24),
            ("1",["1"]*24+["3"]*24)):
            for j,state in enumerate(states):
                if unknown and i==0 and access=="0" and j==0:
                    state="-9999"
                rows.append({"exp_id":animal,"current_state_code":state,
                             "res_access_m":access})
    return rows,init

class RancResourceClosureSourceTests(unittest.TestCase):
    def test_closure_and_reopening_changes_state_use(self):
        rows,init=synthetic()
        result=phase_source_report(rows,init)
        self.assertEqual(result["source_animal_year_experimental_sequences"],2)
        self.assertEqual(result["original_animal_year_count_where_M_declines_during_closure"],2)
        self.assertEqual(result["original_animal_year_count_where_M_rises_after_reopening"],2)
        before=result["source_three_phase_state_use"]["before_accessible"]
        closed=result["source_three_phase_state_use"]["closed_inaccessible"]
        self.assertAlmostEqual(before["animal_year_equal_weighted_fraction_manipulated_M"],.5)
        self.assertAlmostEqual(closed["animal_year_equal_weighted_fraction_manipulated_M"],0.)
        self.assertTrue(result["no_animal_ID_or_original_individual_trajectory_exported"])

    def test_missing_recorded_state_not_treated_as_vegetation(self):
        rows,init=synthetic(unknown=True)
        z=phase_source_report(rows,init)
        self.assertEqual(z["source_hourly_missing_recorded_state_rows"],1)
        closed=z["source_three_phase_state_use"]["closed_inaccessible"]
        self.assertEqual(closed["source_missing_state_hours_minus9999"],1)
        self.assertEqual(closed["source_observed_valid_hours"],95)

    def test_unexpected_access_phase_is_explicit_stop(self):
        rows,init=synthetic()
        rows[-1]["res_access_m"]="0"
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            phase_source_report(rows,init)

    def test_invalid_original_state_not_imputed(self):
        rows,init=synthetic()
        rows[0]["current_state_code"]="4"
        with self.assertRaisesRegex(ValueError,"UNEXPECTED_STATE"):
            phase_source_report(rows,init)

    def test_noncontiguous_animal_year_is_source_stop(self):
        rows,init=synthetic()
        row=rows.pop(1)
        rows.append(row)
        with self.assertRaisesRegex(ValueError,"NONCONTIGUOUS"):
            phase_source_report(rows,init)

    def test_missing_or_extra_initialization_is_source_stop(self):
        rows,init=synthetic()
        with self.assertRaisesRegex(ValueError,"INITIALIZED"):
            phase_source_report(rows,init[:-1])
        with self.assertRaisesRegex(ValueError,"DUPLICATE_SOURCE"):
            phase_source_report(rows,init+init[:1])

    def test_git_blob_hash_format(self):
        import hashlib
        b=b"abc"
        want=hashlib.sha1(b"blob 3\x00abc").hexdigest()
        self.assertEqual(source_blob_sha(b),want)

if __name__=="__main__":
    unittest.main()
