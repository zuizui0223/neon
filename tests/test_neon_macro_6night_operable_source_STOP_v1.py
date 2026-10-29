"""The original NEON trapStatus 4/5/6 six-night source gate FAILED.

Exercise real saved aggregate result and ensure the ecological runner
returns a structured STOP without fetching original NEON source or
opening any genus×trap recurrence outcome. Not a new biological test.
"""
import os
from unittest import TestCase,main
from unittest.mock import patch

from analysis.run_multiscale_density_estimability_release2026_v3 import TOKEN_ENV
from analysis.run_neon_macro_6night_operable_ecology_v1 import run


class CurrentSixNightOperableStopTests(TestCase):
    def test_saved_18pair_original_source_gate_blocks_all_new_ecological_effects(self):
        with patch.dict(os.environ,{TOKEN_ENV:"DUMMY_ORIGINAL_SOURCE_TOKEN"}):
            with patch("analysis.run_neon_macro_6night_operable_ecology_v1.original_sources_for_two_genus",
                       side_effect=AssertionError("should never retrieve mammal data after STOP")):
                result=run()
        self.assertEqual(result["status"],"STOP_ORIGINAL_ALL6_OPERABLE_STATUS456_SOURCE_GATE")
        self.assertEqual(result["original_exact_two_genus_pair_universe"],158)
        self.assertEqual((result["strict_all_six_456_retained_pairs"],
                          result["strict_retained_independent_sites"],
                          result["strict_retained_domains"]),(18,8,7))
        self.assertTrue(result["new_operable_subcohort_ecological_Z_or_p_NOT_computed"])
        self.assertTrue(result["original_30_site_positive_capture_recurrence_unchanged"])
        self.assertTrue(result["not_a_negative_animal_ecological_effect"])
        self.assertNotIn("DUMMY_ORIGINAL_SOURCE_TOKEN",str(result))


if __name__=="__main__":
    main()
