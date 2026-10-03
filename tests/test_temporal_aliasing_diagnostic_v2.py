from __future__ import annotations
import math, unittest
from analysis import temporal_aliasing_diagnostic_v2 as m

class DiagnosticV2Tests(unittest.TestCase):
    def test_aba_endpoint_false_negative(self):
        rows=[
          {"id":"a","occ":"1","time":"1","x":"0","y":"0"},
          {"id":"a","occ":"1","time":"2","x":"2","y":"0"},
          {"id":"a","occ":"1","time":"3","x":"0","y":"0"},
        ]
        g,q=m.occasion_geometry(rows,individual_col="id",occasion_col="occ",time_col="time",coordinate_cols=["x","y"])
        self.assertEqual(len(g),1)
        self.assertAlmostEqual(g[0]["endpoint_span"],0)
        self.assertAlmostEqual(g[0]["positional_diameter"],2)
        s=m.summarize_geometry(g,material_scale=1,total_occasions=q["individual_occasions"])
        self.assertEqual(s["endpoint_span"]["material_count"],0)
        self.assertEqual(s["positional_diameter"]["material_count"],1)
        self.assertEqual(s["endpoint_false_negative_count"],1)

    def test_diameter_bounds_any_representative_choice(self):
        # occasion t: A=(0,0), B=(3,0), diameter 3
        # occasion u: C=(0,4), D=(0,8), diameter 4
        A=(0.,0.); B=(3.,0.); C=(0.,4.); D=(0.,8.)
        lhs=abs(m.euclidean(A,C)-m.euclidean(B,D))
        self.assertLessEqual(lhs,m.representative_distance_bound(3,4)+1e-12)

    def test_diameter_not_smaller_than_endpoint(self):
        rows=[
          {"id":"a","occ":"1","time":"1","x":"0","y":"0"},
          {"id":"a","occ":"1","time":"2","x":"1","y":"5"},
          {"id":"a","occ":"1","time":"3","x":"4","y":"0"},
        ]
        g,_=m.occasion_geometry(rows,individual_col="id",occasion_col="occ",time_col="time",coordinate_cols=["x","y"])
        self.assertGreaterEqual(g[0]["positional_diameter"],g[0]["endpoint_span"])

    def test_mpd_bound(self):
        self.assertAlmostEqual(m.mpd_representative_bound([1,2,3]),4)

if __name__=="__main__":
    unittest.main()
