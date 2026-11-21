"""Synthetic original 2026 source schema and metadata checks."""
import unittest
from analysis.audit_neon_figshare_2026_original_foraging_schema_v1 import (
    SOURCE_FILES,validate_provider_info,original_csv_structure,
)

class TestFigshare2026OriginalSource(unittest.TestCase):
    def meta(self):
        return {"id":28207769,"version":2,
                "title":"Data: Intraspecific and environmental variation",
                "files":[
                    {"id":fid,"name":n,"size":size,"computed_md5":md5,
                     "download_url":f"https://ndownloader.figshare.com/files/{fid}"}
                    for fid,(n,size,md5) in SOURCE_FILES.items()
                ] + [
                    {"id":51823913,"name":"Main Analysis - Clean.R","size":68819,
                     "computed_md5":"b5f99bfd6b800cdecb435dfb23f6e6b9"},
                    {"id":51823916,"name":"Repeatability.R","size":34050,
                     "computed_md5":"9e4fc28d8f223373c99fd409703d1ed2"},
                    {"id":51682223,"name":"BLUPS_MG 2016-2023.csv","size":132503,
                     "computed_md5":"65a9f2335a0acf00cc0530b68f322c19"},
                    {"id":51682226,"name":"BLUPS_PM 2016-2023.csv","size":106657,
                     "computed_md5":"0f50cc5bcb1910a49340c22b5eea85c8"}
                ]}

    def test_exact_version_file_meta_and_IDs(self):
        d=validate_provider_info(self.meta())
        self.assertEqual(set(d),set(SOURCE_FILES))

    def test_wrong_version_and_MD5_stop(self):
        x=self.meta();x["version"]=1
        with self.assertRaisesRegex(ValueError,"ARTICLE_VERSION"):
            validate_provider_info(x)
        x=self.meta();x["files"][0]["computed_md5"]="wrong"
        with self.assertRaisesRegex(ValueError,"MD5_CHANGED"):
            validate_provider_info(x)

    def test_unlabeled_original_columns_recorded_not_given_scientific_meaning(self):
        z=original_csv_structure(b",PIT,GRID\\n1,animal01,G1\\n2,animal02,G1\\n")
        self.assertEqual(z["original_rows"],2)
        self.assertEqual(z["unlabeled_source_column_positions"],[0])
        self.assertEqual(z["scientific_header_names_excluding_unlabeled"],["PIT","GRID"])

    def test_original_repeated_and_ragged_headers_stop(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATED_NAMED_COLUMNS"):
            original_csv_structure(b"a,a\\n1,2\\n")
        with self.assertRaisesRegex(ValueError,"RAGGED_ROW_WIDTH"):
            original_csv_structure(b"a,b\\n1,2\\n1,2,3\\n")

if __name__=="__main__":
    unittest.main()
