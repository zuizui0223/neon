import unittest,json
from hashlib import md5
from analysis.audit_neon_direct_seed_fate_stage_sources_v1 import SOURCES,audit,header
class StageSourceTest(unittest.TestCase):
    def test_pinned_primary_bytes_and_header(self):
        raw=b"seed_id,stage,block\nPRIVATE,cache,1\n"
        meta={"id":3189775,"title":"Indirect seed interactions","version":1,"doi":"10.6084/m9.figshare.3189775.v1","files":[{"id":2,"name":"data.csv","size":len(raw),"computed_md5":md5(raw).hexdigest(),"download_url":"https://ndownloader.figshare.com/files/2"}]}
        def fetch(u,n):return json.dumps(meta).encode() if "api.figshare" in u else raw
        out=audit(3189775,SOURCES[3189775],fetch)
        self.assertEqual(out["status"],"CHECKSUM_SOURCE_GO_SCHEMA_ONLY")
        self.assertEqual(out["source_receipts"][0]["schema"]["candidate_headers"],["seed_id","stage","block"])
        self.assertNotIn("PRIVATE",str(out))
        def bad(u,n):return json.dumps(meta).encode() if "api.figshare" in u else b"x"*len(raw)
        self.assertEqual(audit(3189775,SOURCES[3189775],bad)["status"],"STOP_INCOMPLETE_SOURCE_BYTES")
        meta["version"]=2
        with self.assertRaises(ValueError):audit(3189775,SOURCES[3189775],fetch)
    def test_numeric_header_not_exported(self):
        self.assertIsNone(header(b"123,456,789\n","data.csv")["candidate_headers"])
if __name__=="__main__":unittest.main()
