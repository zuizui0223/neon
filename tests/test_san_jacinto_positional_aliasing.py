from __future__ import annotations

# AI assistance disclosure: This test file was drafted or refactored with OpenAI ChatGPT (GPT-5.6 Sol, September 2026); it remains under author responsibility and is verified in repository workflows.

import unittest

from analysis import san_jacinto_positional_aliasing_v1 as m


class PositionalAliasingTests(unittest.TestCase):
    def test_wilson_interval_sensible(self):
        low,high=m.wilson_interval(50,100)
        self.assertLess(low,0.5)
        self.assertGreater(high,0.5)

    def test_one_grid_spacing(self):
        x1,y1=m.flag_xy("A1")
        x2,y2=m.flag_xy("A2")
        self.assertAlmostEqual(((x2-x1)**2+(y2-y1)**2)**0.5,6.25)

    def test_first_last_repeat_night(self):
        rows=[
            {"species":"PEMA","grid":"1","unique_ID":"a","date":"1/1/16","flag":"A1","time":"10:00"},
            {"species":"PEMA","grid":"1","unique_ID":"a","date":"1/1/16","flag":"A2","time":"1:00"},
        ]
        out=m.prepare_repeat_nights(rows)
        self.assertEqual(len(out),1)
        self.assertTrue(out[0]["one_spacing_shift"])
        self.assertEqual(out[0]["first_flag"],"A1")
        self.assertEqual(out[0]["last_flag"],"A2")


if __name__=="__main__":
    unittest.main()
