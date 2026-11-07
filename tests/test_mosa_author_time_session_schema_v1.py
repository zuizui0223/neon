"""Check public author time-variable table parsing without any capture effects."""
import unittest
from analysis.audit_mosa_author_time_session_schema_v1 import (
    parse_time_table, source_method_slice,
)

class AuthorTimeSchemaTests(unittest.TestCase):
    def test_csv_categorical_time_columns(self):
        raw=b"primary,secondary,day\n1,1,1994-03-01\n1,2,1994-03-02\n1,3,1994-03-03\n2,1,1994-04-01\n"
        o=parse_time_table(raw)
        self.assertEqual(o["record_count"],4)
        self.assertEqual(o["columns"],["primary","secondary","day"])
        self.assertEqual(o["distinct_nonblank_by_column"]["primary"],2)
        self.assertEqual(o["preview"][0]["secondary"],"1")

    def test_fail_closed_if_html_masquerades_as_csv(self):
        with self.assertRaisesRegex(ValueError,"HTML"):
            parse_time_table(b"<!doctype html><html><title>Validating...</title></html>")

    def test_reject_ragged_rows(self):
        with self.assertRaisesRegex(ValueError,"ragged"):
            parse_time_table(b"a,b,c\n1,2,3\n1,2,3,4\n")

    def test_relevant_rmd_slice_includes_original_line_numbers(self):
        text="\n".join("line %d"%i for i in range(1,330))
        x=source_method_slice(text,start_line=175,end_line=177)
        self.assertEqual(x[0]["line"],175)
        self.assertEqual(x[-1]["line"],177)

if __name__=="__main__":
    unittest.main()
