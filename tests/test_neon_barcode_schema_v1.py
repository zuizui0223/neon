"""Source-schema-only tests. Never ingest mammal positions or barcodes."""
from __future__ import annotations

import unittest
from analysis.audit_neon_barcode_schema_v1 import (
    BOLD_TABLES, BARCODE_PRODUCT, classify_file, parse_schema,
    choose_schema_files, extract_inventory
)


class BarcodeSourceSchemaTests(unittest.TestCase):
    def test_all_four_bold_table_types_and_optional_qa(self):
        self.assertEqual(len(BOLD_TABLES),4)
        self.assertEqual(BARCODE_PRODUCT,"DP1.10076.001")
        for base in (*BOLD_TABLES,"mam_barcodingqa"):
            self.assertEqual(classify_file("NEON.D01.TEST."+base+".2020-07.basic.20260801T000000Z.csv"),base)
        self.assertIsNone(classify_file("nonbarcode_mam_pertrapnight.csv"))
        self.assertIsNone(classify_file("mam_BOLDtaxonomy.variables.csv"))

    def test_schema_valid_and_never_exports_sample_values(self):
        src="earSampleID,boldProcessID,taxonID,qualityFlag\nSECRET_ID,PROCESS_123,PEMA,Q\n"
        out=parse_schema(src.encode())
        self.assertEqual(out["sampled_file_data_rows"],1)
        self.assertEqual(out["n_columns"],4)
        self.assertEqual(out["possible_sample_link_fields"],["boldProcessID","earSampleID"])
        self.assertNotIn("SECRET_ID",str(out))
        self.assertNotIn("PROCESS_123",str(out))
        self.assertTrue(out["no_sample_values_exported"])

    def test_duplicate_header_and_ragged_rows_fail_closed(self):
        with self.assertRaisesRegex(RuntimeError,"duplicate"):
            parse_schema(b"sampleID,sampleID\na,b\n")
        with self.assertRaisesRegex(RuntimeError,"ragged"):
            parse_schema(b"sampleID,processID\na\n")
        with self.assertRaisesRegex(RuntimeError,"unnamed"):
            parse_schema(b"sampleID,\na,b\n")

    def test_inventory_reuses_exact_release_and_MD5_guard(self):
        def meta(table,month):
            return {
                "name":f"NEON.D01.TEST.{table}.{month}.basic.20260201T000000Z.csv",
                "size":12,
                "md5":"0"*32,
                "url":"https://data.neonscience.org/api/v0/fake.csv",
            }
        allfiles=[meta(t,"2020-07") for t in BOLD_TABLES]
        allfiles += [meta("mam_BOLDtaxonomy","2022-11")]
        allfiles += [meta("mam_pertrapnight","2022-11")]
        payload={
            "data":{
                "releases":[{
                    "release":"RELEASE-2026",
                    "packages":[
                        {"siteCode":"TEST","month":"2020-07","packageType":"basic","files":allfiles[:4]},
                        {"siteCode":"TEST","month":"2022-11","packageType":"basic","files":allfiles[4:]},
                    ],
                }]
            }
        }
        files=extract_inventory(payload)
        self.assertEqual(len(files),5)
        chosen=choose_schema_files(files)
        self.assertEqual(len(chosen),5)
        self.assertEqual({classify_file(x["name"]) for x in chosen},set(BOLD_TABLES))

    def test_no_implicit_rewrite_of_nonbarcode_csv(self):
        self.assertIsNone(classify_file("NEON.D01.TEST.mam_pertrapnight.2021-08.basic.csv"))
        self.assertIsNone(classify_file("README.md"))
        self.assertIsNone(classify_file("NEON.D01.TEST.mam_BOLDtaxonomy.2020-08.basic.txt"))


if __name__=="__main__":
    unittest.main()
