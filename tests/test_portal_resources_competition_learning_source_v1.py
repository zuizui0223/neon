"""Synthetic no-outcome tests: Portal source-only resource × competitor gate."""
from __future__ import annotations
import unittest
from datetime import date

from analysis.audit_portal_resources_competition_learning_source_v1 import (
    MIN_QUADRATS, strict_plant_match, strict_survey_census, survey_day,
)

class TestPortalThreeMechanismSourceOnly(unittest.TestCase):
    def test_exact_day_no_month_imputation(self):
        self.assertEqual(survey_day("2024","2","29"),date(2024,2,29))
        self.assertIsNone(survey_day("2023","2","29"))
        self.assertIsNone(survey_day("2024","unknown","4"))

    def test_past_90days_only_and_twelve_quadrats(self):
        original = {(2024,"summer",3):set(range(12))}
        numeric = {(2024,"summer",3):{1}}
        dates=[(2024,"summer",date(2024,6,1))]
        self.assertIsNotNone(strict_plant_match(
            (3,2024,8,30),original,numeric,dates))
        self.assertIsNone(strict_plant_match(
            (3,2024,9,1),original,numeric,dates))
        self.assertIsNone(strict_plant_match(
            (3,2024,5,30),original,numeric,dates))
        self.assertIsNone(strict_plant_match(
            (3,2024,8,30),{(2024,"summer",3):set(range(11))},
            numeric,dates))

    def test_numeric_availability_is_not_plant_quantity(self):
        q={(2023,"winter",8):set(range(12))}
        d=[(2023,"winter",date(2023,2,1))]
        a=strict_plant_match((8,2023,4,1),q,
            {(2023,"winter",8):{1}},d)
        b=strict_plant_match((8,2023,4,1),q,
            {(2023,"winter",8):{1,4,5}},d)
        self.assertEqual(a,b)
        self.assertTrue(a["numeric_plant_abundance_source_present"])

    def test_original_plant_support_does_not_compute_plant_values(self):
        census=(["year,season,plot,quadrat,censused,area"]+
                [f"2023,winter,3,{i},1,0.25" for i in range(1,13)])
        plant=("year,season,plot,quadrat,species,abundance,cover,cf,notes\n"
               "2023,winter,3,1,xy,2,14,,\n")
        dates=("year,season,censusdone,start_month,start_day,end_month,end_day\n"
               "2023,winter,yes,2,1,2,8\n")
        sources={
            "Plants/Portal_plant_censuses.csv":("\n".join(census)+"\n").encode(),
            "Plants/Portal_plant_census_dates.csv":dates.encode(),
            "Plants/Portal_plant_quadrats.csv":plant.encode(),
        }
        quad,numeric,dt,summary=strict_survey_census(sources)
        self.assertEqual(len(quad[(2023,"winter",3)]),12)
        self.assertEqual(numeric[(2023,"winter",3)],{1})
        self.assertTrue(summary["no_plant_counts_cover_or_biomass_summed"])
        sources["Plants/Portal_plant_quadrats.csv"]=plant.replace(
            "xy,2,14,,","xy,200000,100,,").encode()
        _,_,_,again=strict_survey_census(sources)
        self.assertEqual(summary,again)

if __name__=="__main__":
    unittest.main()
