import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"run_neon_space_use_development_v1.py"
spec=importlib.util.spec_from_file_location("runner",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class NeonSpaceUseDevelopmentRunnerTests(unittest.TestCase):
    def test_collect_site_codes_is_recursive_and_unique(self):
        payload={"a":[{"siteCode":"SRER"},{"x":{"siteCode":"WOOD"}}],"siteCode":"SRER"}
        self.assertEqual(m.collect_site_codes(payload),{"SRER","WOOD"})

    def test_select_release_files_keeps_only_required_tables(self):
        payload={
            "data":{
                "releases":[{
                    "release":"RELEASE-2026",
                    "packages":[{
                        "siteCode":"SRER",
                        "packageType":"expanded",
                        "month":"2024-05",
                        "files":[
                            {"name":"x.mam_perplotnight.2024-05.csv","url":"https://x/plot","md5":"a"*32,"size":10},
                            {"name":"x.mam_pertrapnight.2024-05.csv","url":"https://x/trap","md5":"b"*32,"size":20},
                            {"name":"x.mam_identificationHistory.2024-05.csv","url":"https://x/hist","md5":"c"*32,"size":30},
                            {"name":"x.mam_voucher.2024-05.csv","url":"https://x/voucher","md5":"d"*32,"size":40},
                        ],
                    }],
                }],
            }
        }
        rows=m.select_required_files(payload,release="RELEASE-2026")
        self.assertEqual([r["table"] for r in rows],[
            "mam_identificationHistory","mam_perplotnight","mam_pertrapnight"
        ])
        self.assertEqual({r["site_code"] for r in rows},{"SRER"})

    def test_target_taxa_uses_protocol_target_species_without_excluding_cryptic_pair(self):
        payload={"data":[
            {"taxonID":"PM","dwc:scientificName":"Peromyscus maniculatus","dwc:taxonRank":"species","taxonProtocolCategory":"target"},
            {"taxonID":"PL","dwc:scientificName":"Peromyscus leucopus","dwc:taxonRank":"species","taxonProtocolCategory":"target"},
            {"taxonID":"UR","dwc:scientificName":"Rodent sp.","dwc:taxonRank":"genus","taxonProtocolCategory":"target"},
            {"taxonID":"INC","dwc:scientificName":"Incidental species","dwc:taxonRank":"species","taxonProtocolCategory":"incidental"},
        ]}
        ids,names=m.target_taxa_from_taxonomy(payload)
        self.assertEqual(ids,{"PM","PL"})
        self.assertEqual(names,{"PM":"Peromyscus maniculatus","PL":"Peromyscus leucopus"})

    def test_taxonomy_uncertainty_summary_counts_qualifiers_and_history_links(self):
        rows=[
            {"siteID":"A","taxonID":"PM","scientificName":"Peromyscus maniculatus","identificationQualifier":"cf. species","identificationHistoryID":""},
            {"siteID":"A","taxonID":"PM","scientificName":"Peromyscus maniculatus","identificationQualifier":"","identificationHistoryID":"H1"},
            {"siteID":"B","taxonID":"PL","scientificName":"Peromyscus leucopus","identificationQualifier":"","identificationHistoryID":""},
        ]
        out=m.taxonomy_uncertainty_summary(rows)
        self.assertEqual(out[0]["site"],"A")
        self.assertEqual(out[0]["species"],"Peromyscus maniculatus")
        self.assertEqual(out[0]["capture_row_count"],2)
        self.assertEqual(out[0]["qualified_capture_row_count"],1)
        self.assertEqual(out[0]["history_linked_capture_row_count"],1)



    def test_location_registry_coordinates_are_preferred_over_plot_centroid_fields(self):
        # mam_pertrapnight decimalLatitude/Longitude can be plot-level and identical
        # across trap rows; the runner must use the NEON location registry instead.
        rows=[
            {"namedLocation":"SITE_001.mammalGrid.mam","trapCoordinate":"A1","plotID":"SITE_001","decimalLatitude":"35.0","decimalLongitude":"-106.0"},
            {"namedLocation":"SITE_001.mammalGrid.mam","trapCoordinate":"A2","plotID":"SITE_001","decimalLatitude":"35.0","decimalLongitude":"-106.0"},
        ]
        registry={
            "SITE_001.mammalGrid.mam.A1":(0.0,0.0),
            "SITE_001.mammalGrid.mam.A2":(10.0,0.0),
        }
        coords=m.coordinate_map_for_site(rows,registry)
        self.assertEqual(coords,registry)
        self.assertNotEqual(coords["SITE_001.mammalGrid.mam.A1"],coords["SITE_001.mammalGrid.mam.A2"])

    def test_pathogen_recapture_estimability_requires_three_moving_recaptures_per_event(self):
        plot_rows=[
            {"siteID":"S","plotID":"P","eventID":"E1","nightuid":"N1","mammalGridSamplingMethod":"pathogen","gridCompletion":"setting complete, processing complete","samplingImpractical":"OK"},
            {"siteID":"S","plotID":"P","eventID":"E1","nightuid":"N2","mammalGridSamplingMethod":"pathogen","gridCompletion":"setting complete, processing complete","samplingImpractical":"OK"},
        ]
        trap_rows=[]
        for tag,a,b in (("T1","A1","A2"),("T2","A2","A3"),("T3","A3","A4")):
            trap_rows.append({"nightuid":"N1","taxonID":"SP","scientificName":"Species one","taxonRank":"species","identificationQualifier":"","tagID":tag,"trapCoordinate":a,"trapStatus":"5 - capture"})
            trap_rows.append({"nightuid":"N2","taxonID":"SP","scientificName":"Species one","taxonRank":"species","identificationQualifier":"","tagID":tag,"trapCoordinate":b,"trapStatus":"5 - capture"})
        out=m.pathogen_recapture_estimability(plot_rows,trap_rows,{"SP"})
        self.assertEqual(out["estimable_event_count"],1)
        self.assertEqual(out["species_estimable_event_counts"]["Species one"],1)
        self.assertEqual(out["pathogen_species_with_estimable_recapture"],0)

    def test_pathogen_species_requires_five_estimable_events(self):
        plot_rows=[]
        trap_rows=[]
        for e in range(5):
            event=f"E{e}"
            for n in (1,2):
                night=f"{event}_N{n}"
                plot_rows.append({"siteID":"S","plotID":"P","eventID":event,"nightuid":night,"mammalGridSamplingMethod":"pathogen","gridCompletion":"setting complete, processing complete","samplingImpractical":"OK"})
            for tag,a,b in (("T1","A1","A2"),("T2","A2","A3"),("T3","A3","A4")):
                trap_rows.append({"nightuid":f"{event}_N1","taxonID":"SP","scientificName":"Species one","taxonRank":"species","identificationQualifier":"","tagID":tag,"trapCoordinate":a,"trapStatus":"5 - capture"})
                trap_rows.append({"nightuid":f"{event}_N2","taxonID":"SP","scientificName":"Species one","taxonRank":"species","identificationQualifier":"","tagID":tag,"trapCoordinate":b,"trapStatus":"5 - capture"})
        out=m.pathogen_recapture_estimability(plot_rows,trap_rows,{"SP"})
        self.assertEqual(out["estimable_event_count"],5)
        self.assertEqual(out["pathogen_species_with_estimable_recapture"],1)
        self.assertEqual(out["pathogen_species_names_with_estimable_recapture"],["Species one"])


if __name__=="__main__":
    unittest.main()
