from __future__ import annotations

import random
import unittest

from analysis import audit_live_trap_aliasing_individual_cluster_v1 as m


class IndividualClusterAuditTests(unittest.TestCase):
    def test_cluster_summary_preserves_repeat_dependence(self):
        rows=[
            {"species":"PEMA","grid":"1","unique_ID":"a","one_spacing_shift":True},
            {"species":"PEMA","grid":"1","unique_ID":"a","one_spacing_shift":True},
            {"species":"PEMA","grid":"1","unique_ID":"b","one_spacing_shift":False},
            {"species":"PEMA","grid":"2","unique_ID":"c","one_spacing_shift":True},
        ]
        out=m.summarize_species(
            rows,"PEMA",
            rng=random.Random(1),
            replicates=200,
        )
        self.assertEqual(out["individual_grid_clusters"],3)
        self.assertAlmostEqual(out["raw_night_weighted_shift_fraction"],0.75)
        self.assertAlmostEqual(out["equal_individual_shift_fraction"],2/3)
        self.assertAlmostEqual(out["max_single_individual_night_share"],0.5)

    def test_quantile(self):
        self.assertEqual(m.quantile([0,1,2],0.5),1)


if __name__=="__main__":
    unittest.main()
