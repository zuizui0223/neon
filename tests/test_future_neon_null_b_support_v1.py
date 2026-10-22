import unittest
from analysis.audit_future_neon_null_b_support_v1 import null_b_screen_on_varying_series

def sess(event,n,m,site="HARV",plot="P1",taxon="PEMA",genus="Peromyscus"):
    return {
        "taxon":taxon,"site_ids":[site],"plot_id":plot,
        "event_id":event,"genus_labels":[genus],
        "n_repeat_coordinate_supported_tagged_individuals":m,
        "all_capture_trap_night_fraction_of_observed":.12,
        "primary_complete_session":True,
    },(site,plot,event,genus),n


class NullBTests(unittest.TestCase):
    def test_correct_mnka_varying_subset_denominator(self):
        a=[
            sess("a",7,5),
            sess("b",10,7),
            sess("c",12,6),
            sess("x",2,5,site="MOAB"),
            sess("y",2,20,site="MOAB"),
        ]
        mapping={key:n for _,key,n in a}
        output=null_b_screen_on_varying_series([r for r,_,_ in a],{"PEMA"},mapping)
        x=output["per_genus"]["Peromyscus"]
        self.assertEqual(x["varying_series_sessions"],3)
        self.assertEqual(x["other_event_reference_opportunity_count"],3)
        self.assertEqual(x["structural_upper_bound_coverage"],1.)
        self.assertFalse(output["can_claim_independent_ecological_confirmation"])

    def test_single_event_too_dominant_lowers_coverage(self):
        a=[sess("a",4,5),sess("b",5,5),sess("c",6,25)]
        out=null_b_screen_on_varying_series(
            [v[0] for v in a],{"PEMA"},{v[1]:v[2] for v in a})
        x=out["per_genus"]["Peromyscus"]
        self.assertEqual(x["other_event_reference_opportunity_count"],2)
        self.assertAlmostEqual(x["structural_upper_bound_coverage"],2/3)
        self.assertFalse(out["peromyscus_structural_screen"]["nullB_structural_upper_bound_ge90pct"])

    def test_event_duplication_fails_closed(self):
        a=[sess("a",4,5),sess("b",5,5),sess("a",7,5)]
        with self.assertRaisesRegex(RuntimeError,"duplicate response event"):
            null_b_screen_on_varying_series(
                [v[0] for v in a],{"PEMA"},{v[1]:v[2] for v in a})


if __name__ == "__main__":
    unittest.main()
