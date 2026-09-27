import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"build_neon_space_use_sessions_v1.py"
spec=importlib.util.spec_from_file_location("neon_sessions",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def plotnight(night="N1",event="E1",method="diversity",completion="setting complete, processing complete",date="2024-05-01"):
    return {
        "nightuid":night,
        "eventID":event,
        "namedLocation":"SITE_001.mammalGrid.mam",
        "siteID":"SITE",
        "plotID":"SITE_001",
        "mammalGridSamplingMethod":method,
        "collectDate":date,
        "samplingImpractical":"OK",
        "gridCompletion":completion,
    }


def trap(uid,night,coord,status="5 - capture",tag="T1",taxon="SP1",name="Species one",qual="",nlcd="Grassland/Herbaceous"):
    return {
        "uid":uid,
        "nightuid":night,
        "namedLocation":"SITE_001.mammalGrid.mam",
        "siteID":"SITE",
        "plotID":"SITE_001",
        "trapCoordinate":coord,
        "nlcdClass":nlcd,
        "trapStatus":status,
        "collectDate":"2024-05-01",
        "tagID":tag,
        "taxonID":taxon,
        "scientificName":name,
        "taxonRank":"species",
        "identificationQualifier":qual,
        "identificationHistoryID":"",
    }


class NeonSpaceUseSessionTests(unittest.TestCase):
    def setUp(self):
        self.coords={
            f"SITE_001.mammalGrid.mam.A{i+1}":(float(i*10),0.0)
            for i in range(8)
        }
        self.base_traps=[
            trap(str(i+1),"N1",f"A{i+1}",tag=f"T{i+1}")
            for i in range(5)
        ] + [
            trap(str(i+6),"N1",f"A{i+6}",status="6 - trap set and empty",tag="",taxon="",name="")
            for i in range(3)
        ]

    def test_sampling_method_and_grid_completion_are_exact(self):
        self.assertTrue(m.is_primary_plotnight(plotnight()))
        self.assertFalse(m.is_primary_plotnight(plotnight(method="pathogen")))
        self.assertFalse(m.is_primary_plotnight(plotnight(completion="")))
        self.assertFalse(m.is_primary_plotnight(plotnight(completion="setting incomplete, processing complete")))

    def test_usable_active_traps_exclude_not_set_and_disturbed(self):
        self.assertFalse(m.is_usable_active_trap("1 - trap not set"))
        self.assertFalse(m.is_usable_active_trap("2 - trap disturbed/door closed but empty"))
        self.assertFalse(m.is_usable_active_trap("3 - trap door open or closed w/ spoor left"))
        self.assertTrue(m.is_usable_active_trap("4 - more than 1 capture in one trap"))
        self.assertTrue(m.is_usable_active_trap("5 - capture"))
        self.assertTrue(m.is_usable_active_trap("6 - trap set and empty"))

    def test_only_diversity_one_night_events_enter_primary_table(self):
        plots=[
            plotnight("N1","E1","diversity"),
            plotnight("N2","E2","pathogen"),
        ]
        traps=self.base_traps + [
            {**row,"uid":"P"+row["uid"],"nightuid":"N2"}
            for row in self.base_traps
        ]
        rows=m.build_neon_sessions(
            plots,traps,
            target_taxon_ids={"SP1"},
            coordinate_map=self.coords,
            history_rows=[],
            replicates=99,
        )
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["event_id"],"E1")

    def test_multi_night_diversity_event_is_excluded(self):
        plots=[plotnight("N1","E1"),plotnight("N2","E1",date="2024-05-02")]
        traps=self.base_traps + [
            {**row,"uid":"X"+row["uid"],"nightuid":"N2","collectDate":"2024-05-02"}
            for row in self.base_traps
        ]
        rows=m.build_neon_sessions(
            plots,traps,target_taxon_ids={"SP1"},coordinate_map=self.coords,history_rows=[],replicates=99
        )
        self.assertEqual(rows,[])

    def test_nightuid_join_and_missing_tag_filter(self):
        traps=list(self.base_traps)
        traps[0]={**traps[0],"tagID":""}
        traps.append(trap("other","OTHER","A1",tag="ZZ"))
        rows=m.build_neon_sessions(
            [plotnight()],traps,target_taxon_ids={"SP1"},coordinate_map=self.coords,history_rows=[],replicates=99
        )
        self.assertEqual(rows[0]["n_unique_individuals"],4)
        self.assertFalse(rows[0]["primary_n5_eligible"])

    def test_uncertain_identification_is_removed_from_primary_species_session(self):
        traps=list(self.base_traps)
        traps[0]={**traps[0],"identificationQualifier":"cf. species"}
        rows=m.build_neon_sessions(
            [plotnight()],traps,target_taxon_ids={"SP1"},coordinate_map=self.coords,history_rows=[],replicates=99
        )
        self.assertEqual(rows[0]["n_unique_individuals"],4)
        self.assertEqual(rows[0]["uncertain_capture_rows_excluded"],1)

    def test_duplicate_tag_uses_lexically_first_uid_once(self):
        traps=list(self.base_traps)
        traps.append(trap("00","N1","A8",tag="T1"))
        rows=m.build_neon_sessions(
            [plotnight()],traps,target_taxon_ids={"SP1"},coordinate_map=self.coords,history_rows=[],replicates=99
        )
        self.assertEqual(rows[0]["n_unique_individuals"],5)
        # uid 00 at A8 replaces uid 1 at A1, so observed MPD changes from the base configuration
        self.assertGreater(rows[0]["mpd_observed_m"],20)

    def test_current_taxonomy_is_used_and_history_is_audited_not_reverted(self):
        traps=list(self.base_traps)
        traps[0]={**traps[0],"identificationHistoryID":"H1","scientificName":"Current species"}
        history=[{"identificationHistoryID":"H1","scientificName":"Previous species"}]
        rows=m.build_neon_sessions(
            [plotnight()],traps,target_taxon_ids={"SP1"},coordinate_map=self.coords,history_rows=history,replicates=99
        )
        names={r["species"] for r in rows}
        self.assertIn("Current species",names)
        current=[r for r in rows if r["species"]=="Current species"][0]
        self.assertEqual(current["history_linked_capture_count"],1)

    def test_peromyscus_cryptic_complex_is_flagged(self):
        traps=[
            {**row,"scientificName":"Peromyscus maniculatus"}
            for row in self.base_traps
        ]
        rows=m.build_neon_sessions(
            [plotnight()],traps,target_taxon_ids={"SP1"},coordinate_map=self.coords,history_rows=[],replicates=99
        )
        self.assertTrue(rows[0]["cryptic_complex_sensitivity"])



    def test_coordinate_map_uses_trap_latlon_and_is_local_to_plot(self):
        rows=[
            {**trap("1","N1","A1"),"decimalLatitude":"35.000000","decimalLongitude":"-106.000000"},
            {**trap("2","N1","A2"),"decimalLatitude":"35.000000","decimalLongitude":"-105.999890"},
        ]
        coords=m.coordinate_map_from_trap_rows(rows)
        a=coords["SITE_001.mammalGrid.mam.A1"]
        b=coords["SITE_001.mammalGrid.mam.A2"]
        self.assertAlmostEqual(a[0],0.0,places=6)
        self.assertAlmostEqual(a[1],0.0,places=6)
        self.assertGreater(b[0],9.0)
        self.assertLess(b[0],11.0)
        self.assertAlmostEqual(b[1],0.0,places=3)

    def test_inventory_counts_eligibility_sites_species_habitat_and_taxonomy_flags(self):
        sessions=[
            {"site":"A","plot_id":"A_001","event_id":"E1","year":2024,"species":"Species one","nlcd_class":"Grassland/Herbaceous","n_unique_individuals":5,"active_trap_count":100,"sensitivity_n3_eligible":True,"primary_n5_eligible":True,"sensitivity_n8_eligible":False,"packing_estimable":True,"uncertain_capture_rows_excluded":1,"history_linked_capture_count":0,"cryptic_complex_sensitivity":False},
            {"site":"A","plot_id":"A_001","event_id":"E2","year":2025,"species":"Species one","nlcd_class":"Grassland/Herbaceous","n_unique_individuals":8,"active_trap_count":99,"sensitivity_n3_eligible":True,"primary_n5_eligible":True,"sensitivity_n8_eligible":True,"packing_estimable":True,"uncertain_capture_rows_excluded":0,"history_linked_capture_count":1,"cryptic_complex_sensitivity":False},
            {"site":"B","plot_id":"B_001","event_id":"E3","year":2025,"species":"Peromyscus maniculatus","nlcd_class":"Deciduous Forest","n_unique_individuals":3,"active_trap_count":100,"sensitivity_n3_eligible":True,"primary_n5_eligible":False,"sensitivity_n8_eligible":False,"packing_estimable":True,"uncertain_capture_rows_excluded":2,"history_linked_capture_count":0,"cryptic_complex_sensitivity":True},
        ]
        inv=m.summarize_neon_sessions(sessions)
        self.assertEqual(inv["session_count"],3)
        self.assertEqual(inv["site_count"],2)
        self.assertEqual(inv["species_count"],2)
        self.assertEqual(inv["eligible_n3"],3)
        self.assertEqual(inv["eligible_n5"],2)
        self.assertEqual(inv["eligible_n8"],1)
        self.assertEqual(inv["cryptic_complex_session_count"],1)
        self.assertEqual(inv["uncertain_capture_rows_excluded"],3)
        self.assertEqual(inv["history_linked_capture_count"],1)
        self.assertEqual(inv["species_habitat_session_counts"]["Species one"]["Grassland/Herbaceous"],2)
        self.assertEqual(inv["active_trap_count_range"],[99,100])
        self.assertEqual(inv["year_range"],[2024,2025])

    def test_zero_variance_null_is_retained_as_non_estimable(self):
        coords={f"SITE_001.mammalGrid.mam.A{i+1}":(float(i*10),0.0) for i in range(5)}
        traps=[trap(str(i+1),"N1",f"A{i+1}",tag=f"T{i+1}") for i in range(5)]
        rows=m.build_neon_sessions(
            [plotnight()],traps,target_taxon_ids={"SP1"},coordinate_map=coords,history_rows=[],replicates=99
        )
        self.assertEqual(len(rows),1)
        self.assertFalse(rows[0]["packing_estimable"])
        self.assertEqual(rows[0]["packing_non_estimable_reason"],"zero_null_variance")
        self.assertFalse(rows[0]["primary_n5_eligible"])


if __name__=="__main__":
    unittest.main()
