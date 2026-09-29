from __future__ import annotations

import unittest

from analysis import audit_san_jacinto_measurement_sensitivity_v1 as m


class MeasurementSensitivityAuditTests(unittest.TestCase):
    def test_compare_states_counts_changed_flags(self):
        first=[
            {
                "grid":"1","species":"CHFA","unique_ID":"a","bout_id":1,
                "date":"2016-01-01","flag":"A1","nocturnal_time":22.0,
            },
            {
                "grid":"1","species":"CHFA","unique_ID":"b","bout_id":1,
                "date":"2016-01-01","flag":"B1","nocturnal_time":22.0,
            },
        ]
        last=[
            {
                "grid":"1","species":"CHFA","unique_ID":"a","bout_id":1,
                "date":"2016-01-01","flag":"A2","nocturnal_time":26.0,
            },
            {
                "grid":"1","species":"CHFA","unique_ID":"b","bout_id":1,
                "date":"2016-01-01","flag":"B1","nocturnal_time":22.5,
            },
        ]
        out=m.compare_states(first,last)
        self.assertEqual(out["nightly_states"],2)
        self.assertEqual(out["first_last_flag_different_count"],1)
        self.assertAlmostEqual(out["first_last_flag_different_fraction"],0.5)
        self.assertGreater(out["max_first_last_distance_m"],0.0)


if __name__=="__main__":
    unittest.main()
