import unittest,json
from hashlib import md5
from analysis.audit_neon_holt_2025_capture_source_v1 import audit,csv_schema
class CaptureSourceTest(unittest.TestCase):
    def test_schema_does_not_export_outcome_values(self):
        r=csv_schema(b"year,id,weight\n1999,PRIVATE,123\n2000,OTHER,456\n","test.csv")
        self.assertEqual(r["rows"],2)
        self.assertEqual(r["year_counts_by_column_index"]["0"],{"1999":1,"2000":1})
        self.assertNotIn("PRIVATE",str(r))
        self.assertNotIn("123",str(r))
    def test_exact_bytes_and_version(self):
        raw=b"year,count\n1999,2\n"
        m={"id":27152484,"version":2,"title":"Coupled effects of forest growth and climate change","doi":"10.6084/m9.figshare.27152484.v2","files":[{"id":123,"name":"data.csv","size":len(raw),"computed_md5":md5(raw).hexdigest(),"download_url":"https://ndownloader.figshare.com/files/123"}]}
        def fetch(url,limit):return json.dumps(m).encode() if "api.figshare" in url else raw
        self.assertEqual(audit(fetch)["status"],"CHECKSUM_SOURCE_GO_SCHEMA_ONLY")
        def bad(url,limit):return json.dumps(m).encode() if "api.figshare" in url else b"x"*len(raw)
        self.assertEqual(audit(bad)["status"],"STOP_INCOMPLETE_SOURCE_BYTES")
        m["version"]=1
        with self.assertRaises(ValueError):audit(fetch)
if __name__=="__main__":unittest.main()
