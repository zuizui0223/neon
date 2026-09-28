from __future__ import annotations

import unittest

from analysis import neon_sex_recapture_estimability_v1 as m


class RecaptureEstimabilityTests(unittest.TestCase):
    def test_two_nights_three_per_sex_passes_primary(self):
        plots=[
            {
                "siteID":"S","plotID":"P","eventID":"E",
                "nightuid":"N1","collectDate":"2026-01-01",
                "mammalGridSamplingMethod":"pathogen",
                "gridCompletion":"setting complete, processing complete",
                "samplingImpractical":"",
            },
            {
                "siteID":"S","plotID":"P","eventID":"E",
                "nightuid":"N2","collectDate":"2026-01-02",
                "mammalGridSamplingMethod":"pathogen",
                "gridCompletion":"setting complete, processing complete",
                "samplingImpractical":"",
            },
        ]
        traps=[]
        for sex,prefix in [("M","M"),("F","F")]:
            for i in range(3):
                for night,coord in [("N1",f"A{i+1}"),("N2",f"B{i+1}")]:
                    traps.append({
                        "nightuid":night,
                        "trapStatus":"4 - capture",
                        "taxonID":"T",
                        "scientificName":"Dipodomys ordii",
                        "taxonRank":"species",
                        "identificationQualifier":"",
                        "tagID":f"{prefix}{i}",
                        "sex":sex,
                        "namedLocation":"P",
                        "trapCoordinate":coord,
                        "uid":f"{prefix}{i}-{night}",
                    })
        coords={
            f"P.{letter}{i}":(float(i),0.0)
            for letter in ("A","B") for i in range(1,4)
        }
        rows=m.build_recapture_estimability_rows(
            plots,traps,target_taxon_ids={"T"},coordinate_map=coords
        )
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["n_recapture_male"],3)
        self.assertEqual(rows[0]["n_recapture_female"],3)
        self.assertTrue(rows[0]["paired_n3_eligible"])

    def test_conflicting_sex_is_not_counted(self):
        plots=[
            {
                "siteID":"S","plotID":"P","eventID":"E",
                "nightuid":"N1","collectDate":"2026-01-01",
                "mammalGridSamplingMethod":"pathogen",
                "gridCompletion":"setting complete, processing complete",
                "samplingImpractical":"",
            },
            {
                "siteID":"S","plotID":"P","eventID":"E",
                "nightuid":"N2","collectDate":"2026-01-02",
                "mammalGridSamplingMethod":"pathogen",
                "gridCompletion":"setting complete, processing complete",
                "samplingImpractical":"",
            },
        ]
        traps=[
            {
                "nightuid":"N1","trapStatus":"4 - capture","taxonID":"T",
                "scientificName":"Dipodomys ordii","taxonRank":"species",
                "identificationQualifier":"","tagID":"X","sex":"M",
                "namedLocation":"P","trapCoordinate":"A1","uid":"1",
            },
            {
                "nightuid":"N2","trapStatus":"4 - capture","taxonID":"T",
                "scientificName":"Dipodomys ordii","taxonRank":"species",
                "identificationQualifier":"","tagID":"X","sex":"F",
                "namedLocation":"P","trapCoordinate":"A2","uid":"2",
            },
        ]
        coords={"P.A1":(0.,0.),"P.A2":(1.,0.)}
        rows=m.build_recapture_estimability_rows(
            plots,traps,target_taxon_ids={"T"},coordinate_map=coords
        )
        self.assertEqual(rows[0]["n_recapture_male"],0)
        self.assertEqual(rows[0]["n_recapture_female"],0)
        self.assertEqual(rows[0]["n_conflict_or_unknown_sex"],1)


if __name__=="__main__":
    unittest.main()
