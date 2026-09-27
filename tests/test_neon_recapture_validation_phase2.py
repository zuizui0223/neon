import importlib.util
from pathlib import Path
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"neon_recapture_validation_phase2_v1.py"
spec=importlib.util.spec_from_file_location("movement",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class NeonRecaptureValidationPhase2Tests(unittest.TestCase):
    def test_successive_displacements(self):
        points=[
            ("2026-01-01","n1",0.0,0.0),
            ("2026-01-02","n2",3.0,4.0),
            ("2026-01-03","n3",3.0,8.0),
        ]
        self.assertEqual(m.successive_displacements(points),[5.0,4.0])

    def test_individual_movement_requires_distinct_nights_and_locations(self):
        rows=[
            {"tagID":"a","collectDate":"2026-01-01","nightuid":"n1","node":"A"},
            {"tagID":"a","collectDate":"2026-01-02","nightuid":"n2","node":"B"},
            {"tagID":"b","collectDate":"2026-01-01","nightuid":"n1","node":"C"},
            {"tagID":"b","collectDate":"2026-01-02","nightuid":"n2","node":"C"},
        ]
        coords={"A":(0.0,0.0),"B":(3.0,4.0),"C":(10.0,0.0)}
        out=m.individual_movement_summaries(rows,coords)
        self.assertEqual(set(out),{"a"})
        self.assertAlmostEqual(out["a"],5.0)

    def test_event_movement_requires_three_moving_individuals(self):
        rows=[]
        coords={}
        for i,d in enumerate((3.0,4.0,5.0),start=1):
            a=f"{i}a"; b=f"{i}b"
            coords[a]=(0.0,float(i))
            coords[b]=(d,float(i))
            rows.extend([
                {"tagID":str(i),"collectDate":"2026-01-01","nightuid":"n1","node":a},
                {"tagID":str(i),"collectDate":"2026-01-02","nightuid":"n2","node":b},
            ])
        out=m.event_movement_summary(rows,coords,min_moving_individuals=3)
        self.assertTrue(out["estimable"])
        self.assertEqual(out["moving_individual_count"],3)
        self.assertAlmostEqual(out["median_individual_displacement_m"],4.0)

    def test_first_night_population_packing_uses_only_first_night(self):
        rows=[]
        coords={}
        for i in range(1,11):
            coord=f"A{i}"
            node=f"PLOT.mammalGrid.mam.{coord}"
            coords[node]=(float(i-1),0.0)
            rows.append({
                "collectDate":"2026-01-01","nightuid":"n1",
                "namedLocation":"PLOT.mammalGrid.mam","trapCoordinate":coord,
                "trapStatus":"4 - Capture" if i<=5 else "6 - No Capture",
                "taxonID":"T1" if i<=5 else "",
                "scientificName":"Species alpha" if i<=5 else "",
                "taxonRank":"species" if i<=5 else "",
                "identificationQualifier":"",
                "tagID":f"id{i}" if i<=5 else "",
            })
        # Later-night captures must not alter the first-night N.
        rows.append({
            "collectDate":"2026-01-02","nightuid":"n2",
            "namedLocation":"PLOT.mammalGrid.mam","trapCoordinate":"A10",
            "trapStatus":"4 - Capture","taxonID":"T1",
            "scientificName":"Species alpha","taxonRank":"species",
            "identificationQualifier":"","tagID":"later",
        })
        out=m.first_night_population_packing(
            rows,coords,
            taxon_id="T1",
            scientific_name="Species alpha",
            replicates=999,
        )
        self.assertEqual(out["first_night"],"n1")
        self.assertEqual(out["n_unique_individuals"],5)
        self.assertTrue(out["packing_estimable"])


    def test_build_pathogen_validation_rows_from_two_night_event(self):
        plot_rows=[
            {
                "siteID":"SITE","plotID":"PLOT","eventID":"E1",
                "nightuid":"n1","collectDate":"2026-01-01",
                "mammalGridSamplingMethod":"pathogen",
                "gridCompletion":"setting complete, processing complete",
                "samplingImpractical":"OK",
            },
            {
                "siteID":"SITE","plotID":"PLOT","eventID":"E1",
                "nightuid":"n2","collectDate":"2026-01-02",
                "mammalGridSamplingMethod":"pathogen",
                "gridCompletion":"setting complete, processing complete",
                "samplingImpractical":"OK",
            },
        ]
        coords={}
        trap_rows=[]
        for night,date in [("n1","2026-01-01"),("n2","2026-01-02")]:
            for i in range(1,11):
                coord=f"A{i}"
                node=f"PLOT.mammalGrid.mam.{coord}"
                coords[node]=(float(i-1),0.0)
                tag=""
                capture=False
                if night=="n1" and i<=5:
                    tag=f"id{i}"; capture=True
                if night=="n2" and i in (6,7,8):
                    tag=f"id{i-5}"; capture=True
                trap_rows.append({
                    "siteID":"SITE","plotID":"PLOT","nightuid":night,
                    "collectDate":date,"namedLocation":"PLOT.mammalGrid.mam",
                    "trapCoordinate":coord,
                    "trapStatus":"4 - Capture" if capture else "6 - No Capture",
                    "taxonID":"T1" if capture else "",
                    "scientificName":"Species alpha" if capture else "",
                    "taxonRank":"species" if capture else "",
                    "identificationQualifier":"",
                    "tagID":tag,
                })
        rows=m.build_pathogen_validation_rows(
            plot_rows,trap_rows,
            target_taxon_ids={"T1"},
            coordinate_map=coords,
            replicates=99,
        )
        self.assertEqual(len(rows),1)
        row=rows[0]
        self.assertEqual(row["site"],"SITE")
        self.assertEqual(row["plot_id"],"PLOT")
        self.assertEqual(row["event_id"],"E1")
        self.assertEqual(row["species"],"Species alpha")
        self.assertEqual(row["n_unique_individuals"],5)
        self.assertEqual(row["moving_individual_count"],3)
        self.assertIsNotNone(row["packing_z"])
        self.assertIsNotNone(row["median_individual_displacement_m"])

    def test_validation_frame_requires_five_events_per_species_site(self):
        rows=[]
        for species,site in [("A","S1"),("B","S2")]:
            for i in range(5):
                rows.append({
                    "species":species,"site":site,"event_id":f"{species}{i}",
                    "packing_z":(-1.0+0.5*i),
                    "n_unique_individuals":5+i,
                    "median_individual_displacement_m":10+2*i,
                    "moving_individual_count":3,
                })
        # A third stratum with only four events is excluded.
        for i in range(4):
            rows.append({
                "species":"C","site":"S3","event_id":f"C{i}",
                "packing_z":0.1*i,"n_unique_individuals":5+i,
                "median_individual_displacement_m":5+i,
                "moving_individual_count":3,
            })
        df=m.prepare_validation_frame(rows,min_events_per_stratum=5)
        self.assertEqual(set(df["species_site"]),{"A|S1","B|S2"})
        self.assertEqual(len(df),10)
        self.assertAlmostEqual(float(df["z_logN"].mean()),0.0,places=12)

    def test_validation_model_contains_packing_effect(self):
        rows=[]
        for species,site,offset in [("A","S1",0.0),("B","S2",0.3)]:
            for i in range(6):
                packing=-1.0+0.4*i
                rows.append({
                    "species":species,"site":site,"event_id":f"{species}{i}",
                    "packing_z":packing,
                    "n_unique_individuals":5+i,
                    "median_individual_displacement_m":10+offset+3*packing+0.2*i,
                    "moving_individual_count":3,
                })
        df=m.prepare_validation_frame(rows,min_events_per_stratum=5)
        result=m.fit_validation_model(df)
        self.assertIn("packing_z",result.params.index)
        self.assertGreater(float(result.params["packing_z"]),0)


if __name__=="__main__":
    unittest.main()
