from __future__ import annotations

import unittest

from analysis import konza_hispidus_crossscale_estimability_v1 as m


def row(**kwargs):
    base={
        "Recyear":"2010","Season":"SP","RecMonth":"3","Recday":"15",
        "TrapDay":"1","Watershed":"004B","Line":"E","Sta":"1",
        "Species":"Ch","Sex":"M","Status":"a",
        "ToeClip":"","HairClip":"","REarTag":"","LEarTag":"",
    }
    base.update(kwargs)
    return base


class KonzaHispidusEstimabilityTests(unittest.TestCase):
    def test_mark_normalization_requires_digit(self):
        self.assertIsNone(m._mark("RE"))
        self.assertEqual(m._mark("R-010"),"R010")
        self.assertEqual(m._mark(" 2053 "),"2053")

    def test_shared_mark_links_nights(self):
        rows=[
            row(TrapDay="1",Sta="1",Sex="M",REarTag="R010"),
            row(TrapDay="2",Sta="2",Sex="M",REarTag="R010"),
        ]
        out=m.movement_identity_summary(rows)
        self.assertEqual(out["n_recapture_male"],1)
        self.assertEqual(out["n_invalid_sex_components"],0)

    def test_same_mark_two_stations_same_day_fails_component(self):
        rows=[
            row(TrapDay="1",Sta="1",Sex="M",REarTag="R010"),
            row(TrapDay="1",Sta="2",Sex="M",REarTag="R010"),
            row(TrapDay="2",Sta="3",Sex="M",REarTag="R010"),
        ]
        out=m.movement_identity_summary(rows)
        self.assertEqual(out["n_recapture_male"],0)
        self.assertEqual(out["n_invalid_same_day_station_components"],1)

    def test_two_captures_same_station_are_allowed_but_three_fail_geometry(self):
        rows=[
            row(TrapDay="1",Sta="1",Sex="M",REarTag="1"),
            row(TrapDay="1",Sta="1",Sex="F",REarTag="2"),
        ]
        out=m.packing_night_rows(rows)[0]
        self.assertTrue(out["trap_slot_geometry_valid"])

        rows.append(
            row(TrapDay="1",Sta="1",Sex="M",REarTag="3")
        )
        out=m.packing_night_rows(rows)[0]
        self.assertFalse(out["trap_slot_geometry_valid"])
        self.assertEqual(out["overfull_station_count"],1)

    def test_crossscale_gate_requires_all_conditions(self):
        packing=[]
        movement=[]
        for i in range(6):
            line=f"L{i}"
            watershed=f"W{i//2}"
            for j in range(4):
                packing.append({
                    "trapline_id":line,"watershed":watershed,
                    "paired_n3_eligible":True,"paired_n5_eligible":True,
                })
            movement.append({
                "trapline_id":line,"watershed":watershed,
                "paired_n3_eligible":True,"paired_n5_eligible":True,
            })
        out=m.summarize(packing,movement)
        self.assertTrue(out["crossscale_gate"]["passed"])
        self.assertEqual(
            out["crossscale_gate"]["decision"],
            "authorize_konza_crossscale_effect_lock",
        )


if __name__=="__main__":
    unittest.main()
