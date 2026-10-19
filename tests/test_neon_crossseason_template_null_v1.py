"""TDD: fixed-fixed genus-trap null and independent physical-site inference.

All fixtures are artificial. No real NEON spatial response is inspected.
"""
import unittest

from analysis.audit_neon_crossseason_genus_support_v1 import source_event_support
from analysis.neon_crossseason_template_null_v1 import (
    swap_fixed_margins, fixed_fixed_null_for_unit,
    signflip_site_mean_test, crossseason_template_inference
)
from test_neon_crossseason_genus_support_v1 import two_seasons


class NeONCrossSeasonTemplateNullTests(unittest.TestCase):
    def setUp(self):
        self.A={
            "Gen1":{"A1","A2","B1","B2"},
            "Gen2":{"A3","A4","B3","B4"},
            "Gen3":{"C1","C2","D1","D2"},
        }
        self.B={
            "Gen1":{"A1","A2","B1","B2"},
            "Gen2":{"A3","A4","B3","B4"},
            "Gen3":{"C1","C2","D1","D2"},
        }

    def test_fixed_fixed_swap_preserves_row_and_column_margins(self):
        from random import Random
        base=[0b000111,0b111000,0b100100]
        prior_rows=sorted(int(z).bit_count() for z in base)
        def col_sums(vals):
            return tuple(sum(bool(x&(1<<i)) for x in vals) for i in range(6))
        prior_cols=col_sums(base)
        rng=Random(44)
        moves=0
        for _ in range(200):
            moves+=swap_fixed_margins(base,rng,max_proposals=30)
            self.assertEqual(sorted(z.bit_count() for z in base),prior_rows)
            self.assertEqual(col_sums(base),prior_cols)
        self.assertGreater(moves,0)

    def test_identical_spatial_genus_templates_give_positive_recurrence(self):
        z=fixed_fixed_null_for_unit(self.A,self.B,seed=1234,
                                    n_draws=500,burn_in=200,swaps_per_draw=30,
                                    min_effective_draws=50)
        self.assertEqual(z["status"],"INFORMATIVE_FIXED_FIXED_NULL")
        self.assertGreater(z["z"],0)
        self.assertEqual(z["observed_same_genus_same_trap_overlap"],12)
        self.assertGreater(z["null_sd"],0)
        self.assertTrue(z["genus_and_trap_occupancy_margins_preserved"])
        self.assertTrue(z["site_independence_not_claimed"])

    def test_no_possible_swap_is_uninformative_not_false_success(self):
        all_traps={"A1","A2","A3"}
        a={x:set(all_traps) for x in ("G1","G2","G3")}
        z=fixed_fixed_null_for_unit(a,a,seed=12,n_draws=50,
                                    burn_in=30,swaps_per_draw=10,min_effective_draws=8)
        self.assertNotEqual(z["status"],"INFORMATIVE_FIXED_FIXED_NULL")
        self.assertIsNone(z["z"])

    def test_species_order_does_not_change_result(self):
        b=dict(reversed(list(self.B.items())))
        x=fixed_fixed_null_for_unit(self.A,self.B,seed=33,n_draws=130,
                                   burn_in=80,swaps_per_draw=25,min_effective_draws=25)
        y=fixed_fixed_null_for_unit(self.A,b,seed=33,n_draws=130,
                                   burn_in=80,swaps_per_draw=25,min_effective_draws=25)
        self.assertEqual(x,y)

    def test_exact_six_site_signflip_has_p_one_over_64_for_all_positive(self):
        x=signflip_site_mean_test([2.,2.,2.,2.,2.,2.],seed=99)
        self.assertEqual(x["physical_sites"],6)
        self.assertEqual(x["one_sided_site_signflip_p"],1/64)
        self.assertEqual(x["signflip_samples"],64)
        self.assertEqual(x["positive_site_means"],6)

    def test_site_level_inference_cannot_use_fewer_than_eight_sites_as_success(self):
        pairs={f"S{i}":[3.,4.] for i in range(7)}
        out=crossseason_template_inference(pairs,seed=2026101901)
        self.assertEqual(out["status"],"STOP_FEWER_THAN_8_INFORMATIVE_PHYSICAL_SITES")
        self.assertFalse(out["ecological_site_level_criterion_passed"])
        self.assertNotIn("S0",str(out))
        self.assertNotIn("S6",str(out))

    def test_one_site_with_many_pairs_is_still_one_site(self):
        out=crossseason_template_inference({"S1":[2.]*50},seed=2)
        self.assertEqual(out["physical_sites"],1)
        self.assertFalse(out["ecological_site_level_criterion_passed"])

    def test_support_can_pass_private_genus_occupancy_to_null_without_leakage(self):
        plot,trap,tax=two_seasons()
        units=[]
        support=source_event_support(plot,trap,tax,internal_units=units)
        self.assertEqual(support["eligible_primary_pairs"],1)
        self.assertEqual(len(units),1)
        self.assertEqual(set(units[0]["A"]),set(tax))
        self.assertEqual(set(units[0]["B"]),set(tax))
        self.assertNotIn("early-GEN",str(support))
        self.assertFalse(support["crossseason_spatial_overlap_opened"])


if __name__=="__main__":
    unittest.main()
