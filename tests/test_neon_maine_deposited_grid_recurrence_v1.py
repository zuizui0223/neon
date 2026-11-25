import unittest
from analysis.run_neon_maine_deposited_grid_recurrence_v1 import build_pairs,summarize
class MaineRecurrenceTests(unittest.TestCase):
    def test_shared_tag_removed_across_grid(self):
        grids={"g":{str(i) for i in range(100)}}
        mo={(16,1):{"1","2","3"},(16,2):{"4","5","6"}}
        obs=set()
        for m,o in [(1,"1"),(2,"4")]:
            for sp,coords in [("MG",[0,1]),("PM",[2,3])]:
                for j,s in enumerate(coords):obs.add(("g",str(s),o,16,m,f"{sp}{m}{j}",sp))
        obs.add(("g","4","1",16,1,"bridge","PM"))
        obs.add(("other","9","4",16,2,"bridge","PM"))
        from collections import defaultdict
        p,d=build_pairs(grids,obs,defaultdict(set,mo))
        self.assertEqual(len(p),1)
        self.assertEqual(len(p[0][3]["PM"]),2)
        self.assertGreater(summarize(p)["equal_grid_mean_Z"],0)
    def test_no_invented_occasion(self):
        from collections import defaultdict
        p,d=build_pairs({"g":{str(i) for i in range(100)}},set(),defaultdict(set))
        self.assertEqual(p,[])
        self.assertEqual(d["not_three_documented_occasions"],8)
if __name__=="__main__":unittest.main()
