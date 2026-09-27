import importlib.util
from pathlib import Path
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"portal_cpen_phase2_sensitivity_v1.py"
spec=importlib.util.spec_from_file_location("portal_sens",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class PortalCpenPhase2SensitivityTests(unittest.TestCase):
    def test_long_term_plot_set_is_frozen(self):
        self.assertEqual(
            m.long_term_portal_plots(),
            {"3","4","10","11","14","15","16","17","19","21","23"},
        )

    def test_threshold_selection_uses_prespecified_flags(self):
        rows=[
            {"species":"Chaetodipus penicillatus","treatment":"control","plot_id":"11","period":"1","n_unique_individuals":"3","packing_z":"0.1","sensitivity_n3_eligible":"True","primary_n5_eligible":"False","sensitivity_n8_eligible":"False"},
            {"species":"Chaetodipus penicillatus","treatment":"exclosure","plot_id":"3","period":"1","n_unique_individuals":"8","packing_z":"0.2","sensitivity_n3_eligible":"True","primary_n5_eligible":"True","sensitivity_n8_eligible":"True"},
            {"species":"Dipodomys merriami","treatment":"control","plot_id":"14","period":"1","n_unique_individuals":"10","packing_z":"0.3","sensitivity_n3_eligible":"True","primary_n5_eligible":"True","sensitivity_n8_eligible":"True"},
        ]
        n3=m.select_portal_sensitivity_rows(rows,n_min=3)
        n8=m.select_portal_sensitivity_rows(rows,n_min=8)
        self.assertEqual([r["n_unique_individuals"] for r in n3],[3,8])
        self.assertEqual([r["n_unique_individuals"] for r in n8],[8])

    def test_long_term_only_selection(self):
        rows=[
            {"species":"Chaetodipus penicillatus","treatment":"control","plot_id":"11","period":"1","n_unique_individuals":"5","packing_z":"0.1","primary_n5_eligible":"True"},
            {"species":"Chaetodipus penicillatus","treatment":"control","plot_id":"1","period":"1","n_unique_individuals":"5","packing_z":"0.1","primary_n5_eligible":"True"},
            {"species":"Chaetodipus penicillatus","treatment":"exclosure","plot_id":"3","period":"1","n_unique_individuals":"5","packing_z":"0.2","primary_n5_eligible":"True"},
        ]
        selected=m.select_portal_sensitivity_rows(rows,n_min=5,long_term_only=True)
        self.assertEqual({r["plot_id"] for r in selected},{"11","3"})

    def test_pit_filter_keeps_only_reliable_individual_rows(self):
        rows=[
            {"id":"a","pit_tag":"TRUE"},
            {"id":"b","pit_tag":"1"},
            {"id":"c","pit_tag":"FALSE"},
            {"id":"d","pit_tag":""},
        ]
        self.assertEqual(
            [r["id"] for r in m.filter_pit_reliable_captures(rows)],
            ["a","b"],
        )

    def test_radius_of_gyration(self):
        xy=np.array([[0.,0.],[2.,0.]])
        self.assertAlmostEqual(m.radius_of_gyration(xy),1.0)

    def test_mean_nearest_neighbour_distance(self):
        xy=np.array([[0.,0.],[1.,0.],[4.,0.]])
        self.assertAlmostEqual(m.mean_nearest_neighbour_distance(xy),(1+1+3)/3)

    def test_alternative_metric_score_is_negative_for_clustered_points(self):
        traps=np.array([[0.,0.],[1.,0.],[2.,0.],[10.,0.],[20.,0.]])
        obs=np.array([[0.,0.],[1.,0.]])
        out=m.standardized_geometry_metric(
            obs,traps,
            metric=m.radius_of_gyration,
            replicates=999,
            seed=7,
        )
        self.assertTrue(out["estimable"])
        self.assertLess(out["z"],0)

    def test_direction_reversal_summary(self):
        primary={"treatment":0.2,"interaction":-0.1}
        checks=[
            {"label":"a","treatment":0.1,"interaction":-0.3},
            {"label":"b","treatment":-0.2,"interaction":-0.2},
        ]
        out=m.direction_reversal_summary(primary,checks)
        self.assertEqual(out["treatment_reversal_labels"],["b"])
        self.assertEqual(out["interaction_reversal_labels"],[])


if __name__=="__main__":
    unittest.main()
