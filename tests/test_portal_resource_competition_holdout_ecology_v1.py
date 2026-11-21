"""Synthetic ecology metric and plot-fixed model checks, no original outcomes."""
from __future__ import annotations
import unittest
from math import isfinite

from analysis.run_portal_resource_competition_holdout_ecology_v1 import (
    tv_distance, original_plant_abundance, model_matrix, fit_fixed,
    treatment_plot_mean_difference,
)

class TestPortalPlantChangeCompetitorModel(unittest.TestCase):
    def test_one_individual_per_source_taxon_composition(self):
        self.assertAlmostEqual(tv_distance({"A":5,"B":5},{"A":5,"B":5}),0.)
        self.assertAlmostEqual(tv_distance({"A":10},{"B":10}),1.)
        self.assertAlmostEqual(tv_distance({"A":5,"B":5},{"A":10}),.5)
        self.assertRaises(ValueError, tv_distance, {}, {"A":5})

    def test_plant_zero_only_for_actually_censused_quadrats(self):
        quad={(2024,"summer",7):set(range(1,13))}
        raw=("year,season,plot,quadrat,species,abundance,cover,cf,notes\n"
             "2024,summer,7,1,x,5,12,,\n"
             "2024,summer,7,13,x,100,50,,\n")
        d,c=original_plant_abundance({
            "Plants/Portal_plant_quadrats.csv":raw.encode()},quad)
        self.assertAlmostEqual(d[(2024,"summer",7)],5/12)
        self.assertEqual(c["plant_original_rows_not_confirmed_censused"],1)
        self.assertEqual(c["plant_original_numeric_censused_species_rows"],1)

    def test_negative_plant_row_fails_closed(self):
        quad={(2024,"summer",7):set(range(1,13))}
        raw=("year,season,plot,quadrat,species,abundance,cover,cf,notes\n"
             "2024,summer,7,1,x,-1,12,,\n")
        with self.assertRaisesRegex(ValueError,"PLANT_ABUNDANCE_NEGATIVE_OR_INFINITE"):
            original_plant_abundance({
                "Plants/Portal_plant_quadrats.csv":raw.encode()},quad)

    def test_plot_FEs_resource_and_treatment_slope_identifiable(self):
        data=[]
        for p in range(1,19):
            trt="control" if p<=9 else "exclosure"
            for year in (2021,2022,2023,2024):
                for month in (2,5,8,11):
                    # Non-additive plant changes within plot-month/year so x is
                    # NOT simply a composite of site/month/year indicators.
                    x=(.15 + .01*p + .035*(year-2021) +
                       .013*month + .007*(p%4)*(month%5) +
                       .002*(p%5)*(year-2021))
                    y=(.25 + .003*p + .002*month + .003*(year-2021)
                       + .17*x + (.24*x if trt=="exclosure" else 0.))
                    data.append({"plot":p,"plotblock":str(p),"start_year":year,
                                 "month":month,"treatment":trt,"x":x,"y":y})
        X,Y=model_matrix(data)
        self.assertEqual(X.shape[0],len(data))
        a,b,theta=fit_fixed(data)
        self.assertAlmostEqual(a,.17,places=7)
        self.assertAlmostEqual(b,.41,places=7)
        self.assertAlmostEqual(theta,.24,places=7)
        self.assertTrue(isfinite(treatment_plot_mean_difference(data)))

if __name__=="__main__":
    unittest.main()
