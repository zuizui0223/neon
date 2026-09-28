from __future__ import annotations

import unittest

from analysis import neon_unseen_heteromyid_highinfo_effects_v1 as m


class UnseenHighinfoEffectTests(unittest.TestCase):
    def test_family_weights_species_equally(self):
        rows=[
            {"species":"A alpha","site":"S1","n_recapture_male":5,"n_recapture_female":5,"delta_movement":1.0},
            {"species":"A alpha","site":"S1","n_recapture_male":5,"n_recapture_female":5,"delta_movement":1.0},
            {"species":"B beta","site":"S2","n_recapture_male":5,"n_recapture_female":5,"delta_movement":0.0},
            {"species":"C gamma","site":"S3","n_recapture_male":5,"n_recapture_female":5,"delta_movement":0.5},
        ]
        out=m.movement_effect(rows,species_set=["A alpha","B beta","C gamma"],n_min=5)
        self.assertAlmostEqual(out["family"]["effect"],0.5)

    def test_two_thirds_positive_rule(self):
        rows=[
            {"species":"A alpha","site":"S1","n_recapture_male":5,"n_recapture_female":5,"delta_movement":1.0},
            {"species":"B beta","site":"S2","n_recapture_male":5,"n_recapture_female":5,"delta_movement":1.0},
            {"species":"C gamma","site":"S3","n_recapture_male":5,"n_recapture_female":5,"delta_movement":-0.01},
        ]
        out=m.movement_effect(rows,species_set=["A alpha","B beta","C gamma"],n_min=5)
        self.assertEqual(out["required_positive_species"],2)
        self.assertEqual(len(out["positive_species"]),2)

    def test_discovery_species_remain_excluded_by_estimability_module(self):
        self.assertFalse(m.EST.is_unseen_heteromyid("Dipodomys ordii"))
        self.assertTrue(m.EST.is_unseen_heteromyid("Perognathus parvus"))


if __name__=="__main__":
    unittest.main()
