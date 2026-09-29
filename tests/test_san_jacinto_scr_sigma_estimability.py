from __future__ import annotations

import unittest

from analysis import san_jacinto_scr_sigma_estimability_v1 as m


class SCRSigmaEstimabilityTests(unittest.TestCase):
    def test_bouts_split_on_month_gap(self):
        rows=[
            {"date":"1/1/16"},{"date":"1/2/16"},
            {"date":"2/1/16"},{"date":"2/2/16"},
            {"date":"3/1/16"},{"date":"4/1/16"},
            {"date":"5/1/16"},{"date":"6/1/16"},
            {"date":"7/1/16"},{"date":"8/1/16"},
            {"date":"9/1/16"},{"date":"10/1/16"},
        ]
        mapping,summary=m.build_bouts(rows)
        self.assertGreaterEqual(len(summary),10)
        self.assertNotEqual(mapping["2016-01-01"],mapping["2016-02-01"])

    def test_nocturnal_time_order(self):
        self.assertLess(m.parse_nocturnal_time("10:00"),m.parse_nocturnal_time("1:00"))


if __name__=="__main__":
    unittest.main()
