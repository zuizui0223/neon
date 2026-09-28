import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"build_neon_sex_packing_inventory_v1.py"
spec=importlib.util.spec_from_file_location("neon_sex",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class NeonSexPackingInventoryTests(unittest.TestCase):
    def _plot(self, site="JORN", plot="JORN_001", event="E1", night="N1"):
        return {
            "siteID":site,
            "plotID":plot,
            "eventID":event,
            "nightuid":night,
            "collectDate":"2020-05-01",
            "mammalGridSamplingMethod":"diversity",
            "gridCompletion":"setting complete, processing complete",
            "samplingImpractical":"OK",
        }

    def _capture(self, coord, tag, sex, *, taxon="PEFL", name="Perognathus flavus", qualifier=""):
        return {
            "siteID":"JORN",
            "plotID":"JORN_001",
            "eventID":"E1",
            "nightuid":"N1",
            "namedLocation":"JORN_001.mammalGrid.mam",
            "trapCoordinate":coord,
            "trapStatus":"5 - capture",
            "taxonID":taxon,
            "scientificName":name,
            "taxonRank":"species",
            "identificationQualifier":qualifier,
            "tagID":tag,
            "sex":sex,
            "uid":tag,
        }

    def test_primary_diversity_session_counts_known_males_and_females(self):
        plot_rows=[self._plot()]
        trap_rows=[
            self._capture("A1","m1","M"),
            self._capture("A2","m2","Male"),
            self._capture("A3","m3","1 - Male"),
            self._capture("A4","f1","F"),
            self._capture("A5","f2","Female"),
            self._capture("A6","f3","2 - Female"),
            self._capture("A7","u1","U"),
        ]
        rows=m.build_neon_sex_sessions(
            plot_rows,
            trap_rows,
            target_taxon_ids={"PEFL"},
        )
        self.assertEqual(len(rows),1)
        row=rows[0]
        self.assertEqual(row["species"],"Perognathus flavus")
        self.assertEqual(row["site"],"JORN")
        self.assertEqual(row["n_total"],7)
        self.assertEqual(row["n_male"],3)
        self.assertEqual(row["n_female"],3)
        self.assertTrue(row["paired_n3_eligible"])
        self.assertEqual(row["active_trap_count"],7)

    def test_pathogen_incomplete_uncertain_and_nonheteromyid_are_excluded(self):
        pathogen=self._plot()
        pathogen["mammalGridSamplingMethod"]="pathogen"
        incomplete=self._plot(plot="JORN_002",event="E2",night="N2")
        incomplete["gridCompletion"]="setting incomplete"
        trap_rows=[
            self._capture("A1","x1","M",qualifier="cf."),
            self._capture("A2","x2","F",taxon="PEMA",name="Peromyscus maniculatus"),
        ]
        self.assertEqual(
            m.build_neon_sex_sessions(
                [pathogen,incomplete],
                trap_rows,
                target_taxon_ids={"PEFL","PEMA"},
            ),
            [],
        )

    def test_duplicate_tag_is_counted_once(self):
        plot_rows=[self._plot()]
        trap_rows=[
            self._capture("A1","same","M"),
            self._capture("A2","same","M"),
            self._capture("A3","f1","F"),
        ]
        rows=m.build_neon_sex_sessions(plot_rows,trap_rows,target_taxon_ids={"PEFL"})
        self.assertEqual(rows[0]["n_total"],2)
        self.assertEqual(rows[0]["n_male"],1)
        self.assertEqual(rows[0]["n_female"],1)

    def test_active_trap_completeness_uses_actual_session_traps(self):
        plot_rows=[self._plot()]
        # Expected design has 10 coordinates but only 5 usable active traps.
        trap_rows=[]
        for i in range(1,11):
            row=self._capture(f"A{i}",f"x{i}","M" if i%2 else "F")
            if i>5:
                row["trapStatus"]="1 - trap not set"
                row["tagID"]=""
            trap_rows.append(row)
        rows=m.build_neon_sex_sessions(plot_rows,trap_rows,target_taxon_ids={"PEFL"})
        self.assertEqual(rows,[])

    def test_inventory_reports_species_site_replication_only(self):
        sessions=[
            {"species":"Dipodomys ordii","site":"JORN","plot_id":"p1","year":2020,"paired_n2_eligible":True,"paired_n3_eligible":True,"paired_n5_eligible":False,"known_sex_fraction":1.0},
            {"species":"Dipodomys ordii","site":"MOAB","plot_id":"p2","year":2021,"paired_n2_eligible":True,"paired_n3_eligible":True,"paired_n5_eligible":True,"known_sex_fraction":0.9},
            {"species":"Perognathus flavus","site":"JORN","plot_id":"p1","year":2020,"paired_n2_eligible":True,"paired_n3_eligible":False,"paired_n5_eligible":False,"known_sex_fraction":0.8},
        ]
        inv=m.summarize_neon_sex_sessions(sessions)
        self.assertEqual(inv["paired_n3_sessions"],2)
        self.assertEqual(inv["species"]["Dipodomys ordii"]["paired_n3_sessions"],2)
        self.assertEqual(inv["species"]["Dipodomys ordii"]["independent_sites"],2)
        self.assertFalse(inv["ecological_effects_inspected"])


if __name__=="__main__":
    unittest.main()
