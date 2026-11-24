import unittest
from analysis.audit_neon_holt_annual_bridge_v1 import key_diagnosis,pair_support,annual_capture
class AnnualBridgeTest(unittest.TestCase):
    def test_invalid_keys_not_imputed(self):
        rows=[{"YEAR":"1988","LINE":"N","PLOT":"1","FIASP":"833","SPEC":"5","COUNT":"0"},
              {"YEAR":"1988","LINE":"S","PLOT":"0","FIASP":"833","SPEC":"5","COUNT":"1"},
              {"YEAR":"1988","LINE":"X","PLOT":"2","FIASP":"0","SPEC":"0","COUNT":"0"}]
        report,k,s=key_diagnosis(rows,"seedfall")
        self.assertEqual(report["invalid_key_reason_counts"]["rows_with_any_invalid_key"],2)
        self.assertEqual(k,{(1988,"N",1)})
        self.assertEqual(report["explicit_zero_blank_noninteger_field_counts"]["COUNT_explicit_zero"],1)
        self.assertEqual(pair_support(k,{(1989,"N",1)},s,{(1989,"N",1,"833")})["1"]["red_oak_FIASP_833_shared_keys"],1)
    def test_explicit_month_join_not_guessed(self):
        base={"year":"1999","id_new":"PRIVATE","STRAPSTAT":"A","date":"805"}
        cap=[{**base,"month":"8"}]
        old=[{**base,"used":"1"},{**base,"date":"806","used":"1"}]
        o=annual_capture(cap,[{"year":"1999","month":"8","nind":"1"}],old)
        self.assertEqual(o["old_2022_target_used_exact_crosswalk"],{"exact_match_all_explicit_august":1,"no_exact_match":1})
        self.assertEqual(o["annual_nind_crosscheck_counts"]["summary_equals_unique_ID"],1)
        self.assertNotIn("PRIVATE",str(o))
if __name__=="__main__":unittest.main()
