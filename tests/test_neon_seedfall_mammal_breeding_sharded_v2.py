import unittest
from analysis.audit_neon_seedfall_mammal_breeding_sharded_v2 import (
    partition,merge_numeric,merge_headers,expected,combined,manifest_pin_digest)
class ShardedSourceTests(unittest.TestCase):
    def test_disjoint_whole_site_partition(self):
        p=partition(["s"+str(i) for i in range(32)])
        self.assertEqual([len(x) for x in p],[8]*4)
        self.assertEqual(len(set.union(*p)),32)
        self.assertTrue(all(not a&b for i,a in enumerate(p) for b in p[i+1:]))
    def test_nested_counts_and_boolean_semantics(self):
        self.assertEqual(merge_numeric([{"x":{"a":2},"flag":False},{"x":{"a":3,"b":1},"flag":False}]),{"x":{"a":5,"b":1},"flag":False})
        with self.assertRaises(ValueError):merge_numeric([{"flag":True},{"flag":False}])
        with self.assertRaises(ValueError):merge_numeric([{"n":True},{"n":1}])
    def test_headers(self):
        self.assertEqual(merge_headers([{"t":[{"header":["x","y"],"files":2}]},{"t":[{"header":["x","y"],"files":3}]}]),{"t":[{"header":["x","y"],"files":5}]})
    def test_original_pin_and_partial_stop(self):
        p=expected()
        self.assertEqual(p["litter_manifest"]["files"]+p["mammal_manifest_selected"]["files"],7009)
        self.assertEqual(p["litter_manifest"]["bytes"]+p["mammal_manifest_selected"]["bytes"],622537748)
        self.assertEqual(len(manifest_pin_digest(p)),64)
        with self.assertRaises(ValueError):combined([],p)
        with self.assertRaises(ValueError):combined([{"shard_index":i,"status":"STOP"} for i in range(4)],p)
if __name__=="__main__":unittest.main()
