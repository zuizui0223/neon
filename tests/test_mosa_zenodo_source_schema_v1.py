import hashlib
import unittest
from analysis.audit_mosa_zenodo_source_schema_v1 import (
    select_datafile,validate_source_bytes,PublishedSourceError
)

class MOSASourceIntegrityTests(unittest.TestCase):
    def fake(self,n=1200):
        head=b"animal,session,night,station,species,sex,weight\n"
        body=b"".join(
            f"tag{i},2020-01,{i%3+1},A{i%10+1},MAST,F,20\n".encode()
            for i in range(n))
        raw=head+body
        f={"key":"mosa_Feb2023_Flags.csv","size":len(raw),
           "checksum":"md5:"+hashlib.md5(raw).hexdigest(),
           "links":{"self":"https://zenodo.org/api/records/10049811/files/sample/content"}}
        return raw,f

    def test_exact_published_source_bytes(self):
        raw,f=self.fake()
        x=validate_source_bytes(raw,f)
        self.assertEqual(x["raw_capture_records"],1200)
        self.assertTrue(x["all_csv_rows_structurally_well_formed"])
        self.assertEqual(x["csv_field_count"],7)

    def test_non_utf8_cp1252_capture_text_is_valid_when_checksum_matches(self):
        raw,f=self.fake()
        raw=raw.replace(b",MAST,F,20",b",MAST"+bytes([0xe9])+b",F,20")
        f["size"]=len(raw)
        f["checksum"]="md5:"+hashlib.md5(raw).hexdigest()
        result=validate_source_bytes(raw,f)
        self.assertEqual(result["text_encoding"],"cp1252")
        self.assertEqual(result["raw_capture_records"],1200)

    def test_legacy_latin1_when_cp1252_has_undefined_byte(self):
        raw,f=self.fake()
        raw=raw.replace(b",MAST,F,20",b",MAST"+bytes([0x81])+b",F,20")
        f["size"]=len(raw)
        f["checksum"]="md5:"+hashlib.md5(raw).hexdigest()
        result=validate_source_bytes(raw,f)
        self.assertEqual(result["text_encoding"],"latin-1")
        self.assertEqual(result["raw_capture_records"],1200)

    def test_semicolon_delimited_verified_legacy_CSV(self):
        raw,f=self.fake()
        raw=raw.replace(b",",b";")
        f["size"]=len(raw)
        f["checksum"]="md5:"+hashlib.md5(raw).hexdigest()
        result=validate_source_bytes(raw,f)
        self.assertEqual(result["delimiter_type"],"SEMICOLON")
        self.assertEqual(result["raw_capture_records"],1200)

    def test_tab_delimited_verified_legacy_CSV(self):
        raw,f=self.fake()
        raw=raw.replace(b",",bytes([9]))
        f["size"]=len(raw)
        f["checksum"]="md5:"+hashlib.md5(raw).hexdigest()
        result=validate_source_bytes(raw,f)
        self.assertEqual(result["delimiter_type"],"TAB")
        self.assertEqual(result["raw_capture_records"],1200)

    def test_bot_challenge_even_if_metadata_checksum_matches(self):
        raw=b'<!DOCTYPE html><html><head><title>Validating...</title></head></html>'
        f={"key":"mosa_Feb2023_Flags.csv","size":len(raw),
           "checksum":"md5:"+hashlib.md5(raw).hexdigest()}
        with self.assertRaisesRegex(PublishedSourceError,"HTML"):
            validate_source_bytes(raw,f)

    def test_corrupt_bytes_fail_closed(self):
        raw,f=self.fake()
        with self.assertRaisesRegex(PublishedSourceError,"checksum mismatch"):
            validate_source_bytes(raw[:-1]+b"X",f)

    def test_mismatched_expected_size_fails_closed(self):
        raw,f=self.fake()
        f["size"]+=1
        with self.assertRaisesRegex(PublishedSourceError,"size mismatch"):
            validate_source_bytes(raw,f)

    def test_metadata_selects_single_real_source(self):
        raw,f=self.fake()
        m={"files":[f,{"key":"CMRINPUT Manual.pdf","links":{"self":"https://zenodo.org/manual.pdf"}}]}
        self.assertEqual(select_datafile(m)["key"],f["key"])
        with self.assertRaisesRegex(PublishedSourceError,"Expected one"):
            select_datafile({"files":[]})

if __name__=="__main__":
    unittest.main()
