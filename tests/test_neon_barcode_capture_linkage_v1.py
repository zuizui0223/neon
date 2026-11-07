"""Pure tests of NEON BOLD sampleID/earSampleID exact-key logic.

Test records are synthetic; no raw NEON sample, animal, sequence or
spatial coordinate is read or exported. No biological effect computed.
"""
from __future__ import annotations

import unittest
from unittest.mock import patch

from analysis.audit_neon_barcode_capture_linkage_v1 import (
    known_code, choose_field, parse_capture_file,
    source_barcode_rows, summarize_keys
)


class BarcodeEarSampleLinkageTests(unittest.TestCase):
    def test_neutral_codes_not_made_into_samples(self):
        for s in ("","NA","na","N/A","NULL",None):
            self.assertIsNone(known_code(s))
        self.assertEqual(known_code(" BARCODE001 "),"BARCODE001")
        with self.assertRaisesRegex(ValueError,"Missing"):
            choose_field(["sampleID","tagID"],"earSampleID")

    def test_capture_source_requires_real_earSampleID_header(self):
        fake=("tagID,plotID,taxonID,trapStatus\n"
              "T_ABC,P,PEMA,capture\n").encode()
        with self.assertRaisesRegex(ValueError,"earSampleID"):
            parse_capture_file(fake,{"site":"SITE","month":"2022-07"},
                               {"PEMA":"Peromyscus"})

    def test_only_tagged_actual_capture_with_single_ear_sample(self):
        csv=(
          "earSampleID,trapStatus,tagID,plotID,taxonID,nightuid\n"
          " SECRET_A ,capture,TAG_A,P,PEMA,n1\n"
          "SECRET_B,no capture,TAG_B,P,PEMA,n2\n"
          "SECRET_C,capture,,P,PEMA,n3\n"
          "SECRET_D|SECRET_E,capture,TAG_D,P,PEMA,n4\n"
          "NA,capture,TAG_E,P,PEMA,n5\n"
          "SECRET_F,capture,TAG_F,P,SIHI,n6\n"
        ).encode()
        out=parse_capture_file(csv,{"site":"SITE","month":"2022-07"},
                               {"PEMA":"Peromyscus","SIHI":"Sigmodon"})
        self.assertEqual(out["counts"]["all_trap_rows"],6)
        self.assertEqual(out["counts"]["capture_rows"],5)
        self.assertEqual(out["counts"]["target_captures_with_ear_sampleID"],3)
        self.assertEqual(out["counts"]["target_ear_sampleID_multivalue_rows"],1)
        self.assertEqual(len(out["observations"]),2)
        self.assertEqual(out["observations"][0]["sample"],"SECRET_A")
        self.assertTrue(out["earSampleID_column_verified"])

    def test_taxonomy_voucher_metadata_exact_unambiguous_source(self):
        files=[{
            "name":"NEON.D01.SITE.DP1.10076.001.mam_BOLDtaxonomy.2022-07.basic.20260201T000000Z.csv",
            "site":"SITE","month":"2022-07","md5":"0"*32,
            "size":10,"url":"https://example.org/test.csv",
        }]
        raw=(
            "sampleID,genus,species,taxonID,identificationMethod\n"
            " SECRET_A,Peromyscus,Peromyscus maniculatus,PEMA,ID Engine\n"
            " SECRET_B,Peromyscus,Peromyscus leucopus,PELE,Morphology\n"
        ).encode()
        with patch("analysis.audit_neon_barcode_capture_linkage_v1._download_many",
                   return_value=[raw]):
            data,summary=source_barcode_rows(files,"TEST_TOKEN","mam_BOLDtaxonomy")
        self.assertEqual(summary["source_files_MD5_verified"],1)
        self.assertEqual(summary["distinct_source_sampleIDs"],2)
        self.assertEqual(summary["taxonomy_identification_method_category_counts"]["ID Engine"],1)
        self.assertEqual(summary["taxonomy_identification_method_category_counts"]["Morphology"],1)
        self.assertEqual(data["SECRET_A"]["values"],
                         {("PEMA","Peromyscus","Peromyscus maniculatus","ID Engine")})
        self.assertNotIn("SECRET_A",str(summary))
        self.assertNotIn("SECRET_B",str(summary))

    def test_link_counts_ambiguity_and_species_consistency_not_DNA_confirmation(self):
        rows=[
            {"sample":"SECRET1","history":("SITE","P","TAG_A"),
             "site":"SITE","capture_year":"2022","genus":"Peromyscus","taxon":"PEMA"},
            {"sample":"SECRET2","history":("SITE","P","TAG_B"),
             "site":"SITE","capture_year":"2022","genus":"Peromyscus","taxon":"PELE"},
            {"sample":"SECRET2","history":("SITE","P","TAG_C"),
             "site":"SITE","capture_year":"2022","genus":"Peromyscus","taxon":"PELE"},
            {"sample":"SECRET3","history":("SITE","P","TAG_D"),
             "site":"SITE","capture_year":"2022","genus":"Peromyscus","taxon":"PEMA"},
            {"sample":"SECRET4","history":("SITE","P","TAG_E"),
             "site":"SITE","capture_year":"2023","genus":"Peromyscus","taxon":"PEMA"},
        ]
        def bold(taxon,site="SITE",method="Morphology"):
            return {"sites":{site},"months":{"2022-07"},
                    "values":{(taxon,"Peromyscus","specie label",method)},"rows":1}
        def voucher(site="SITE"):
            return {"sites":{site},"months":{"2022-07"},
                    "values":{"FIELD_CODE"},"rows":1}
        taxonomy={
            "SECRET1":bold("PEMA"),
            "SECRET2":bold("PELE"),
            "SECRET3":bold("PEMA",site="OTHER"),
            "SECRET4":bold("PELE"),
        }
        vouchers={s:voucher() for s in taxonomy}
        result=summarize_keys(
            rows,taxonomy,vouchers,{"PEMA":"Peromyscus","PELE":"Peromyscus"}
        )
        self.assertEqual(result["captured_samples_with_nonblank_single_earSampleID"],4)
        self.assertEqual(result["capture_unique_Peromyscus_histories_with_earSampleID"],5)
        self.assertEqual(result["capture_unique_Peromyscus_histories_with_unambiguous_BOLD_join"],2)
        self.assertEqual(result["source_key_anomalies"]["earSampleID_reused_between_animal_histories"],1)
        self.assertEqual(result["source_key_anomalies"]["barcode_and_capture_site_mismatch"],1)
        self.assertEqual(result["metadata_taxonID_consistency_not_DNA_verification"]["metadata_same_taxonID"],1)
        self.assertEqual(result["metadata_taxonID_consistency_not_DNA_verification"]["metadata_different_taxonID"],1)
        self.assertFalse(result["DNA_sequence_quality_or_species_identity_proven"])
        for secret in ("SECRET1","SECRET2","SECRET3","SECRET4","TAG_A"):
            self.assertNotIn(secret,str(result))

    def test_taxonomy_disagreement_same_barcode_is_not_species_call(self):
        h=("SITE","P","TAG_A")
        rows=[{"sample":"SECRET1","history":h,"site":"SITE",
               "capture_year":"2022","genus":"Peromyscus","taxon":"PEMA"}]
        taxonomy={"SECRET1":{"sites":{"SITE"},"months":{"2022-07"},
             "rows":2,"values":{
                ("PEMA","Peromyscus","P. maniculatus","Morphology"),
                ("PELE","Peromyscus","P. leucopus","ID Engine"),
             }}}
        voucher={"SECRET1":{"sites":{"SITE"},"months":{"2022-07"},
                              "rows":1,"values":{"CODE"}}}
        result=summarize_keys(
            rows,taxonomy,voucher,{"PEMA":"Peromyscus","PELE":"Peromyscus"}
        )
        self.assertEqual(result["capture_unique_histories_with_unambiguous_BOLD_join"],0)
        self.assertEqual(result["source_key_anomalies"]["conflicting_barcode_taxonomy_or_voucherInfo"],1)


if __name__=="__main__":
    unittest.main()
