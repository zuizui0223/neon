"""Tests use synthetic bytes and provider metadata ONLY."""
from __future__ import annotations
import unittest

from analysis.audit_neon_figshare_2023_original_csv_schema_v1 import (
    FILES,audit_metadata,exact_file_href,original_header_and_row_count,
)

class TestFigshareOriginal2023CSVGate(unittest.TestCase):
    def meta(self):
        return {
            "id":21512436,"version":1,
            "title":"Data: Predation risk and personality influence seed predation",
            "files":[
                {"id":fid,"name":name,"size":size,"computed_md5":digest,
                 "download_url":f"https://ndownloader.figshare.com/files/{fid}"}
                for fid,(name,size,digest) in FILES.items()
            ]+[
                {"id":38217888,"name":"Main Analysis Script.R","size":54662,
                 "computed_md5":"b209339b7d0f1f2a7be3b00ebd6fbf4d",
                 "download_url":"https://ndownloader.figshare.com/files/38217888"},
                {"id":38217894,"name":"Repeatability and BLUPS Script.R","size":16130,
                 "computed_md5":"a57329cf3eb25fcbff2ead6f86439715",
                 "download_url":"https://ndownloader.figshare.com/files/38217894"}
            ]
        }

    def test_exact_all_pinned_and_optional_unselected_scripts(self):
        hrefs=audit_metadata(self.meta())
        self.assertEqual(len(hrefs),3)
        self.assertEqual(set(hrefs),set(FILES))

    def test_source_drift_rejected_not_fallback(self):
        m=self.meta();m["version"]=2
        with self.assertRaisesRegex(ValueError,"ARTICLE_VERSION_CHANGED"):
            audit_metadata(m)
        m=self.meta();m["files"][0]["size"]+=1
        with self.assertRaisesRegex(ValueError,"SOURCE_NAME_OR_SIZE_DRIFT"):
            audit_metadata(m)
        m=self.meta();m["files"][0]["computed_md5"]="0"*32
        with self.assertRaisesRegex(ValueError,"PROVIDER_MD5_DRIFT"):
            audit_metadata(m)

    def test_url_only_original_https_provider_file_id(self):
        self.assertTrue(exact_file_href(
            "https://ndownloader.figshare.com/files/38217891",38217891))
        for x in (
            "http://ndownloader.figshare.com/files/38217891",
            "https://attacker.example/files/38217891",
            "https://ndownloader.figshare.com/files/38217892",
            "https://user:pw@ndownloader.figshare.com/files/38217891"
        ):
            self.assertFalse(exact_file_href(x,38217891))

    def test_header_only_and_original_row_count(self):
        parsed=original_header_and_row_count(
            b'\xef\xbb\xbf"Grid","Tag","Seed offered"\n"a","rabbit","5"\n')
        self.assertEqual(parsed["original_column_names"],["Grid","Tag","Seed offered"])
        self.assertEqual(parsed["original_row_count"],1)
        self.assertNotIn("rabbit",str(parsed))
        with self.assertRaisesRegex(ValueError,"SOURCE_DUPLICATE_HEADER"):
            original_header_and_row_count(b"a,a\n1,2\n")
        with self.assertRaisesRegex(ValueError,"ORIGINAL_RAGGED_CSV"):
            original_header_and_row_count(b"a,b\n1,2,3\n")

if __name__=="__main__":
    unittest.main()
