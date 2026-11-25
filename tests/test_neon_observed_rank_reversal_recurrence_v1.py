import unittest
from analysis.run_neon_observed_rank_reversal_recurrence_v1 import category,verify_unit,evaluate
class RankReversalTests(unittest.TestCase):
    def test_strict_classification(self):
        self.assertEqual(category((8,3),(3,9),(5,2),(2,6)),"strict_reversal")
        self.assertEqual(category((8,3),(3,9),(2,5),(2,6)),"tie_or_disagreement")
        self.assertEqual(category((8,3),(9,3),(5,2),(6,2)),"strict_retained_rank")
    def test_matrix_replay_shared_tags(self):
        a=("s","p","a");b=("s","p","b")
        u={"site_plot":("s","p"),"season_ordinal":10,
           "A":{"g":{"A1","A2","A3"},"h":{"B1","B2"}},"B":{"g":{"C1","C2"},"h":{"D1","D2","D3"}}}
        tag={a:{"g":{"1","2","3","shared"},"h":{"4","5"}},b:{"g":{"6","7","shared"},"h":{"8","9","10","shared2"}}}
        c={}
        for g,ss in tag[a].items():
            for j,t in enumerate(sorted(ss-{"shared"})):c[a,g,t]={("A" if g=="g" else "B")+str(j+1)}
        # shared2 is observed in genus j in A and therefore excluded in B.
        tag[a]["j"]={"shared2"}
        for g,ss in tag[b].items():
            for j,t in enumerate(sorted(ss-{"shared","shared2"})):c[b,g,t]={("C" if g=="g" else "D")+str(j+1)}
        ctx=({("s","p",10):a,("s","p",11):b},tag,c)
        self.assertEqual(verify_unit(u,ctx),"strict_reversal")
        u["A"]["g"].add("E5")
        with self.assertRaises(ValueError):verify_unit(u,ctx)
    def test_thin_support(self):
        self.assertEqual(evaluate([],1,20,8)["status"],"STOP_SUBGROUP_SUPPORT")
if __name__=="__main__":unittest.main()
