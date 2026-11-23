from __future__ import annotations

# AI assistance disclosure: This test file was drafted with OpenAI ChatGPT
# (GPT-5.6 Sol, September 2026) and is verified in repository workflows.

import unittest

from analysis import audit_live_trap_night_label_semantics_v1 as m


class NightLabelSemanticsTests(unittest.TestCase):
    def test_literal_calendar_shift_moves_post_midnight_back(self):
        self.assertEqual(
            m.literal_calendar_night_label("8/10/15","1:30"),
            "2015-08-09",
        )
        self.assertEqual(
            m.literal_calendar_night_label("8/10/15","10:30"),
            "2015-08-10",
        )

    def test_raw_grouping_keeps_three_bins_together(self):
        rows=[
            {"grid":"1","date":"8/10/15","time":"9:00","time_bin":"early"},
            {"grid":"1","date":"8/10/15","time":"12:30","time_bin":"middle"},
            {"grid":"1","date":"8/10/15","time":"3:00","time_bin":"late"},
        ]
        raw=m.grouping_summary(rows,mode="raw")
        shifted=m.grouping_summary(rows,mode="literal_calendar_shift")
        self.assertEqual(raw["groups_with_all_three_bins"],1)
        self.assertEqual(shifted["groups_with_all_three_bins"],0)

    def test_nocturnal_bin_order(self):
        rows=[
            {"time":"9:00","time_bin":"early"},
            {"time":"12:30","time_bin":"middle"},
            {"time":"3:00","time_bin":"late"},
        ]
        out=m.time_bin_order(rows)
        self.assertTrue(out["median_order_early_middle_late"])


if __name__=="__main__":
    unittest.main()
