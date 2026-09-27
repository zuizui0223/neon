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


if __name__=="__main__":
    unittest.main()
