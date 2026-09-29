from __future__ import annotations

import unittest

from analysis import audit_powdermill_dataone_source_v1 as m


class PowdermillSourceAuditTests(unittest.TestCase):
    def test_version_parser_handles_pasta_data_pid(self):
        pid="https://pasta.lternet.edu/package/data/eml/knb-lter-vcr/67/21/abc123"
        self.assertEqual(m.package_version(pid),21)

    def test_documented_headerless_block_is_detected(self):
        preamble=["metadata line"]*21
        row='1,N,PL,10,1,1979-09-01,44,M,0,20,0,1,0,0,0,0'
        raw=("\n".join(preamble+[row]*120)+"\n").encode()
        out=m.parse_record_block(raw)
        self.assertTrue(out["record_block_found"])
        self.assertTrue(out["documented_schema_match"])
        self.assertEqual(out["record_start_line_one_based"],22)
        self.assertEqual(out["data_row_count"],120)

    def test_wrong_field_count_is_rejected(self):
        raw=("a,b,c\n"*100).encode()
        out=m.parse_record_block(raw)
        self.assertFalse(out["documented_schema_match"])


if __name__=="__main__":
    unittest.main()
