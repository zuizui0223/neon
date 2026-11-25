import unittest,json
from analysis.audit_neon_independent_resource_stage_sources_v1 import csv_table,ROOT
class IndependentResourceStageTests(unittest.TestCase):
    def test_csv_dialect(self):
        self.assertEqual(csv_table(b"year,seed\n2013,3\n2014,9\n")[2],[["2013","3"],["2014","9"]])
        with self.assertRaises(ValueError):csv_table(b"year,seed;stage\n2013,3;1\n")
    def test_published_arithmetic(self):
        d=json.loads((ROOT/"data/neon_huang2021_published_extreme_crop_fractions_20261125.json").read_text())
        o=json.loads((ROOT/"results/neon_huang2021_fraction_vs_loss_density_20261125.json").read_text())
        for k in ("vertebrate","rodent"):
            f=k+"_loss_pct";h=d["extremes"]["high"];l=d["extremes"]["low"]
            for tag,e in (("high",h),("low",l)):
                self.assertAlmostEqual(o["implied_loss_density"][tag][k],e["density"]*e[f]/100)
            self.assertAlmostEqual(o["contrasts"][k]["fraction_difference_pp"],h[f]-l[f])
            self.assertAlmostEqual(o["contrasts"][k]["high_to_low_implied_loss_density_ratio"],h["density"]*h[f]/(l["density"]*l[f]))
            self.assertLess(o["contrasts"][k]["fraction_difference_pp"],0)
            self.assertGreater(o["contrasts"][k]["ratio_min_rounding"],1)
if __name__=="__main__":unittest.main()
