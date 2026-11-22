"""Source-receipt locked unit tests for retrospective Gu 2025 hoarding bounds."""
import copy
import json
from pathlib import Path
from fractions import Fraction
import tempfile
import unittest
from unittest.mock import patch
import sys

from analysis.gu2025_scatter_hoarding_partial_ID_v1 import (
    DEFAULT_INPUT,compute,main,validate_receipt
)

class GuArchivePartialIdentificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=json.loads(DEFAULT_INPUT.read_text(encoding="utf-8"))

    def test_original_source_identity_and_archive_row_grain(self):
        x=validate_receipt(self.source)
        self.assertEqual(sum(map(sum,(d.values() for d in x.values()))),536)
        self.assertEqual(self.source["distinct_seed_codes"],735)
        self.assertEqual(self.source["archive_rows"],738)

    def test_species_difference_may_have_either_sign_with_unknown_M(self):
        z=compute(self.source)
        self.assertLess(z["N_minus_A_cache_fraction_sharp_row_partial_ID_lower"],0)
        self.assertGreater(z["N_minus_A_cache_fraction_sharp_row_partial_ID_upper"],0)
        self.assertAlmostEqual(z["N_minus_A_cache_fraction_sharp_row_partial_ID_lower"],
                               -0.27821336435833877,places=12)
        self.assertAlmostEqual(z["N_minus_A_cache_fraction_sharp_row_partial_ID_upper"],
                               0.27084492555684825,places=12)
        self.assertAlmostEqual(z["N_confucianus_minus_A_draco_cache_fraction_among_only_known_fates"],
                               Fraction(18,122)-Fraction(28,255),places=12)

    def test_record_unknown_M_is_not_nonhoard_and_rare_species_retained(self):
        z=compute(self.source)
        ap=z["source_species_row_metrics"]["Apodemus draco"]
        self.assertEqual(ap["original_rows_with_recorded_known_fate"],255)
        self.assertEqual(ap["original_M_unknown_fate_rows"],118)
        self.assertGreater(ap["partial_ID_max_SHI_fraction_if_all_M_SHI"],
                           ap["partial_ID_min_SHI_fraction_if_all_M_NOT_shi"])
        rare=z["source_species_row_metrics"]["Niviventer fulvescens"]
        self.assertEqual(rare["original_species_assigned_row_count"],4)
        self.assertEqual(rare["original_M_unknown_fate_rows"],2)
        self.assertEqual(rare["partial_ID_max_SHI_fraction_if_all_M_SHI"],0.5)

    def test_confirmed_consumption_dominates_worst_case_scatter_hoarding(self):
        z=compute(self.source)
        self.assertEqual(z["assigned_species_confirmed_EAR_or_EIS"],333)
        self.assertEqual(z["assigned_species_max_possible_SHI_including_every_missing_M"],203)
        self.assertEqual(z["robust_positive_count_margin_original_rows"],130)
        self.assertEqual(z["minimum_positive_margin_after_any_three_duplicate_rows_removed"],127)
        self.assertTrue(z["confirmed_eating_exceeds_even_all_M_as_SHI"])
        expected={
            "Apodemus draco":(227,146,81),
            "Niviventer confucianus":(104,55,49),
            "Niviventer fulvescens":(2,2,0)
        }
        for name,(eaten,max_shi,margin) in expected.items():
            x=z["source_species_row_metrics"][name]
            self.assertEqual(x["original_confirmed_eaten_EAR_plus_EIS"],eaten)
            self.assertEqual(x["max_possible_primary_SHI_if_all_missing_M_are_scatter_hoarded"],max_shi)
            self.assertEqual(x["confirmed_eaten_minus_max_possible_primary_SHI_rows"],margin)
            self.assertEqual(x["consumption_outnumbers_max_possible_primary_SHI_among_record_rows"],
                             margin>0)

    def test_shared_missing_fate_tipping_point_is_hypothetical_not_mar(self):
        z=compute(self.source)
        self.assertEqual(z["common_hypothetical_missing_M_tipping_exact_fraction"],
                         "2262/4961")
        self.assertTrue(z["hypothetical_common_missing_fraction_IS_NOT_assumed_MAR_or_true_biology"])

    def test_duplicated_seed_codes_cannot_be_relabelled_independent_seeds(self):
        y=copy.deepcopy(self.source)
        y["archive_rows"]=735
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            compute(y)
        y=copy.deepcopy(self.source)
        y["nonidentical_repeated_code_groups"]=0
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            compute(y)

    def test_falsified_species_counts_fail_before_effect(self):
        y=copy.deepcopy(self.source)
        y["rows_by_assigned_species_and_fate"]["Niviventer confucianus"]["M"]+=1
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            compute(y)

    def test_wrong_upstream_sha_or_version_fails(self):
        y=copy.deepcopy(self.source)
        y["manifest"]["files"][0]["sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            compute(y)
        y=copy.deepcopy(self.source)
        y["manifest"]["doi"]="10.6084/m9.figshare.29815622.v1"
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            compute(y)

    def test_output_argument_cannot_overwrite_input(self):
        with patch.object(sys,"argv",["prog","--source",str(DEFAULT_INPUT),
                                     "--output",str(DEFAULT_INPUT)]):
            with self.assertRaisesRegex(ValueError,"OUTPUT_ALIASES_SOURCE"):
                main()

    def test_json_output_contains_no_seed_ids_or_individual_ids(self):
        z=compute(self.source)
        assert "Dispersal" not in z
        self.assertTrue(z["no_independent_seed_sampling_variance_or_p_value_calculated"])
        self.assertTrue(z["one_NEON_ecology_Draft_SUBMISSION_HOLD"])
        text=json.dumps(z)
        self.assertNotIn('"PIT"',text)
        self.assertNotIn('"Code"',text)
        self.assertNotIn('"Seed"',text)

if __name__=="__main__":
    unittest.main()
