import unittest
from datetime import date
from analysis.run_neon_matched_species_pregnancy_season_v1 import contrasts,aggregate,phase,tally
class ReproSeasonTests(unittest.TestCase):
    def test_matched_plot_phase_contrast(self):
        x={}
        for ph,m in (("early",5),("late",8)):
            z=[]
            for tax,name,n in (("a","Genus alpha",1 if ph=="early" else 4),("b","Genus beta",4 if ph=="early" else 1)):
                for i in range(5):z.append((date(2020,m,15),tax+str(i),tax,name,"pregnant" if i<n else "not"))
            x["s",2020,"p",ph]=z
        out,diag=contrasts(x,{"s"})
        self.assertEqual(diag["eligible_pair_site_years"],1)
        self.assertAlmostEqual(out[0]["pairs"][0]["mean_D"],1.2)
        self.assertEqual(aggregate(out)["status"],"NO_CROSS_SITE_REPEAT_SUPPORT")
    def test_earliest_tag_status_unknown_on_conflict(self):
        a=date(2020,5,1);b=date(2020,5,2)
        x=[(a,"tag","a","Genus alpha","not"),(a,"tag","a","Genus alpha","pregnant"),(b,"tag","a","Genus alpha","pregnant")]
        self.assertEqual(tally(x)[("a","Genus alpha")]["unknown"],1)
        self.assertIsNone(phase(date(2020,7,15)))
    def test_heldout_prediction_requires_repeated_sites_and_pairs(self):
        p={"species_a":["a","Genus alpha"],"species_b":["b","Genus beta"],"years":2,"mean_D":.3,"unknown_lo":.1,"unknown_hi":.4}
        z=aggregate([{"pairs":[p.copy()]} for _ in range(3)])
        self.assertEqual(z["status"],"DESCRIPTIVE_ONLY_THIN_SUPPORT")
        self.assertEqual(z["effect"]["equal_site_sign_agreement"],1)
        self.assertAlmostEqual(z["effect"]["equal_site_mse"],0)
        self.assertGreater(z["effect"]["zero_contrast_baseline_mse"],0)
if __name__=="__main__":unittest.main()
