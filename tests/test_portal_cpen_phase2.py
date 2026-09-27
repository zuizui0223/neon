from pathlib import Path
import importlib.util
import unittest
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"fit_portal_cpen_phase2_v1.py"
spec=importlib.util.spec_from_file_location("portal_phase2",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class PortalCpenPhase2Tests(unittest.TestCase):
    def test_prepare_primary_filters_and_canonicalizes(self):
        rows=[
            {"species":"Chaetodipus penicillatus","treatment":"control","n_unique_individuals":"5","primary_n5_eligible":"True","packing_z":"-0.2","plot_id":"1","period":"100"},
            {"species":"Chaetodipus penicillatus","treatment":"exclosure","n_unique_individuals":"10","primary_n5_eligible":"True","packing_z":"0.4","plot_id":"2","period":"100"},
            {"species":"Chaetodipus penicillatus","treatment":"exclosure","n_unique_individuals":"4","primary_n5_eligible":"False","packing_z":"0.1","plot_id":"3","period":"100"},
            {"species":"Dipodomys merriami","treatment":"control","n_unique_individuals":"8","primary_n5_eligible":"True","packing_z":"1.0","plot_id":"4","period":"100"},
        ]
        df=m.prepare_portal_primary(rows)
        self.assertEqual(len(df),2)
        self.assertEqual(set(df["treatment"]),{"control","kangaroo_rat_exclosure"})
        self.assertEqual(list(df["n_unique_individuals"]),[5,10])
        self.assertAlmostEqual(float(df["z_logN"].mean()),0.0,places=12)
        self.assertAlmostEqual(float(df["z_logN"].std(ddof=0)),1.0,places=12)

    def test_prepare_primary_rejects_missing_primary_level(self):
        rows=[
            {"species":"Chaetodipus penicillatus","treatment":"control","n_unique_individuals":"5","primary_n5_eligible":"True","packing_z":"0","plot_id":"1","period":"100"},
            {"species":"Chaetodipus penicillatus","treatment":"control","n_unique_individuals":"6","primary_n5_eligible":"True","packing_z":"0","plot_id":"2","period":"101"},
        ]
        with self.assertRaises(ValueError):
            m.prepare_portal_primary(rows)

    def test_build_model_is_true_crossed_plot_period_structure(self):
        rows=[]
        for period in range(6):
            for plot in range(4):
                rows.append({
                    "species":"Chaetodipus penicillatus",
                    "treatment":"control" if plot<2 else "exclosure",
                    "n_unique_individuals":str(5+((period+plot)%5)),
                    "primary_n5_eligible":"True",
                    "packing_z":str((plot-1.5)*0.1 + period*0.01),
                    "plot_id":str(plot),
                    "period":str(period),
                })
        df=m.prepare_portal_primary(rows)
        model=m.build_portal_mixed_model(df)
        np.testing.assert_allclose(np.unique(model.groups),[1.0])
        self.assertEqual(model.k_re,0)
        self.assertEqual(model.k_vc,2)
        self.assertEqual(set(model.exog_vc.names),{"plot","period"})

    def test_primary_term_names_are_frozen(self):
        terms=m.primary_term_names()
        self.assertEqual(
            terms,
            {
                "treatment":"C(treatment, Treatment(reference='control'))[T.kangaroo_rat_exclosure]",
                "interaction":"C(treatment, Treatment(reference='control'))[T.kangaroo_rat_exclosure]:z_logN",
            },
        )


if __name__=="__main__":
    unittest.main()
