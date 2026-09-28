from __future__ import annotations

import unittest

from analysis import neon_sex_recapture_effects_v1 as m


class RecaptureEffectTests(unittest.TestCase):
    def test_individual_movement_uses_successive_nights(self):
        rows=[
            {
                "tagID":"A","sex":"M","collectDate":"2026-01-01",
                "nightuid":"N1","uid":"1","namedLocation":"P","trapCoordinate":"A1",
            },
            {
                "tagID":"A","sex":"M","collectDate":"2026-01-02",
                "nightuid":"N2","uid":"2","namedLocation":"P","trapCoordinate":"A2",
            },
            {
                "tagID":"A","sex":"M","collectDate":"2026-01-03",
                "nightuid":"N3","uid":"3","namedLocation":"P","trapCoordinate":"A3",
            },
        ]
        coords={"P.A1":(0.,0.),"P.A2":(3.,4.),"P.A3":(3.,4.)}
        out=m.individual_movement_records(rows,coords)
        self.assertEqual(len(out),1)
        self.assertAlmostEqual(out[0]["median_successive_displacement_m"],2.5)

    def test_hierarchy_weights_sites_equally(self):
        rows=[
            {
                "species":"Dipodomys ordii","site":"A",
                "n_recapture_male":3,"n_recapture_female":3,
                "delta_sex_movement":10.0,
            },
            {
                "species":"Dipodomys ordii","site":"A",
                "n_recapture_male":3,"n_recapture_female":3,
                "delta_sex_movement":10.0,
            },
            {
                "species":"Dipodomys ordii","site":"B",
                "n_recapture_male":3,"n_recapture_female":3,
                "delta_sex_movement":0.0,
            },
        ]
        out=m.movement_effect(
            rows,species_set=["Dipodomys ordii"],n_min=3
        )
        self.assertAlmostEqual(out["species"][0]["effect"],5.0)

    def test_manuscript_gate_requires_ci_above_zero(self):
        gate={
            "decisions":{
                "non_estimable":"STOP_EST",
                "nonpositive":"STOP_DIR",
                "positive_but_ci_overlaps_zero":"STOP_CI",
                "pass":"PASS",
            },
            "authorize_decoupling_if":{"minimum_positive_species":2},
        }
        primary={
            "family":{"estimable":True,"effect":1.0,"ci95_low":-0.1},
            "species":[
                {"species":"A","effect":1.0},
                {"species":"B","effect":1.0},
            ],
        }
        self.assertEqual(
            m.manuscript_decision(primary,gate)["decision"],
            "STOP_CI",
        )
        primary["family"]["ci95_low"]=0.1
        self.assertEqual(
            m.manuscript_decision(primary,gate)["decision"],
            "PASS",
        )


if __name__=="__main__":
    unittest.main()
