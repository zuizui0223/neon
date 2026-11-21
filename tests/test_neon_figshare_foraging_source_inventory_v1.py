"""Synthetic Figshare metadata-only inventory tests; never retrieve any file."""
import unittest
from analysis.audit_neon_figshare_foraging_source_inventory_v1 import (
    audit_article_meta, validate_download_href,
)

class TestOriginalFigshareBehavioralSourceInventory(unittest.TestCase):
    def metadata(self):
        return {
            "id":21512436,
            "title":"Data: Predation risk and personality influence seed predation and dispersal",
            "doi":"10.6084/m9.figshare.21512436.v1",
            "version":1,
            "files":[
                {"id":99,"name":"behavior_events.csv","size":125000,
                 "computed_md5":"a"*32,
                 "download_url":"https://ndownloader.figshare.com/files/99"},
                {"id":100,"name":"README.txt","size":8000,
                 "computed_md5":"b"*32}
            ]
        }

    def test_source_inventory_no_biology(self):
        d=audit_article_meta(self.metadata(),21512436,"e"*64)
        self.assertEqual(d["status"],"PROVIDER_FILE_INVENTORY_GO_METADATA_ONLY")
        self.assertEqual(d["original_file_count"],2)
        self.assertTrue(d["no_original_animal_ID_or_seed_response_observed"])
        self.assertEqual(d["provider_meta_json_sha256"],"e"*64)
        self.assertNotIn("source_behavioral_effect",d)

    def test_unexpected_article_id_or_title_fails_closed(self):
        m=self.metadata()
        with self.assertRaisesRegex(ValueError,"UNEXPECTED_ARTICLE_ID"):
            audit_article_meta(m,28207769)
        m["title"]="Different title"
        with self.assertRaisesRegex(ValueError,"TITLE_ID_PROVENANCE_MISMATCH"):
            audit_article_meta(m,21512436)

    def test_duplicate_filename_or_missing_checksum_does_not_guess(self):
        m=self.metadata()
        m["files"][1]["name"]=m["files"][0]["name"]
        with self.assertRaisesRegex(ValueError,"UNSAFE_FILENAME"):
            audit_article_meta(m,21512436)
        m=self.metadata()
        m["files"][0]["computed_md5"]="corrupt"
        with self.assertRaisesRegex(ValueError,"INVALID_MD5"):
            audit_article_meta(m,21512436)

    def test_metadata_rejects_offsite_download_or_empty_file_list(self):
        for url in ("http://ndownloader.figshare.com/files/99",
                    "https://evil.example.org/99",
                    "https://figshare.com.evil.example.org/file",
                    "https://user:secret@figshare.com/99"):
            self.assertFalse(validate_download_href(url))
        m=self.metadata()
        m["files"][0]["download_url"]="https://evil.example.org/x.csv"
        with self.assertRaisesRegex(ValueError,"NONFIGSHARE"):
            audit_article_meta(m,21512436)
        m=self.metadata()
        m["files"]=[]
        with self.assertRaisesRegex(ValueError,"INVENTORY_EMPTY"):
            audit_article_meta(m,21512436)

    def test_unsafe_path_from_metadata_stops(self):
        m=self.metadata()
        m["files"][0]["name"]="../../animal.csv"
        with self.assertRaisesRegex(ValueError,"UNSAFE_FILENAME"):
            audit_article_meta(m,21512436)

if __name__=="__main__":
    unittest.main()
