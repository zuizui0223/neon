from __future__ import annotations

import unittest

from analysis import audit_san_jacinto_aliasing_cluster_robust_v1 as m


class ClusterRobustAliasingAuditTests(unittest.TestCase):
    def test_cluster_fractions_equal_weight_clusters(self):
        rows=[
            {"grid":"1","unique_ID":"a","changed":True,"bout_id":1},
            {"grid":"1","unique_ID":"a","changed":True,"bout_id":1},
            {"grid":"1","unique_ID":"b","changed":False,"bout_id":1},
            {"grid":"2","unique_ID":"c","changed":False,"bout_id":2},
        ]
        vals=sorted(m.cluster_fractions(rows,("grid","unique_ID")))
        self.assertEqual(vals,[0,0,1])

    def test_grid_cluster_fraction(self):
        rows=[
            {"grid":"1","unique_ID":"a","changed":True,"bout_id":1},
            {"grid":"1","unique_ID":"b","changed":False,"bout_id":1},
            {"grid":"2","unique_ID":"c","changed":True,"bout_id":2},
        ]
        vals=sorted(m.cluster_fractions(rows,("grid",)))
        self.assertEqual(vals,[0.5,1])


if __name__=="__main__":
    unittest.main()
