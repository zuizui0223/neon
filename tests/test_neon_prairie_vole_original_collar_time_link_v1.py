"""Pure synthetic device-reuse and date-qualified animal ID source tests."""
from __future__ import annotations
from datetime import date
import unittest
from analysis.run_neon_prairie_vole_original_collar_time_link_v1 import (
    collar_source_episodes,unique_device_assignment,mask_format,
    SOURCE_MIN_RELINK_RATE,SOURCE_MIN_COLLARED_TAGS_WITH_TRAP
)
class OriginalCollarTimeMappingTests(unittest.TestCase):
    def test_same_device_later_deployed_on_another_animal(self):
        rows=[
            {"tag":"A","collar":"100","date_on":"2021-12-01","date_off":"2021-12-09"},
            {"tag":"B","collar":"100","date_on":"2021-12-15","date_off":"2021-12-22"}
        ]
        episodes,invalid,overlap=collar_source_episodes(rows)
        self.assertEqual((invalid,overlap),({},0))
        self.assertEqual(unique_device_assignment(episodes,"100",date(2021,12,3)),("A","unique"))
        self.assertEqual(unique_device_assignment(episodes,"100",date(2021,12,18)),("B","unique"))
        self.assertEqual(unique_device_assignment(episodes,"100",date(2021,12,12)),(None,"device_outside_date"))
    def test_collars_two_different_tags_same_day_are_ambiguous(self):
        rows=[
            {"tag":"A","collar":"100","date_on":"2021-12-01","date_off":"2021-12-09"},
            {"tag":"B","collar":"100","date_on":"2021-12-09","date_off":"2021-12-22"}
        ]
        episodes,invalid,overlap=collar_source_episodes(rows)
        self.assertEqual(overlap,1)
        self.assertEqual(unique_device_assignment(episodes,"100",date(2021,12,9)),
                         (None,"date_multiple_different_tags"))
    def test_missing_no_device_never_becomes_negative_contact(self):
        episodes,_,_=collar_source_episodes([{
            "tag":"A","collar":"100","date_on":"2021-12-01","date_off":"2021-12-09"}])
        self.assertEqual(unique_device_assignment(episodes,"101",date(2021,12,3)),
                         (None,"device_unrecorded"))
        self.assertEqual(unique_device_assignment(episodes,"100",None),
                         (None,"bad_event_date"))
    def test_timestamp_mask_strips_actual_date_and_pit(self):
        x=mask_format("2021-12-15 02:04:16")
        self.assertEqual(x,"9999-99-99 99:99:99")
        self.assertNotIn("2021",x)
    def test_source_gate_predeclared(self):
        self.assertEqual(SOURCE_MIN_RELINK_RATE,.8)
        self.assertEqual(SOURCE_MIN_COLLARED_TAGS_WITH_TRAP,12)
if __name__=="__main__":
    unittest.main()
