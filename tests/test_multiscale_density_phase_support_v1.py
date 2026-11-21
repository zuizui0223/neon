import unittest
from analysis.audit_multiscale_density_phase_support_v1 import assess

def row(when, n, event, plot="P1", genus="Peromyscus", site="SITE", taxon="PEMA"):
    return dict(event_date=when, mnka=n, event_id=event, plot_id=plot,
                genus=genus, site=site, taxon=taxon)


class PhaseSupportTests(unittest.TestCase):
    def test_opposite_trend_at_same_abundance_is_support_pair(self):
        rows=[row("2020-01-01",5,"a"),row("2020-02-01",9,"b"),
              row("2020-03-01",12,"c"),row("2020-04-01",9,"d")]
        r=assess(rows)
        self.assertEqual(r["genera"]["Peromyscus"]["near_equal_opposite_phase_pairs"],1)
        self.assertEqual(r["genera"]["Peromyscus"]["paired_taxon_plot_series"],1)
        self.assertFalse(r["both_modes_structurally_supportable"])

    def test_gap_guard_censors_distant_history(self):
        rows=[row("2018-01-01",3,"a"),row("2020-01-01",9,"b"),
              row("2020-02-01",7,"c")]
        r=assess(rows)
        self.assertEqual(r["gap_gt_370"],1)
        self.assertEqual(r["genera"]["Peromyscus"]["near_equal_opposite_phase_pairs"],0)

    def test_pair_requires_same_taxon_plot_series(self):
        rows=[row("2020-01-01",3,"a"),row("2020-02-01",9,"b"),
              row("2020-01-01",15,"c",plot="P2"),row("2020-02-01",9,"d",plot="P2")]
        r=assess(rows)
        self.assertEqual(r["genera"]["Peromyscus"]["near_equal_opposite_phase_pairs"],0)

    def test_equal_abundance_is_not_growth(self):
        rows=[row("2020-01-01",8,"a"),row("2020-02-01",8,"b"),
              row("2020-03-01",7,"c")]
        r=assess(rows)
        self.assertEqual(r["genera"]["Peromyscus"]["stable"],1)
        self.assertEqual(r["genera"]["Peromyscus"]["decreasing"],1)
        self.assertEqual(r["genera"]["Peromyscus"]["near_equal_opposite_phase_pairs"],0)

if __name__=="__main__":
    unittest.main()
