import unittest
from analysis.audit_sevilleta_external_source_schema_v1 import inspect_sev8_bytes

class Sev8SourceTests(unittest.TestCase):
    def test_real_tsv_shape_carries_headers_and_sha(self):
        data=b"site\tweb\tdate\tnight\tstake\tindividual\tspecies\n"+(
            b"GRASS\t1\t2015-05-23\t1\t11\t123\tPEMA\n"
            b"GRASS\t1\t2015-05-24\t2\t11\t123\tPEMA\n"
            b"GRASS\t1\t2015-05-25\t3\t12\t456\tDIME\n"
        )
        x=inspect_sev8_bytes(data,minimum_bytes=10)
        self.assertEqual(x["delimiter"],"TAB")
        self.assertEqual(x["row_count"],3)
        self.assertEqual(x["header_count"],7)
        self.assertEqual(x["distinct_source_sha256_bytes"],64)
        self.assertFalse(x["individual_W_B_opened"])

    def test_html_challenge_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"HTML"):
            inspect_sev8_bytes(b'<!doctype html><html>validating</html>',minimum_bytes=10)

    def test_ragged_field_record_fails_closed(self):
        v=b"site,web,date,night,stake,tag\nA,1,2020-01,1,11,x\nA,1,2020-01\n"
        with self.assertRaisesRegex(ValueError,"ragged"):
            inspect_sev8_bytes(v,minimum_bytes=10)

if __name__=="__main__":
    unittest.main()
